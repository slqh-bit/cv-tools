"""
Unit tests for the Streamlit dashboard.

Streamlit is an optional dependency (``requirements-dashboard.txt``). Where it
is absent the whole module skips, the way the GUI tests skip without Tkinter.

Importing ``src.dashboard`` outside ``streamlit run`` puts Streamlit in "bare
mode": widgets return their default value instead of a user's, and
``st.session_state`` works while warning that it does not persist. That is
exactly the harness these tests need - the dashboard's own logic runs for real,
and only the widgets are inert. Two calls do *not* behave as they would in the
app and are patched wherever the assertion depends on them: ``st.stop`` and
``st.rerun`` return normally in bare mode rather than halting the script.
"""

import io
import os
import unittest
from unittest import mock

import numpy as np
from PIL import Image

try:
    import streamlit as st
    import src.dashboard as dash
    DASHBOARD_AVAILABLE = True
    DASHBOARD_ERROR = ''
except Exception as exc:            # pragma: no cover - environment dependent
    DASHBOARD_AVAILABLE = False
    DASHBOARD_ERROR = str(exc)

from src.filters import CATEGORY_ORDER, FILTER_REGISTRY


def png_bytes(height: int = 40, width: int = 60) -> bytes:
    """A PNG whose channels differ, so a channel swap is visible."""
    image = np.zeros((height, width, 3), dtype=np.uint8)
    image[:, :, 0] = 200        # red
    image[:, :, 1] = 100        # green
    image[:, :, 2] = 30         # blue
    buffer = io.BytesIO()
    Image.fromarray(image).save(buffer, format='PNG')
    return buffer.getvalue()


@unittest.skipUnless(DASHBOARD_AVAILABLE, f'streamlit unavailable: {DASHBOARD_ERROR}')
class DashboardTestCase(unittest.TestCase):
    """Session state is process-wide in bare mode, so each test starts clean."""

    def setUp(self):
        st.session_state.clear()

    tearDown = setUp


# ---- the access gate ---------------------------------------------------

class TestRequireAuth(DashboardTestCase):
    """
    The gate is the one piece of this file with a security consequence.

    It is only armed when CVTOOLS_PASSWORD is set. Armed and unsatisfied, it
    must call ``st.stop`` - in the real app that halts the script before a
    single control is drawn, and a test that only checked ``authed`` would pass
    while the whole dashboard rendered underneath the prompt.
    """

    def call(self, password=None, entered='', authed=False):
        environment = {} if password is None else {'CVTOOLS_PASSWORD': password}
        if authed:
            st.session_state.authed = True
        with mock.patch.dict(os.environ, environment, clear=True), \
             mock.patch.object(dash.st, 'text_input', return_value=entered), \
             mock.patch.object(dash.st, 'stop') as stop, \
             mock.patch.object(dash.st, 'rerun') as rerun, \
             mock.patch.object(dash.st, 'error') as error, \
             mock.patch.object(dash.st, 'title'), \
             mock.patch.object(dash.st, 'caption'):
            dash._require_auth()
        return stop, rerun, error

    def test_no_password_set_means_no_gate(self):
        stop, _, _ = self.call(password=None)
        stop.assert_not_called()
        self.assertNotIn('authed', st.session_state)

    def test_empty_password_variable_does_not_arm_the_gate(self):
        # An unset variable and one set to '' must behave the same. Were ''
        # treated as a password, compare_digest('', '') would let anyone in.
        stop, _, _ = self.call(password='')
        stop.assert_not_called()

    def test_armed_gate_stops_before_rendering(self):
        stop, _, _ = self.call(password='s3cret')
        stop.assert_called_once()

    def test_correct_password_authenticates(self):
        stop, rerun, error = self.call(password='s3cret', entered='s3cret')
        self.assertTrue(st.session_state.get('authed'))
        rerun.assert_called_once()
        error.assert_not_called()

    def test_wrong_password_is_refused(self):
        stop, rerun, error = self.call(password='s3cret', entered='guess')
        self.assertFalse(st.session_state.get('authed', False))
        error.assert_called_once()
        rerun.assert_not_called()
        stop.assert_called_once()

    def test_wrong_password_of_a_different_length_is_refused(self):
        # hmac.compare_digest raises on mismatched types, not lengths; this
        # guards the comparison against being swapped for something fussier.
        stop, rerun, error = self.call(password='s3cret', entered='x')
        self.assertFalse(st.session_state.get('authed', False))
        error.assert_called_once()
        stop.assert_called_once()

    def test_near_miss_password_is_refused(self):
        stop, rerun, _ = self.call(password='s3cret', entered='s3cres')
        self.assertFalse(st.session_state.get('authed', False))
        rerun.assert_not_called()

    def test_password_comparison_is_constant_time(self):
        with mock.patch.dict(os.environ, {'CVTOOLS_PASSWORD': 's3cret'}, clear=True), \
             mock.patch.object(dash.st, 'text_input', return_value='s3cret'), \
             mock.patch.object(dash.st, 'stop'), \
             mock.patch.object(dash.st, 'rerun'), \
             mock.patch.object(dash.st, 'title'), \
             mock.patch.object(dash.st, 'caption'), \
             mock.patch.object(dash.hmac, 'compare_digest',
                               wraps=dash.hmac.compare_digest) as compare:
            dash._require_auth()
        compare.assert_called_once_with('s3cret', 's3cret')

    def test_authenticated_session_skips_the_prompt(self):
        with mock.patch.dict(os.environ, {'CVTOOLS_PASSWORD': 's3cret'}, clear=True), \
             mock.patch.object(dash.st, 'text_input') as text_input, \
             mock.patch.object(dash.st, 'stop') as stop:
            st.session_state.authed = True
            dash._require_auth()
        text_input.assert_not_called()
        stop.assert_not_called()


