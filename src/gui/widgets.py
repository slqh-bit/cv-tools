"""
Reusable widgets for the cv-tools GUI.

``ImageCanvas`` displays a processed image alongside its original, including
the split view forensic work relies on, and reports the region dragged out on
it. ``ParameterPanel`` builds its controls by introspecting a filter's
signature, so every registered filter gets a usable parameter form without one
being written by hand, and fills a dragged region into it.
"""

import inspect
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image, ImageTk

from ..utils.compare import difference_map
from ..utils.parsing import parse_value
from .theme import DARK, FONT_BOLD

# Sliders need a range, and a signature does not carry one. These cover the
# numeric parameters that recur across the filter set; anything unlisted falls
# back to a plain entry box, which still accepts any value.
SLIDER_RANGES: Dict[str, Tuple[float, float]] = {
    'alpha': (0.0, 1.0),
    'amount': (0.0, 3.0),
    'amplify': (0.1, 10.0),
    'aggressiveness': (0.1, 3.0),
    'angle': (-180.0, 180.0),
    'black_point': (0.0, 255.0),
    'blur_radius': (0.1, 50.0),
    'blur_sigma': (0.0, 10.0),
    'brightness': (-255.0, 255.0),
    'clip_limit': (0.1, 10.0),
    'contrast': (0.0, 3.0),
    'cutoff': (1.0, 200.0),
    'cutoff_high': (1.0, 200.0),
    'factor': (0.0, 3.0),
    'gain': (0.1, 10.0),
    'gamma': (0.1, 3.0),
    'h': (1.0, 50.0),
    'h_color': (1.0, 50.0),
    'high_threshold': (0.0, 255.0),
    'hue_center': (0.0, 360.0),
    'hue_range': (1.0, 180.0),
    'k1': (-1.0, 1.0),
    'k2': (-1.0, 1.0),
    'length': (1.0, 64.0),
    'length_units': (1.0, 1000.0),
    'low_threshold': (0.0, 255.0),
    'noise_power': (0.0001, 0.5),
    'notch_radius': (1.0, 20.0),
    'output_black': (0.0, 255.0),
    'output_white': (0.0, 255.0),
    'percentile': (50.0, 100.0),
    'pixel_aspect': (0.25, 4.0),
    'quality': (1.0, 100.0),
    'radius': (0.1, 50.0),
    'scale': (0.1, 8.0),
    'sigma': (0.01, 1.0),
    'sigma_color': (1.0, 200.0),
    'sigma_r': (0.01, 1.0),
    'sigma_s': (1.0, 200.0),
    'sigma_space': (1.0, 200.0),
    'strength': (0.0, 2.0),
    'temperature': (-100.0, 100.0),
    'threshold': (0.0, 255.0),
    'tint': (-100.0, 100.0),
    'white_point': (0.0, 255.0),
    'zoom': (0.5, 3.0),
}

# String parameters with a fixed set of valid values
CHOICES: Dict[str, List[str]] = {
    'border_mode': ['constant', 'replicate', 'reflect', 'wrap'],
    'channel': ['', 'r', 'g', 'b'],
    'color_mode': ['lab', 'hsv', 'yuv', 'channelwise', 'luminance', 'grayscale'],
    'direction': ['horizontal', 'vertical', 'both'],
    'filter_type': ['lowpass', 'highpass', 'bandpass'],
    'interpolation': ['auto', 'nearest', 'bilinear', 'bicubic', 'lanczos', 'area'],
    'method': ['fill', 'noise', 'blur', 'pixelate', 'gray_world', 'white_patch',
               'shades_of_gray', 'luminance', 'average', 'lightness', 'max', 'min',
               'nearest', 'bilinear', 'bicubic', 'lanczos'],
    'mode': ['pad', 'crop', 'stretch'],
    'position': ['bottom_right', 'bottom_left', 'top_right', 'top_left'],
    'scale_axis': ['width', 'height'],
    'shape': ['rectangle', 'circle', 'ellipse', 'line', 'polygon'],
}

VIEW_MODES = ('processed', 'original', 'split', 'side by side', 'difference')

