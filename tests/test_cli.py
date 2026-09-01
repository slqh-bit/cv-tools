"""Unit tests for argument parsing and the CLI entry point."""

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

import cv2
import numpy as np

from src.cli import main, translate_step
from src.core import ImageLoader
from src.filters import ANALYSIS_REGISTRY
from src.filters import estimate_noise
from src.utils.parsing import (
    parse_float_list,
    parse_int_list,
    parse_kv,
    parse_resize_spec,
    parse_size,
    parse_value,
)


class TestParsing(unittest.TestCase):

    def test_parse_value_types(self):
        self.assertEqual(parse_value('3'), 3)
        self.assertEqual(parse_value('2.5'), 2.5)
        self.assertIs(parse_value('true'), True)
        self.assertIs(parse_value('false'), False)
        self.assertIsNone(parse_value('none'))
        self.assertEqual(parse_value('8x8'), (8, 8))
        self.assertEqual(parse_value('lab'), 'lab')

    def test_parse_kv(self):
        self.assertEqual(parse_kv(['clip=2.0', 'tile=8x8', 'mode=lab']),
                         {'clip': 2.0, 'tile': (8, 8), 'mode': 'lab'})

    def test_parse_kv_rejects_bare_token(self):
        with self.assertRaises(ValueError):
            parse_kv(['clip'])

    def test_parse_kv_rejects_empty_key(self):
        with self.assertRaises(ValueError):
            parse_kv(['=2.0'])

    def test_parse_size(self):
        self.assertEqual(parse_size('800x600'), (800, 600))
        with self.assertRaises(ValueError):
            parse_size('800')
        with self.assertRaises(ValueError):
            parse_size('axb')

    def test_parse_int_list_enforces_count(self):
        self.assertEqual(parse_int_list('1,2,3,4', 4), [1, 2, 3, 4])
        with self.assertRaises(ValueError):
            parse_int_list('1,2,3', 4)
        with self.assertRaises(ValueError):
            parse_int_list('1,2,3,x', 4)

    def test_parse_float_list(self):
        self.assertEqual(parse_float_list('20,1.0,220', 3), [20.0, 1.0, 220.0])

    def test_parse_resize_spec_forms(self):
        self.assertEqual(parse_resize_spec('800x600'), {'width': 800, 'height': 600})
        self.assertEqual(parse_resize_spec('800x'), {'width': 800})
        self.assertEqual(parse_resize_spec('x600'), {'height': 600})
        self.assertEqual(parse_resize_spec('50%'), {'scale': 0.5})
        self.assertEqual(parse_resize_spec('0.5'), {'scale': 0.5})

    def test_parse_resize_spec_rejects_garbage(self):
        with self.assertRaises(ValueError):
            parse_resize_spec('big')


class TestTranslateStep(unittest.TestCase):

    def test_clahe_params_are_mapped_to_function_kwargs(self):
        name, params = translate_step('clahe', ['clip=3.0', 'tile=16x16', 'mode=yuv'], 'auto')
        self.assertEqual(name, 'clahe')
        self.assertEqual(params, {'clip_limit': 3.0, 'tile_grid_size': (16, 16),
                                  'color_mode': 'yuv'})

    def test_clahe_without_params_uses_defaults(self):
        self.assertEqual(translate_step('clahe', [], 'auto'), ('clahe', {}))

    def test_levels_triplet(self):
        name, params = translate_step('levels', '20,0.8,230', 'auto')
        self.assertEqual(name, 'levels')
        self.assertEqual(params, {'black_point': 20.0, 'gamma': 0.8, 'white_point': 230.0})

    def test_roi_and_crop_map_to_different_filters(self):
        self.assertEqual(translate_step('roi', '1,2,3,4', 'auto')[0], 'roi_crop')
        self.assertEqual(translate_step('crop', '1,2,3,4', 'auto')[0], 'crop')

    def test_resize_carries_interpolation(self):
        name, params = translate_step('resize', '50%', 'lanczos')
        self.assertEqual(name, 'resize')
        self.assertEqual(params, {'scale': 0.5, 'interpolation': 'lanczos'})

    def test_histeq_mode_is_renamed(self):
        self.assertEqual(translate_step('histeq', ['mode=hsv'], 'auto'),
                         ('histeq', {'color_mode': 'hsv'}))

    def test_malformed_levels_raises(self):
        with self.assertRaises(ValueError):
            translate_step('levels', '20,230', 'auto')

    def test_sharpen_params(self):
        name, params = translate_step('sharpen', ['amount=1.5', 'radius=2.0', 'threshold=4'],
                                      'auto')
        self.assertEqual(name, 'sharpen')
        self.assertEqual(params, {'amount': 1.5, 'radius': 2.0, 'threshold': 4})

    def test_sharpen_laplacian_renames_kernel(self):
        self.assertEqual(translate_step('sharpen_laplacian', ['strength=2.0', 'kernel=3'], 'auto'),
                         ('sharpen_laplacian', {'strength': 2.0, 'kernel_size': 3}))

    def test_gaussian_and_median_defaults(self):
        self.assertEqual(translate_step('gaussian', None, 'auto'),
                         ('gaussian_blur', {'radius': 2.0}))
        self.assertEqual(translate_step('median', None, 'auto'),
                         ('median_filter', {'kernel_size': 3}))

    def test_bilateral_shorthand_params(self):
        name, params = translate_step('bilateral', ['d=7', 'color=50', 'space=9'], 'auto')
        self.assertEqual(name, 'bilateral_filter')
        self.assertEqual(params, {'diameter': 7, 'sigma_color': 50.0, 'sigma_space': 9.0})

    def test_canny_threshold_pair(self):
        self.assertEqual(translate_step('canny', '50,150', 'auto'),
                         ('canny', {'low_threshold': 50.0, 'high_threshold': 150.0}))

    def test_blur_first_reaches_edge_detectors(self):
        _, params = translate_step('canny', '50,150', 'auto', blur_first=1.5)
        self.assertEqual(params['blur_sigma'], 1.5)
        _, params = translate_step('auto_canny', None, 'auto', blur_first=1.5)
        self.assertEqual(params, {'sigma': 0.33, 'blur_sigma': 1.5})

    def test_laplacian_explicit_blur_beats_blur_first(self):
        _, params = translate_step('laplacian', ['blur=3.0'], 'auto', blur_first=1.0)
        self.assertEqual(params['blur_sigma'], 3.0)

    def test_sobel_renames_kernel(self):
        self.assertEqual(translate_step('sobel', ['dx=1', 'dy=0', 'kernel=5'], 'auto'),
                         ('sobel', {'dx': 1, 'dy': 0, 'kernel_size': 5}))

    def test_malformed_canny_raises(self):
        with self.assertRaises(ValueError):
            translate_step('canny', '50', 'auto')

    def test_ela_renames_gray(self):
        self.assertEqual(translate_step('ela', ['quality=80', 'gray=true'], 'auto'),
                         ('ela', {'quality': 80, 'grayscale': True}))

    def test_fft_renames_log(self):
        self.assertEqual(translate_step('fft', ['log=false'], 'auto'),
                         ('fft_spectrum', {'log_scale': False}))

    def test_fft_filter_renames_type(self):
        name, params = translate_step('fft_filter', ['type=highpass', 'cutoff=20'], 'auto')
        self.assertEqual(name, 'fft_filter')
        self.assertEqual(params, {'filter_type': 'highpass', 'cutoff': 20})

    def test_clone_detect_shorthand(self):
        name, params = translate_step(
            'clone_detect', ['block=8', 'step=2', 'matches=4', 'variance=5'], 'auto')
        self.assertEqual(name, 'clone_detect')
        self.assertEqual(params, {'block_size': 8, 'step': 2,
                                  'min_matches': 4, 'min_variance': 5.0})

    def test_deblur_renames_noise(self):
        self.assertEqual(
            translate_step('deblur', ['length=15', 'angle=30', 'noise=0.02'], 'auto'),
            ('deblur_motion', {'length': 15, 'angle': 30, 'noise_power': 0.02}))

    def test_deblur_defocus_shorthand(self):
        self.assertEqual(translate_step('deblur_defocus', ['radius=4'], 'auto'),
                         ('deblur_defocus', {'radius': 4}))

    def test_noise_map_default_block(self):
        self.assertEqual(translate_step('noise_map', None, 'auto'),
                         ('noise_map', {'block_size': 32}))

    def test_remove_periodic_renames_notch(self):
        self.assertEqual(translate_step('remove_periodic', ['notch=6'], 'auto'),
                         ('remove_periodic', {'notch_radius': 6.0}))


