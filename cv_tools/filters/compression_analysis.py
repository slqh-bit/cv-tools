"""
Compression Analysis - Detect blocking and estimate JPEG history.

JPEG encodes in 8x8 blocks, quantising each independently. That leaves two
readable traces: discontinuities on the 8-pixel grid, and the quantisation
tables themselves when the file is still a JPEG.

What this is good for:

    - Judging how heavily an image has been compressed, which bounds what any
      enhancement can recover. Detail destroyed by quantisation is gone.
    - Spotting a region whose block grid is out of phase with the rest, which
      happens when part of an image was pasted from a differently-aligned
      source.

What it is not good for: proving manipulation. Strong blocking means heavy
compression, nothing more, and re-saving normalises the grid across the whole
frame, erasing any local difference.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Union

import cv2
import numpy as np

# JPEG's fixed transform size
BLOCK = 8


def _to_gray(image: np.ndarray) -> np.ndarray:
    """Single-channel uint8 view."""
    img = image.astype(np.uint8) if image.dtype != np.uint8 else image
    if img.ndim == 2:
        return img
    if img.shape[2] == 1:
        return img[:, :, 0]
    if img.shape[2] == 4:
        return cv2.cvtColor(img[:, :, :3], cv2.COLOR_RGB2GRAY)
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)


def blockiness_score(image: np.ndarray) -> Dict[str, float]:
    """
    Measure discontinuity on the 8x8 grid against the surrounding image.

    Compares the average intensity step across block boundaries with the
    average step everywhere else. Uncompressed images sit near 1; heavy JPEG
    compression pushes the ratio well above it.

    The measure assumes photographic content, where detail is spread across the
    frame. An image dominated by hard synthetic edges that avoid the 8-pixel
    grid - a test chart, a screenshot of line art - inflates the interior term
    and can drive the ratio *below* 1, which reads as no blocking whatever the
    compression history.

    Args:
        image: Input image

    Returns:
        Dict with the boundary and interior step sizes, their ratio, and a
        0-100 blockiness score
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")

    gray = _to_gray(image).astype(np.float32)
    height, width = gray.shape
    if height < BLOCK * 2 or width < BLOCK * 2:
        raise ValueError(f"Image must be at least {BLOCK * 2}x{BLOCK * 2}, got {width}x{height}")

    horizontal = np.abs(np.diff(gray, axis=1))
    vertical = np.abs(np.diff(gray, axis=0))

    # Column i of the horizontal difference spans pixels i and i+1, so a block
    # boundary after column 7 appears at index 7, 15, 23 ...
    h_columns = np.arange(horizontal.shape[1])
    v_rows = np.arange(vertical.shape[0])
    h_boundary = (h_columns % BLOCK) == (BLOCK - 1)
    v_boundary = (v_rows % BLOCK) == (BLOCK - 1)

    boundary_steps = np.concatenate([
        horizontal[:, h_boundary].ravel(),
        vertical[v_boundary, :].ravel(),
    ])
    interior_steps = np.concatenate([
        horizontal[:, ~h_boundary].ravel(),
        vertical[~v_boundary, :].ravel(),
    ])

    boundary_mean = float(boundary_steps.mean()) if boundary_steps.size else 0.0
    interior_mean = float(interior_steps.mean()) if interior_steps.size else 0.0

    # Quantisation strong enough to flatten every block drives the interior
    # step to exactly zero. Dividing by a floor rather than special-casing it
    # keeps the ratio monotonic: the earlier guard returned 1.0 ("no blocking")
    # for the most heavily blocked images there are.
    ratio = boundary_mean / max(interior_mean, 1e-3)
    # Map the ratio onto 0-100. Real JPEG ratios run from about 1 (untouched)
    # to beyond 12 (severe), so the span is divided across that range rather
    # than saturating at 2 - otherwise quality 50 and quality 8 both read 100.
    score = float(np.clip((ratio - 1.0) / 9.0 * 100.0, 0.0, 100.0))

    return {
        'boundary_step': boundary_mean,
        'interior_step': interior_mean,
        'ratio': float(ratio),
        'blockiness': score,
    }


