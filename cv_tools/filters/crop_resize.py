"""
Crop & Resize - Geometric operations.
"""

from typing import Tuple, Optional, Union
import numpy as np
import cv2


def crop(
    image: np.ndarray,
    x: int,
    y: int,
    width: int,
    height: int,
) -> np.ndarray:
    """
    Crop image to specified region.

    Args:
        image: Source image
        x: X coordinate of top-left corner
        y: Y coordinate of top-left corner
        width: Width of crop region
        height: Height of crop region

    Returns:
        Cropped image
    """
    h, w = image.shape[:2]

    # Clip to image bounds
    x1 = max(0, x)
    y1 = max(0, y)
    x2 = min(w, x + width)
    y2 = min(h, y + height)

    if x1 >= x2 or y1 >= y2:
        raise ValueError(f"Invalid crop region: ({x}, {y}, {width}, {height}) for image ({w}, {h})")

    return image[y1:y2, x1:x2].copy()


def resize(
    image: np.ndarray,
    width: Optional[int] = None,
    height: Optional[int] = None,
    scale: Optional[float] = None,
    interpolation: str = 'auto',
) -> np.ndarray:
    """
    Resize image.

    Args:
        image: Source image
        width: Target width (optional)
        height: Target height (optional)
        scale: Scale factor (optional, applied if width/height not given)
        interpolation: Interpolation method:
            - 'auto': Choose based on upscaling/downscaling
            - 'nearest': Nearest neighbor (fastest, blocky)
            - 'bilinear': Bilinear (fast, smooth)
            - 'bicubic': Bicubic (better quality)
            - 'lanczos': Lanczos (best quality, slowest)
            - 'area': Area resampling (good for downscaling)

    Returns:
        Resized image
    """
    h, w = image.shape[:2]

    # Determine target size
    if width is not None and height is not None:
        new_w, new_h = width, height
    elif width is not None:
        ratio = width / w
        new_w, new_h = width, int(h * ratio)
    elif height is not None:
        ratio = height / h
        new_w, new_h = int(w * ratio), height
    elif scale is not None:
        new_w, new_h = int(w * scale), int(h * scale)
    else:
        raise ValueError("Must specify width, height, or scale")

    if new_w <= 0 or new_h <= 0:
        raise ValueError(f"Invalid target size: ({new_w}, {new_h})")

    # Select interpolation
    inter_map = {
        'nearest': cv2.INTER_NEAREST,
        'bilinear': cv2.INTER_LINEAR,
        'bicubic': cv2.INTER_CUBIC,
        'lanczos': cv2.INTER_LANCZOS4,
        'area': cv2.INTER_AREA,
    }

    if interpolation == 'auto':
        if new_w < w or new_h < h:
            inter = cv2.INTER_AREA
        else:
            inter = cv2.INTER_LANCZOS4
    else:
        inter = inter_map.get(interpolation, cv2.INTER_LINEAR)

    return cv2.resize(image, (new_w, new_h), interpolation=inter)


def resize_one_to_one(image: np.ndarray, dpi: Optional[int] = None) -> np.ndarray:
    """
    Resize image to display at 1:1 pixel ratio.
    Useful for forensic analysis where pixel accuracy matters.

    Args:
        image: Source image
        dpi: Display DPI (if None, assumes 96 DPI)

    Returns:
        Image at 1:1 display size
    """
    # For digital display, 1:1 means actual pixels
    # This is mostly a pass-through, but documented for workflow clarity
    return image.copy()


def rotate(
    image: np.ndarray,
    angle: float,
    center: Optional[Tuple[int, int]] = None,
    scale: float = 1.0,
    border_mode: str = 'constant',
    border_value: Tuple[int, int, int] = (0, 0, 0),
) -> np.ndarray:
    """
    Rotate image by arbitrary angle.

    Args:
        image: Source image
        angle: Rotation angle in degrees (positive = counter-clockwise)
        center: Rotation center (default = image center)
        scale: Scale factor
        border_mode: How to handle borders ('constant', 'replicate', 'reflect')
        border_value: Fill color for constant border

    Returns:
        Rotated image
    """
    h, w = image.shape[:2]

    if center is None:
        center = (w // 2, h // 2)

    border_map = {
        'constant': cv2.BORDER_CONSTANT,
        'replicate': cv2.BORDER_REPLICATE,
        'reflect': cv2.BORDER_REFLECT,
        'wrap': cv2.BORDER_WRAP,
    }
    border = border_map.get(border_mode, cv2.BORDER_CONSTANT)

    M = cv2.getRotationMatrix2D(center, angle, scale)

    # Compute new bounding box to avoid cropping
    cos_a = abs(np.cos(np.deg2rad(angle)))
    sin_a = abs(np.sin(np.deg2rad(angle)))
    new_w = int(h * sin_a + w * cos_a)
    new_h = int(h * cos_a + w * sin_a)

    # Adjust rotation matrix for new center
    M[0, 2] += (new_w - w) / 2
    M[1, 2] += (new_h - h) / 2

    return cv2.warpAffine(
        image, M, (new_w, new_h),
        flags=cv2.INTER_LINEAR,
        borderMode=border,
        borderValue=border_value,
    )


def flip(image: np.ndarray, direction: str = 'horizontal') -> np.ndarray:
    """
    Flip image horizontally or vertically.

    Args:
        image: Source image
        direction: 'horizontal', 'vertical', or 'both'

    Returns:
        Flipped image
    """
    if direction == 'horizontal':
        return cv2.flip(image, 1)
    elif direction == 'vertical':
        return cv2.flip(image, 0)
    elif direction == 'both':
        return cv2.flip(image, -1)
    else:
        raise ValueError(f"Invalid direction: {direction}")