class CLITestCase(unittest.TestCase):
    """Base class providing a temp workspace with one input image."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        rng = np.random.default_rng(3)
        self.image = rng.integers(100, 140, size=(60, 80, 3), dtype=np.uint8)
        self.input = self.dir / 'input.png'
        cv2.imwrite(str(self.input), cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR))

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, argv):
        """Run main() capturing stdout/stderr. Returns (exit_code, stdout)."""
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(argv)
        return code, out.getvalue()

    def read(self, path):
        return cv2.cvtColor(cv2.imread(str(path)), cv2.COLOR_BGR2RGB)


class TestCLIRun(CLITestCase):

    def test_clahe_writes_output(self):
        out = self.dir / 'out.png'
        code, _ = self.run_cli([str(self.input), '--clahe', 'clip=3.0', 'tile=8x8',
                                '-o', str(out)])
        self.assertEqual(code, 0)
        self.assertTrue(out.exists())
        self.assertGreater(self.read(out).std(), self.image.std())

    def test_roi_crop_changes_dimensions(self):
        out = self.dir / 'crop.png'
        code, _ = self.run_cli([str(self.input), '--roi', '10,10,30,20', '-o', str(out)])
        self.assertEqual(code, 0)
        self.assertEqual(self.read(out).shape[:2], (20, 30))

    def test_resize_percentage(self):
        out = self.dir / 'small.png'
        code, _ = self.run_cli([str(self.input), '--resize', '50%', '-o', str(out)])
        self.assertEqual(code, 0)
        self.assertEqual(self.read(out).shape[:2], (30, 40))

    def test_filters_apply_in_command_line_order(self):
        # Input is 80x60. Cropping to 40x40 then halving gives 20x20, while
        # halving to 40x30 first clips the crop to 40x30.
        crop_then_resize = self.dir / 'a.png'
        resize_then_crop = self.dir / 'b.png'
        self.run_cli([str(self.input), '--roi', '0,0,40,40', '--resize', '50%',
                      '-o', str(crop_then_resize)])
        self.run_cli([str(self.input), '--resize', '50%', '--roi', '0,0,40,40',
                      '-o', str(resize_then_crop)])
        self.assertEqual(self.read(crop_then_resize).shape[:2], (20, 20))
        self.assertEqual(self.read(resize_then_crop).shape[:2], (30, 40))

    def test_chain_order_is_recorded_as_typed(self):
        report = self.dir / 'order.json'
        self.run_cli([str(self.input), '--histeq', '--brightness', '10', '--clahe',
                      '--report', str(report), '-o', str(self.dir / 'o.png')])
        data = json.loads(report.read_text(encoding='utf-8'))
        self.assertEqual([f['name'] for f in data['processing']['filters']],
                         ['histeq', 'contrast_brightness', 'clahe'])

    def test_chain_of_several_filters(self):
        out = self.dir / 'chained.png'
        code, _ = self.run_cli([str(self.input), '--brightness', '20', '--contrast', '1.5',
                                '--clahe', 'clip=2.0', '-o', str(out)])
        self.assertEqual(code, 0)
        self.assertTrue(out.exists())

    def test_report_records_every_step(self):
        report = self.dir / 'report.json'
        code, _ = self.run_cli([str(self.input), '--levels', '20,1.0,220', '--histeq',
                                '--report', str(report), '-o', str(self.dir / 'o.png')])
        self.assertEqual(code, 0)
        data = json.loads(report.read_text(encoding='utf-8'))
        self.assertEqual(data['processing']['filter_count'], 2)
        self.assertEqual([f['name'] for f in data['processing']['filters']],
                         ['levels', 'histeq'])
        self.assertEqual(len(data['source_file']['sha256']), 64)

    def test_markdown_report_by_extension(self):
        report = self.dir / 'report.md'
        self.run_cli([str(self.input), '--clahe', '--report', str(report),
                      '-o', str(self.dir / 'o.png')])
        self.assertIn('# Image Processing Report', report.read_text(encoding='utf-8'))

    def test_preset_roundtrip_via_cli(self):
        preset = self.dir / 'preset.json'
        direct = self.dir / 'direct.png'
        replayed = self.dir / 'replayed.png'

        # tile=8x8 parses to a tuple, which JSON stores as a list - the reload
        # path has to accept both.
        self.run_cli([str(self.input), '--brightness', '30',
                      '--clahe', 'clip=2.5', 'tile=8x8',
                      '--save-preset', str(preset), '-o', str(direct)])
        saved = json.loads(preset.read_text(encoding='utf-8'))
        self.assertEqual(saved['filters'][1]['params']['tile_grid_size'], [8, 8])

        code, _ = self.run_cli([str(self.input), '--load-preset', str(preset),
                                '-o', str(replayed)])
        self.assertEqual(code, 0)
        np.testing.assert_array_equal(self.read(direct), self.read(replayed))

    def test_compare_image_is_wider_than_both_panels(self):
        compare = self.dir / 'compare.png'
        code, _ = self.run_cli([str(self.input), '--clahe', '--compare', str(compare),
                                '-o', str(self.dir / 'o.png')])
        self.assertEqual(code, 0)
        self.assertGreaterEqual(self.read(compare).shape[1], self.image.shape[1] * 2)

    def test_analyze_roi_prints_stats(self):
        code, output = self.run_cli([str(self.input), '--analyze-roi', '0,0,10,10'])
        self.assertEqual(code, 0)
        self.assertIn('ROI analysis', output)
        self.assertIn('mean=', output)

    def test_info_prints_metadata(self):
        code, output = self.run_cli([str(self.input), '--info'])
        self.assertEqual(code, 0)
        self.assertIn('sha256', output)
        self.assertIn('input.png', output)

    def test_list_filters(self):
        code, output = self.run_cli(['--list-filters'])
        self.assertEqual(code, 0)
        self.assertIn('clahe', output)
        self.assertIn('roi_crop', output)

    def test_list_analyses(self):
        code, output = self.run_cli(['--list-analyses'])
        self.assertEqual(code, 0)
        for spec in ANALYSIS_REGISTRY.values():
            self.assertIn(spec.cli_flag, output)

    def test_every_registered_analysis_has_a_flag_that_runs_it(self):
        # The flags are generated from the registry, so a report added there
        # is reachable from the command line without the CLI being edited
        for name, spec in ANALYSIS_REGISTRY.items():
            with self.subTest(analysis=name):
                code, output = self.run_cli([str(self.input), spec.cli_flag])
                self.assertEqual(code, 0)
                self.assertIn(spec.caveat[:30], output)

    def test_pdf_report_by_extension(self):
        report = self.dir / 'report.pdf'
        code, _ = self.run_cli([str(self.input), '--clahe', '--report', str(report),
                                '-o', str(self.dir / 'o.png')])
        self.assertEqual(code, 0)
        self.assertEqual(report.read_bytes()[:5], b'%PDF-')

    def test_recursive_batch_mirrors_the_input_tree(self):
        root = self.dir / 'tree'
        (root / 'a').mkdir(parents=True)
        (root / 'b').mkdir(parents=True)
        # Same basename in two subdirectories: a flat output would lose one
        for sub in ('a', 'b'):
            cv2.imwrite(str(root / sub / 'frame.png'),
                        cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR))

        out = self.dir / 'out'
        code, output = self.run_cli([str(root), '--clahe', '--batch', '--recursive',
                                     '-o', str(out)])
        self.assertEqual(code, 0)
        self.assertIn('2/2 succeeded', output)
        self.assertTrue((out / 'a' / 'frame.png').exists())
        self.assertTrue((out / 'b' / 'frame.png').exists())

    def test_batch_without_recursive_skips_subdirectories(self):
        root = self.dir / 'tree2'
        (root / 'sub').mkdir(parents=True)
        cv2.imwrite(str(root / 'top.png'), cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR))
        cv2.imwrite(str(root / 'sub' / 'deep.png'),
                    cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR))

        out = self.dir / 'out2'
        code, output = self.run_cli([str(root), '--clahe', '--batch', '-o', str(out)])
        self.assertEqual(code, 0)
        self.assertIn('1/1 succeeded', output)
        self.assertFalse((out / 'sub').exists())

    def test_batch_processes_directory(self):
        batch_in = self.dir / 'frames'
        batch_in.mkdir()
        for i in range(3):
            cv2.imwrite(str(batch_in / f'frame{i}.png'),
                        cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR))
        batch_out = self.dir / 'enhanced'

        code, output = self.run_cli([str(batch_in), '--clahe', '--batch',
                                     '-o', str(batch_out)])
        self.assertEqual(code, 0)
        self.assertEqual(len(list(batch_out.glob('*.png'))), 3)
        self.assertIn('3/3 succeeded', output)

    def test_missing_input_file_exits_nonzero(self):
        code, _ = self.run_cli([str(self.dir / 'nope.png'), '--clahe'])
        self.assertEqual(code, 1)

    def test_batch_on_non_directory_exits_nonzero(self):
        code, _ = self.run_cli([str(self.input), '--clahe', '--batch'])
        self.assertEqual(code, 1)

    def test_no_filters_is_an_error(self):
        with self.assertRaises(SystemExit):
            self.run_cli([str(self.input), '-o', str(self.dir / 'o.png')])

    def test_bad_roi_argument_is_an_error(self):
        with self.assertRaises(SystemExit):
            self.run_cli([str(self.input), '--roi', '10,10', '-o', str(self.dir / 'o.png')])

    def test_sharpen_writes_output(self):
        out = self.dir / 'sharp.png'
        code, _ = self.run_cli([str(self.input), '--sharpen', 'amount=1.5', 'radius=1.0',
                                '-o', str(out)])
        self.assertEqual(code, 0)
        self.assertTrue(out.exists())

    def test_denoise_then_sharpen_chain(self):
        out = self.dir / 'clean.png'
        code, _ = self.run_cli([str(self.input), '--bilateral', 'd=7', 'color=50',
                                '--sharpen', 'amount=1.2', '-o', str(out)])
        self.assertEqual(code, 0)
        self.assertEqual(self.read(out).shape, self.image.shape)

    def test_gaussian_and_median_shorthand(self):
        for flag in (['--gaussian'], ['--gaussian', '1.5'], ['--median'], ['--median', '5']):
            with self.subTest(flag=flag):
                out = self.dir / 'blur.png'
                code, _ = self.run_cli([str(self.input)] + flag + ['-o', str(out)])
                self.assertEqual(code, 0)

    def test_canny_produces_grayscale_edge_map(self):
        out = self.dir / 'edges.png'
        code, _ = self.run_cli([str(self.input), '--canny', '50,150', '-o', str(out)])
        self.assertEqual(code, 0)
        edges = cv2.imread(str(out), cv2.IMREAD_UNCHANGED)
        self.assertEqual(edges.ndim, 2)
        self.assertEqual(edges.shape, self.image.shape[:2])

    def test_auto_canny_and_blur_first(self):
        out = self.dir / 'auto_edges.png'
        code, _ = self.run_cli([str(self.input), '--auto-canny', '--blur-first', '1.5',
                                '-o', str(out)])
        self.assertEqual(code, 0)
        self.assertTrue(out.exists())

    def test_sobel_and_laplacian(self):
        for flag in (['--sobel'], ['--sobel', 'dx=1', 'dy=0'], ['--laplacian', 'kernel=3']):
            with self.subTest(flag=flag):
                out = self.dir / 'grad.png'
                code, _ = self.run_cli([str(self.input)] + flag + ['-o', str(out)])
                self.assertEqual(code, 0)

    def test_histogram_chart_is_written(self):
        chart = self.dir / 'hist.png'
        code, output = self.run_cli([str(self.input), '--clahe', '--histogram', str(chart),
                                     '-o', str(self.dir / 'o.png')])
        self.assertEqual(code, 0)
        self.assertTrue(chart.exists())
        self.assertIn('Saved histogram', output)

    def test_histogram_without_any_filter(self):
        chart = self.dir / 'hist.png'
        code, _ = self.run_cli([str(self.input), '--histogram', str(chart), '--histogram-log'])
        self.assertEqual(code, 0)
        self.assertTrue(chart.exists())

    def test_hist_stats_prints_clipping(self):
        code, output = self.run_cli([str(self.input), '--hist-stats'])
        self.assertEqual(code, 0)
        self.assertIn('Histogram statistics', output)
        self.assertIn('dynamic range used', output)

    def test_hist_stats_reports_clipping_after_aggressive_levels(self):
        code, output = self.run_cli([str(self.input), '--levels', '110,1.0,130',
                                     '--hist-stats'])
        self.assertEqual(code, 0)
        self.assertIn('clipped:', output)

    def test_sprint2_preset_roundtrip(self):
        preset = self.dir / 'p.json'
        direct = self.dir / 'd.png'
        replayed = self.dir / 'r.png'
        self.run_cli([str(self.input), '--median', '3', '--sharpen', 'amount=1.5',
                      '--save-preset', str(preset), '-o', str(direct)])
        code, _ = self.run_cli([str(self.input), '--load-preset', str(preset),
                                '-o', str(replayed)])
        self.assertEqual(code, 0)
        np.testing.assert_array_equal(self.read(direct), self.read(replayed))

    def test_bad_canny_argument_is_an_error(self):
        with self.assertRaises(SystemExit):
            self.run_cli([str(self.input), '--canny', '50', '-o', str(self.dir / 'o.png')])

    def test_invalid_filter_params_exit_nonzero(self):
        # An even median kernel is rejected by the filter, not by argparse
        code, _ = self.run_cli([str(self.input), '--median', '4', '-o', str(self.dir / 'o.png')])
        self.assertEqual(code, 1)

    def test_forensic_filters_run(self):
        for flag in (['--ela'], ['--ela', 'quality=80', 'gray=true'],
                     ['--fft'], ['--fft-filter', 'type=lowpass', 'cutoff=20'],
                     ['--remove-periodic'], ['--noise-map'], ['--noise-map', '16'],
                     ['--deblur', 'length=9', 'angle=0'],
                     ['--deblur-defocus', 'radius=3'],
                     ['--ghost'], ['--ghost', 'block=8', 'min=40', 'max=100', 'step=10']):
            with self.subTest(flag=flag):
                out = self.dir / 'f.png'
                code, _ = self.run_cli([str(self.input)] + flag + ['-o', str(out)])
                self.assertEqual(code, 0)
                self.assertTrue(out.exists())

    def test_clone_detect_runs(self):
        out = self.dir / 'clones.png'
        code, _ = self.run_cli([str(self.input), '--clone-detect', 'step=4',
                                '-o', str(out)])
        self.assertEqual(code, 0)
        self.assertEqual(self.read(out).shape, self.image.shape)

    def test_noise_stats_printed(self):
        code, output = self.run_cli([str(self.input), '--noise-stats'])
        self.assertEqual(code, 0)
        self.assertIn('Noise analysis', output)
        self.assertIn('global sigma', output)
        self.assertIn('SNR', output)

    def test_ela_stats_printed_with_caveat(self):
        code, output = self.run_cli([str(self.input), '--ela-stats'])
        self.assertEqual(code, 0)
        self.assertIn('Error Level Analysis', output)
        self.assertIn('hottest block', output)
        self.assertIn('JPEG originals', output)

    def test_clone_stats_printed(self):
        code, output = self.run_cli([str(self.input), '--clone-stats'])
        self.assertEqual(code, 0)
        self.assertIn('Copy-move detection', output)
        self.assertIn('blocks analyzed', output)

    def test_ela_stats_accepts_quality(self):
        code, output = self.run_cli([str(self.input), '--ela-stats', '75'])
        self.assertEqual(code, 0)
        self.assertIn('quality 75', output)

    def test_forensic_preset_roundtrip(self):
        preset = self.dir / 'p3.json'
        direct = self.dir / 'd3.png'
        replayed = self.dir / 'r3.png'
        self.run_cli([str(self.input), '--ela', 'quality=85',
                      '--save-preset', str(preset), '-o', str(direct)])
        code, _ = self.run_cli([str(self.input), '--load-preset', str(preset),
                                '-o', str(replayed)])
        self.assertEqual(code, 0)
        np.testing.assert_array_equal(self.read(direct), self.read(replayed))

    def test_frames_requires_video(self):
        code, _ = self.run_cli([str(self.input), '--frames', '4', '--clahe',
                                '-o', str(self.dir / 'o.png')])
        self.assertEqual(code, 1)

    def test_unreadable_preset_exits_nonzero(self):
        bad = self.dir / 'bad.json'
        bad.write_text('{not json')
        code, _ = self.run_cli([str(self.input), '--load-preset', str(bad),
                                '-o', str(self.dir / 'o.png')])
        self.assertEqual(code, 1)


class TestCLICatalogue(CLITestCase):
    """The filters completing the plan's 40-item catalogue."""

    ADJUST = [
        ['--curves', 'preset=lift_shadows'],
        ['--curves', 'points=0:0,128:170,255:255'],
        ['--curves', 'preset=contrast', 'channel=r'],
        ['--s-curve'], ['--s-curve', '0.4'],
        ['--white-balance'], ['--white-balance', 'method=gray_world'],
        ['--wb-patch', '10,10,20,20'],
        ['--temperature', 'temperature=20', 'tint=-10'],
        ['--saturation', '1.4'], ['--vibrance', '1.5'],
        ['--desaturate'], ['--desaturate', 'lightness'],
        ['--color-balance', 'shadows=-15:0:15', 'highlights=15:5:-10'],
        ['--cmyk', 'cyan=10', 'yellow=-5'],
        ['--invert'], ['--invert', 'luminance'], ['--invert', 'r'],
        ['--solarize'], ['--solarize', '140'],
    ]

    ENHANCE = [
        ['--nl-means', 'h=10'], ['--nl-means-auto'],
        ['--upscale', 'scale=2', 'method=nearest'],
        ['--local-contrast', 'radius=20', 'strength=0.5'],
        ['--detail-enhance'], ['--texture-boost'],
    ]

    CORRECT = [
        ['--perspective', '5,5,70,8,72,50,3,52'],
        ['--auto-perspective'],
        ['--barrel', 'k1=-0.2', 'zoom=1.1'],
        ['--fisheye', 'strength=0.5'],
        ['--pixel-aspect', 'pal_43'], ['--pixel-aspect', '1.09'],
        ['--fit-aspect', 'ratio=1.777', 'mode=pad'],
    ]

    SPECIAL = [
        ['--component', 'lab:a'], ['--component', 'hsv:S'],
        ['--bit-plane', '0'], ['--bit-plane', '7'],
        ['--stain', 'preset=h_e', 'index=0'],
        ['--redact', '10,10,30,20'],
        ['--blocking-map'], ['--deblock'],
    ]

    def _run_each(self, flag_sets):
        for flags in flag_sets:
            with self.subTest(flags=' '.join(flags)):
                out = self.dir / 'o.png'
                code, _ = self.run_cli([str(self.input)] + flags + ['-o', str(out)])
                self.assertEqual(code, 0)
                self.assertTrue(out.exists())

    def test_adjust_filters_run(self):
        self._run_each(self.ADJUST)

    def test_enhance_filters_run(self):
        self._run_each(self.ENHANCE)

    def test_correct_filters_run(self):
        self._run_each(self.CORRECT)

    def test_special_filters_run(self):
        self._run_each(self.SPECIAL)

    def test_perspective_named_ratio(self):
        out = self.dir / 'plate.png'
        code, _ = self.run_cli([str(self.input), '--perspective', '5,5,70,8,72,50,3,52',
                                '--perspective-ratio', 'plate_eu', '-o', str(out)])
        self.assertEqual(code, 0)
        result = self.read(out)
        # The output size is whole pixels, so on a small region the achievable
        # ratio is quantised - 69x15 is the closest this crop gets to 4.73
        self.assertAlmostEqual(result.shape[1] / result.shape[0], 520 / 110, delta=0.25)

    def test_unknown_perspective_ratio_is_an_error(self):
        with self.assertRaises(SystemExit):
            self.run_cli([str(self.input), '--perspective', '5,5,70,8,72,50,3,52',
                          '--perspective-ratio', 'betamax', '-o', str(self.dir / 'o.png')])

    def test_redact_method_reaches_the_filter(self):
        filled = self.dir / 'filled.png'
        pixelated = self.dir / 'pixelated.png'
        self.run_cli([str(self.input), '--redact', '10,10,30,20', '-o', str(filled)])
        self.run_cli([str(self.input), '--redact', '10,10,30,20',
                      '--redact-method', 'pixelate', '-o', str(pixelated)])

        # fill blanks the region outright; pixelate leaves structure behind
        self.assertEqual(int(self.read(filled)[10:30, 10:40].max()), 0)
        self.assertGreater(int(self.read(pixelated)[10:30, 10:40].max()), 0)

    def test_undistort_uses_a_calibration_file(self):
        from src.filters import CameraCalibration, save_calibration
        path = self.dir / 'cal.json'
        save_calibration(CameraCalibration(
            np.array([[80.0, 0, 40], [0, 80.0, 30], [0, 0, 1]]),
            np.array([-0.2, 0.05, 0.0, 0.0, 0.0]), (80, 60), 0.5), path)

        out = self.dir / 'undistorted.png'
        code, _ = self.run_cli([str(self.input), '--undistort', str(path), '-o', str(out)])
        self.assertEqual(code, 0)
        self.assertEqual(self.read(out).shape[:2], self.image.shape[:2])

    def test_compression_stats_printed(self):
        code, output = self.run_cli([str(self.input), '--compression-stats'])
        self.assertEqual(code, 0)
        self.assertIn('Compression analysis', output)
        self.assertIn('blockiness', output)

    def test_compression_stats_reads_jpeg_quality(self):
        jpeg = self.dir / 'q60.jpg'
        cv2.imwrite(str(jpeg), cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR),
                    [int(cv2.IMWRITE_JPEG_QUALITY), 60])
        code, output = self.run_cli([str(jpeg), '--compression-stats'])
        self.assertEqual(code, 0)
        self.assertIn('estimated quality', output)

    def test_ghost_stats_printed(self):
        code, output = self.run_cli([str(self.input), '--ghost-stats'])
        self.assertEqual(code, 0)
        self.assertIn('JPEG ghost', output)
        # Without a region it says what it cannot do rather than guessing
        self.assertIn('does not search for one', output)

    def test_metadata_stats_printed(self):
        code, output = self.run_cli([str(self.input), '--metadata-stats'])
        self.assertEqual(code, 0)
        self.assertIn('Metadata forensics', output)
        self.assertIn('EXIF', output)

    def test_metadata_stats_reports_findings(self):
        from PIL import Image
        path = self.dir / 'edited.jpg'
        image = Image.fromarray(self.image)
        tags = image.getexif()
        tags[305] = 'Adobe Photoshop 25.0'
        image.save(path, 'JPEG', exif=tags, quality=90)

        code, output = self.run_cli([str(path), '--metadata-stats'])
        self.assertEqual(code, 0)
        self.assertIn('[FLAG]', output)
        self.assertIn('editing_software', output)

    def test_catalogue_filters_survive_a_preset_roundtrip(self):
        preset = self.dir / 'p.json'
        direct = self.dir / 'd.png'
        replayed = self.dir / 'r.png'

        self.run_cli([str(self.input), '--curves', 'preset=film',
                      '--white-balance', '--saturation', '1.2', '--invert', 'luminance',
                      '--save-preset', str(preset), '-o', str(direct)])
        code, _ = self.run_cli([str(self.input), '--load-preset', str(preset),
                                '-o', str(replayed)])
        self.assertEqual(code, 0)
        np.testing.assert_array_equal(self.read(direct), self.read(replayed))

    def test_malformed_arguments_are_errors(self):
        cases = [
            ['--component', 'lab'],            # missing the channel
            ['--pixel-aspect', 'betamax'],     # unknown format
            ['--fit-aspect', 'mode=pad'],      # missing the ratio
            ['--perspective', '1,2,3'],        # needs 8 numbers
            ['--invert', 'sideways'],          # not a channel or mode
        ]
        for flags in cases:
            with self.subTest(flags=' '.join(flags)):
                with self.assertRaises(SystemExit):
                    self.run_cli([str(self.input)] + flags + ['-o', str(self.dir / 'o.png')])

    def test_every_registered_filter_is_listed(self):
        from src.filters import FILTER_REGISTRY
        code, output = self.run_cli(['--list-filters'])
        self.assertEqual(code, 0)
        for name in FILTER_REGISTRY:
            self.assertIn(name, output)


