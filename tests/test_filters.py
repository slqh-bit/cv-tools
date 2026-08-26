"""Unit tests for the Sprint 1 filters."""

import unittest

import numpy as np

from src.filters import (
    ROI,
    adjust_contrast_brightness,
    adjust_levels,
    analyze_roi,
    apply_clahe,
    apply_clahe_grid,
    apply_to_roi,
    auto_contrast,
    auto_levels,
    crop,
    draw_roi,
    extract_roi,
    flip,
    get_centered_roi,
    histogram_equalization,
    resize,
    roi_from_ratio,
    rotate,
)


def low_contrast_image(height: int = 64, width: int = 96) -> np.ndarray:
    """RGB image whose values sit in a narrow band around mid-gray."""
    rng = np.random.default_rng(0)
    base = rng.integers(110, 140, size=(height, width, 3), dtype=np.uint8)
    return base


def gradient_gray(height: int = 64, width: int = 64) -> np.ndarray:
    """Grayscale horizontal gradient."""
    row = np.linspace(0, 255, width, dtype=np.float32)
    return np.tile(row, (height, 1)).astype(np.uint8)


class TestClahe(unittest.TestCase):

    def test_preserves_shape_and_dtype(self):
        image = low_contrast_image()
        result = apply_clahe(image, clip_limit=2.0, tile_grid_size=8)
        self.assertEqual(result.shape, image.shape)
        self.assertEqual(result.dtype, np.uint8)

    def test_increases_contrast(self):
        image = low_contrast_image()
        result = apply_clahe(image, clip_limit=4.0, tile_grid_size=8)
        self.assertGreater(result.std(), image.std())

    def test_grayscale_input_returns_2d(self):
        image = gradient_gray()
        result = apply_clahe(image)
        self.assertEqual(result.ndim, 2)
        self.assertEqual(result.shape, image.shape)

    def test_alpha_channel_is_preserved(self):
        rgb = low_contrast_image()
        alpha = np.full((*rgb.shape[:2], 1), 128, dtype=np.uint8)
        rgba = np.concatenate([rgb, alpha], axis=2)
        result = apply_clahe(rgba)
        self.assertEqual(result.shape[2], 4)
        np.testing.assert_array_equal(result[:, :, 3], alpha[:, :, 0])

    def test_tuple_tile_grid_size(self):
        image = low_contrast_image()
        result = apply_clahe(image, tile_grid_size=(4, 8))
        self.assertEqual(result.shape, image.shape)

    def test_all_color_modes_run(self):
        image = low_contrast_image()
        for mode in ('lab', 'hsv', 'yuv', 'channelwise', 'luminance'):
            with self.subTest(mode=mode):
                result = apply_clahe(image, color_mode=mode)
                self.assertEqual(result.shape, image.shape)

    def test_unknown_color_mode_raises(self):
        with self.assertRaises(ValueError):
            apply_clahe(low_contrast_image(), color_mode='cmyk')

    def test_empty_image_raises(self):
        with self.assertRaises(ValueError):
            apply_clahe(np.array([], dtype=np.uint8))

    def test_luminance_is_close_to_yuv_but_not_identical(self):
        """
        The two modes are the same BT.601 combination rounded differently.

        Both halves matter. They are close, so 'luminance' is not some other
        operation; they are not identical, so collapsing the branches would
        silently change what an existing preset replays. On the validation
        corpus the luma channels differ by 1 on 0.001% of pixels, which CLAHE
        amplifies to a handful of levels in the output - more on a synthetic
        low-contrast fixture like this one than on a real frame.
        """
        image = low_contrast_image()
        difference = np.abs(
            apply_clahe(image, color_mode='luminance').astype(int)
            - apply_clahe(image, color_mode='yuv').astype(int))
        self.assertGreater(difference.max(), 0)
        self.assertLess(difference.max(), 16)


class TestCLAHEGrid(unittest.TestCase):
    """The contact sheet an operator picks a clip_limit from."""

    def test_grid_covers_every_combination(self):
        image = low_contrast_image()
        result = apply_clahe_grid(image, clip_limits=[1.5, 3.0], tile_grid_sizes=[4, 8])
        self.assertEqual(result.ndim, 3)
        self.assertEqual(result.shape[2], 3)

    def test_defaults_need_no_arguments(self):
        # The registry offers this filter, so its form must produce a board
        # without the operator typing a list first
        result = apply_clahe_grid(low_contrast_image())
        self.assertEqual(result.ndim, 3)

    def test_single_values_are_accepted(self):
        # A parameter form with one value typed in it yields a scalar
        result = apply_clahe_grid(low_contrast_image(), clip_limits=2.0,
                                  tile_grid_sizes=8)
        self.assertEqual(result.ndim, 3)

    def test_empty_settings_raise(self):
        with self.assertRaises(ValueError):
            apply_clahe_grid(low_contrast_image(), clip_limits=[], tile_grid_sizes=[8])

    def test_registered_so_a_front_end_can_reach_it(self):
        from src.filters import FILTER_REGISTRY
        self.assertIn('clahe_grid', FILTER_REGISTRY)


