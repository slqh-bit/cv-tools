"""
Presentation metadata for filter parameters, shared by every front end.

A filter's signature carries names, types and defaults, which is enough to
generate a form - but not enough to generate a *good* one: it does not say that
``clip_limit`` is sensibly 0.5 to 10, or that ``color_mode`` takes one of three
named values. That knowledge lives here, so the Tkinter GUI and the Streamlit
dashboard build the same controls for the same filter.

It sits in ``utils`` rather than in either front end because both depend on it
and neither should depend on the other. Nothing here imports a UI toolkit:
importing this module must stay possible on a headless box with no Tkinter,
which is where the dashboard is normally served from.
"""

from typing import Dict, List, Tuple

import cv2
import numpy as np


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