class TestCLIMeasurement(CLITestCase):
    """
    The measurement and annotation flags.

    The calibration is a modifier shared by every measurement in the chain,
    because a scale belongs to an image plane rather than to one measurement.
    """

    CALIBRATION = ['--scale-ref', '10,10,60,10', '--scale-length', '520']

    def test_measure_draws_a_dimension_line(self):
        out = self.dir / 'measured.png'
        code, _ = self.run_cli([str(self.input), *self.CALIBRATION,
                                '--measure', '10,30,60,30', '-o', str(out)])
        self.assertEqual(code, 0)
        result = self.read(out)
        self.assertEqual(result.shape[:2], self.image.shape[:2])
        self.assertFalse(np.array_equal(result, self.image))

    def test_measure_works_without_a_calibration(self):
        out = self.dir / 'pixels.png'
        code, _ = self.run_cli([str(self.input), '--measure', '10,30,60,30',
                                '-o', str(out)])
        self.assertEqual(code, 0)
        self.assertFalse(np.array_equal(self.read(out), self.image))

    def test_measure_area_accepts_more_than_four_vertices(self):
        out = self.dir / 'area.png'
        code, _ = self.run_cli([str(self.input), '--measure-area',
                                '5,5,40,5,50,25,25,45,5,25', '-o', str(out)])
        self.assertEqual(code, 0)
        self.assertFalse(np.array_equal(self.read(out), self.image))

    def test_scale_bar_needs_a_calibration(self):
        with self.assertRaises(SystemExit):
            self.run_cli([str(self.input), '--scale-bar', '100',
                          '-o', str(self.dir / 'o.png')])

    def test_scale_bar_draws_with_a_calibration(self):
        out = self.dir / 'bar.png'
        code, _ = self.run_cli([str(self.input), *self.CALIBRATION,
                                '--scale-bar', '200',
                                '--scale-bar-position', 'top_left',
                                '-o', str(out)])
        self.assertEqual(code, 0)
        self.assertFalse(np.array_equal(self.read(out), self.image))

    def test_annotation_flags_draw(self):
        cases = {
            'arrow': ['--arrow', 'start=50,10', 'end=20,30', 'label=plate'],
            'text': ['--text', 'text=Exhibit_A', 'position=5,15'],
            'shape': ['--shape', 'shape=rectangle', 'points=5,5,40,30'],
        }
        for name, flags in cases.items():
            with self.subTest(flag=name):
                out = self.dir / f'{name}.png'
                code, _ = self.run_cli([str(self.input), *flags, '-o', str(out)])
                self.assertEqual(code, 0)
                self.assertFalse(np.array_equal(self.read(out), self.image))

    def test_one_calibration_serves_every_measurement_in_the_chain(self):
        out = self.dir / 'both.png'
        code, _ = self.run_cli([str(self.input), *self.CALIBRATION,
                                '--measure', '10,30,60,30',
                                '--measure-area', '5,40,40,40,40,55,5,55',
                                '-o', str(out)])
        self.assertEqual(code, 0)
        self.assertFalse(np.array_equal(self.read(out), self.image))

    def test_malformed_measurement_flags_are_rejected(self):
        cases = [
            ['--measure', '10,30,60'],                    # needs 4 numbers
            ['--measure-area', '10,30,60,40'],            # only 2 vertices
            ['--measure-area', '10,30,60,40,50'],         # odd count
            ['--measure', '10,30,60,30', '--scale-ref', '1,2,3,4'],  # no length
            ['--text', 'position=5,15'],                  # no text
            ['--shape', 'points=5,5,40,30'],              # no shape
            ['--shape', 'shape=rectangle'],               # no points
        ]
        for flags in cases:
            with self.subTest(flags=' '.join(flags)):
                with self.assertRaises(SystemExit):
                    self.run_cli([str(self.input)] + flags
                                 + ['-o', str(self.dir / 'o.png')])


