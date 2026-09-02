"""
Unit tests for frame alignment.

Ground truth is available here: the frames are made by warping one image by a
known transform, so these assert that the motion was actually recovered and
that combining the aligned stack beats combining the raw one. A test that only
checked an image came back would pass on an alignment that did nothing, which
is precisely the failure this module exists to prevent.
"""

import unittest

import cv2
import numpy as np

from cv_tools.filters import (
    MOTION_MODELS,
    STABILISE_METHODS,
    align_frames,
    alignment_report,
    average_frames,
    common_valid_region,
    estimate_alignment,
    warp_frame,
)
from cv_tools.filters.stabilise import _largest_rectangle


def textured(height: int = 180, width: int = 240) -> np.ndarray:
    """Broadband detail plus hard shapes, so both ECC and ORB have something."""
    rng = np.random.default_rng(7)
    noise = cv2.GaussianBlur(
        rng.integers(0, 255, (height, width), dtype=np.uint8), (5, 5), 2)
    image = cv2.cvtColor(noise, cv2.COLOR_GRAY2RGB)
    cv2.rectangle(image, (40, 40), (120, 100), (255, 80, 40), -1)
    cv2.circle(image, (180, 130), 25, (40, 220, 120), -1)
    cv2.putText(image, 'AB 123', (25, 165), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (250, 250, 250), 2, cv2.LINE_AA)
    return image


def moved(image: np.ndarray, dx: float, dy: float, degrees: float = 0.0) -> np.ndarray:
    """The image shifted and rotated about its centre."""
    height, width = image.shape[:2]
    matrix = cv2.getRotationMatrix2D((width / 2, height / 2), degrees, 1.0)
    matrix[0, 2] += dx
    matrix[1, 2] += dy
    return cv2.warpAffine(image, matrix, (width, height),
                          borderMode=cv2.BORDER_REFLECT)


def noisy(image: np.ndarray, sigma: float, rng) -> np.ndarray:
    return np.clip(image.astype(np.float32) + rng.normal(0, sigma, image.shape),
                   0, 255).astype(np.uint8)


def psnr(a: np.ndarray, b: np.ndarray) -> float:
    error = np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2)
    return 99.0 if error == 0 else float(10 * np.log10(255 * 255 / error))


class LargestRectangleTests(unittest.TestCase):
    """
    The crop that follows an alignment.

    This started as a whole-row / whole-column scan, which finds nothing once
    the valid region is tilted - and a rotated frame's region always is.
    """

    def test_finds_a_plain_rectangle(self):
        mask = np.zeros((10, 10), dtype=bool)
        mask[2:8, 3:9] = True
        self.assertEqual(_largest_rectangle(mask), (3, 2, 6, 6))

    def test_a_full_mask_is_the_whole_frame(self):
        self.assertEqual(_largest_rectangle(np.ones((10, 12), dtype=bool)),
                         (0, 0, 12, 10))

    def test_an_empty_mask_has_no_region(self):
        x, y, width, height = _largest_rectangle(np.zeros((5, 5), dtype=bool))
        self.assertEqual((width, height), (0, 0))

    def test_a_rotated_region_still_yields_a_rectangle(self):
        ones = np.ones((120, 160), dtype=np.uint8)
        matrix = cv2.getRotationMatrix2D((80, 60), 5.0, 1.0)
        rotated = cv2.warpAffine(ones, matrix, (160, 120), flags=cv2.INTER_NEAREST)

        x, y, width, height = common_valid_region([rotated])
        self.assertGreater(width * height, 0)
        # Every pixel of the reported region must really be covered
        self.assertTrue(rotated[y:y + height, x:x + width].all())

    def test_frames_with_nothing_in_common_are_refused(self):
        with self.assertRaises(ValueError):
            common_valid_region([np.zeros((8, 8), dtype=np.uint8)])


