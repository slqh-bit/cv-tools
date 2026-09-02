"""
Sharpen - Unsharp mask and Laplacian sharpening.

Inspired by Amped FIVE's Enhance group. Sharpening amplifies noise as readily
as detail, so both filters here expose a way to protect flat regions: the
unsharp mask has a threshold, and Laplacian sharpening is best applied after a
denoise step.
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


def unsharp_mask(
    image: np.ndarray,
    amount: float = 1.0,
    radius: float = 1.0,
    threshold: int = 0,
) -> np.ndarray:
    """
    Sharpen using an unsharp mask.

    Subtracts a blurred copy to isolate detail, then adds that detail back
    scaled by ``amount``.

    Args:
        image: Input image (RGB, RGBA, or grayscale)
        amount: Strength of the effect (0 = no change, 1.0 = standard,
                >2 usually looks artificial)
        radius: Gaussian blur sigma in pixels. Small values sharpen fine
                detail, large values boost local contrast.
        threshold: Minimum local contrast (0-255) before a pixel is sharpened.
                   Raise it to leave smooth areas - and their noise - alone.

    Returns:
        Sharpened image in uint8

    Example:
        >>> sharper = unsharp_mask(plate, amount=1.5, radius=1.0, threshold=4)
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if radius <= 0:
        raise ValueError(f"radius must be positive, got {radius}")
    if threshold < 0:
        raise ValueError(f"threshold must be non-negative, got {threshold}")

    img = image.astype(np.uint8) if image.dtype != np.uint8 else image.copy()
    rgb, alpha = _split_alpha(img)

    blurred = cv2.GaussianBlur(rgb, (0, 0), sigmaX=radius, sigmaY=radius)

    base = rgb.astype(np.float32)
    detail = base - blurred.astype(np.float32)

    if threshold > 0:
        detail = np.where(np.abs(detail) < threshold, 0.0, detail)

    result = np.clip(base + amount * detail, 0, 255).astype(np.uint8)
    return _merge_alpha(result, alpha)


def laplacian_sharpen(
    image: np.ndarray,
    strength: float = 1.0,
    kernel_size: int = 3,
) -> np.ndarray:
    """
    Sharpen by subtracting the Laplacian (second derivative) of the image.

    Harsher and more noise-sensitive than an unsharp mask, but it needs no
    radius choice and responds strongly to edges.

    Args:
        image: Input image (RGB, RGBA, or grayscale)
        strength: Scale applied to the Laplacian before subtraction
        kernel_size: Aperture size, odd, 1 to 31

    Returns:
        Sharpened image in uint8
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if kernel_size % 2 == 0 or kernel_size < 1:
        raise ValueError(f"kernel_size must be a positive odd number, got {kernel_size}")

    img = image.astype(np.uint8) if image.dtype != np.uint8 else image.copy()
    rgb, alpha = _split_alpha(img)

    laplacian = cv2.Laplacian(rgb, cv2.CV_32F, ksize=kernel_size)
    result = np.clip(rgb.astype(np.float32) - strength * laplacian, 0, 255).astype(np.uint8)

    return _merge_alpha(result, alpha)


def sharpen_grid(
    image: np.ndarray,
    amounts: list,
    radii: list,
) -> np.ndarray:
    """
    Render a labelled grid of unsharp mask settings for picking parameters,
    mirroring ``clahe.apply_clahe_grid``.

    Args:
        image: Input image
        amounts: Amount values to try
        radii: Radius values to try

    Returns:
        Grid image showing every combination
    """
    import math

    combinations = [(a, r) for a in amounts for r in radii]
    n = len(combinations)
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)

    h, w = image.shape[:2]
    thumb_h, thumb_w = h // rows, w // cols

    grid = np.zeros((thumb_h * rows, thumb_w * cols, 3), dtype=np.uint8)

    for idx, (amount, radius) in enumerate(combinations):
        sharpened = unsharp_mask(image, amount=amount, radius=radius)
        if sharpened.ndim == 2:
            sharpened = cv2.cvtColor(sharpened, cv2.COLOR_GRAY2RGB)
        elif sharpened.shape[2] == 4:
            sharpened = sharpened[:, :, :3]

        thumb = cv2.resize(sharpened, (thumb_w, thumb_h))

        row, col = divmod(idx, cols)
        y1, x1 = row * thumb_h, col * thumb_w
        grid[y1:y1 + thumb_h, x1:x1 + thumb_w] = thumb

        cv2.putText(grid, f"amount={amount}, radius={radius}", (x1 + 5, y1 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    return grid
