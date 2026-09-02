"""Unit tests for the colour adjustment filters: curves, white balance,
saturation, colour balance, invert."""

import unittest

import cv2
import numpy as np

from cv_tools.filters import (
    CURVE_PRESETS,
    adjust_cmyk,
    adjust_color_balance,
    adjust_saturation,
    adjust_temperature,
    adjust_vibrance,
    apply_curve,
    auto_white_balance,
    build_lut,
    channel_mixer,
    compute_gains,
    curve_from_string,
    desaturate,
    invert,
    invert_channel,
    invert_luminance,
    s_curve,
    selective_saturation,
    solarize,
    white_balance_from_patch,
)


def gradient_rgb(height: int = 48, width: int = 64) -> np.ndarray:
    """Neutral gray ramp, so any colour cast is introduced deliberately."""
    ramp = np.linspace(10, 245, width, dtype=np.float32)
    gray = np.tile(ramp, (height, 1))
    return np.repeat(gray[:, :, np.newaxis], 3, axis=2).astype(np.uint8)


def cast_image(gains=(1.35, 1.0, 0.7)) -> np.ndarray:
    """Neutral ramp pushed towards orange, as sodium lighting would."""
    base = gradient_rgb().astype(np.float32)
    for index, gain in enumerate(gains):
        base[:, :, index] *= gain
    return np.clip(base, 0, 255).astype(np.uint8)


