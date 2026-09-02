"""
Noise Analysis - Estimate noise level, SNR, and map noise across an image.

The global estimate uses Immerkaer's method: convolve with a kernel that
cancels smooth content and doubles as a Laplacian, then take the mean absolute
response. It is fast and needs no reference image.

The local map is the forensically interesting part. Sensor noise should be
roughly uniform across a frame; a region whose noise level differs markedly
from its surroundings came from somewhere else - a different camera, a
different resize, or a denoise pass applied to that region alone.
"""

from typing import Any, Dict, Tuple

import cv2
import numpy as np

# Immerkaer's kernel: zero response to any linear intensity ramp, so what
# survives is noise rather than image structure
_NOISE_KERNEL = np.array([
    [1, -2, 1],
    [-2, 4, -2],
    [1, -2, 1],
], dtype=np.float32)


def _to_gray(image: np.ndarray) -> np.ndarray:
    """Reduce any supported input to single-channel uint8."""
    img = image.astype(np.uint8) if image.dtype != np.uint8 else image

    if img.ndim == 2:
        return img
    if img.shape[2] == 1:
        return img[:, :, 0]
    if img.shape[2] == 4:
        return cv2.cvtColor(img[:, :, :3], cv2.COLOR_RGB2GRAY)
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)


def estimate_noise(image: np.ndarray) -> float:
    """
    Estimate the standard deviation of additive Gaussian noise.

    Args:
        image: Input image (color is converted to luminance)

    Returns:
        Estimated noise sigma in intensity units (0-255 scale)

    Example:
        >>> sigma = estimate_noise(frame)
        >>> sigma > 5  # visibly noisy
        True
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")

    gray = _to_gray(image).astype(np.float32)
    h, w = gray.shape
    if h < 3 or w < 3:
        raise ValueError(f"Image must be at least 3x3, got {w}x{h}")

    response = cv2.filter2D(gray, cv2.CV_32F, _NOISE_KERNEL)
    # Trim the border, where filter2D's edge extension distorts the response
    response = response[1:-1, 1:-1]

    # sqrt(pi/2)/6 converts the mean absolute Laplacian response to a sigma
    return float(np.sqrt(np.pi / 2.0) / 6.0 * np.abs(response).mean())


def estimate_snr(image: np.ndarray) -> float:
    """
    Estimate the signal-to-noise ratio in decibels.

    Uses the image's own standard deviation as the signal level, so a flat
    image scores low no matter how clean it is.

    Args:
        image: Input image

    Returns:
        SNR in dB, or ``float('inf')`` when no noise is detected
    """
    gray = _to_gray(image).astype(np.float32)
    noise = estimate_noise(image)

    if noise <= 0:
        return float('inf')

    signal = float(gray.std())
    if signal <= 0:
        return 0.0

    return float(20.0 * np.log10(signal / noise))


def noise_map(
    image: np.ndarray,
    block_size: int = 32,
    normalize: bool = True,
    upscale: bool = True,
) -> np.ndarray:
    """
    Measure noise block by block and render the result as an image.

    Args:
        image: Input image
        block_size: Side length of each analysis block. Smaller gives finer
                    localisation but a noisier estimate per block.
        normalize: Stretch the map to fill 0-255
        upscale: Resize the block grid back to the input's dimensions

    Returns:
        Noise map as single-channel uint8. Bright means noisier.
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if block_size < 4:
        raise ValueError(f"block_size must be at least 4, got {block_size}")

    gray = _to_gray(image).astype(np.float32)
    h, w = gray.shape
    rows, cols = h // block_size, w // block_size
    if rows < 1 or cols < 1:
        raise ValueError(f"block_size {block_size} is larger than the image ({w}x{h})")

    response = np.abs(cv2.filter2D(gray, cv2.CV_32F, _NOISE_KERNEL))
    trimmed = response[:rows * block_size, :cols * block_size]
    blocks = trimmed.reshape(rows, block_size, cols, block_size).mean(axis=(1, 3))
    blocks = blocks * (np.sqrt(np.pi / 2.0) / 6.0)

    if normalize:
        peak = blocks.max()
        blocks = blocks * (255.0 / peak) if peak > 0 else blocks

    result = np.clip(blocks, 0, 255).astype(np.uint8)

    if upscale:
        result = cv2.resize(result, (w, h), interpolation=cv2.INTER_NEAREST)

    return result


def noise_report(image: np.ndarray, block_size: int = 32) -> Dict[str, Any]:
    """
    Analyze noise globally and per block, flagging non-uniform regions.

    ``uniformity`` is the ratio of the block-level standard deviation to the
    block-level mean. Sensor noise on an untouched frame is fairly even, so a
    high value means some regions are far noisier than others - worth a look,
    though heavy texture raises it too.

    Args:
        image: Input image
        block_size: Side length of the analysis blocks

    Returns:
        Dict with the global sigma, SNR, per-block statistics, and the
        quietest and noisiest block locations
    """
    global_sigma = estimate_noise(image)
    snr = estimate_snr(image)

    blocks = noise_map(image, block_size=block_size, normalize=False, upscale=False)
    block_values = blocks.astype(np.float32)

    quietest = np.unravel_index(int(np.argmin(block_values)), block_values.shape)
    noisiest = np.unravel_index(int(np.argmax(block_values)), block_values.shape)

    mean = float(block_values.mean())
    std = float(block_values.std())

    return {
        'noise_sigma': global_sigma,
        'snr_db': snr,
        'block_size': block_size,
        'blocks': {'rows': int(blocks.shape[0]), 'cols': int(blocks.shape[1])},
        'block_mean': mean,
        'block_std': std,
        'uniformity': float(std / mean) if mean > 0 else 0.0,
        'quietest_block': {
            'row': int(quietest[0]), 'col': int(quietest[1]),
            'x': int(quietest[1] * block_size), 'y': int(quietest[0] * block_size),
            'sigma': float(block_values[quietest]),
        },
        'noisiest_block': {
            'row': int(noisiest[0]), 'col': int(noisiest[1]),
            'x': int(noisiest[1] * block_size), 'y': int(noisiest[0] * block_size),
            'sigma': float(block_values[noisiest]),
        },
    }
