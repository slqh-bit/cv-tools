"""
White Balance - Remove a colour cast.

CCTV footage is rarely neutral: sodium street lighting pushes everything
orange, fluorescent tubes push green, and IR-assisted cameras skew red. All
three make skin, paint and clothing colours unreliable, so correcting the cast
comes before any judgement about colour.

Each automatic method rests on an assumption about the scene, and each fails
when the assumption does not hold:

    - ``gray_world``  the average of the scene is neutral gray. Fails when one
                      colour genuinely dominates - a red car filling the frame
                      gets neutralised along with the cast.
    - ``white_patch`` the brightest pixels are white. Fails on a blown highlight
                      or a coloured light source in shot.
    - ``shades_of_gray`` a compromise between the two, and the safest default.

When the scene contains something known to be neutral, measure it instead:
``white_balance_from_patch`` takes the guesswork out.
"""

from typing import Optional, Tuple

import cv2
import numpy as np


def _split_alpha(image: np.ndarray) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """Separate an alpha channel so it is not colour-corrected."""
    if image.ndim == 3 and image.shape[2] == 4:
        return image[:, :, :3], image[:, :, 3:4]
    return image, None


def _apply_gains(rgb: np.ndarray, gains: np.ndarray) -> np.ndarray:
    """Scale each channel by its gain and clip."""
    balanced = rgb.astype(np.float32) * gains.reshape(1, 1, 3)
    return np.clip(balanced, 0, 255).astype(np.uint8)


def compute_gains(image: np.ndarray, method: str = 'shades_of_gray',
                  norm: float = 6.0, percentile: float = 97.0) -> np.ndarray:
    """
    Compute the per-channel gains that would neutralise the cast.

    Exposed separately so a gain measured on one frame can be applied to a
    whole sequence, keeping colour consistent across frames.

    Args:
        image: Reference image
        method: 'gray_world', 'white_patch', or 'shades_of_gray'
        norm: Minkowski exponent for 'shades_of_gray'. 1 becomes gray world,
              infinity becomes white patch; 6 is the usual compromise.
        percentile: Brightness percentile treated as white by 'white_patch',
                    below 100 so a few blown pixels cannot set the gain

    Returns:
        Array of three gains, normalised so the green channel is unchanged
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")

    rgb, _ = _split_alpha(image)
    if rgb.ndim != 3 or rgb.shape[2] < 3:
        raise ValueError("White balance needs a colour image")

    channels = rgb.astype(np.float32)

    if method == 'gray_world':
        estimate = np.array([channels[:, :, c].mean() for c in range(3)])
    elif method == 'white_patch':
        estimate = np.array([
            np.percentile(channels[:, :, c], percentile) for c in range(3)
        ])
    elif method == 'shades_of_gray':
        if norm <= 0:
            raise ValueError(f"norm must be positive, got {norm}")
        estimate = np.array([
            np.power(np.mean(np.power(channels[:, :, c], norm)), 1.0 / norm)
            for c in range(3)
        ])
    else:
        raise ValueError(
            f"Unknown method '{method}'. Use gray_world, white_patch, or shades_of_gray"
        )

    estimate[estimate <= 0] = 1.0
    # Anchor on green: it carries most of the luminance, so holding it fixed
    # keeps overall brightness roughly unchanged
    return estimate[1] / estimate


def auto_white_balance(
    image: np.ndarray,
    method: str = 'shades_of_gray',
    norm: float = 6.0,
    percentile: float = 97.0,
) -> np.ndarray:
    """
    Estimate and remove a colour cast automatically.

    Args:
        image: Input image (RGB or RGBA)
        method: 'gray_world', 'white_patch', or 'shades_of_gray'
        norm: Minkowski exponent for 'shades_of_gray'
        percentile: Brightness percentile treated as white by 'white_patch'

    Returns:
        Balanced image, alpha preserved

    Example:
        >>> corrected = auto_white_balance(sodium_lit_frame)
    """
    rgb, alpha = _split_alpha(image)
    gains = compute_gains(image, method=method, norm=norm, percentile=percentile)
    result = _apply_gains(rgb, gains)

    if alpha is not None:
        result = np.concatenate([result, alpha], axis=2)
    return result


def white_balance_from_patch(
    image: np.ndarray,
    x: int,
    y: int,
    width: int,
    height: int,
) -> np.ndarray:
    """
    Balance using a region known to be neutral gray or white.

    The reliable method when the scene offers a reference - a white wall, a
    number plate's background, a sheet of paper.

    Args:
        image: Input image
        x, y, width, height: Region containing the neutral reference

    Returns:
        Balanced image

    Example:
        >>> corrected = white_balance_from_patch(frame, 300, 200, 40, 30)
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if width <= 0 or height <= 0:
        raise ValueError(f"Patch must be non-empty, got {width}x{height}")

    rgb, alpha = _split_alpha(image)
    h, w = rgb.shape[:2]

    x1, y1 = max(0, x), max(0, y)
    x2, y2 = min(w, x + width), min(h, y + height)
    if x1 >= x2 or y1 >= y2:
        raise ValueError(
            f"Patch ({x}, {y}, {width}, {height}) lies outside the image ({w}x{h})"
        )

    patch = rgb[y1:y2, x1:x2].astype(np.float32)
    means = np.array([patch[:, :, c].mean() for c in range(3)])
    means[means <= 0] = 1.0

    result = _apply_gains(rgb, means[1] / means)

    if alpha is not None:
        result = np.concatenate([result, alpha], axis=2)
    return result


def adjust_temperature(
    image: np.ndarray,
    temperature: float = 0.0,
    tint: float = 0.0,
) -> np.ndarray:
    """
    Shift colour temperature and tint by hand.

    Args:
        image: Input image
        temperature: -100 (cooler, bluer) to +100 (warmer, more orange)
        tint: -100 (greener) to +100 (more magenta)

    Returns:
        Adjusted image
    """
    if not -100 <= temperature <= 100:
        raise ValueError(f"temperature must be between -100 and 100, got {temperature}")
    if not -100 <= tint <= 100:
        raise ValueError(f"tint must be between -100 and 100, got {tint}")

    rgb, alpha = _split_alpha(image)
    adjusted = rgb.astype(np.float32)

    # Warmth trades blue against red; tint trades green against the other two
    adjusted[:, :, 0] += temperature * 0.6
    adjusted[:, :, 2] -= temperature * 0.6
    adjusted[:, :, 1] -= tint * 0.4
    adjusted[:, :, 0] += tint * 0.2
    adjusted[:, :, 2] += tint * 0.2

    result = np.clip(adjusted, 0, 255).astype(np.uint8)

    if alpha is not None:
        result = np.concatenate([result, alpha], axis=2)
    return result
