"""
JPEG Ghost Detection - locate a region saved at a different JPEG quality than
its surroundings.

Recompresses the image across a range of JPEG qualities and diffs each pass
against the source, the same trick ELA uses at a single quality. A pasted
region carries its own compression history: JPEG requantising an already
lossy image at the SAME quality it was previously saved at leaves it almost
unchanged, so a block's difference curve dips sharply right at its true prior
quality - the "ghost". A block from a different source dips at a different
point on the quality axis than the rest of a single-JPEG composite.

What this is good for:
    - Flagging a spliced region whose JPEG generation differs from the rest
      of the image, when the regions were composited as pixels and never
      unified by a later full-frame JPEG save (a PNG composite of JPEG
      sources is the common case).
    - Recovering a single-generation JPEG's compression quality from pixel
      evidence alone, once the file has been resaved and its quantisation
      tables are gone.

What it is not good for: proving manipulation, or anything once resizing or
heavy editing has intervened. A uniform JPEG resave of the *whole* composite
is also a blind spot: every block then shares one true last quality, and its
trivially-near-zero dip there swamps any subtler trace of what a region was
compressed at before. Flat, low-texture regions dip only shallowly at every
quality and read as ambiguous by design. Treat a best-quality mismatch as a
pointer to inspect, never as a finding.
"""

from typing import Any, Dict, List, Sequence, Tuple

import cv2
import numpy as np

from .ela import recompress

# Sane sweep for typical camera/editor JPEG saves; 5-point steps keep the
# per-block minimum easy to localise without an excessive number of passes.
DEFAULT_QUALITIES: Tuple[int, ...] = tuple(range(50, 101, 5))


def _to_rgb(image: np.ndarray) -> np.ndarray:
    """3-channel uint8 RGB view, matching recompress()'s output space."""
    img = image.astype(np.uint8) if image.dtype != np.uint8 else image
    if img.ndim == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    if img.shape[2] == 1:
        return cv2.cvtColor(img[:, :, 0], cv2.COLOR_GRAY2RGB)
    if img.shape[2] == 4:
        return img[:, :, :3]
    return img


def _block_diffs(image: np.ndarray, qualities: Sequence[int], block_size: int) -> np.ndarray:
    """
    Per-block mean squared difference against the source, at each quality.

    Returns an array shaped ``(len(qualities), rows, cols)``.
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if len(qualities) < 2:
        raise ValueError("qualities needs at least two steps to compare")
    if block_size < 2:
        raise ValueError(f"block_size must be at least 2, got {block_size}")

    original = _to_rgb(image).astype(np.float32)
    height, width = original.shape[:2]
    rows, cols = height // block_size, width // block_size
    if rows < 1 or cols < 1:
        raise ValueError(f"block_size {block_size} is larger than the image ({width}x{height})")

    trimmed_original = original[:rows * block_size, :cols * block_size]
    stack = np.zeros((len(qualities), rows, cols), dtype=np.float32)

    for i, quality in enumerate(qualities):
        compressed = _to_rgb(recompress(image, quality=quality)).astype(np.float32)
        trimmed = compressed[:rows * block_size, :cols * block_size]
        diff = ((trimmed_original - trimmed) ** 2).mean(axis=2)
        stack[i] = diff.reshape(rows, block_size, cols, block_size).mean(axis=(1, 3))

    return stack


def ghost_map(
    image: np.ndarray,
    qualities: Sequence[int] = DEFAULT_QUALITIES,
    block_size: int = 16,
    upscale: bool = True,
) -> np.ndarray:
    """
    Map each block to the quality step where it best matches its own
    recompression - its likely prior JPEG quality.

    Args:
        image: Input image, meaningful only for a JPEG original
        qualities: Ascending quality steps to sweep
        block_size: Side length of the analysis blocks
        upscale: Resize the block grid back to the input's dimensions

    Returns:
        Single-channel uint8 map, where intensity encodes the index into
        ``qualities`` of each block's best match - darker means an earlier
        (lower-quality) step. A region whose shade differs sharply from its
        surroundings had a different JPEG history.

    Example:
        >>> ghost_map(photo, block_size=16).shape[:2] == photo.shape[:2]
        True
    """
    stack = _block_diffs(image, qualities, block_size)
    best_index = np.argmin(stack, axis=0).astype(np.float32)

    result = (best_index * (255.0 / (len(qualities) - 1))).astype(np.uint8)

    if upscale:
        rows, cols = result.shape
        result = cv2.resize(result, (cols * block_size, rows * block_size),
                             interpolation=cv2.INTER_NEAREST)
    return result


def ghost_report(
    image: np.ndarray,
    qualities: Sequence[int] = DEFAULT_QUALITIES,
    block_size: int = 16,
) -> Dict[str, Any]:
    """
    Summarize each block's best-match quality and flag outliers.

    Args:
        image: Input image
        qualities: Ascending quality steps to sweep
        block_size: Side length of the analysis blocks

    Returns:
        Dict with the per-block best-quality grid, the image's dominant
        quality (its mode), and the outlier blocks whose best match departs
        from it
    """
    stack = _block_diffs(image, qualities, block_size)
    best_index = np.argmin(stack, axis=0)
    rows, cols = best_index.shape

    counts = np.bincount(best_index.ravel(), minlength=len(qualities))
    dominant_index = int(np.argmax(counts))

    outliers: List[Dict[str, int]] = []
    for row in range(rows):
        for col in range(cols):
            idx = int(best_index[row, col])
            if idx != dominant_index:
                outliers.append({
                    'row': row, 'col': col,
                    'x': col * block_size, 'y': row * block_size,
                    'quality': int(qualities[idx]),
                })

    total_blocks = rows * cols
    return {
        'qualities': list(qualities),
        'block_size': block_size,
        'block_grid': best_index,
        'dominant_quality': int(qualities[dominant_index]),
        'outlier_count': len(outliers),
        'outlier_fraction': len(outliers) / total_blocks if total_blocks else 0.0,
        'outliers': outliers[:50],
    }