# ---- filter ordering ---------------------------------------------------

class TestOrderedFilterNames(DashboardTestCase):

    def test_lists_every_registered_filter_exactly_once(self):
        names = dash._ordered_filter_names()
        self.assertEqual(sorted(names), sorted(FILTER_REGISTRY))
        self.assertEqual(len(names), len(set(names)))

    def test_grouped_by_category_in_declared_order(self):
        names = dash._ordered_filter_names()
        positions = [CATEGORY_ORDER.index(FILTER_REGISTRY[n].category) for n in names]
        self.assertEqual(positions, sorted(positions))

    def test_alphabetical_within_each_category(self):
        names = dash._ordered_filter_names()
        for category in CATEGORY_ORDER:
            block = [n for n in names if FILTER_REGISTRY[n].category == category]
            self.assertEqual(block, sorted(block), f'{category} is not A-Z')

    def test_every_category_is_represented(self):
        # A filter given a category outside CATEGORY_ORDER would vanish from
        # the picker entirely rather than fail loudly.
        used = {spec.category for spec in FILTER_REGISTRY.values()}
        self.assertTrue(used.issubset(set(CATEGORY_ORDER)),
                        f'categories missing from CATEGORY_ORDER: {used - set(CATEGORY_ORDER)}')


# ---- session state and loading -----------------------------------------

class TestInitState(DashboardTestCase):

    def test_sets_every_key_the_app_reads(self):
        dash._init_state()
        for key in ('pipeline', 'metadata', 'source_name',
                    'selected_filter', 'picks', 'last_tap'):
            self.assertIn(key, st.session_state)

    def test_default_selection_is_a_real_filter(self):
        dash._init_state()
        self.assertIn(st.session_state.selected_filter, FILTER_REGISTRY)

    def test_does_not_clobber_an_existing_session(self):
        st.session_state.selected_filter = 'clahe'
        st.session_state.picks = [(1, 2)]
        dash._init_state()
        self.assertEqual(st.session_state.selected_filter, 'clahe')
        self.assertEqual(st.session_state.picks, [(1, 2)])


