"""Unit tests for compression analysis, colour deconvolution, component
separation, redaction, and annotation."""

import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np

from cv_tools.filters import (
    COLOR_SPACES,
    STAIN_PRESETS,
    Scale,
    blockiness_score,
    blocking_map,
    channel_grid,
    compression_report,
    deblock,
    deconvolve_colors,
    draw_area_measurement,
    draw_arrow,
    draw_measurement,
    draw_scale_bar,
    draw_shape,
    draw_text,
    estimate_jpeg_quality,
    estimate_stain_vector,
    extract_bit_plane,
    extract_component,
    extract_stain,
    is_reversible,
    measure_area,
    measure_distance,
    normalize_vectors,
    redact,
    redact_region,
    scale_from_reference,
    separate_bit_planes,
    separate_channels,
    separate_frequency,
    verify_redaction,
)


def detailed(height: int = 128, width: int = 160) -> np.ndarray:
    """Sharp edges and text, so compression has something to damage."""
    image = np.full((height, width, 3), 40, dtype=np.uint8)
    for index in range(4, width - 8, 16):
        cv2.rectangle(image, (index, 12), (index + 7, height - 12), (215, 215, 215), -1)
    cv2.circle(image, (width // 3, height // 2), 18, (240, 90, 60), -1)
    cv2.putText(image, 'AB 123', (12, height - 18), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (250, 250, 250), 1, cv2.LINE_AA)
    return image


def photographic(height: int = 128, width: int = 160) -> np.ndarray:
    """
    Smoothly varying content with fine texture, as a camera produces.

    Blockiness is measured against the image's own detail, so it needs
    photographic content: an image of hard synthetic edges that miss the
    8-pixel grid inflates the interior term and hides real blocking.
    """
    rng = np.random.default_rng(13)
    yy, xx = np.mgrid[0:height, 0:width]
    image = np.zeros((height, width, 3), dtype=np.float32)
    image[:, :, 0] = 110 + 60 * np.sin(xx / 37.0) + 25 * np.cos(yy / 23.0)
    image[:, :, 1] = 120 + 50 * np.sin((xx + yy) / 41.0)
    image[:, :, 2] = 100 + 45 * np.cos(xx / 29.0)
    image += rng.normal(0, 6.0, image.shape)
    return np.clip(image, 0, 255).astype(np.uint8)


def jpeg_roundtrip(image: np.ndarray, quality: int) -> np.ndarray:
    """Compress and decompress, so real JPEG artefacts are present."""
    bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    ok, buffer = cv2.imencode('.jpg', bgr, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    assert ok
    return cv2.cvtColor(cv2.imdecode(buffer, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)


def stained_document(height: int = 64, width: int = 96) -> np.ndarray:
    """Blue ink strokes over a black printed line on white paper."""
    image = np.full((height, width, 3), 245, dtype=np.uint8)
    cv2.line(image, (5, 30), (90, 30), (35, 35, 35), 3)         # black toner
    cv2.line(image, (10, 20), (85, 45), (40, 60, 190), 3)       # blue ink
    return image


class TestCompressionAnalysis(unittest.TestCase):

    def test_heavy_compression_scores_higher(self):
        original = photographic()
        light = jpeg_roundtrip(original, 95)
        heavy = jpeg_roundtrip(original, 15)

        self.assertGreater(blockiness_score(heavy)['blockiness'],
                           blockiness_score(light)['blockiness'])

    def test_score_tracks_quality_monotonically(self):
        # The score must discriminate across the whole realistic range, not
        # saturate as soon as blocking becomes visible
        original = photographic()
        scores = [
            blockiness_score(jpeg_roundtrip(original, q))['blockiness']
            for q in (90, 50, 20, 8)
        ]
        self.assertEqual(scores, sorted(scores))
        self.assertLess(scores[0], scores[-1])
        self.assertGreater(scores[-1] - scores[1], 5.0)

    def test_uncompressed_image_scores_low(self):
        score = blockiness_score(photographic())
        self.assertLess(score['blockiness'], 10.0)

    def test_synthetic_edges_defeat_the_measure(self):
        # Documented limitation: hard edges that miss the 8-pixel grid inflate
        # the interior term, so heavy compression can still read as none
        heavy = jpeg_roundtrip(detailed(), 10)
        self.assertLess(blockiness_score(heavy)['ratio'], 1.0)

    def test_score_reports_its_components(self):
        score = blockiness_score(jpeg_roundtrip(photographic(), 20))
        for key in ('boundary_step', 'interior_step', 'ratio', 'blockiness'):
            self.assertIn(key, score)
        self.assertGreater(score['ratio'], 0)

    def test_tiny_image_raises(self):
        with self.assertRaises(ValueError):
            blockiness_score(np.zeros((8, 8), dtype=np.uint8))

    def test_blocking_map_matches_input_size(self):
        image = jpeg_roundtrip(photographic(), 20)
        mapped = blocking_map(image, block_size=32)
        self.assertEqual(mapped.shape, image.shape[:2])
        self.assertEqual(mapped.ndim, 2)

    def test_blocking_map_without_upscale(self):
        mapped = blocking_map(detailed(), block_size=32, upscale=False)
        self.assertEqual(mapped.shape, (128 // 32, 160 // 32))

    def test_blocking_map_rejects_small_block(self):
        with self.assertRaises(ValueError):
            blocking_map(detailed(), block_size=8)

    def test_jpeg_quality_read_from_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'sample.jpg'
            cv2.imwrite(str(path), cv2.cvtColor(detailed(), cv2.COLOR_RGB2BGR),
                        [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            info = estimate_jpeg_quality(path)

        self.assertIsNotNone(info)
        self.assertAlmostEqual(info['quality'], 85, delta=8)
        self.assertGreaterEqual(info['tables'], 1)

    def test_jpeg_quality_none_for_png(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'sample.png'
            cv2.imwrite(str(path), cv2.cvtColor(detailed(), cv2.COLOR_RGB2BGR))
            self.assertIsNone(estimate_jpeg_quality(path))

    def test_jpeg_quality_none_for_missing_file(self):
        self.assertIsNone(estimate_jpeg_quality('does_not_exist.jpg'))

    def test_report_flags_likely_jpeg(self):
        heavy = compression_report(jpeg_roundtrip(photographic(), 12))
        clean = compression_report(photographic())
        self.assertTrue(heavy['likely_jpeg'])
        self.assertGreater(heavy['blockiness'], clean['blockiness'])

    def test_report_includes_quality_when_path_given(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'sample.jpg'
            cv2.imwrite(str(path), cv2.cvtColor(detailed(), cv2.COLOR_RGB2BGR),
                        [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            image = cv2.cvtColor(cv2.imread(str(path)), cv2.COLOR_BGR2RGB)
            report = compression_report(image, path=path)

        self.assertIn('jpeg_quality', report)
        self.assertIsNotNone(report['jpeg_quality'])

    def test_deblock_reduces_blockiness(self):
        heavy = jpeg_roundtrip(photographic(), 12)
        smoothed = deblock(heavy, strength=1.0)
        self.assertLess(blockiness_score(smoothed)['ratio'],
                        blockiness_score(heavy)['ratio'])

    def test_deblock_zero_strength_is_a_no_op(self):
        image = detailed()
        np.testing.assert_array_equal(deblock(image, strength=0.0), image)

    def test_deblock_rejects_bad_strength(self):
        with self.assertRaises(ValueError):
            deblock(detailed(), strength=2.0)


class TestColorDeconvolution(unittest.TestCase):

    def test_returns_three_channels(self):
        channels = deconvolve_colors(stained_document(), preset='h_e')
        self.assertEqual(len(channels), 3)
        for channel in channels:
            self.assertEqual(channel.ndim, 2)
            self.assertEqual(channel.dtype, np.uint8)

    def test_separates_two_inks(self):
        document = stained_document()
        ink_vector = estimate_stain_vector(document, 45, 30, 6, 6)
        channels = deconvolve_colors(document, vectors=[ink_vector])

        # The channel matching the sampled ink should register it strongly
        self.assertEqual(channels[0].shape, document.shape[:2])
        self.assertLess(float(channels[0].min()), 250.0)

    def test_normalize_vectors_produces_unit_length(self):
        basis = normalize_vectors([(0.65, 0.70, 0.29)])
        for row in basis:
            self.assertAlmostEqual(float(np.linalg.norm(row)), 1.0, places=6)

    def test_normalize_completes_a_two_vector_basis(self):
        basis = normalize_vectors([(0.65, 0.70, 0.29), (0.07, 0.99, 0.11)])
        self.assertEqual(basis.shape, (3, 3))
        self.assertGreater(abs(float(np.linalg.det(basis))), 1e-6)

    def test_parallel_vectors_raise(self):
        with self.assertRaises(ValueError):
            normalize_vectors([(1.0, 0.0, 0.0), (2.0, 0.0, 0.0)])

    def test_zero_vector_raises(self):
        with self.assertRaises(ValueError):
            normalize_vectors([(0.0, 0.0, 0.0)])

    def test_too_many_vectors_raise(self):
        with self.assertRaises(ValueError):
            normalize_vectors([(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0)])

    def test_unknown_preset_lists_options(self):
        with self.assertRaises(ValueError) as ctx:
            deconvolve_colors(stained_document(), preset='nope')
        self.assertIn('h_e', str(ctx.exception))

    def test_requires_vectors_or_preset(self):
        with self.assertRaises(ValueError):
            deconvolve_colors(stained_document())

    def test_grayscale_input_raises(self):
        with self.assertRaises(ValueError):
            deconvolve_colors(np.zeros((16, 16), dtype=np.uint8), preset='h_e')

    def test_extract_stain_selects_one_channel(self):
        result = extract_stain(stained_document(), index=1, preset='h_e')
        self.assertEqual(result.ndim, 2)

    def test_extract_stain_invert(self):
        document = stained_document()
        plain = extract_stain(document, index=0, preset='h_e')
        inverted = extract_stain(document, index=0, preset='h_e', invert=True)
        np.testing.assert_array_equal(inverted, 255 - plain)

    def test_extract_stain_rejects_bad_index(self):
        with self.assertRaises(ValueError):
            extract_stain(stained_document(), index=5)

    def test_estimate_vector_is_unit_length(self):
        vector = estimate_stain_vector(stained_document(), 45, 30, 6, 6)
        self.assertAlmostEqual(float(np.linalg.norm(vector)), 1.0, places=5)

    def test_estimate_vector_rejects_blank_paper(self):
        blank = np.full((32, 32, 3), 255, dtype=np.uint8)
        with self.assertRaises(ValueError):
            estimate_stain_vector(blank, 5, 5, 10, 10)

    def test_estimate_vector_rejects_outside_region(self):
        with self.assertRaises(ValueError):
            estimate_stain_vector(stained_document(), 500, 500, 10, 10)


class TestComponentSeparation(unittest.TestCase):

    def test_rgb_channels_match_the_source(self):
        image = detailed()
        channels = separate_channels(image, 'rgb')
        np.testing.assert_array_equal(channels['R'], image[:, :, 0])
        np.testing.assert_array_equal(channels['B'], image[:, :, 2])

    def test_every_space_yields_three_channels(self):
        image = detailed()
        for space in COLOR_SPACES:
            with self.subTest(space=space):
                channels = separate_channels(image, space)
                self.assertEqual(len(channels), 3)
                for channel in channels.values():
                    self.assertEqual(channel.shape, image.shape[:2])

    def test_unknown_space_raises(self):
        with self.assertRaises(ValueError):
            separate_channels(detailed(), 'cmyk')

    def test_grayscale_input_raises(self):
        with self.assertRaises(ValueError):
            separate_channels(np.zeros((16, 16), dtype=np.uint8))

    def test_extract_component_normalizes(self):
        image = detailed()
        plain = extract_component(image, 'lab', 'a', normalize=False)
        stretched = extract_component(image, 'lab', 'a', normalize=True)
        self.assertGreaterEqual(float(np.ptp(stretched)), float(np.ptp(plain)))

    def test_extract_component_unknown_channel_raises(self):
        with self.assertRaises(ValueError):
            extract_component(detailed(), 'lab', 'Z')

    def test_frequency_split_recombines(self):
        image = detailed()
        base, detail = separate_frequency(image, radius=6.0, amplify=1.0)

        self.assertEqual(base.shape, image.shape)
        self.assertEqual(detail.shape, image.shape)
        # base + (detail - 128) should approximate the original
        recombined = np.clip(base.astype(np.float32)
                             + detail.astype(np.float32) - 128.0, 0, 255)
        self.assertLess(float(np.abs(recombined - image.astype(np.float32)).mean()), 3.0)

    def test_frequency_split_validates_arguments(self):
        with self.assertRaises(ValueError):
            separate_frequency(detailed(), radius=0)
        with self.assertRaises(ValueError):
            separate_frequency(detailed(), amplify=0)

    def test_bit_planes_reconstruct_the_intensity(self):
        image = detailed()
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        planes = separate_bit_planes(image)

        self.assertEqual(len(planes), 8)
        rebuilt = sum((planes[bit] // 255).astype(np.uint16) << bit for bit in range(8))
        np.testing.assert_array_equal(rebuilt.astype(np.uint8), gray)

    def test_bit_planes_are_binary(self):
        for plane in separate_bit_planes(detailed()):
            self.assertTrue(set(np.unique(plane).tolist()).issubset({0, 255}))

    def test_high_plane_resembles_the_image_more_than_the_low_one(self):
        image = detailed()
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY).astype(float)
        planes = separate_bit_planes(image)

        correlate = lambda p: abs(np.corrcoef(gray.ravel(), p.ravel().astype(float))[0, 1])
        self.assertGreater(correlate(planes[7]), correlate(planes[0]))

    def test_extract_bit_plane_rejects_bad_index(self):
        with self.assertRaises(ValueError):
            extract_bit_plane(detailed(), bit=9)

    def test_channel_grid_is_three_panels_wide(self):
        image = detailed()
        grid = channel_grid(image, 'rgb')
        self.assertEqual(grid.shape[0], image.shape[0])
        self.assertEqual(grid.shape[1], image.shape[1] * 3)


class TestRedaction(unittest.TestCase):

    def setUp(self):
        self.image = detailed()
        self.region = (20, 20, 60, 40)

    def test_fill_destroys_the_content(self):
        result = redact(self.image, [self.region], method='fill')
        patch = result[20:60, 20:80]
        self.assertEqual(int(patch.max()), 0)

    def test_fill_leaves_the_rest_untouched(self):
        result = redact(self.image, [self.region], method='fill')
        np.testing.assert_array_equal(result[80:, :], self.image[80:, :])

    def test_every_method_changes_the_region(self):
        for method in ('fill', 'noise', 'blur', 'pixelate'):
            with self.subTest(method=method):
                result = redact(self.image, [self.region], method=method, seed=1)
                self.assertFalse(np.array_equal(result[20:60, 20:80],
                                                self.image[20:60, 20:80]))

    def test_multiple_regions(self):
        result = redact(self.image, [(10, 10, 20, 20), (100, 60, 30, 30)])
        self.assertEqual(int(result[10:30, 10:30].max()), 0)
        self.assertEqual(int(result[60:90, 100:130].max()), 0)

    def test_regions_are_clipped_to_the_image(self):
        result = redact(self.image, [(140, 100, 200, 200)])
        self.assertEqual(result.shape, self.image.shape)

    def test_region_entirely_outside_raises(self):
        with self.assertRaises(ValueError):
            redact(self.image, [(500, 500, 10, 10)])

    def test_malformed_region_raises(self):
        with self.assertRaises(ValueError):
            redact(self.image, [(10, 10, 20)])

    def test_zero_size_region_raises(self):
        with self.assertRaises(ValueError):
            redact(self.image, [(10, 10, 0, 20)])

    def test_unknown_method_raises(self):
        with self.assertRaises(ValueError):
            redact(self.image, [self.region], method='scribble')

    def test_noise_is_reproducible_with_a_seed(self):
        first = redact(self.image, [self.region], method='noise', seed=7)
        second = redact(self.image, [self.region], method='noise', seed=7)
        np.testing.assert_array_equal(first, second)

    def test_reversibility_classification(self):
        self.assertFalse(is_reversible('fill'))
        self.assertFalse(is_reversible('noise'))
        self.assertTrue(is_reversible('blur'))
        self.assertTrue(is_reversible('pixelate'))

    def test_is_reversible_rejects_unknown(self):
        with self.assertRaises(ValueError):
            is_reversible('scribble')

    def test_verify_passes_destructive_methods(self):
        for method in ('fill', 'noise'):
            with self.subTest(method=method):
                result = redact(self.image, [self.region], method=method, seed=2)
                report = verify_redaction(self.image, result, [self.region])
                self.assertTrue(report['safe'])

    def test_verify_flags_blur_as_recoverable(self):
        # Blur preserves structure, which is exactly why it is unsafe
        blurred = redact(self.image, [self.region], method='blur', blur_radius=6)
        report = verify_redaction(self.image, blurred, [self.region])
        self.assertFalse(report['safe'])
        self.assertGreater(report['max_correlation'], 0.2)

    def test_verify_rejects_mismatched_images(self):
        with self.assertRaises(ValueError):
            verify_redaction(self.image, detailed(64, 64), [self.region])

    def test_redact_region_chain_form(self):
        result = redact_region(self.image, 20, 20, 60, 40, method='fill')
        self.assertEqual(int(result[20:60, 20:80].max()), 0)


class TestRedactionReproducibility(unittest.TestCase):
    """A chain that cannot replay identically cannot back a report."""

    def test_noise_redaction_is_reproducible_when_seeded(self):
        image = textured(96, 128) if 'textured' in globals() else np.full(
            (96, 128, 3), 128, np.uint8)
        first = redact_region(image, 10, 10, 60, 40, method='noise', seed=7)
        again = redact_region(image, 10, 10, 60, 40, method='noise', seed=7)
        np.testing.assert_array_equal(first, again)

    def test_noise_redaction_varies_without_a_seed(self):
        # The default has to stay random: a fixed default would make every
        # redaction in the world identical, which is worse
        image = np.full((96, 128, 3), 128, np.uint8)
        first = redact_region(image, 10, 10, 60, 40, method='noise')
        again = redact_region(image, 10, 10, 60, 40, method='noise')
        self.assertFalse(np.array_equal(first, again))

    def test_a_seeded_redaction_still_destroys_the_region(self):
        image = np.tile(np.arange(128, dtype=np.uint8), (96, 1))
        image = np.stack([image] * 3, axis=2)
        redacted = redact_region(image, 10, 10, 60, 40, method='noise', seed=7)
        report = verify_redaction(image, redacted, [(10, 10, 60, 40)])
        self.assertTrue(report['safe'])


class TestAnnotate(unittest.TestCase):

    def setUp(self):
        self.image = detailed()

    def test_arrow_marks_the_image(self):
        result = draw_arrow(self.image, (10, 10), (100, 80), label='here')
        self.assertEqual(result.shape[:2], self.image.shape[:2])
        self.assertFalse(np.array_equal(result, self.image))

    def test_arrow_rejects_zero_thickness(self):
        with self.assertRaises(ValueError):
            draw_arrow(self.image, (0, 0), (10, 10), thickness=0)

    def test_text_is_drawn(self):
        result = draw_text(self.image, 'exhibit A', (10, 30))
        self.assertFalse(np.array_equal(result, self.image))

    def test_empty_text_raises(self):
        with self.assertRaises(ValueError):
            draw_text(self.image, '', (10, 30))

    def test_grayscale_input_becomes_colour(self):
        gray = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)
        result = draw_text(gray, 'x', (10, 30))
        self.assertEqual(result.ndim, 3)
        self.assertEqual(result.shape[2], 3)

    def test_every_shape_draws(self):
        cases = {
            'rectangle': [(10, 10), (60, 50)],
            'line': [(10, 10), (60, 50)],
            'circle': [(50, 50), (70, 50)],
            'ellipse': [(50, 50), (80, 70)],
            'polygon': [(10, 10), (60, 20), (40, 60)],
        }
        for shape, points in cases.items():
            with self.subTest(shape=shape):
                result = draw_shape(self.image, shape, points)
                self.assertFalse(np.array_equal(result, self.image))

    def test_shape_wrong_point_count_raises(self):
        with self.assertRaises(ValueError):
            draw_shape(self.image, 'rectangle', [(10, 10)])

    def test_polygon_needs_three_points(self):
        with self.assertRaises(ValueError):
            draw_shape(self.image, 'polygon', [(10, 10), (20, 20)])

    def test_unknown_shape_raises(self):
        with self.assertRaises(ValueError):
            draw_shape(self.image, 'blob', [(10, 10), (20, 20)])

    def test_scale_converts_pixels_to_units(self):
        scale = Scale(pixels=240, units=520, unit_name='mm')
        self.assertAlmostEqual(scale.convert(240), 520.0)
        self.assertAlmostEqual(scale.convert(120), 260.0)

    def test_scale_rejects_non_positive_values(self):
        with self.assertRaises(ValueError):
            Scale(pixels=0, units=100)
        with self.assertRaises(ValueError):
            Scale(pixels=100, units=0)

    def test_scale_from_reference(self):
        scale = scale_from_reference((100, 200), (340, 200), 520, 'mm')
        self.assertAlmostEqual(scale.pixels, 240.0)
        self.assertAlmostEqual(scale.convert(240), 520.0)

    def test_scale_from_identical_points_raises(self):
        with self.assertRaises(ValueError):
            scale_from_reference((10, 10), (10, 10), 100)

    def test_measure_distance_in_pixels(self):
        result = measure_distance((0, 0), (30, 40))
        self.assertAlmostEqual(result['pixel_distance'], 50.0)
        self.assertNotIn('distance', result)

    def test_measure_distance_with_scale(self):
        scale = Scale(pixels=240, units=520, unit_name='mm')
        result = measure_distance((100, 200), (340, 200), scale)
        self.assertAlmostEqual(result['distance'], 520.0)
        self.assertEqual(result['unit'], 'mm')

    def test_measure_distance_reports_angle(self):
        # Screen y runs downwards, so this is 45 degrees above horizontal
        result = measure_distance((0, 100), (100, 0))
        self.assertAlmostEqual(result['angle_degrees'], 45.0, places=4)

    def test_measure_area_of_a_rectangle(self):
        result = measure_area([(0, 0), (100, 0), (100, 50), (0, 50)])
        self.assertAlmostEqual(result['pixel_area'], 5000.0)
        self.assertAlmostEqual(result['pixel_perimeter'], 300.0)

    def test_measure_area_ignores_winding_direction(self):
        clockwise = measure_area([(0, 0), (100, 0), (100, 50), (0, 50)])
        anticlockwise = measure_area([(0, 50), (100, 50), (100, 0), (0, 0)])
        self.assertAlmostEqual(clockwise['pixel_area'], anticlockwise['pixel_area'])

    def test_measure_area_scales_by_the_square(self):
        scale = Scale(pixels=10, units=20, unit_name='mm')   # 2 mm per pixel
        result = measure_area([(0, 0), (10, 0), (10, 10), (0, 10)], scale)
        self.assertAlmostEqual(result['area'], 400.0)        # 100 px^2 * 4
        self.assertEqual(result['area_unit'], 'mm^2')

    def test_measure_area_needs_three_points(self):
        with self.assertRaises(ValueError):
            measure_area([(0, 0), (10, 10)])

    def test_draw_measurement_labels_in_units(self):
        scale = Scale(pixels=100, units=250, unit_name='mm')
        result = draw_measurement(self.image, (20, 60), (120, 60), scale)
        self.assertEqual(result.shape[:2], self.image.shape[:2])
        self.assertFalse(np.array_equal(result, self.image))

    def test_draw_measurement_without_scale(self):
        result = draw_measurement(self.image, (20, 60), (120, 60))
        self.assertFalse(np.array_equal(result, self.image))

    def test_scale_bar_draws(self):
        scale = Scale(pixels=100, units=250, unit_name='mm')
        result = draw_scale_bar(self.image, scale, length_units=100)
        self.assertEqual(result.shape[:2], self.image.shape[:2])

    def test_scale_bar_rejects_a_bar_wider_than_the_image(self):
        scale = Scale(pixels=100, units=10, unit_name='mm')
        with self.assertRaises(ValueError):
            draw_scale_bar(self.image, scale, length_units=1000)

    def test_scale_bar_rejects_bad_position(self):
        scale = Scale(pixels=100, units=250, unit_name='mm')
        with self.assertRaises(ValueError):
            draw_scale_bar(self.image, scale, position='middle')

    def test_annotations_do_not_modify_the_original(self):
        before = self.image.copy()
        draw_arrow(self.image, (10, 10), (50, 50))
        draw_text(self.image, 'x', (10, 10))
        draw_shape(self.image, 'rectangle', [(5, 5), (40, 40)])
        np.testing.assert_array_equal(self.image, before)

    # ---- Flat coordinate lists ----
    # A form field and a command line both hand over "x1,y1,x2,y2" as a run of
    # numbers, so the same points arrive in two shapes and must mean one thing.

    def test_flat_coordinates_match_pairs_for_a_shape(self):
        flat = draw_shape(self.image, 'rectangle', [10, 10, 60, 50])
        pairs = draw_shape(self.image, 'rectangle', [(10, 10), (60, 50)])
        np.testing.assert_array_equal(flat, pairs)

    def test_flat_coordinates_match_pairs_for_an_area(self):
        flat = measure_area([0, 0, 100, 0, 100, 50, 0, 50])
        pairs = measure_area([(0, 0), (100, 0), (100, 50), (0, 50)])
        self.assertAlmostEqual(flat['pixel_area'], pairs['pixel_area'])
        self.assertAlmostEqual(flat['pixel_area'], 5000.0)

    def test_odd_flat_coordinate_count_raises(self):
        with self.assertRaises(ValueError):
            measure_area([0, 0, 100, 0, 100])

    def test_a_non_pair_point_raises(self):
        with self.assertRaises(ValueError):
            draw_shape(self.image, 'polygon', [(1, 2), (3, 4, 5), (6, 7)])

    # ---- Area measurement drawing ----

    def test_draw_area_measurement_labels_in_square_units(self):
        # 10 px reference called 20 mm -> 2 mm/px, so 100 px^2 is 400 mm^2
        scale = Scale(pixels=10, units=20, unit_name='mm')
        result = draw_area_measurement(
            self.image, [(10, 10), (20, 10), (20, 20), (10, 20)], scale)
        self.assertEqual(result.shape[:2], self.image.shape[:2])
        self.assertFalse(np.array_equal(result, self.image))

    def test_draw_area_measurement_without_scale(self):
        result = draw_area_measurement(
            self.image, [(10, 10), (60, 10), (60, 40)])
        self.assertFalse(np.array_equal(result, self.image))

    def test_draw_area_measurement_needs_three_points(self):
        with self.assertRaises(ValueError):
            draw_area_measurement(self.image, [(10, 10), (60, 10)])

    def test_draw_area_measurement_does_not_modify_the_original(self):
        before = self.image.copy()
        draw_area_measurement(self.image, [(10, 10), (60, 10), (60, 40)])
        np.testing.assert_array_equal(self.image, before)


class MeasurementAdapterTests(unittest.TestCase):
    """
    The registry's flat-parameter wrappers around annotate.

    A Scale cannot travel through JSON, so these take the two ends of a
    reference of known length instead. The arithmetic is the point: a 100 px
    reference called 520 mm makes 150 px read 780 mm, and these check that
    rather than only that an image came back.
    """

    def setUp(self):
        self.image = detailed(200, 300)

    def test_calibration_from_a_reference_span(self):
        from cv_tools.filters.registry import _calibration

        scale = _calibration([100, 200], [200, 200], 520.0, 'mm')
        self.assertAlmostEqual(scale.pixels, 100.0)
        self.assertAlmostEqual(scale.convert(150), 780.0)
        self.assertEqual(scale.unit_name, 'mm')

    def test_no_reference_means_no_calibration(self):
        from cv_tools.filters.registry import _calibration

        self.assertIsNone(_calibration(None, None, None, 'mm'))

    def test_half_a_calibration_raises(self):
        from cv_tools.filters.registry import _calibration

        with self.assertRaises(ValueError):
            _calibration([0, 0], [10, 0], None, 'mm')
        with self.assertRaises(ValueError):
            _calibration([0, 0], None, 520.0, 'mm')

    def test_measure_matches_the_underlying_dimension_line(self):
        from cv_tools.filters.registry import measure

        adapted = measure(self.image, [20, 60], [120, 60],
                          reference_a=[20, 30], reference_b=[70, 30],
                          reference_length=260.0)
        direct = draw_measurement(self.image, [20, 60], [120, 60],
                                  Scale(pixels=50, units=260, unit_name='mm'))
        np.testing.assert_array_equal(adapted, direct)

    def test_measure_without_a_reference_falls_back_to_pixels(self):
        from cv_tools.filters.registry import measure

        adapted = measure(self.image, [20, 60], [120, 60])
        direct = draw_measurement(self.image, [20, 60], [120, 60])
        np.testing.assert_array_equal(adapted, direct)

    def test_measure_area_adapter_accepts_flat_coordinates(self):
        from cv_tools.filters.registry import measure_area_annotated

        flat = measure_area_annotated(self.image, [10, 10, 90, 10, 90, 60, 10, 60])
        pairs = measure_area_annotated(
            self.image, [[10, 10], [90, 10], [90, 60], [10, 60]])
        np.testing.assert_array_equal(flat, pairs)

    def test_scale_bar_adapter_matches_a_hand_built_scale(self):
        from cv_tools.filters.registry import scale_bar

        adapted = scale_bar(self.image, [20, 30], [120, 30], 520.0,
                            length_units=260.0)
        direct = draw_scale_bar(self.image,
                                Scale(pixels=100, units=520, unit_name='mm'),
                                length_units=260.0)
        np.testing.assert_array_equal(adapted, direct)

    def test_registered_under_the_expected_names(self):
        from cv_tools.filters.registry import FILTER_REGISTRY

        for name in ('measure', 'measure_area', 'scale_bar', 'arrow', 'text',
                     'shape'):
            with self.subTest(name=name):
                self.assertIn(name, FILTER_REGISTRY)
                self.assertEqual(FILTER_REGISTRY[name].category, 'Special')

    def test_every_measurement_filter_has_a_click_plan(self):
        from cv_tools.filters.registry import POINT_PARAMETERS

        for name in ('measure', 'measure_area', 'scale_bar', 'arrow', 'text',
                     'shape'):
            with self.subTest(name=name):
                self.assertIn(name, POINT_PARAMETERS)

    def test_click_plans_name_real_parameters(self):
        """A plan that names a parameter the filter lacks fills nothing."""
        import inspect

        from cv_tools.filters.registry import FILTER_REGISTRY, POINT_PARAMETERS

        for name, plan in POINT_PARAMETERS.items():
            spec = FILTER_REGISTRY[name]
            accepted = set(inspect.signature(spec.fn).parameters)
            for parameter, _count, _prompt in plan:
                with self.subTest(filter=name, parameter=parameter):
                    self.assertIn(parameter, accepted)


if __name__ == '__main__':
    unittest.main()
