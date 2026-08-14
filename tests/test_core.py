"""Unit tests for the core engine: loader, pipeline, report."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import cv2
import numpy as np

from src.core import FilterStep, ImageLoader, Pipeline, ReportGenerator, hash_image, save_image
from src.filters import (
    adjust_contrast_brightness,
    apply_clahe,
    apply_preset,
    filter_function,
    resolve_filter,
)


def sample_rgb(height: int = 32, width: int = 48) -> np.ndarray:
    rng = np.random.default_rng(7)
    return rng.integers(100, 150, size=(height, width, 3), dtype=np.uint8)


class TestImageLoader(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.image = sample_rgb()
        self.path = self.dir / 'test.png'
        cv2.imwrite(str(self.path), cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR))

    def tearDown(self):
        self.tmp.cleanup()

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            ImageLoader(self.dir / 'nope.png')

    def test_unsupported_extension_raises(self):
        bad = self.dir / 'notes.txt'
        bad.write_text('hello')
        with self.assertRaises(ValueError):
            ImageLoader(bad)

    def test_load_roundtrips_rgb(self):
        with ImageLoader(self.path) as loader:
            loaded = loader.load()
        np.testing.assert_array_equal(loaded, self.image)

    def test_metadata_includes_hash_and_dimensions(self):
        with ImageLoader(self.path) as loader:
            loader.load()
            metadata = loader.metadata
        self.assertEqual(metadata['filename'], 'test.png')
        self.assertEqual(metadata['width'], self.image.shape[1])
        self.assertEqual(metadata['height'], self.image.shape[0])
        self.assertEqual(len(metadata['sha256']), 64)

    def test_save_image_roundtrip(self):
        out = self.dir / 'out' / 'saved.png'
        save_image(self.image, out)
        self.assertTrue(out.exists())
        reloaded = cv2.cvtColor(cv2.imread(str(out)), cv2.COLOR_BGR2RGB)
        np.testing.assert_array_equal(reloaded, self.image)

    def test_save_image_reports_write_failure(self):
        # cv2.imwrite only returns False for an unwritable target; a silent
        # failure here would make the CLI claim a save that never happened.
        with self.assertRaises(OSError):
            save_image(self.image, self.dir / 'out.unsupported_ext')

    def test_find_images_lists_supported_files_sorted(self):
        for name in ('b.png', 'a.png', 'notes.txt', 'c.jpg'):
            (self.dir / name).write_bytes(b'x')
        cv2.imwrite(str(self.dir / 'a.png'), cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR))

        found = ImageLoader.find_images(self.dir)
        names = [p.name for p in found]

        self.assertEqual(names, ['a.png', 'b.png', 'c.jpg', 'test.png'])
        self.assertNotIn('notes.txt', names)

    def test_find_images_includes_raw_extensions(self):
        (self.dir / 'shot.cr2').write_bytes(b'x')
        (self.dir / 'shot.nef').write_bytes(b'x')
        names = [p.name for p in ImageLoader.find_images(self.dir)]
        self.assertIn('shot.cr2', names)
        self.assertIn('shot.nef', names)

    def test_find_images_non_recursive_by_default(self):
        nested = self.dir / 'sub'
        nested.mkdir()
        cv2.imwrite(str(nested / 'inner.png'), cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR))

        self.assertNotIn('inner.png', [p.name for p in ImageLoader.find_images(self.dir)])
        self.assertIn('inner.png',
                      [p.name for p in ImageLoader.find_images(self.dir, recursive=True)])

    def test_find_images_rejects_a_file(self):
        with self.assertRaises(NotADirectoryError):
            ImageLoader.find_images(self.path)

    def test_load_directory_yields_paths_and_images(self):
        cv2.imwrite(str(self.dir / 'second.png'),
                    cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR))

        loaded = list(ImageLoader.load_directory(self.dir))

        self.assertEqual(len(loaded), 2)
        for path, image in loaded:
            self.assertTrue(path.exists())
            np.testing.assert_array_equal(image, self.image)

    def test_load_directory_is_lazy(self):
        # A generator, so a directory of large frames need not fit in memory
        result = ImageLoader.load_directory(self.dir)
        self.assertFalse(isinstance(result, list))
        self.assertEqual(len(list(result)), 1)

    def test_raw_extension_is_accepted(self):
        raw_path = self.dir / 'shot.cr2'
        raw_path.write_bytes(b'not really a raw file')
        loader = ImageLoader(raw_path)
        self.assertFalse(loader.is_video)
        self.assertTrue(loader.is_raw)

    def test_raw_load_reports_missing_rawpy_clearly(self):
        raw_path = self.dir / 'shot.nef'
        raw_path.write_bytes(b'x')

        with mock.patch.dict(sys.modules, {'rawpy': None}):
            with self.assertRaises(RuntimeError) as ctx:
                ImageLoader(raw_path).load()

        self.assertIn('rawpy', str(ctx.exception))
        self.assertIn('pip install', str(ctx.exception))

    def test_raw_load_uses_forensic_postprocess_defaults(self):
        raw_path = self.dir / 'shot.arw'
        raw_path.write_bytes(b'x')

        fake_raw = mock.MagicMock()
        fake_raw.__enter__.return_value = fake_raw
        fake_raw.postprocess.return_value = self.image.copy()
        fake_raw.sizes.raw_width = 6000
        fake_raw.sizes.raw_height = 4000
        fake_raw.camera_whitebalance = [2.1, 1.0, 1.5, 0.0]
        fake_raw.black_level_per_channel = [512, 512, 512, 512]
        fake_raw.color_desc = b'RGBG'

        fake_rawpy = mock.MagicMock()
        fake_rawpy.imread.return_value = fake_raw

        with mock.patch.dict(sys.modules, {'rawpy': fake_rawpy}):
            loader = ImageLoader(raw_path)
            image = loader.load()
            metadata = loader.metadata

        np.testing.assert_array_equal(image, self.image)

        options = fake_raw.postprocess.call_args.kwargs
        # Exposure must not be silently stretched, and the camera's own white
        # balance is kept rather than guessed
        self.assertTrue(options['no_auto_bright'])
        self.assertTrue(options['use_camera_wb'])
        self.assertEqual(options['output_bps'], 8)

        self.assertEqual(metadata['raw']['raw_width'], 6000)
        self.assertEqual(metadata['raw']['color_description'], 'RGBG')
        self.assertEqual(len(metadata['sha256']), 64)

    def test_raw_options_can_be_overridden(self):
        raw_path = self.dir / 'shot.dng'
        raw_path.write_bytes(b'x')

        fake_raw = mock.MagicMock()
        fake_raw.__enter__.return_value = fake_raw
        fake_raw.postprocess.return_value = self.image.copy()
        fake_raw.color_desc = b'RGBG'
        fake_rawpy = mock.MagicMock()
        fake_rawpy.imread.return_value = fake_raw

        with mock.patch.dict(sys.modules, {'rawpy': fake_rawpy}):
            ImageLoader(raw_path, raw_options={'no_auto_bright': False,
                                               'output_bps': 16}).load()

        options = fake_raw.postprocess.call_args.kwargs
        self.assertFalse(options['no_auto_bright'])
        self.assertEqual(options['output_bps'], 16)
        self.assertTrue(options['use_camera_wb'])  # untouched default

    def test_raw_decode_failure_is_wrapped(self):
        raw_path = self.dir / 'broken.cr2'
        raw_path.write_bytes(b'x')

        fake_rawpy = mock.MagicMock()
        fake_rawpy.imread.side_effect = OSError('corrupt file')

        with mock.patch.dict(sys.modules, {'rawpy': fake_rawpy}):
            with self.assertRaises(RuntimeError) as ctx:
                ImageLoader(raw_path).load()

        self.assertIn('Failed to decode raw file', str(ctx.exception))

    def test_navigation_rejected_on_a_still(self):
        with ImageLoader(self.path) as loader:
            for call in (loader.next_frame, loader.previous_frame):
                with self.subTest(call=call.__name__):
                    with self.assertRaises(ValueError):
                        call()
            with self.assertRaises(ValueError):
                loader.goto_frame(0)

    def test_is_video_false_for_still(self):
        with ImageLoader(self.path) as loader:
            self.assertFalse(loader.is_video)
            self.assertEqual(loader.get_video_frame_count(), 1)


class TestPipeline(unittest.TestCase):

    def setUp(self):
        self.image = sample_rgb()
        self.pipeline = Pipeline(self.image)

    def test_starts_empty(self):
        self.assertEqual(len(self.pipeline), 0)
        np.testing.assert_array_equal(self.pipeline.current, self.image)

    def test_original_is_isolated_from_mutation(self):
        original = self.pipeline.original
        original[0, 0] = 0
        np.testing.assert_array_equal(self.pipeline.original, self.image)

    def test_apply_records_step(self):
        self.pipeline.apply(apply_clahe, 'clahe', 'src.filters.clahe', {'clip_limit': 3.0})
        self.assertEqual(len(self.pipeline), 1)
        self.assertEqual(self.pipeline.chain[0].name, 'clahe')
        self.assertEqual(self.pipeline.chain[0].params, {'clip_limit': 3.0})

    def test_undo_restores_previous_state(self):
        self.pipeline.apply(apply_clahe, 'clahe', 'src.filters.clahe', {})
        self.pipeline.undo()
        self.assertEqual(len(self.pipeline), 0)
        np.testing.assert_array_equal(self.pipeline.current, self.image)

    def test_redo_reapplies(self):
        after = self.pipeline.apply(apply_clahe, 'clahe', 'src.filters.clahe', {})
        self.pipeline.undo()
        redone = self.pipeline.redo()
        np.testing.assert_array_equal(redone, after)
        self.assertEqual(len(self.pipeline), 1)

    def test_undo_on_empty_returns_none(self):
        self.assertIsNone(self.pipeline.undo())

    def test_redo_stack_cleared_by_new_action(self):
        self.pipeline.apply(apply_clahe, 'clahe', 'src.filters.clahe', {})
        self.pipeline.undo()
        self.pipeline.apply(adjust_contrast_brightness, 'contrast_brightness',
                            'src.filters.contrast_brightness', {'brightness': 10})
        self.assertIsNone(self.pipeline.redo())

    def test_failed_filter_rolls_back(self):
        def broken(image):
            raise RuntimeError('boom')

        with self.assertRaises(RuntimeError):
            self.pipeline.apply(broken, 'broken', 'test', {})
        self.assertEqual(len(self.pipeline), 0)
        np.testing.assert_array_equal(self.pipeline.current, self.image)

    def test_non_array_return_is_rejected(self):
        with self.assertRaises(RuntimeError):
            self.pipeline.apply(lambda image: 'not an array', 'bad', 'test', {})
        self.assertEqual(len(self.pipeline), 0)

    def test_reset_clears_everything(self):
        self.pipeline.apply(apply_clahe, 'clahe', 'src.filters.clahe', {})
        self.pipeline.reset()
        self.assertEqual(len(self.pipeline), 0)
        self.assertIsNone(self.pipeline.undo())
        np.testing.assert_array_equal(self.pipeline.current, self.image)

    def test_order_matters(self):
        first = Pipeline(self.image)
        first.apply(adjust_contrast_brightness, 'contrast_brightness',
                    'src.filters.contrast_brightness', {'brightness': 60})
        first.apply(apply_clahe, 'clahe', 'src.filters.clahe', {'clip_limit': 4.0})

        second = Pipeline(self.image)
        second.apply(apply_clahe, 'clahe', 'src.filters.clahe', {'clip_limit': 4.0})
        second.apply(adjust_contrast_brightness, 'contrast_brightness',
                     'src.filters.contrast_brightness', {'brightness': 60})

        self.assertFalse(np.array_equal(first.current, second.current))

    def test_compare_returns_original_and_current(self):
        self.pipeline.apply(apply_clahe, 'clahe', 'src.filters.clahe', {})
        original, current = self.pipeline.compare()
        np.testing.assert_array_equal(original, self.image)
        self.assertFalse(np.array_equal(original, current))

    def test_preset_roundtrip_reproduces_result(self):
        self.pipeline.apply(adjust_contrast_brightness, 'contrast_brightness',
                            'src.filters.contrast_brightness', {'brightness': 25})
        self.pipeline.apply(apply_clahe, 'clahe', 'src.filters.clahe', {'clip_limit': 3.0})
        expected = self.pipeline.current

        with tempfile.TemporaryDirectory() as tmp:
            preset_path = Path(tmp) / 'preset.json'
            self.pipeline.save_preset(str(preset_path), name='test')
            preset = json.loads(preset_path.read_text(encoding='utf-8'))

        replayed = Pipeline(self.image)
        result = apply_preset(replayed, preset)

        np.testing.assert_array_equal(result, expected)
        self.assertEqual(len(replayed), 2)

    def test_replace_chain_actually_applies_the_filters(self):
        expected = Pipeline(self.image)
        expected.apply(adjust_contrast_brightness, 'contrast_brightness',
                       'src.filters.contrast_brightness', {'brightness': 25})
        expected.apply(apply_clahe, 'clahe', 'src.filters.clahe', {'clip_limit': 3.0})

        replaced = Pipeline(self.image)
        result = replaced.replace_chain(expected.chain, filter_function)

        np.testing.assert_array_equal(result, expected.current)
        self.assertFalse(np.array_equal(result, self.image))

    def test_replace_chain_discards_the_previous_chain(self):
        self.pipeline.apply(adjust_contrast_brightness, 'contrast_brightness',
                            'src.filters.contrast_brightness', {'brightness': 90})

        new_chain = [FilterStep('clahe', 'src.filters.clahe', {'clip_limit': 2.0})]
        self.pipeline.replace_chain(new_chain, filter_function)

        self.assertEqual([step.name for step in self.pipeline.chain], ['clahe'])

        # The result must come from the original, not from the brightened state
        reference = Pipeline(self.image)
        reference.apply(apply_clahe, 'clahe', 'src.filters.clahe', {'clip_limit': 2.0})
        np.testing.assert_array_equal(self.pipeline.current, reference.current)

    def test_replace_chain_report_matches_the_applied_image(self):
        # The defect this method used to have: the chain claimed filters that
        # were never applied, so the report described processing that did not
        # happen while the image sat untouched.
        chain = [
            FilterStep('levels', 'src.filters.levels',
                       {'black_point': 20, 'gamma': 1.0, 'white_point': 220}),
            FilterStep('clahe', 'src.filters.clahe', {'clip_limit': 2.5}),
        ]
        self.pipeline.replace_chain(chain, filter_function)

        report = self.pipeline.generate_report()
        self.assertEqual(report['filter_count'], 2)
        self.assertFalse(np.array_equal(self.pipeline.current, self.image))

    def test_replace_chain_with_empty_chain_restores_original(self):
        self.pipeline.apply(apply_clahe, 'clahe', 'src.filters.clahe', {})
        result = self.pipeline.replace_chain([], filter_function)

        np.testing.assert_array_equal(result, self.image)
        self.assertEqual(len(self.pipeline), 0)

    def test_replace_chain_supports_reordering(self):
        self.pipeline.apply(adjust_contrast_brightness, 'contrast_brightness',
                            'src.filters.contrast_brightness', {'brightness': 60})
        self.pipeline.apply(apply_clahe, 'clahe', 'src.filters.clahe', {'clip_limit': 4.0})
        original_order = self.pipeline.current

        reversed_chain = list(reversed(self.pipeline.chain))
        reordered = self.pipeline.replace_chain(reversed_chain, filter_function)

        self.assertFalse(np.array_equal(reordered, original_order))
        self.assertEqual([step.name for step in self.pipeline.chain],
                         ['clahe', 'contrast_brightness'])

    def test_replace_chain_rolls_back_on_unknown_filter(self):
        self.pipeline.apply(apply_clahe, 'clahe', 'src.filters.clahe', {'clip_limit': 2.0})
        before_image = self.pipeline.current
        before_chain = self.pipeline.chain

        bad_chain = [
            FilterStep('levels', 'src.filters.levels', {'black_point': 10}),
            FilterStep('no_such_filter', 'nowhere', {}),
        ]
        with self.assertRaises(KeyError):
            self.pipeline.replace_chain(bad_chain, filter_function)

        np.testing.assert_array_equal(self.pipeline.current, before_image)
        self.assertEqual([s.name for s in self.pipeline.chain],
                         [s.name for s in before_chain])

    def test_replace_chain_rolls_back_on_bad_parameters(self):
        self.pipeline.apply(apply_clahe, 'clahe', 'src.filters.clahe', {'clip_limit': 2.0})
        before_image = self.pipeline.current

        # black_point above white_point is rejected by the levels filter
        bad_chain = [FilterStep('levels', 'src.filters.levels',
                                {'black_point': 200, 'white_point': 100})]
        with self.assertRaises(RuntimeError):
            self.pipeline.replace_chain(bad_chain, filter_function)

        np.testing.assert_array_equal(self.pipeline.current, before_image)
        self.assertEqual(len(self.pipeline), 1)

    def test_replace_chain_leaves_undo_usable_after_rollback(self):
        self.pipeline.apply(apply_clahe, 'clahe', 'src.filters.clahe', {'clip_limit': 2.0})

        with self.assertRaises(KeyError):
            self.pipeline.replace_chain(
                [FilterStep('no_such_filter', 'nowhere', {})], filter_function)

        # History survived the failed rebuild, so undo still works
        self.assertIsNotNone(self.pipeline.undo())
        np.testing.assert_array_equal(self.pipeline.current, self.image)

    def test_replace_chain_history_allows_undo_of_replayed_steps(self):
        chain = [
            FilterStep('contrast_brightness', 'src.filters.contrast_brightness',
                       {'brightness': 30}),
            FilterStep('clahe', 'src.filters.clahe', {'clip_limit': 2.0}),
        ]
        self.pipeline.replace_chain(chain, filter_function)

        self.pipeline.undo()
        self.assertEqual([step.name for step in self.pipeline.chain],
                         ['contrast_brightness'])

    def test_replace_chain_accepts_a_custom_resolver(self):
        def resolver(name):
            if name != 'double_brightness':
                raise KeyError(name)
            return lambda image: np.clip(image.astype(np.int32) * 2, 0, 255).astype(np.uint8)

        chain = [FilterStep('double_brightness', 'custom', {})]
        result = self.pipeline.replace_chain(chain, resolver)

        np.testing.assert_array_equal(
            result, np.clip(self.image.astype(np.int32) * 2, 0, 255).astype(np.uint8))

    def test_replace_chain_round_trips_a_saved_preset(self):
        self.pipeline.apply(adjust_contrast_brightness, 'contrast_brightness',
                            'src.filters.contrast_brightness', {'brightness': 25})
        self.pipeline.apply(apply_clahe, 'clahe', 'src.filters.clahe', {'clip_limit': 3.0})
        expected = self.pipeline.current

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'preset.json'
            self.pipeline.save_preset(str(path))
            preset = Pipeline(self.image).load_preset(str(path))

        rebuilt = Pipeline(self.image)
        steps = [FilterStep.from_dict(step) for step in preset['filters']]
        result = rebuilt.replace_chain(steps, filter_function)

        np.testing.assert_array_equal(result, expected)

    def test_generate_report_counts_filters(self):
        self.pipeline.apply(apply_clahe, 'clahe', 'src.filters.clahe', {})
        report = self.pipeline.generate_report()
        self.assertEqual(report['filter_count'], 1)
        self.assertEqual(len(report['filters']), 1)


class TestRegistry(unittest.TestCase):

    def test_resolve_known_filter(self):
        self.assertEqual(resolve_filter('clahe').fn, apply_clahe)

    def test_unknown_filter_raises_with_suggestions(self):
        # Deliberately not a plausible future filter name: this test is about
        # the error message, and should not break as the roadmap fills in.
        with self.assertRaises(KeyError) as ctx:
            resolve_filter('no_such_filter_exists')
        self.assertIn('clahe', str(ctx.exception))


class TestReport(unittest.TestCase):

    def setUp(self):
        pipeline = Pipeline(sample_rgb())
        pipeline.apply(apply_clahe, 'clahe', 'src.filters.clahe', {'clip_limit': 2.0})
        self.report = ReportGenerator(pipeline.generate_report(), {'filename': 'test.png'})

    def test_markdown_contains_chain_details(self):
        markdown = self.report.to_markdown()
        self.assertIn('# Image Processing Report', markdown)
        self.assertIn('clahe', markdown)
        self.assertIn('clip_limit', markdown)

    def test_save_markdown_and_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            md_path = Path(tmp) / 'report.md'
            json_path = Path(tmp) / 'report.json'
            self.report.save(str(md_path), format='markdown')
            self.report.save(str(json_path), format='json')

            self.assertTrue(md_path.exists())
            data = json.loads(json_path.read_text(encoding='utf-8'))
            self.assertEqual(data['processing']['filter_count'], 1)

    def test_unknown_format_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                self.report.save(str(Path(tmp) / 'report.docx'), format='docx')

    def test_save_pdf_produces_a_valid_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'report.pdf'
            self.report.save(str(path), format='pdf')

            self.assertTrue(path.exists())
            self.assertGreater(path.stat().st_size, 1000)
            # A PDF always starts with the %PDF- magic bytes
            self.assertEqual(path.read_bytes()[:5], b'%PDF-')

    def test_save_pdf_corrects_the_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.report.save(str(Path(tmp) / 'report.txt'), format='pdf')
            self.assertTrue((Path(tmp) / 'report.pdf').exists())

    def test_to_pdf_creates_parent_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'nested' / 'deep' / 'report.pdf'
            self.report.to_pdf(str(path))
            self.assertTrue(path.exists())

    def test_pdf_paginates_a_long_chain(self):
        # Enough steps to overflow one page, which exercises the page break
        pipeline = Pipeline(sample_rgb())
        for _ in range(40):
            pipeline.apply(apply_clahe, 'clahe', 'src.filters.clahe', {'clip_limit': 2.0})
        report = ReportGenerator(pipeline.generate_report(), {'filename': 'long.png'})

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'long.pdf'
            report.to_pdf(str(path))
            # Each page is a separate object in the PDF's page tree
            self.assertGreater(path.read_bytes().count(b'/Type /Page'), 1)

    def test_styled_lines_cover_the_chain(self):
        lines = self.report._styled_lines()
        text = '\n'.join(line for line, _ in lines)
        self.assertIn('Image Processing Report', text)
        self.assertIn('clahe', text)
        self.assertIn('clip_limit', text)
        # No Markdown syntax leaking into the PDF text
        self.assertNotIn('**', text)

    def test_hash_image_is_stable_and_sensitive(self):
        image = sample_rgb()
        self.assertEqual(hash_image(image), hash_image(image.copy()))
        modified = image.copy()
        modified[0, 0, 0] = (int(modified[0, 0, 0]) + 1) % 256
        self.assertNotEqual(hash_image(image), hash_image(modified))


if __name__ == '__main__':
    unittest.main()