class TestLoadImage(DashboardTestCase):

    def test_builds_a_pipeline_from_uploaded_bytes(self):
        dash._load_image(png_bytes(), 'evidence.png')
        self.assertIsNotNone(st.session_state.pipeline)
        self.assertEqual(st.session_state.source_name, 'evidence.png')

    def test_records_the_source_dimensions(self):
        dash._load_image(png_bytes(height=40, width=60), 'evidence.png')
        self.assertEqual(st.session_state.metadata['width'], 60)
        self.assertEqual(st.session_state.metadata['height'], 40)
        self.assertEqual(st.session_state.metadata['filename'], 'evidence.png')

    def test_converts_to_bgr_for_the_filters(self):
        # Filters are OpenCV-shaped. Loading RGB straight through would swap
        # every colour operation in the toolkit without raising anything.
        dash._load_image(png_bytes(), 'evidence.png')
        pixel = st.session_state.pipeline.original[0, 0]
        self.assertEqual(tuple(int(v) for v in pixel), (30, 100, 200))

    def test_replacing_the_image_resets_the_chain(self):
        dash._load_image(png_bytes(), 'first.png')
        st.session_state.pipeline.apply(
            FILTER_REGISTRY['invert'].fn, 'invert', 'src.filters.invert', {})
        dash._load_image(png_bytes(), 'second.png')
        self.assertEqual(st.session_state.pipeline.chain, [])


# ---- the parameter form ------------------------------------------------

class TestChoicesFor(DashboardTestCase):

    def test_component_offers_colour_space_channels_not_rgb(self):
        # A Streamlit selectbox offers only what it lists, so the global r/g/b
        # channel list would make `component` impossible to drive.
        choices = dash._choices_for(FILTER_REGISTRY['component'])
        self.assertIn('L', choices['channel'])
        self.assertNotEqual(choices['channel'], dash.CHOICES['channel'])

    def test_component_channel_names_are_unique_and_sorted(self):
        channels = dash._choices_for(FILTER_REGISTRY['component'])['channel']
        self.assertEqual(channels, sorted(set(channels)))

    def test_curves_preset_allows_an_empty_choice(self):
        # curves works with explicit control points and no preset, so the
        # empty option has to be reachable.
        presets = dash._choices_for(FILTER_REGISTRY['curves'])['preset']
        self.assertEqual(presets[0], '')

    def test_stain_preset_is_stain_presets_only(self):
        from src.filters import STAIN_PRESETS
        self.assertEqual(dash._choices_for(FILTER_REGISTRY['stain'])['preset'],
                         sorted(STAIN_PRESETS))

    def test_an_ordinary_filter_gets_the_global_lists(self):
        choices = dash._choices_for(FILTER_REGISTRY['clahe'])
        self.assertEqual(choices['channel'], dash.CHOICES['channel'])


class TestParamForm(DashboardTestCase):

    def test_every_registered_filter_builds_a_form(self):
        # In bare mode each widget returns its default, so this asserts that
        # every filter's signature can be rendered at all - the failure mode
        # being a filter that is registered but unreachable from the browser.
        for name, spec in FILTER_REGISTRY.items():
            with self.subTest(filter=name):
                st.session_state.clear()
                params = dash._param_form(spec)
                self.assertTrue(params is None or isinstance(params, dict))

    def test_optional_parameters_come_back_as_their_defaults(self):
        import inspect
        params = dash._param_form(FILTER_REGISTRY['clahe'])
        signature = inspect.signature(FILTER_REGISTRY['clahe'].fn)
        self.assertEqual(params['clip_limit'],
                         signature.parameters['clip_limit'].default)

    def test_a_filter_with_no_parameters_returns_an_empty_dict(self):
        with mock.patch.object(dash.st, 'caption') as caption:
            params = dash._param_form(FILTER_REGISTRY['invert'])
        self.assertEqual(params, {})
        caption.assert_called_once()

    def test_missing_required_parameters_block_the_apply(self):
        # roi_crop needs a region. Returning {} instead of None would apply the
        # filter with no arguments and raise inside the pipeline.
        with mock.patch.object(dash.st, 'warning') as warning:
            params = dash._param_form(FILTER_REGISTRY['roi_crop'])
        self.assertIsNone(params)
        warning.assert_called_once()

    def test_boolean_parameters_become_checkboxes(self):
        spec = next(s for s in FILTER_REGISTRY.values()
                    if any(isinstance(p.default, bool)
                           for p in list(__import__('inspect')
                                         .signature(s.fn).parameters.values())[1:]))
        with mock.patch.object(dash.st, 'checkbox',
                               side_effect=lambda label, value, key: value) as checkbox:
            dash._param_form(spec)
        checkbox.assert_called()

    def test_widget_keys_are_namespaced_by_filter(self):
        # Two filters sharing a parameter name must not share a widget key, or
        # switching between them carries the other's value across.
        with mock.patch.object(dash.st, 'slider',
                               side_effect=lambda l, lo, hi, d, key: d) as slider:
            dash._param_form(FILTER_REGISTRY['clahe'])
        keys = [call.kwargs['key'] for call in slider.call_args_list]
        self.assertTrue(all(key.startswith('param_clahe_') for key in keys), keys)


