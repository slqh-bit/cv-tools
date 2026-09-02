"""Unit tests for the enhancement and geometric-correction filters."""

import json
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np

from cv_tools.filters import (
    CameraCalibration,
    KNOWN_RATIOS,
    PIXEL_ASPECT_RATIOS,
    apply_barrel_distortion,
    auto_correct_perspective,
    correct_barrel_distortion,
    correct_fisheye,
    correct_perspective,
    correct_perspective_named,
    correct_pixel_aspect,
    correct_pixel_aspect_named,
    describe_aspect,
    enhance_detail,
    estimate_h,
    estimate_shifts,
    estimate_straightness,
    find_document_corners,
    fit_to_aspect,
    load_calibration,
    local_contrast,
    multiscale_detail,
    nl_means_denoise,
    nl_means_denoise_auto,
    nl_means_denoise_frames,
    order_corners,
    save_calibration,
    super_resolve,
    super_resolve_report,
    texture_boost,
    undistort,
    upscale,
)


def textured(height: int = 64, width: int = 80) -> np.ndarray:
    rng = np.random.default_rng(5)
    yy, xx = np.mgrid[0:height, 0:width]
    image = np.zeros((height, width, 3), dtype=np.float32)
    image[:, :, 0] = 120 + 50 * np.sin(xx / 9.0)
    image[:, :, 1] = 130 + 40 * np.cos(yy / 7.0)
    image[:, :, 2] = 110 + 45 * np.sin((xx + yy) / 11.0)
    image += rng.normal(0, 3.0, image.shape)
    return np.clip(image, 0, 255).astype(np.uint8)


def broadband(height: int = 64, width: int = 80) -> np.ndarray:
    """
    Detail with a flat spectrum, which phase correlation locks onto cleanly.
    Unlike the sinusoidal ``textured``, its autocorrelation has one clear peak.
    """
    rng = np.random.default_rng(21)
    return rng.integers(0, 256, (height, width, 3), dtype=np.uint8)


def noisy(sigma: float = 22.0) -> np.ndarray:
    rng = np.random.default_rng(8)
    base = textured().astype(np.float32)
    return np.clip(base + rng.normal(0, sigma, base.shape), 0, 255).astype(np.uint8)


