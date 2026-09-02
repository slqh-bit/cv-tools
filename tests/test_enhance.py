"""Unit tests for the Sprint 2 filters: sharpen, smoothing, edges, histogram."""

import unittest

import numpy as np

from cv_tools.filters import (
    auto_canny,
    bilateral_filter,
    canny_edges,
    compute_histogram,
    dynamic_range_used,
    edge_density,
    estimate_h,
    estimate_noise,
    gaussian_blur,
    histogram_stats,
    laplacian_edges,
    laplacian_sharpen,
    median_filter,
    nl_means_denoise_auto,
    render_histogram,
    sharpen_grid,
    sobel_edges,
    unsharp_mask,
)


def step_edge(height: int = 64, width: int = 64) -> np.ndarray:
    """Grayscale image split into a dark half and a bright half."""
    image = np.full((height, width), 40, dtype=np.uint8)
    image[:, width // 2:] = 210
    return image


def rgb_step_edge(height: int = 64, width: int = 64) -> np.ndarray:
    """Three-channel version of the step edge."""
    return np.repeat(step_edge(height, width)[:, :, np.newaxis], 3, axis=2)


def noisy_image(height: int = 64, width: int = 64, sigma: float = 25.0) -> np.ndarray:
    """Flat mid-gray RGB image with Gaussian noise."""
    rng = np.random.default_rng(11)
    base = np.full((height, width, 3), 128.0)
    return np.clip(base + rng.normal(0, sigma, base.shape), 0, 255).astype(np.uint8)


def fine_texture(height: int = 64, width: int = 64, square: int = 2) -> np.ndarray:
    """Fine checkerboard - the kind of high-frequency detail blurring destroys."""
    yy, xx = np.mgrid[0:height, 0:width]
    return np.where(((yy // square) + (xx // square)) % 2 == 0, 40, 210).astype(np.uint8)


def salt_and_pepper(height: int = 64, width: int = 64, amount: float = 0.08) -> np.ndarray:
    """Flat gray image speckled with pure black and white pixels."""
    rng = np.random.default_rng(5)
    image = np.full((height, width), 128, dtype=np.uint8)
    mask = rng.random((height, width))
    image[mask < amount / 2] = 0
    image[mask > 1 - amount / 2] = 255
    return image


class TestUnsharpMask(unittest.TestCase):

    def test_preserves_shape_and_dtype(self):
        image = rgb_step_edge()
        result = unsharp_mask(image)
        self.assertEqual(result.shape, image.shape)
        self.assertEqual(result.dtype, np.uint8)

    def test_increases_edge_contrast(self):
        image = rgb_step_edge()
        result = unsharp_mask(image, amount=2.0, radius=2.0)
        # Overshoot at the boundary widens the overall spread
        self.assertGreater(result.std(), image.std())

    def test_zero_amount_is_a_no_op(self):
        image = rgb_step_edge()
        np.testing.assert_array_equal(unsharp_mask(image, amount=0.0), image)

    def test_threshold_protects_flat_noise(self):
        image = noisy_image(sigma=8.0)
        aggressive = unsharp_mask(image, amount=2.0, radius=1.0, threshold=0)
        protected = unsharp_mask(image, amount=2.0, radius=1.0, threshold=40)
        # A high threshold leaves low-contrast noise untouched
        self.assertLess(protected.std(), aggressive.std())

    def test_grayscale_input(self):
        image = step_edge()
        result = unsharp_mask(image)
        self.assertEqual(result.shape, image.shape)
        self.assertEqual(result.ndim, 2)

    def test_alpha_channel_is_preserved(self):
        rgb = rgb_step_edge()
        alpha = np.full((*rgb.shape[:2], 1), 200, dtype=np.uint8)
        result = unsharp_mask(np.concatenate([rgb, alpha], axis=2), amount=1.5)
        self.assertEqual(result.shape[2], 4)
        np.testing.assert_array_equal(result[:, :, 3], alpha[:, :, 0])

    def test_invalid_radius_raises(self):
        with self.assertRaises(ValueError):
            unsharp_mask(rgb_step_edge(), radius=0)

    def test_negative_threshold_raises(self):
        with self.assertRaises(ValueError):
            unsharp_mask(rgb_step_edge(), threshold=-1)

    def test_empty_image_raises(self):
        with self.assertRaises(ValueError):
            unsharp_mask(np.array([], dtype=np.uint8))

    def test_sharpen_grid_returns_composite(self):
        grid = sharpen_grid(rgb_step_edge(), amounts=[0.5, 1.5], radii=[1.0, 2.0])
        self.assertEqual(grid.ndim, 3)
        self.assertGreater(grid.size, 0)


class TestLaplacianSharpen(unittest.TestCase):

    def test_increases_edge_contrast(self):
        image = rgb_step_edge()
        result = laplacian_sharpen(image, strength=1.0)
        self.assertGreater(result.std(), image.std())

    def test_zero_strength_is_a_no_op(self):
        image = rgb_step_edge()
        np.testing.assert_array_equal(laplacian_sharpen(image, strength=0.0), image)

    def test_even_kernel_raises(self):
        with self.assertRaises(ValueError):
            laplacian_sharpen(rgb_step_edge(), kernel_size=4)

    def test_alpha_channel_is_preserved(self):
        rgb = rgb_step_edge()
        alpha = np.full((*rgb.shape[:2], 1), 90, dtype=np.uint8)
        result = laplacian_sharpen(np.concatenate([rgb, alpha], axis=2))
        np.testing.assert_array_equal(result[:, :, 3], alpha[:, :, 0])


class TestSmoothing(unittest.TestCase):

    def test_gaussian_reduces_noise(self):
        image = noisy_image()
        result = gaussian_blur(image, radius=2.0)
        self.assertLess(result.std(), image.std())
        self.assertEqual(result.shape, image.shape)

    def test_gaussian_larger_radius_smooths_more(self):
        image = noisy_image()
        self.assertLess(gaussian_blur(image, radius=4.0).std(),
                        gaussian_blur(image, radius=1.0).std())

    def test_gaussian_rejects_non_positive_radius(self):
        with self.assertRaises(ValueError):
            gaussian_blur(noisy_image(), radius=0)

    def test_gaussian_rejects_even_kernel(self):
        with self.assertRaises(ValueError):
            gaussian_blur(noisy_image(), radius=1.0, kernel_size=4)

    def test_median_removes_salt_and_pepper(self):
        image = salt_and_pepper()
        result = median_filter(image, kernel_size=3)
        # Impulse noise is gone: no pure black or white pixels remain
        self.assertEqual(np.count_nonzero(result == 0), 0)
        self.assertEqual(np.count_nonzero(result == 255), 0)
        self.assertLess(result.std(), image.std())

    def test_median_preserves_a_step_edge(self):
        image = step_edge()
        result = median_filter(image, kernel_size=3)
        # A median filter keeps the two plateaus, unlike a blur
        self.assertEqual(set(np.unique(result).tolist()), {40, 210})

    def test_median_rejects_even_kernel(self):
        with self.assertRaises(ValueError):
            median_filter(salt_and_pepper(), kernel_size=4)

    def test_median_rejects_kernel_below_three(self):
        with self.assertRaises(ValueError):
            median_filter(salt_and_pepper(), kernel_size=1)

    def test_median_large_kernel_on_rgba(self):
        rgb = noisy_image()
        alpha = np.full((*rgb.shape[:2], 1), 255, dtype=np.uint8)
        result = median_filter(np.concatenate([rgb, alpha], axis=2), kernel_size=7)
        self.assertEqual(result.shape[2], 4)

    def test_bilateral_reduces_noise_but_keeps_edge(self):
        rng = np.random.default_rng(2)
        image = rgb_step_edge().astype(np.float32)
        image += rng.normal(0, 12, image.shape)
        image = np.clip(image, 0, 255).astype(np.uint8)

        result = bilateral_filter(image, diameter=9, sigma_color=50, sigma_space=9)

        left = result[:, :20].mean()
        right = result[:, -20:].mean()
        # Flat regions are smoothed
        self.assertLess(result[:, :20].std(), image[:, :20].std())
        # ...while the step between them survives
        self.assertGreater(right - left, 140)

    def test_bilateral_rejects_non_positive_sigma(self):
        with self.assertRaises(ValueError):
            bilateral_filter(noisy_image(), sigma_color=0)

    def test_bilateral_preserves_alpha(self):
        rgb = noisy_image()
        alpha = np.full((*rgb.shape[:2], 1), 128, dtype=np.uint8)
        result = bilateral_filter(np.concatenate([rgb, alpha], axis=2))
        self.assertEqual(result.shape[2], 4)
        np.testing.assert_array_equal(result[:, :, 3], alpha[:, :, 0])


class TestEdgeDetection(unittest.TestCase):

    def test_canny_returns_binary_single_channel(self):
        result = canny_edges(rgb_step_edge(), 50, 150)
        self.assertEqual(result.ndim, 2)
        self.assertEqual(result.dtype, np.uint8)
        self.assertEqual(set(np.unique(result).tolist()), {0, 255})

    def test_canny_finds_the_step_edge(self):
        result = canny_edges(step_edge(), 50, 150)
        columns = np.nonzero(result.any(axis=0))[0]
        # The edge sits at the midpoint of the image
        self.assertTrue(np.all(np.abs(columns - 32) <= 2))

    def test_canny_flat_image_has_no_edges(self):
        flat = np.full((32, 32), 100, dtype=np.uint8)
        self.assertEqual(np.count_nonzero(canny_edges(flat, 50, 150)), 0)

    def test_canny_rejects_inverted_thresholds(self):
        with self.assertRaises(ValueError):
            canny_edges(step_edge(), 200, 100)

    def test_canny_rejects_bad_aperture(self):
        with self.assertRaises(ValueError):
            canny_edges(step_edge(), 50, 150, aperture_size=4)

    def test_canny_pre_blur_suppresses_noise_edges(self):
        image = noisy_image(sigma=40.0)
        unblurred = canny_edges(image, 50, 150)
        blurred = canny_edges(image, 50, 150, blur_sigma=2.0)
        self.assertLess(np.count_nonzero(blurred), np.count_nonzero(unblurred))

    def test_canny_accepts_rgba(self):
        rgb = rgb_step_edge()
        alpha = np.full((*rgb.shape[:2], 1), 255, dtype=np.uint8)
        result = canny_edges(np.concatenate([rgb, alpha], axis=2), 50, 150)
        self.assertEqual(result.ndim, 2)

    def test_auto_canny_finds_edges_without_thresholds(self):
        result = auto_canny(step_edge())
        self.assertGreater(np.count_nonzero(result), 0)

    def test_auto_canny_handles_near_black_frame(self):
        # Median 0 would collapse both thresholds onto the same value
        dark = np.zeros((32, 32), dtype=np.uint8)
        dark[:, 16:] = 30
        result = auto_canny(dark)
        self.assertEqual(result.shape, dark.shape)

    def test_sobel_magnitude_peaks_at_the_edge(self):
        result = sobel_edges(step_edge(), dx=1, dy=1)
        self.assertEqual(result.ndim, 2)
        self.assertEqual(result.dtype, np.uint8)
        self.assertGreater(result[:, 30:35].max(), result[:, :10].max())

    def test_sobel_horizontal_only_ignores_horizontal_edge(self):
        # A vertical gradient has no horizontal derivative
        image = np.tile(np.linspace(0, 255, 64, dtype=np.uint8).reshape(-1, 1), (1, 64))
        horizontal = sobel_edges(image, dx=1, dy=0, normalize=False)
        vertical = sobel_edges(image, dx=0, dy=1, normalize=False)
        self.assertEqual(horizontal.max(), 0)
        self.assertGreater(vertical.max(), 0)

    def test_sobel_rejects_zero_derivatives(self):
        with self.assertRaises(ValueError):
            sobel_edges(step_edge(), dx=0, dy=0)

    def test_sobel_rejects_bad_kernel(self):
        with self.assertRaises(ValueError):
            sobel_edges(step_edge(), kernel_size=9)

    def test_laplacian_responds_to_edges(self):
        result = laplacian_edges(step_edge())
        self.assertEqual(result.ndim, 2)
        self.assertGreater(result[:, 30:35].max(), result[:, :10].max())

    def test_laplacian_rejects_even_kernel(self):
        with self.assertRaises(ValueError):
            laplacian_edges(step_edge(), kernel_size=2)

    def test_edge_density_is_a_fraction(self):
        edges = canny_edges(step_edge(), 50, 150)
        density = edge_density(edges)
        self.assertGreater(density, 0.0)
        self.assertLess(density, 1.0)

    def test_edge_density_higher_for_sharper_image(self):
        # Fine detail, not a single step edge: blurring a lone edge just
        # spreads it over more pixels and would raise the density.
        sharp = fine_texture()
        blurred = gaussian_blur(sharp, radius=3.0)
        self.assertGreater(
            edge_density(sobel_edges(sharp, normalize=False), threshold=50),
            edge_density(sobel_edges(blurred, normalize=False), threshold=50),
        )

    def test_edge_density_on_empty_raises(self):
        with self.assertRaises(ValueError):
            edge_density(np.array([], dtype=np.uint8))


class TestDenoiseStrength(unittest.TestCase):
    """The automatic strength has to improve the image, not flatten it."""

    @staticmethod
    def _psnr(candidate, truth):
        import cv2
        a = cv2.cvtColor(candidate, cv2.COLOR_RGB2GRAY).astype(float)
        b = cv2.cvtColor(truth, cv2.COLOR_RGB2GRAY).astype(float)
        return 10 * np.log10(255 ** 2 / max(float(((a - b) ** 2).mean()), 1e-9))

    def test_auto_denoising_beats_leaving_the_noise_alone(self):
        # It did not. estimate_h returned three times the measured sigma - a
        # strength quoted for other implementations of the algorithm - and at
        # that setting the filter scored 6.9 dB *below* the untouched input on
        # a real CCTV frame, removing more picture than noise.
        rng = np.random.default_rng(7)
        truth = np.repeat(np.repeat(
            rng.integers(40, 210, (24, 32, 3)).astype(np.uint8), 6, axis=0), 6, axis=1)
        noisy = np.clip(truth.astype(float) + rng.normal(0, 12, truth.shape),
                        0, 255).astype(np.uint8)

        cleaned = nl_means_denoise_auto(noisy)
        self.assertGreater(self._psnr(cleaned, truth), self._psnr(noisy, truth))

    def test_the_suggested_strength_stays_near_the_measured_noise(self):
        rng = np.random.default_rng(3)
        frame = np.clip(np.full((96, 128, 3), 120.0) + rng.normal(0, 10, (96, 128, 3)),
                        0, 255).astype(np.uint8)
        sigma = estimate_noise(frame)
        suggested = estimate_h(frame)

        # Below sigma, not a multiple of it: above about 1.5x sigma the filter
        # starts taking texture with the noise
        self.assertLess(suggested, sigma * 1.5)
        self.assertGreater(suggested, sigma * 0.2)

    def test_aggressiveness_scales_the_suggestion(self):
        rng = np.random.default_rng(5)
        frame = np.clip(np.full((64, 64, 3), 120.0) + rng.normal(0, 8, (64, 64, 3)),
                        0, 255).astype(np.uint8)
        self.assertAlmostEqual(estimate_h(frame, aggressiveness=2.0),
                               estimate_h(frame) * 2.0, places=3)


class TestDeterminism(unittest.TestCase):
    """A chain that does not replay identically cannot back a report."""

    def test_sobel_returns_the_same_map_every_time(self):
        # cv2.magnitude dispatches to different SIMD paths between calls and
        # returns results differing in the last float bits - 553.759887695
        # against 553.759826660 for one input. A pixel of a real CCTV frame
        # sat on an integer boundary, so the same image gave two different
        # uint8 maps from one run to the next.
        image = noisy_image(120, 160)
        first = sobel_edges(image)
        for _ in range(8):
            np.testing.assert_array_equal(sobel_edges(image), first)

    def test_every_edge_filter_replays_identically(self):
        image = noisy_image(120, 160)
        for name, call in (
                ('sobel', lambda i: sobel_edges(i)),
                ('laplacian', lambda i: laplacian_edges(i)),
                ('canny', lambda i: canny_edges(i, 50, 150)),
                ('auto_canny', lambda i: auto_canny(i)),
        ):
            with self.subTest(filter=name):
                first = call(image)
                np.testing.assert_array_equal(call(image), first)


class TestHistogram(unittest.TestCase):

    def test_counts_sum_to_pixel_count(self):
        image = rgb_step_edge(32, 32)
        histograms = compute_histogram(image)
        self.assertEqual(sorted(histograms), ['B', 'G', 'R'])
        for counts in histograms.values():
            self.assertEqual(counts.sum(), 32 * 32)

    def test_grayscale_yields_single_channel(self):
        histograms = compute_histogram(step_edge())
        self.assertEqual(list(histograms), ['Gray'])

    def test_normalize_sums_to_one(self):
        histograms = compute_histogram(rgb_step_edge(), normalize=True)
        self.assertAlmostEqual(histograms['R'].sum(), 1.0)

    def test_bin_count_is_respected(self):
        self.assertEqual(len(compute_histogram(step_edge(), bins=32)['Gray']), 32)

    def test_step_edge_is_bimodal(self):
        counts = compute_histogram(step_edge())['Gray']
        self.assertEqual(np.count_nonzero(counts), 2)

    def test_invalid_bins_raises(self):
        with self.assertRaises(ValueError):
            compute_histogram(step_edge(), bins=0)

    def test_stats_report_mean_and_range(self):
        image = np.full((16, 16, 3), 100, dtype=np.uint8)
        stats = histogram_stats(image)
        self.assertEqual(stats['pixels'], 256)
        self.assertAlmostEqual(stats['channels']['R']['mean'], 100.0)
        self.assertEqual(stats['channels']['R']['min'], 100)
        self.assertEqual(stats['channels']['R']['std'], 0.0)

    def test_stats_detect_clipping(self):
        image = np.full((10, 10), 128, dtype=np.uint8)
        image[0, :] = 0     # 10% crushed shadows
        image[1, :] = 255   # 10% blown highlights
        channel = histogram_stats(image)['channels']['Gray']
        self.assertAlmostEqual(channel['clipped_shadows_pct'], 10.0)
        self.assertAlmostEqual(channel['clipped_highlights_pct'], 10.0)

    def test_stats_on_empty_raises(self):
        with self.assertRaises(ValueError):
            histogram_stats(np.array([], dtype=np.uint8))

    def test_dynamic_range_low_for_flat_image(self):
        flat = np.full((32, 32), 128, dtype=np.uint8)
        self.assertLess(dynamic_range_used(flat), 0.05)

    def test_dynamic_range_high_for_full_gradient(self):
        gradient = np.tile(np.linspace(0, 255, 64, dtype=np.uint8), (64, 1))
        self.assertGreater(dynamic_range_used(gradient), 0.9)

    def test_render_returns_requested_size(self):
        chart = render_histogram(rgb_step_edge(), width=400, height=200)
        self.assertEqual(chart.shape, (200, 400, 3))
        self.assertEqual(chart.dtype, np.uint8)

    def test_render_draws_something(self):
        chart = render_histogram(rgb_step_edge(), show_grid=False)
        # Curves are brighter than the background
        self.assertGreater(chart.max(), 100)

    def test_render_log_scale_runs(self):
        chart = render_histogram(rgb_step_edge(), log_scale=True)
        self.assertEqual(chart.shape[2], 3)

    def test_render_grayscale_input(self):
        chart = render_histogram(step_edge())
        self.assertEqual(chart.ndim, 3)

    def test_render_channel_subset(self):
        chart = render_histogram(rgb_step_edge(), channels=['R'])
        self.assertEqual(chart.ndim, 3)

    def test_render_unknown_channel_raises(self):
        with self.assertRaises(ValueError):
            render_histogram(step_edge(), channels=['R'])

    def test_render_rejects_tiny_canvas(self):
        with self.assertRaises(ValueError):
            render_histogram(step_edge(), width=8, height=8)


if __name__ == '__main__':
    unittest.main()