class TestParseText(DashboardTestCase):

    def test_parses_a_single_value(self):
        self.assertEqual(dash._parse_text('5'), 5)

    def test_parses_a_comma_list(self):
        self.assertEqual(dash._parse_text('1,2,3'), [1, 2, 3])

    def test_eight_numbers_become_four_corner_pairs(self):
        # perspective takes four corners; typing eight numbers is how they are
        # given, and the filter wants them paired.
        self.assertEqual(dash._parse_text('0,0,10,0,10,10,0,10'),
                         [[0, 0], [10, 0], [10, 10], [0, 10]])

    def test_eight_values_containing_a_non_number_stay_flat(self):
        parsed = dash._parse_text('0,0,10,0,10,10,0,edge')
        self.assertEqual(len(parsed), 8)
        self.assertEqual(parsed[-1], 'edge')

    def test_six_numbers_stay_flat(self):
        self.assertEqual(dash._parse_text('1,2,3,4,5,6'), [1, 2, 3, 4, 5, 6])

    def test_whitespace_around_items_is_ignored(self):
        self.assertEqual(dash._parse_text('1, 2 ,3'), [1, 2, 3])


# ---- coordinate grid ---------------------------------------------------

class TestCoordinateGrid(DashboardTestCase):

    def test_shape_and_dtype_are_preserved(self):
        image = np.full((200, 300, 3), 90, dtype=np.uint8)
        grid = dash._draw_coordinate_grid(image, 50)
        self.assertEqual(grid.shape, image.shape)
        self.assertEqual(grid.dtype, image.dtype)

    def test_the_source_image_is_not_modified(self):
        # The overlay is display-only; drawing into the pipeline's array would
        # put gridlines in the download and in every measurement.
        image = np.full((200, 300, 3), 90, dtype=np.uint8)
        before = image.copy()
        grid = dash._draw_coordinate_grid(image, 50)
        np.testing.assert_array_equal(image, before)
        self.assertIsNot(grid, image)

    def test_something_is_actually_drawn(self):
        image = np.full((200, 300, 3), 90, dtype=np.uint8)
        self.assertTrue((dash._draw_coordinate_grid(image, 50) != image).any())

    # (x=50, y=175) sits on a minor vertical gridline for a 50px grid, well
    # away from the labels, whose dark plates otherwise dominate a whole-image
    # mean and hide what the lines themselves did.
    LINE_PIXEL = (175, 50)

    def test_lines_are_light_on_a_dark_image(self):
        dark = np.full((300, 300, 3), 10, dtype=np.uint8)
        grid = dash._draw_coordinate_grid(dark, 50)
        self.assertGreater(grid[self.LINE_PIXEL].mean(), 10,
                           'gridline is not lighter than the dark image under it')

    def test_lines_are_dark_on_a_bright_image(self):
        bright = np.full((300, 300, 3), 240, dtype=np.uint8)
        grid = dash._draw_coordinate_grid(bright, 50)
        self.assertLess(grid[self.LINE_PIXEL].mean(), 240,
                        'gridline is not darker than the bright image under it')

    def test_the_chosen_tone_actually_depends_on_the_image(self):
        # The two tests above pass a fixed white tone if read separately; this
        # is the one that says the choice is made, not assumed.
        dark = np.full((300, 300, 3), 10, dtype=np.uint8)
        bright = np.full((300, 300, 3), 240, dtype=np.uint8)
        on_dark = dash._draw_coordinate_grid(dark, 50)[self.LINE_PIXEL].mean() - 10
        on_bright = dash._draw_coordinate_grid(bright, 50)[self.LINE_PIXEL].mean() - 240
        self.assertGreater(on_dark, 0, 'dark image did not get a lighter line')
        self.assertLess(on_bright, 0, 'bright image did not get a darker line')

    def test_spacing_is_clamped_so_it_cannot_hang(self):
        # A zero or negative spacing would be an infinite range() step.
        image = np.full((100, 100, 3), 90, dtype=np.uint8)
        for spacing in (0, -10, 1):
            with self.subTest(spacing=spacing):
                self.assertEqual(dash._draw_coordinate_grid(image, spacing).shape,
                                 image.shape)

    def test_survives_an_image_smaller_than_the_spacing(self):
        tiny = np.full((8, 8, 3), 90, dtype=np.uint8)
        self.assertEqual(dash._draw_coordinate_grid(tiny, 50).shape, tiny.shape)

    def test_labels_stay_inside_the_frame(self):
        canvas = np.zeros((60, 60, 3), dtype=np.uint8)
        dash._grid_label(canvas, '1000', (58, 58), 0.5, 1)   # off the edge
        self.assertTrue(canvas.any(), 'label was clipped away entirely')