def document_scene(height: int = 200, width: int = 260) -> np.ndarray:
    """A bright quadrilateral on a dark background."""
    image = np.full((height, width, 3), 30, dtype=np.uint8)
    corners = np.array([[60, 30], [210, 50], [195, 165], [40, 145]], dtype=np.int32)
    cv2.fillPoly(image, [corners], (235, 235, 230))
    cv2.putText(image, 'TEXT', (80, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (20, 20, 20), 2)
    return image


def grid_scene(height: int = 120, width: int = 160) -> np.ndarray:
    """Straight lines, so distortion is visible."""
    image = np.full((height, width, 3), 20, dtype=np.uint8)
    for x in range(10, width, 20):
        cv2.line(image, (x, 0), (x, height), (230, 230, 230), 1)
    for y in range(10, height, 20):
        cv2.line(image, (0, y), (width, y), (230, 230, 230), 1)
    return image


class TestNLMeans(unittest.TestCase):

    def test_reduces_noise(self):
        from cv_tools.filters import estimate_noise
        image = noisy()
        result = nl_means_denoise(image, h=12)
        self.assertLess(estimate_noise(result), estimate_noise(image))
        self.assertEqual(result.shape, image.shape)

    def test_grayscale_input(self):
        gray = cv2.cvtColor(noisy(), cv2.COLOR_RGB2GRAY)
        result = nl_means_denoise(gray, h=12)
        self.assertEqual(result.shape, gray.shape)
        self.assertEqual(result.ndim, 2)

    def test_alpha_preserved(self):
        rgb = noisy()
        alpha = np.full((*rgb.shape[:2], 1), 210, dtype=np.uint8)
        result = nl_means_denoise(np.concatenate([rgb, alpha], axis=2), h=10)
        np.testing.assert_array_equal(result[:, :, 3], alpha[:, :, 0])

    def test_stronger_h_smooths_more(self):
        image = noisy()
        gentle = nl_means_denoise(image, h=5)
        strong = nl_means_denoise(image, h=25)
        self.assertLess(strong.std(), gentle.std())

    def test_rejects_bad_parameters(self):
        image = noisy()
        for kwargs in ({'h': 0}, {'template_window': 4}, {'search_window': 4},
                       {'template_window': 21, 'search_window': 7}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    nl_means_denoise(image, **kwargs)

    def test_estimate_h_tracks_noise(self):
        self.assertGreater(estimate_h(noisy(30.0)), estimate_h(noisy(5.0)))

    def test_estimate_h_rejects_bad_aggressiveness(self):
        with self.assertRaises(ValueError):
            estimate_h(noisy(), aggressiveness=0)

    def test_auto_denoise_runs(self):
        from cv_tools.filters import estimate_noise
        image = noisy()
        result = nl_means_denoise_auto(image)
        self.assertLess(estimate_noise(result), estimate_noise(image))

    def test_temporal_denoise_uses_neighbours(self):
        rng = np.random.default_rng(3)
        base = textured()
        frames = [
            np.clip(base.astype(np.float32) + rng.normal(0, 20, base.shape), 0, 255
                    ).astype(np.uint8)
            for _ in range(5)
        ]
        result = nl_means_denoise_frames(frames, index=2, h=12, temporal_window=3)
        error = lambda a: float(np.abs(a.astype(float) - base.astype(float)).mean())
        self.assertLess(error(result), error(frames[2]))

    def test_temporal_denoise_validates_input(self):
        frames = [textured() for _ in range(3)]
        with self.assertRaises(ValueError):
            nl_means_denoise_frames([], temporal_window=3)
        with self.assertRaises(ValueError):
            nl_means_denoise_frames(frames, temporal_window=4)
        with self.assertRaises(ValueError):
            nl_means_denoise_frames(frames, index=99, temporal_window=3)

    def test_temporal_denoise_rejects_shape_mismatch(self):
        frames = [textured(), textured(32, 32), textured()]
        with self.assertRaises(ValueError):
            nl_means_denoise_frames(frames, temporal_window=3)


class TestSuperResolution(unittest.TestCase):

    def test_upscale_changes_size_only(self):
        image = textured()
        result = upscale(image, scale=2.0)
        self.assertEqual(result.shape[:2], (image.shape[0] * 2, image.shape[1] * 2))

    def test_upscale_methods_run(self):
        image = textured()
        for method in ('nearest', 'bilinear', 'bicubic', 'lanczos'):
            with self.subTest(method=method):
                self.assertEqual(upscale(image, 2.0, method).shape[:2],
                                 (image.shape[0] * 2, image.shape[1] * 2))

    def test_upscale_nearest_invents_no_values(self):
        image = textured()
        enlarged = upscale(image, 2.0, 'nearest')
        # Nearest-neighbour can only repeat existing samples
        self.assertTrue(set(np.unique(enlarged)).issubset(set(np.unique(image))))

    def test_upscale_rejects_bad_arguments(self):
        with self.assertRaises(ValueError):
            upscale(textured(), scale=0)
        with self.assertRaises(ValueError):
            upscale(textured(), method='magic')

    def test_estimate_shifts_recovers_a_known_offset(self):
        # Broadband detail, not the sinusoidal texture: phase correlation needs
        # a single dominant peak, and a periodic scene gives it several
        base = broadband()
        matrix = np.float32([[1, 0, 2.0], [0, 1, -1.0]])
        shifted = cv2.warpAffine(base, matrix, (base.shape[1], base.shape[0]),
                                 borderMode=cv2.BORDER_REFLECT)

        shifts = estimate_shifts([base, shifted])
        dx, dy = shifts[1]
        self.assertAlmostEqual(dx, 2.0, delta=0.5)
        self.assertAlmostEqual(dy, -1.0, delta=0.5)

    def test_estimate_shifts_is_unreliable_on_periodic_content(self):
        # Documented limitation: a repeating pattern defeats the method
        yy, xx = np.mgrid[0:64, 0:80]
        periodic = np.clip(120 + 50 * np.sin(xx / 9.0), 0, 255).astype(np.uint8)
        periodic = np.repeat(periodic[:, :, np.newaxis], 3, axis=2)

        matrix = np.float32([[1, 0, 2.5], [0, 1, 0]])
        shifted = cv2.warpAffine(periodic, matrix, (80, 64), borderMode=cv2.BORDER_REFLECT)

        dx, _ = estimate_shifts([periodic, shifted])[1]
        # Far from the true 2.5 - which is why super_resolve_report exists
        self.assertGreater(abs(dx - 2.5), 1.0)

    def test_estimate_shifts_reference_is_zero(self):
        frames = [textured(), textured()]
        self.assertEqual(estimate_shifts(frames)[0], (0.0, 0.0))

    def test_estimate_shifts_validates_input(self):
        with self.assertRaises(ValueError):
            estimate_shifts([])
        with self.assertRaises(ValueError):
            estimate_shifts([textured()], reference=5)

    def test_super_resolve_produces_the_target_size(self):
        base = broadband()
        frames = []
        for dx, dy in ((0, 0), (0.5, 0), (0, 0.5), (0.5, 0.5)):
            matrix = np.float32([[1, 0, dx], [0, 1, dy]])
            frames.append(cv2.warpAffine(base, matrix, (base.shape[1], base.shape[0]),
                                         borderMode=cv2.BORDER_REFLECT))

        result = super_resolve(frames, scale=2.0)
        self.assertEqual(result.shape[:2], (base.shape[0] * 2, base.shape[1] * 2))

    def test_super_resolve_rejects_scale_of_one(self):
        with self.assertRaises(ValueError):
            super_resolve([textured()], scale=1.0)

    def test_super_resolve_refuses_a_single_usable_frame(self):
        # The reference always measures as zero shift, so it survives any
        # limit; reconstructing from it alone would just be an upscale
        base = broadband()
        matrix = np.float32([[1, 0, 30], [0, 1, 30]])
        far = cv2.warpAffine(base, matrix, (base.shape[1], base.shape[0]),
                             borderMode=cv2.BORDER_REFLECT)

        with self.assertRaises(ValueError) as ctx:
            super_resolve([base, far], scale=2.0, max_shift=2.0)
        self.assertIn('plain upscale', str(ctx.exception))

    def test_super_resolve_needs_more_than_one_frame(self):
        with self.assertRaises(ValueError):
            super_resolve([broadband()], scale=2.0)

    def test_report_flags_absent_subpixel_motion(self):
        identical = [textured() for _ in range(4)]
        report = super_resolve_report(identical)
        self.assertFalse(report['usable'])
        self.assertEqual(report['frames'], 4)

    def test_report_detects_subpixel_motion(self):
        base = textured()
        frames = [base]
        for dx, dy in ((0.5, 0.25), (0.25, 0.5), (0.75, 0.75)):
            matrix = np.float32([[1, 0, dx], [0, 1, dy]])
            frames.append(cv2.warpAffine(base, matrix, (base.shape[1], base.shape[0]),
                                         borderMode=cv2.BORDER_REFLECT))
        self.assertTrue(super_resolve_report(frames)['usable'])


class TestDetailEnhancement(unittest.TestCase):

    def test_local_contrast_increases_spread(self):
        image = textured()
        self.assertGreater(local_contrast(image, strength=1.0).std(), image.std())

    def test_local_contrast_zero_strength_is_a_no_op(self):
        image = textured()
        np.testing.assert_array_equal(local_contrast(image, strength=0.0), image)

    def test_local_contrast_rejects_bad_parameters(self):
        with self.assertRaises(ValueError):
            local_contrast(textured(), radius=0)
        with self.assertRaises(ValueError):
            local_contrast(textured(), strength=-1)

    def test_enhance_detail_preserves_shape(self):
        image = textured()
        self.assertEqual(enhance_detail(image).shape, image.shape)

    def test_enhance_detail_handles_grayscale(self):
        gray = cv2.cvtColor(textured(), cv2.COLOR_RGB2GRAY)
        result = enhance_detail(gray)
        self.assertEqual(result.ndim, 2)
        self.assertEqual(result.shape, gray.shape)

    def test_enhance_detail_rejects_bad_sigmas(self):
        with self.assertRaises(ValueError):
            enhance_detail(textured(), sigma_r=2.0)
        with self.assertRaises(ValueError):
            enhance_detail(textured(), sigma_s=500)

    def test_multiscale_detail_runs(self):
        image = textured()
        result = multiscale_detail(image, scales=(2.0, 8.0), strengths=(0.6, 0.3))
        self.assertEqual(result.shape, image.shape)
        self.assertGreater(result.std(), image.std())

    def test_multiscale_detail_validates_arguments(self):
        image = textured()
        with self.assertRaises(ValueError):
            multiscale_detail(image, scales=(2.0, 8.0), strengths=(0.5,))
        with self.assertRaises(ValueError):
            multiscale_detail(image, scales=(8.0, 2.0), strengths=(0.5, 0.5))
        with self.assertRaises(ValueError):
            multiscale_detail(image, scales=(), strengths=())

    def test_texture_boost_runs(self):
        image = textured()
        self.assertEqual(texture_boost(image).shape, image.shape)

    def test_texture_boost_zero_amount_is_a_no_op(self):
        image = textured()
        np.testing.assert_array_equal(texture_boost(image, amount=0.0), image)


class TestPerspective(unittest.TestCase):

    def test_order_corners_is_order_independent(self):
        square = [(10, 10), (90, 12), (95, 80), (5, 78)]
        expected = order_corners(square)
        for rotation in range(4):
            rotated = square[rotation:] + square[:rotation]
            np.testing.assert_array_equal(order_corners(rotated), expected)

    def test_order_corners_rejects_wrong_count(self):
        with self.assertRaises(ValueError):
            order_corners([(0, 0), (1, 1)])

    def test_rectifies_to_a_rectangle(self):
        image = document_scene()
        corners = [(60, 30), (210, 50), (195, 165), (40, 145)]
        result = correct_perspective(image, corners)
        self.assertEqual(result.ndim, 3)
        self.assertGreater(result.shape[0], 10)
        self.assertGreater(result.shape[1], 10)

    def test_known_aspect_ratio_is_honoured(self):
        image = document_scene()
        corners = [(60, 30), (210, 50), (195, 165), (40, 145)]
        result = correct_perspective(image, corners, aspect_ratio=2.0)
        ratio = result.shape[1] / result.shape[0]
        self.assertAlmostEqual(ratio, 2.0, delta=0.05)

    def test_named_ratio(self):
        image = document_scene()
        corners = [(60, 30), (210, 50), (195, 165), (40, 145)]
        result = correct_perspective_named(image, corners, 'plate_eu')
        ratio = result.shape[1] / result.shape[0]
        self.assertAlmostEqual(ratio, KNOWN_RATIOS['plate_eu'], delta=0.05)

    def test_unknown_named_ratio_raises(self):
        with self.assertRaises(ValueError):
            correct_perspective_named(document_scene(), [(0, 0), (10, 0), (10, 10), (0, 10)],
                                      'nonexistent')

    def test_explicit_output_size(self):
        image = document_scene()
        corners = [(60, 30), (210, 50), (195, 165), (40, 145)]
        result = correct_perspective(image, corners, output_width=200, output_height=100)
        self.assertEqual(result.shape[:2], (100, 200))

    def test_unknown_interpolation_raises(self):
        with self.assertRaises(ValueError):
            correct_perspective(document_scene(), [(0, 0), (10, 0), (10, 10), (0, 10)],
                                interpolation='magic')

    def test_find_document_corners_locates_the_shape(self):
        corners = find_document_corners(document_scene())
        self.assertIsNotNone(corners)
        self.assertEqual(corners.shape, (4, 2))
        # Near the corners the scene was drawn with
        expected = order_corners([(60, 30), (210, 50), (195, 165), (40, 145)])
        self.assertLess(float(np.abs(corners - expected).max()), 15)

    def test_find_document_corners_returns_none_on_noise(self):
        rng = np.random.default_rng(2)
        noise = rng.integers(0, 255, (120, 120, 3), dtype=np.uint8)
        self.assertIsNone(find_document_corners(noise, min_area_ratio=0.5))

    def test_find_document_corners_validates_ratio(self):
        with self.assertRaises(ValueError):
            find_document_corners(document_scene(), min_area_ratio=0)

    def test_auto_correct_returns_original_when_nothing_found(self):
        rng = np.random.default_rng(4)
        noise = rng.integers(0, 255, (120, 120, 3), dtype=np.uint8)
        np.testing.assert_array_equal(
            auto_correct_perspective(noise, min_area_ratio=0.9), noise
        )


class TestFisheye(unittest.TestCase):

    def test_barrel_correction_preserves_size(self):
        image = grid_scene()
        self.assertEqual(correct_barrel_distortion(image, k1=-0.2).shape, image.shape)

    def test_barrel_zero_coefficients_is_near_identity(self):
        image = grid_scene()
        result = correct_barrel_distortion(image, k1=0.0, k2=0.0, zoom=1.0)
        self.assertLess(float(np.abs(result.astype(int) - image.astype(int)).mean()), 2.0)

    def test_barrel_round_trip_recovers_straightness(self):
        image = grid_scene()
        distorted = apply_barrel_distortion(image, k1=0.25)
        corrected = correct_barrel_distortion(distorted, k1=-0.25)

        # Correction should bring it closer to the original than the distortion left it
        error = lambda a: float(np.abs(a.astype(float) - image.astype(float)).mean())
        self.assertLess(error(corrected), error(distorted))

    def test_barrel_rejects_bad_zoom(self):
        with self.assertRaises(ValueError):
            correct_barrel_distortion(grid_scene(), zoom=0)

    def test_barrel_rejects_unknown_border(self):
        with self.assertRaises(ValueError):
            correct_barrel_distortion(grid_scene(), border_mode='magic')

    def test_fisheye_preserves_size(self):
        image = grid_scene()
        self.assertEqual(correct_fisheye(image, strength=0.5).shape, image.shape)

    def test_fisheye_zero_strength_is_identity(self):
        image = grid_scene()
        np.testing.assert_array_equal(correct_fisheye(image, strength=0.0), image)

    def test_fisheye_rejects_out_of_range_strength(self):
        with self.assertRaises(ValueError):
            correct_fisheye(grid_scene(), strength=2.0)

    def test_straightness_scores_a_grid_above_noise(self):
        rng = np.random.default_rng(7)
        noise = rng.integers(0, 255, (120, 160, 3), dtype=np.uint8)
        self.assertGreater(estimate_straightness(grid_scene()),
                           estimate_straightness(noise))

    def test_straightness_rejects_bad_length(self):
        with self.assertRaises(ValueError):
            estimate_straightness(grid_scene(), min_line_length=1)


class TestAspectRatio(unittest.TestCase):

    def test_pixel_aspect_stretches_width(self):
        image = textured(48, 64)
        result = correct_pixel_aspect(image, 1.5)
        self.assertEqual(result.shape[0], 48)
        self.assertEqual(result.shape[1], 96)

    def test_pixel_aspect_can_squash_height(self):
        image = textured(48, 64)
        result = correct_pixel_aspect(image, 1.5, scale_axis='height')
        self.assertEqual(result.shape[1], 64)
        self.assertEqual(result.shape[0], 32)

    def test_unity_pixel_aspect_is_a_no_op(self):
        image = textured()
        np.testing.assert_array_equal(correct_pixel_aspect(image, 1.0), image)

    def test_named_format(self):
        image = textured(48, 64)
        result = correct_pixel_aspect_named(image, 'pal_43')
        expected = int(round(64 * PIXEL_ASPECT_RATIOS['pal_43']))
        self.assertEqual(result.shape[1], expected)

    def test_unknown_format_raises(self):
        with self.assertRaises(ValueError):
            correct_pixel_aspect_named(textured(), 'betamax')

    def test_rejects_bad_arguments(self):
        with self.assertRaises(ValueError):
            correct_pixel_aspect(textured(), 0)
        with self.assertRaises(ValueError):
            correct_pixel_aspect(textured(), 1.5, scale_axis='depth')

    def test_fit_pad_keeps_all_content(self):
        image = textured(48, 64)   # 4:3
        result = fit_to_aspect(image, 16 / 9, mode='pad')
        self.assertEqual(result.shape[0], 48)
        self.assertAlmostEqual(result.shape[1] / result.shape[0], 16 / 9, delta=0.02)

    def test_fit_crop_trims(self):
        image = textured(48, 64)
        result = fit_to_aspect(image, 1.0, mode='crop')
        self.assertEqual(result.shape[:2], (48, 48))

    def test_fit_stretch_distorts(self):
        image = textured(48, 64)
        result = fit_to_aspect(image, 1.0, mode='stretch')
        self.assertEqual(result.shape[:2], (48, 48))

    def test_fit_matching_ratio_is_a_no_op(self):
        image = textured(48, 64)
        np.testing.assert_array_equal(fit_to_aspect(image, 64 / 48), image)

    def test_fit_rejects_bad_mode(self):
        with self.assertRaises(ValueError):
            fit_to_aspect(textured(), 1.5, mode='squish')

    def test_describe_reports_display_geometry(self):
        info = describe_aspect(textured(48, 64), pixel_aspect=1.5)
        self.assertEqual(info['stored_width'], 64)
        self.assertEqual(info['display_width'], 96)
        self.assertFalse(info['square_pixels'])
        self.assertAlmostEqual(info['display_aspect'], (64 / 48) * 1.5)


class TestUndistort(unittest.TestCase):

    def setUp(self):
        self.calibration = CameraCalibration(
            camera_matrix=np.array([[80.0, 0, 40], [0, 80.0, 32], [0, 0, 1]]),
            distortion=np.array([-0.25, 0.08, 0.0, 0.0, 0.0]),
            image_size=(80, 64),
            reprojection_error=0.4,
        )

    def test_undistort_preserves_size_at_alpha_zero(self):
        image = grid_scene(64, 80)
        self.assertEqual(undistort(image, self.calibration).shape, image.shape)

    def test_undistort_changes_the_image(self):
        image = grid_scene(64, 80)
        self.assertFalse(np.array_equal(undistort(image, self.calibration), image))

    def test_undistort_rescales_for_a_different_resolution(self):
        # A calibration made at 80x64 applied to double-size footage
        image = grid_scene(128, 160)
        result = undistort(image, self.calibration)
        self.assertEqual(result.shape[:2], (128, 160))

    def test_undistort_rejects_bad_alpha(self):
        with self.assertRaises(ValueError):
            undistort(grid_scene(64, 80), self.calibration, alpha=2.0)

    def test_reliability_threshold(self):
        self.assertTrue(self.calibration.is_reliable)
        poor = CameraCalibration(self.calibration.camera_matrix,
                                 self.calibration.distortion, (80, 64), 3.5)
        self.assertFalse(poor.is_reliable)

    def test_calibration_roundtrips_through_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'cal.json'
            save_calibration(self.calibration, path)
            loaded = load_calibration(path)

        np.testing.assert_allclose(loaded.camera_matrix, self.calibration.camera_matrix)
        np.testing.assert_allclose(loaded.distortion, self.calibration.distortion)
        self.assertEqual(loaded.image_size, self.calibration.image_size)
        self.assertAlmostEqual(loaded.reprojection_error,
                               self.calibration.reprojection_error)

    def test_rejects_bad_camera_matrix(self):
        with self.assertRaises(ValueError):
            CameraCalibration(np.eye(2), np.zeros(5), (80, 64))

    def test_calibration_requires_enough_detections(self):
        from cv_tools.filters import calibrate_from_chessboard
        # Blank frames contain no chessboard at all
        blanks = [np.zeros((64, 80, 3), dtype=np.uint8) for _ in range(4)]
        with self.assertRaises(ValueError) as ctx:
            calibrate_from_chessboard(blanks, (9, 6))
        self.assertIn('chessboard', str(ctx.exception))

    def test_calibration_validates_arguments(self):
        from cv_tools.filters import calibrate_from_chessboard
        with self.assertRaises(ValueError):
            calibrate_from_chessboard([], (9, 6))
        with self.assertRaises(ValueError):
            calibrate_from_chessboard([grid_scene()], (1, 6))
        with self.assertRaises(ValueError):
            calibrate_from_chessboard([grid_scene()], (9, 6), square_size=0)


if __name__ == '__main__':
    unittest.main()