class TestCLIVideo(CLITestCase):
    """Multi-frame input, which needs a real video file to exercise."""

    def setUp(self):
        super().setUp()
        self.video = self.dir / 'clip.avi'
        rng = np.random.default_rng(31)
        base = np.zeros((48, 64, 3), dtype=np.uint8)
        base[:, :32] = (60, 90, 140)
        base[:, 32:] = (180, 150, 90)

        writer = cv2.VideoWriter(
            str(self.video), cv2.VideoWriter_fourcc(*'MJPG'), 10, (64, 48))
        if not writer.isOpened():
            self.skipTest("MJPG video writer unavailable in this environment")
        try:
            for index in range(12):
                frame = np.clip(
                    base.astype(np.float32) + rng.normal(0, 22, base.shape), 0, 255
                ).astype(np.uint8)
                # A bright square crossing the scene, present in every frame
                # at a different place - the median should erase it
                x = 2 + index * 4
                frame[10:24, x:x + 10] = 255
                writer.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        finally:
            writer.release()

    def test_single_frame_loads_by_default(self):
        out = self.dir / 'frame.png'
        code, _ = self.run_cli([str(self.video), '--clahe', '-o', str(out)])
        self.assertEqual(code, 0)
        self.assertEqual(self.read(out).shape[:2], (48, 64))

    def test_frame_index_selects_a_different_frame(self):
        first, later = self.dir / 'f0.png', self.dir / 'f8.png'
        self.run_cli([str(self.video), '--frame', '0', '--clahe', '-o', str(first)])
        self.run_cli([str(self.video), '--frame', '8', '--clahe', '-o', str(later)])
        self.assertFalse(np.array_equal(self.read(first), self.read(later)))

    def test_frames_mean_reduces_noise(self):
        single, averaged = self.dir / 'one.png', self.dir / 'avg.png'
        self.run_cli([str(self.video), '--frame', '0', '--gaussian', '0.01',
                      '-o', str(single)])
        code, _ = self.run_cli([str(self.video), '--frames', '12',
                                '--gaussian', '0.01', '-o', str(averaged)])
        self.assertEqual(code, 0)
        self.assertLess(estimate_noise(self.read(averaged)),
                        estimate_noise(self.read(single)))

    def test_frames_median_removes_the_moving_object(self):
        out = self.dir / 'median.png'
        code, _ = self.run_cli([str(self.video), '--frames', '12',
                                '--frame-method', 'median', '-o', str(out)])
        self.assertEqual(code, 0)
        result = self.read(out)
        # The bright square occupied rows 10-24 in every frame but never the
        # same columns, so the median should show no pure-white pixels there
        self.assertLess((result[10:24] > 245).mean(), 0.05)

    def test_all_frame_methods_run(self):
        for method in ('mean', 'median', 'integrate', 'sharpest'):
            with self.subTest(method=method):
                out = self.dir / f'{method}.png'
                code, _ = self.run_cli([str(self.video), '--frames', '6',
                                        '--frame-method', method, '-o', str(out)])
                self.assertEqual(code, 0)
                self.assertTrue(out.exists())

    def test_frame_step_spreads_the_sample(self):
        out = self.dir / 'stepped.png'
        code, _ = self.run_cli([str(self.video), '--frames', '4', '--frame-step', '3',
                                '--frame-method', 'median', '-o', str(out)])
        self.assertEqual(code, 0)

    def test_loader_rejects_frames_on_a_still(self):
        with ImageLoader(self.input) as loader:
            with self.assertRaises(ValueError):
                loader.load_frames(4)

    def test_loader_stops_at_end_of_video(self):
        with ImageLoader(self.video) as loader:
            frames = loader.load_frames(500)
        self.assertGreater(len(frames), 0)
        self.assertLess(len(frames), 500)

    def test_goto_frame_seeks_and_tracks_position(self):
        with ImageLoader(self.video) as loader:
            loader.goto_frame(5)
            self.assertEqual(loader.current_frame_index, 5)
            first = loader.goto_frame(0)
            self.assertEqual(loader.current_frame_index, 0)
            np.testing.assert_array_equal(first, loader.goto_frame(0))

    def test_next_and_previous_walk_the_video(self):
        with ImageLoader(self.video) as loader:
            loader.goto_frame(3)
            loader.next_frame()
            self.assertEqual(loader.current_frame_index, 4)
            loader.previous_frame()
            self.assertEqual(loader.current_frame_index, 3)

    def test_next_frame_returns_none_at_the_end(self):
        with ImageLoader(self.video) as loader:
            last = loader.get_video_frame_count() - 1
            loader.goto_frame(last)
            self.assertIsNone(loader.next_frame())
            self.assertEqual(loader.current_frame_index, last)

    def test_previous_frame_returns_none_at_the_start(self):
        with ImageLoader(self.video) as loader:
            loader.goto_frame(0)
            self.assertIsNone(loader.previous_frame())

    def test_goto_frame_rejects_out_of_range(self):
        with ImageLoader(self.video) as loader:
            with self.assertRaises(ValueError):
                loader.goto_frame(-1)
            with self.assertRaises(ValueError):
                loader.goto_frame(loader.get_video_frame_count() + 10)

    def test_navigation_reads_distinct_frames(self):
        with ImageLoader(self.video) as loader:
            frame_a = loader.goto_frame(1)
            frame_b = loader.next_frame()
            self.assertFalse(np.array_equal(frame_a, frame_b))

    def test_load_frames_updates_the_navigation_cursor(self):
        with ImageLoader(self.video) as loader:
            loader.load_frames(4, start=0, step=2)
            self.assertEqual(loader.current_frame_index, 6)

    def test_loader_rejects_bad_frame_arguments(self):
        with ImageLoader(self.video) as loader:
            for kwargs in ({'count': 0}, {'count': 4, 'step': 0}, {'count': 4, 'start': -1}):
                with self.subTest(kwargs=kwargs):
                    with self.assertRaises(ValueError):
                        loader.load_frames(**kwargs)


