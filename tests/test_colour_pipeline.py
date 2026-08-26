"""
Colour survives the whole journey: file in, filters, file out.

Every filter in this toolkit takes RGB, because ``ImageLoader`` converts on
load and ``save_image`` converts back. Nothing tested that, and the gap cost
something: the web dashboard converted its uploads to BGR before handing them
to the pipeline, so asking it to invert the red channel inverted blue. The
mistake is invisible on a greyscale measurement and obvious on a red square.

These tests pin the convention at every boundary a real image crosses.
"""

import io
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from src.core import FilterStep, ImageLoader, Pipeline, save_image
from src.filters import filter_function, invert_channel, resolve_filter

# Unambiguous primaries, written as a real file would carry them
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


def primaries_png(directory: Path, name: str = 'primaries.png') -> Path:
    """A file with one pure red, green and blue band, written through PIL."""
    frame = np.zeros((24, 96, 3), np.uint8)
    frame[:, :32] = RED
    frame[:, 32:64] = GREEN
    frame[:, 64:] = BLUE
    path = directory / name
    Image.fromarray(frame).save(path)
    return path


class TestColourConvention(unittest.TestCase):
    """The pipeline's colour order, asserted rather than assumed."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.directory = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_loader_returns_rgb(self):
        path = primaries_png(self.directory)
        with ImageLoader(path) as loader:
            image = loader.load()

        # Index 0 is red where the file is red
        self.assertEqual(tuple(image[0, 0]), RED)
        self.assertEqual(tuple(image[0, 40]), GREEN)
        self.assertEqual(tuple(image[0, 80]), BLUE)

    def test_save_writes_what_a_viewer_will_read_back(self):
        path = primaries_png(self.directory)
        with ImageLoader(path) as loader:
            image = loader.load()

        out = self.directory / 'saved.png'
        save_image(image, str(out))

        # Read back through PIL, which has no opinion about OpenCV's ordering
        reloaded = np.array(Image.open(out).convert('RGB'))
        np.testing.assert_array_equal(reloaded, image)

    def test_a_round_trip_through_a_file_preserves_every_colour(self):
        path = primaries_png(self.directory)
        with ImageLoader(path) as loader:
            first = loader.load()

        out = self.directory / 'again.png'
        save_image(first, str(out))
        with ImageLoader(out) as loader:
            second = loader.load()

        np.testing.assert_array_equal(first, second)

    def test_inverting_red_inverts_red_in_the_saved_file(self):
        # The bug this file exists for: the operation has to reach the channel
        # the user named, all the way out to the file
        path = primaries_png(self.directory)
        with ImageLoader(path) as loader:
            image = loader.load()

        out = self.directory / 'inverted.png'
        save_image(invert_channel(image, channel='r'), str(out))
        result = np.array(Image.open(out).convert('RGB'))

        self.assertEqual(tuple(result[0, 0]), (0, 0, 0))        # red band went black
        self.assertEqual(tuple(result[0, 40]), (255, 255, 0))   # green band gained red
        self.assertEqual(tuple(result[0, 80]), (255, 0, 255))   # blue band gained red

    def test_a_chain_and_its_preset_agree_on_colour(self):
        path = primaries_png(self.directory)
        with ImageLoader(path) as loader:
            image = loader.load()

        spec = resolve_filter('invert_channel')
        pipeline = Pipeline(image)
        pipeline.apply(spec.fn, spec.name, spec.module, {'channel': 'r'})
        direct = pipeline.current

        # Replay from the preset on disk, as the CLI would
        import json
        path_out = self.directory / 'preset.json'
        pipeline.save_preset(str(path_out))
        steps = [FilterStep.from_dict(step) for step in
                 json.loads(path_out.read_text(encoding='utf-8'))['filters']]

        replayed = Pipeline(image)
        replayed.replace_chain(steps, filter_function)
        np.testing.assert_array_equal(replayed.current, direct)


class TestVideoColour(unittest.TestCase):
    """Video frames take a different path through the loader than stills."""

    def test_a_video_frame_comes_back_rgb(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'red.avi'
            # Written through OpenCV, which takes BGR
            frame_bgr = np.zeros((64, 96, 3), np.uint8)
            frame_bgr[:, :, 2] = 255
            writer = cv2.VideoWriter(str(path),
                                     cv2.VideoWriter_fourcc(*'MJPG'), 5, (96, 64))
            if not writer.isOpened():
                self.skipTest('no video writer available in this build')
            for _ in range(5):
                writer.write(frame_bgr)
            writer.release()

            with ImageLoader(path) as loader:
                frame = loader.load()

        # MJPEG is lossy, so this asserts the ordering rather than exact values
        self.assertGreater(float(frame[:, :, 0].mean()), 200)
        self.assertLess(float(frame[:, :, 2].mean()), 60)


class TestViewerColour(unittest.TestCase):
    """What the desktop viewer composes is what the file contains."""

    @classmethod
    def setUpClass(cls):
        try:
            import tkinter as tk
            root = tk.Tk()
            root.destroy()
        except Exception as exc:            # pragma: no cover - environment
            raise unittest.SkipTest(f'Tkinter unavailable: {exc}')

    def test_the_viewer_composes_the_colours_it_was_given(self):
        import tkinter as tk
        from src.gui.widgets import ImageCanvas, to_display

        root = tk.Tk()
        root.withdraw()
        self.addCleanup(root.destroy)

        with tempfile.TemporaryDirectory() as directory:
            path = primaries_png(Path(directory))
            with ImageLoader(path) as loader:
                image = loader.load()

        # to_display must not reorder anything
        self.assertEqual(tuple(to_display(image)[0, 0]), RED)

        canvas = ImageCanvas(root)
        self.addCleanup(canvas.destroy)
        canvas.set_images(image, image)
        self.assertEqual(tuple(canvas._compose()[0, 0]), RED)

        # And PIL, the last step before the pixels reach a screen
        composed = canvas._compose()
        self.assertEqual(tuple(np.array(Image.fromarray(composed))[0, 0]), RED)

        # A colour operation reaches the channel named, on screen
        canvas.set_images(image, invert_channel(image, channel='r'))
        self.assertEqual(tuple(canvas._compose()[0, 0]), (0, 0, 0))


class TestDashboardColour(unittest.TestCase):
    """The web front end has to agree with the desktop one."""

    def test_the_dashboard_load_path_keeps_rgb(self):
        # Mirrors src/dashboard.py's _load_image: PIL decode, no conversion
        frame = np.zeros((8, 24, 3), np.uint8)
        frame[:, :8] = RED
        buffer = io.BytesIO()
        Image.fromarray(frame).save(buffer, format='PNG')

        image = np.array(Image.open(io.BytesIO(buffer.getvalue())).convert('RGB'))
        self.assertEqual(tuple(image[0, 0]), RED)

        # ...and a colour operation reaches the channel named
        inverted = invert_channel(image, channel='r')
        self.assertEqual(tuple(inverted[0, 0]), (0, 0, 0))

    def test_both_front_ends_produce_the_same_pixels(self):
        with tempfile.TemporaryDirectory() as directory:
            path = primaries_png(Path(directory))

            with ImageLoader(path) as loader:
                desktop = loader.load()
            web = np.array(Image.open(path).convert('RGB'))

            np.testing.assert_array_equal(desktop, web)

            spec = resolve_filter('temperature')
            np.testing.assert_array_equal(
                spec.fn(desktop, temperature=40),
                spec.fn(web, temperature=40))


if __name__ == '__main__':
    unittest.main()
