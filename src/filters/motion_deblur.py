"""
Motion Deblur - Wiener deconvolution.

Deconvolution tries to invert a blur. Doing so naively divides by the blur's
frequency response, which is near zero at some frequencies - so noise at those
frequencies is amplified without limit. The Wiener filter tempers the division
with a noise term:

    F = G * conj(H) / (|H|^2 + K)

``K`` is ``noise_power``. Raise it on noisy footage to trade sharpness for
stability; lower it on clean footage to recover more detail.

Two caveats worth stating plainly:

    - You must supply the right point spread function. A guessed length or
      angle produces confident-looking detail that is not in the original.
    - Deconvolution assumes one uniform blur across the frame. A scene where
      only one object moved needs that object isolated first, via an ROI.
"""

from typing import Optional, Sequence, Tuple

import cv2
import numpy as np


def motion_blur_psf(length: float = 15.0, angle: float = 0.0) -> np.ndarray:
    """
    Build a linear motion blur point spread function.

    Args:
        length: Blur extent in pixels
        angle: Direction in degrees, 0 = horizontal, increasing
               counter-clockwise

    Returns:
        Normalized float32 PSF that sums to 1

    Example:
        >>> psf = motion_blur_psf(length=21, angle=30)
    """
    if length < 1:
        raise ValueError(f"length must be at least 1, got {length}")

    size = int(np.ceil(length)) | 1  # odd, so there is a true centre
    psf = np.zeros((size, size), dtype=np.float32)

    centre = size // 2
    radians = np.deg2rad(angle)
    # Negative sin because image rows run downwards
    dx = np.cos(radians) * (length - 1) / 2.0
    dy = -np.sin(radians) * (length - 1) / 2.0

    cv2.line(
        psf,
        (int(round(centre - dx)), int(round(centre - dy))),
        (int(round(centre + dx)), int(round(centre + dy))),
        1.0,
        thickness=1,
        lineType=cv2.LINE_AA,
    )

    total = psf.sum()
    if total <= 0:
        psf[centre, centre] = 1.0
        return psf

    return psf / total


def defocus_psf(radius: float = 5.0) -> np.ndarray:
    """
    Build a defocus (circular aperture) point spread function.

    Args:
        radius: Blur circle radius in pixels

    Returns:
        Normalized float32 PSF that sums to 1
    """
    if radius < 1:
        raise ValueError(f"radius must be at least 1, got {radius}")

    size = int(np.ceil(radius)) * 2 + 1
    centre = size // 2

    yy, xx = np.ogrid[0:size, 0:size]
    disc = (((yy - centre) ** 2 + (xx - centre) ** 2) <= radius ** 2).astype(np.float32)

    return disc / disc.sum()


def apply_psf(image: np.ndarray, psf: np.ndarray) -> np.ndarray:
    """
    Convolve an image with a PSF - the forward operation deconvolution undoes.

    Useful for previewing what a PSF represents, and for building test cases
    with a known blur.

    Args:
        image: Input image
        psf: Point spread function

    Returns:
        Blurred image in uint8
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")

    img = image.astype(np.uint8) if image.dtype != np.uint8 else image
    blurred = cv2.filter2D(img.astype(np.float32), cv2.CV_32F, psf,
                           borderType=cv2.BORDER_REFLECT)
    return np.clip(blurred, 0, 255).astype(np.uint8)


def _psf_transfer_function(psf: np.ndarray, shape: Tuple[int, int]) -> np.ndarray:
    """
    Pad a PSF to the image size and transform it, keeping its centre at the
    origin so the deconvolved result is not spatially shifted.
    """
    padded = np.zeros(shape, dtype=np.float32)
    kh, kw = psf.shape

    if kh > shape[0] or kw > shape[1]:
        raise ValueError(
            f"PSF ({kw}x{kh}) is larger than the image ({shape[1]}x{shape[0]})"
        )

    padded[:kh, :kw] = psf
    padded = np.roll(padded, -(kh // 2), axis=0)
    padded = np.roll(padded, -(kw // 2), axis=1)

    return np.fft.fft2(padded)


def wiener_deconvolution(
    image: np.ndarray,
    psf: np.ndarray,
    noise_power: float = 0.01,
) -> np.ndarray:
    """
    Deconvolve an image with a known PSF using a Wiener filter.

    Args:
        image: Blurred image (RGB, RGBA, or grayscale). Color channels are
               deconvolved independently.
        psf: Point spread function, as built by ``motion_blur_psf`` or
             ``defocus_psf``
        noise_power: Regularization term. Too small amplifies noise into
                     ripples; too large leaves the image blurred.

    Returns:
        Deconvolved image in uint8, same channel count as the input
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if psf is None or psf.size == 0:
        raise ValueError("PSF is empty")
    if noise_power <= 0:
        raise ValueError(f"noise_power must be positive, got {noise_power}")

    img = image.astype(np.uint8) if image.dtype != np.uint8 else image

    if psf.shape[0] > img.shape[0] or psf.shape[1] > img.shape[1]:
        raise ValueError(
            f"PSF ({psf.shape[1]}x{psf.shape[0]}) is larger than the image "
            f"({img.shape[1]}x{img.shape[0]})"
        )

    if img.ndim == 3 and img.shape[2] == 4:
        rgb, alpha = img[:, :, :3], img[:, :, 3:4]
    else:
        rgb, alpha = img, None

    psf = psf.astype(np.float32)
    total = psf.sum()
    if total > 0:
        psf = psf / total

    # The FFT treats the image as tiling the plane, so the left edge is
    # convolved with the right edge. Reflect-padding first, and cropping
    # afterwards, keeps that wraparound out of the visible result.
    pad_y, pad_x = psf.shape[0], psf.shape[1]

    if rgb.ndim == 2:
        channels = [rgb]
    else:
        channels = [rgb[:, :, c] for c in range(rgb.shape[2])]

    padded_shape = (rgb.shape[0] + 2 * pad_y, rgb.shape[1] + 2 * pad_x)
    transfer = _psf_transfer_function(psf, padded_shape)
    # The Wiener kernel, identical for every channel
    kernel = np.conj(transfer) / (np.abs(transfer) ** 2 + noise_power)

    restored = []
    for channel in channels:
        padded = np.pad(
            channel.astype(np.float32),
            ((pad_y, pad_y), (pad_x, pad_x)),
            mode='reflect',
        )
        deconvolved = np.real(np.fft.ifft2(np.fft.fft2(padded) * kernel))
        restored.append(deconvolved[pad_y:pad_y + rgb.shape[0],
                                    pad_x:pad_x + rgb.shape[1]])

    if rgb.ndim == 2:
        result = np.clip(restored[0], 0, 255).astype(np.uint8)
    else:
        result = np.clip(np.stack(restored, axis=2), 0, 255).astype(np.uint8)

    if alpha is not None:
        result = np.concatenate([result, alpha], axis=2)

    return result