class TestContrastBrightness(unittest.TestCase):

    def test_brightness_increases_mean(self):
        image = low_contrast_image()
        result = adjust_contrast_brightness(image, brightness=40)
        self.assertGreater(result.mean(), image.mean())

    def test_contrast_factor_increases_spread(self):
        image = low_contrast_image()
        result = adjust_contrast_brightness(image, contrast=2.0)
        self.assertGreater(result.std(), image.std())

    def test_identity_parameters_leave_image_unchanged(self):
        image = low_contrast_image()
        result = adjust_contrast_brightness(image, brightness=0, contrast=1.0, gamma=1.0)
        np.testing.assert_array_equal(result, image)

    def test_output_is_clipped_to_uint8_range(self):
        image = np.full((8, 8, 3), 250, dtype=np.uint8)
        result = adjust_contrast_brightness(image, brightness=200)
        self.assertEqual(result.max(), 255)
        self.assertEqual(result.dtype, np.uint8)

    def test_single_channel_adjustment(self):
        image = low_contrast_image()
        result = adjust_contrast_brightness(image, brightness=50, channel='r')
        self.assertGreater(result[:, :, 0].mean(), image[:, :, 0].mean())
        np.testing.assert_array_equal(result[:, :, 1], image[:, :, 1])
        np.testing.assert_array_equal(result[:, :, 2], image[:, :, 2])

    def test_invalid_channel_raises(self):
        with self.assertRaises(ValueError):
            adjust_contrast_brightness(low_contrast_image(), channel='alpha')

    def test_auto_contrast_widens_range(self):
        image = low_contrast_image()
        result = auto_contrast(image)
        self.assertGreater(result.std(), image.std())


class TestLevels(unittest.TestCase):

    def test_maps_input_range_to_full_range(self):
        image = np.full((8, 8), 100, dtype=np.uint8)
        image[0, 0] = 50
        image[0, 1] = 200
        result = adjust_levels(image, black_point=50, white_point=200)
        self.assertEqual(result[0, 0], 0)
        self.assertEqual(result[0, 1], 255)

    def test_black_point_above_white_point_raises(self):
        with self.assertRaises(ValueError):
            adjust_levels(gradient_gray(), black_point=200, white_point=100)

    def test_gamma_below_one_darkens_midtones(self):
        image = np.full((8, 8), 128, dtype=np.uint8)
        darker = adjust_levels(image, gamma=0.5)
        brighter = adjust_levels(image, gamma=2.0)
        self.assertLess(darker.mean(), image.mean())
        self.assertGreater(brighter.mean(), image.mean())

    def test_output_range_is_respected(self):
        image = gradient_gray()
        result = adjust_levels(image, output_black=50, output_white=200)
        self.assertGreaterEqual(result.min(), 50)
        self.assertLessEqual(result.max(), 200)

    def test_auto_levels_uses_full_range(self):
        image = np.linspace(100, 150, 64, dtype=np.uint8).reshape(8, 8)
        result = auto_levels(image)
        self.assertLess(result.min(), 10)
        self.assertGreater(result.max(), 245)


class TestHistogramEqualization(unittest.TestCase):

    def test_grayscale_flattens_histogram(self):
        image = low_contrast_image()[:, :, 0]
        result = histogram_equalization(image)
        self.assertGreater(result.std(), image.std())
        self.assertEqual(result.ndim, 2)

    def test_color_preserves_shape(self):
        image = low_contrast_image()
        result = histogram_equalization(image)
        self.assertEqual(result.shape, image.shape)

    def test_all_color_modes_run(self):
        image = low_contrast_image()
        for mode in ('lab', 'hsv', 'yuv', 'channelwise', 'grayscale'):
            with self.subTest(mode=mode):
                self.assertEqual(histogram_equalization(image, color_mode=mode).shape, image.shape)

    def test_unknown_color_mode_raises(self):
        with self.assertRaises(ValueError):
            histogram_equalization(low_contrast_image(), color_mode='bogus')


