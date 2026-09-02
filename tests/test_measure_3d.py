"""
Unit tests for single-view height measurement.

The substantive tests project a synthetic scene through a known pinhole camera
and check that the recovered heights match what was put in. Ground truth is
available exactly here, so these assert on real numbers rather than on the
result merely being finite.
"""

import unittest

import numpy as np

from cv_tools.filters import (
    draw_height_measurement,
    horizon_from_lines,
    horizon_from_vanishing_points,
    line_through,
    measure_height,
    resolve_horizon,
    vanishing_point,
)


class SyntheticCamera:
    """A pinhole camera looking down at the plane Z=0. World: X right, Y forward, Z up."""

    def __init__(self, pitch_degrees=18.0, camera_height=2500.0, focal=900.0):
        theta = np.radians(pitch_degrees)
        self.K = np.array([[focal, 0, 640.0], [0, focal, 360.0], [0, 0, 1.0]])
        self.R = np.array([
            [1.0, 0.0, 0.0],
            [0.0, -np.sin(theta), -np.cos(theta)],
            [0.0, np.cos(theta), -np.sin(theta)],
        ])
        centre = np.array([0.0, 0.0, camera_height])
        self.P = self.K @ np.hstack([self.R, (-self.R @ centre).reshape(3, 1)])

    def project(self, point):
        homogeneous = self.P @ np.array([point[0], point[1], point[2], 1.0])
        return homogeneous[:2] / homogeneous[2]

    @property
    def horizon(self):
        return horizon_from_vanishing_points(
            self.K @ self.R @ np.array([1.0, 0.0, 0.0]),
            self.K @ self.R @ np.array([0.0, 1.0, 0.0]),
        )

    @property
    def vertical_point(self):
        return self.K @ self.R @ np.array([0.0, 0.0, 1.0])

    def pole(self, x, y, height):
        """Base and top image points of a vertical pole standing on the ground."""
        return self.project((x, y, 0.0)), self.project((x, y, height))


class TestGeometryHelpers(unittest.TestCase):

    def test_line_through_horizontal_points(self):
        line = line_through((0, 10), (100, 10))
        # Any point at y=10 must satisfy the line equation
        self.assertAlmostEqual(float(line @ np.array([50.0, 10.0, 1.0])), 0.0, places=6)

    def test_identical_points_have_no_line(self):
        with self.assertRaises(ValueError):
            line_through((5, 5), (5, 5))

    def test_vanishing_point_of_converging_lines(self):
        point = vanishing_point([(0, 0, 10, 10), (20, 0, 10, 10)])
        self.assertAlmostEqual(point[0] / point[2], 10.0, places=6)
        self.assertAlmostEqual(point[1] / point[2], 10.0, places=6)

    def test_parallel_lines_vanish_at_infinity(self):
        point = vanishing_point([(0, 0, 0, 100), (50, 0, 50, 100)])
        self.assertAlmostEqual(point[2], 0.0, places=9)

    def test_vanishing_point_needs_two_lines(self):
        with self.assertRaises(ValueError):
            vanishing_point([(0, 0, 10, 10)])

    def test_resolve_horizon_accepts_scalar_row(self):
        line = resolve_horizon(200)
        self.assertAlmostEqual(float(line @ np.array([123.0, 200.0, 1.0])), 0.0, places=6)

    def test_resolve_horizon_accepts_two_points_and_coefficients(self):
        from_points = resolve_horizon((0, 50, 100, 50))
        from_coefficients = resolve_horizon((0.0, 1.0, -50.0))
        # Same line up to scale
        self.assertAlmostEqual(
            abs(float(np.dot(from_points / np.linalg.norm(from_points),
                             from_coefficients / np.linalg.norm(from_coefficients)))),
            1.0, places=6)

    def test_resolve_horizon_rejects_missing_and_malformed(self):
        for bad in (None, (1, 2), (1, 2, 3, 4, 5)):
            with self.assertRaises(ValueError):
                resolve_horizon(bad)


