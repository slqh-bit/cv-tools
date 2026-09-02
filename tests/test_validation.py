"""
Unit tests for the validation harness.

These assert the degradation model behaves like the physics it claims to model
- shot noise scaling with signal, IR night going monochrome and vignetted,
transform quantisation producing 8x8 structure - because a degradation that is
merely "some noise" would make every filter look better than it is, and the
benchmark built on it would be worse than no benchmark at all.
"""

import unittest
from unittest import mock

import cv2
import numpy as np

from cv_tools.validation import (
    PRESETS, anamorphic, block_compression, codec_generations, compare,
    degrade, degrade_preset, evaluate, interlace, ir_night, low_light,
    motion_blur, resolution_loss, run_matrix, sensor_noise, sharpness,
    to_markdown,
)


def ramp(height: int = 64, width: int = 96) -> np.ndarray:
    """A left-to-right brightness ramp, so signal-dependent effects are visible."""
    row = np.linspace(0, 255, width, dtype=np.float32)
    plane = np.repeat(row[None, :], height, axis=0)
    return np.repeat(plane[:, :, None], 3, axis=2).astype(np.uint8)


def textured(height: int = 64, width: int = 96, seed: int = 1) -> np.ndarray:
    """Mid-grey with structure, so blurring and sharpening have something to act on."""
    rng = np.random.default_rng(seed)
    base = np.full((height, width, 3), 128, dtype=np.float32)
    base += rng.normal(0, 30, size=base.shape)
    cv2.rectangle(base, (10, 10), (40, 40), (220, 220, 220), -1)
    cv2.circle(base, (70, 40), 12, (30, 30, 30), -1)
    return np.clip(base, 0, 255).astype(np.uint8)


class TestSensorNoise(unittest.TestCase):

    def test_is_reproducible_with_a_seed(self):
        image = textured()
        np.testing.assert_array_equal(sensor_noise(image, seed=3),
                                      sensor_noise(image, seed=3))

    def test_different_seeds_give_different_noise(self):
        image = textured()
        self.assertFalse(np.array_equal(sensor_noise(image, seed=3),
                                        sensor_noise(image, seed=4)))

    def test_noise_scales_with_signal(self):
        # The point of the Poisson model: shot noise grows with the square root
        # of the signal, so bright areas carry more absolute noise than dark
        # ones. A flat Gaussian field would show the same spread in both.
        image = ramp(height=200, width=200)
        noisy = sensor_noise(image, photon_scale=20.0, read_sigma=0.0, seed=5)
        residual = noisy.astype(float) - image.astype(float)
        dark = residual[:, :40].std()
        bright = residual[:, -40:].std()
        self.assertGreater(bright, dark * 1.5,
                           f'noise did not scale with signal (dark {dark:.2f}, '
                           f'bright {bright:.2f})')

    def test_lower_photon_scale_is_noisier(self):
        image = textured()
        noisy_high = sensor_noise(image, photon_scale=400.0, read_sigma=0.0, seed=5)
        noisy_low = sensor_noise(image, photon_scale=20.0, read_sigma=0.0, seed=5)
        self.assertGreater(
            np.abs(noisy_low.astype(float) - image).mean(),
            np.abs(noisy_high.astype(float) - image).mean())

    def test_output_is_uint8_and_same_shape(self):
        image = textured()
        out = sensor_noise(image, seed=1)
        self.assertEqual(out.dtype, np.uint8)
        self.assertEqual(out.shape, image.shape)