class TestCLIStabilise(CLITestCase):
    """
    Aligning a stack of stills before combining it.

    The frames are a known image moved by known amounts, so the assertion can
    be that the motion was undone rather than that a file appeared.
    """

    def setUp(self):
        super().setUp()
        rng = np.random.default_rng(19)
        noise = cv2.GaussianBlur(
            rng.integers(0, 255, (120, 160), dtype=np.uint8), (5, 5), 2)
        self.clean = cv2.cvtColor(noise, cv2.COLOR_GRAY2RGB)
        cv2.rectangle(self.clean, (30, 30), (90, 75), (255, 80, 40), -1)
        cv2.putText(self.clean, 'AB 123', (20, 108), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (250, 250, 250), 2, cv2.LINE_AA)

        self.stack = self.dir / 'stack'
        self.stack.mkdir()
        for index in range(8):
            dx = 4 * np.sin(index * 0.6) + rng.normal(0, 0.8)
            dy = 3 * np.cos(index * 0.5) + rng.normal(0, 0.8)
            matrix = cv2.getRotationMatrix2D((80, 60), 1.0 * np.sin(index * 0.4), 1.0)
            matrix[0, 2] += dx
            matrix[1, 2] += dy
            frame = cv2.warpAffine(self.clean, matrix, (160, 120),
                                   borderMode=cv2.BORDER_REFLECT)
            frame = np.clip(frame.astype(np.float32)
                            + rng.normal(0, 14, frame.shape), 0, 255).astype(np.uint8)
            cv2.imwrite(str(self.stack / f'f{index:02d}.png'),
                        cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

    def _psnr(self, a, b):
        error = np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2)
        return 99.0 if error == 0 else float(10 * np.log10(255 * 255 / error))

    def test_stabilising_sharpens_the_average(self):
        naive, stabilised = self.dir / 'naive.png', self.dir / 'stab.png'
        self.run_cli([str(self.stack), '--frames', '8', '-o', str(naive)])
        code, _ = self.run_cli([str(self.stack), '--frames', '8',
                                '--stabilise', '-o', str(stabilised)])
        self.assertEqual(code, 0)

        aligned = self.read(stabilised)
        # The output is cropped to the common region; locate it in the truth
        match = cv2.matchTemplate(self.clean, aligned, cv2.TM_SQDIFF)
        _, _, (x, y), _ = cv2.minMaxLoc(match)
        height, width = aligned.shape[:2]
        truth = self.clean[y:y + height, x:x + width]

        raw = self.read(naive)[y:y + height, x:x + width]
        self.assertGreater(self._psnr(aligned, truth),
                           self._psnr(raw, truth) + 1.0)

    def test_stabilising_crops_to_the_common_region(self):
        out = self.dir / 'cropped.png'
        self.run_cli([str(self.stack), '--frames', '8', '--stabilise',
                      '-o', str(out)])
        result = self.read(out)
        self.assertLess(result.shape[0], 120)
        self.assertLess(result.shape[1], 160)

    def test_every_motion_model_is_accepted(self):
        for model in ('translation', 'euclidean', 'affine', 'homography'):
            with self.subTest(model=model):
                out = self.dir / f'{model}.png'
                code, _ = self.run_cli([str(self.stack), '--frames', '6',
                                        '--stabilise', model, '-o', str(out)])
                self.assertEqual(code, 0)
                self.assertTrue(out.exists())

    def test_the_american_spelling_works_too(self):
        out = self.dir / 'z.png'
        code, _ = self.run_cli([str(self.stack), '--frames', '6',
                                '--stabilize', 'euclidean', '-o', str(out)])
        self.assertEqual(code, 0)

    def test_the_report_records_the_alignment(self):
        out, report = self.dir / 'r.png', self.dir / 'r.md'
        code, _ = self.run_cli([str(self.stack), '--frames', '8', '--stabilise',
                                '--report', str(report), '-o', str(out)])
        self.assertEqual(code, 0)

        text = report.read_text(encoding='utf-8')
        self.assertIn('Frame Alignment', text)
        self.assertIn('euclidean motion model', text)
        self.assertIn('| Frame | Method | Confidence |', text)
        # The raw dict must not also be dumped into the metadata list
        self.assertNotIn("'per_frame'", text)

    def test_an_unknown_model_is_rejected(self):
        with self.assertRaises(SystemExit):
            self.run_cli([str(self.stack), '--frames', '8', '--stabilise',
                          'wobble', '-o', str(self.dir / 'o.png')])


