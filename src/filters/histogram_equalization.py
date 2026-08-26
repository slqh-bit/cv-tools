"""
Histogram Equalization - Global histogram equalization.
"""

from typing import Optional
import numpy as np
import cv2


# The colour strategies this filter implements. Not the same set as CLAHE's:
# 'grayscale' discards colour outright, which adaptive equalization has no
# reason to offer, and 'luminance' is CLAHE's blend, which this does not do.
COLOR_MODES = ('lab', 'hsv', 'yuv', 'channelwise', 'grayscale')


def histogram_equalization(
    image: np.ndarray,
    color_mode: str = 'lab',
    mask: Optional[np.ndarray] = None,
) -> np.ndarray:
    """
    Apply global histogram equalization.

    Args:
        image: Input image (RGB, RGBA, or grayscale)
        color_mode: Strategy for color images:
            - 'lab': Equalize L channel in LAB space (recommended)
            - 'hsv': Equalize V channel in HSV space
            - 'yuv': Equalize Y channel in YUV space
            - 'channelwise': Equalize each RGB channel independently
            - 'grayscale': Convert to grayscale, equalize, convert back
        mask: Optional mask (same size as image) to restrict equalization region

    Returns:
        Histogram-equalized image
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")

    # Handle grayscale
    if image.ndim == 2 or (image.ndim == 3 and image.shape[2] == 1):
        gray = image.astype(np.uint8) if image.dtype != np.uint8 else image.copy()
        if gray.ndim == 3:
            gray = gray[:, :, 0]
        if mask is not None:
            return cv2.equalizeHist(gray, mask=mask.astype(np.uint8) if mask.dtype != np.uint8 else mask)
        return cv2.equalizeHist(gray)

    image = image.astype(np.uint8) if image.dtype != np.uint8 else image.copy()
    has_alpha = image.shape[2] == 4 if image.ndim == 3 else False

    if has_alpha:
        rgb = image[:, :, :3]
        alpha = image[:, :, 3:4]
    else:
        rgb = image
        alpha = None

    if color_mode == 'lab':
        lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
        if mask is not None:
            mask_u8 = mask.astype(np.uint8) if mask.dtype != np.uint8 else mask
            lab[:, :, 0] = cv2.equalizeHist(lab[:, :, 0], mask=mask_u8)
        else:
            lab[:, :, 0] = cv2.equalizeHist(lab[:, :, 0])
        result = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

    elif color_mode == 'hsv':
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        hsv[:, :, 2] = cv2.equalizeHist(hsv[:, :, 2])
        result = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

    elif color_mode == 'yuv':
        yuv = cv2.cvtColor(rgb, cv2.COLOR_RGB2YUV)
        yuv[:, :, 0] = cv2.equalizeHist(yuv[:, :, 0])
        result = cv2.cvtColor(yuv, cv2.COLOR_YUV2RGB)

    elif color_mode == 'channelwise':
        result = np.zeros_like(rgb)
        for c in range(3):
            result[:, :, c] = cv2.equalizeHist(rgb[:, :, c])

    elif color_mode == 'grayscale':
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        equalized = cv2.equalizeHist(gray)
        result = cv2.cvtColor(equalized, cv2.COLOR_GRAY2RGB)

    else:
        raise ValueError(
            f"Unknown color_mode: {color_mode}. "
            f"Expected one of: {', '.join(COLOR_MODES)}")

    if has_alpha and alpha is not None:
        result = np.concatenate([result, alpha], axis=2)

    return result


def adaptive_histogram_equalization(
    image: np.ndarray,
    clip_limit: float = 2.0,
    tile_size: int = 8,
) -> np.ndarray:
    """
    Convenience wrapper: CLAHE (same as filters.clahe but simpler signature).
    """
    from .clahe import apply_clahe
    return apply_clahe(image, clip_limit=clip_limit, tile_grid_size=tile_size)