class TestLowLight(unittest.TestCase):

    def test_darkens_the_image(self):
        image = textured()
        self.assertLess(low_light(image, exposure=0.25, seed=2).mean(), image.mean())

    def test_noise_is_generated_after_the_light_is_lost(self):
        # Darkening an already-noisy frame scales its noise down with it and
        # produces something far cleaner than any real night frame. Relative to
        # the signal present, this must be noisier than that.
        image = textured()
        # black_level off, or its constant offset dominates the comparison and
        # the assertion passes whichever order the noise was applied in.
        correct = low_light(image, exposure=0.2, black_level=0, seed=2).astype(float)
        naive = sensor_noise(image, seed=2).astype(float) * 0.2
        signal = image.astype(float) * 0.2
        self.assertGreater(np.abs(correct - signal).mean(),
                           np.abs(naive - signal).mean() * 1.5)

    def test_black_level_lifts_the_floor(self):
        image = np.zeros((32, 32, 3), dtype=np.uint8)
        lifted = low_light(image, exposure=0.5, black_level=10,
                           photon_scale=1e6, read_sigma=0.0, seed=1)
        self.assertGreaterEqual(int(lifted.min()), 9)


class TestIrNight(unittest.TestCase):

    def test_output_is_monochrome(self):
        out = ir_night(textured(), seed=1)
        np.testing.assert_array_equal(out[:, :, 0], out[:, :, 1])
        np.testing.assert_array_equal(out[:, :, 1], out[:, :, 2])

    def test_illumination_falls_off_toward_the_corners(self):
        # The camera lights the scene itself, so the vignette is part of the
        # lighting rather than a lens artefact.
        flat = np.full((120, 120, 3), 200, dtype=np.uint8)
        out = ir_night(flat, falloff=0.3, photon_scale=1e6, read_sigma=0.0, seed=1)
        centre = out[50:70, 50:70].mean()
        corner = out[:15, :15].mean()
        self.assertGreater(centre, corner * 1.2)

    def test_keeps_three_channels(self):
        self.assertEqual(ir_night(textured(), seed=1).shape[2], 3)

    def test_brightness_follows_luma_not_a_single_channel(self):
        # An IR sensor responds to overall brightness. Taking one colour channel
        # would still produce a monochrome frame, so the monochrome test alone
        # does not catch it - but it would rank a blue scene far too bright.
        blue = np.zeros((60, 60, 3), dtype=np.uint8)
        blue[:, :, 0] = 255                     # BGR: pure blue
        out = ir_night(blue, exposure=1.0, falloff=1.0,
                       photon_scale=1e6, read_sigma=0.0, seed=1)
        # Rec.601 luma of pure blue is about 29, nowhere near 255.
        self.assertLess(int(out[30, 30, 0]), 80)


class TestBlockCompression(unittest.TestCase):

    def test_zero_severity_is_a_no_op(self):
        image = textured()
        np.testing.assert_array_equal(block_compression(image, 0.0), image)

    def test_more_severity_costs_more_fidelity(self):
        image = textured()
        mild = compare(image, block_compression(image, 1.0))['psnr']
        harsh = compare(image, block_compression(image, 8.0))['psnr']
        self.assertGreater(mild, harsh)

    def test_shape_and_dtype_are_preserved(self):
        # Deliberately not a multiple of 8, so the padding path runs.
        image = textured(height=53, width=71)
        out = block_compression(image, 4.0)
        self.assertEqual(out.shape, image.shape)
        self.assertEqual(out.dtype, np.uint8)

    def test_edge_blocks_are_quantised_too(self):
        # Padding to whole blocks then trimming means the partial block at the
        # edge is degraded like any other; leaving it untouched would make a
        # crop of the edge look better than the middle.
        image = textured(height=53, width=71)
        out = block_compression(image, 8.0)
        edge_changed = np.abs(out[-5:, -5:].astype(int)
                              - image[-5:, -5:].astype(int)).mean()
        self.assertGreater(edge_changed, 0.0)

    def test_grayscale_input_stays_grayscale(self):
        grey = cv2.cvtColor(textured(), cv2.COLOR_BGR2GRAY)
        self.assertEqual(block_compression(grey, 4.0).shape, grey.shape)

    def test_high_frequencies_are_quantised_harder_than_low(self):
        # This is the shape of the JPEG table and of every real transform
        # codec: coarser toward high frequencies. A flat table would damage a
        # smooth gradient as much as fine detail, which is not what blocking
        # looks like.
        height = width = 64
        xs = np.arange(width, dtype=np.float32)
        smooth = np.repeat((xs / width * 255)[None, :], height, axis=0)
        fine = 128 + 100 * np.sin(xs * np.pi / 2.0)      # alternating pixels
        fine = np.repeat(fine[None, :], height, axis=0)

        def loss(plane):
            image = np.repeat(np.clip(plane, 0, 255).astype(np.uint8)[:, :, None], 3, axis=2)
            return np.abs(block_compression(image, 6.0).astype(float)
                          - image.astype(float)).mean()

        self.assertGreater(loss(fine), loss(smooth) * 2,
                           'high frequencies were not quantised harder')


