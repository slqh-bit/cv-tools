"""
Unit tests for the analysis registry.

The registry is what the CLI prints, what the GUI's Analysis tab shows and
what the dashboard renders, so these tests cover the contract all three rely
on: every spec runs, every report renders, and a spec that needs the source
file says so rather than failing obscurely.
"""

import tempfile
import unittest
from pathlib import Path

import numpy as np

from cv_tools.core import save_image
from cv_tools.filters import (
    ANALYSIS_REGISTRY,
    Row,
    list_analyses,
    render_report,
    report_lines,
    resolve_analysis,
    run_analysis,
)


def sample_image(height: int = 64, width: int = 96) -> np.ndarray:
    rng = np.random.default_rng(11)
    base = np.linspace(20, 220, width, dtype=np.float32)
    image = np.repeat(np.tile(base, (height, 1))[:, :, np.newaxis], 3, axis=2)
    return np.clip(image + rng.normal(0, 6, image.shape), 0, 255).astype(np.uint8)


class TestRegistry(unittest.TestCase):

    def test_names_are_the_ones_the_cli_exposes(self):
        # --noise-stats, --ela-stats and so on; the GUI and dashboard pick
        # from the same names
        self.assertEqual(set(ANALYSIS_REGISTRY),
                         {'noise', 'ela', 'clone', 'compression', 'ghost', 'metadata'})

    def test_every_spec_describes_itself(self):
        for name, spec in ANALYSIS_REGISTRY.items():
            with self.subTest(analysis=name):
                self.assertTrue(spec.description)
                # The caveat is the point of a forensic report: no measure here
                # concludes anything on its own
                self.assertTrue(spec.caveat)
                self.assertTrue(spec.module.startswith('cv_tools.filters.'))

    def test_list_analyses_pairs_names_with_descriptions(self):
        pairs = dict(list_analyses())
        self.assertEqual(set(pairs), set(ANALYSIS_REGISTRY))

    def test_unknown_name_lists_the_alternatives(self):
        with self.assertRaises(KeyError) as caught:
            resolve_analysis('nope')
        self.assertIn('noise', str(caught.exception))


class TestRunning(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.image = sample_image()
        cls._tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls._tmp.name) / 'evidence.jpg'
        save_image(cls.image, str(cls.path), quality=85)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_every_analysis_runs_and_renders(self):
        # Catches any report whose formatter reads a key its analysis function
        # stopped producing, including ones added after this test was written
        for name, spec in ANALYSIS_REGISTRY.items():
            with self.subTest(analysis=name):
                report = run_analysis(spec, image=self.image, path=self.path)
                self.assertIsInstance(report, dict)

                rows = render_report(spec, report)
                self.assertTrue(all(isinstance(row, Row) for row in rows))
                # Header first, caveat last
                self.assertEqual(rows[0].indent, -1)
                self.assertTrue(rows[0].value.endswith(':'))
                self.assertEqual(rows[-1].label, 'note')

    def test_report_lines_are_indented_text(self):
        spec = resolve_analysis('noise')
        report = run_analysis(spec, image=self.image)
        lines = report_lines(spec, report)

        self.assertEqual(lines[0], 'Noise analysis:')
        self.assertTrue(all(line.startswith('  ') for line in lines[1:]))
        self.assertTrue(any('global sigma' in line for line in lines))

    def test_params_reach_the_analysis_function(self):
        spec = resolve_analysis('ela')
        report = run_analysis(spec, image=self.image, params={'quality': 70})
        self.assertEqual(report['quality'], 70)

    def test_a_path_only_analysis_needs_no_image(self):
        spec = resolve_analysis('metadata')
        self.assertFalse(spec.needs_image)
        report = run_analysis(spec, path=self.path)
        self.assertEqual(report['filename'], 'evidence.jpg')

    def test_a_missing_path_is_reported_not_guessed(self):
        spec = resolve_analysis('metadata')
        with self.assertRaises(ValueError):
            run_analysis(spec, image=self.image)

    def test_a_missing_image_is_reported(self):
        spec = resolve_analysis('noise')
        with self.assertRaises(ValueError):
            run_analysis(spec, image=None)

    def test_path_parameter_is_hidden_from_generated_forms(self):
        # Both front ends build their parameter form from the signature; the
        # path comes from the loaded file rather than being typed
        for name in ('compression', 'metadata'):
            with self.subTest(analysis=name):
                self.assertIn('path', resolve_analysis(name).skip_params)

    def test_severity_marks_the_findings_worth_investigating(self):
        spec = resolve_analysis('metadata')
        report = run_analysis(spec, path=self.path)
        severities = {row.severity for row in render_report(spec, report)}
        self.assertTrue(severities <= {'', 'info', 'flag'})


if __name__ == '__main__':
    unittest.main()
