"""
Batch mode over a directory that looks like real evidence.

This is the path most likely to meet a real case - a folder of frames in
whatever formats the camera, the exporter and the recipient happened to
produce - and it had no test for the first twenty hours of the validation
campaign. What it needs to survive is a mixture of formats, a file that is not
an image, a file that is corrupt, and a subdirectory.
"""

import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

import numpy as np
from PIL import Image

from cv_tools.cli import main


def bands(height: int = 48, width: int = 96) -> np.ndarray:
    """Pure red, green and blue thirds - unmistakable after processing."""
    frame = np.zeros((height, width, 3), np.uint8)
    third = width // 3
    frame[:, :third] = (255, 0, 0)
    frame[:, third:2 * third] = (0, 255, 0)
    frame[:, 2 * third:] = (0, 0, 255)
    return frame


class TestBatch(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.source = self.root / 'evidence'
        (self.source / 'day2').mkdir(parents=True)
        self.addCleanup(self._tmp.cleanup)

    def run_cli(self, argv):
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(argv)
        return code, out.getvalue(), err.getvalue()

    def populate(self, formats=('a.png', 'b.jpg', 'c.jpeg', 'd.bmp', 'e.tif',
                                'f.webp')):
        for name in formats:
            Image.fromarray(bands()).save(self.source / name)
        Image.fromarray(bands()).save(self.source / 'day2' / 'g.png')

    def test_every_supported_format_is_processed(self):
        self.populate()
        out = self.root / 'out'
        code, stdout, _ = self.run_cli([str(self.source), '--gamma', '0.9',
                                        '--batch', '-o', str(out)])

        self.assertEqual(code, 0)
        produced = sorted(p.name for p in out.glob('*') if p.is_file())
        self.assertEqual(produced,
                         ['a.png', 'b.jpg', 'c.jpeg', 'd.bmp', 'e.tif', 'f.webp'])
        self.assertIn('6/6 succeeded', stdout)

    def test_a_file_that_is_not_an_image_is_not_treated_as_one(self):
        self.populate(('a.png',))
        (self.source / 'notes.txt').write_text('not an image', encoding='utf-8')

        out = self.root / 'out'
        code, stdout, _ = self.run_cli([str(self.source), '--gamma', '0.9',
                                        '--batch', '-o', str(out)])
        self.assertEqual(code, 0)
        self.assertIn('1/1 succeeded', stdout)

    def test_one_corrupt_file_does_not_abandon_the_batch(self):
        # The case that matters: a single unreadable frame in a folder of
        # hundreds must not cost the other hundreds
        self.populate(('a.png', 'b.png'))
        (self.source / 'broken.png').write_bytes(b'\x89PNG\r\n\x1a\n' + b'x' * 40)

        out = self.root / 'out'
        code, stdout, stderr = self.run_cli([str(self.source), '--gamma', '0.9',
                                             '--batch', '-o', str(out)])

        # The good ones are through, the bad one is named, and the exit code
        # says something went wrong
        self.assertEqual(sorted(p.name for p in out.glob('*.png')),
                         ['a.png', 'b.png'])
        self.assertIn('2/3 succeeded', stdout)
        self.assertIn('broken.png', stderr)
        self.assertEqual(code, 1)

    def test_recursive_mirrors_the_input_tree(self):
        self.populate(('a.png',))
        out = self.root / 'out'
        code, _, _ = self.run_cli([str(self.source), '--gamma', '0.9', '--batch',
                                   '--recursive', '-o', str(out)])

        self.assertEqual(code, 0)
        self.assertTrue((out / 'a.png').exists())
        self.assertTrue((out / 'day2' / 'g.png').exists())

    def test_colour_survives_the_batch(self):
        self.populate(('a.png', 'b.png'))
        out = self.root / 'out'
        self.run_cli([str(self.source), '--gamma', '0.9', '--batch', '-o', str(out)])

        for name in ('a.png', 'b.png'):
            with self.subTest(image=name):
                result = np.array(Image.open(out / name).convert('RGB'))
                row = result.shape[0] // 2
                third = result.shape[1] // 3
                dominant = [int(np.argmax(result[row, x]))
                            for x in (third // 2, third + third // 2,
                                      2 * third + third // 2)]
                self.assertEqual(dominant, [0, 1, 2])

    def test_the_report_and_preset_are_written_once_not_per_file(self):
        # Per-file reports would overwrite each other and leave whichever
        # frame happened to be last
        self.populate(('a.png', 'b.png', 'c.png'))
        out = self.root / 'out'
        report = self.root / 'report.md'
        preset = self.root / 'preset.json'

        code, _, _ = self.run_cli([str(self.source), '--gamma', '0.9', '--batch',
                                   '-o', str(out), '--report', str(report),
                                   '--save-preset', str(preset)])

        self.assertEqual(code, 0)
        self.assertTrue(report.exists())
        self.assertTrue(preset.exists())

        recorded = json.loads(preset.read_text(encoding='utf-8'))
        self.assertEqual([step['name'] for step in recorded['filters']],
                         ['contrast_brightness'])

    def test_batch_on_a_file_rather_than_a_directory_is_refused(self):
        self.populate(('a.png',))
        code, _, stderr = self.run_cli([str(self.source / 'a.png'), '--gamma',
                                        '0.9', '--batch', '-o',
                                        str(self.root / 'out')])
        self.assertEqual(code, 1)
        self.assertIn('requires a directory', stderr)

    def test_an_empty_directory_says_so(self):
        code, _, stderr = self.run_cli([str(self.source / 'day2'), '--gamma',
                                        '0.9', '--batch', '-o',
                                        str(self.root / 'out')])
        self.assertEqual(code, 1)
        self.assertIn('no supported images', stderr)

class TestStillSequence(unittest.TestCase):
    """--frames over a directory of stills, not only a video."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.source = self.root / 'frames'
        self.source.mkdir()
        self.addCleanup(self._tmp.cleanup)

    def run_cli(self, argv):
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(argv)
        return code, out.getvalue(), err.getvalue()

    def write_noisy(self, count: int, sigma: float = 12.0):
        rng = np.random.default_rng(11)
        base = np.full((64, 96, 3), 128.0)
        for index in range(count):
            frame = np.clip(base + rng.normal(0, sigma, base.shape),
                            0, 255).astype(np.uint8)
            Image.fromarray(frame).save(self.source / f'{index:03d}.png')

    def test_averaging_stills_reduces_noise(self):
        from cv_tools.filters import estimate_noise

        self.write_noisy(16)
        out = self.root / 'averaged.png'
        code, _, _ = self.run_cli([str(self.source), '--frames', '16',
                                   '--frame-method', 'mean', '-o', str(out)])
        self.assertEqual(code, 0)

        one = np.array(Image.open(self.source / '000.png').convert('RGB'))
        combined = np.array(Image.open(out).convert('RGB'))
        # Independent noise, so the sqrt(N) law should very nearly hold
        self.assertGreater(estimate_noise(one) / estimate_noise(combined), 3.0)

    def test_a_directory_of_one_image_is_refused(self):
        self.write_noisy(1)
        code, _, stderr = self.run_cli([str(self.source), '--frames', '4',
                                        '-o', str(self.root / 'x.png')])
        self.assertEqual(code, 1)
        self.assertIn('at least 2 images', stderr)

    def test_frames_of_different_sizes_are_refused(self):
        self.write_noisy(2)
        Image.fromarray(np.zeros((32, 32, 3), np.uint8)).save(self.source / 'zz.png')

        code, _, stderr = self.run_cli([str(self.source), '--frames', '3',
                                        '-o', str(self.root / 'x.png')])
        self.assertEqual(code, 1)
        self.assertIn('must share a size', stderr)

    def test_the_metadata_records_what_was_combined(self):
        self.write_noisy(4)
        code, stdout, _ = self.run_cli([str(self.source), '--frames', '4',
                                        '--info', '-o', str(self.root / 'x.png')])
        self.assertEqual(code, 0)
        self.assertIn('4 frames from frames', stdout)

    def test_a_still_file_still_refuses_frames(self):
        self.write_noisy(2)
        code, _, stderr = self.run_cli([str(self.source / '000.png'), '--frames', '2',
                                        '-o', str(self.root / 'x.png')])
        self.assertEqual(code, 1)
        self.assertIn('needs a video or a directory', stderr)

if __name__ == '__main__':
    unittest.main()