class EstimateAlignmentTests(unittest.TestCase):

    def setUp(self):
        self.image = textured()

    def test_pure_translation_is_recovered_to_a_fraction_of_a_pixel(self):
        for dx, dy in [(7, -4), (-11, 6), (3, 9)]:
            with self.subTest(dx=dx, dy=dy):
                result = estimate_alignment(moved(self.image, dx, dy),
                                            self.image, model='translation')
                self.assertTrue(result.converged)
                self.assertAlmostEqual(result.shift[0], dx, delta=0.5)
                self.assertAlmostEqual(result.shift[1], dy, delta=0.5)

    def test_a_still_frame_measures_as_no_motion(self):
        result = estimate_alignment(self.image, self.image, model='euclidean')
        self.assertTrue(result.converged)
        self.assertLess(float(np.hypot(*result.shift)), 0.5)
        self.assertGreater(result.confidence, 0.9)

    def test_warping_back_undoes_the_motion(self):
        """The measure that matters: does the aligned frame match the reference."""
        for dx, dy, degrees, model in [
            (7, -4, 0.0, 'translation'),
            (6, 3, 4.0, 'euclidean'),
            (-9, 7, -3.0, 'euclidean'),
            (5, 5, 2.0, 'affine'),
        ]:
            with self.subTest(model=model, degrees=degrees):
                shifted = moved(self.image, dx, dy, degrees)
                result = estimate_alignment(shifted, self.image, model=model)
                restored, mask = warp_frame(shifted, result.matrix, model)

                covered = mask.astype(bool)
                before = np.abs(shifted[covered].astype(float)
                                - self.image[covered].astype(float)).mean()
                after = np.abs(restored[covered].astype(float)
                               - self.image[covered].astype(float)).mean()
                self.assertLess(after, before / 4,
                                f'{model}: error {before:.1f} -> {after:.1f}')

    def test_every_method_recovers_a_known_shift(self):
        shifted = moved(self.image, 8, -5)
        for method in STABILISE_METHODS:
            with self.subTest(method=method):
                result = estimate_alignment(shifted, self.image,
                                            model='translation', method=method)
                self.assertTrue(result.converged)
                self.assertAlmostEqual(result.shift[0], 8, delta=1.0)
                self.assertAlmostEqual(result.shift[1], -5, delta=1.0)

    def test_every_motion_model_runs(self):
        shifted = moved(self.image, 5, 4, 2.0)
        for model in MOTION_MODELS:
            with self.subTest(model=model):
                result = estimate_alignment(shifted, self.image, model=model)
                self.assertTrue(result.converged)
                self.assertEqual(result.model, model)

    def test_featureless_frames_do_not_pretend_to_align(self):
        """A flat field has nothing to match; saying so beats inventing a warp."""
        blank = np.full((120, 160, 3), 128, dtype=np.uint8)
        other = np.full((120, 160, 3), 128, dtype=np.uint8)
        result = estimate_alignment(other, blank, model='euclidean',
                                    method='features')
        self.assertFalse(result.converged)
        self.assertEqual(result.confidence, 0.0)
        self.assertTrue(result.note)

    def test_unknown_model_and_method_are_rejected(self):
        with self.assertRaises(ValueError):
            estimate_alignment(self.image, self.image, model='wobble')
        with self.assertRaises(ValueError):
            estimate_alignment(self.image, self.image, method='vibes')

    def test_the_record_is_json_serializable(self):
        import json

        result = estimate_alignment(moved(self.image, 4, 4), self.image)
        json.dumps(result.to_dict())        # must not raise


