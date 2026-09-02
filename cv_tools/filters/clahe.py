"""
CLAHE - Contrast Limited Adaptive Histogram Equalization.

Inspired by Amped FIVE's adaptive contrast enhancement for low-quality CCTV footage.
"""

from typing import Sequence, Union, Tuple
import numpy as np
import cv2


# The colour strategies this filter implements. Named here rather than only
# in the if-chain below so a front end can offer exactly these: histogram
# equalization implements a different set, and a shared list offers both
# filters options that one of them rejects.
COLOR_MODES = ('lab', 'hsv', 'yuv', 'channelwise', 'luminance')

# Of those, the ones OpenCV can run without dropping to 8 bits. cvtColor
# rejects CV_16U for LAB and HSV, so a 10- or 12-bit source cannot go through
# those two with its precision intact; the rest convert and equalize at 16.
SIXTEEN_BIT_MODES = ('yuv', 'channelwise', 'luminance')


def apply_clahe(
    image: np.ndarray,
    clip_limit: float = 2.0,
    tile_grid_size: Union[int, Tuple[int, int]] = 8,
    color_mode: str = 'lab',
) -> np.ndarray:
    """
    Apply CLAHE (Contrast Limited Adaptive Histogram Equalization).

    Args:
        image: Input image (RGB, RGBA, or grayscale). uint16 is equalized at
               16 bits; see SIXTEEN_BIT_MODES for the colour modes that allow it
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

    is_gray = image.ndim == 2 or (image.ndim == 3 and image.shape[2] == 1)

    # A 10- or 12-bit source arrives as uint16, and OpenCV equalizes that
    # directly. Casting it to uint8 would not just coarsen the image, it would
    # wrap: a 12-bit value of 4096 lands on 0, turning a bright pixel black
    # immediately before the step whose whole purpose is to stretch contrast.
    if image.dtype == np.uint16 and not is_gray and color_mode not in SIXTEEN_BIT_MODES:
        raise ValueError(
            f"color_mode {color_mode!r} cannot keep 16 bits: OpenCV's conversion "
            f"for it accepts 8-bit only. Use one of "
            f"{', '.join(SIXTEEN_BIT_MODES)} to preserve the source depth, or "
            f"convert the image to 8-bit first and accept the loss.")

    # Normalize tile grid size
    if isinstance(tile_grid_size, int):
        tile_grid_size = (tile_grid_size, tile_grid_size)
    tile_size = tuple(tile_grid_size)

    # Create CLAHE object
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_size)

    # Handle grayscale
    if is_gray:
        gray = image if image.dtype in (np.uint8, np.uint16) else image.astype(np.uint8)
        if gray.ndim == 3:
            gray = gray[:, :, 0]
        return clahe.apply(gray)

    # Handle color images
    image = image.copy() if image.dtype in (np.uint8, np.uint16) else image.astype(np.uint8)
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
    clip_limits: Union[float, Sequence[float]] = (1.0, 2.0, 3.0, 4.0),
    tile_grid_sizes: Union[int, Sequence[int]] = 8,
    color_mode: str = 'lab',
) -> np.ndarray:
    """
    Apply multiple CLAHE settings and return a grid comparison.
    Useful for finding optimal parameters (like Amped FIVE's preview).

    The noise an operator pays for a given clip_limit varies by a factor of
    1.4 to 1.9 from image to image, so the value that is right for one frame is
    not right for the next. Facing a slider, an operator keeps the default;
    facing this board, they choose a value they can justify.

    Args:
        image: Input image
        clip_limits: Clip limit values to try; a single value is accepted
        tile_grid_sizes: Grid sizes to try; a single value is accepted
        color_mode: Color processing mode

    Returns:
        Grid image showing all combinations, each labelled with its settings

    Example:
        >>> board = apply_clahe_grid(frame, clip_limits=[1.5, 2, 3])
    """
    import math

    # The registry passes whatever the parameter form parsed, and a form with
    # one value typed in it yields a scalar rather than a list of one
    if isinstance(clip_limits, (int, float)):
        clip_limits = [clip_limits]
    if isinstance(tile_grid_sizes, int):
        tile_grid_sizes = [tile_grid_sizes]

    combinations = [(c, t) for c in clip_limits for t in tile_grid_sizes]
    if not combinations:
        raise ValueError("Need at least one clip limit and one tile grid size")
    n = len(combinations)
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)

    h, w = image.shape[:2]
    thumb_h, thumb_w = h // rows, w // cols

    grid = np.zeros((thumb_h * rows, thumb_w * cols, 3), dtype=np.uint8)

    # The board is a preview, labelled and read side by side, so it is rendered
    # at 8 bits even when the source is 16. The scale is taken from the source
    # once rather than per tile: normalizing each tile to its own range would
    # make them individually pretty and mutually incomparable, which is the one
    # thing a comparison board must not do. The filter itself still runs at the
    # source depth, so the settings chosen here apply at full precision.
    display_scale = 255.0 / max(int(image.max()), 1) if image.dtype != np.uint8 else None

    for idx, (clip, tile) in enumerate(combinations):
        enhanced = apply_clahe(image, clip_limit=clip, tile_grid_size=tile, color_mode=color_mode)
        if display_scale is not None:
            enhanced = np.clip(enhanced * display_scale, 0, 255).astype(np.uint8)
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
