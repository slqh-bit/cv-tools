"""
Invert - Tonal and colour inversion.

Straightforward, and more useful than it looks. Inverting a scanned film
negative recovers the positive image. Inverting only the luminance, leaving
hue alone, sometimes makes faint dark-on-dark detail readable where raising
brightness only washes it out.
"""

from typing import Optional, Tuple

import cv2
import numpy as np

_CHANNEL_INDEX = {'r': 0, 'g': 1, 'b': 2, 'red': 0, 'green': 1, 'blue': 2}


def _split_alpha(image: np.ndarray) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """Separate an alpha channel so transparency is not inverted."""
    if image.ndim == 3 and image.shape[2] == 4:
        return image[:, :, :3], image[:, :, 3:4]
    return image, None


def invert(image: np.ndarray) -> np.ndarray:
    """
    Invert every colour channel.

    Args:
        image: Input image (RGB, RGBA, or grayscale)

    Returns:
        Inverted image; alpha is left untouched

    Example:
        >>> positive = invert(scanned_negative)
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")

    img = image.astype(np.uint8) if image.dtype != np.uint8 else image
    rgb, alpha = _split_alpha(img)

    result = 255 - rgb

    if alpha is not None:
        result = np.concatenate([result, alpha], axis=2)
    return result


def invert_channel(image: np.ndarray, channel: str) -> np.ndarray:
    """
    Invert a single colour channel.

    Args:
        image: Input image (RGB or RGBA)
        channel: 'r', 'g', or 'b'

    Returns:
        Image with that one channel inverted
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if image.ndim == 2:
        raise ValueError("Channel inversion needs a colour image")

    img = image.astype(np.uint8) if image.dtype != np.uint8 else image.copy()
    rgb, alpha = _split_alpha(img)

    index = _CHANNEL_INDEX.get(channel.lower())
    if index is None:
        raise ValueError(f"Invalid channel: {channel}")

    result = rgb.copy()
    result[:, :, index] = 255 - result[:, :, index]

    if alpha is not None:
        result = np.concatenate([result, alpha], axis=2)
    return result


def invert_luminance(image: np.ndarray) -> np.ndarray:
    """
    Invert brightness while keeping hue and saturation.

    Produces a negative of the tones without the colour reversal of a full
    invert, so objects keep recognisable colours.

    Args:
        image: Input image (RGB, RGBA, or grayscale)

    Returns:
        Luminance-inverted image
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")

    img = image.astype(np.uint8) if image.dtype != np.uint8 else image

    if img.ndim == 2:
        return 255 - img

    rgb, alpha = _split_alpha(img)

    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    lab[:, :, 0] = 255 - lab[:, :, 0]
    result = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

    if alpha is not None:
        result = np.concatenate([result, alpha], axis=2)
    return result


def solarize(image: np.ndarray, threshold: int = 128) -> np.ndarray:
    """
    Invert only the pixels above a threshold, as over-exposed film does.

    Creates a hard tonal break at the threshold, which can separate two regions
    of similar brightness that the eye otherwise merges.

    Args:
        image: Input image
        threshold: Values above this are inverted, 0-255

    Returns:
        Solarized image
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if not 0 <= threshold <= 255:
        raise ValueError(f"threshold must be between 0 and 255, got {threshold}")

    img = image.astype(np.uint8) if image.dtype != np.uint8 else image
    rgb, alpha = _split_alpha(img)

    result = np.where(rgb > threshold, 255 - rgb, rgb).astype(np.uint8)

    if alpha is not None:
        result = np.concatenate([result, alpha], axis=2)
    return result