class TestCodecGenerations(unittest.TestCase):

    def test_zero_generations_is_a_no_op(self):
        image = textured()
        np.testing.assert_array_equal(codec_generations(image, 0), image)

    def test_a_pass_reports_the_codec_it_used(self):
        codec_generations(textured(), generations=1)
        self.assertIn(codec_generations.last_codec,
                      {'avc1', 'mp4v', 'XVID', 'MJPG'})

    def test_encoding_costs_fidelity(self):
        image = textured()
        self.assertLess(compare(image, codec_generations(image, 1))['psnr'], 60.0)

    def test_odd_dimensions_are_cropped_not_padded(self):
        # Encoders reject odd sizes. Padding would put invented pixels into a
        # measurement; cropping only loses a row.
        image = textured(height=51, width=71)
        out = codec_generations(image, 1)
        self.assertEqual(out.shape[0] % 2, 0)
        self.assertEqual(out.shape[1] % 2, 0)
        # Padding would also give even dimensions, so evenness alone proves
        # nothing. The distinguishing property is that no pixel was invented.
        self.assertLessEqual(out.shape[0], image.shape[0])
        self.assertLessEqual(out.shape[1], image.shape[1])

    def test_reports_clearly_when_no_encoder_exists(self):
        # Patch the attribute on the cv2 module object, which degrade.py looks
        # up at call time, so this reaches the same object it will use.
        #
        # Not the dotted string 'cv_tools.validation.degrade.cv2.VideoWriter'.
        # `degrade` names both a submodule and the function the package
        # re-exports, and the function shadows it, so that path resolves
        # through a function rather than a module. Python 3.11's mock finds the
        # real module in sys.modules anyway; 3.10's falls through to importing
        # `degrade.cv2` as a submodule and raises. It passed here and failed in
        # CI for exactly that reason.
        with mock.patch.object(cv2, 'VideoWriter') as writer:
            writer.return_value.isOpened.return_value = False
            with self.assertRaises(RuntimeError) as ctx:
                codec_generations(textured(), 1)
        self.assertIn('encoder', str(ctx.exception))


class TestGeometricDegradations(unittest.TestCase):

    def test_motion_blur_of_length_one_is_a_no_op(self):
        image = textured()
        np.testing.assert_array_equal(motion_blur(image, length=1), image)

    def test_motion_blur_reduces_acutance(self):
        image = textured()
        self.assertLess(sharpness(motion_blur(image, length=9)), sharpness(image))

    def test_resolution_loss_keeps_the_frame_size(self):
        image = textured()
        self.assertEqual(resolution_loss(image, 0.5).shape, image.shape)

    def test_resolution_loss_removes_detail(self):
        image = textured()
        self.assertLess(sharpness(resolution_loss(image, 0.4)), sharpness(image))

    def test_full_factor_resolution_loss_is_a_no_op(self):
        image = textured()
        np.testing.assert_array_equal(resolution_loss(image, 1.0), image)

    def test_anamorphic_narrows_by_the_pixel_aspect(self):
        image = textured(width=100)
        out = anamorphic(image, pixel_aspect=1.25)
        self.assertEqual(out.shape[1], 80)
        self.assertEqual(out.shape[0], image.shape[0])

    def test_interlace_disturbs_only_one_field(self):
        image = textured()
        out = interlace(image, shift=4)
        np.testing.assert_array_equal(out[0::2], image[0::2])
        self.assertFalse(np.array_equal(out[1::2], image[1::2]))

    def test_zero_shift_interlace_is_a_no_op(self):
        image = textured()
        np.testing.assert_array_equal(interlace(image, shift=0), image)


