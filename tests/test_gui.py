"""
Unit tests for the GUI.

Tkinter needs a display. Where there is none - a headless CI box - the whole
module skips rather than fails, since the GUI is an optional component.
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

try:
    import tkinter as tk
    _root = tk.Tk()
    _root.destroy()
    TK_AVAILABLE = True
    TK_ERROR = ''
except Exception as exc:            # pragma: no cover - environment dependent
    TK_AVAILABLE = False
    TK_ERROR = str(exc)

from src.core import FilterStep, Pipeline
from src.filters import (
    ANALYSIS_REGISTRY,
    CATEGORY_ORDER,
    FILTER_REGISTRY,
    apply_clahe,
    resolve_filter,
)


def sample_image(height: int = 48, width: int = 64) -> np.ndarray:
    rng = np.random.default_rng(4)
    base = np.linspace(30, 200, width, dtype=np.float32)
    image = np.repeat(np.tile(base, (height, 1))[:, :, np.newaxis], 3, axis=2)
    return np.clip(image + rng.normal(0, 8, image.shape), 0, 255).astype(np.uint8)


@unittest.skipUnless(TK_AVAILABLE, f'Tkinter unavailable: {TK_ERROR}')
class TestParameterPanel(unittest.TestCase):
    """The panel is generated from each filter's signature."""

    @classmethod
    def setUpClass(cls):
        from src.gui.widgets import ParameterPanel
        cls.ParameterPanel = ParameterPanel
        cls.root = tk.Tk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_builds_for_every_registered_filter(self):
        # Catches any filter whose signature the introspection cannot handle,
        # including ones added after this test was written
        panel = self.ParameterPanel(self.root)
        for name, spec in FILTER_REGISTRY.items():
            with self.subTest(filter=name):
                panel.build(spec)
                self.assertIsNotNone(panel._body)
        panel.destroy()

    def test_defaults_match_the_signature(self):
        panel = self.ParameterPanel(self.root)
        panel.build(resolve_filter('clahe'))
        params = panel.get_params()
        self.assertAlmostEqual(params['clip_limit'], 2.0, places=3)
        self.assertEqual(params['color_mode'], 'lab')
        panel.destroy()

    def test_produces_params_the_filter_accepts(self):
        panel = self.ParameterPanel(self.root)
        image = sample_image()
        for name in ('clahe', 'levels', 'sharpen', 'gaussian_blur', 'saturation',
                     'invert', 'canny', 'white_balance', 'local_contrast'):
            with self.subTest(filter=name):
                spec = resolve_filter(name)
                panel.build(spec)
                params = panel.get_params()
                result = spec.fn(image, **params)
                self.assertIsInstance(result, np.ndarray)
        panel.destroy()

    def test_either_or_parameters_need_a_choice(self):
        # curves takes points *or* a preset; a signature cannot express that,
        # so the filter rejects the empty case with a clear message
        panel = self.ParameterPanel(self.root)
        spec = resolve_filter('curves')
        panel.build(spec)

        with self.assertRaises(ValueError) as ctx:
            spec.fn(sample_image(), **panel.get_params())
        self.assertIn('points or a preset', str(ctx.exception))

        # Choosing a preset in the combobox makes it work
        panel._entries['preset']['var'].set('lift_shadows')
        result = spec.fn(sample_image(), **panel.get_params())
        self.assertIsInstance(result, np.ndarray)
        panel.destroy()

    def test_required_parameter_left_blank_raises(self):
        panel = self.ParameterPanel(self.root)
        panel.build(resolve_filter('roi_crop'))   # x, y, width, height have no defaults
        with self.assertRaises(ValueError):
            panel.get_params()
        panel.destroy()

    def test_prefilled_values_are_used(self):
        panel = self.ParameterPanel(self.root)
        panel.build(resolve_filter('clahe'), values={'clip_limit': 4.5,
                                                     'color_mode': 'yuv'})
        params = panel.get_params()
        self.assertAlmostEqual(params['clip_limit'], 4.5, places=3)
        self.assertEqual(params['color_mode'], 'yuv')
        panel.destroy()

    def test_boolean_parameters_become_checkboxes(self):
        panel = self.ParameterPanel(self.root)
        panel.build(resolve_filter('sobel'))
        self.assertEqual(panel._entries['normalize']['kind'], 'bool')
        self.assertIs(panel.get_params()['normalize'], True)
        panel.destroy()

    def test_comma_text_parses_to_a_list(self):
        from src.gui.widgets import _parse_text
        self.assertEqual(_parse_text('1,2,3'), [1, 2, 3])
        self.assertEqual(_parse_text('8x8'), (8, 8))
        self.assertEqual(_parse_text('lab'), 'lab')

    def test_eight_numbers_become_corner_pairs(self):
        from src.gui.widgets import _parse_text
        self.assertEqual(_parse_text('1,2,3,4,5,6,7,8'),
                         [[1, 2], [3, 4], [5, 6], [7, 8]])

    def test_clear_removes_controls(self):
        panel = self.ParameterPanel(self.root)
        panel.build(resolve_filter('clahe'))
        panel.clear()
        self.assertEqual(panel.get_params(), {})
        panel.destroy()