class TestHorizonFromLines(unittest.TestCase):
    """Deriving the horizon from what is visible instead of from the answer."""

    def test_two_receding_lines_give_the_row_they_converge_on(self):
        # Both lines pass through (80, 30)
        line = horizon_from_lines([(0, 10, 60, 25), (0, 50, 60, 35)])
        self.assertAlmostEqual(-line[2] / line[1], 30.0, places=6)
        self.assertAlmostEqual(line[0], 0.0, places=9)

    def test_a_second_direction_handles_a_rolled_camera(self):
        # Vanishing points at (80, 30) and (-40, 70): the horizon runs through
        # both, so it is tilted rather than level
        line = horizon_from_lines([(0, 10, 60, 25), (0, 50, 60, 35)],
                                  [(0, 90, -20, 80), (0, 50, -20, 60)])
        for point in ((80.0, 30.0), (-40.0, 70.0)):
            self.assertAlmostEqual(
                float(line @ np.array([point[0], point[1], 1.0])), 0.0, places=6)
        self.assertNotAlmostEqual(line[0], 0.0, places=6)

    def test_image_parallel_lines_have_no_level_horizon(self):
        with self.assertRaises(ValueError) as ctx:
            horizon_from_lines([(0, 10, 60, 10), (0, 50, 60, 50)])
        self.assertIn('infinity', str(ctx.exception))

    def test_one_line_is_not_enough(self):
        with self.assertRaises(ValueError):
            horizon_from_lines([(0, 10, 60, 25)])

    def test_resolve_horizon_accepts_eight_numbers_as_two_lines(self):
        direct = horizon_from_lines([(0, 10, 60, 25), (0, 50, 60, 35)])
        viaflat = resolve_horizon([0, 10, 60, 25, 0, 50, 60, 35])
        np.testing.assert_allclose(viaflat / viaflat[1], direct / direct[1], atol=1e-9)

    def test_resolve_horizon_accepts_the_same_points_as_pairs(self):
        """The parameter form re-pairs eight numbers; both shapes must work."""
        flat = resolve_horizon([0, 10, 60, 25, 0, 50, 60, 35])
        pairs = resolve_horizon([[0, 10], [60, 25], [0, 50], [60, 35]])
        np.testing.assert_allclose(pairs / pairs[1], flat / flat[1], atol=1e-9)

    def test_resolve_horizon_accepts_sixteen_numbers_as_four_lines(self):
        line = resolve_horizon([0, 10, 60, 25, 0, 50, 60, 35,
                                0, 90, -20, 80, 0, 50, -20, 60])
        for point in ((80.0, 30.0), (-40.0, 70.0)):
            self.assertAlmostEqual(
                float(line @ np.array([point[0], point[1], 1.0])), 0.0, places=6)

    def test_an_unusable_count_says_how_many_it_got(self):
        with self.assertRaises(ValueError) as ctx:
            resolve_horizon([1, 2, 3, 4, 5])
        self.assertIn('5 numbers', str(ctx.exception))

    def test_the_derived_horizon_measures_correctly(self):
        """
        End to end: recover the horizon from two lines lying along the ground
        and measure with it, rather than being told where the horizon is.
        """
        camera = SyntheticCamera(pitch_degrees=0.0)
        reference = camera.pole(-900, 9000, 1800.0)
        base, top = camera.pole(600, 14000, 1650.0)

        # Two rails running away from the camera, at different offsets
        rails = []
        for offset in (-1500, 1500):
            near = camera.project((offset, 6000, 0.0))
            far = camera.project((offset, 30000, 0.0))
            rails.append((near[0], near[1], far[0], far[1]))

        result = measure_height(base, top, reference[0], reference[1], 1800.0,
                                horizon=horizon_from_lines(rails),
                                vertical_point=camera.vertical_point)
        self.assertAlmostEqual(result['height'], 1650.0, places=2)


