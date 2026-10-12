"""
Motion Deblur - Wiener deconvolution.

Deconvolution tries to invert a blur. Doing so naively divides by the blur's
frequency response, which is near zero at some frequencies - so noise at those
frequencies is amplified without limit. The Wiener filter tempers the division
with a noise term:

    F = G * conj(H) / (|H|^2 + K)

``K`` is ``noise_power``. Raise it on noisy footage to trade sharpness for
stability; lower it on clean footage to recover more detail.

That is one linear filter, and the default. ``solver='richardson_lucy'`` is
the alternative for noisy, compressed footage: iterative, in linear light,
unable to overshoot below black. It recovers more there and is no longer a
fixed weighted sum of the input - see ``richardson_lucy_deconvolution``.

Two caveats worth stating plainly:

    - You must supply the right point spread function. A guessed length or
      angle produces confident-looking detail that is not in the original.
    - Deconvolution assumes one uniform blur across the frame. A scene where
      only one object moved needs that object isolated first, via an ROI.
"""

from typing import Dict, Optional, Sequence, Tuple

import cv2
import numpy as np
from scipy.fft import irfft2, rfft2


def _subpixel_grid(half: int) -> Tuple[np.ndarray, np.ndarray, int]:
    """
    Sample positions for area-sampling a PSF of ``2 * half + 1`` pixels a side.

    Each pixel is split into ``oversample`` sub-samples per axis, so a shape
    that covers part of a pixel contributes part of its weight. Returns the
    x and y coordinates of every sub-sample, relative to the PSF centre, and
    the oversampling factor.
    """
    size = 2 * half + 1
    # Fine sampling where the PSF is small and every fraction of a pixel
    # matters; coarser on a large one, where it would cost memory for nothing.
    oversample = int(np.clip(1024 // size, 3, 8))
    coords = (np.arange(size * oversample) + 0.5) / oversample - 0.5 - half
    xx, yy = np.meshgrid(coords, coords)
    return xx, yy, oversample


def _area_sample(coverage: np.ndarray, oversample: int) -> np.ndarray:
    """Average sub-sample coverage down to pixels, and normalize to sum 1."""
    size = coverage.shape[0] // oversample
    psf = coverage.reshape(size, oversample, size, oversample).mean(axis=(1, 3))

    # Drop outer rings nothing reached, so the PSF is no larger than its blur
    while psf.shape[0] > 1 and not (psf[0].any() or psf[-1].any()
                                    or psf[:, 0].any() or psf[:, -1].any()):
        psf = psf[1:-1, 1:-1]

    return (psf / psf.sum()).astype(np.float32)


def motion_blur_psf(
    length: float = 15.0,
    angle: float = 0.0,
    thickness: float = 1.0,
) -> np.ndarray:
    """
    Build a linear motion blur point spread function.

    The PSF is the area of each pixel covered by a ``length`` x ``thickness``
    rectangle turned to ``angle``, so fractional lengths and any angle give a
    distinct PSF. That matters more than it sounds: a PSF two pixels too long,
    or five degrees off, restores worse than not deblurring at all.

    Args:
        length: Blur extent in pixels - how far a point moved during the
                exposure, which is the distance between its two ghosts
        angle: Direction in degrees, 0 = horizontal, increasing
               counter-clockwise
        thickness: Width of the streak in pixels. 1 is pure linear motion;
                   raise it when the streak of a point light is visibly wider
                   than a pixel, which means the frame is also slightly soft.

    Returns:
        Normalized float32 PSF that sums to 1

    Example:
        >>> psf = motion_blur_psf(length=21.4, angle=30)
    """
    if length < 1:
        raise ValueError(f"length must be at least 1, got {length}")
    if thickness <= 0:
        raise ValueError(f"thickness must be positive, got {thickness}")

    half = int(np.ceil(np.hypot(length, thickness) / 2.0))
    xx, yy, oversample = _subpixel_grid(half)

    radians = np.deg2rad(angle)
    # Image rows run downwards, so counter-clockwise on screen is -sin in y
    along = xx * np.cos(radians) - yy * np.sin(radians)
    across = xx * np.sin(radians) + yy * np.cos(radians)

    # Ramp across one sub-sample at each edge rather than a hard inside/outside
    # test, so the PSF changes continuously with length and angle
    coverage = (np.clip((length / 2.0 - np.abs(along)) * oversample + 0.5, 0, 1)
                * np.clip((thickness / 2.0 - np.abs(across)) * oversample + 0.5, 0, 1))

    return _area_sample(coverage, oversample)


def defocus_psf(radius: float = 5.0) -> np.ndarray:
    """
    Build a defocus (circular aperture) point spread function.

    Area-sampled like ``motion_blur_psf``: a pixel the circle's edge passes
    through carries the fraction of it the circle covers. Mild defocus - a
    radius of one to three pixels - is the common case on CCTV, and there a
    hard-edged disc cannot tell 1.0 from 1.4.

    Args:
        radius: Blur circle radius in pixels

    Returns:
        Normalized float32 PSF that sums to 1
    """
    # Below half a pixel the circle sits inside one pixel: there is no blur
    # to remove, and deconvolving it would only amplify noise.
    if radius < 0.5:
        raise ValueError(f"radius must be at least 0.5, got {radius}")

    xx, yy, oversample = _subpixel_grid(int(np.ceil(radius)))
    coverage = np.clip((radius - np.hypot(xx, yy)) * oversample + 0.5, 0, 1)

    return _area_sample(coverage, oversample)


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

    return rfft2(padded)


def _extend_periodic(channel: np.ndarray, margin: int) -> np.ndarray:
    """
    Extend a channel so that it tiles the plane without a seam.

    The FFT treats the image as repeating, so its right edge runs straight
    into its left edge. Where those differ there is a step that was never in
    the scene, and deconvolution rings off it across the whole frame - not
    only near the border. Mirroring the edges does not help: a mirrored
    margin is smooth where it meets the image and still ends on a different
    value than the opposite side starts with.

    This appends a margin after the image in which each row (then column)
    fades from the last one to the first. The image itself is untouched and
    sits at the origin, so the result is cropped back with ``[:h, :w]``.

    Args:
        channel: Single channel, float
        margin: Smallest margin to add, in pixels. Rounded up to a size the
                FFT is fast on.
    """
    for axis in (0, 1):
        length = channel.shape[axis]
        gap = cv2.getOptimalDFTSize(length + margin) - length

        last = np.take(channel, [-1], axis=axis)
        first = np.take(channel, [0], axis=axis)
        ramp = 0.5 - 0.5 * np.cos(np.pi * (np.arange(gap) + 0.5) / gap)
        ramp = ramp.reshape((-1, 1) if axis == 0 else (1, -1))

        channel = np.concatenate([channel, last + (first - last) * ramp], axis=axis)

    return channel


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

    if rgb.ndim == 2:
        channels = [rgb]
    else:
        channels = [rgb[:, :, c] for c in range(rgb.shape[2])]

    height, width = rgb.shape[:2]
    margin = 2 * max(psf.shape)

    kernel = None
    restored = []
    for channel in channels:
        # A blur moves light around without adding or removing any, so the
        # frame's mean is known exactly. Deconvolving around it keeps the
        # noise term, which scales the mean by 1 / (1 + K), from darkening
        # the frame.
        mean = float(channel.mean())
        extended = _extend_periodic(channel.astype(np.float32) - mean, margin)

        if kernel is None:
            # The Wiener kernel, identical for every channel
            transfer = _psf_transfer_function(psf, extended.shape)
            kernel = np.conj(transfer) / (np.abs(transfer) ** 2 + noise_power)

        deconvolved = irfft2(rfft2(extended) * kernel, s=extended.shape)
        restored.append(deconvolved[:height, :width] + mean)

    if rgb.ndim == 2:
        result = np.clip(np.rint(restored[0]), 0, 255).astype(np.uint8)
    else:
        result = np.clip(np.rint(np.stack(restored, axis=2)), 0, 255).astype(np.uint8)

    if alpha is not None:
        result = np.concatenate([result, alpha], axis=2)

    return result


SOLVERS = ('wiener', 'richardson_lucy')

# sRGB decoding, by table: display values to linear light
_TO_LINEAR = np.where(
    np.arange(256) / 255.0 <= 0.04045,
    np.arange(256) / 255.0 / 12.92,
    ((np.arange(256) / 255.0 + 0.055) / 1.055) ** 2.4,
).astype(np.float32)


def _to_display(linear: np.ndarray) -> np.ndarray:
    """Linear light back to sRGB display values, 0-255."""
    linear = np.clip(linear, 0.0, 1.0)
    return np.where(linear <= 0.0031308, linear * 12.92,
                    1.055 * np.power(linear, 1 / 2.4) - 0.055) * 255.0


def _richardson_lucy_channel(
    observed: np.ndarray,
    psf: np.ndarray,
    iterations: int,
    smoothing: float,
) -> np.ndarray:
    """
    Richardson-Lucy on one channel of linear light.

    The frame is set in a margin one PSF wide that carries no weight: light
    from outside the frame was blurred into it, and here the margin is free
    to become whatever explains the pixels near the border, instead of being
    assumed. Nothing in the margin is returned.
    """
    height, width = observed.shape
    pad_y, pad_x = psf.shape
    shape = (cv2.getOptimalDFTSize(height + 2 * pad_y),
             cv2.getOptimalDFTSize(width + 2 * pad_x))
    inside = (slice(pad_y, pad_y + height), slice(pad_x, pad_x + width))

    data = np.zeros(shape, dtype=np.float32)
    weight = np.zeros(shape, dtype=np.float32)
    data[inside] = observed
    weight[inside] = 1.0

    blur = _psf_transfer_function(psf, shape).astype(np.complex64)
    unblur = np.conj(blur)

    def convolve(values: np.ndarray, transfer: np.ndarray) -> np.ndarray:
        return irfft2(rfft2(values) * transfer, s=shape)

    # How much of each pixel's light lands inside the frame. Beyond the
    # PSF's reach of the frame it is none, and the estimate there is left be.
    coverage = convolve(weight, unblur)
    reached = coverage > 1e-3
    scale = np.where(reached, 1.0 / np.maximum(coverage, 1e-3), 0.0).astype(np.float32)

    estimate = np.full(shape, max(float(observed.mean()), 1e-4), dtype=np.float32)

    for _ in range(iterations):
        predicted = np.maximum(convolve(estimate, blur), 1e-6)
        correction = convolve(weight * data / predicted, unblur) * scale

        # Total-variation term (Dey et al. 2006): it resists the pixel-scale
        # oscillation that noise turns into as the iterations go on, and
        # leaves edges, which are a large step in one place
        across = np.roll(estimate, -1, axis=1) - estimate
        down = np.roll(estimate, -1, axis=0) - estimate
        size = np.sqrt(across * across + down * down + 1e-8)
        across /= size
        down /= size
        curvature = (across - np.roll(across, 1, axis=1)
                     + down - np.roll(down, 1, axis=0))
        correction /= np.maximum(1.0 - smoothing * curvature, 0.5)

        estimate = np.where(reached, estimate * correction, estimate).astype(np.float32)

    return estimate[inside]


def richardson_lucy_deconvolution(
    image: np.ndarray,
    psf: np.ndarray,
    noise_power: float = 0.01,
    iterations: int = 40,
) -> np.ndarray:
    """
    Deconvolve an image with a known PSF by Richardson-Lucy iteration.

    Where the Wiener filter divides the spectrum once, this starts from a
    flat frame and repeatedly corrects it: blur the current estimate, compare
    with the recorded frame, and push the estimate towards agreement. Three
    things follow from working that way, and they are why it does better on
    compressed, noisy footage:

        - The estimate can never go negative. Most of a Wiener result's
          ringing is the filter overshooting below black beside something
          bright - a headlight, a lit window - and that cannot happen here.
        - It works in linear light, where a blur actually adds up. Recorded
          values are gamma-encoded; they are decoded as sRGB first and
          encoded again afterwards. This is right for a blur made by a lens
          or a moving subject, and wrong for one applied to stored values by
          software - on those, ``wiener_deconvolution`` is the better match.
        - What lay outside the frame is estimated, not assumed.

    The price is that the result is no longer one fixed weighted sum of the
    input pixels. It is still fully determined by the frame and the
    parameters, and repeats exactly; but "each output pixel is this
    combination of input pixels" can be said of ``wiener_deconvolution`` and
    cannot be said of this. It also takes tens of times as long: seconds
    on a CCTV frame, so crop to the subject first.

    Args:
        image: Blurred image (RGB, RGBA, or grayscale). Color channels are
               deconvolved independently.
        psf: Point spread function
        noise_power: How strongly noise is held down, on the same scale as
                     ``wiener_deconvolution`` and with the same meaning:
                     raise it on noisy footage, lower it on clean.
        iterations: Number of correction passes. More recovers finer detail
                    and, on noisy footage with ``noise_power`` too low,
                    more noise with it.

    Returns:
        Deconvolved image in uint8, same channel count as the input
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if psf is None or psf.size == 0:
        raise ValueError("PSF is empty")
    if noise_power <= 0:
        raise ValueError(f"noise_power must be positive, got {noise_power}")
    if iterations < 1:
        raise ValueError(f"iterations must be at least 1, got {iterations}")

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

    # Measured, not derived: over simulated CCTV captures this ratio puts
    # the best result at the same noise_power that suits the Wiener filter
    smoothing = 0.6 * float(noise_power)

    linear = _TO_LINEAR[rgb]
    if rgb.ndim == 2:
        restored = _richardson_lucy_channel(linear, psf, int(iterations), smoothing)
    else:
        restored = np.stack(
            [_richardson_lucy_channel(linear[:, :, c], psf, int(iterations), smoothing)
             for c in range(rgb.shape[2])], axis=2)

    result = np.clip(np.rint(_to_display(restored)), 0, 255).astype(np.uint8)

    if alpha is not None:
        result = np.concatenate([result, alpha], axis=2)

    return result


def deconvolve(
    image: np.ndarray,
    psf: np.ndarray,
    noise_power: float = 0.01,
    solver: str = 'wiener',
    iterations: int = 40,
) -> np.ndarray:
    """
    Deconvolve with a known PSF, by the named solver.

    Args:
        image: Blurred image
        psf: Point spread function
        noise_power: Regularization, with the same meaning for both solvers
        solver: 'wiener' - one linear filter, fast, and the default - or
                'richardson_lucy', iterative and better on noisy, compressed
                footage; see ``richardson_lucy_deconvolution`` for what that
                costs
        iterations: Correction passes, for 'richardson_lucy' only

    Returns:
        Deconvolved image in uint8
    """
    if solver == 'wiener':
        return wiener_deconvolution(image, psf, noise_power)
    if solver == 'richardson_lucy':
        return richardson_lucy_deconvolution(image, psf, noise_power, iterations)
    raise ValueError(f"solver must be one of {', '.join(SOLVERS)}, got {solver!r}")


def deblur_motion(
    image: np.ndarray,
    length: float = 15.0,
    angle: float = 0.0,
    noise_power: float = 0.01,
    thickness: float = 1.0,
    solver: str = 'wiener',
    iterations: int = 40,
) -> np.ndarray:
    """
    Remove linear motion blur of a known length and direction.

    Args:
        image: Blurred image
        length: Motion extent in pixels - the distance between the two ghosts
                of one point, such as the corners of a plate
        angle: Motion direction in degrees, 0 = horizontal
        noise_power: Regularization term; raise it on noisy footage
        thickness: Width of the streak in pixels; see ``motion_blur_psf``
        solver: 'wiener' or 'richardson_lucy'; see ``deconvolve``
        iterations: Correction passes, for 'richardson_lucy' only

    Returns:
        Deblurred image in uint8

    Example:
        >>> sharper = deblur_motion(frame, length=21.5, angle=8, noise_power=0.02)
    """
    return deconvolve(image, motion_blur_psf(length, angle, thickness),
                      noise_power, solver, iterations)


def deblur_defocus(
    image: np.ndarray,
    radius: float = 5.0,
    noise_power: float = 0.01,
    solver: str = 'wiener',
    iterations: int = 40,
) -> np.ndarray:
    """
    Remove defocus blur of a known radius.

    Args:
        image: Blurred image
        radius: Defocus circle radius in pixels
        noise_power: Regularization term; raise it on noisy footage
        solver: 'wiener' or 'richardson_lucy'; see ``deconvolve``
        iterations: Correction passes, for 'richardson_lucy' only

    Returns:
        Deblurred image in uint8
    """
    return deconvolve(image, defocus_psf(radius), noise_power, solver, iterations)


def focus_score(image: np.ndarray) -> float:
    """
    Score how sharp an image is, by the variance of its Laplacian.

    Comparable only between versions of the same image - it says nothing in
    absolute terms. It rises with ringing as readily as with recovered detail,
    so a deconvolution with the wrong PSF can outscore the right one: do not
    choose a PSF by it.

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


# Longest side of a contact sheet before its tiles are scaled down. Three CCTV
# frames across fit; anything larger is a frame that should be cropped first.
_BOARD_LIMIT = 2400
_LABEL_STRIP = 18


def _contact_sheet(tiles: Sequence[np.ndarray], labels: Sequence[str],
                   cols: int) -> np.ndarray:
    """
    Lay equally sized results out as a labelled board.

    Tiles are kept at full resolution wherever the board allows. Ringing and
    amplified noise are what separate a right PSF from a nearly right one,
    and both live at the pixel level: a board of thumbnails averages them
    away and makes every setting look acceptable. Each label sits in a strip
    above its tile rather than over it, so no pixel of a result is hidden.
    """
    rows = -(-len(tiles) // cols)
    height, width = tiles[0].shape[:2]
    scale = min(1.0, _BOARD_LIMIT / (width * cols), _BOARD_LIMIT / (height * rows))
    tile_w, tile_h = max(int(width * scale), 1), max(int(height * scale), 1)

    board = np.zeros((rows * (tile_h + _LABEL_STRIP), cols * tile_w, 3), dtype=np.uint8)
    font = cv2.FONT_HERSHEY_SIMPLEX

    for index, (tile, label) in enumerate(zip(tiles, labels)):
        if tile.ndim == 2:
            tile = cv2.cvtColor(tile, cv2.COLOR_GRAY2RGB)
        elif tile.shape[2] == 4:
            tile = tile[:, :, :3]
        if scale < 1.0:
            tile = cv2.resize(tile, (tile_w, tile_h), interpolation=cv2.INTER_AREA)

        row, col = divmod(index, cols)
        y, x = row * (tile_h + _LABEL_STRIP), col * tile_w
        board[y + _LABEL_STRIP:y + _LABEL_STRIP + tile_h, x:x + tile_w] = tile

        size = 0.45
        text_width = cv2.getTextSize(label, font, size, 1)[0][0]
        if text_width > tile_w - 6:
            size *= max(tile_w - 6, 1) / text_width
        cv2.putText(board, label, (x + 3, y + _LABEL_STRIP - 5), font, size,
                    (255, 255, 255), 1, cv2.LINE_AA)

    return board


def deblur_sweep(
    image: np.ndarray,
    lengths: Sequence[float],
    angles: Sequence[float],
    noise_power: float = 0.01,
    thickness: float = 1.0,
    solver: str = 'wiener',
    iterations: int = 40,
) -> np.ndarray:
    """
    Render a labelled grid of motion deblur results across PSF parameters.

    The blur's true length and angle cannot be read off an image reliably -
    scene content with strong directional structure defeats the usual spectral
    estimators. Sweeping the parameters and judging the results by eye is the
    honest approach, and the one Amped FIVE's preview encourages.

    Crop to the subject first. Tiles are shown at full resolution while the
    board stays under 2400 pixels a side, and scaled down beyond that - which
    hides exactly the ringing that tells two settings apart.

    Args:
        image: Blurred image
        lengths: Motion lengths to try
        angles: Motion angles to try, in degrees
        noise_power: Regularization term
        thickness: Width of the streak in pixels; see ``motion_blur_psf``
        solver: 'wiener' or 'richardson_lucy'; see ``deconvolve``
        iterations: Correction passes, for 'richardson_lucy' only

    Returns:
        Grid image showing every combination, each labelled with its parameters

    Example:
        >>> grid = deblur_sweep(frame, lengths=[9, 15, 21], angles=[0, 30, 60])
    """
    combinations = [(length, angle) for length in lengths for angle in angles]
    if not combinations:
        raise ValueError("lengths and angles must each contain at least one value")

    tiles = [deblur_motion(image, length=length, angle=angle,
                           noise_power=noise_power, thickness=thickness,
                           solver=solver, iterations=iterations)
             for length, angle in combinations]
    labels = [f"length {length:g}  angle {angle:g}" for length, angle in combinations]

    # One row per length, so reading across a row is reading across angles
    return _contact_sheet(tiles, labels, len(angles))


def deblur_motion_grid(
    image: np.ndarray,
    length: float = 15.0,
    angle: float = 0.0,
    length_step: float = 2.0,
    angle_step: float = 5.0,
    noise_power: float = 0.01,
    thickness: float = 1.0,
    solver: str = 'wiener',
    iterations: int = 40,
) -> np.ndarray:
    """
    Contact sheet of motion deblurs around a first estimate.

    A line drawn between two ghosts gives the length and angle to within a
    pixel or two and a few degrees, and that is not close enough: the right
    PSF and one two pixels longer are the difference between a readable plate
    and a worse one. This lays the estimate out beside its neighbours - one
    step shorter and longer down the rows, one step either way in angle across
    the columns - so the choice is made by looking at all nine.

    Halve the steps and run it again around the best tile to close in.

    Args:
        image: Blurred image; crop to the subject first
        length: Estimated motion extent in pixels, the centre of the board
        angle: Estimated direction in degrees, the centre of the board
        length_step: Pixels between rows
        angle_step: Degrees between columns
        noise_power: Regularization term, the same on every tile
        thickness: Width of the streak in pixels; see ``motion_blur_psf``
        solver: 'wiener' or 'richardson_lucy'; see ``deconvolve``. The PSF
                that is right for one solver is right for the other, so the
                fast one is the one to search with.
        iterations: Correction passes, for 'richardson_lucy' only

    Returns:
        Board of up to nine results, each labelled with its length and angle

    Example:
        >>> board = deblur_motion_grid(plate, length=22.5, angle=12, length_step=1)
    """
    if length_step <= 0 or angle_step <= 0:
        raise ValueError("length_step and angle_step must be positive, got "
                         f"{length_step} and {angle_step}")

    # A length under one pixel is no blur at all, so that row is left out
    lengths = [value for value in (length - length_step, length, length + length_step)
               if value >= 1]
    angles = [angle - angle_step, angle, angle + angle_step]
    return deblur_sweep(image, lengths, angles, noise_power, thickness,
                        solver, iterations)


def deblur_defocus_grid(
    image: np.ndarray,
    radius: float = 5.0,
    radius_step: float = 1.0,
    noise_power: float = 0.01,
    solver: str = 'wiener',
    iterations: int = 40,
) -> np.ndarray:
    """
    Contact sheet of defocus deblurs around a first estimate.

    Defocus leaves nothing to draw a line along, so the radius is found by
    trying it. Radius runs down the rows; across the columns the noise term is
    a third of, equal to, and three times the value given, because the two
    trade against each other - a radius that looks wrong at one noise setting
    can be the right one at another.

    Args:
        image: Blurred image; crop to the subject first
        radius: Estimated blur circle radius in pixels, the centre of the board
        radius_step: Pixels between rows
        noise_power: Regularization term for the middle column
        solver: 'wiener' or 'richardson_lucy'; see ``deconvolve``
        iterations: Correction passes, for 'richardson_lucy' only

    Returns:
        Board of up to nine results, each labelled with its radius and noise

    Example:
        >>> board = deblur_defocus_grid(plate, radius=3, radius_step=0.5)
    """
    if radius_step <= 0:
        raise ValueError(f"radius_step must be positive, got {radius_step}")
    if noise_power <= 0:
        raise ValueError(f"noise_power must be positive, got {noise_power}")

    radii = [value for value in (radius - radius_step, radius, radius + radius_step)
             if value >= 0.5]
    if not radii:
        raise ValueError(f"radius must be at least 0.5, got {radius}")
    noises = [noise_power / 3.0, noise_power, noise_power * 3.0]

    tiles = [deblur_defocus(image, radius=r, noise_power=k, solver=solver,
                            iterations=iterations)
             for r in radii for k in noises]
    labels = [f"radius {r:g}  noise {k:.2g}" for r in radii for k in noises]
    return _contact_sheet(tiles, labels, len(noises))


def motion_from_line(start: Sequence[float], end: Sequence[float]) -> Dict[str, float]:
    """
    Turn a line drawn along a motion streak into ``length`` and ``angle``.

    This is how a motion blur is measured by hand: find one point of the
    scene that the blur has drawn twice - the two ghosts of a plate corner, or
    the two ends of the streak a point light left - and join them. The
    distance is how far the subject moved during the exposure; the direction
    is which way.

    Clicks land on whole pixels, so the result is good to about a pixel and a
    few degrees. Refine it with ``deblur_motion_grid``.

    Args:
        start: One end of the streak, as (x, y)
        end: The other end

    Returns:
        ``{'length': ..., 'angle': ...}``, ready to pass to ``deblur_motion``

    Raises:
        ValueError: If the two points are less than a pixel apart
    """
    dx, dy = float(end[0]) - float(start[0]), float(end[1]) - float(start[1])
    length = float(np.hypot(dx, dy))
    if length < 1:
        raise ValueError("The two ends of the motion line are the same point")

    # Rows run downwards, and a streak has no head or tail: 200 degrees is
    # the same blur as 20
    angle = float(np.rad2deg(np.arctan2(-dy, dx))) % 180.0
    return {'length': round(length, 1), 'angle': round(angle, 1) % 180.0}


def psf_preview(psf: np.ndarray, size: int = 160) -> np.ndarray:
    """
    Render a PSF as a picture: white where the blur spread the light.

    A length and an angle are hard to check as numbers and easy to check as a
    shape - the picture should look like the streak a point light left in the
    frame. A small PSF is enlarged by whole pixels without smoothing, so what
    is shown is the kernel itself and not an interpolation of it.

    Args:
        psf: Point spread function
        size: Side of the square picture, in pixels

    Returns:
        ``size`` x ``size`` RGB image in uint8
    """
    if psf is None or psf.size == 0:
        raise ValueError("PSF is empty")

    picture = psf.astype(np.float32)
    kh, kw = picture.shape
    factor = size // max(kh, kw)
    if factor >= 1:
        picture = cv2.resize(picture, (kw * factor, kh * factor),
                             interpolation=cv2.INTER_NEAREST)
    else:
        shrink = size / max(kh, kw)
        picture = cv2.resize(picture, (max(int(kw * shrink), 1), max(int(kh * shrink), 1)),
                             interpolation=cv2.INTER_AREA)

    peak = float(picture.max())
    if peak > 0:
        picture = picture / peak

    canvas = np.zeros((size, size), dtype=np.float32)
    ph, pw = picture.shape
    top, left = (size - ph) // 2, (size - pw) // 2
    canvas[top:top + ph, left:left + pw] = picture

    return cv2.cvtColor(np.rint(canvas * 255).astype(np.uint8), cv2.COLOR_GRAY2RGB)