def blocking_map(
    image: np.ndarray,
    block_size: int = 32,
    normalize: bool = True,
    upscale: bool = True,
) -> np.ndarray:
    """
    Map blocking strength across the image, region by region.

    A region whose blocking differs markedly from its surroundings is worth a
    look - though flat areas naturally show little blocking regardless, so
    read it alongside the image itself.

    Args:
        image: Input image
        block_size: Side length of each analysis region, a multiple of 8
        normalize: Stretch the output to fill 0-255
        upscale: Resize back to the input's dimensions

    Returns:
        Single-channel uint8 map; brighter means stronger blocking
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if block_size < BLOCK * 2:
        raise ValueError(f"block_size must be at least {BLOCK * 2}, got {block_size}")

    gray = _to_gray(image).astype(np.float32)
    height, width = gray.shape
    rows, cols = height // block_size, width // block_size
    if rows < 1 or cols < 1:
        raise ValueError(f"block_size {block_size} is larger than the image ({width}x{height})")

    scores = np.zeros((rows, cols), dtype=np.float32)
    for row in range(rows):
        for col in range(cols):
            region = gray[row * block_size:(row + 1) * block_size,
                          col * block_size:(col + 1) * block_size]
            try:
                scores[row, col] = blockiness_score(region.astype(np.uint8))['ratio']
            except ValueError:
                scores[row, col] = 0.0

    if normalize:
        peak = scores.max()
        scores = scores * (255.0 / peak) if peak > 0 else scores
    else:
        scores = np.clip((scores - 1.0) * 255.0, 0, 255)

    result = np.clip(scores, 0, 255).astype(np.uint8)

    if upscale:
        result = cv2.resize(result, (width, height), interpolation=cv2.INTER_NEAREST)

    return result


def estimate_jpeg_quality(path: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """
    Read the quality setting from a JPEG's own quantisation tables.

    Exact rather than inferred, because the tables are stored in the file - but
    only available while the file is still a JPEG. Once re-saved as PNG the
    information is gone.

    Args:
        path: Path to an image file

    Returns:
        Dict with the estimated quality and table statistics, or None if the
        file has no quantisation tables

    Example:
        >>> estimate_jpeg_quality('evidence.jpg')['quality']
        92
    """
    from PIL import Image

    try:
        with Image.open(path) as img:
            tables = getattr(img, 'quantization', None)
    except Exception:
        return None

    if not tables:
        return None

    luminance = np.array(tables[0], dtype=np.float64)

    # The standard IJG table, against which a quality factor is defined
    standard = np.array([
        16, 11, 10, 16, 24, 40, 51, 61,
        12, 12, 14, 19, 26, 58, 60, 55,
        14, 13, 16, 24, 40, 57, 69, 56,
        14, 17, 22, 29, 51, 87, 80, 62,
        18, 22, 37, 56, 68, 109, 103, 77,
        24, 35, 55, 64, 81, 104, 113, 92,
        49, 64, 78, 87, 103, 121, 120, 101,
        72, 92, 95, 98, 112, 100, 103, 99,
    ], dtype=np.float64)

    size = min(len(luminance), len(standard))
    ratios = luminance[:size] / standard[:size]
    scale = float(np.median(ratios)) * 100.0

    # Invert the IJG scaling: quality above 50 halves the scale factor,
    # below 50 divides into it
    if scale <= 0:
        quality = 100.0
    elif scale < 100:
        quality = (200.0 - scale) / 2.0
    else:
        quality = 5000.0 / scale

    return {
        'quality': int(round(float(np.clip(quality, 1, 100)))),
        'tables': len(tables),
        'luminance_mean': float(luminance.mean()),
        'luminance_max': float(luminance.max()),
        # An all-ones table means no quantisation at all
        'lossless': bool(np.all(luminance <= 1)),
    }


def compression_report(
    image: np.ndarray,
    path: Optional[Union[str, Path]] = None,
    block_size: int = 32,
) -> Dict[str, Any]:
    """
    Summarise an image's compression history and blocking.

    Args:
        image: Input image
        path: Original file, so the quantisation tables can be read. Without
              it only the pixel evidence is available.
        block_size: Region size for the uniformity check

    Returns:
        Dict with blockiness measures, per-region uniformity, and the quality
        estimate when a JPEG path was supplied
    """
    scores = blockiness_score(image)

    regions = blocking_map(image, block_size=block_size, normalize=False, upscale=False)
    region_values = regions.astype(np.float32)
    mean = float(region_values.mean())
    std = float(region_values.std())

    report: Dict[str, Any] = {
        'blockiness': scores['blockiness'],
        'boundary_step': scores['boundary_step'],
        'interior_step': scores['interior_step'],
        'ratio': scores['ratio'],
        'block_size': block_size,
        'region_mean': mean,
        'region_std': std,
        'region_uniformity': float(std / mean) if mean > 0 else 0.0,
        'likely_jpeg': scores['ratio'] > 1.15,
    }

    if path is not None:
        report['jpeg_quality'] = estimate_jpeg_quality(path)

    return report


def deblock(image: np.ndarray, strength: float = 0.5) -> np.ndarray:
    """
    Soften JPEG block edges without blurring the whole image.

    Smooths across the 8-pixel grid lines only, blending the result by
    ``strength``. It hides the artefact; it does not restore what quantisation
    discarded.

    Args:
        image: Input image
        strength: Blend amount, 0 (no change) to 1 (fully smoothed grid)

    Returns:
        Deblocked image
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if not 0 <= strength <= 1:
        raise ValueError(f"strength must be between 0 and 1, got {strength}")

    if strength == 0:
        return image.copy()

    img = image.astype(np.uint8) if image.dtype != np.uint8 else image
    has_alpha = img.ndim == 3 and img.shape[2] == 4
    rgb = img[:, :, :3] if has_alpha else img
    alpha = img[:, :, 3:4] if has_alpha else None

    smoothed = cv2.bilateralFilter(rgb, 5, 30, 5)

    height, width = rgb.shape[:2]
    mask = np.zeros((height, width), dtype=np.float32)
    mask[BLOCK - 1::BLOCK, :] = 1.0
    mask[:, BLOCK - 1::BLOCK] = 1.0
    mask[BLOCK::BLOCK, :] = 1.0
    mask[:, BLOCK::BLOCK] = 1.0
    # Feather so the correction does not itself become a visible grid
    mask = cv2.GaussianBlur(mask, (0, 0), sigmaX=1.0, sigmaY=1.0) * strength

    if rgb.ndim == 3:
        mask = mask[:, :, np.newaxis]

    blended = rgb.astype(np.float32) * (1 - mask) + smoothed.astype(np.float32) * mask
    result = np.clip(blended, 0, 255).astype(np.uint8)

    if alpha is not None:
        result = np.concatenate([result, alpha], axis=2)
    return result
