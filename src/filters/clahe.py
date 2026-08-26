"""
CLAHE - Contrast Limited Adaptive Histogram Equalization.

Inspired by Amped FIVE's adaptive contrast enhancement for low-quality CCTV footage.
"""

from typing import Union, Tuple
import numpy as np
import cv2


# The colour strategies this filter implements. Named here rather than only
# in the if-chain below so a front end can offer exactly these: histogram
# equalization implements a different set, and a shared list offers both
# filters options that one of them rejects.
COLOR_MODES = ('lab', 'hsv', 'yuv', 'channelwise', 'luminance')


def apply_clahe(
    image: np.ndarray,
    clip_limit: float = 2.0,
    tile_grid_size: Union[int, Tuple[int, int]] = 8,
    color_mode: str = 'lab',
) -> np.ndarray:
    """
    Apply CLAHE (Contrast Limited Adaptive Histogram Equalization).

    Args:
        image: Input image (RGB, RGBA, or grayscale)
        clip_limit: Threshold for contrast limiting (higher = more contrast)
        tile_grid_size: Size of grid for histogram equalization.
                        If int, creates square tiles (e.g., 8 -> 8x8).
                        If tuple, specifies (rows, cols) tiles.
        color_mode: Strategy for color images:
            - 'lab': Convert to LAB, apply CLAHE to L channel (recommended)
            - 'hsv': Convert to HSV, apply CLAHE to V channel
            - 'yuv': Convert to YUV, apply CLAHE to Y channel
            - 'luminance': Equalize the grayscale luma, write it back as Y
              (within 1/255 of 'yuv'; see the note on the branch)
            - 'channelwise': Apply CLAHE to each RGB channel separately

    Returns:
        Enhanced image with same number of channels as input

    Example:
        >>> enhanced = apply_clahe(dark_image, clip_limit=3.0, tile_grid_size=8)
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")

    # Normalize tile grid size
    if isinstance(tile_grid_size, int):
        tile_grid_size = (tile_grid_size, tile_grid_size)
    tile_size = tuple(tile_grid_size)

    # Create CLAHE object
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_size)

    # Handle grayscale
    if image.ndim == 2 or (image.ndim == 3 and image.shape[2] == 1):
        gray = image.astype(np.uint8) if image.dtype != np.uint8 else image
        if gray.ndim == 3:
            gray = gray[:, :, 0]
        return clahe.apply(gray)

    # Handle color images
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
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        result = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

    elif color_mode == 'hsv':
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        hsv[:, :, 2] = clahe.apply(hsv[:, :, 2])
        result = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

    elif color_mode == 'yuv':
        yuv = cv2.cvtColor(rgb, cv2.COLOR_RGB2YUV)
        yuv[:, :, 0] = clahe.apply(yuv[:, :, 0])
        result = cv2.cvtColor(yuv, cv2.COLOR_YUV2RGB)

    elif color_mode == 'channelwise':
        result = np.zeros_like(rgb)
        for c in range(3):
            result[:, :, c] = clahe.apply(rgb[:, :, c])

    # Very nearly 'yuv', and deliberately not merged with it. RGB2GRAY and the
    # Y of RGB2YUV are the same BT.601 combination but round differently: over
    # the validation corpus they disagree by 1 on 400 pixels in 35.6M (0.001%),
    # which CLAHE then amplifies to as much as 4/255 in the output. Neither
    # rounding is the correct one, so collapsing these two branches would buy a
    # few lines at the price of changing what an existing preset replays.
    elif color_mode == 'luminance':
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        equalized = clahe.apply(gray)
        yuv = cv2.cvtColor(rgb, cv2.COLOR_RGB2YUV)
        yuv[:, :, 0] = equalized
        result = cv2.cvtColor(yuv, cv2.COLOR_YUV2RGB)

    else:
        raise ValueError(
            f"Unknown color_mode: {color_mode}. "
            f"Expected one of: {', '.join(COLOR_MODES)}")

    if has_alpha and alpha is not None:
        result = np.concatenate([result, alpha], axis=2)

    return result


def apply_clahe_grid(
    image: np.ndarray,
    clip_limits: list,
    tile_grid_sizes: list,
    color_mode: str = 'lab',
) -> np.ndarray:
    """
    Apply multiple CLAHE settings and return a grid comparison.
    Useful for finding optimal parameters (like Amped FIVE's preview).

    Args:
        image: Input image
        clip_limits: List of clip limit values to try
        tile_grid_sizes: List of tile grid sizes to try
        color_mode: Color processing mode

    Returns:
        Grid image showing all combinations
    """
    import math

    combinations = [(c, t) for c in clip_limits for t in tile_grid_sizes]
    n = len(combinations)
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)

    h, w = image.shape[:2]
    thumb_h, thumb_w = h // rows, w // cols

    grid = np.zeros((thumb_h * rows, thumb_w * cols, 3), dtype=np.uint8)

    for idx, (clip, tile) in enumerate(combinations):
        enhanced = apply_clahe(image, clip_limit=clip, tile_grid_size=tile, color_mode=color_mode)
        if enhanced.ndim == 2:
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)
        elif enhanced.shape[2] == 4:
            enhanced = enhanced[:, :, :3]

        thumb = cv2.resize(enhanced, (thumb_w, thumb_h))

        row = idx // cols
        col = idx % cols
        y1, y2 = row * thumb_h, (row + 1) * thumb_h
        x1, x2 = col * thumb_w, (col + 1) * thumb_w
        grid[y1:y2, x1:x2] = thumb

        # Label
        label = f"clip={clip}, tile={tile}"
        cv2.putText(grid, label, (x1 + 5, y1 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    return grid
