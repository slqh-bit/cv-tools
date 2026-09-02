"""
Aspect Ratio - Pixel aspect correction and frame fitting.

Standard-definition video does not use square pixels. PAL and NTSC DVD footage,
and most older CCTV recorders, store frames whose pixels are wider or narrower
than they are tall. Displayed without correction, everything in frame is
stretched or squashed - people look too thin or too wide, and any measurement
taken from the frame is wrong in one axis.

Correcting this is a rescale, so it resamples the image. Do it once, and
preferably before measuring rather than after.
"""

from typing import Dict, Optional, Tuple

import cv2
import numpy as np

# Pixel aspect ratios (width / height of one pixel) for common formats
PIXEL_ASPECT_RATIOS: Dict[str, float] = {
    'square': 1.0,
    'pal_43': 12.0 / 11.0,        # 720x576 shown as 4:3
    'pal_169': 16.0 / 11.0,       # 720x576 shown as 16:9
    'ntsc_43': 10.0 / 11.0,       # 720x480 shown as 4:3
    'ntsc_169': 40.0 / 33.0,      # 720x480 shown as 16:9
    'hdv_1080': 4.0 / 3.0,        # 1440x1080 shown as 1920x1080
    'dvcpro_hd_720': 4.0 / 3.0,   # 960x720 shown as 1280x720
    'anamorphic_2x': 2.0,
}

_INTERPOLATIONS = {
    'nearest': cv2.INTER_NEAREST,
    'bilinear': cv2.INTER_LINEAR,
    'bicubic': cv2.INTER_CUBIC,
    'lanczos': cv2.INTER_LANCZOS4,
    'area': cv2.INTER_AREA,
}


# The kernels this module offers. Again no 'auto': these rescale one axis by
# a known factor, so there is nothing to infer.
INTERPOLATIONS = tuple(_INTERPOLATIONS)


