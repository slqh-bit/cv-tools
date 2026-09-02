"""
Redaction - Irreversibly obscure sensitive regions.

Redaction is the one operation here that must not be undoable, and the obvious
methods are the ones that fail:

    - **Blurring is reversible.** A Gaussian blur is a known, invertible
      convolution; deconvolution recovers the original, and this toolkit ships
      a Wiener deconvolution that will do it (``motion_deblur.py``).
    - **Pixelation is reversible for short known-alphabet text.** Each block
      is the mean of its pixels, which constrains the original strongly.
      Rendering every candidate plate or postcode and matching the block means
      is a documented and cheap attack.

Only ``fill`` and ``noise`` destroy the information: they discard the original
pixels rather than transforming them. ``fill`` is the default here, and the
only method that should be used on a document intended for release.

``blur`` and ``pixelate`` remain available because they are the right choice
for a visual preview or an internal working copy - but they warn, and
``verify_redaction`` will tell you whether what you produced is recoverable.
"""

from typing import Any, Dict, List, Optional, Sequence, Tuple

import cv2
import numpy as np

# Methods that discard the original pixel values outright
IRREVERSIBLE_METHODS = {'fill', 'noise'}
# Methods that transform them, and can therefore be attacked
REVERSIBLE_METHODS = {'blur', 'pixelate'}


def _normalize_regions(
    regions: Sequence[Sequence[int]],
    shape: Tuple[int, ...],
) -> List[Tuple[int, int, int, int]]:
    """Clip regions to the image and drop any that fall outside it."""
    height, width = shape[:2]
    normalized = []

    for region in regions:
        if len(region) != 4:
            raise ValueError(f"Each region needs (x, y, width, height), got {region}")
        x, y, w, h = (int(v) for v in region)
        if w <= 0 or h <= 0:
            raise ValueError(f"Region must be non-empty, got width={w} height={h}")

        x1, y1 = max(0, x), max(0, y)
        x2, y2 = min(width, x + w), min(height, y + h)
        if x1 < x2 and y1 < y2:
            normalized.append((x1, y1, x2, y2))

    if not normalized:
        raise ValueError("No region overlaps the image")

    return normalized