class TestDegradeChain(unittest.TestCase):

    def test_applies_stages_in_order(self):
        image = textured()
        forward = degrade(image, [('motion_blur', {'length': 9}),
                                  ('resolution_loss', {'factor': 0.4})])
        reverse = degrade(image, [('resolution_loss', {'factor': 0.4}),
                                  ('motion_blur', {'length': 9})])
        self.assertFalse(np.array_equal(forward, reverse))

    def test_is_reproducible_from_one_seed(self):
        image = textured()
        chain = [('sensor_noise', {}), ('block_compression', {'severity': 2.0})]
        np.testing.assert_array_equal(degrade(image, chain, seed=11),
                                      degrade(image, chain, seed=11))

    def test_two_noise_stages_do_not_share_a_realisation(self):
        # Both stages taking the same seed would add the identical noise field
        # twice, which is a doubling rather than two independent draws.
        image = np.full((64, 64, 3), 128, dtype=np.uint8)
        chain = [('sensor_noise', {'read_sigma': 5.0}),
                 ('sensor_noise', {'read_sigma': 5.0})]
        out = degrade(image, chain, seed=2)
        first = sensor_noise(image, read_sigma=5.0, seed=2)
        doubled = sensor_noise(first, read_sigma=5.0, seed=2)
        self.assertFalse(np.array_equal(out, doubled))

    def test_an_explicit_seed_in_the_chain_wins(self):
        image = textured()
        chain = [('sensor_noise', {'seed': 99})]
        np.testing.assert_array_equal(degrade(image, chain, seed=1),
                                      degrade(image, chain, seed=50))

    def test_unknown_degradation_names_itself(self):
        with self.assertRaises(KeyError) as ctx:
            degrade(textured(), [('polish', {})])
        self.assertIn('polish', str(ctx.exception))

    def test_every_preset_runs(self):
        image = textured(height=80, width=120)
        for name in PRESETS:
            with self.subTest(preset=name):
                out = degrade_preset(image, name, seed=4)
                self.assertEqual(out.dtype, np.uint8)
                self.assertEqual(out.ndim, 3)

    def test_every_preset_actually_degrades(self):
        image = textured(height=80, width=120)
        for name in PRESETS:
            with self.subTest(preset=name):
                degraded = degrade_preset(image, name, seed=4)
                self.assertLess(compare(image, degraded)['psnr'], 45.0)

    def test_unknown_preset_lists_the_real_ones(self):
        with self.assertRaises(KeyError) as ctx:
            degrade_preset(textured(), 'midnight')
        self.assertIn('night_ir', str(ctx.exception))


class TestMetrics(unittest.TestCase):

    def test_an_identical_image_scores_perfectly(self):
        image = textured()
        metrics = compare(image, image)
        self.assertEqual(metrics['ssim'], 1.0)
        self.assertTrue(np.isinf(metrics['psnr']) or metrics['psnr'] > 90)

    def test_a_worse_image_scores_lower(self):
        image = textured()
        mild = compare(image, block_compression(image, 1.0))
        harsh = compare(image, block_compression(image, 10.0))
        self.assertGreater(mild['psnr'], harsh['psnr'])
        self.assertGreater(mild['ssim'], harsh['ssim'])

    def test_a_single_channel_result_is_still_comparable(self):
        # Every edge detector greys its output; erroring on shape would make
        # them unscoreable rather than merely inappropriate to score.
        image = textured()
        grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.assertIn('psnr', compare(image, grey))

    def test_mismatched_sizes_are_cropped_to_the_common_area(self):
        image = textured(height=64, width=96)
        self.assertIn('psnr', compare(image, image[:63, :95]))

    def test_a_tiny_image_does_not_break_ssim(self):
        tiny = textured(height=5, width=5)
        self.assertIn('ssim', compare(tiny, tiny))

    def test_sharpness_falls_with_blur(self):
        image = textured()
        self.assertLess(sharpness(cv2.GaussianBlur(image, (9, 9), 3)),
                        sharpness(image))