def correct_pixel_aspect(
    image: np.ndarray,
    pixel_aspect: float = 1.0,
    interpolation: str = 'lanczos',
    scale_axis: str = 'width',
) -> np.ndarray:
    """
    Rescale non-square pixels to square ones.

    Args:
        image: Input image
        pixel_aspect: Width divided by height of a single stored pixel. Above 1
                      means pixels are wider than tall, so the image must be
                      stretched horizontally to look right.
        interpolation: 'nearest', 'bilinear', 'bicubic', 'lanczos', or 'area'
        scale_axis: 'width' stretches horizontally and keeps every original
                    row; 'height' squashes vertically and keeps every column.
                    Stretching invents no samples along the preserved axis, so
                    'width' is usually the safer choice.

    Returns:
        Image with square pixels

    Example:
        >>> corrected = correct_pixel_aspect(pal_frame,
        ...                                  PIXEL_ASPECT_RATIOS['pal_43'])
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if pixel_aspect <= 0:
        raise ValueError(f"pixel_aspect must be positive, got {pixel_aspect}")
    if interpolation not in _INTERPOLATIONS:
        available = ', '.join(sorted(_INTERPOLATIONS))
        raise ValueError(f"Unknown interpolation '{interpolation}'. Available: {available}")
    if scale_axis not in ('width', 'height'):
        raise ValueError(f"scale_axis must be 'width' or 'height', got {scale_axis!r}")

    if pixel_aspect == 1.0:
        return image.copy()

    height, width = image.shape[:2]

    if scale_axis == 'width':
        new_width = max(1, int(round(width * pixel_aspect)))
        new_height = height
    else:
        new_width = width
        new_height = max(1, int(round(height / pixel_aspect)))

    return cv2.resize(image, (new_width, new_height),
                      interpolation=_INTERPOLATIONS[interpolation])


def correct_pixel_aspect_named(
    image: np.ndarray,
    format_name: str,
    interpolation: str = 'lanczos',
) -> np.ndarray:
    """
    Correct pixel aspect using a named broadcast format.

    Args:
        image: Input image
        format_name: Key from ``PIXEL_ASPECT_RATIOS``
        interpolation: Resampling method

    Returns:
        Image with square pixels
    """
    if format_name not in PIXEL_ASPECT_RATIOS:
        available = ', '.join(sorted(PIXEL_ASPECT_RATIOS))
        raise ValueError(f"Unknown format '{format_name}'. Available: {available}")

    return correct_pixel_aspect(
        image, PIXEL_ASPECT_RATIOS[format_name], interpolation=interpolation
    )


def fit_to_aspect(
    image: np.ndarray,
    target_ratio: float,
    mode: str = 'pad',
    fill: Tuple[int, int, int] = (0, 0, 0),
    interpolation: str = 'lanczos',
) -> np.ndarray:
    """
    Fit an image to a target display aspect ratio.

    Args:
        image: Input image
        target_ratio: Desired width divided by height, e.g. 16/9
        mode: 'pad' adds bars and keeps all content and its proportions;
              'crop' trims to fill the frame, losing content at the edges;
              'stretch' distorts the content to fit. For forensic work 'pad'
              is the only one that alters neither geometry nor content.
        fill: RGB colour for the padding bars
        interpolation: Resampling method, used by 'stretch'

    Returns:
        Image at the requested aspect ratio

    Example:
        >>> letterboxed = fit_to_aspect(frame, 16 / 9, mode='pad')
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if target_ratio <= 0:
        raise ValueError(f"target_ratio must be positive, got {target_ratio}")
    if mode not in ('pad', 'crop', 'stretch'):
        raise ValueError(f"mode must be 'pad', 'crop' or 'stretch', got {mode!r}")
    if interpolation not in _INTERPOLATIONS:
        available = ', '.join(sorted(_INTERPOLATIONS))
        raise ValueError(f"Unknown interpolation '{interpolation}'. Available: {available}")

    height, width = image.shape[:2]
    current_ratio = width / height

    if abs(current_ratio - target_ratio) < 1e-9:
        return image.copy()

    if mode == 'stretch':
        new_width = max(1, int(round(height * target_ratio)))
        return cv2.resize(image, (new_width, height),
                          interpolation=_INTERPOLATIONS[interpolation])

    if mode == 'crop':
        if current_ratio > target_ratio:
            new_width = max(1, int(round(height * target_ratio)))
            offset = (width - new_width) // 2
            return image[:, offset:offset + new_width].copy()
        new_height = max(1, int(round(width / target_ratio)))
        offset = (height - new_height) // 2
        return image[offset:offset + new_height, :].copy()

    # pad
    if current_ratio > target_ratio:
        new_height = max(1, int(round(width / target_ratio)))
        total = new_height - height
        top, bottom, left, right = total // 2, total - total // 2, 0, 0
    else:
        new_width = max(1, int(round(height * target_ratio)))
        total = new_width - width
        top, bottom, left, right = 0, 0, total // 2, total - total // 2

    if image.ndim == 3 and image.shape[2] == 4:
        border_value = (*fill, 255)
    elif image.ndim == 2:
        border_value = int(sum(fill) / 3)
    else:
        border_value = fill

    return cv2.copyMakeBorder(
        image, top, bottom, left, right,
        cv2.BORDER_CONSTANT, value=border_value,
    )


def describe_aspect(image: np.ndarray, pixel_aspect: float = 1.0) -> Dict[str, object]:
    """
    Report an image's stored and displayed geometry.

    Args:
        image: Input image
        pixel_aspect: Width divided by height of one stored pixel

    Returns:
        Dict with stored size, storage aspect, pixel aspect, and the display
        aspect the two combine to give
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if pixel_aspect <= 0:
        raise ValueError(f"pixel_aspect must be positive, got {pixel_aspect}")

    height, width = image.shape[:2]
    storage_aspect = width / height
    display_aspect = storage_aspect * pixel_aspect

    return {
        'stored_width': int(width),
        'stored_height': int(height),
        'storage_aspect': float(storage_aspect),
        'pixel_aspect': float(pixel_aspect),
        'display_aspect': float(display_aspect),
        'display_width': int(round(width * pixel_aspect)),
        'display_height': int(height),
        'square_pixels': abs(pixel_aspect - 1.0) < 1e-9,
    }