class TestCLISuperResolution(CLITestCase):
    """
    Multi-frame reconstruction from the command line.

    The frames are made the way the method assumes: one high-resolution truth,
    shifted by known sub-pixel amounts and downsampled. That gives a real
    answer to compare against, so the test can assert reconstruction beat
    interpolation rather than merely that a larger file appeared.
    """

    def setUp(self):
        super().setUp()
        self.truth = np.zeros((160, 240), dtype=np.uint8)
        cv2.putText(self.truth, 'AB 12', (20, 95), cv2.FONT_HERSHEY_SIMPLEX,
                    1.4, 255, 4, cv2.LINE_AA)
        for x in range(0, 240, 16):
            cv2.line(self.truth, (x, 120), (x, 150), 200, 1)

        # Offsets covering the half-pixel grid, which is the sampling pattern
        # a 2x reconstruction actually needs
        self.stack = self.dir / 'sr'
        self.stack.mkdir()
        for index, (dx, dy) in enumerate([(0, 0), (1, 0), (0, 1), (1, 1)] * 3):
            matrix = np.float32([[1, 0, dx], [0, 1, dy]])
            moved = cv2.warpAffine(self.truth, matrix, (240, 160),
                                   flags=cv2.INTER_CUBIC,
                                   borderMode=cv2.BORDER_REFLECT)
            small = cv2.resize(moved, (120, 80), interpolation=cv2.INTER_AREA)
            cv2.imwrite(str(self.stack / f'f{index:02d}.png'), small)

        self.still = self.dir / 'still'
        self.still.mkdir()
        rng = np.random.default_rng(23)
        flat = cv2.resize(self.truth, (120, 80), interpolation=cv2.INTER_AREA)
        for index in range(6):
            noisy = np.clip(flat.astype(np.float32) + rng.normal(0, 6, flat.shape),
                            0, 255).astype(np.uint8)
            cv2.imwrite(str(self.still / f'f{index}.png'), noisy)

    def _psnr(self, a, b):
        error = np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2)
        return 99.0 if error == 0 else float(10 * np.log10(255 * 255 / error))

    def test_reconstruction_enlarges_by_the_scale(self):
        out = self.dir / 'sr.png'
        code, _ = self.run_cli([str(self.stack), '--frames', '12',
                                '--frame-method', 'superres', '-o', str(out)])
        self.assertEqual(code, 0)
        self.assertEqual(self.read(out).shape[:2], (160, 240))

    def test_scale_is_configurable(self):
        out = self.dir / 'sr3.png'
        code, _ = self.run_cli([str(self.stack), '--frames', '12',
                                '--frame-method', 'superres',
                                '--sr-scale', '3', '-o', str(out)])
        self.assertEqual(code, 0)
        self.assertEqual(self.read(out).shape[:2], (240, 360))

    def test_reconstruction_beats_interpolating_one_frame(self):
        """The claim the method makes, against ground truth."""
        reconstructed, interpolated = self.dir / 'sr.png', self.dir / 'up.png'
        self.run_cli([str(self.stack), '--frames', '12', '--frame-method',
                      'superres', '-o', str(reconstructed)])
        self.run_cli([str(self.stack / 'f00.png'), '--upscale', 'scale=2',
                      '-o', str(interpolated)])

        truth = cv2.cvtColor(self.truth, cv2.COLOR_GRAY2RGB)
        self.assertGreater(self._psnr(self.read(reconstructed), truth),
                           self._psnr(self.read(interpolated), truth) + 0.5)

    def test_a_sequence_without_sub_pixel_motion_is_flagged(self):
        """
        Reconstruction without motion is an upscale wearing its name.

        The warning goes to stderr, which run_cli does not return, so this
        checks the run still succeeds and asserts on the report instead.
        """
        from src.filters import super_resolve_report

        frames = [self.read(path)
                  for path in sorted(self.still.glob('*.png'))]
        self.assertFalse(super_resolve_report(frames)['usable'])

        out = self.dir / 'flat.png'
        code, _ = self.run_cli([str(self.still), '--frames', '6',
                                '--frame-method', 'superres', '-o', str(out)])
        self.assertEqual(code, 0)

    def test_stabilising_first_removes_what_reconstruction_needs(self):
        """
        The two features work against each other, and the guard notices.

        Aligning to sub-pixel accuracy is exactly the motion reconstruction
        feeds on, so a stabilised stack reports as unusable. Nothing forbids
        the combination - it is measured rather than ruled out.
        """
        from src.filters import align_frames, super_resolve_report

        frames = [self.read(path) for path in sorted(self.stack.glob('*.png'))]
        self.assertTrue(super_resolve_report(frames)['usable'])

        aligned, _ = align_frames(frames, model='translation', crop=False)
        after = super_resolve_report(aligned)
        self.assertLess(after['frames_with_subpixel_motion'],
                        super_resolve_report(frames)['frames_with_subpixel_motion'])


