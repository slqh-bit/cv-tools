"""
cv-tools GUI.

    Left    filter chain, with reordering, plus the filter picker
    Centre  image viewer with original/processed comparison
    Right   parameters for the selected filter or chain step
    Bottom  histogram and metadata, and the analysis reports

The window is a view onto the same ``Pipeline`` the CLI drives, so a chain
built by clicking saves as a preset the CLI can replay, and vice versa. Nothing
here reimplements a filter, and the analysis tab reads the same
``ANALYSIS_REGISTRY`` the CLI prints from - so a report added there appears
here without this file being touched.
"""

import ctypes
import sys
import tkinter as tk
import traceback
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any, Dict, List, Optional

import numpy as np

from ..core import FilterStep, ImageLoader, Pipeline, ReportGenerator, save_image
from ..filters import (
    ANALYSIS_REGISTRY,
    CATEGORY_ORDER,
    Row,
    FILTER_REGISTRY,
    dynamic_range_used,
    filter_function,
    histogram_stats,
    render_histogram,
    render_report,
    resolve_analysis,
    resolve_filter,
    run_analysis,
)
from .theme import (
    FONT_BOLD,
    HISTOGRAM_BACKGROUND,
    PALETTES,
    apply_theme,
    listbox_options,
    text_options,
)
from .widgets import VIEW_MODES, ImageCanvas, ParameterPanel

REPORT_FORMATS = {'.json': 'json', '.pdf': 'pdf', '.md': 'markdown'}


def enable_dpi_awareness() -> None:
    """
    Ask Windows to hand us real pixels on a scaled display.

    Without this the OS renders the window at 96 DPI and bitmap-scales it up,
    which blurs exactly what this tool exists to show - the pixels. It also
    makes Tk's reported geometry match the screen's, so a 1:1 zoom really is
    one image pixel per screen pixel.

    A no-op off Windows, and on Windows versions without the API.
    """
    if sys.platform != 'win32':
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)   # per-monitor aware
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()    # older fallback
        except Exception:
            pass


