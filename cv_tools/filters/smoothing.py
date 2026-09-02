"""
Smoothing & Denoising - Gaussian blur, median filter, bilateral filter.

Inspired by Amped FIVE's Enhance group. Each filter targets a different noise
type:
    - Gaussian: general-purpose smoothing, blurs edges along with noise
    - Median: salt-and-pepper / impulse noise, preserves edges well
    - Bilateral: sensor noise, smooths flat areas while keeping edges sharp
"""

from typing import Optional, Tuple

import cv2
import numpy as np


def _split_alpha(image: np.ndarray) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """Separate an alpha channel so filters only see color data."""
    if image.ndim == 3 and image.shape[2] == 4:
        return image[:, :, :3], image[:, :, 3:4]
    return image, None


def _merge_alpha(image: np.ndarray, alpha: Optional[np.ndarray]) -> np.ndarray:
    """Reattach a previously split alpha channel."""
    if alpha is None:
        return image
    return np.concatenate([image, alpha], axis=2)


def gaussian_blur(
    image: np.ndarray,
    radius: float = 2.0,
    kernel_size: int = 0,
) -> np.ndarray:
    """
    Apply Gaussian smoothing.

    Args:
        image: Input image (RGB, RGBA, or grayscale)
        radius: Gaussian sigma in pixels. Larger = blurrier.
        kernel_size: Explicit odd kernel size. 0 derives it from the radius,
                     which is what you normally want.

    Returns:
        Blurred image

    Example:
        >>> softened = gaussian_blur(noisy, radius=1.5)
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if radius <= 0:
        raise ValueError(f"radius must be positive, got {radius}")
    if kernel_size != 0 and (kernel_size % 2 == 0 or kernel_size < 0):
        raise ValueError(f"kernel_size must be 0 or a positive odd number, got {kernel_size}")

    ksize = (kernel_size, kernel_size) if kernel_size else (0, 0)
    return cv2.GaussianBlur(image, ksize, sigmaX=radius, sigmaY=radius)


def median_filter(image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """
    Apply a median filter - the standard remedy for salt-and-pepper noise.

    Unlike a Gaussian blur, the output only ever contains values that were
    already present nearby, so edges stay crisp.

    Args:
        image: Input image (RGB, RGBA, or grayscale)
        kernel_size: Odd window size, 3 or greater. Larger removes more noise
                     and more fine detail.

    Returns:
        Filtered image
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if kernel_size % 2 == 0 or kernel_size < 3:
        raise ValueError(f"kernel_size must be an odd number >= 3, got {kernel_size}")

    img = image.astype(np.uint8) if image.dtype != np.uint8 else image
    # cv2.medianBlur only accepts 1 or 3 channels once kernel_size exceeds 5
    rgb, alpha = _split_alpha(img)
    filtered = cv2.medianBlur(rgb, kernel_size)
    return _merge_alpha(filtered, alpha)


def bilateral_filter(
    image: np.ndarray,
    diameter: int = 9,
    sigma_color: float = 75.0,
    sigma_space: float = 75.0,
) -> np.ndarray:
    """
    Apply an edge-preserving bilateral filter.

    Averages neighbouring pixels weighted by both distance and color
    similarity, so it smooths noise inside regions without bleeding across
    boundaries. Slower than the other smoothing filters.

    Args:
        image: Input image (RGB, RGBA, or grayscale)
        diameter: Pixel neighbourhood diameter. 0 derives it from sigma_space.
        sigma_color: Color-difference tolerance. Larger mixes more distinct
                     colors together.
        sigma_space: Spatial extent. Larger pulls in more distant pixels.

    Returns:
        Filtered image
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if sigma_color <= 0 or sigma_space <= 0:
        raise ValueError("sigma_color and sigma_space must be positive")

    img = image.astype(np.uint8) if image.dtype != np.uint8 else image
    # cv2.bilateralFilter handles 1 or 3 channels only
    rgb, alpha = _split_alpha(img)
    filtered = cv2.bilateralFilter(rgb, diameter, sigma_color, sigma_space)
    return _merge_alpha(filtered, alpha)
