"""
Unit tests for single-view height measurement.

The substantive tests project a synthetic scene through a known pinhole camera
and check that the recovered heights match what was put in. Ground truth is
available exactly here, so these assert on real numbers rather than on the
result merely being finite.
"""

import unittest

import numpy as np

from src.filters import (
    draw_height_measurement,
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
        from src.filters import FILTER_REGISTRY, filter_function
        self.assertIn('measure_3d', FILTER_REGISTRY)
        self.assertIs(filter_function('measure_3d'), draw_height_measurement)


if __name__ == '__main__':
    unittest.main()
