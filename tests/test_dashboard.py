"""
Unit tests for the web dashboard.

Streamlit is an optional dependency (requirements-dashboard.txt), so the whole
module skips where it is absent rather than failing. ``AppTest`` runs the
script the way the server would and surfaces anything it raised, which is what
these tests assert on: the dashboard drives the shared Pipeline and registries,
so what is checked here is the wiring, not the filters.
"""

import unittest
from pathlib import Path

try:
    from streamlit.testing.v1 import AppTest
    STREAMLIT_AVAILABLE = True
    STREAMLIT_ERROR = ''
except Exception as exc:            # pragma: no cover - environment dependent
    STREAMLIT_AVAILABLE = False
    STREAMLIT_ERROR = str(exc)

DASHBOARD = Path(__file__).resolve().parent.parent / 'src' / 'dashboard.py'
SAMPLE = 'cctv_dark.png'


def button(app, label: str):
    """The button carrying a label; they have no keys of their own."""
    return next(b for b in app.button if b.label == label)


@unittest.skipUnless(STREAMLIT_AVAILABLE, f'Streamlit unavailable: {STREAMLIT_ERROR}')
class TestDashboard(unittest.TestCase):

    def _app(self, with_image: bool = True):
        app = AppTest.from_file(str(DASHBOARD), default_timeout=180)
        app.run()
        if with_image:
            app.selectbox[0].select(SAMPLE).run()
            button(app, 'Load sample').click().run()
            self.assertEqual(app.exception, [])
        return app

    def test_starts_without_an_image(self):
        app = self._app(with_image=False)
        self.assertEqual(app.exception, [])
        self.assertTrue(any('Upload an image' in info.value for info in app.info))

    def test_loading_a_sample_builds_a_pipeline(self):
        app = self._app()
        self.assertIsNotNone(app.session_state.pipeline)
        self.assertEqual(app.session_state.source_name, SAMPLE)
        self.assertEqual(len(app.tabs), 3)

    def test_statistics_tiles_describe_the_current_image(self):
        app = self._app()
        tiles = {metric.label: metric.value for metric in app.metric}
        self.assertEqual(tiles['Size'], '640 x 480')
        self.assertEqual(tiles['Filters applied'], '0')
        self.assertIn('Dynamic range used', tiles)

    def test_applying_a_filter_adds_it_to_the_chain(self):
        app = self._app()
        app.selectbox(key='selected_filter').select('clahe').run()
        button(app, 'Apply filter').click().run()

        self.assertEqual(app.exception, [])
        self.assertEqual([s.name for s in app.session_state.pipeline.chain], ['clahe'])

    def test_undo_is_offered_only_once_there_is_something_to_undo(self):
        app = self._app()
        self.assertTrue(button(app, 'Undo').disabled)
        self.assertTrue(button(app, 'Redo').disabled)

        app.selectbox(key='selected_filter').select('invert').run()
        button(app, 'Apply filter').click().run()
        self.assertFalse(button(app, 'Undo').disabled)

        button(app, 'Undo').click().run()
        self.assertEqual(len(app.session_state.pipeline), 0)
        self.assertFalse(button(app, 'Redo').disabled)

    def test_reordering_reprocesses_from_the_original(self):
        app = self._app()
        for name in ('clahe', 'invert'):
            app.selectbox(key='selected_filter').select(name).run()
            button(app, 'Apply filter').click().run()

        app.button(key='down_0').click().run()

        self.assertEqual(app.exception, [])
        self.assertEqual([s.name for s in app.session_state.pipeline.chain],
                         ['invert', 'clahe'])

    def test_removing_a_step_rebuilds_the_chain(self):
        app = self._app()
        for name in ('clahe', 'invert'):
            app.selectbox(key='selected_filter').select(name).run()
            button(app, 'Apply filter').click().run()

        app.button(key='remove_0').click().run()
        self.assertEqual([s.name for s in app.session_state.pipeline.chain], ['invert'])

    def test_guided_point_picking_fills_the_parameters(self):
        # The desktop viewer has filled coordinate parameters from clicks
        # since hour 5; the dashboard collected loose taps and left the user
        # to type them in
        app = self._app()
        app.selectbox(key='selected_filter').select('measure_3d').run()

        pick = [b for b in app.button if b.label.startswith('Pick')]
        self.assertTrue(pick, 'no picking button offered for measure_3d')
        pick[0].click().run()
        self.assertEqual(app.session_state.picking_for, 'measure_3d')

        # The prompt names the point wanted rather than counting
        self.assertTrue(any('FOOT of the reference' in info.value
                            for info in app.info))

        app.session_state.picks = [(300, 400), (300, 250), (450, 420),
                                   (450, 300),
                                   (0, 100), (600, 250), (0, 500), (600, 350)]
        app.run()

        self.assertEqual(app.exception, [])
        self.assertIsNone(app.session_state.picking_for)
        self.assertEqual(app.session_state['param_measure_3d_base'], '450,420')
        # Four taps become the eight numbers of two receding lines, which is
        # what the horizon is now derived from rather than guessed
        self.assertEqual(app.session_state['param_measure_3d_horizon'],
                         '0,100,600,250,0,500,600,350')

    def test_picking_is_offered_only_where_it_applies(self):
        app = self._app()
        app.selectbox(key='selected_filter').select('clahe').run()
        self.assertFalse([b for b in app.button if b.label.startswith('Pick')])

    def test_measuring_from_taps_all_the_way_into_the_chain(self):
        """
        Pick, calibrate, apply - the path the measurement filters exist for.

        The four taps are the two ends of what is measured and then the two
        ends of the reference, which is the order the click plan asks for.
        """
        app = self._app()
        app.selectbox(key='selected_filter').select('measure').run()

        pick = [b for b in app.button if b.label.startswith('Pick')]
        self.assertTrue(pick, 'no picking button offered for measure')
        pick[0].click().run()

        self.assertTrue(any('KNOWN length' in info.value for info in app.info)
                        or any('measuring' in info.value for info in app.info))

        # A 100px reference called 520mm, and a 200px span to measure by it
        app.session_state.picks = [(100, 300), (300, 300),
                                   (100, 100), (200, 100)]
        app.run()
        self.assertEqual(app.exception, [])
        self.assertEqual(app.session_state['param_measure_point_a'], '100,300')
        self.assertEqual(app.session_state['param_measure_reference_b'], '200,100')

        app.text_input(key='param_measure_reference_length').set_value('520').run()
        button(app, 'Apply filter').click().run()

        self.assertEqual(app.exception, [])
        chain = app.session_state.pipeline.chain
        self.assertEqual([step.name for step in chain], ['measure'])
        self.assertEqual(chain[0].params['reference_length'], 520.0)

    def test_running_an_image_report(self):
        app = self._app()
        app.selectbox(key='analysis_name').select('noise').run()
        button(app, 'Run report').click().run()

        self.assertEqual(app.exception, [])
        name, rows = app.session_state.analysis
        self.assertEqual(name, 'noise')
        self.assertTrue(rows[0].value.startswith('Noise analysis'))
        self.assertEqual(rows[-1].label, 'note')

    def test_a_report_that_reads_the_file_gets_the_uploaded_name(self):
        # The browser only ever hands over bytes, so the dashboard writes them
        # back to a file - keeping the name, which the report quotes
        app = self._app()
        app.selectbox(key='analysis_name').select('metadata').run()
        button(app, 'Run report').click().run()

        self.assertEqual(app.exception, [])
        _name, rows = app.session_state.analysis
        self.assertIn(SAMPLE, rows[0].value)


if __name__ == '__main__':
    unittest.main()