class TestMeasureHeight(unittest.TestCase):

    def setUp(self):
        self.camera = SyntheticCamera()
        self.reference_height = 1800.0
        self.reference = self.camera.pole(-900, 9000, self.reference_height)

    def _measure(self, x, y, height, **kwargs):
        base, top = self.camera.pole(x, y, height)
        return measure_height(
            base, top, self.reference[0], self.reference[1],
            self.reference_height, self.camera.horizon,
            kwargs.pop('vertical_point', self.camera.vertical_point), **kwargs)

    def test_recovers_known_heights_across_the_scene(self):
        for true_height, (x, y) in (
            (1500.0, (1200, 7000)),
            (1800.0, (0, 12000)),
            (2100.0, (-400, 16000)),
            (1650.0, (2000, 22000)),
        ):
            with self.subTest(height=true_height, y=y):
                result = self._measure(x, y, true_height)
                self.assertAlmostEqual(result['height'], true_height, places=3)

    def test_reference_measures_as_itself(self):
        result = measure_height(
            self.reference[0], self.reference[1],
            self.reference[0], self.reference[1],
            self.reference_height, self.camera.horizon, self.camera.vertical_point)
        self.assertAlmostEqual(result['height'], self.reference_height, places=6)
        self.assertAlmostEqual(result['ratio'], 1.0, places=9)

    def test_height_is_independent_of_horizon_scaling(self):
        base, top = self.camera.pole(0, 12000, 1750.0)
        args = (base, top, self.reference[0], self.reference[1], self.reference_height)
        plain = measure_height(*args, self.camera.horizon, self.camera.vertical_point)
        scaled = measure_height(*args, self.camera.horizon * -37.0,
                                self.camera.vertical_point * 5.0)
        self.assertAlmostEqual(plain['height'], scaled['height'], places=6)

    def test_uncertainty_grows_with_distance(self):
        near = self._measure(0, 7000, 1750.0)['uncertainty_per_pixel']
        far = self._measure(0, 22000, 1750.0)['uncertainty_per_pixel']
        self.assertGreater(far, near)
        self.assertGreater(near, 0.0)

    def test_horizon_sensitivity_is_reported(self):
        result = self._measure(0, 12000, 1750.0)
        self.assertIn('horizon_uncertainty_per_pixel', result)
        self.assertGreater(result['horizon_uncertainty_per_pixel'], 0.0)

    def test_horizon_sensitivity_grows_with_distance(self):
        """
        Far from the camera the base crowds the horizon, so a horizon shifted
        by a pixel spans more real ground - the same reason the click
        sensitivity grows, and the reason the number is worth printing.
        """
        near = self._measure(0, 7000, 1750.0)['horizon_uncertainty_per_pixel']
        far = self._measure(0, 22000, 1750.0)['horizon_uncertainty_per_pixel']
        self.assertGreater(far, near)

    def test_horizon_sensitivity_does_not_depend_on_the_line_scaling(self):
        # The horizon is homogeneous, so (a, b, c) and -37(a, b, c) are one
        # line; a per-pixel figure that moved with the scaling would be junk
        base, top = self.camera.pole(0, 12000, 1750.0)
        args = (base, top, self.reference[0], self.reference[1], self.reference_height)
        plain = measure_height(*args, self.camera.horizon, self.camera.vertical_point)
        scaled = measure_height(*args, self.camera.horizon * -37.0,
                                self.camera.vertical_point * 5.0)
        self.assertAlmostEqual(plain['horizon_uncertainty_per_pixel'],
                               scaled['horizon_uncertainty_per_pixel'], places=6)

    def test_bases_straddling_the_horizon_are_refused(self):
        """
        Two objects on one ground plane image on one side of its horizon.
        Bases either side of it is not a hard measurement but an impossible
        one, and the usual cause is a horizon drawn along a ceiling.
        """
        base, top = self.camera.pole(0, 12000, 1750.0)
        line = resolve_horizon(self.camera.horizon)

        # Mirror the reference base across the horizon to put it on the far side
        reference_base = list(self.reference[0])
        y_horizon = -(line[0] * reference_base[0] + line[2]) / line[1]
        reference_base[1] = y_horizon - (reference_base[1] - y_horizon)

        with self.assertRaises(ValueError) as ctx:
            measure_height(base, top, reference_base, self.reference[1],
                           self.reference_height, self.camera.horizon,
                           self.camera.vertical_point)
        self.assertIn('opposite sides', str(ctx.exception))

    def test_a_valid_pair_is_not_refused(self):
        # The guard must not fire on ordinary geometry
        self.assertGreater(self._measure(0, 12000, 1750.0)['height'], 0)

    def test_parallel_vertical_assumption_is_exact_for_a_level_camera(self):
        camera = SyntheticCamera(pitch_degrees=0.0)
        reference = camera.pole(-900, 9000, 1800.0)
        base, top = camera.pole(400, 15000, 1750.0)
        result = measure_height(base, top, reference[0], reference[1], 1800.0,
                                camera.horizon, None)
        self.assertAlmostEqual(result['height'], 1750.0, places=3)

    def test_result_reports_units_and_reference(self):
        result = self._measure(0, 12000, 1750.0, unit_name='cm')
        self.assertEqual(result['unit'], 'cm')
        self.assertAlmostEqual(result['reference_height'], self.reference_height)

    def test_rejects_non_positive_reference_height(self):
        base, top = self.camera.pole(0, 12000, 1750.0)
        with self.assertRaises(ValueError):
            measure_height(base, top, self.reference[0], self.reference[1],
                           0.0, self.camera.horizon)

    def test_base_on_the_horizon_is_rejected(self):
        # A base sitting exactly on the horizon is infinitely far away
        with self.assertRaises(ValueError):
            measure_height((100.0, 200.0), (100.0, 150.0),
                           self.reference[0], self.reference[1],
                           self.reference_height, horizon=200.0)