class CVToolsApp(tk.Tk):
    """Main application window."""

    def __init__(self):
        enable_dpi_awareness()
        super().__init__()

        self.title('cv-tools')
        self.theme_name = tk.StringVar(value='dark')
        self.palette = apply_theme(self, self.theme_name.get())
        # Fit the screen rather than asking for a size it may not have: a
        # clamped request squeezes the bottom panel to nothing
        width = min(1280, self.winfo_screenwidth() - 80)
        height = min(820, self.winfo_screenheight() - 80)
        self.geometry(f'{width}x{height}')
        self.minsize(900, 600)

        self.pipeline: Optional[Pipeline] = None
        self.metadata: Dict[str, Any] = {}
        self.source_path: Optional[Path] = None
        self._selected_filter: Optional[str] = None
        # Index of the chain step being edited, when the parameter panel is
        # showing an applied step rather than a filter about to be added
        self._editing_step: Optional[int] = None
        # Registry name per filter-list row; None marks a family heading
        self._filter_rows: List[Optional[str]] = []
        self._layout_job: Optional[str] = None

        self._build_menu()
        self._build_layout()
        self._bind_keys()
        self._refresh()

    # ---- construction ----

    def _build_menu(self) -> None:
        menu = tk.Menu(self)

        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label='Open image...', accelerator='Ctrl+O',
                              command=self.open_image)
        file_menu.add_command(label='Save processed image...', accelerator='Ctrl+S',
                              command=self.save_image_as)
        file_menu.add_separator()
        file_menu.add_command(label='Load preset...', command=self.load_preset)
        file_menu.add_command(label='Save preset...', accelerator='Ctrl+Shift+S',
                              command=self.save_preset)
        file_menu.add_separator()
        file_menu.add_command(label='Export report...', command=self.export_report)
        file_menu.add_separator()
        file_menu.add_command(label='Quit', command=self.destroy)
        menu.add_cascade(label='File', menu=file_menu)

        edit_menu = tk.Menu(menu, tearoff=0)
        edit_menu.add_command(label='Undo', accelerator='Ctrl+Z', command=self.undo)
        edit_menu.add_command(label='Redo', accelerator='Ctrl+Y', command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label='Duplicate step', command=self.duplicate_step)
        edit_menu.add_command(label='Remove step', accelerator='Del',
                              command=self.remove_step)
        edit_menu.add_command(label='Reset chain', command=self.reset_chain)
        menu.add_cascade(label='Edit', menu=edit_menu)

        view_menu = tk.Menu(menu, tearoff=0)
        for mode in VIEW_MODES:
            view_menu.add_command(label=mode.title(),
                                  command=lambda m=mode: self._set_view(m))
        view_menu.add_separator()
        view_menu.add_command(label='Fit to window', command=lambda: self._set_zoom(None))
        view_menu.add_command(label='100%', command=lambda: self._set_zoom(1.0))
        view_menu.add_command(label='200%', command=lambda: self._set_zoom(2.0))
        view_menu.add_command(label='400%', command=lambda: self._set_zoom(4.0))
        view_menu.add_separator()
        theme_menu = tk.Menu(view_menu, tearoff=0)
        for name in PALETTES:
            theme_menu.add_radiobutton(label=name.title(), value=name,
                                       variable=self.theme_name,
                                       command=lambda n=name: self.set_theme(n))
        view_menu.add_cascade(label='Theme', menu=theme_menu)
        view_menu.add_command(label='Reset panel layout', command=self.reset_layout)
        menu.add_cascade(label='View', menu=view_menu)

        self.configure(menu=menu)

    def _build_layout(self) -> None:
        self._outer = ttk.PanedWindow(self, orient='vertical')
        self._outer.pack(fill='both', expand=True)

        self._upper = ttk.PanedWindow(self._outer, orient='horizontal')
        self._outer.add(self._upper, weight=4)

        self._upper.add(self._build_chain_panel(self._upper), weight=1)
        self._upper.add(self._build_viewer(self._upper), weight=4)
        self._upper.add(self._build_parameter_panel(self._upper), weight=1)

        self._outer.add(self._build_bottom_panel(self._outer), weight=1)

        self.status = ttk.Label(self, text='Ready', anchor='w', padding=(8, 4),
                                style='Status.TLabel')
        self.status.pack(fill='x', side='bottom')

        # A pane's initial size comes from what its contents ask for, not from
        # its weight, and the viewer asks for everything - which leaves the
        # bottom panel with no height at all. Place the sashes once the window
        # has a real size to divide.
        self._layout_job = self.after(60, self.reset_layout)

    def reset_layout(self) -> None:
        """Place the sashes proportionally. Safe to call at any time."""
        self._layout_job = None
        self.update_idletasks()

        height = self._outer.winfo_height()
        width = self._upper.winfo_width()
        if height <= 1 or width <= 1:
            # Not mapped yet; try again rather than dividing nothing
            self._layout_job = self.after(60, self.reset_layout)
            return

        try:
            self._outer.sashpos(0, int(height * 0.74))
            self._upper.sashpos(0, int(width * 0.22))
            self._upper.sashpos(1, int(width * 0.78))
        except tk.TclError:
            # The window can be torn down before this fires
            return

        self._refresh_histogram()

    def _build_chain_panel(self, master) -> ttk.Frame:
        frame = ttk.Frame(master, padding=8)

        ttk.Label(frame, text='Filter chain', style='Heading.TLabel').pack(anchor='w')

        self.chain_list = tk.Listbox(frame, exportselection=False, height=10,
                                     activestyle='none',
                                     **listbox_options(self.palette))
        self.chain_list.pack(fill='both', expand=True, pady=(6, 6))
        self.chain_list.bind('<<ListboxSelect>>', self._on_step_selected)
        self.chain_list.bind('<Delete>', lambda _e: self.remove_step())

        # Two by two rather than one row of four: the panel is the narrowest
        # in the window, and four buttons across it clip their own labels
        buttons = ttk.Frame(frame)
        buttons.pack(fill='x')
        for index, (text, command) in enumerate(
                (('Up', self.move_up), ('Down', self.move_down),
                 ('Duplicate', self.duplicate_step), ('Remove', self.remove_step))):
            row, column = divmod(index, 2)
            ttk.Button(buttons, text=text, width=1, command=command).grid(
                row=row, column=column, sticky='ew',
                padx=(0 if column == 0 else 3, 0), pady=(0 if row == 0 else 3, 0))
        buttons.columnconfigure(0, weight=1)
        buttons.columnconfigure(1, weight=1)

        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=10)

        ttk.Label(frame, text='Add filter', style='Heading.TLabel').pack(anchor='w')

        # Search and family narrow the same list, which is grouped by family
        # rather than sorted A-Z - the same order the dashboard and the filter
        # reference use, so a filter is looked up in one place in all three
        filters_row = ttk.Frame(frame)
        filters_row.pack(fill='x', pady=(6, 4))
        self.search = tk.StringVar()
        self.search.trace_add('write', lambda *_: self._refresh_filter_list())
        ttk.Entry(filters_row, textvariable=self.search).pack(fill='x')

        self.category = tk.StringVar(value='All')
        category_box = ttk.Combobox(filters_row, textvariable=self.category,
                                    values=['All'] + list(CATEGORY_ORDER),
                                    state='readonly')
        category_box.pack(fill='x', pady=(4, 0))
        category_box.bind('<<ComboboxSelected>>',
                          lambda _e: self._refresh_filter_list())

        self.filter_list = tk.Listbox(frame, exportselection=False, height=14,
                                      activestyle='none',
                                      **listbox_options(self.palette))
        self.filter_list.pack(fill='both', expand=True, pady=(4, 0))
        self.filter_list.bind('<<ListboxSelect>>', self._on_filter_selected)
        self.filter_list.bind('<Double-Button-1>', lambda _e: self.apply_filter())

        self._refresh_filter_list()
        return frame

    def _build_viewer(self, master) -> ttk.Frame:
        frame = ttk.Frame(master, padding=8)

        toolbar = ttk.Frame(frame)
        toolbar.pack(fill='x')

        ttk.Label(toolbar, text='View', style='Muted.TLabel').pack(side='left')
        self.view_mode = tk.StringVar(value='processed')
        view_box = ttk.Combobox(toolbar, textvariable=self.view_mode, width=13,
                                values=list(VIEW_MODES), state='readonly')
        view_box.pack(side='left', padx=(6, 14))
        view_box.bind('<<ComboboxSelected>>',
                      lambda _e: self._set_view(self.view_mode.get()))

        for text, zoom in (('Fit', None), ('100%', 1.0), ('200%', 2.0), ('400%', 4.0)):
            ttk.Button(toolbar, text=text, width=5,
                       command=lambda z=zoom: self._set_zoom(z)).pack(side='left', padx=1)

        self.zoom_label = ttk.Label(toolbar, text='', width=6, anchor='e',
                                    style='Muted.TLabel')
        self.zoom_label.pack(side='left', padx=(8, 0))

        self.pixel_label = ttk.Label(toolbar, text='', style='Muted.TLabel')
        self.pixel_label.pack(side='right')

        self.viewer = ImageCanvas(frame, palette=self.palette)
        self.viewer.pack(fill='both', expand=True, pady=(8, 0))
        self.viewer.on_pixel = self._on_pixel
        self.viewer.on_zoom = self._on_zoom

        return frame

    def _build_parameter_panel(self, master) -> ttk.Frame:
        frame = ttk.Frame(master, padding=8)

        self.parameter_title = ttk.Label(frame, text='Parameters',
                                         style='Heading.TLabel')
        self.parameter_title.pack(anchor='w')

        self.parameters = ParameterPanel(frame)
        self.parameters.pack(fill='both', expand=True, pady=(8, 8))

        self.apply_button = ttk.Button(frame, text='Apply filter',
                                       style='Accent.TButton',
                                       command=self.apply_filter)
        self.apply_button.pack(fill='x')

        # Selecting an applied step loads its parameters here, so a value can
        # be corrected in place instead of the step being removed and re-added
        self.update_button = ttk.Button(frame, text='Update selected step',
                                        command=self.update_step)
        self.update_button.pack(fill='x', pady=(4, 0))

        return frame

    def _build_bottom_panel(self, master) -> ttk.Frame:
        frame = ttk.Frame(master, style='Window.TFrame')

        self.bottom_tabs = ttk.Notebook(frame)
        self.bottom_tabs.pack(fill='both', expand=True)
        self.bottom_tabs.add(self._build_statistics_tab(self.bottom_tabs),
                             text='Statistics')
        self.bottom_tabs.add(self._build_analysis_tab(self.bottom_tabs),
                             text='Analysis')

        return frame

    def _build_statistics_tab(self, master) -> ttk.Frame:
        frame = ttk.Frame(master, padding=8)

        histogram_frame = ttk.Frame(frame)
        histogram_frame.pack(side='left', fill='both', expand=True)
        ttk.Label(histogram_frame, text='Histogram', style='Muted.TLabel').pack(
            anchor='w', pady=(0, 4))
        self.histogram_canvas = tk.Canvas(histogram_frame, height=150,
                                          bg=self._histogram_hex(),
                                          highlightthickness=0)
        self.histogram_canvas.pack(fill='both', expand=True)
        self._histogram_photo = None

        info_frame = ttk.Frame(frame)
        info_frame.pack(side='left', fill='both', expand=True, padx=(12, 0))
        ttk.Label(info_frame, text='Source and statistics', style='Muted.TLabel').pack(
            anchor='w', pady=(0, 4))
        self.info_text = tk.Text(info_frame, height=9, wrap='none',
                                 **text_options(self.palette))
        self.info_text.pack(fill='both', expand=True)
        self.info_text.configure(state='disabled')

        return frame

    def _build_analysis_tab(self, master) -> ttk.Frame:
        """
        The measurements that describe an image without changing it.

        Driven by ``ANALYSIS_REGISTRY``, so this panel shows the same reports
        the CLI prints - and a report added to the registry appears here with
        no work in this file.
        """
        frame = ttk.Frame(master, padding=8)

        controls = ttk.Frame(frame)
        controls.pack(side='left', fill='y')
        controls.configure(width=220)

        ttk.Label(controls, text='Report', style='Muted.TLabel').pack(anchor='w')
        self.analysis_name = tk.StringVar(value=next(iter(ANALYSIS_REGISTRY)))
        analysis_box = ttk.Combobox(controls, textvariable=self.analysis_name,
                                    values=list(ANALYSIS_REGISTRY), state='readonly',
                                    width=18)
        analysis_box.pack(fill='x', pady=(4, 4))
        analysis_box.bind('<<ComboboxSelected>>',
                          lambda _e: self._on_analysis_selected())

        # Above the parameters rather than below them: this panel is the
        # shortest in the window, and a button under a generated form is the
        # first thing to fall off the bottom of it
        self.analysis_button = ttk.Button(controls, text='Run report',
                                          style='Accent.TButton',
                                          command=self.run_selected_analysis)
        self.analysis_button.pack(fill='x', pady=(0, 6))

        self.analysis_params = ParameterPanel(controls)
        self.analysis_params.pack(fill='both', expand=True)

        output_frame = ttk.Frame(frame)
        output_frame.pack(side='left', fill='both', expand=True, padx=(12, 0))
        self.analysis_text = tk.Text(output_frame, height=9, wrap='word',
                                     **text_options(self.palette))
        scroll = ttk.Scrollbar(output_frame, orient='vertical',
                               command=self.analysis_text.yview)
        self.analysis_text.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        self.analysis_text.pack(side='left', fill='both', expand=True)
        self._configure_analysis_tags()
        self.analysis_text.configure(state='disabled')

        self._on_analysis_selected()
        return frame

    def _histogram_hex(self) -> str:
        """The chart's own background, as a Tk colour for the canvas behind it."""
        return '#%02x%02x%02x' % HISTOGRAM_BACKGROUND

    def _configure_analysis_tags(self) -> None:
        """Colour the report rows by severity, from the current palette."""
        self.analysis_text.tag_configure('header', foreground=self.palette['accent'],
                                         font=FONT_BOLD, spacing1=6)
        self.analysis_text.tag_configure('flag', foreground=self.palette['flag'])
        self.analysis_text.tag_configure('info', foreground=self.palette['muted'])
        self.analysis_text.tag_configure('label', foreground=self.palette['muted'])

    def _bind_keys(self) -> None:
        self.bind('<Control-o>', lambda _e: self.open_image())
        self.bind('<Control-s>', lambda _e: self.save_image_as())
        self.bind('<Control-S>', lambda _e: self.save_preset())
        self.bind('<Control-z>', lambda _e: self.undo())
        self.bind('<Control-y>', lambda _e: self.redo())

    # ---- filter list ----

    def _refresh_filter_list(self) -> None:
        query = self.search.get().strip().lower()
        wanted = self.category.get()

        self.filter_list.delete(0, 'end')
        self._filter_rows = []

        for category in CATEGORY_ORDER:
            if wanted != 'All' and wanted != category:
                continue

            names = sorted(name for name, spec in FILTER_REGISTRY.items()
                           if spec.category == category
                           and (not query
                                or query in name.lower()
                                or query in spec.description.lower()))
            if not names:
                continue

            # A heading is a row like any other as far as Tk is concerned, so
            # it is greyed out here and refused on selection below
            self.filter_list.insert('end', f'  {category.upper()}')
            self.filter_list.itemconfigure('end', foreground=self.palette['muted'],
                                           selectbackground=self.palette['panel'],
                                           selectforeground=self.palette['muted'])
            self._filter_rows.append(None)

            for name in names:
                self.filter_list.insert('end', f'    {name}')
                self._filter_rows.append(name)

        if not self._filter_rows:
            self.filter_list.insert('end', '  no matching filters')
            self.filter_list.itemconfigure('end', foreground=self.palette['muted'])
            self._filter_rows.append(None)

    def _on_filter_selected(self, _event=None) -> None:
        selection = self.filter_list.curselection()
        if not selection:
            return

        name = self._filter_rows[selection[0]]
        if name is None:                      # a family heading, not a filter
            self.filter_list.selection_clear(selection[0])
            return

        self._selected_filter = name
        self._editing_step = None
        self.chain_list.selection_clear(0, 'end')

        spec = resolve_filter(name)
        self.parameter_title.configure(text=f'Parameters - {name}')
        self.parameters.build(spec)
        self._refresh_buttons()

    # ---- chain steps ----

    def _on_step_selected(self, _event=None) -> None:
        """Load the selected step's own parameters, ready to be corrected."""
        index = self._selected_step()
        if index is None or index >= len(self.pipeline.chain):
            self._refresh_buttons()
            return

        step = self.pipeline.chain[index]
        try:
            spec = resolve_filter(step.name)
        except KeyError:
            self._refresh_buttons()
            return

        self._selected_filter = step.name
        self._editing_step = index
        self.parameter_title.configure(text=f'Step {index + 1} - {step.name}')
        self.parameters.build(spec, values=step.params)
        self._refresh_buttons()

    # ---- actions ----

    def open_image(self) -> None:
        path = filedialog.askopenfilename(
            title='Open image',
            filetypes=[
                ('Images', '*.png *.jpg *.jpeg *.jfif *.bmp *.tif *.tiff *.webp'),
                ('Camera raw', '*.cr2 *.cr3 *.nef *.arw *.dng *.orf *.rw2 *.raf'),
                ('Video', '*.mp4 *.avi *.mkv *.mov'),
                ('All files', '*.*'),
            ],
        )
        if not path:
            return

        try:
            with ImageLoader(path) as loader:
                image = loader.load()
                self.metadata = loader.metadata
        except Exception as exc:
            messagebox.showerror('Could not open', str(exc))
            return

        self.source_path = Path(path)
        self.pipeline = Pipeline(image)
        self._set_status(f'Opened {self.source_path.name} '
                         f'({image.shape[1]}x{image.shape[0]})')
        self._refresh()

    def apply_filter(self) -> None:
        if not self._require_image():
            return
        if self._selected_filter is None:
            messagebox.showinfo('No filter selected',
                                'Choose a filter from the list first.')
            return

        spec = resolve_filter(self._selected_filter)
        try:
            params = self.parameters.get_params()
        except ValueError as exc:
            messagebox.showerror('Missing parameter', str(exc))
            return

        self._busy(True)
        try:
            self.pipeline.apply(spec.fn, spec.name, spec.module, params)
            self._editing_step = None
            self._set_status(f'Applied {spec.name}')
        except Exception as exc:
            messagebox.showerror('Filter failed', str(exc))
            self._set_status(f'{spec.name} failed')
        finally:
            self._busy(False)

        self._refresh()

    def remove_step(self) -> None:
        index = self._selected_step()
        if index is None:
            return
        chain = self.pipeline.chain
        del chain[index]
        self._rebuild(chain, f'Removed step {index + 1}')

    def move_up(self) -> None:
        index = self._selected_step()
        if index is None or index == 0:
            return
        chain = self.pipeline.chain
        chain[index - 1], chain[index] = chain[index], chain[index - 1]
        self._rebuild(chain, 'Reordered chain', select=index - 1)

    def move_down(self) -> None:
        index = self._selected_step()
        if index is None or index >= len(self.pipeline.chain) - 1:
            return
        chain = self.pipeline.chain
        chain[index + 1], chain[index] = chain[index], chain[index + 1]
        self._rebuild(chain, 'Reordered chain', select=index + 1)

    def duplicate_step(self) -> None:
        """Repeat a step in place - a second pass of the same filter."""
        index = self._selected_step()
        if index is None:
            return
        chain = self.pipeline.chain
        step = chain[index]
        chain.insert(index + 1, FilterStep(step.name, step.module, dict(step.params)))
        self._rebuild(chain, f'Duplicated step {index + 1}', select=index + 1)

    def update_step(self) -> None:
        """Re-apply the selected step with the parameters now in the panel."""
        index = self._editing_step
        if index is None or self.pipeline is None:
            return
        if index >= len(self.pipeline.chain):
            self._editing_step = None
            return

        try:
            params = self.parameters.get_params()
        except ValueError as exc:
            messagebox.showerror('Missing parameter', str(exc))
            return

        chain = self.pipeline.chain
        step = chain[index]
        chain[index] = FilterStep(step.name, step.module, params)
        # Everything after it is re-processed from the original, so a change
        # to an early step shows through the whole chain
        self._rebuild(chain, f'Updated step {index + 1}', select=index)

    def _rebuild(self, chain: List[FilterStep], message: str,
                 select: Optional[int] = None) -> None:
        """Re-process from the original with a modified chain."""
        self._busy(True)
        try:
            self.pipeline.replace_chain(chain, filter_function)
            self._set_status(message)
        except Exception as exc:
            # replace_chain restores the previous state on failure, so the
            # pipeline is still the one that worked
            messagebox.showerror('Could not rebuild chain', str(exc))
        finally:
            self._busy(False)

        self._refresh()
        if select is not None and 0 <= select < self.chain_list.size():
            self.chain_list.selection_set(select)
            self._refresh_buttons()

    def undo(self) -> None:
        if self.pipeline is not None and self.pipeline.undo() is not None:
            self._set_status('Undo')
            self._refresh()

    def redo(self) -> None:
        if self.pipeline is not None and self.pipeline.redo() is not None:
            self._set_status('Redo')
            self._refresh()

    def reset_chain(self) -> None:
        if self.pipeline is None:
            return
        self.pipeline.reset()
        self._set_status('Chain cleared')
        self._refresh()

    def save_image_as(self) -> None:
        if not self._require_image():
            return

        path = filedialog.asksaveasfilename(
            title='Save processed image', defaultextension='.png',
            filetypes=[('PNG', '*.png'), ('JPEG', '*.jpg'), ('TIFF', '*.tif')],
        )
        if not path:
            return

        try:
            save_image(self.pipeline.current, path)
            self._set_status(f'Saved {Path(path).name}')
        except OSError as exc:
            messagebox.showerror('Could not save', str(exc))

    def save_preset(self) -> None:
        if not self._require_image():
            return
        path = filedialog.asksaveasfilename(
            title='Save preset', defaultextension='.json',
            filetypes=[('JSON preset', '*.json')])
        if not path:
            return
        self.pipeline.save_preset(path)
        self._set_status(f'Saved preset {Path(path).name}')

    def load_preset(self) -> None:
        if not self._require_image():
            return
        path = filedialog.askopenfilename(
            title='Load preset', filetypes=[('JSON preset', '*.json')])
        if not path:
            return

        try:
            preset = self.pipeline.load_preset(path)
            steps = [FilterStep.from_dict(step) for step in preset.get('filters', [])]
        except Exception as exc:
            messagebox.showerror('Could not read preset', str(exc))
            return

        self._rebuild(steps, f'Loaded preset {Path(path).name}')

    def export_report(self) -> None:
        if not self._require_image():
            return

        path = filedialog.asksaveasfilename(
            title='Export report', defaultextension='.md',
            filetypes=[('Markdown', '*.md'), ('PDF', '*.pdf'), ('JSON', '*.json')])
        if not path:
            return

        report = ReportGenerator(self.pipeline.generate_report(), self.metadata)
        fmt = REPORT_FORMATS.get(Path(path).suffix.lower(), 'markdown')
        try:
            report.save(path, format=fmt)
            self._set_status(f'Exported {Path(path).name}')
        except Exception as exc:
            messagebox.showerror('Could not export', str(exc))

    # ---- analysis ----

    def _on_analysis_selected(self) -> None:
        spec = resolve_analysis(self.analysis_name.get())
        self.analysis_params.build(spec)

    def run_selected_analysis(self) -> None:
        """Run the selected report and show it, severity by severity."""
        if not self._require_image():
            return

        spec = resolve_analysis(self.analysis_name.get())
        try:
            params = self.analysis_params.get_params()
        except ValueError as exc:
            messagebox.showerror('Missing parameter', str(exc))
            return

        if spec.needs_path and self.source_path is None:
            messagebox.showinfo(
                'No source file',
                f"'{spec.name}' reads the file itself rather than the pixels, so "
                f"it needs an image opened from disk.")
            return

        self._busy(True)
        self._set_status(f'Running {spec.name}...')
        try:
            report = run_analysis(spec, image=self.pipeline.current,
                                  path=self.source_path, params=params)
        except Exception as exc:
            messagebox.showerror('Analysis failed', str(exc))
            self._set_status(f'{spec.name} failed')
            return
        finally:
            self._busy(False)

        self._show_analysis(render_report(spec, report))
        self._set_status(f'Ran {spec.name}')

    def _show_analysis(self, rows: List[Row]) -> None:
        self.analysis_text.configure(state='normal')
        self.analysis_text.delete('1.0', 'end')

        for row in rows:
            if row.indent < 0:                      # the report's header line
                self.analysis_text.insert('end', f'{row.value}\n', 'header')
                continue

            pad = '    ' * (row.indent + 1)
            if row.label:
                self.analysis_text.insert('end', f'{pad}{row.label}: ', 'label')
                self.analysis_text.insert('end', f'{row.value}\n', row.severity)
            else:
                self.analysis_text.insert('end', f'{pad}{row.value}\n', row.severity)

        self.analysis_text.configure(state='disabled')

    # ---- view ----

    def set_theme(self, name: str) -> None:
        """Restyle every widget, including the ones ttk does not reach."""
        self.theme_name.set(name)
        self.palette = apply_theme(self, name)

        for listbox in (self.chain_list, self.filter_list):
            listbox.configure(**listbox_options(self.palette))
        for text in (self.info_text, self.analysis_text):
            state = text.cget('state')
            text.configure(state='normal', **text_options(self.palette))
            text.configure(state=state)

        self._configure_analysis_tags()
        self.viewer.palette = self.palette
        self.viewer.canvas.configure(bg=self.palette['canvas'])
        self.histogram_canvas.configure(bg=self._histogram_hex())

        self._refresh_filter_list()
        self._refresh()
        self._set_status(f'{name.title()} theme')

    def _set_view(self, mode: str) -> None:
        self.view_mode.set(mode)
        self.viewer.set_mode(mode)

    def _set_zoom(self, zoom: Optional[float]) -> None:
        self.viewer.set_zoom(zoom)

    def _on_zoom(self, zoom: float) -> None:
        self.zoom_label.configure(text=f'{zoom * 100:.0f}%')

    def _on_pixel(self, x: int, y: int) -> None:
        if self.pipeline is None:
            return
        image = self.pipeline.current
        if not (0 <= y < image.shape[0] and 0 <= x < image.shape[1]):
            self.pixel_label.configure(text='')
            return

        value = image[y, x]
        text = f"({x}, {y})  " + (
            f"L {int(value)}" if np.isscalar(value) or value.ndim == 0
            else ' '.join(f"{c}{int(v)}" for c, v in zip('RGBA', np.atleast_1d(value)))
        )
        self.pixel_label.configure(text=text)

    # ---- refresh ----

    def _refresh(self) -> None:
        self._refresh_chain()
        self._refresh_viewer()
        self._refresh_histogram()
        self._refresh_info()
        self._refresh_buttons()

    def _refresh_chain(self) -> None:
        self.chain_list.delete(0, 'end')
        if self.pipeline is None:
            return
        for index, step in enumerate(self.pipeline.chain, start=1):
            summary = ', '.join(f"{k}={v}" for k, v in step.params.items())
            label = f"{index}. {step.name}"
            if summary:
                label += f"  ({summary[:40]}{'...' if len(summary) > 40 else ''})"
            self.chain_list.insert('end', label)

    def _refresh_viewer(self) -> None:
        if self.pipeline is None:
            self.viewer.set_images(None, None)
            return
        original, current = self.pipeline.compare()
        self.viewer.set_images(original, current)

    def _refresh_histogram(self) -> None:
        self.histogram_canvas.delete('all')
        if self.pipeline is None:
            return

        width = max(self.histogram_canvas.winfo_width(), 320)
        height = max(self.histogram_canvas.winfo_height(), 120)

        try:
            chart = render_histogram(self.pipeline.current, width=width, height=height,
                                     background=HISTOGRAM_BACKGROUND)
        except ValueError:
            return

        from PIL import Image, ImageTk
        self._histogram_photo = ImageTk.PhotoImage(Image.fromarray(chart))
        self.histogram_canvas.create_image(0, 0, anchor='nw',
                                           image=self._histogram_photo)

    def _refresh_info(self) -> None:
        self.info_text.configure(state='normal')
        self.info_text.delete('1.0', 'end')

        if self.pipeline is None:
            self.info_text.insert('end', 'No image loaded.\n')
            self.info_text.configure(state='disabled')
            return

        lines = []
        for key in ('filename', 'format', 'width', 'height', 'filesize_bytes'):
            if key in self.metadata:
                lines.append(f"{key:<16}{self.metadata[key]}")
        if 'sha256' in self.metadata:
            lines.append(f"{'sha256':<16}{self.metadata['sha256'][:32]}...")

        current = self.pipeline.current
        lines.append(f"{'shape':<16}{current.shape}")
        lines.append(f"{'filters':<16}{len(self.pipeline)}")

        try:
            stats = histogram_stats(current)
            lines.append(f"{'range used':<16}{dynamic_range_used(current) * 100:.1f}%")
            for name, values in stats['channels'].items():
                clipped = values['clipped_shadows_pct'] + values['clipped_highlights_pct']
                lines.append(
                    f"{name:<16}mean {values['mean']:6.1f}  std {values['std']:5.1f}"
                    f"  clipped {clipped:.2f}%"
                )
        except ValueError:
            pass

        self.info_text.insert('end', '\n'.join(lines))
        self.info_text.configure(state='disabled')

    def _refresh_buttons(self) -> None:
        has_image = self.pipeline is not None
        self.apply_button.configure(
            state='normal' if has_image and self._selected_filter else 'disabled')
        self.update_button.configure(
            state='normal' if has_image and self._editing_step is not None
            else 'disabled')
        self.analysis_button.configure(state='normal' if has_image else 'disabled')

    # ---- helpers ----

    def _selected_step(self) -> Optional[int]:
        if self.pipeline is None:
            return None
        selection = self.chain_list.curselection()
        return selection[0] if selection else None

    def _require_image(self) -> bool:
        if self.pipeline is None:
            messagebox.showinfo('No image', 'Open an image first.')
            return False
        return True

    def _busy(self, busy: bool) -> None:
        self.configure(cursor='watch' if busy else '')
        self.update_idletasks()

    def _set_status(self, message: str) -> None:
        self.status.configure(text=message)

    def destroy(self) -> None:
        """Cancel any pending callback before the widgets it names disappear."""
        if self._layout_job is not None:
            try:
                self.after_cancel(self._layout_job)
            except tk.TclError:
                pass
            self._layout_job = None
        super().destroy()


def main(argv: Optional[List[str]] = None) -> int:
    """
    Launch the GUI.

    Args:
        argv: Optional command line; a single path is opened at startup

    Returns:
        Process exit code
    """
    app = CVToolsApp()

    if argv:
        path = Path(argv[0])
        if path.exists():
            try:
                with ImageLoader(path) as loader:
                    image = loader.load()
                    app.metadata = loader.metadata
                app.source_path = path
                app.pipeline = Pipeline(image)
                app._set_status(f'Opened {path.name}')
                app._refresh()
            except Exception:
                traceback.print_exc()

    app.mainloop()
    return 0
