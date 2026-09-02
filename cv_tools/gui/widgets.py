"""
Reusable widgets for the cv-tools GUI.

``ImageCanvas`` displays a processed image alongside its original, including
the split view forensic work relies on. ``ParameterPanel`` builds its controls
by introspecting a filter's signature, so every registered filter gets a usable
parameter form without one being written by hand.
"""

import inspect
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image, ImageTk

from ..utils.parsing import parse_value

# Parameter presentation metadata lives in utils, shared with the Streamlit
# dashboard, which cannot import this module because it imports tkinter.
# Re-exported here so existing ``from .widgets import ...`` callers still work.
from ..utils.params import (          # noqa: F401
    CHOICES,
    SLIDER_RANGES,
    _dynamic_choices,
    to_display,
)

VIEW_MODES = ('processed', 'original', 'split', 'side by side')


class ImageCanvas(ttk.Frame):
    """
    Scrollable image view with original/processed comparison.

    The split view puts the original left of a movable divider and the
    processed image right of it, which is how a change is judged - the eye
    compares far better across an edge than across a gap.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._original: Optional[np.ndarray] = None
        self._processed: Optional[np.ndarray] = None
        self._photo: Optional[ImageTk.PhotoImage] = None

        self.mode = tk.StringVar(value='processed')
        self.zoom = 1.0
        self.fit_to_window = True
        self._split = 0.5
        self._dragging_split = False

        self.canvas = tk.Canvas(self, bg='#1e1e20', highlightthickness=0,
                                cursor='crosshair')
        x_scroll = ttk.Scrollbar(self, orient='horizontal', command=self.canvas.xview)
        y_scroll = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)

        self.canvas.grid(row=0, column=0, sticky='nsew')
        y_scroll.grid(row=0, column=1, sticky='ns')
        x_scroll.grid(row=1, column=0, sticky='ew')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.canvas.bind('<Configure>', lambda _event: self.redraw())
        self.canvas.bind('<Button-1>', self._on_press)
        self.canvas.bind('<B1-Motion>', self._on_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_release)

        self.on_pixel: Optional[Callable[[int, int], None]] = None

    # ---- content ----

    def set_images(self, original: Optional[np.ndarray],
                   processed: Optional[np.ndarray]) -> None:
        """Replace the displayed pair and redraw."""
        self._original = original
        self._processed = processed
        self.redraw()

    def set_mode(self, mode: str) -> None:
        self.mode.set(mode)
        self.redraw()

    def set_zoom(self, zoom: Optional[float]) -> None:
        """Set an explicit zoom, or None to fit the window."""
        if zoom is None:
            self.fit_to_window = True
        else:
            self.fit_to_window = False
            self.zoom = max(0.05, min(16.0, zoom))
        self.redraw()

    # ---- rendering ----

    def _compose(self) -> Optional[np.ndarray]:
        """Build the image to display from the current mode."""
        if self._processed is None:
            return None

        processed = to_display(self._processed)
        original = to_display(self._original) if self._original is not None else processed

        mode = self.mode.get()
        if mode == 'processed':
            return processed
        if mode == 'original':
            return original

        # Comparison modes need a common size; a crop or resize step makes the
        # two differ, so pad both onto one canvas rather than distorting either
        height = max(original.shape[0], processed.shape[0])
        width = max(original.shape[1], processed.shape[1])

        def padded(img: np.ndarray) -> np.ndarray:
            canvas = np.zeros((height, width, 3), dtype=np.uint8)
            canvas[:img.shape[0], :img.shape[1]] = img
            return canvas

        left, right = padded(original), padded(processed)

        if mode == 'side by side':
            gap = np.full((height, 8, 3), 40, dtype=np.uint8)
            return np.hstack([left, gap, right])

        # split
        divider = int(np.clip(self._split, 0.0, 1.0) * width)
        composite = right.copy()
        composite[:, :divider] = left[:, :divider]
        if 0 < divider < width:
            composite[:, max(0, divider - 1):divider + 1] = (255, 200, 40)
        return composite

    def redraw(self) -> None:
        """Recompose and repaint."""
        self.canvas.delete('all')
        composite = self._compose()
        if composite is None:
            self.canvas.create_text(
                self.canvas.winfo_width() // 2 or 200,
                self.canvas.winfo_height() // 2 or 150,
                text='Open an image to begin  (Ctrl+O)',
                fill='#8a8a90', font=('Segoe UI', 11),
            )
            return

        height, width = composite.shape[:2]

        if self.fit_to_window:
            view_w = max(1, self.canvas.winfo_width())
            view_h = max(1, self.canvas.winfo_height())
            self.zoom = min(view_w / width, view_h / height, 1.0)

        display_w = max(1, int(width * self.zoom))
        display_h = max(1, int(height * self.zoom))

        # Nearest-neighbour when magnifying, so pixels are shown as they are
        # rather than smoothed into a guess
        interpolation = cv2.INTER_NEAREST if self.zoom >= 1.0 else cv2.INTER_AREA
        scaled = cv2.resize(composite, (display_w, display_h), interpolation=interpolation)

        self._photo = ImageTk.PhotoImage(Image.fromarray(scaled))
        self.canvas.create_image(0, 0, anchor='nw', image=self._photo)
        self.canvas.configure(scrollregion=(0, 0, display_w, display_h))

        if self.mode.get() in ('split', 'side by side'):
            for text, x in (('ORIGINAL', 8), ('PROCESSED', display_w // 2 + 8)):
                self.canvas.create_text(x, 8, text=text, anchor='nw',
                                        fill='#ffffff', font=('Segoe UI', 9, 'bold'))

    # ---- interaction ----

    def _to_image_coords(self, event) -> Tuple[int, int]:
        x = int(self.canvas.canvasx(event.x) / max(self.zoom, 1e-6))
        y = int(self.canvas.canvasy(event.y) / max(self.zoom, 1e-6))
        return x, y

    def _on_press(self, event) -> None:
        if self.mode.get() == 'split':
            self._dragging_split = True
            self._on_drag(event)
            return
        if self.on_pixel is not None and self._processed is not None:
            x, y = self._to_image_coords(event)
            self.on_pixel(x, y)

    def _on_drag(self, event) -> None:
        if not self._dragging_split or self._processed is None:
            return
        composite = self._compose()
        if composite is None:
            return
        width = composite.shape[1] * self.zoom
        self._split = float(np.clip(self.canvas.canvasx(event.x) / max(width, 1e-6), 0, 1))
        self.redraw()

    def _on_release(self, _event) -> None:
        self._dragging_split = False


class ParameterPanel(ttk.Frame):
    """
    A parameter form generated from a filter's signature.

    Introspection rather than hand-written forms: every registered filter gets
    a usable panel, and a filter added later needs no GUI work at all.
    """

    def __init__(self, master, on_change: Optional[Callable[[], None]] = None, **kwargs):
        super().__init__(master, **kwargs)
        self._on_change = on_change
        self._entries: Dict[str, Dict[str, Any]] = {}
        self._choices = dict(CHOICES)
        self._choices.update(_dynamic_choices())
        self._body: Optional[ttk.Frame] = None
        self.columnconfigure(0, weight=1)

    def clear(self) -> None:
        """Remove every control."""
        if self._body is not None:
            self._body.destroy()
            self._body = None
        self._entries = {}

    def build(self, spec, values: Optional[Dict[str, Any]] = None) -> None:
        """
        Build controls for a filter.

        Args:
            spec: A ``FilterSpec`` from the registry
            values: Existing parameter values to pre-fill, for editing a step
        """
        self.clear()
        values = values or {}

        self._body = ttk.Frame(self)
        self._body.grid(row=0, column=0, sticky='nsew')
        self._body.columnconfigure(1, weight=1)

        ttk.Label(self._body, text=spec.description, wraplength=250,
                  foreground='#4a4a52').grid(row=0, column=0, columnspan=2,
                                             sticky='w', pady=(0, 8))

        signature = inspect.signature(spec.fn)
        parameters = list(signature.parameters.values())[1:]   # skip `image`

        if not parameters:
            ttk.Label(self._body, text='No parameters.').grid(
                row=1, column=0, columnspan=2, sticky='w')
            return

        for row, parameter in enumerate(parameters, start=1):
            required = parameter.default is inspect.Parameter.empty
            default = values.get(
                parameter.name,
                '' if required else parameter.default,
            )
            label = parameter.name + (' *' if required else '')
            ttk.Label(self._body, text=label).grid(row=row, column=0, sticky='w',
                                                   padx=(0, 6), pady=2)
            self._add_control(self._body, row, parameter.name, default, required)

    def _add_control(self, parent, row: int, name: str, default: Any,
                     required: bool) -> None:
        """Create the control best suited to a parameter's type and name."""
        container = ttk.Frame(parent)
        container.grid(row=row, column=1, sticky='ew', pady=2)
        container.columnconfigure(0, weight=1)

        if isinstance(default, bool):
            variable = tk.BooleanVar(value=default)
            widget = ttk.Checkbutton(container, variable=variable,
                                     command=self._changed)
            widget.grid(row=0, column=0, sticky='w')
            self._entries[name] = {'kind': 'bool', 'var': variable}
            return

        if name in self._choices:
            variable = tk.StringVar(value='' if default is None else str(default))
            widget = ttk.Combobox(container, textvariable=variable, width=14,
                                  values=self._choices[name], state='normal')
            widget.grid(row=0, column=0, sticky='ew')
            widget.bind('<<ComboboxSelected>>', lambda _e: self._changed())
            self._entries[name] = {'kind': 'text', 'var': variable}
            return

        if isinstance(default, (int, float)) and name in SLIDER_RANGES:
            low, high = SLIDER_RANGES[name]
            variable = tk.DoubleVar(value=float(default))
            is_integer = isinstance(default, int)

            readout = ttk.Label(container, width=7)

            def update_readout(*_args):
                value = variable.get()
                readout.configure(text=f"{int(round(value))}" if is_integer
                                  else f"{value:.3g}")

            scale = ttk.Scale(container, from_=low, to=high, variable=variable,
                              command=lambda _v: update_readout())
            scale.grid(row=0, column=0, sticky='ew')
            readout.grid(row=0, column=1, padx=(4, 0))
            update_readout()
            scale.bind('<ButtonRelease-1>', lambda _e: self._changed())

            self._entries[name] = {'kind': 'int' if is_integer else 'float',
                                   'var': variable}
            return

        # Anything else - tuples, paths, unranged numbers, optional values
        text = '' if default is None or default == '' else (
            ','.join(str(v) for v in default) if isinstance(default, (tuple, list))
            else str(default)
        )
        variable = tk.StringVar(value=text)
        entry = ttk.Entry(container, textvariable=variable)
        entry.grid(row=0, column=0, sticky='ew')
        entry.bind('<Return>', lambda _e: self._changed())
        entry.bind('<FocusOut>', lambda _e: self._changed())
        self._entries[name] = {'kind': 'text', 'var': variable, 'required': required}

    def _changed(self) -> None:
        if self._on_change is not None:
            self._on_change()

    def get_params(self) -> Dict[str, Any]:
        """
        Collect the current values.

        Raises:
            ValueError: If a parameter with no default was left blank
        """
        params: Dict[str, Any] = {}

        for name, entry in self._entries.items():
            kind = entry['kind']

            if kind == 'bool':
                params[name] = bool(entry['var'].get())
            elif kind == 'int':
                params[name] = int(round(float(entry['var'].get())))
            elif kind == 'float':
                params[name] = round(float(entry['var'].get()), 4)
            else:
                text = entry['var'].get().strip()
                if not text:
                    if entry.get('required'):
                        raise ValueError(f"'{name}' is required")
                    continue
                params[name] = _parse_text(text)

        return params


def _parse_text(text: str) -> Any:
    """Parse an entry's text into a value, allowing comma-separated tuples."""
    if ',' in text:
        parts = [part.strip() for part in text.split(',')]
        parsed = [parse_value(part) for part in parts]
        # A flat list of four numbers is how corner sets are typed, and those
        # have to reach the filter as pairs
        if len(parsed) == 8 and all(isinstance(v, (int, float)) for v in parsed):
            return [[parsed[i], parsed[i + 1]] for i in range(0, 8, 2)]
        return parsed
    return parse_value(text)
