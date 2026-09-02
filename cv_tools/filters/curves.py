"""
Curves - Tonal adjustment through a control-point curve.

The most flexible of the tonal tools: levels can only set three points, while a
curve bends any part of the range independently. Control points are
interpolated with a monotonic (PCHIP) spline, so the mapping never doubles back
on itself - an ordinary cubic spline can overshoot between points and invert
the tonal order, producing bright halos where the image should darken.
"""

from typing import Dict, List, Optional, Sequence, Tuple

import cv2
import numpy as np

# Ready-made curves, each a list of (input, output) points
CURVE_PRESETS: Dict[str, List[Tuple[int, int]]] = {
    'linear': [(0, 0), (255, 255)],
    'brighten': [(0, 0), (64, 90), (192, 214), (255, 255)],
    'darken': [(0, 0), (64, 40), (192, 170), (255, 255)],
    'contrast': [(0, 0), (64, 44), (128, 128), (192, 212), (255, 255)],
    'reduce_contrast': [(0, 20), (128, 128), (255, 235)],
    # Raises shadow detail without blowing the highlights - the usual first
    # move on underexposed CCTV stills
    'lift_shadows': [(0, 0), (32, 62), (96, 130), (255, 255)],
    'film': [(0, 12), (64, 58), (128, 132), (192, 208), (255, 250)],
}

_CHANNEL_INDEX = {'r': 0, 'g': 1, 'b': 2, 'red': 0, 'green': 1, 'blue': 2}


def build_lut(points: Sequence[Tuple[float, float]]) -> np.ndarray:
    """
    Build a 256-entry lookup table from curve control points.

    Args:
        points: (input, output) pairs, 0-255. At least two, and inputs must be
                distinct; they are sorted for you.

    Returns:
        uint8 array of 256 output values

    Example:
        >>> lut = build_lut([(0, 0), (128, 160), (255, 255)])
        >>> lut[128]
        160
    """
    if points is None or len(points) < 2:
        raise ValueError(f"A curve needs at least 2 points, got {len(points or [])}")

    ordered = sorted((float(x), float(y)) for x, y in points)
    xs = np.array([p[0] for p in ordered], dtype=np.float64)
    ys = np.array([p[1] for p in ordered], dtype=np.float64)

    if len(np.unique(xs)) != len(xs):
        raise ValueError("Curve points must have distinct input values")
    if xs.min() < 0 or xs.max() > 255 or ys.min() < 0 or ys.max() > 255:
        raise ValueError("Curve points must lie within 0-255")

    grid = np.arange(256, dtype=np.float64)

    if len(xs) == 2:
        values = np.interp(grid, xs, ys)
    else:
        try:
            from scipy.interpolate import PchipInterpolator
            # Shape-preserving: monotonic between points, so the curve cannot
            # overshoot and invert the tonal order
            values = PchipInterpolator(xs, ys, extrapolate=True)(grid)
        except ImportError:
            values = np.interp(grid, xs, ys)

    # Rounded, not truncated: the spline returns 254.9999... at a control point
    # of 255, and truncation would put every entry up to one level low
    return np.clip(np.round(values), 0, 255).astype(np.uint8)


def apply_curve(
    image: np.ndarray,
    points: Optional[Sequence[Tuple[float, float]]] = None,
    preset: Optional[str] = None,
    channel: Optional[str] = None,
) -> np.ndarray:
    """
    Apply a tonal curve.

    Args:
        image: Input image (RGB, RGBA, or grayscale)
        points: (input, output) control points. Ignored when ``preset`` is set.
        preset: Name from ``CURVE_PRESETS``
        channel: Limit to one channel ('r', 'g', 'b'); None applies to all

    Returns:
        Adjusted image, alpha preserved

    Example:
        >>> lifted = apply_curve(dark_frame, preset='lift_shadows')
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")

    if preset is not None:
        if preset not in CURVE_PRESETS:
            available = ', '.join(sorted(CURVE_PRESETS))
            raise ValueError(f"Unknown curve preset '{preset}'. Available: {available}")
        points = CURVE_PRESETS[preset]
    elif points is None:
        raise ValueError("Provide either points or a preset")

    lut = build_lut(points)
    img = image.astype(np.uint8) if image.dtype != np.uint8 else image.copy()

    if img.ndim == 2:
        return cv2.LUT(img, lut)

    has_alpha = img.shape[2] == 4
    rgb = img[:, :, :3] if has_alpha else img
    alpha = img[:, :, 3:4] if has_alpha else None

    if channel is None:
        result = cv2.LUT(rgb, lut)
    else:
        index = _CHANNEL_INDEX.get(channel.lower())
        if index is None or index >= rgb.shape[2]:
            raise ValueError(f"Invalid channel: {channel}")
        result = rgb.copy()
        result[:, :, index] = cv2.LUT(rgb[:, :, index], lut)

    if alpha is not None:
        result = np.concatenate([result, alpha], axis=2)
    return result


def s_curve(image: np.ndarray, strength: float = 0.25) -> np.ndarray:
    """
    Apply a symmetric S-curve, deepening shadows and lifting highlights.

    Args:
        image: Input image
        strength: Curve depth, 0 (no change) to 1 (extreme)

    Returns:
        Adjusted image
    """
    if not 0.0 <= strength <= 1.0:
        raise ValueError(f"strength must be between 0 and 1, got {strength}")

    offset = 64.0 * strength
    points = [(0, 0), (64, 64 - offset), (128, 128), (192, 192 + offset), (255, 255)]
    return apply_curve(image, points=points)


def curve_from_string(text: str) -> List[Tuple[float, float]]:
    """
    Parse a curve written as ``in:out`` pairs, e.g. ``"0:0,128:160,255:255"``.

    Args:
        text: Comma-separated ``input:output`` pairs

    Returns:
        List of control points
    """
    points = []
    for token in text.split(','):
        token = token.strip()
        if ':' not in token:
            raise ValueError(f"Expected input:output, got {token!r}")
        raw_in, _, raw_out = token.partition(':')
        try:
            points.append((float(raw_in), float(raw_out)))
        except ValueError:
            raise ValueError(f"Curve points must be numbers, got {token!r}") from None

    if len(points) < 2:
        raise ValueError("A curve needs at least 2 points")
    return points