@unittest.skipUnless(TK_AVAILABLE, f'Tkinter unavailable: {TK_ERROR}')
class TestImageCanvas(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from src.gui.widgets import ImageCanvas
        cls.ImageCanvas = ImageCanvas
        cls.root = tk.Tk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def setUp(self):
        self.canvas = self.ImageCanvas(self.root)
        self.original = sample_image()
        self.processed = apply_clahe(self.original, clip_limit=4.0)

    def tearDown(self):
        self.canvas.destroy()

    def test_empty_canvas_composes_nothing(self):
        self.assertIsNone(self.canvas._compose())

    def test_processed_mode_shows_the_processed_image(self):
        self.canvas.set_images(self.original, self.processed)
        np.testing.assert_array_equal(self.canvas._compose(), self.processed)

    def test_original_mode_shows_the_original(self):
        self.canvas.set_images(self.original, self.processed)
        self.canvas.set_mode('original')
        np.testing.assert_array_equal(self.canvas._compose(), self.original)

    def test_side_by_side_is_wider_than_both(self):
        self.canvas.set_images(self.original, self.processed)
        self.canvas.set_mode('side by side')
        composite = self.canvas._compose()
        self.assertGreaterEqual(composite.shape[1], self.original.shape[1] * 2)

    def test_split_takes_each_side_from_a_different_image(self):
        self.canvas.set_images(self.original, self.processed)
        self.canvas.set_mode('split')
        composite = self.canvas._compose()

        self.assertEqual(composite.shape, self.original.shape)
        # Left of the divider matches the original, right matches the processed
        np.testing.assert_array_equal(composite[:, :10], self.original[:, :10])
        np.testing.assert_array_equal(composite[:, -10:], self.processed[:, -10:])

    def test_comparison_handles_differently_sized_images(self):
        # A crop step makes the two differ; both must still compose
        cropped = self.processed[:20, :30]
        self.canvas.set_images(self.original, cropped)
        for mode in ('split', 'side by side'):
            with self.subTest(mode=mode):
                self.canvas.set_mode(mode)
                self.assertIsNotNone(self.canvas._compose())

    def test_grayscale_output_is_displayable(self):
        from src.filters import canny_edges
        edges = canny_edges(self.original, 50, 150)
        self.canvas.set_images(self.original, edges)
        composite = self.canvas._compose()
        self.assertEqual(composite.ndim, 3)
        self.assertEqual(composite.shape[2], 3)

    def test_zoom_setting(self):
        self.canvas.set_zoom(2.0)
        self.assertFalse(self.canvas.fit_to_window)
        self.assertEqual(self.canvas.zoom, 2.0)
        self.canvas.set_zoom(None)
        self.assertTrue(self.canvas.fit_to_window)

    def test_zoom_is_clamped(self):
        self.canvas.set_zoom(500.0)
        self.assertLessEqual(self.canvas.zoom, 16.0)


@unittest.skipUnless(TK_AVAILABLE, f'Tkinter unavailable: {TK_ERROR}')
class TestApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from src.gui.app import CVToolsApp
        cls.CVToolsApp = CVToolsApp

    def setUp(self):
        # Modal dialogs block forever without a user to dismiss them, so they
        # are intercepted; the mock also lets a test assert one was raised
        self.messagebox = mock.patch('src.gui.app.messagebox').start()
        self.filedialog = mock.patch('src.gui.app.filedialog').start()
        self.addCleanup(mock.patch.stopall)

        self.app = self.CVToolsApp()
        self.app.withdraw()
        self.image = sample_image()
        self.app.pipeline = Pipeline(self.image)
        self.app.metadata = {'filename': 'test.png', 'width': 64, 'height': 48,
                             'sha256': 'a' * 64}
        self.app.update_idletasks()

    def tearDown(self):
        self.app.destroy()

    def _select(self, name: str) -> None:
        # The list is grouped by family, so a row's index is not the filter's
        # position in a sorted registry; _filter_rows maps rows to names
        self.app.filter_list.selection_clear(0, 'end')
        self.app.filter_list.selection_set(self.app._filter_rows.index(name))
        self.app._on_filter_selected()

    def _listed(self) -> list:
        return [name for name in self.app._filter_rows if name is not None]

    def test_filter_list_holds_every_registered_filter(self):
        self.assertEqual(set(self._listed()), set(FILTER_REGISTRY))

    def test_filter_list_is_grouped_by_family(self):
        rows = list(self.app.filter_list.get(0, 'end'))
        headings = [row.strip() for row, name in zip(rows, self.app._filter_rows)
                    if name is None]
        self.assertEqual(headings, [c.upper() for c in CATEGORY_ORDER])

        # Every filter sits under the heading for its own family
        current = None
        for row, name in zip(rows, self.app._filter_rows):
            if name is None:
                current = row.strip().title()
            else:
                self.assertEqual(FILTER_REGISTRY[name].category, current)

    def test_category_narrows_the_list(self):
        self.app.category.set('Forensic')
        self.app._refresh_filter_list()
        categories = {FILTER_REGISTRY[name].category for name in self._listed()}
        self.assertEqual(categories, {'Forensic'})

    def test_headings_cannot_be_selected_as_filters(self):
        self.app._selected_filter = None
        heading = self.app._filter_rows.index(None)
        self.app.filter_list.selection_set(heading)
        self.app._on_filter_selected()

        self.assertIsNone(self.app._selected_filter)
        self.assertEqual(self.app.filter_list.curselection(), ())

    def test_search_filters_the_list(self):
        self.app.search.set('clahe')
        self.app.update_idletasks()
        self.assertEqual(self._listed(), ['clahe'])

    def test_search_matches_descriptions_too(self):
        self.app.search.set('wiener')
        self.app.update_idletasks()
        self.assertIn('deblur_motion', self._listed())

    def test_apply_adds_to_the_chain(self):
        self._select('clahe')
        self.app.apply_filter()
        self.assertEqual(len(self.app.pipeline), 1)
        self.assertEqual(self.app.pipeline.chain[0].name, 'clahe')
        self.assertEqual(self.app.chain_list.size(), 1)

    def test_applied_image_differs_from_the_original(self):
        self._select('clahe')
        self.app.apply_filter()
        self.assertFalse(np.array_equal(self.app.pipeline.current, self.image))

    def test_undo_and_redo(self):
        self._select('clahe')
        self.app.apply_filter()
        self.app.undo()
        self.assertEqual(len(self.app.pipeline), 0)
        self.app.redo()
        self.assertEqual(len(self.app.pipeline), 1)

    def test_reset_clears_the_chain(self):
        self._select('clahe')
        self.app.apply_filter()
        self.app.reset_chain()
        self.assertEqual(len(self.app.pipeline), 0)
        np.testing.assert_array_equal(self.app.pipeline.current, self.image)

    def test_remove_step(self):
        for name in ('clahe', 'invert'):
            self._select(name)
            self.app.apply_filter()

        self.app.chain_list.selection_set(0)
        self.app.remove_step()

        self.assertEqual([s.name for s in self.app.pipeline.chain], ['invert'])

    def test_reorder_reprocesses_from_the_original(self):
        self._select('contrast_brightness')
        self.app.parameters._entries['brightness']['var'].set(60.0)
        self.app.apply_filter()
        self._select('clahe')
        self.app.apply_filter()
        first_order = self.app.pipeline.current.copy()

        self.app.chain_list.selection_set(0)
        self.app.move_down()

        self.assertEqual([s.name for s in self.app.pipeline.chain],
                         ['clahe', 'contrast_brightness'])
        self.assertFalse(np.array_equal(self.app.pipeline.current, first_order))

    def test_move_up_at_the_top_does_nothing(self):
        self._select('clahe')
        self.app.apply_filter()
        self.app.chain_list.selection_set(0)
        self.app.move_up()
        self.assertEqual(len(self.app.pipeline), 1)

    def test_duplicate_step_repeats_it_in_place(self):
        self._select('clahe')
        self.app.apply_filter()
        self.app.chain_list.selection_set(0)
        self.app.duplicate_step()

        self.assertEqual([s.name for s in self.app.pipeline.chain],
                         ['clahe', 'clahe'])
        self.assertEqual(self.app.pipeline.chain[0].params,
                         self.app.pipeline.chain[1].params)

    def test_selecting_a_step_loads_its_own_parameters(self):
        self._select('contrast_brightness')
        self.app.parameters._entries['brightness']['var'].set(40.0)
        self.app.apply_filter()

        self.app.chain_list.selection_set(0)
        self.app._on_step_selected()

        self.assertEqual(self.app._editing_step, 0)
        self.assertAlmostEqual(
            self.app.parameters._entries['brightness']['var'].get(), 40.0, places=3)
        self.assertIn('Step 1', self.app.parameter_title.cget('text'))

    def test_updating_a_step_reprocesses_rather_than_appending(self):
        self._select('contrast_brightness')
        self.app.parameters._entries['brightness']['var'].set(20.0)
        self.app.apply_filter()
        before = self.app.pipeline.current.copy()

        self.app.chain_list.selection_set(0)
        self.app._on_step_selected()
        self.app.parameters._entries['brightness']['var'].set(90.0)
        self.app.update_step()

        self.assertEqual(len(self.app.pipeline), 1)
        self.assertEqual(self.app.pipeline.chain[0].params['brightness'], 90.0)
        self.assertFalse(np.array_equal(self.app.pipeline.current, before))

    def test_a_step_edit_does_not_survive_selecting_a_filter(self):
        self._select('clahe')
        self.app.apply_filter()
        self.app.chain_list.selection_set(0)
        self.app._on_step_selected()

        self._select('invert')
        self.assertIsNone(self.app._editing_step)

    def test_analysis_tab_offers_every_registered_report(self):
        box_values = self.app.analysis_name.get()
        self.assertIn(box_values, ANALYSIS_REGISTRY)

        for name in ANALYSIS_REGISTRY:
            with self.subTest(analysis=name):
                self.app.analysis_name.set(name)
                self.app._on_analysis_selected()
                self.assertIsNotNone(self.app.analysis_params._body)

    def test_running_a_report_shows_it_with_its_caveat(self):
        self.app.analysis_name.set('noise')
        self.app._on_analysis_selected()
        self.app.run_selected_analysis()

        text = self.app.analysis_text.get('1.0', 'end')
        self.assertIn('Noise analysis:', text)
        self.assertIn('global sigma', text)
        self.assertIn('note:', text)

    def test_a_report_needing_the_file_says_so_when_there_is_none(self):
        # The image was set directly in setUp, as an upload would be, so there
        # is no file for the metadata check to read
        self.app.source_path = None
        self.app.analysis_name.set('metadata')
        self.app._on_analysis_selected()
        self.app.run_selected_analysis()

        self.messagebox.showinfo.assert_called_once()
        self.assertEqual(self.app.analysis_text.get('1.0', 'end').strip(), '')

    def test_theme_switch_recolours_every_kind_of_widget(self):
        from src.gui.theme import LIGHT

        self.app.set_theme('light')
        self.assertEqual(self.app.palette, LIGHT)
        self.assertEqual(self.app.filter_list.cget('background'), LIGHT['field'])
        self.assertEqual(self.app.info_text.cget('background'), LIGHT['field'])
        self.assertEqual(self.app.viewer.canvas.cget('background'), LIGHT['canvas'])
        # The info panel is read-only, and has to stay that way afterwards
        self.assertEqual(str(self.app.info_text.cget('state')), 'disabled')

    def test_zoom_readout_follows_the_viewer(self):
        self.app._refresh()
        self.app._set_zoom(2.0)
        self.assertEqual(self.app.zoom_label.cget('text'), '200%')

    def test_preset_roundtrip_matches_the_cli_format(self):
        self._select('clahe')
        self.app.apply_filter()
        expected = self.app.pipeline.current.copy()

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'preset.json'
            self.app.pipeline.save_preset(str(path))
            preset = json.loads(path.read_text(encoding='utf-8'))

            self.assertEqual(preset['filters'][0]['name'], 'clahe')

            # Replay it through the plain pipeline, as the CLI would
            from src.filters import filter_function
            replayed = Pipeline(self.image)
            steps = [FilterStep.from_dict(s) for s in preset['filters']]
            replayed.replace_chain(steps, filter_function)

        np.testing.assert_array_equal(replayed.current, expected)

    def test_report_export(self):
        self._select('clahe')
        self.app.apply_filter()

        from src.core import ReportGenerator
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'report.md'
            ReportGenerator(self.app.pipeline.generate_report(),
                            self.app.metadata).save(str(path))
            self.assertIn('clahe', path.read_text(encoding='utf-8'))

    def test_view_modes_switch(self):
        for mode in ('processed', 'original', 'split', 'side by side'):
            with self.subTest(mode=mode):
                self.app._set_view(mode)
                self.assertEqual(self.app.viewer.mode.get(), mode)

    def test_info_panel_reports_the_source(self):
        self.app._refresh_info()
        text = self.app.info_text.get('1.0', 'end')
        self.assertIn('test.png', text)
        self.assertIn('filters', text)

    def test_pixel_readout_within_bounds(self):
        self.app._on_pixel(10, 10)
        self.assertIn('(10, 10)', self.app.pixel_label.cget('text'))

    def test_pixel_readout_outside_bounds_is_blank(self):
        self.app._on_pixel(9999, 9999)
        self.assertEqual(self.app.pixel_label.cget('text'), '')

    def test_reset_layout_gives_the_bottom_panel_height(self):
        self.app.deiconify()
        self.app.update()
        self.app.reset_layout()
        self.app.update_idletasks()

        bottom = self.app.nametowidget(self.app._outer.panes()[1])
        self.assertGreater(bottom.winfo_height(), 50)

    def test_apply_without_a_selected_filter_prompts_instead_of_applying(self):
        self.app._selected_filter = None
        self.app.apply_filter()
        self.assertEqual(len(self.app.pipeline), 0)
        self.messagebox.showinfo.assert_called_once()

    def test_missing_required_parameter_reports_instead_of_applying(self):
        self._select('roi_crop')   # x, y, width, height have no defaults
        self.app.apply_filter()
        self.assertEqual(len(self.app.pipeline), 0)
        self.messagebox.showerror.assert_called_once()

    def test_a_failing_filter_leaves_the_chain_untouched(self):
        self._select('levels')
        # black_point above white_point is rejected by the filter itself
        self.app.parameters._entries['black_point']['var'].set(200.0)
        self.app.parameters._entries['white_point']['var'].set(100.0)
        self.app.apply_filter()

        self.assertEqual(len(self.app.pipeline), 0)
        np.testing.assert_array_equal(self.app.pipeline.current, self.image)
        self.messagebox.showerror.assert_called_once()

    def test_actions_without_an_image_prompt_rather_than_crash(self):
        self.app.pipeline = None
        for action in (self.app.save_image_as, self.app.save_preset,
                       self.app.load_preset, self.app.export_report):
            with self.subTest(action=action.__name__):
                action()
        self.assertGreaterEqual(self.messagebox.showinfo.call_count, 4)


if __name__ == '__main__':
    unittest.main()