class TestEvaluate(unittest.TestCase):

    def test_scores_a_filter_that_helps(self):
        clean = textured()
        degraded = sensor_noise(clean, photon_scale=25.0, seed=1)
        result = evaluate(clean, degraded,
                          lambda img: cv2.medianBlur(img, 3), 'median', 'noise')
        self.assertIsNone(result.error)
        self.assertGreater(result.psnr_delta, 0)

    def test_a_filter_that_raises_is_recorded_not_propagated(self):
        # On a sweep, a filter that cannot handle the input is itself a finding
        # worth seeing beside the others rather than an aborted run.
        clean = textured()
        def broken(image):
            raise ValueError('needs a region')
        result = evaluate(clean, clean, broken, 'broken', 'noise')
        self.assertEqual(result.error, 'needs a region')
        self.assertTrue(np.isnan(result.psnr_delta))

    def test_a_filter_returning_nothing_is_an_error(self):
        clean = textured()
        result = evaluate(clean, clean, lambda image: None, 'none', 'noise')
        self.assertIn('did not return an image', result.error)

    def test_deltas_are_measured_against_the_untouched_degraded_frame(self):
        clean = textured()
        degraded = sensor_noise(clean, photon_scale=25.0, seed=1)
        result = evaluate(clean, degraded, lambda image: image, 'identity', 'noise')
        self.assertAlmostEqual(result.psnr_delta, 0.0, places=6)
        self.assertAlmostEqual(result.ssim_delta, 0.0, places=6)

    def test_result_serialises_with_its_deltas(self):
        clean = textured()
        result = evaluate(clean, clean, lambda image: image, 'identity', 'none')
        data = result.to_dict()
        for key in ('filter_name', 'degradation', 'psnr_delta', 'sharpness_ratio'):
            self.assertIn(key, data)


class TestMatrixAndReport(unittest.TestCase):

    def setUp(self):
        self.clean = textured()
        self.degradations = [('noise', sensor_noise(self.clean, seed=1)),
                             ('blocks', block_compression(self.clean, 6.0))]
        self.filters = [('median', lambda i: cv2.medianBlur(i, 3), {}),
                        ('identity', lambda i: i, {})]

    def test_scores_every_combination(self):
        results = run_matrix(self.clean, self.degradations, self.filters)
        self.assertEqual(len(results), 4)

    def test_markdown_lists_every_scored_row(self):
        table = to_markdown(run_matrix(self.clean, self.degradations, self.filters))
        for name in ('median', 'identity'):
            self.assertIn(f'`{name}`', table)

    def test_markdown_is_sorted_best_first(self):
        results = run_matrix(self.clean, self.degradations, self.filters)
        table = to_markdown(results, sort_by='psnr_delta')
        rows = [line for line in table.splitlines() if line.startswith('| `')]
        deltas = [float(row.split('|')[4]) for row in rows]
        self.assertEqual(deltas, sorted(deltas, reverse=True))

    def test_markdown_separates_filters_that_raised(self):
        def broken(image):
            raise ValueError('nope')
        results = run_matrix(self.clean, self.degradations,
                             [('broken', broken, {})])
        table = to_markdown(results)
        self.assertIn('Filters that raised', table)
        self.assertIn('nope', table)


if __name__ == '__main__':
    unittest.main()