def colorful(height: int = 48, width: int = 64) -> np.ndarray:
    """Patches of varied hue and saturation."""
    image = np.zeros((height, width, 3), dtype=np.uint8)
    image[:, : width // 3] = (200, 60, 60)
    image[:, width // 3: 2 * width // 3] = (140, 130, 120)   # nearly neutral
    image[:, 2 * width // 3:] = (60, 90, 200)
    return image


class TestCurves(unittest.TestCase):

    def test_lut_is_256_entries(self):
        lut = build_lut([(0, 0), (255, 255)])
        self.assertEqual(lut.shape, (256,))
        self.assertEqual(lut.dtype, np.uint8)

    def test_identity_curve_changes_nothing(self):
        image = gradient_rgb()
        np.testing.assert_array_equal(apply_curve(image, preset='linear'), image)

    def test_lut_passes_through_control_points(self):
        lut = build_lut([(0, 0), (128, 180), (255, 255)])
        self.assertEqual(lut[0], 0)
        self.assertEqual(lut[255], 255)
        self.assertAlmostEqual(int(lut[128]), 180, delta=2)

    def test_lut_is_monotonic(self):
        # A shape-preserving spline must never reverse the tonal order
        lut = build_lut([(0, 0), (60, 20), (128, 200), (200, 210), (255, 255)])
        self.assertTrue(np.all(np.diff(lut.astype(int)) >= 0))

    def test_brighten_preset_raises_mean(self):
        image = gradient_rgb()
        self.assertGreater(apply_curve(image, preset='brighten').mean(), image.mean())

    def test_darken_preset_lowers_mean(self):
        image = gradient_rgb()
        self.assertLess(apply_curve(image, preset='darken').mean(), image.mean())

    def test_lift_shadows_targets_the_dark_end(self):
        image = gradient_rgb()
        result = apply_curve(image, preset='lift_shadows')
        dark_before = image[:, :10].mean()
        dark_after = result[:, :10].mean()
        bright_before = image[:, -10:].mean()
        bright_after = result[:, -10:].mean()
        # Shadows move much more than highlights
        self.assertGreater(dark_after - dark_before, bright_after - bright_before)

    def test_single_channel_curve(self):
        image = gradient_rgb()
        result = apply_curve(image, preset='brighten', channel='r')
        self.assertGreater(result[:, :, 0].mean(), image[:, :, 0].mean())
        np.testing.assert_array_equal(result[:, :, 1], image[:, :, 1])

    def test_unknown_preset_lists_options(self):
        with self.assertRaises(ValueError) as ctx:
            apply_curve(gradient_rgb(), preset='nope')
        self.assertIn('lift_shadows', str(ctx.exception))

    def test_requires_points_or_preset(self):
        with self.assertRaises(ValueError):
            apply_curve(gradient_rgb())

    def test_too_few_points_raises(self):
        with self.assertRaises(ValueError):
            build_lut([(0, 0)])

    def test_duplicate_inputs_raise(self):
        with self.assertRaises(ValueError):
            build_lut([(0, 0), (128, 100), (128, 200), (255, 255)])

    def test_out_of_range_points_raise(self):
        with self.assertRaises(ValueError):
            build_lut([(0, 0), (300, 255)])

    def test_points_are_sorted_for_you(self):
        forward = build_lut([(0, 0), (128, 180), (255, 255)])
        shuffled = build_lut([(255, 255), (0, 0), (128, 180)])
        np.testing.assert_array_equal(forward, shuffled)

    def test_s_curve_increases_contrast(self):
        image = gradient_rgb()
        self.assertGreater(s_curve(image, 0.5).std(), image.std())

    def test_s_curve_rejects_out_of_range_strength(self):
        with self.assertRaises(ValueError):
            s_curve(gradient_rgb(), 1.5)

    def test_curve_from_string(self):
        self.assertEqual(curve_from_string('0:0,128:160,255:255'),
                         [(0.0, 0.0), (128.0, 160.0), (255.0, 255.0)])

    def test_curve_from_string_rejects_garbage(self):
        for text in ('0-0,255-255', '0:0', 'a:b,c:d'):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    curve_from_string(text)

    def test_alpha_preserved(self):
        rgb = gradient_rgb()
        alpha = np.full((*rgb.shape[:2], 1), 128, dtype=np.uint8)
        result = apply_curve(np.concatenate([rgb, alpha], axis=2), preset='brighten')
        np.testing.assert_array_equal(result[:, :, 3], alpha[:, :, 0])


class TestWhiteBalance(unittest.TestCase):

    def test_removes_a_known_cast(self):
        neutral = gradient_rgb()
        cast = cast_image()

        corrected = auto_white_balance(cast, method='gray_world')

        # Channel means should be closer together after correction
        spread = lambda img: float(np.ptp([img[:, :, c].mean() for c in range(3)]))
        self.assertLess(spread(corrected), spread(cast))
        self.assertLess(spread(corrected), 12.0)

    def test_all_methods_reduce_the_cast(self):
        cast = cast_image()
        spread = lambda img: float(np.ptp([img[:, :, c].mean() for c in range(3)]))
        for method in ('gray_world', 'white_patch', 'shades_of_gray'):
            with self.subTest(method=method):
                corrected = auto_white_balance(cast, method=method)
                self.assertLess(spread(corrected), spread(cast))

    def test_neutral_image_is_left_alone(self):
        neutral = gradient_rgb()
        corrected = auto_white_balance(neutral, method='gray_world')
        self.assertLess(float(np.abs(corrected.astype(int) - neutral.astype(int)).mean()), 2.0)

    def test_gains_anchor_on_green(self):
        gains = compute_gains(cast_image(), method='gray_world')
        self.assertAlmostEqual(float(gains[1]), 1.0, places=6)
        # The orange cast means red is scaled down and blue up
        self.assertLess(gains[0], 1.0)
        self.assertGreater(gains[2], 1.0)

    def test_unknown_method_raises(self):
        with self.assertRaises(ValueError):
            auto_white_balance(cast_image(), method='magic')

    def test_grayscale_input_raises(self):
        with self.assertRaises(ValueError):
            auto_white_balance(np.zeros((16, 16), dtype=np.uint8))

    def test_patch_balance_neutralises_the_patch(self):
        cast = cast_image()
        corrected = white_balance_from_patch(cast, 20, 10, 20, 20)
        patch = corrected[10:30, 20:40]
        means = [patch[:, :, c].mean() for c in range(3)]
        self.assertLess(float(np.ptp(means)), 6.0)

    def test_patch_outside_image_raises(self):
        with self.assertRaises(ValueError):
            white_balance_from_patch(cast_image(), 500, 500, 10, 10)

    def test_temperature_warms_and_cools(self):
        image = gradient_rgb()
        warm = adjust_temperature(image, temperature=50)
        cool = adjust_temperature(image, temperature=-50)
        self.assertGreater(warm[:, :, 0].mean(), image[:, :, 0].mean())
        self.assertGreater(cool[:, :, 2].mean(), image[:, :, 2].mean())

    def test_temperature_out_of_range_raises(self):
        with self.assertRaises(ValueError):
            adjust_temperature(gradient_rgb(), temperature=200)


class TestSaturation(unittest.TestCase):

    def test_zero_factor_removes_colour(self):
        result = adjust_saturation(colorful(), 0.0)
        # Every pixel becomes gray, so the channels agree
        self.assertLess(float(np.abs(result[:, :, 0].astype(int)
                                     - result[:, :, 2].astype(int)).mean()), 2.0)

    def test_factor_above_one_increases_saturation(self):
        image = colorful()
        boosted = adjust_saturation(image, 1.6)
        saturation = lambda img: cv2.cvtColor(img, cv2.COLOR_RGB2HSV)[:, :, 1].mean()
        self.assertGreater(saturation(boosted), saturation(image))

    def test_identity_factor_is_near_lossless(self):
        image = colorful()
        result = adjust_saturation(image, 1.0)
        self.assertLess(float(np.abs(result.astype(int) - image.astype(int)).mean()), 2.0)

    def test_negative_factor_raises(self):
        with self.assertRaises(ValueError):
            adjust_saturation(colorful(), -1.0)

    def test_grayscale_passes_through(self):
        gray = np.full((16, 16), 128, dtype=np.uint8)
        np.testing.assert_array_equal(adjust_saturation(gray, 2.0), gray)

    def test_vibrance_boosts_muted_colours_proportionally_more(self):
        image = colorful()
        result = adjust_vibrance(image, 2.0)

        saturation = lambda img, s: cv2.cvtColor(
            img, cv2.COLOR_RGB2HSV)[:, s, 1].astype(float).mean()

        width = image.shape[1]
        muted = slice(width // 3, 2 * width // 3)
        vivid = slice(0, width // 3)

        muted_ratio = saturation(result, muted) / saturation(image, muted)
        vivid_ratio = saturation(result, vivid) / saturation(image, vivid)

        # The falloff is proportional, not absolute: a mid-saturation colour
        # can still gain more raw saturation than a nearly-neutral one
        self.assertGreater(muted_ratio, vivid_ratio)

    def test_vibrance_protects_saturated_colours(self):
        # The point of vibrance over plain saturation: a colour already near
        # full saturation is left almost alone instead of clipping
        vivid = np.zeros((16, 16, 3), dtype=np.uint8)
        vivid[:, :] = (250, 5, 5)

        by_saturation = adjust_saturation(vivid, 2.0)
        by_vibrance = adjust_vibrance(vivid, 2.0)

        shift = lambda img: float(np.abs(img.astype(int) - vivid.astype(int)).mean())
        self.assertLess(shift(by_vibrance), shift(by_saturation) + 1e-9)
        self.assertLess(shift(by_vibrance), 5.0)

    def test_vibrance_leaves_gray_gray(self):
        gray = np.full((16, 16, 3), 128, dtype=np.uint8)
        np.testing.assert_array_equal(adjust_vibrance(gray, 2.0), gray)

    def test_desaturate_methods_differ(self):
        image = colorful()
        results = {m: desaturate(image, m)
                   for m in ('luminance', 'average', 'lightness', 'max', 'min')}
        for result in results.values():
            self.assertEqual(result.ndim, 2)
        self.assertFalse(np.array_equal(results['luminance'], results['max']))

    def test_desaturate_unknown_method_raises(self):
        with self.assertRaises(ValueError):
            desaturate(colorful(), 'bogus')

    def test_selective_saturation_targets_one_hue(self):
        image = colorful()
        # Red sits at hue 0
        result = selective_saturation(image, hue_center=0, hue_range=30, factor=2.0)

        width = image.shape[1]
        hsv_before = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)[:, :, 1].astype(float)
        hsv_after = cv2.cvtColor(result, cv2.COLOR_RGB2HSV)[:, :, 1].astype(float)

        red_gain = hsv_after[:, :width // 3].mean() - hsv_before[:, :width // 3].mean()
        blue_gain = hsv_after[:, 2 * width // 3:].mean() - hsv_before[:, 2 * width // 3:].mean()

        self.assertGreater(red_gain, 5.0)
        self.assertLess(abs(blue_gain), red_gain)

    def test_selective_saturation_rejects_bad_range(self):
        with self.assertRaises(ValueError):
            selective_saturation(colorful(), hue_center=0, hue_range=0)


class TestColorBalance(unittest.TestCase):

    def test_shadow_shift_affects_dark_tones_most(self):
        image = gradient_rgb()
        result = adjust_color_balance(image, shadows=(60, 0, -60),
                                      preserve_luminosity=False)

        dark_shift = result[:, :8, 0].mean() - image[:, :8, 0].mean()
        bright_shift = result[:, -8:, 0].mean() - image[:, -8:, 0].mean()
        self.assertGreater(dark_shift, bright_shift)

    def test_highlight_shift_affects_bright_tones_most(self):
        image = gradient_rgb()
        result = adjust_color_balance(image, highlights=(60, 0, -60),
                                      preserve_luminosity=False)

        dark_shift = result[:, :8, 0].mean() - image[:, :8, 0].mean()
        bright_shift = result[:, -8:, 0].mean() - image[:, -8:, 0].mean()
        self.assertGreater(bright_shift, dark_shift)

    def test_preserve_luminosity_holds_brightness(self):
        image = gradient_rgb()
        luma = lambda img: float((img.astype(np.float32) @ [0.299, 0.587, 0.114]).mean())

        shifted = adjust_color_balance(image, midtones=(50, 0, -50),
                                       preserve_luminosity=True)
        self.assertLess(abs(luma(shifted) - luma(image)), 5.0)

    def test_zero_shift_is_a_no_op(self):
        image = gradient_rgb()
        result = adjust_color_balance(image)
        self.assertLess(float(np.abs(result.astype(int) - image.astype(int)).mean()), 1.0)

    def test_wrong_value_count_raises(self):
        with self.assertRaises(ValueError):
            adjust_color_balance(gradient_rgb(), shadows=(10, 10))

    def test_out_of_range_value_raises(self):
        with self.assertRaises(ValueError):
            adjust_color_balance(gradient_rgb(), shadows=(500, 0, 0))

    def test_cmyk_cyan_reduces_red(self):
        image = gradient_rgb()
        result = adjust_cmyk(image, cyan=40)
        self.assertLess(result[:, :, 0].mean(), image[:, :, 0].mean())

    def test_cmyk_black_darkens_everything(self):
        image = gradient_rgb()
        self.assertLess(adjust_cmyk(image, black=30).mean(), image.mean())

    def test_cmyk_out_of_range_raises(self):
        with self.assertRaises(ValueError):
            adjust_cmyk(gradient_rgb(), cyan=500)

    def test_channel_mixer_identity(self):
        image = colorful()
        np.testing.assert_array_equal(channel_mixer(image), image)

    def test_channel_mixer_can_build_monochrome(self):
        image = colorful()
        result = channel_mixer(image, (1, 0, 0), (1, 0, 0), (1, 0, 0))
        np.testing.assert_array_equal(result[:, :, 0], result[:, :, 1])
        np.testing.assert_array_equal(result[:, :, 1], result[:, :, 2])

    def test_channel_mixer_rejects_bad_shape(self):
        with self.assertRaises(ValueError):
            channel_mixer(colorful(), (1, 0), (0, 1, 0), (0, 0, 1))


class TestInvert(unittest.TestCase):

    def test_invert_is_its_own_inverse(self):
        image = colorful()
        np.testing.assert_array_equal(invert(invert(image)), image)

    def test_invert_maps_black_to_white(self):
        black = np.zeros((8, 8, 3), dtype=np.uint8)
        self.assertTrue((invert(black) == 255).all())

    def test_invert_preserves_alpha(self):
        rgb = colorful()
        alpha = np.full((*rgb.shape[:2], 1), 77, dtype=np.uint8)
        result = invert(np.concatenate([rgb, alpha], axis=2))
        np.testing.assert_array_equal(result[:, :, 3], alpha[:, :, 0])

    def test_invert_channel_touches_only_that_channel(self):
        image = colorful()
        result = invert_channel(image, 'g')
        np.testing.assert_array_equal(result[:, :, 0], image[:, :, 0])
        np.testing.assert_array_equal(result[:, :, 1], 255 - image[:, :, 1])

    def test_invert_channel_rejects_bad_name(self):
        with self.assertRaises(ValueError):
            invert_channel(colorful(), 'x')

    def test_invert_luminance_flips_brightness(self):
        image = gradient_rgb()
        result = invert_luminance(image)
        # The dark end becomes the bright end
        self.assertGreater(result[:, :8].mean(), result[:, -8:].mean())

    def test_invert_luminance_on_grayscale(self):
        gray = np.linspace(0, 255, 64, dtype=np.uint8).reshape(8, 8)
        np.testing.assert_array_equal(invert_luminance(gray), 255 - gray)

    def test_solarize_only_affects_values_above_threshold(self):
        image = gradient_rgb()
        result = solarize(image, threshold=128)
        below = image <= 128
        np.testing.assert_array_equal(result[below], image[below])
        above = image > 128
        np.testing.assert_array_equal(result[above], 255 - image[above])

    def test_solarize_rejects_bad_threshold(self):
        with self.assertRaises(ValueError):
            solarize(gradient_rgb(), threshold=300)


if __name__ == '__main__':
    unittest.main()
