"""
Tests for src/utils/compare.py - the original-vs-processed renderings.

Kept out of test_gui.py because these belong to both front ends and the CLI,
and test_gui skips entirely when tkinter is unavailable.
"""

import unittest

import numpy as np

from src.utils.compare import difference_map, side_by_side


class TestSideBySide(unittest.TestCase):

    def test_canvas_fits_both_panels(self):
        left = np.full((40, 60, 3), 30, dtype=np.uint8)
        right = np.full((20, 50, 3), 200, dtype=np.uint8)

        canvas = side_by_side(left, right, gap=8)
        self.assertEqual(canvas.shape[0], 40)
        self.assertEqual(canvas.shape[1], 60 + 8 + 50)


class TestDifferenceMap(unittest.TestCase):
    """The view that shows what a filter did instead of measuring it."""

    def test_scaling_makes_a_small_change_visible(self):
        base = np.full((40, 60, 3), 90, dtype=np.uint8)
        changed = base.copy()
        changed[10:20, 10:30] = 92          # two levels, invisible unscaled

        shown, stats = difference_map(base, changed, label=False)

        self.assertEqual(stats['peak'], 2.0)
        self.assertGreater(int(shown[12:18, 12:28].mean()), 200)

    def test_stats_report_the_change_before_scaling(self):
        """
        The scaling is what makes the view readable and what makes it capable
        of overstating. The true numbers have to survive it.
        """
        base = np.zeros((20, 20, 3), dtype=np.uint8)
        changed = np.full((20, 20, 3), 10, dtype=np.uint8)

        _shown, stats = difference_map(base, changed, label=False)
        self.assertEqual(stats['peak'], 10.0)
        self.assertAlmostEqual(stats['mean'], 10.0)

    def test_a_fixed_amplification_is_honoured(self):
        base = np.zeros((10, 10, 3), dtype=np.uint8)
        changed = np.full((10, 10, 3), 3, dtype=np.uint8)

        shown, stats = difference_map(base, changed, amplify=10.0, label=False)
        self.assertEqual(stats['scale'], 10.0)
        self.assertEqual(int(shown.max()), 30)

    def test_identical_images_do_not_divide_by_zero(self):
        image = np.full((10, 10, 3), 200, dtype=np.uint8)
        shown, stats = difference_map(image, image.copy(), label=False)

        self.assertEqual(stats['peak'], 0.0)
        self.assertEqual(stats['scale'], 1.0)
        self.assertEqual(int(shown.max()), 0)

    def test_different_sizes_are_padded_rather_than_rejected(self):
        base = np.full((40, 60, 3), 50, dtype=np.uint8)
        cropped = base[:20, :30].copy()

        shown, _stats = difference_map(base, cropped, label=False)
        self.assertEqual(shown.shape[:2], (40, 60))
        # What the crop removed reads as changed, because it is
        self.assertGreater(int(shown[30:, 40:].mean()), 0)

    def test_the_label_states_the_scale_it_applied(self):
        base = np.zeros((300, 640, 3), dtype=np.uint8)
        changed = base.copy()
        changed[100:200, 200:400] = 5

        labelled, stats = difference_map(base, changed, label=True)
        plain, _ = difference_map(base, changed, label=False)

        self.assertEqual(stats['labelled'], 1.0)
        self.assertFalse(np.array_equal(labelled[:40], plain[:40]))

    def test_the_caption_is_dropped_when_it_would_bury_the_picture(self):
        # A thumbnail cannot carry 40 characters of caption; the numbers are
        # still in the stats for whoever needs them
        base = np.zeros((40, 60, 3), dtype=np.uint8)
        changed = base.copy()
        changed[10:20, 10:30] = 5

        shown, stats = difference_map(base, changed, label=True)
        plain, _ = difference_map(base, changed, label=False)

        self.assertEqual(stats['labelled'], 0.0)
        np.testing.assert_array_equal(shown, plain)
        self.assertEqual(stats['peak'], 5.0)

    def test_colour_shift_shows_up_coloured(self):
        """
        A channelwise operation moves the channels apart. The map is per
        channel so that reads as colour, which is the tell on an exhibit.
        """
        base = np.full((30, 30, 3), 100, dtype=np.uint8)
        shifted = base.copy()
        shifted[:, :, 0] = 130          # red only

        shown, _ = difference_map(base, shifted, label=False)
        self.assertGreater(int(shown[:, :, 0].mean()), 200)
        self.assertEqual(int(shown[:, :, 1].max()), 0)
        self.assertEqual(int(shown[:, :, 2].max()), 0)

    def test_it_finds_the_action_where_nobody_wanted_it(self):
        """
        The document's own example: on a night scene, most of a contrast
        filter's action lands in the sky - that is, nowhere the analyst cared
        about. The map has to make that obvious without being told where to
        look.
        """
        from src.filters.clahe import apply_clahe

        frame = np.full((80, 120, 3), 12, dtype=np.uint8)     # dark ground
        frame[:30, :] = 60                                    # brighter sky band
        rng = np.random.default_rng(7)
        frame = np.clip(frame + rng.integers(-4, 5, frame.shape), 0, 255).astype(np.uint8)

        _shown, _stats = difference_map(frame, apply_clahe(frame, clip_limit=4.0),
                                        label=False)
        raw = np.abs(apply_clahe(frame, clip_limit=4.0).astype(int) - frame.astype(int))
        sky, ground = raw[:30].mean(), raw[40:].mean()
        self.assertGreater(sky, ground)


if __name__ == '__main__':
    unittest.main()