class TestCLIVideoOutput(CLITestCase):
    """Applying the chain across a frame range and writing video back out."""

    def setUp(self):
        super().setUp()
        self.clip = self.dir / 'clip.avi'
        rng = np.random.default_rng(29)
        base = np.zeros((64, 80, 3), dtype=np.uint8)
        base[:, :40] = (60, 90, 140)
        base[:, 40:] = (180, 150, 90)

        writer = cv2.VideoWriter(str(self.clip),
                                 cv2.VideoWriter_fourcc(*'MJPG'), 12, (80, 64))
        if not writer.isOpened():
            self.skipTest('MJPG video writer unavailable in this environment')
        try:
            for index in range(20):
                frame = np.clip(base.astype(np.float32)
                                + rng.normal(0, 12, base.shape), 0, 255).astype(np.uint8)
                cv2.rectangle(frame, (2 + index * 3, 20), (10 + index * 3, 44),
                              (255, 255, 255), -1)
                writer.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        finally:
            writer.release()

    def frames_of(self, path):
        capture = cv2.VideoCapture(str(path))
        out = []
        try:
            while True:
                ok, frame = capture.read()
                if not ok:
                    break
                out.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        finally:
            capture.release()
        return out

    def test_the_chain_runs_over_every_frame(self):
        out = self.dir / 'out.avi'
        code, _ = self.run_cli([str(self.clip), '--video', '--clahe',
                                '-o', str(out)])
        self.assertEqual(code, 0)
        self.assertEqual(len(self.frames_of(out)), 20)

    def test_a_range_can_be_selected(self):
        out = self.dir / 'range.avi'
        code, _ = self.run_cli([str(self.clip), '--video', '--frame', '5',
                                '--video-frames', '6', '-o', str(out)])
        self.assertEqual(code, 0)
        self.assertEqual(len(self.frames_of(out)), 6)

    def test_a_stride_thins_the_sequence(self):
        out = self.dir / 'strided.avi'
        code, _ = self.run_cli([str(self.clip), '--video', '--frame-step', '4',
                                '-o', str(out)])
        self.assertEqual(code, 0)
        self.assertEqual(len(self.frames_of(out)), 5)

    def test_the_output_is_lossless_by_default(self):
        """
        Writing a range with no filters must return the pixels unchanged.

        This is the guarantee the FFV1 default exists for: passing an exhibit
        through the tool should not add a compression generation.
        """
        out = self.dir / 'copy.avi'
        code, _ = self.run_cli([str(self.clip), '--video', '-o', str(out)])
        self.assertEqual(code, 0)

        source, written = self.frames_of(self.clip), self.frames_of(out)
        self.assertEqual(len(source), len(written))
        for index, (before, after) in enumerate(zip(source, written)):
            with self.subTest(frame=index):
                np.testing.assert_array_equal(after, before)

    def test_the_chain_actually_changed_the_frames(self):
        plain, filtered = self.dir / 'p.avi', self.dir / 'f.avi'
        self.run_cli([str(self.clip), '--video', '-o', str(plain)])
        self.run_cli([str(self.clip), '--video', '--invert', '-o', str(filtered)])
        self.assertFalse(np.array_equal(self.frames_of(plain)[0],
                                        self.frames_of(filtered)[0]))

    def test_a_codec_can_be_named(self):
        out = self.dir / 'mjpg.avi'
        code, _ = self.run_cli([str(self.clip), '--video', '--codec', 'MJPG',
                                '-o', str(out)])
        self.assertEqual(code, 0)
        self.assertEqual(len(self.frames_of(out)), 20)

    def test_video_needs_an_output_path(self):
        code, _ = self.run_cli([str(self.clip), '--video', '--clahe'])
        self.assertEqual(code, 1)

    def test_video_needs_a_video_input(self):
        code, _ = self.run_cli([str(self.input), '--video', '--clahe',
                                '-o', str(self.dir / 'x.avi')])
        self.assertEqual(code, 1)

    def test_a_start_past_the_end_is_refused(self):
        code, _ = self.run_cli([str(self.clip), '--video', '--frame', '500',
                                '-o', str(self.dir / 'y.avi')])
        self.assertEqual(code, 1)

    def test_the_report_describes_the_run(self):
        out, report = self.dir / 'r.avi', self.dir / 'r.md'
        code, _ = self.run_cli([str(self.clip), '--video', '--clahe',
                                '--report', str(report), '-o', str(out)])
        self.assertEqual(code, 0)

        text = report.read_text(encoding='utf-8')
        self.assertIn('frames_written', text)
        self.assertIn('output_codec', text)
        self.assertIn('clahe', text)


if __name__ == '__main__':
    unittest.main()
