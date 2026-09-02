"""
Colour Balance - Per-tonal-range RGB and CMY shifts.

Unlike white balance, which applies one gain to the whole frame, this shifts
shadows, midtones and highlights independently. That matters when a scene is
lit by two sources at once - daylight through a window and tungsten indoors -
where the cast differs by brightness and no single gain corrects both.

Each range is weighted by luminance with overlapping falloffs, so adjustments
blend rather than banding at the boundaries.
"""

from typing import Optional, Sequence, Tuple

import cv2
import numpy as np

_LUMA = np.array([0.299, 0.587, 0.114], dtype=np.float32)


def _split_alpha(image: np.ndarray) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """Separate an alpha channel so it is not colour-shifted."""
    if image.ndim == 3 and image.shape[2] == 4:
        return image[:, :, :3], image[:, :, 3:4]
    return image, None


def _tonal_weights(luminance: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Weight each pixel's membership of shadows, midtones and highlights.

    Gaussian falloffs centred on black, mid-gray and white. They overlap, so a
    pixel part-way between ranges receives a blend of both adjustments.
    """
    normalized = luminance / 255.0

    shadows = np.exp(-(normalized ** 2) / (2 * 0.30 ** 2))
    midtones = np.exp(-((normalized - 0.5) ** 2) / (2 * 0.25 ** 2))
    highlights = np.exp(-((normalized - 1.0) ** 2) / (2 * 0.30 ** 2))

    return shadows, midtones, highlights


def adjust_color_balance(
    image: np.ndarray,
    shadows: Sequence[float] = (0.0, 0.0, 0.0),
    midtones: Sequence[float] = (0.0, 0.0, 0.0),
    highlights: Sequence[float] = (0.0, 0.0, 0.0),
    preserve_luminosity: bool = True,
) -> np.ndarray:
    """
    Shift colour independently across the tonal range.

    Args:
        image: Input image (RGB or RGBA)
        shadows: (red, green, blue) shift for dark tones, each -100 to 100.
                 Positive red adds red, negative adds cyan.
        midtones: Same, for mid tones
        highlights: Same, for bright tones
        preserve_luminosity: Rescale afterwards so overall brightness is
                             unchanged and only the colour moves

    Returns:
        Adjusted image, alpha preserved

    Example:
        >>> # Cool the shadows, warm the highlights
        >>> graded = adjust_color_balance(frame, shadows=(-15, 0, 15),
        ...                               highlights=(15, 5, -10))
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if image.ndim == 2:
        raise ValueError("Colour balance needs a colour image")

    for name, values in (('shadows', shadows), ('midtones', midtones),
                         ('highlights', highlights)):
        if len(values) != 3:
            raise ValueError(f"{name} needs 3 values (r, g, b), got {len(values)}")
        if any(not -100 <= v <= 100 for v in values):
            raise ValueError(f"{name} values must be between -100 and 100")

    rgb, alpha = _split_alpha(image)
    channels = rgb.astype(np.float32)

    luminance = channels @ _LUMA
    weight_shadow, weight_mid, weight_high = _tonal_weights(luminance)

    result = channels.copy()
    for index in range(3):
        # Scaled to 0.8 so a full +/-100 is a strong but not destructive shift
        result[:, :, index] += (
            weight_shadow * shadows[index] * 0.8
            + weight_mid * midtones[index] * 0.8
            + weight_high * highlights[index] * 0.8
        )

    result = np.clip(result, 0, 255)

    if preserve_luminosity:
        new_luminance = result @ _LUMA
        scale = np.divide(
            luminance, new_luminance,
            out=np.ones_like(luminance), where=new_luminance > 1e-6,
        )
        result = np.clip(result * scale[:, :, np.newaxis], 0, 255)

    output = result.astype(np.uint8)

    if alpha is not None:
        output = np.concatenate([output, alpha], axis=2)
    return output


def adjust_cmyk(
    image: np.ndarray,
    cyan: float = 0.0,
    magenta: float = 0.0,
    yellow: float = 0.0,
    black: float = 0.0,
) -> np.ndarray:
    """
    Adjust in subtractive (CMYK) terms, as a print workflow would.

    Cyan opposes red, magenta opposes green and yellow opposes blue, so this is
    the same space as RGB seen from the other side - convenient when matching a
    printed reference.

    Args:
        image: Input image (RGB or RGBA)
        cyan: -100 to 100; positive adds cyan, negative adds red
        magenta: -100 to 100; positive adds magenta, negative adds green
        yellow: -100 to 100; positive adds yellow, negative adds blue
        black: -100 to 100; positive darkens overall

    Returns:
        Adjusted image
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if image.ndim == 2:
        raise ValueError("CMYK adjustment needs a colour image")

    for name, value in (('cyan', cyan), ('magenta', magenta),
                        ('yellow', yellow), ('black', black)):
        if not -100 <= value <= 100:
            raise ValueError(f"{name} must be between -100 and 100, got {value}")

    rgb, alpha = _split_alpha(image)
    channels = rgb.astype(np.float32)

    scale = 2.55
    channels[:, :, 0] -= cyan * scale
    channels[:, :, 1] -= magenta * scale
    channels[:, :, 2] -= yellow * scale
    channels -= black * scale

    result = np.clip(channels, 0, 255).astype(np.uint8)

    if alpha is not None:
        result = np.concatenate([result, alpha], axis=2)
    return result


def channel_mixer(
    image: np.ndarray,
    red: Sequence[float] = (1.0, 0.0, 0.0),
    green: Sequence[float] = (0.0, 1.0, 0.0),
    blue: Sequence[float] = (0.0, 0.0, 1.0),
) -> np.ndarray:
    """
    Rebuild each output channel as a weighted mix of the input channels.

    Lets one channel stand in for another - useful when a cast has destroyed
    one channel but the detail survives in a different one.

    Args:
        image: Input image (RGB or RGBA)
        red: Weights (from_r, from_g, from_b) forming the output red channel
        green: Weights forming the output green channel
        blue: Weights forming the output blue channel

    Returns:
        Adjusted image

    Example:
        >>> # Build a monochrome image from the red channel alone
        >>> mixed = channel_mixer(frame, (1, 0, 0), (1, 0, 0), (1, 0, 0))
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if image.ndim == 2:
        raise ValueError("Channel mixing needs a colour image")

    matrix = np.array([red, green, blue], dtype=np.float32)
    if matrix.shape != (3, 3):
        raise ValueError("Each of red, green and blue needs exactly 3 weights")

    rgb, alpha = _split_alpha(image)
    channels = rgb.astype(np.float32)

    mixed = channels @ matrix.T
    result = np.clip(mixed, 0, 255).astype(np.uint8)

    if alpha is not None:
        result = np.concatenate([result, alpha], axis=2)
    return result
