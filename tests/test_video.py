"""
Unit tests for video output.

The assertion that matters is fidelity: the default codec has to give back
exactly the pixels it was given. A tool that reads compression history
elsewhere must not add a generation of its own without saying so.
"""

import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np

from src.core import (
    DEFAULT_CODECS,
    LOSSLESS_CODECS,
    VideoWriter,
    codec_for,
    is_lossless,
    save_video,
)


def frames(count: int = 8, height: int = 64, width: int = 80):
    """Frames with hard edges and noise, which lossy codecs damage visibly."""
    rng = np.random.default_rng(5)
    made = []
    for index in range(count):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:, :width // 2] = (60, 90, 140)
        frame[:, width // 2:] = (180, 150, 90)
        cv2.rectangle(frame, (4 + index * 3, 20), (14 + index * 3, 44),
                      (255, 255, 255), -1)
        made.append(np.clip(frame.astype(np.float32)
                            + rng.normal(0, 6, frame.shape), 0, 255).astype(np.uint8))
    return made


def read_back(path: Path):
    """Every frame of a written file, as RGB."""
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


class CodecChoiceTests(unittest.TestCase):

    def test_containers_have_a_default(self):
        self.assertEqual(codec_for('out.avi'), 'FFV1')
        self.assertEqual(codec_for(Path('out.mkv')), 'FFV1')
        self.assertEqual(codec_for('out.mp4'), 'mp4v')

    def test_an_unknown_container_is_refused(self):
        with self.assertRaises(ValueError):
            codec_for('out.gif')
        with self.assertRaises(ValueError):
            codec_for('out')

    def test_lossless_codecs_are_named_as_such(self):
        self.assertTrue(is_lossless('FFV1'))
        self.assertTrue(is_lossless('ffv1'))
        self.assertFalse(is_lossless('MJPG'))
        self.assertFalse(is_lossless('mp4v'))

    def test_the_avi_default_is_lossless(self):
        """The container an exhibit should be written to."""
        self.assertIn(DEFAULT_CODECS['.avi'], LOSSLESS_CODECS)


class VideoWriterTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.frames = frames()

    def tearDown(self):
        self.tmp.cleanup()

    def test_the_default_codec_preserves_every_pixel(self):
        """
        The claim the default rests on.

        Written and read back, an FFV1 file has to be the input exactly.
        Anything less means the tool added compression to the evidence.
        """
        path = self.dir / 'clip.avi'
        written = save_video(self.frames, path, fps=10)
        self.assertEqual(written, len(self.frames))

        recovered = read_back(path)
        self.assertEqual(len(recovered), len(self.frames))
        for index, (original, back) in enumerate(zip(self.frames, recovered)):
            with self.subTest(frame=index):
                np.testing.assert_array_equal(back, original)

    def test_a_lossy_codec_really_is_lossy(self):
        """The distinction is measured, not assumed from the name."""
        path = self.dir / 'lossy.avi'
        save_video(self.frames, path, fps=10, codec='MJPG')
        recovered = read_back(path)
        self.assertTrue(recovered)
        self.assertFalse(np.array_equal(recovered[0], self.frames[0]))

    def test_frames_written_counts_up(self):
        path = self.dir / 'count.avi'
        with VideoWriter(path, fps=10) as writer:
            self.assertEqual(writer.frames_written, 0)
            for frame in self.frames:
                writer.write(frame)
            self.assertEqual(writer.frames_written, len(self.frames))

    def test_a_grayscale_frame_is_accepted(self):
        path = self.dir / 'gray.avi'
        gray = [cv2.cvtColor(f, cv2.COLOR_RGB2GRAY) for f in self.frames]
        self.assertEqual(save_video(gray, path, fps=10), len(gray))
        self.assertEqual(read_back(path)[0].shape[2], 3)

    def test_an_alpha_channel_is_dropped_rather_than_refused(self):
        path = self.dir / 'alpha.avi'
        rgba = [cv2.cvtColor(f, cv2.COLOR_RGB2RGBA) for f in self.frames]
        self.assertEqual(save_video(rgba, path, fps=10), len(rgba))

    def test_a_frame_of_a_different_size_is_refused(self):
        """
        Silently rescaling would hide that the chain is not one chain.

        A step that resizes some frames and not others has produced a sequence
        that does not mean a single thing, and stretching them to match would
        conceal exactly that.
        """
        path = self.dir / 'mixed.avi'
        with VideoWriter(path, fps=10) as writer:
            writer.write(self.frames[0])
            with self.assertRaises(ValueError) as caught:
                writer.write(cv2.resize(self.frames[1], (40, 32)))
        self.assertIn('40x32', str(caught.exception))

    def test_an_empty_frame_is_refused(self):
        with VideoWriter(self.dir / 'e.avi', fps=10) as writer:
            with self.assertRaises(ValueError):
                writer.write(np.zeros((0, 0, 3), dtype=np.uint8))

    def test_a_non_positive_rate_is_refused(self):
        for fps in (0, -5):
            with self.subTest(fps=fps):
                with self.assertRaises(ValueError):
                    VideoWriter(self.dir / 'x.avi', fps=fps)

    def test_an_unknown_codec_says_so(self):
        with VideoWriter(self.dir / 'bad.avi', fps=10, codec='ZZZZ') as writer:
            with self.assertRaises(RuntimeError) as caught:
                writer.write(self.frames[0])
        self.assertIn('ZZZZ', str(caught.exception))

    def test_writing_nothing_is_refused(self):
        with self.assertRaises(ValueError):
            save_video([], self.dir / 'none.avi')

    def test_closing_twice_is_safe(self):
        writer = VideoWriter(self.dir / 'twice.avi', fps=10)
        writer.write(self.frames[0])
        writer.close()
        writer.close()

    def test_the_parent_directory_is_created(self):
        path = self.dir / 'nested' / 'deeper' / 'clip.avi'
        save_video(self.frames, path, fps=10)
        self.assertTrue(path.exists())


if __name__ == '__main__':
    unittest.main()
