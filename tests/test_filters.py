"""Unit tests for the Sprint 1 filters."""

import unittest

import numpy as np

from src.filters import (
    ROI,
    adjust_contrast_brightness,
    adjust_levels,
    analyze_roi,
    CLAHE_SIXTEEN_BIT_MODES,
    apply_clahe,
    apply_clahe_grid,
    feather_mask,
    roi_filter,
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

    def test_sixteen_bit_survives_instead_of_wrapping(self):
        """
        A 10- or 12-bit source arrives as uint16. Casting it to uint8 does not
        coarsen it, it wraps it modulo 256 - so 4096 becomes 0 and a bright
        pixel goes black immediately before the step meant to stretch
        contrast. Rank correlation catches that where a shape check would not.
        """
        ramp = np.tile(np.linspace(0, 4095, 256, dtype=np.uint16), (64, 1))
        result = apply_clahe(ramp)

        self.assertEqual(result.dtype, np.uint16)
        # Ordering must survive: CLAHE redistributes levels, it does not
        # reorder them wholesale
        order = np.corrcoef(ramp.ravel().argsort().argsort(),
                            result.ravel().argsort().argsort())[0, 1]
        self.assertGreater(order, 0.9)

    def test_sixteen_bit_colour_modes_keep_their_depth(self):
        rng = np.random.default_rng(4)
        image = (rng.random((32, 48, 3)) * 4095).astype(np.uint16)
        for mode in CLAHE_SIXTEEN_BIT_MODES:
            with self.subTest(mode=mode):
                result = apply_clahe(image, color_mode=mode)
                self.assertEqual(result.dtype, np.uint16)
                self.assertEqual(result.shape, image.shape)

    def test_sixteen_bit_is_refused_by_modes_that_cannot_hold_it(self):
        """
        OpenCV's LAB and HSV conversions reject CV_16U. Saying so beats
        quietly dropping to 8 bits, which is what the cast used to do.
        """
        rng = np.random.default_rng(5)
        image = (rng.random((32, 48, 3)) * 4095).astype(np.uint16)
        for mode in ('lab', 'hsv'):
            with self.subTest(mode=mode):
                with self.assertRaises(ValueError) as ctx:
                    apply_clahe(image, color_mode=mode)
                self.assertIn('16 bits', str(ctx.exception))

    def test_eight_bit_is_untouched_by_the_depth_handling(self):
        image = low_contrast_image()
        self.assertEqual(apply_clahe(image).dtype, np.uint8)


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

    def test_feather_softens_the_border(self):
        """
        A visible seam around an enhanced region is a question at the hearing.
        The ramp has to make the step across the border materially smaller
        than the hard-edged version.
        """
        image = low_contrast_image(80, 120)
        roi = ROI(30, 20, 50, 40)

        def step(result):
            inside = result[roi.y:roi.y2, roi.x].astype(float)
            outside = result[roi.y:roi.y2, roi.x - 1].astype(float)
            return float(np.abs(inside - outside).mean())

        hard = apply_to_roi(image, roi, adjust_contrast_brightness,
                            brightness=60, feather=0)
        soft = apply_to_roi(image, roi, adjust_contrast_brightness,
                            brightness=60, feather=10)

        self.assertLess(step(soft), step(hard) / 2)
        # and the region is still actually enhanced in the middle
        self.assertGreater(soft[40:50, 50:60].mean(), image[40:50, 50:60].mean())

    def test_feather_leaves_the_outside_alone(self):
        image = low_contrast_image(80, 120)
        roi = ROI(30, 20, 50, 40)
        result = apply_to_roi(image, roi, adjust_contrast_brightness,
                              brightness=60, feather=10)
        np.testing.assert_array_equal(result[:roi.y, :], image[:roi.y, :])
        np.testing.assert_array_equal(result[:, :roi.x], image[:, :roi.x])

    def test_feather_mask_ramps_from_edge_to_middle(self):
        mask = feather_mask(40, 60, 8)
        self.assertEqual(mask.shape, (40, 60))
        self.assertAlmostEqual(float(mask[20, 30]), 1.0)
        self.assertLess(float(mask[0, 30]), float(mask[4, 30]))
        self.assertLess(float(mask[4, 30]), 1.0)

    def test_feather_is_clamped_to_a_small_region(self):
        # Two ramps must not meet and leave the middle unfiltered
        mask = feather_mask(6, 6, 50)
        self.assertGreater(float(mask.max()), 0.0)
        self.assertEqual(mask.shape, (6, 6))

    def test_a_filter_that_resizes_the_region_is_refused(self):
        from src.filters import resize
        image = low_contrast_image(80, 120)
        with self.assertRaises(ValueError) as ctx:
            apply_to_roi(image, ROI(30, 20, 50, 40), resize, scale=0.5)
        self.assertIn('same region', str(ctx.exception))

    def test_roi_filter_is_registered_and_runs(self):
        from src.filters import FILTER_REGISTRY
        self.assertIn('roi_filter', FILTER_REGISTRY)

        image = low_contrast_image(80, 120)
        result = roi_filter(image, x=30, y=20, width=50, height=40,
                            filter_name='clahe')
        self.assertEqual(result.shape, image.shape)
        np.testing.assert_array_equal(result[:20, :], image[:20, :])

    def test_roi_filter_refuses_itself_and_filters_needing_arguments(self):
        image = low_contrast_image(80, 120)
        for inner in ('roi_filter', 'crop'):
            with self.subTest(inner=inner):
                with self.assertRaises(ValueError):
                    roi_filter(image, x=30, y=20, width=50, height=40,
                               filter_name=inner)

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
