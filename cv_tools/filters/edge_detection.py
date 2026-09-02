"""
Edge Detection - Canny, Sobel, and Laplacian edge maps.

Inspired by Amped FIVE's Analyze group. Every function returns a single-channel
uint8 edge map, so these steps change a color image into grayscale mid-chain.
"""

from typing import Optional

import cv2
import numpy as np


def _to_gray(image: np.ndarray) -> np.ndarray:
    """Reduce any supported input to a single-channel uint8 image."""
    img = image.astype(np.uint8) if image.dtype != np.uint8 else image

    if img.ndim == 2:
        return img
    if img.shape[2] == 1:
        return img[:, :, 0]
    if img.shape[2] == 4:
        return cv2.cvtColor(img[:, :, :3], cv2.COLOR_RGB2GRAY)
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)


def canny_edges(
    image: np.ndarray,
    low_threshold: float = 100,
    high_threshold: float = 200,
    aperture_size: int = 3,
    l2_gradient: bool = False,
    blur_sigma: float = 0.0,
) -> np.ndarray:
    """
    Detect edges with the Canny algorithm.

    Args:
        image: Input image (any channel count)
        low_threshold: Weak edge threshold - pixels above it survive only if
                       connected to a strong edge
        high_threshold: Strong edge threshold. A 1:2 or 1:3 ratio of low to
                        high is the usual starting point.
        aperture_size: Sobel aperture used internally, odd, 3 to 7
        l2_gradient: Use the exact L2 gradient magnitude instead of the
                     cheaper L1 approximation
        blur_sigma: Optional Gaussian pre-blur. Noisy footage produces a mess
                    of spurious edges without one.

    Returns:
        Binary edge map (0 or 255) as single-channel uint8

    Example:
        >>> edges = canny_edges(frame, 50, 150, blur_sigma=1.0)
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if low_threshold > high_threshold:
        raise ValueError(
            f"low_threshold ({low_threshold}) must not exceed high_threshold ({high_threshold})"
        )
    if aperture_size not in (3, 5, 7):
        raise ValueError(f"aperture_size must be 3, 5, or 7, got {aperture_size}")

    gray = _to_gray(image)

    if blur_sigma > 0:
        gray = cv2.GaussianBlur(gray, (0, 0), sigmaX=blur_sigma, sigmaY=blur_sigma)

    return cv2.Canny(gray, float(low_threshold), float(high_threshold),
                     apertureSize=aperture_size, L2gradient=l2_gradient)


def auto_canny(image: np.ndarray, sigma: float = 0.33, blur_sigma: float = 0.0) -> np.ndarray:
    """
    Canny with thresholds derived from the image's median intensity.

    Useful when processing a batch of frames whose exposure varies, where one
    fixed threshold pair would not suit them all.

    Args:
        image: Input image
        sigma: Spread around the median, 0-1. Larger keeps more edges.
        blur_sigma: Optional Gaussian pre-blur

    Returns:
        Binary edge map as single-channel uint8
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")

    gray = _to_gray(image)
    median = float(np.median(gray))

    low = max(0.0, (1.0 - sigma) * median)
    high = min(255.0, (1.0 + sigma) * median)

    # A near-black or near-white frame can collapse both thresholds onto the
    # same value, which would return an empty map.
    if high <= low:
        low, high = 50.0, 150.0

    return canny_edges(gray, low, high, blur_sigma=blur_sigma)


def sobel_edges(
    image: np.ndarray,
    dx: int = 1,
    dy: int = 1,
    kernel_size: int = 3,
    normalize: bool = True,
) -> np.ndarray:
    """
    Compute Sobel gradients.

    With both ``dx`` and ``dy`` set, the gradient magnitude is returned;
    otherwise the single directional derivative is. Unlike Canny this produces
    a continuous-valued map rather than a binary one.

    Args:
        image: Input image
        dx: Order of the horizontal derivative (0 or 1)
        dy: Order of the vertical derivative (0 or 1)
        kernel_size: Sobel aperture, odd, 1 to 7
        normalize: Stretch the result to fill 0-255

    Returns:
        Gradient map as single-channel uint8
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if dx == 0 and dy == 0:
        raise ValueError("At least one of dx, dy must be non-zero")
    if kernel_size % 2 == 0 or not 1 <= kernel_size <= 7:
        raise ValueError(f"kernel_size must be an odd number 1-7, got {kernel_size}")

    gray = _to_gray(image)

    if dx and dy:
        grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=kernel_size)
        grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=kernel_size)
        magnitude = cv2.magnitude(grad_x, grad_y)
    else:
        magnitude = np.abs(cv2.Sobel(gray, cv2.CV_32F, dx, dy, ksize=kernel_size))

    if normalize:
        peak = magnitude.max()
        if peak > 0:
            magnitude = magnitude * (255.0 / peak)

    return np.clip(magnitude, 0, 255).astype(np.uint8)


def laplacian_edges(
    image: np.ndarray,
    kernel_size: int = 3,
    normalize: bool = True,
    blur_sigma: float = 0.0,
) -> np.ndarray:
    """
    Compute the Laplacian (second derivative) edge map.

    Responds to intensity changes in all directions at once, and to noise just
    as eagerly - a small ``blur_sigma`` is usually worth it.

    Args:
        image: Input image
        kernel_size: Aperture size, odd, 1 to 31
        normalize: Stretch the result to fill 0-255
        blur_sigma: Optional Gaussian pre-blur

    Returns:
        Edge map as single-channel uint8
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if kernel_size % 2 == 0 or kernel_size < 1:
        raise ValueError(f"kernel_size must be a positive odd number, got {kernel_size}")

    gray = _to_gray(image)

    if blur_sigma > 0:
        gray = cv2.GaussianBlur(gray, (0, 0), sigmaX=blur_sigma, sigmaY=blur_sigma)

    laplacian = np.abs(cv2.Laplacian(gray, cv2.CV_32F, ksize=kernel_size))

    if normalize:
        peak = laplacian.max()
        if peak > 0:
            laplacian = laplacian * (255.0 / peak)

    return np.clip(laplacian, 0, 255).astype(np.uint8)


def edge_density(edges: np.ndarray, threshold: int = 0) -> float:
    """
    Fraction of pixels in an edge map that carry an edge.

    Useful as a focus proxy when comparing frames of the same scene: blurring
    wipes out fine detail, dropping the density. Note it is not a general
    sharpness measure - blurring an image whose only feature is one strong
    edge spreads that edge over more pixels and *raises* the density.

    Args:
        edges: Edge map from any of the detectors above
        threshold: Intensity above which a pixel counts as an edge

    Returns:
        Value between 0 and 1
    """
    if edges is None or edges.size == 0:
        raise ValueError("Input edge map is empty")
    return float(np.count_nonzero(edges > threshold) / edges.size)