def deblur_motion(
    image: np.ndarray,
    length: float = 15.0,
    angle: float = 0.0,
    noise_power: float = 0.01,
) -> np.ndarray:
    """
    Remove linear motion blur of a known length and direction.

    Args:
        image: Blurred image
        length: Motion extent in pixels
        angle: Motion direction in degrees, 0 = horizontal
        noise_power: Wiener regularization term

    Returns:
        Deblurred image in uint8

    Example:
        >>> sharper = deblur_motion(frame, length=21, angle=8, noise_power=0.02)
    """
    return wiener_deconvolution(image, motion_blur_psf(length, angle), noise_power)


def deblur_defocus(
    image: np.ndarray,
    radius: float = 5.0,
    noise_power: float = 0.01,
) -> np.ndarray:
    """
    Remove defocus blur of a known radius.

    Args:
        image: Blurred image
        radius: Defocus circle radius in pixels
        noise_power: Wiener regularization term

    Returns:
        Deblurred image in uint8
    """
    return wiener_deconvolution(image, defocus_psf(radius), noise_power)


def focus_score(image: np.ndarray) -> float:
    """
    Score how sharp an image is, by the variance of its Laplacian.

    Comparable only between versions of the same image - it says nothing in
    absolute terms. Use it to rank the results of ``deblur_sweep``.

    Args:
        image: Input image

    Returns:
        Focus score; higher is sharper
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")

    img = image.astype(np.uint8) if image.dtype != np.uint8 else image
    if img.ndim == 3:
        gray = cv2.cvtColor(img[:, :, :3], cv2.COLOR_RGB2GRAY)
    else:
        gray = img

    return float(cv2.Laplacian(gray, cv2.CV_32F).var())


def deblur_sweep(
    image: np.ndarray,
    lengths: Sequence[float],
    angles: Sequence[float],
    noise_power: float = 0.01,
) -> np.ndarray:
    """
    Render a labelled grid of motion deblur results across PSF parameters.

    The blur's true length and angle cannot be read off an image reliably -
    scene content with strong directional structure defeats the usual spectral
    estimators. Sweeping the parameters and judging the results by eye is the
    honest approach, and the one Amped FIVE's preview encourages.

    Args:
        image: Blurred image
        lengths: Motion lengths to try
        angles: Motion angles to try, in degrees
        noise_power: Wiener regularization term

    Returns:
        Grid image showing every combination, each labelled with its parameters

    Example:
        >>> grid = deblur_sweep(frame, lengths=[9, 15, 21], angles=[0, 30, 60])
    """
    import math

    combinations = [(length, angle) for length in lengths for angle in angles]
    if not combinations:
        raise ValueError("lengths and angles must each contain at least one value")

    n = len(combinations)
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)

    h, w = image.shape[:2]
    thumb_h, thumb_w = h // rows, w // cols

    grid = np.zeros((thumb_h * rows, thumb_w * cols, 3), dtype=np.uint8)

    for index, (length, angle) in enumerate(combinations):
        restored = deblur_motion(image, length=length, angle=angle,
                                 noise_power=noise_power)
        if restored.ndim == 2:
            restored = cv2.cvtColor(restored, cv2.COLOR_GRAY2RGB)
        elif restored.shape[2] == 4:
            restored = restored[:, :, :3]

        thumb = cv2.resize(restored, (thumb_w, thumb_h))

        row, col = divmod(index, cols)
        y1, x1 = row * thumb_h, col * thumb_w
        grid[y1:y1 + thumb_h, x1:x1 + thumb_w] = thumb

        cv2.putText(grid, f"L={length}, a={angle}", (x1 + 5, y1 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    return grid