class TestCropResize(unittest.TestCase):

    def test_crop_returns_requested_region(self):
        image = gradient_gray(64, 64)
        result = crop(image, 10, 20, 30, 40)
        self.assertEqual(result.shape, (40, 30))
        np.testing.assert_array_equal(result, image[20:60, 10:40])

    def test_crop_clips_to_bounds(self):
        image = gradient_gray(64, 64)
        result = crop(image, 50, 50, 100, 100)
        self.assertEqual(result.shape, (14, 14))

    def test_crop_fully_outside_raises(self):
        with self.assertRaises(ValueError):
            crop(gradient_gray(64, 64), 100, 100, 10, 10)

    def test_crop_returns_a_copy(self):
        image = gradient_gray(64, 64)
        result = crop(image, 0, 0, 10, 10)
        result[0, 0] = 42
        self.assertNotEqual(image[0, 0], 42)

    def test_resize_to_exact_size(self):
        result = resize(gradient_gray(64, 64), width=32, height=16)
        self.assertEqual(result.shape, (16, 32))

    def test_resize_width_only_preserves_aspect(self):
        result = resize(gradient_gray(40, 80), width=40)
        self.assertEqual(result.shape, (20, 40))

    def test_resize_by_scale(self):
        result = resize(gradient_gray(64, 64), scale=0.5)
        self.assertEqual(result.shape, (32, 32))

    def test_resize_without_target_raises(self):
        with self.assertRaises(ValueError):
            resize(gradient_gray())

    def test_resize_to_zero_raises(self):
        with self.assertRaises(ValueError):
            resize(gradient_gray(64, 64), scale=0.0)

    def test_rotate_90_swaps_dimensions(self):
        image = gradient_gray(40, 80)
        result = rotate(image, 90)
        self.assertEqual(result.shape[:2], (80, 40))

    def test_flip_horizontal_is_reversible(self):
        image = gradient_gray()
        np.testing.assert_array_equal(flip(flip(image, 'horizontal'), 'horizontal'), image)

    def test_flip_invalid_direction_raises(self):
        with self.assertRaises(ValueError):
            flip(gradient_gray(), 'diagonal')


class TestROI(unittest.TestCase):

    def test_geometry_properties(self):
        roi = ROI(10, 20, 30, 40)
        self.assertEqual(roi.bbox, (10, 20, 40, 60))
        self.assertEqual(roi.xywh, (10, 20, 30, 40))
        self.assertEqual(roi.center, (25, 40))
        self.assertEqual(roi.area, 1200)

    def test_from_xyxy_roundtrip(self):
        roi = ROI.from_xyxy(10, 20, 40, 60)
        self.assertEqual(roi.xywh, (10, 20, 30, 40))

    def test_dict_roundtrip(self):
        roi = ROI(1, 2, 3, 4)
        self.assertEqual(ROI.from_dict(roi.to_dict()), roi)

    def test_is_valid_bounds_check(self):
        shape = (100, 100, 3)
        self.assertTrue(ROI(0, 0, 100, 100).is_valid(shape))
        self.assertFalse(ROI(50, 50, 100, 100).is_valid(shape))
        self.assertFalse(ROI(0, 0, 0, 10).is_valid(shape))

    def test_clip_constrains_to_image(self):
        clipped = ROI(90, 90, 50, 50).clip((100, 100))
        self.assertEqual(clipped.xywh, (90, 90, 10, 10))

    def test_extract_returns_region(self):
        image = gradient_gray(64, 64)
        region = extract_roi(image, ROI(10, 10, 20, 20))
        self.assertEqual(region.shape, (20, 20))
        np.testing.assert_array_equal(region, image[10:30, 10:30])

    def test_apply_to_roi_leaves_outside_untouched(self):
        image = low_contrast_image()
        roi = ROI(10, 10, 20, 20)
        result = apply_to_roi(image, roi, adjust_contrast_brightness, brightness=60)
        self.assertGreater(result[10:30, 10:30].mean(), image[10:30, 10:30].mean())
        np.testing.assert_array_equal(result[0:10, :], image[0:10, :])

    def test_draw_roi_does_not_change_size(self):
        image = low_contrast_image()
        result = draw_roi(image, ROI(5, 5, 20, 20), label='target')
        self.assertEqual(result.shape, image.shape)
        self.assertFalse(np.array_equal(result, image))

    def test_analyze_reports_per_channel_stats(self):
        image = np.zeros((20, 20, 3), dtype=np.uint8)
        image[:, :, 0] = 100
        image[:, :, 1] = 150
        image[:, :, 2] = 200
        stats = analyze_roi(image, ROI(0, 0, 20, 20))
        self.assertEqual(stats['pixels'], 1200)
        self.assertAlmostEqual(stats['channels']['R']['mean'], 100.0)
        self.assertAlmostEqual(stats['channels']['G']['mean'], 150.0)
        self.assertAlmostEqual(stats['channels']['B']['mean'], 200.0)
        self.assertEqual(stats['channels']['R']['std'], 0.0)

    def test_centered_roi_is_centered(self):
        roi = get_centered_roi((100, 100), 40, 40)
        self.assertEqual(roi.xywh, (30, 30, 40, 40))

    def test_roi_from_ratio(self):
        roi = roi_from_ratio((100, 200), 0.5, 0.5, 0.25, 0.25)
        self.assertEqual(roi.xywh, (100, 50, 50, 25))


if __name__ == '__main__':
    unittest.main()