# The rubber band drawn while dragging a region out of the image, and the
# smallest drag that counts as one rather than as a click
SELECTION_COLOR = '#ffc832'
MIN_REGION = 4

# Picked points are drawn on the canvas, so they need a colour that survives
# both a dark frame and a blown-out window
PICK_COLOR = '#4dd2ff'
PICK_RADIUS = 6


def _dynamic_choices() -> Dict[str, List[str]]:
    """Choice lists that come from the filter modules' own constants."""
    from ..filters.aspect_ratio import PIXEL_ASPECT_RATIOS
    from ..filters.color_deconvolution import STAIN_PRESETS
    from ..filters.component_separation import COLOR_SPACES
    from ..filters.curves import CURVE_PRESETS

    return {
        'preset': sorted(set(CURVE_PRESETS) | set(STAIN_PRESETS)),
        'space': sorted(COLOR_SPACES),
        'format_name': sorted(PIXEL_ASPECT_RATIOS),
    }


def choices_for(spec) -> Dict[str, List[str]]:
    """
    Valid values per parameter, narrowed to the filter being configured.

    CHOICES is one map for every filter, so a name that means different things
    to two filters ends up holding the union - and offering a user the half
    their filter rejects. ``color_mode`` is the case that bites: CLAHE
    implements 'luminance' and not 'grayscale', histogram equalization the
    reverse, and a shared list offers both to both.

    Args:
        spec: A ``FilterSpec`` or ``AnalysisSpec``

    Returns:
        The choice map, with the entries this filter narrows replaced
    """
    from ..filters.aspect_ratio import INTERPOLATIONS as ASPECT_INTERPOLATIONS
    from ..filters.clahe import COLOR_MODES as CLAHE_MODES
    from ..filters.registry import filters_with_all_defaults
    from ..filters.color_deconvolution import STAIN_PRESETS
    from ..filters.component_separation import COLOR_SPACES
    from ..filters.curves import CURVE_PRESETS
    from ..filters.fisheye_correction import BORDER_MODES as FISHEYE_BORDERS
    from ..filters.histogram_equalization import COLOR_MODES as HISTEQ_MODES
    from ..filters.redaction import IRREVERSIBLE_METHODS, REVERSIBLE_METHODS
    from ..filters.saturation import DESATURATE_METHODS
    from ..filters.super_resolution import METHODS as UPSCALE_METHODS
    from ..filters.white_balance import METHODS as WHITE_BALANCE_METHODS

    merged = dict(CHOICES)
    merged.update(_dynamic_choices())

    # 'method' is the worst of them: four filters use the name for four
    # unrelated vocabularies, so the shared list is their union and every one
    # of the four is offered the other three's values
    narrowed = {
        'clahe': {'color_mode': list(CLAHE_MODES)},
        'roi_filter': {'filter_name': filters_with_all_defaults()},
        'clahe_grid': {'color_mode': list(CLAHE_MODES)},
        'histeq': {'color_mode': list(HISTEQ_MODES)},
        'redact': {'method': sorted(IRREVERSIBLE_METHODS | REVERSIBLE_METHODS)},
        'white_balance': {'method': list(WHITE_BALANCE_METHODS)},
        'desaturate': {'method': list(DESATURATE_METHODS)},
        'upscale': {'method': list(UPSCALE_METHODS)},
        'pixel_aspect': {'interpolation': list(ASPECT_INTERPOLATIONS)},
        'fit_aspect': {'interpolation': list(ASPECT_INTERPOLATIONS)},
        'barrel': {'border_mode': list(FISHEYE_BORDERS)},
        'fisheye': {'border_mode': list(FISHEYE_BORDERS)},
    }

    name = getattr(spec, 'name', '')
    if name in narrowed:
        merged.update(narrowed[name])
    elif name == 'component':
        # Channel names belong to the chosen colour space, and are matched
        # case-sensitively; the global r/g/b list cannot drive this at all
        names: List[str] = []
        for _code, channels in COLOR_SPACES.values():
            names.extend(channels)
        merged['channel'] = sorted(dict.fromkeys(names))
    elif name == 'curves':
        merged['preset'] = [''] + sorted(CURVE_PRESETS)
    elif name == 'stain':
        merged['preset'] = sorted(STAIN_PRESETS)

    return merged


