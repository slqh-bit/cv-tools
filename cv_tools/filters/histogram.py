"""
Histogram - Display and analysis.

Inspired by Amped FIVE's histogram panel. ``render_histogram`` returns an
ordinary image array, so it saves and composes like any other output rather
than needing a GUI or a plotting backend.
"""

from typing import Any, Dict, Optional, Sequence, Tuple

import cv2
import numpy as np

# Curve colors, keyed by the channel names used throughout the toolkit
CHANNEL_COLORS = {
    'R': (255, 80, 80),
    'G': (80, 230, 80),
    'B': (90, 150, 255),
    'Gray': (235, 235, 235),
}


def _channel_views(image: np.ndarray) -> Dict[str, np.ndarray]:
    """Map channel names to 2D views, ignoring any alpha channel."""
    if image.ndim == 2:
        return {'Gray': image}
    if image.shape[2] == 1:
        return {'Gray': image[:, :, 0]}

    names = ['R', 'G', 'B']
    return {name: image[:, :, index] for index, name in enumerate(names)}


def compute_histogram(
    image: np.ndarray,
    bins: int = 256,
    normalize: bool = False,
) -> Dict[str, np.ndarray]:
    """
    Compute per-channel intensity histograms.

    Args:
        image: Input image (RGB, RGBA, or grayscale). Alpha is ignored.
        bins: Number of bins across the 0-255 range
        normalize: Return fractions of total pixels instead of raw counts

    Returns:
        Dict mapping channel name ('R', 'G', 'B' or 'Gray') to a bin array

    Example:
        >>> hist = compute_histogram(frame)
        >>> hist['R'].sum() == frame.shape[0] * frame.shape[1]
        True
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if bins < 1:
        raise ValueError(f"bins must be positive, got {bins}")

    result = {}
    for name, channel in _channel_views(image).items():
        counts, _ = np.histogram(channel, bins=bins, range=(0, 256))
        counts = counts.astype(np.float64)
        if normalize and counts.sum() > 0:
            counts = counts / counts.sum()
        result[name] = counts

    return result


def histogram_stats(image: np.ndarray) -> Dict[str, Any]:
    """
    Summarize the tonal distribution of an image.

    Clipping percentages matter forensically: pixels stuck at 0 or 255 have
    lost their original values, and no enhancement recovers them.

    Args:
        image: Input image (RGB, RGBA, or grayscale)

    Returns:
        Dict with per-channel mean, median, std, min, max, 1st/99th
        percentiles, and the share of fully clipped shadows and highlights
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")

    channels = {}
    for name, channel in _channel_views(image).items():
        values = channel.astype(np.float64)
        total = values.size
        channels[name] = {
            'mean': float(values.mean()),
            'median': float(np.median(values)),
            'std': float(values.std()),
            'min': int(values.min()),
            'max': int(values.max()),
            'p1': float(np.percentile(values, 1)),
            'p99': float(np.percentile(values, 99)),
            'clipped_shadows_pct': float(np.count_nonzero(channel <= 0) / total * 100.0),
            'clipped_highlights_pct': float(np.count_nonzero(channel >= 255) / total * 100.0),
        }

    return {
        'shape': image.shape,
        'pixels': int(image.shape[0] * image.shape[1]),
        'channels': channels,
    }


def dynamic_range_used(image: np.ndarray) -> float:
    """
    Fraction of the 0-255 range the image actually occupies, measured between
    the 1st and 99th percentiles so a handful of outliers cannot flatter it.

    A low value means levels or CLAHE has room to work.

    Returns:
        Value between 0 and 1
    """
    stats = histogram_stats(image)
    spans = [
        channel['p99'] - channel['p1']
        for channel in stats['channels'].values()
    ]
    return float(max(spans) / 255.0)


def render_histogram(
    image: np.ndarray,
    width: int = 512,
    height: int = 256,
    bins: int = 256,
    log_scale: bool = False,
    show_grid: bool = True,
    background: Tuple[int, int, int] = (18, 18, 20),
    channels: Optional[Sequence[str]] = None,
) -> np.ndarray:
    """
    Draw the histogram as an RGB image.

    Args:
        image: Input image to analyze
        width: Output width in pixels
        height: Output height in pixels
        bins: Number of histogram bins
        log_scale: Plot log(1 + count), which reveals sparse tails that a
                   linear plot flattens to nothing
        show_grid: Draw quarter-point grid lines
        background: Canvas RGB color
        channels: Restrict to these channel names, e.g. ``['R']``

    Returns:
        RGB uint8 chart image

    Example:
        >>> chart = render_histogram(frame, log_scale=True)
        >>> save_image(chart, 'histogram.png')
    """
    if width < 16 or height < 16:
        raise ValueError(f"width and height must be at least 16, got {width}x{height}")

    histograms = compute_histogram(image, bins=bins)

    if channels is not None:
        missing = [name for name in channels if name not in histograms]
        if missing:
            raise ValueError(f"Image has no channel(s): {', '.join(missing)}")
        histograms = {name: histograms[name] for name in channels}

    canvas = np.full((height, width, 3), background, dtype=np.uint8)

    if show_grid:
        grid_color = (55, 55, 60)
        for fraction in (0.25, 0.5, 0.75):
            x = int(fraction * (width - 1))
            y = int(fraction * (height - 1))
            cv2.line(canvas, (x, 0), (x, height - 1), grid_color, 1)
            cv2.line(canvas, (0, y), (width - 1, y), grid_color, 1)

    # One shared vertical scale keeps the channel curves comparable
    peak = max((h.max() for h in histograms.values()), default=0.0)
    if log_scale:
        peak = float(np.log1p(peak))
    if peak <= 0:
        return canvas

    plot_height = height - 4
    x_positions = np.linspace(0, width - 1, bins).astype(np.int32)

    for name, counts in histograms.items():
        values = np.log1p(counts) if log_scale else counts
        y_positions = (height - 2 - (values / peak) * plot_height).astype(np.int32)
        points = np.stack([x_positions, y_positions], axis=1).reshape(-1, 1, 2)
        cv2.polylines(canvas, [points], isClosed=False,
                      color=CHANNEL_COLORS.get(name, (200, 200, 200)),
                      thickness=1, lineType=cv2.LINE_AA)

    return canvas