# ---- tap to pick -------------------------------------------------------

class TestRecordTap(DashboardTestCase):

    def setUp(self):
        super().setUp()
        st.session_state.picks = []
        st.session_state.last_tap = None

    def test_scales_displayed_coordinates_back_to_image_pixels(self):
        # The browser renders the image at whatever width it likes; a tap at
        # the centre of a half-size render is the centre of the image.
        dash._record_tap({'x': 50, 'y': 40, 'width': 100, 'height': 80,
                          'unix_time': 1}, (160, 200))
        self.assertEqual(st.session_state.picks, [(100, 80)])

    def test_an_unscaled_tap_is_recorded_as_is(self):
        dash._record_tap({'x': 30, 'y': 20, 'width': 200, 'height': 160,
                          'unix_time': 1}, (160, 200))
        self.assertEqual(st.session_state.picks, [(30, 20)])

    def test_coordinates_are_clamped_to_the_image(self):
        dash._record_tap({'x': 200, 'y': 160, 'width': 200, 'height': 160,
                          'unix_time': 1}, (160, 200))
        self.assertEqual(st.session_state.picks, [(199, 159)])

    def test_a_replayed_tap_is_not_recorded_twice(self):
        # The component replays its last value on every rerun, so the
        # timestamp is the only thing separating a new tap from a redraw.
        tap = {'x': 10, 'y': 10, 'width': 200, 'height': 160, 'unix_time': 7}
        dash._record_tap(tap, (160, 200))
        dash._record_tap(dict(tap), (160, 200))
        self.assertEqual(len(st.session_state.picks), 1)

    def test_a_new_tap_at_the_same_point_is_recorded(self):
        base = {'x': 10, 'y': 10, 'width': 200, 'height': 160}
        dash._record_tap({**base, 'unix_time': 7}, (160, 200))
        dash._record_tap({**base, 'unix_time': 8}, (160, 200))
        self.assertEqual(len(st.session_state.picks), 2)

    def test_nothing_picked_is_ignored(self):
        for picked in (None, {}):
            with self.subTest(picked=picked):
                dash._record_tap(picked, (160, 200))
        self.assertEqual(st.session_state.picks, [])

    def test_a_zero_sized_render_is_ignored(self):
        # Dividing by the reported width would raise before the first paint.
        dash._record_tap({'x': 5, 'y': 5, 'width': 0, 'height': 0,
                          'unix_time': 1}, (160, 200))
        self.assertEqual(st.session_state.picks, [])

    def test_a_missing_render_size_is_ignored(self):
        dash._record_tap({'x': 5, 'y': 5, 'unix_time': 1}, (160, 200))
        self.assertEqual(st.session_state.picks, [])


if __name__ == '__main__':
    unittest.main()
