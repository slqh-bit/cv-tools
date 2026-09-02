"""
Levels - Histogram levels adjustment (black point, midtones, white point).

Inspired by Amped FIVE's Levels filter for forensic image enhancement.
"""

from typing import Optional, Union, Tuple
import numpy as np


def adjust_levels(
    image: np.ndarray,
    black_point: float = 0,
    gamma: float = 1.0,
    white_point: float = 255,
    output_black: float = 0,
    output_white: float = 255,
    channel: Optional[str] = None,
) -> np.ndarray:
    """
    Adjust image levels like Photoshop/GIMP levels tool.

    Maps input range [black_point, white_point] to [output_black, output_white]
    with gamma correction on midtones.

    Args:
        image: Input image (RGB or grayscale)
        black_point: Input black point (pixels below become black)
        gamma: Midtone gamma (1.0 = linear, <1 = brighter midtones, >1 = darker)
        white_point: Input white point (pixels above become white)
        output_black: Output black level
        output_white: Output white level
        channel: Apply to specific channel ('r', 'g', 'b') or None for all/luminance

    Returns:
        Level-adjusted image

    Example:
        >>> adjusted = adjust_levels(image, black_point=20, gamma=0.8, white_point=230)
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")

    is_float = image.dtype in (np.float32, np.float64)
    img = image.astype(np.float32)

    if is_float:
        max_val = 1.0
        # Normalize parameters for float images
        black_point = black_point / 255.0 if black_point > 1.0 else black_point
        white_point = white_point / 255.0 if white_point > 1.0 else white_point
        output_black = output_black / 255.0 if output_black > 1.0 else output_black
        output_white = output_white / 255.0 if output_white > 1.0 else output_white
    else:
        max_val = 255.0

    # Validate points
    if black_point >= white_point:
        raise ValueError("black_point must be less than white_point")

    # Select target
    if channel is not None and img.ndim == 3:
        ch_map = {'r': 0, 'g': 1, 'b': 2, 'red': 0, 'green': 1, 'blue': 2}
        ch_idx = ch_map.get(channel.lower())
        if ch_idx is None:
            raise ValueError(f"Invalid channel: {channel}")
        target = img[:, :, ch_idx].copy()
    else:
        target = img.copy()

    # Normalize to 0-1
    normalized = (target - black_point) / (white_point - black_point)
    normalized = np.clip(normalized, 0, 1)

    # Apply gamma
    if gamma != 1.0 and gamma > 0:
        normalized = np.power(normalized, 1.0 / gamma)

    # Scale to output range
    result = normalized * (output_white - output_black) + output_black
    result = np.clip(result, 0, max_val)

    if channel is not None:
        img[:, :, ch_idx] = result
        output = img
    else:
        output = result

    if is_float:
        return output.astype(image.dtype)
    return output.astype(np.uint8)


def auto_levels(image: np.ndarray, per_channel: bool = False) -> np.ndarray:
    """
    Automatic levels adjustment (stretch histogram to full range per channel).

    Args:
        image: Input image
        per_channel: If True, adjust each RGB channel independently
                      (may cause color shifts). If False, use luminance.

    Returns:
        Auto-leveled image
    """
    if image.ndim == 2:
        # Grayscale
        black = image.min()
        white = image.max()
        return adjust_levels(image, black_point=float(black), white_point=float(white))

    if per_channel:
        result = image.copy().astype(np.float32)
        for c in range(image.shape[2]):
            ch = result[:, :, c]
            black = ch.min()
            white = ch.max()
            if white > black:
                ch = (ch - black) / (white - black) * 255.0
                result[:, :, c] = np.clip(ch, 0, 255)
        return result.astype(np.uint8)
    else:
        # Use luminance
        import cv2
        yuv = cv2.cvtColor(image, cv2.COLOR_RGB2YUV)
        y = yuv[:, :, 0].astype(np.float32)
        black = y.min()
        white = y.max()
        if white > black:
            y = (y - black) / (white - black) * 255.0
            yuv[:, :, 0] = np.clip(y, 0, 255).astype(np.uint8)
        return cv2.cvtColor(yuv, cv2.COLOR_YUV2RGB)
