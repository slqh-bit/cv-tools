"""
Detail Enhancement - Local contrast at chosen scales.

Sharpening works at the pixel scale; these operate over larger neighbourhoods,
raising the contrast *within* regions rather than at edges. The effect is that
texture and shape become easier to read without the bright fringing an
aggressive unsharp mask leaves behind.

``local_contrast`` is the workhorse: a large-radius unsharp mask, which is what
most "clarity" sliders actually are. ``enhance_detail`` uses an edge-preserving
filter instead, so it lifts texture without dragging halos across boundaries.
``multiscale_detail`` separates the image into frequency bands and boosts each
independently, which gives the most control and the most opportunity to
overdo it.
"""

from typing import Optional, Sequence, Tuple

import cv2
import numpy as np


def _split_alpha(image: np.ndarray) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """Separate an alpha channel so it is not enhanced."""
    if image.ndim == 3 and image.shape[2] == 4:
        return image[:, :, :3], image[:, :, 3:4]
    return image, None


def local_contrast(
    image: np.ndarray,
    radius: float = 20.0,
    strength: float = 0.5,
) -> np.ndarray:
    """
    Raise contrast over a neighbourhood - the "clarity" adjustment.

    A large-radius, low-amount unsharp mask. Because the radius is wide, it
    acts on regional brightness differences rather than edges, so it does not
    sharpen noise the way a small-radius mask does.

    Args:
        image: Input image (RGB, RGBA, or grayscale)
        radius: Neighbourhood size in pixels. Larger affects broader areas.
        strength: Effect amount; 0 is no change, above 1 looks artificial

    Returns:
        Enhanced image, alpha preserved

    Example:
        >>> clearer = local_contrast(hazy_frame, radius=25, strength=0.6)
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if radius <= 0:
        raise ValueError(f"radius must be positive, got {radius}")
    if strength < 0:
        raise ValueError(f"strength must be non-negative, got {strength}")

    img = image.astype(np.uint8) if image.dtype != np.uint8 else image
    rgb, alpha = _split_alpha(img)

    blurred = cv2.GaussianBlur(rgb, (0, 0), sigmaX=radius, sigmaY=radius)
    base = rgb.astype(np.float32)
    enhanced = base + strength * (base - blurred.astype(np.float32))

    result = np.clip(enhanced, 0, 255).astype(np.uint8)

    if alpha is not None:
        result = np.concatenate([result, alpha], axis=2)
    return result


def enhance_detail(
    image: np.ndarray,
    sigma_s: float = 10.0,
    sigma_r: float = 0.15,
) -> np.ndarray:
    """
    Enhance texture with an edge-preserving filter.

    Boosts detail inside regions while leaving boundaries alone, so it avoids
    the halos a plain unsharp mask produces at strong edges.

    Args:
        image: Input image (RGB or RGBA; grayscale is promoted internally)
        sigma_s: Spatial scale, 0-200. Larger works over broader areas.
        sigma_r: Range scale, 0-1. Larger mixes more dissimilar tones and
                 gives a stronger, less natural effect.

    Returns:
        Enhanced image
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if not 0 < sigma_s <= 200:
        raise ValueError(f"sigma_s must be between 0 and 200, got {sigma_s}")
    if not 0 < sigma_r <= 1:
        raise ValueError(f"sigma_r must be between 0 and 1, got {sigma_r}")

    img = image.astype(np.uint8) if image.dtype != np.uint8 else image

    was_gray = img.ndim == 2
    if was_gray:
        working = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        alpha = None
    else:
        working, alpha = _split_alpha(img)

    # cv2.detailEnhance works in BGR order
    bgr = cv2.cvtColor(working, cv2.COLOR_RGB2BGR)
    enhanced = cv2.detailEnhance(bgr, sigma_s=float(sigma_s), sigma_r=float(sigma_r))
    result = cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB)

    if was_gray:
        return cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)

    if alpha is not None:
        result = np.concatenate([result, alpha], axis=2)
    return result


def multiscale_detail(
    image: np.ndarray,
    scales: Sequence[float] = (2.0, 8.0, 32.0),
    strengths: Sequence[float] = (0.5, 0.4, 0.3),
) -> np.ndarray:
    """
    Boost several frequency bands independently.

    The image is split into differences between successive blurs - fine
    texture, mid-scale structure, broad shading - each scaled separately and
    recombined. Fine and coarse detail can therefore be treated differently,
    which one radius cannot do.

    Args:
        image: Input image
        scales: Blur radii defining the bands, ascending
        strengths: Multiplier per band, same length as ``scales``

    Returns:
        Enhanced image

    Example:
        >>> # Lift fine texture, leave broad shading alone
        >>> out = multiscale_detail(frame, scales=(2, 8, 32),
        ...                         strengths=(0.8, 0.3, 0.0))
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if len(scales) != len(strengths):
        raise ValueError(
            f"Got {len(scales)} scales and {len(strengths)} strengths; they must match"
        )
    if not scales:
        raise ValueError("At least one scale is required")
    if any(s <= 0 for s in scales):
        raise ValueError("All scales must be positive")
    if list(scales) != sorted(scales):
        raise ValueError("scales must be in ascending order")

    img = image.astype(np.uint8) if image.dtype != np.uint8 else image
    rgb, alpha = _split_alpha(img)

    base = rgb.astype(np.float32)
    residual = base.copy()
    result = base.copy()

    for scale, strength in zip(scales, strengths):
        blurred = cv2.GaussianBlur(residual, (0, 0), sigmaX=scale, sigmaY=scale)
        band = residual - blurred
        result += band * strength
        residual = blurred

    output = np.clip(result, 0, 255).astype(np.uint8)

    if alpha is not None:
        output = np.concatenate([output, alpha], axis=2)
    return output


def texture_boost(
    image: np.ndarray,
    amount: float = 0.6,
    protect_edges: bool = True,
) -> np.ndarray:
    """
    Raise texture contrast while leaving strong edges untouched.

    Uses an edge mask so the boost applies to surface texture - fabric, skin,
    road surface - rather than to object outlines, which is where sharpening
    artefacts are most visible.

    Args:
        image: Input image
        amount: Boost strength
        protect_edges: Suppress the boost near strong edges

    Returns:
        Enhanced image
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if amount < 0:
        raise ValueError(f"amount must be non-negative, got {amount}")

    img = image.astype(np.uint8) if image.dtype != np.uint8 else image
    rgb, alpha = _split_alpha(img)

    base = rgb.astype(np.float32)
    blurred = cv2.GaussianBlur(base, (0, 0), sigmaX=3.0, sigmaY=3.0)
    detail = base - blurred

    if protect_edges:
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY) if rgb.ndim == 3 else rgb
        edges = cv2.Sobel(gray, cv2.CV_32F, 1, 1, ksize=3)
        magnitude = np.abs(edges)
        peak = magnitude.max()
        if peak > 0:
            magnitude = magnitude / peak
        mask = 1.0 - np.clip(magnitude * 3.0, 0.0, 1.0)
        if rgb.ndim == 3:
            mask = mask[:, :, np.newaxis]
        detail = detail * mask

    result = np.clip(base + detail * amount, 0, 255).astype(np.uint8)

    if alpha is not None:
        result = np.concatenate([result, alpha], axis=2)
    return result
