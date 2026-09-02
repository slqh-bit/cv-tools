"""
Contrast & Brightness - Linear adjustment.

Inspired by Amped FIVE's basic Adjust filters.
"""

from typing import Optional
import numpy as np


def adjust_contrast_brightness(
    image: np.ndarray,
    brightness: float = 0.0,
    contrast: float = 1.0,
    gamma: float = 1.0,
    channel: Optional[str] = None,
) -> np.ndarray:
    """
    Adjust contrast, brightness, and gamma.

    Formula: output = (input - 128) * contrast + 128 + brightness
    Then apply gamma correction.

    Args:
        image: Input image (any dtype, will be converted to float)
        brightness: Brightness offset (-255 to 255, or -1 to 1 for float)
        contrast: Contrast factor (1.0 = no change, >1 = more contrast)
        gamma: Gamma correction (1.0 = no change, <1 = brighter, >1 = darker)
        channel: If specified, apply only to this channel ('r', 'g', 'b')

    Returns:
        Adjusted image in uint8

    Example:
        >>> brightened = adjust_contrast_brightness(dark_img, brightness=40, contrast=1.2)
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")

    is_float = image.dtype in (np.float32, np.float64)
    img = image.astype(np.float32)

    # Determine range
    if is_float:
        max_val = 1.0
        mid = 0.5
    else:
        max_val = 255.0
        mid = 128.0

    # Adjust brightness scale for uint8 vs float
    if not is_float and abs(brightness) <= 1.0:
        # User likely passed normalized brightness
        brightness = brightness * 255.0

    result = img.copy()

    # Apply per-channel or globally
    if channel is not None and img.ndim == 3:
        ch_map = {'r': 0, 'g': 1, 'b': 2, 'red': 0, 'green': 1, 'blue': 2}
        ch_idx = ch_map.get(channel.lower())
        if ch_idx is None or ch_idx >= img.shape[2]:
            raise ValueError(f"Invalid channel: {channel}")
        target = result[:, :, ch_idx]
    else:
        target = result

    # Contrast & brightness
    target = (target - mid) * contrast + mid + brightness

    # Gamma correction
    if gamma != 1.0:
        target = max_val * ((target / max_val) ** (1.0 / gamma))

    # Clip and convert
    target = np.clip(target, 0, max_val)

    if channel is not None:
        result[:, :, ch_idx] = target
    else:
        result = target

    if is_float:
        return np.clip(result, 0, 1).astype(image.dtype)
    return result.astype(np.uint8)


def auto_contrast(image: np.ndarray, cutoff: float = 0.0) -> np.ndarray:
    """
    Automatic contrast adjustment (like Photoshop's Auto Contrast).

    Stretches histogram to use full range, optionally ignoring outliers.

    Args:
        image: Input image
        cutoff: Percentage of darkest/brightest pixels to ignore (0-50)

    Returns:
        Auto-contrasted image
    """
    if image.ndim == 3:
        # Apply to luminance channel
        import cv2
        yuv = cv2.cvtColor(image, cv2.COLOR_RGB2YUV)
        y_channel = yuv[:, :, 0].astype(np.float32)
    else:
        y_channel = image.astype(np.float32)

    # Compute percentiles
    low = np.percentile(y_channel, cutoff)
    high = np.percentile(y_channel, 100 - cutoff)

    if high - low < 1:
        return image.copy()

    # Stretch
    y_channel = (y_channel - low) * (255.0 / (high - low))
    y_channel = np.clip(y_channel, 0, 255).astype(np.uint8)

    if image.ndim == 3:
        yuv[:, :, 0] = y_channel
        return cv2.cvtColor(yuv, cv2.COLOR_YUV2RGB)
    return y_channel