class TestMeasure3dFilter(unittest.TestCase):

    def setUp(self):
        self.image = np.full((480, 640, 3), 60, dtype=np.uint8)

    def test_returns_annotated_image_of_the_same_size(self):
        result = draw_height_measurement(
            self.image, base=(300, 400), top=(300, 250),
            reference_base=(150, 380), reference_top=(150, 250),
            horizon=200, reference_height=1800.0)
        self.assertEqual(result.shape, self.image.shape)
        self.assertEqual(result.dtype, np.uint8)
        # Something was drawn
        self.assertFalse(np.array_equal(result, self.image))

    def test_the_uncertainty_is_drawn_not_just_computed(self):
        """
        The figure existed all along and never reached the operator: the label
        showed only the height. A number with no error beside it reads as a
        measurement rather than an estimate.
        """
        common = dict(base=(300, 400), top=(300, 250),
                      reference_base=(150, 380), reference_top=(150, 250),
                      horizon=200, reference_height=1800.0)
        with_note = draw_height_measurement(self.image, **common)
        without = draw_height_measurement(self.image, show_uncertainty=False, **common)

        self.assertFalse(np.array_equal(with_note, without))
        # The note sits below the height label, so the extra ink is lower down
        self.assertGreater(int((with_note != without).sum()), 0)

    def test_does_not_modify_the_input(self):
        before = self.image.copy()
        draw_height_measurement(self.image, base=(300, 400), top=(300, 250),
                   reference_base=(150, 380), reference_top=(150, 250),
                   horizon=200)
        np.testing.assert_array_equal(self.image, before)

    def test_accepts_a_grayscale_image(self):
        gray = np.full((480, 640), 60, dtype=np.uint8)
        result = draw_height_measurement(gray, base=(300, 400), top=(300, 250),
                            reference_base=(150, 380), reference_top=(150, 250),
                            horizon=200)
        self.assertEqual(result.shape, (480, 640, 3))

    def test_labels_stay_inside_the_frame(self):
        # A target hard against the right edge must not throw while placing text
        result = draw_height_measurement(self.image, base=(638, 460), top=(638, 300),
                            reference_base=(150, 380), reference_top=(150, 250),
                            horizon=200)
        self.assertEqual(result.shape, self.image.shape)

    def test_horizon_can_be_hidden(self):
        shown = draw_height_measurement(self.image, base=(300, 400), top=(300, 250),
                           reference_base=(150, 380), reference_top=(150, 250),
                           horizon=200, show_horizon=True)
        hidden = draw_height_measurement(self.image, base=(300, 400), top=(300, 250),
                            reference_base=(150, 380), reference_top=(150, 250),
                            horizon=200, show_horizon=False)
        self.assertFalse(np.array_equal(shown, hidden))

    def test_is_registered_as_a_chain_filter(self):
        from cv_tools.filters import FILTER_REGISTRY, filter_function
        self.assertIn('measure_3d', FILTER_REGISTRY)
        self.assertIs(filter_function('measure_3d'), draw_height_measurement)


if __name__ == '__main__':
    unittest.main()