class AlignFramesTests(unittest.TestCase):

    def setUp(self):
        self.clean = textured()
        rng = np.random.default_rng(11)
        self.rng = rng
        self.frames = []
        for index in range(10):
            dx = 5 * np.sin(index * 0.6) + rng.normal(0, 1.0)
            dy = 3 * np.cos(index * 0.5) + rng.normal(0, 1.0)
            degrees = 1.2 * np.sin(index * 0.4)
            self.frames.append(
                noisy(moved(self.clean, dx, dy, degrees), 16, rng))

    def test_aligning_before_averaging_beats_averaging_alone(self):
        """
        The whole point of the module, as a number.

        A shaky sequence averaged raw is blurred by its own motion. Both
        results are compared against the same region of the clean original,
        located by matching the cropped output back into it.
        """
        naive = average_frames(self.frames)
        aligned, _ = align_frames(self.frames, model='euclidean')
        stabilised = average_frames(aligned)

        match = cv2.matchTemplate(self.clean, stabilised, cv2.TM_SQDIFF)
        _, _, (x, y), _ = cv2.minMaxLoc(match)
        height, width = stabilised.shape[:2]
        truth = self.clean[y:y + height, x:x + width]

        naive_score = psnr(naive[y:y + height, x:x + width], truth)
        stabilised_score = psnr(stabilised, truth)
        self.assertGreater(stabilised_score, naive_score + 2.0,
                           f'aligned {stabilised_score:.2f} dB vs raw '
                           f'{naive_score:.2f} dB')

    def test_the_reference_frame_is_returned_untouched(self):
        aligned, results = align_frames(self.frames, reference=0, crop=False)
        np.testing.assert_array_equal(aligned[0], self.frames[0])
        self.assertEqual(results[0].method, 'reference')
        self.assertEqual(results[0].shift, (0.0, 0.0))

    def test_cropping_trims_to_the_common_region(self):
        cropped, _ = align_frames(self.frames, crop=True)
        whole, _ = align_frames(self.frames, crop=False)
        self.assertLess(cropped[0].shape[0], whole[0].shape[0])
        self.assertLess(cropped[0].shape[1], whole[0].shape[1])
        # Every returned frame must share a size, or nothing can combine them
        self.assertEqual({frame.shape for frame in cropped}, {cropped[0].shape})

    def test_uncroppable_output_still_shares_one_size(self):
        whole, _ = align_frames(self.frames, crop=False)
        self.assertEqual({frame.shape for frame in whole}, {whole[0].shape})

    def test_a_frame_that_cannot_be_matched_is_left_out(self):
        frames = list(self.frames)
        frames[4] = np.full_like(frames[4], 128)     # nothing to match
        aligned, results = align_frames(frames, model='euclidean',
                                        method='features')

        self.assertLess(len(aligned), len(frames))
        dropped = [r for r in results if not r.converged]
        self.assertTrue(dropped)
        self.assertIn(4, [r.index for r in dropped])

    def test_a_report_describes_what_happened(self):
        _, results = align_frames(self.frames, model='euclidean')
        report = alignment_report(results)

        self.assertEqual(report['frames'], len(self.frames))
        self.assertEqual(report['model'], 'euclidean')
        self.assertEqual(len(report['per_frame']), len(self.frames))
        self.assertGreater(report['max_shift_pixels'], 0)
        self.assertLessEqual(report['aligned'], report['frames'])

    def test_frames_of_different_sizes_are_refused(self):
        frames = list(self.frames)
        frames[2] = cv2.resize(frames[2], (100, 80))
        with self.assertRaises(ValueError):
            align_frames(frames)

    def test_a_reference_outside_the_sequence_is_refused(self):
        with self.assertRaises(ValueError):
            align_frames(self.frames, reference=99)

    def test_no_frames_is_refused(self):
        with self.assertRaises(ValueError):
            align_frames([])

    def test_nothing_alignable_is_an_error_rather_than_one_frame(self):
        """Returning the reference alone would look like a combination."""
        flat = [np.full((100, 120, 3), 128, dtype=np.uint8) for _ in range(4)]
        for index, frame in enumerate(flat[1:], start=1):
            frame[:] = index * 20        # uniform, so features find nothing
        with self.assertRaises(ValueError):
            align_frames(flat, method='features')


if __name__ == '__main__':
    unittest.main()
