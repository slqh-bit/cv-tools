"""
Saturation - Colour intensity and vibrance.

``adjust_saturation`` scales every pixel's colourfulness equally. ``vibrance``
scales muted colours more than already-saturated ones, which keeps strong
colours from clipping into flat blocks - useful when you want to make a faded
garment readable without destroying a bright one elsewhere in frame.

Pushing saturation hard is an interpretation, not a recovery: it exaggerates
colour that compression already approximated, so judge hue from the corrected
original rather than a boosted copy.
"""

from typing import Optional, Tuple

import cv2
import numpy as np

# Rec. 601 luma weights, matching OpenCV's RGB2GRAY
_LUMA = np.array([0.299, 0.587, 0.114], dtype=np.float32)


def _split_alpha(image: np.ndarray) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """Separate an alpha channel so it is not treated as colour."""
    if image.ndim == 3 and image.shape[2] == 4:
        return image[:, :, :3], image[:, :, 3:4]
    return image, None


def adjust_saturation(image: np.ndarray, factor: float = 1.0) -> np.ndarray:
    """
    Scale colour saturation uniformly.

    Args:
        image: Input image (RGB or RGBA)
        factor: 0 = grayscale, 1 = unchanged, >1 = more saturated

    Returns:
        Adjusted image, alpha preserved

    Example:
        >>> vivid = adjust_saturation(frame, 1.4)
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if factor < 0:
        raise ValueError(f"factor must be non-negative, got {factor}")

    if image.ndim == 2:
        # Grayscale has no colour to scale
        return image.copy()

    rgb, alpha = _split_alpha(image)
    rgb = rgb.astype(np.uint8) if rgb.dtype != np.uint8 else rgb

    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV).astype(np.float32)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * factor, 0, 255)
    result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)

    if alpha is not None:
        result = np.concatenate([result, alpha], axis=2)
    return result


def adjust_vibrance(image: np.ndarray, factor: float = 1.0) -> np.ndarray:
    """
    Scale saturation, weighted so muted colours move more than vivid ones.

    Args:
        image: Input image (RGB or RGBA)
        factor: 1 = unchanged, >1 = more vibrant, <1 = more muted

    Returns:
        Adjusted image

    Example:
        >>> lifted = adjust_vibrance(faded_frame, 1.6)
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if factor < 0:
        raise ValueError(f"factor must be non-negative, got {factor}")

    if image.ndim == 2:
        return image.copy()

    rgb, alpha = _split_alpha(image)
    rgb = rgb.astype(np.uint8) if rgb.dtype != np.uint8 else rgb

    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV).astype(np.float32)
    saturation = hsv[:, :, 1]

    # Weight falls to zero as a pixel approaches full saturation, so vivid
    # colours are left alone instead of clipping
    weight = 1.0 - (saturation / 255.0)
    scaled = saturation * (1.0 + (factor - 1.0) * weight)

    hsv[:, :, 1] = np.clip(scaled, 0, 255)
    result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)

    if alpha is not None:
        result = np.concatenate([result, alpha], axis=2)
    return result


def desaturate(image: np.ndarray, method: str = 'luminance') -> np.ndarray:
    """
    Convert to grayscale by a chosen rule.

    The methods disagree on which colours become which grays, so a detail that
    vanishes under one can stay visible under another.

    Args:
        image: Input image
        method: 'luminance' (perceptual weights), 'average' (equal weights),
                'lightness' (midpoint of the lightest and darkest channel),
                'max' (brightest channel), 'min' (darkest channel)

    Returns:
        Single-channel uint8 image
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")

    if image.ndim == 2:
        return image.copy()

    rgb, _ = _split_alpha(image)
    channels = rgb.astype(np.float32)

    if method == 'luminance':
        gray = channels @ _LUMA
    elif method == 'average':
        gray = channels.mean(axis=2)
    elif method == 'lightness':
        gray = (channels.max(axis=2) + channels.min(axis=2)) / 2.0
    elif method == 'max':
        gray = channels.max(axis=2)
    elif method == 'min':
        gray = channels.min(axis=2)
    else:
        raise ValueError(
            f"Unknown method '{method}'. Use luminance, average, lightness, max, or min"
        )

    return np.clip(gray, 0, 255).astype(np.uint8)


def selective_saturation(
    image: np.ndarray,
    hue_center: float,
    hue_range: float = 30.0,
    factor: float = 1.5,
) -> np.ndarray:
    """
    Saturate only colours near a chosen hue, leaving the rest untouched.

    Isolates one colour of interest - a vehicle, a garment - without altering
    the rest of the frame.

    Args:
        image: Input image
        hue_center: Target hue in degrees, 0-360 (0 red, 120 green, 240 blue)
        hue_range: How far either side of the centre to affect, in degrees
        factor: Saturation multiplier inside that band

    Returns:
        Adjusted image
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if image.ndim == 2:
        return image.copy()
    if hue_range <= 0:
        raise ValueError(f"hue_range must be positive, got {hue_range}")

    rgb, alpha = _split_alpha(image)
    rgb = rgb.astype(np.uint8) if rgb.dtype != np.uint8 else rgb

    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV).astype(np.float32)
    # OpenCV packs hue into 0-179 to fit a byte
    hue = hsv[:, :, 0] * 2.0

    distance = np.abs(hue - (hue_center % 360.0))
    distance = np.minimum(distance, 360.0 - distance)

    # Feather the edge of the band so the boundary is not visible
    weight = np.clip(1.0 - distance / hue_range, 0.0, 1.0)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1.0 + (factor - 1.0) * weight), 0, 255)

    result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)

    if alpha is not None:
        result = np.concatenate([result, alpha], axis=2)
    return result