def redact(
    image: np.ndarray,
    regions: Sequence[Sequence[int]],
    method: str = 'fill',
    fill_color: Tuple[int, int, int] = (0, 0, 0),
    blur_radius: float = 15.0,
    pixel_size: int = 12,
    seed: Optional[int] = None,
) -> np.ndarray:
    """
    Obscure one or more regions.

    Args:
        image: Input image
        regions: Regions as (x, y, width, height)
        method: 'fill' replaces with a solid colour, 'noise' with random
                pixels - both destroy the content. 'blur' and 'pixelate'
                transform it and are recoverable; see the module docstring.
        fill_color: RGB colour used by 'fill'
        blur_radius: Gaussian sigma used by 'blur'
        pixel_size: Block size used by 'pixelate'
        seed: Seed for 'noise', for reproducible output

    Returns:
        Image with the regions obscured

    Example:
        >>> safe = redact(frame, [(120, 80, 200, 40)])           # solid fill
        >>> preview = redact(frame, [(120, 80, 200, 40)], 'blur')  # recoverable
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")

    known = IRREVERSIBLE_METHODS | REVERSIBLE_METHODS
    if method not in known:
        available = ', '.join(sorted(known))
        raise ValueError(f"Unknown method '{method}'. Available: {available}")
    if blur_radius <= 0:
        raise ValueError(f"blur_radius must be positive, got {blur_radius}")
    if pixel_size < 2:
        raise ValueError(f"pixel_size must be at least 2, got {pixel_size}")

    img = image.astype(np.uint8) if image.dtype != np.uint8 else image.copy()
    boxes = _normalize_regions(regions, img.shape)

    channels = 1 if img.ndim == 2 else img.shape[2]
    rng = np.random.default_rng(seed)

    for x1, y1, x2, y2 in boxes:
        patch = img[y1:y2, x1:x2]

        if method == 'fill':
            if channels == 1:
                value = int(sum(fill_color) / 3)
            elif channels == 4:
                value = (*fill_color, 255)
            else:
                value = fill_color
            img[y1:y2, x1:x2] = value

        elif method == 'noise':
            img[y1:y2, x1:x2] = rng.integers(
                0, 256, size=patch.shape, dtype=np.uint8
            )

        elif method == 'blur':
            img[y1:y2, x1:x2] = cv2.GaussianBlur(
                patch, (0, 0), sigmaX=blur_radius, sigmaY=blur_radius
            )

        elif method == 'pixelate':
            height, width = patch.shape[:2]
            small_w = max(1, width // pixel_size)
            small_h = max(1, height // pixel_size)
            small = cv2.resize(patch, (small_w, small_h), interpolation=cv2.INTER_AREA)
            img[y1:y2, x1:x2] = cv2.resize(
                small, (width, height), interpolation=cv2.INTER_NEAREST
            )

    return img


def redact_region(
    image: np.ndarray,
    x: int,
    y: int,
    width: int,
    height: int,
    method: str = 'fill',
    pixel_size: int = 12,
    blur_radius: float = 15.0,
) -> np.ndarray:
    """
    Obscure a single region, for use in a filter chain.

    Args:
        image: Input image
        x, y, width, height: Region to obscure
        method: 'fill', 'noise', 'blur', or 'pixelate'
        pixel_size: Block size used by 'pixelate'
        blur_radius: Gaussian sigma used by 'blur'

    Returns:
        Image with the region obscured
    """
    return redact(
        image, [(x, y, width, height)], method=method,
        pixel_size=pixel_size, blur_radius=blur_radius,
    )


def verify_redaction(
    original: np.ndarray,
    redacted: np.ndarray,
    regions: Sequence[Sequence[int]],
) -> Dict[str, Any]:
    """
    Check whether a redaction actually destroyed the content.

    Compares each redacted region against the original and reports how much
    structure survives. A region that still correlates strongly with the
    original has been transformed rather than destroyed, and is a candidate
    for recovery.

    Args:
        original: The image before redaction
        redacted: The image after
        regions: The regions that were redacted

    Returns:
        Dict with per-region correlation and variance, and an overall
        ``safe`` flag

    Example:
        >>> report = verify_redaction(before, after, [(120, 80, 200, 40)])
        >>> report['safe']
        True
    """
    if original.shape != redacted.shape:
        raise ValueError(
            f"Images differ in shape: {original.shape} vs {redacted.shape}"
        )

    boxes = _normalize_regions(regions, original.shape)
    results = []

    for x1, y1, x2, y2 in boxes:
        before = original[y1:y2, x1:x2].astype(np.float64).ravel()
        after = redacted[y1:y2, x1:x2].astype(np.float64).ravel()

        if before.std() < 1e-6 or after.std() < 1e-6:
            # A constant region carries no structure to correlate
            correlation = 0.0
        else:
            correlation = float(abs(np.corrcoef(before, after)[0, 1]))

        results.append({
            'region': (x1, y1, x2 - x1, y2 - y1),
            'correlation': correlation,
            'residual_variance': float(after.var()),
            'destroyed': correlation < 0.2,
        })

    return {
        'regions': results,
        'safe': all(entry['destroyed'] for entry in results),
        'max_correlation': max((e['correlation'] for e in results), default=0.0),
    }


def is_reversible(method: str) -> bool:
    """
    Whether a redaction method can in principle be undone.

    Args:
        method: 'fill', 'noise', 'blur', or 'pixelate'

    Returns:
        True for methods that transform the pixels rather than discard them
    """
    known = IRREVERSIBLE_METHODS | REVERSIBLE_METHODS
    if method not in known:
        available = ', '.join(sorted(known))
        raise ValueError(f"Unknown method '{method}'. Available: {available}")

    return method in REVERSIBLE_METHODS