def to_display(image: np.ndarray) -> np.ndarray:
    """Normalize any filter output to 3-channel uint8 RGB for display."""
    img = image
    if img.dtype != np.uint8:
        img = np.clip(img, 0, 255).astype(np.uint8)
    if img.ndim == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    if img.shape[2] == 1:
        return cv2.cvtColor(img[:, :, 0], cv2.COLOR_GRAY2RGB)
    if img.shape[2] == 4:
        return img[:, :, :3]
    return img


def side_by_side(original: np.ndarray, processed: np.ndarray, gap: int = 8) -> np.ndarray:
    """Pad both images onto a common canvas and place them side by side."""
    original = to_display(original)
    processed = to_display(processed)

    height = max(original.shape[0], processed.shape[0])
    width = max(original.shape[1], processed.shape[1])

    def padded(img: np.ndarray) -> np.ndarray:
        canvas = np.zeros((height, width, 3), dtype=np.uint8)
        canvas[:img.shape[0], :img.shape[1]] = img
        return canvas

    divider = np.full((height, gap, 3), 40, dtype=np.uint8)
    return np.hstack([padded(original), divider, padded(processed)])


class ImageCanvas(ttk.Frame):
    """
    Scrollable image view with original/processed comparison.

    The split view puts the original left of a movable divider and the
    processed image right of it, which is how a change is judged - the eye
    compares far better across an edge than across a gap.
    """

    def __init__(self, master, palette: Optional[Dict[str, str]] = None, **kwargs):
        super().__init__(master, **kwargs)

        self.palette = palette or DARK
        self._original: Optional[np.ndarray] = None
        self._processed: Optional[np.ndarray] = None
        self._photo: Optional[ImageTk.PhotoImage] = None

        self.mode = tk.StringVar(value='processed')
        self.zoom = 1.0
        self.fit_to_window = True
        self._split = 0.5
        self._dragging_split = False
        self._display_size = (1, 1)
        self._region_start = None
        self._region_item = None
        # Point picking: the labels still to be collected, and what has been
        # collected so far. Empty means ordinary click-and-drag behaviour.
        self._pick_queue = []
        self._picked = []

        self.canvas = tk.Canvas(self, bg=self.palette['canvas'], highlightthickness=0,
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
        # Ctrl+wheel zooms, plain wheel scrolls - the convention every image
        # viewer uses, and the only way to zoom without leaving the image
        self.canvas.bind('<Control-MouseWheel>', self._on_wheel_zoom)
        self.canvas.bind('<MouseWheel>', self._on_wheel_scroll)
        self.canvas.bind('<Shift-MouseWheel>', self._on_wheel_pan)

        self.on_pixel: Optional[Callable[[int, int], None]] = None
        self.on_zoom: Optional[Callable[[float], None]] = None
        self.on_region: Optional[Callable[[int, int, int, int], None]] = None
        # Called with (label, remaining) after each pick, and with the full
        # list of (x, y) once the queue empties
        self.on_pick_progress: Optional[Callable[[str, int], None]] = None
        self.on_picks_complete: Optional[Callable[[List[Tuple[int, int]]], None]] = None
        # Peak, mean and scale of the last difference view drawn, so the
        # status bar can quote numbers the picture cannot carry
        self.difference_stats: Optional[Dict[str, float]] = None

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

        if mode == 'difference':
            # The map carries its own scale factor and true peak, so the view
            # cannot be read as showing more change than there was
            composite, self.difference_stats = difference_map(left, right)
            return composite

        if mode == 'side by side':
            return side_by_side(left, right)

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
                fill=self.palette['muted'], font=('Segoe UI', 11),
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
        self._display_size = (display_w, display_h)

        if self.on_zoom is not None:
            self.on_zoom(self.zoom)

        self._draw_picks()

        if self.mode.get() in ('split', 'side by side'):
            for text, x in (('ORIGINAL', 8), ('PROCESSED', display_w // 2 + 8)):
                # Drawn on the image, so these stay white in either theme
                self.canvas.create_text(x + 1, 9, text=text, anchor='nw',
                                        fill='#000000', font=FONT_BOLD)
                self.canvas.create_text(x, 8, text=text, anchor='nw',
                                        fill='#ffffff', font=FONT_BOLD)

    # ---- point picking ----

    @property
    def picking(self) -> bool:
        """Whether clicks are currently collecting points rather than dragging."""
        return bool(self._pick_queue)

    def start_picking(self, labels: List[str]) -> None:
        """
        Collect one point per label, in order, from clicks on the image.

        Typing four corner coordinates read off a hover readout is the slowest
        thing this window asks of anyone, and the numbers are on the image
        already. The labels drive the prompt so the user is told which point
        is wanted next rather than having to remember the order.
        """
        self._pick_queue = list(labels)
        self._picked = []
        self.canvas.configure(cursor='tcross')
        self.redraw()
        if self.on_pick_progress is not None and self._pick_queue:
            self.on_pick_progress(self._pick_queue[0], len(self._pick_queue))

    def cancel_picking(self) -> None:
        """Abandon a pick in progress, keeping nothing."""
        self._pick_queue = []
        self._picked = []
        self.canvas.configure(cursor='crosshair')
        self.redraw()

    def _record_pick(self, x: int, y: int) -> None:
        """Take one point, and finish if it was the last one wanted."""
        self._picked.append((x, y))
        self._pick_queue.pop(0)
        self.redraw()

        if self._pick_queue:
            if self.on_pick_progress is not None:
                self.on_pick_progress(self._pick_queue[0], len(self._pick_queue))
            return

        picked = list(self._picked)
        self.cancel_picking()
        if self.on_picks_complete is not None:
            self.on_picks_complete(picked)

    def _draw_picks(self) -> None:
        """Mark what has been picked, so the user can see it before applying."""
        for index, (x, y) in enumerate(self._picked, start=1):
            cx, cy = x * self.zoom, y * self.zoom
            self.canvas.create_line(cx - PICK_RADIUS, cy, cx + PICK_RADIUS, cy,
                                    fill=PICK_COLOR, width=1)
            self.canvas.create_line(cx, cy - PICK_RADIUS, cx, cy + PICK_RADIUS,
                                    fill=PICK_COLOR, width=1)
            self.canvas.create_oval(cx - PICK_RADIUS, cy - PICK_RADIUS,
                                    cx + PICK_RADIUS, cy + PICK_RADIUS,
                                    outline=PICK_COLOR)
            self.canvas.create_text(cx + PICK_RADIUS + 3, cy - PICK_RADIUS - 3,
                                    text=str(index), anchor='nw',
                                    fill=PICK_COLOR, font=FONT_BOLD)

    # ---- interaction ----

    def _to_image_coords(self, event) -> Tuple[int, int]:
        x = int(self.canvas.canvasx(event.x) / max(self.zoom, 1e-6))
        y = int(self.canvas.canvasy(event.y) / max(self.zoom, 1e-6))
        return x, y

    def _on_press(self, event) -> None:
        if self.picking:
            if self._processed is not None:
                x, y = self._to_image_coords(event)
                height, width = self._processed.shape[:2]
                self._record_pick(max(0, min(x, width - 1)),
                                  max(0, min(y, height - 1)))
            return

        if self.mode.get() == 'split':
            self._dragging_split = True
            self._on_drag(event)
            return

        if self._processed is None:
            return

        x, y = self._to_image_coords(event)
        if self.on_pixel is not None:
            self.on_pixel(x, y)
        if self._can_select_region():
            self._region_start = (x, y)

    def _on_drag(self, event) -> None:
        if self._dragging_split:
            if self._processed is None:
                return
            composite = self._compose()
            if composite is None:
                return
            width = composite.shape[1] * self.zoom
            self._split = float(
                np.clip(self.canvas.canvasx(event.x) / max(width, 1e-6), 0, 1))
            self.redraw()
            return

        if self._region_start is None:
            return

        # A rubber band drawn on the canvas rather than into the image: the
        # pixels under it have to stay exactly as the filter will see them
        start_x, start_y = self._region_start
        current_x, current_y = self._to_image_coords(event)
        box = (start_x * self.zoom, start_y * self.zoom,
               current_x * self.zoom, current_y * self.zoom)

        if self._region_item is None:
            self._region_item = self.canvas.create_rectangle(
                *box, outline=SELECTION_COLOR, width=1, dash=(4, 3))
        else:
            self.canvas.coords(self._region_item, *box)

    def _on_release(self, event) -> None:
        self._dragging_split = False

        if self._region_item is not None:
            self.canvas.delete(self._region_item)
            self._region_item = None

        start, self._region_start = self._region_start, None
        if start is None or self._processed is None:
            return

        region = self._region_between(start, self._to_image_coords(event))
        if region is not None and self.on_region is not None:
            self.on_region(*region)

    def _can_select_region(self) -> bool:
        """
        Whether a drag maps onto one image.

        Side by side puts two frames on the canvas, so a point past the
        midpoint means something different from the same point before it;
        split already spends the drag on its divider.

        Difference is included on purpose. It is drawn on the processed
        frame's own grid, so a drag maps straight through - and seeing where a
        filter actually acted and then dragging that region out is the whole
        point of having the view next to roi_filter.
        """
        return self.mode.get() in ('processed', 'original', 'difference')

    def _region_between(self, start, end) -> Optional[Tuple[int, int, int, int]]:
        """
        The dragged rectangle as x, y, width, height in image pixels.

        None for a drag too small to be one: a click that wanders a pixel is a
        click, and a region that thin is no use to the filters that take one.
        """
        image = self._processed
        if image is None:
            return None

        height, width = image.shape[:2]
        x1, x2 = sorted((start[0], end[0]))
        y1, y2 = sorted((start[1], end[1]))

        # Clamped to the image: the canvas is usually larger than the frame
        # drawn on it, and a drag that overshoots should stop at the edge
        x1, x2 = max(0, min(x1, width - 1)), max(0, min(x2, width))
        y1, y2 = max(0, min(y1, height - 1)), max(0, min(y2, height))

        if x2 - x1 < MIN_REGION or y2 - y1 < MIN_REGION:
            return None
        return x1, y1, x2 - x1, y2 - y1

    def _on_wheel_zoom(self, event) -> None:
        """Zoom about the pointer, so the pixel under it stays put."""
        if self._processed is None:
            return
        before_x = self.canvas.canvasx(event.x) / max(self.zoom, 1e-6)
        before_y = self.canvas.canvasy(event.y) / max(self.zoom, 1e-6)

        step = 1.25 if event.delta > 0 else 1 / 1.25
        self.set_zoom(self.zoom * step)

        display_w, display_h = self._display_size
        self.canvas.xview_moveto(
            max(0.0, before_x * self.zoom - event.x) / max(display_w, 1))
        self.canvas.yview_moveto(
            max(0.0, before_y * self.zoom - event.y) / max(display_h, 1))

    def _on_wheel_scroll(self, event) -> None:
        self.canvas.yview_scroll(-1 if event.delta > 0 else 1, 'units')

    def _on_wheel_pan(self, event) -> None:
        self.canvas.xview_scroll(-1 if event.delta > 0 else 1, 'units')



class ParameterPanel(ttk.Frame):
    """
    A parameter form generated from a filter's signature.

    Introspection rather than hand-written forms: every registered filter gets
    a usable panel, and a filter added later needs no GUI work at all.
    """

    def __init__(self, master, on_change: Optional[Callable[[], None]] = None,
                 palette: Optional[Dict[str, str]] = None, **kwargs):
        super().__init__(master, **kwargs)
        self._on_change = on_change
        self._entries: Dict[str, Dict[str, Any]] = {}
        self._choices: Dict[str, List[str]] = dict(CHOICES)
        self._body: Optional[ttk.Frame] = None
        self.palette = palette or DARK

        # Scrolled, because the forms are generated: measure_3d has fourteen
        # parameters and undistort's is longer still. Without this the tail of
        # a long form is simply unreachable, and so is anything packed below
        # the panel.
        self._canvas = tk.Canvas(self, highlightthickness=0, borderwidth=0,
                                 background=self.palette['panel'])
        self._scroll = ttk.Scrollbar(self, orient='vertical',
                                     command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._scroll.set)

        self._canvas.grid(row=0, column=0, sticky='nsew')
        self._scroll.grid(row=0, column=1, sticky='ns')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self._holder = ttk.Frame(self._canvas)
        self._window = self._canvas.create_window((0, 0), window=self._holder,
                                                  anchor='nw')
        self._holder.bind('<Configure>', self._on_holder_resize)
        self._canvas.bind('<Configure>', self._on_canvas_resize)
        self._canvas.bind('<MouseWheel>', self._on_wheel)

    def _on_holder_resize(self, _event=None) -> None:
        self._canvas.configure(scrollregion=self._canvas.bbox('all'))

    def _on_canvas_resize(self, event) -> None:
        # The form tracks the canvas width, so entries fill it rather than
        # keeping whatever width their contents asked for
        self._canvas.itemconfigure(self._window, width=event.width)

    def _on_wheel(self, event) -> None:
        if self._canvas.bbox('all') is None:
            return
        _, top, _, bottom = self._canvas.bbox('all')
        if bottom - top > self._canvas.winfo_height():
            self._canvas.yview_scroll(-1 if event.delta > 0 else 1, 'units')

    def set_palette(self, palette: Dict[str, str]) -> None:
        """Follow a theme change; ttk cannot reach the scrolling canvas."""
        self.palette = palette
        self._canvas.configure(background=palette['panel'])

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
        # Narrowed per filter, so the list never offers a value this one
        # rejects
        self._choices = choices_for(spec)

        self._body = ttk.Frame(self._holder)
        self._body.grid(row=0, column=0, sticky='nsew')
        self._body.columnconfigure(1, weight=1)
        self._holder.columnconfigure(0, weight=1)
        self._canvas.yview_moveto(0.0)

        ttk.Label(self._body, text=spec.description, wraplength=250,
                  style='Muted.TLabel').grid(row=0, column=0, columnspan=2,
                                             sticky='w', pady=(0, 8))

        signature = inspect.signature(spec.fn)
        parameters = list(signature.parameters.values())[1:]   # skip `image`

        # An analysis spec can name parameters the form should not offer, such
        # as the source path, which comes from the loaded file
        skip = set(getattr(spec, 'skip_params', ()))
        parameters = [p for p in parameters if p.name not in skip]

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
                                   'var': variable, 'readout': update_readout}
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

    def set_values(self, values: Dict[str, Any]) -> List[str]:
        """
        Fill any controls whose parameter names match, ignoring the rest.

        This is how a region dragged on the image reaches the form: x, y,
        width and height are the same four names on crop, roi_crop, roi_draw,
        roi_filter, redact and white_balance_patch, so nothing here has to know which
        filter is selected.

        Args:
            values: Parameter name to value

        Returns:
            The names that were filled, in the order given
        """
        filled = []
        for name, value in values.items():
            entry = self._entries.get(name)
            if entry is None:
                continue

            if entry['kind'] == 'bool':
                entry['var'].set(bool(value))
            elif entry['kind'] in ('int', 'float'):
                entry['var'].set(float(value))
            elif isinstance(value, (tuple, list)):
                # Flattened and comma-joined, which is how the entry parses
                # back: str([[1, 2]]) would not survive the round trip
                flat = []
                for item in value:
                    flat.extend(item if isinstance(item, (tuple, list)) else [item])
                entry['var'].set(','.join(str(v) for v in flat))
            else:
                entry['var'].set(str(value))

            # A slider's number beside it is redrawn by its own command, which
            # setting the variable from here does not run
            if 'readout' in entry:
                entry['readout']()
            filled.append(name)

        if filled:
            self._changed()
        return filled

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
