"""
Clone Detection - Copy-move forgery detection.

Finds regions duplicated from elsewhere in the same image, the signature of a
clone-stamp or copy-paste retouch. The classic block-matching approach is used:

    1. Slide overlapping blocks across the image
    2. Describe each with its low-frequency DCT coefficients, which survive
       mild noise and JPEG compression
    3. Sort the descriptors so near-identical blocks land next to each other
    4. For each matching pair, record the shift between them
    5. A shift shared by many pairs means a whole region moved together -
       a lone matching pair is just coincidence

Flat blocks are discarded before matching. Any two patches of empty sky are
identical, and without that filter they swamp the result.

Two things to know before trusting a result:

    - **Only shifts that are multiples of ``step`` can be found.** Blocks are
      sampled on a grid of that stride, so a region moved by 190 pixels is
      invisible to a stride of 8 - the copy is sampled at a different phase
      than the original. ``step=1`` is exhaustive and is the default; raising
      it trades detection coverage for speed, and is only safe for a quick
      screening pass.
    - Genuine repetition - brick walls, windows, tiled floors, text - is
      duplication too, and will be reported. This locates duplication, not
      intent.
"""

from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
from scipy.fft import dctn


# Blocks transformed per batch, to keep peak memory bounded at step=1
_DCT_CHUNK = 8192


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


def detect_copy_move(
    image: np.ndarray,
    block_size: int = 16,
    step: int = 1,
    coefficients: int = 4,
    quantization: float = 4.0,
    min_distance: float = 0.0,
    min_matches: int = 8,
    min_variance: float = 12.0,
    search_window: int = 3,
    max_blocks: int = 300_000,
) -> Dict[str, Any]:
    """
    Detect duplicated regions within an image.

    Args:
        image: Input image (converted to luminance)
        step: Stride between sampled blocks. **Only shifts that are multiples
              of this value can be detected**, so the default of 1 is
              exhaustive. Raising it cuts cost quadratically but blinds the
              search to most shifts - use it only for quick screening.
        block_size: Side length of each compared block
        coefficients: Size of the top-left DCT square kept as the descriptor.
                      4 means 16 low-frequency coefficients.
        quantization: Descriptor rounding step. Larger tolerates more noise and
                      compression but produces more false matches.
        min_distance: Minimum pixel separation for a pair to count. 0 uses
                      twice the block size, which rejects the trivial matches
                      between neighbouring overlapping blocks.
        min_matches: How many block pairs must share one shift before that
                     shift is reported as a duplicated region
        min_variance: Blocks below this intensity variance are ignored as
                      featureless
        search_window: How many neighbours each block is compared against in
                       the sorted descriptor list
        max_blocks: Guard against exhausting memory on large images. Exceeding
                    it raises rather than allocating gigabytes.

    Returns:
        Dict with ``detected``, a boolean ``mask`` of duplicated pixels, the
        list of ``shifts`` (each with dx, dy and match count), and counts of
        the blocks analyzed and skipped

    Example:
        >>> result = detect_copy_move(photo)
        >>> if result['detected']:
        ...     overlay = draw_clone_regions(photo, result)
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if block_size < 4:
        raise ValueError(f"block_size must be at least 4, got {block_size}")
    if step < 1:
        raise ValueError(f"step must be at least 1, got {step}")
    if not 1 <= coefficients <= block_size:
        raise ValueError(
            f"coefficients must be between 1 and block_size ({block_size}), got {coefficients}"
        )
    if quantization <= 0:
        raise ValueError(f"quantization must be positive, got {quantization}")

    gray = _to_gray(image).astype(np.float32)
    h, w = gray.shape

    if h < block_size or w < block_size:
        raise ValueError(f"Image ({w}x{h}) is smaller than block_size {block_size}")

    if min_distance <= 0:
        min_distance = 2.0 * block_size

    empty_mask = np.zeros((h, w), dtype=np.uint8)

    # ---- 1. Lay out the overlapping block grid (a view, nothing copied) ----
    windows = np.lib.stride_tricks.sliding_window_view(gray, (block_size, block_size))
    windows = windows[::step, ::step]
    rows, cols = windows.shape[:2]

    # ---- 2. Discard featureless blocks ----
    # Local variance via box filters over the whole image: E[x^2] - E[x]^2.
    # Computing it from the stacked blocks instead would allocate
    # block_size^2 floats per block - gigabytes at step=1.
    window = (block_size, block_size)
    local_mean = cv2.boxFilter(gray, cv2.CV_32F, window, anchor=(0, 0), normalize=True)
    local_mean_sq = cv2.boxFilter(gray * gray, cv2.CV_32F, window, anchor=(0, 0),
                                  normalize=True)
    variance_full = local_mean_sq - local_mean * local_mean
    variances = variance_full[:h - block_size + 1:step, :w - block_size + 1:step].ravel()

    keep = variances >= min_variance
    skipped = int((~keep).sum())

    if keep.sum() < 2:
        return {
            'detected': False,
            'mask': empty_mask,
            'shifts': [],
            'match_count': 0,
            'blocks_analyzed': 0,
            'blocks_skipped': skipped,
            'block_size': block_size,
        }

    kept = int(keep.sum())
    if kept > max_blocks:
        raise ValueError(
            f"{kept} blocks exceeds max_blocks ({max_blocks}). "
            f"Raise step (currently {step}, at the cost of missing shifts that "
            f"are not multiples of it), crop to a region of interest, or raise "
            f"max_blocks if you have the memory."
        )

    kept_indices = np.nonzero(keep)[0]
    row_indices = kept_indices // cols
    col_indices = kept_indices % cols
    positions = np.stack([row_indices * step, col_indices * step], axis=1)

    # ---- 3. Describe each block by its low-frequency DCT coefficients ----
    # Gathered and transformed in chunks so peak memory stays bounded
    feature_chunks = []
    for start in range(0, kept, _DCT_CHUNK):
        selected = windows[row_indices[start:start + _DCT_CHUNK],
                           col_indices[start:start + _DCT_CHUNK]]
        transformed = dctn(selected.astype(np.float32), axes=(-2, -1), norm='ortho')
        feature_chunks.append(
            transformed[:, :coefficients, :coefficients].reshape(len(selected), -1)
        )

    features = np.round(np.concatenate(feature_chunks) / quantization)
    del feature_chunks

    # ---- 4. Sort so similar descriptors become neighbours ----
    order = np.lexsort(features[:, ::-1].T)
    features = features[order]
    positions = positions[order]

    # ---- 5. Collect shift vectors from near-identical neighbouring pairs ----
    shift_counts: Dict[Tuple[int, int], int] = {}
    shift_members: Dict[Tuple[int, int], List[Tuple[int, int]]] = {}

    for offset in range(1, search_window + 1):
        if offset >= len(features):
            break

        identical = np.all(features[:-offset] == features[offset:], axis=1)
        if not identical.any():
            continue

        first = positions[:-offset][identical]
        second = positions[offset:][identical]

        deltas = second - first
        distances = np.sqrt((deltas ** 2).sum(axis=1))
        far_enough = distances >= min_distance
        if not far_enough.any():
            continue

        for delta, pos_a, pos_b in zip(
            deltas[far_enough], first[far_enough], second[far_enough]
        ):
            dy, dx = int(delta[0]), int(delta[1])
            # Canonical sign, so a shift and its reverse are the same vector
            if (dy, dx) < (0, 0):
                dy, dx = -dy, -dx
            key = (dy, dx)
            shift_counts[key] = shift_counts.get(key, 0) + 1
            shift_members.setdefault(key, []).append((int(pos_a[0]), int(pos_a[1])))
            shift_members[key].append((int(pos_b[0]), int(pos_b[1])))

    # ---- 6. Keep only shifts backed by enough matching pairs ----
    strong = {
        shift: count for shift, count in shift_counts.items() if count >= min_matches
    }

    mask = empty_mask
    if strong:
        mask = np.zeros((h, w), dtype=np.uint8)
        for shift in strong:
            for y, x in shift_members[shift]:
                mask[y:y + block_size, x:x + block_size] = 255

    shifts = [
        {'dy': shift[0], 'dx': shift[1], 'matches': count}
        for shift, count in sorted(strong.items(), key=lambda item: item[1], reverse=True)
    ]

    return {
        'detected': bool(strong),
        'mask': mask,
        'shifts': shifts,
        'match_count': int(sum(strong.values())),
        'blocks_analyzed': int(len(features)),
        'blocks_skipped': skipped,
        'block_size': block_size,
    }


def draw_clone_regions(
    image: np.ndarray,
    result: Dict[str, Any],
    color: Tuple[int, int, int] = (255, 0, 0),
    alpha: float = 0.4,
) -> np.ndarray:
    """
    Tint the duplicated regions from a ``detect_copy_move`` result.

    Args:
        image: The image the detection was run on
        result: Dict returned by ``detect_copy_move``
        color: RGB overlay color
        alpha: Overlay opacity, 0-1

    Returns:
        RGB image with duplicated regions tinted
    """
    if not 0.0 <= alpha <= 1.0:
        raise ValueError(f"alpha must be between 0 and 1, got {alpha}")

    img = image.astype(np.uint8) if image.dtype != np.uint8 else image.copy()

    if img.ndim == 2:
        rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    elif img.shape[2] == 4:
        rgb = img[:, :, :3].copy()
    else:
        rgb = img.copy()

    mask = result['mask'].astype(bool)
    if not mask.any():
        return rgb

    overlay = rgb.copy()
    overlay[mask] = color
    return cv2.addWeighted(overlay, alpha, rgb, 1.0 - alpha, 0)


def highlight_clones(
    image: np.ndarray,
    block_size: int = 16,
    step: int = 1,
    min_matches: int = 8,
    min_variance: float = 12.0,
    color: Tuple[int, int, int] = (255, 0, 0),
    alpha: float = 0.4,
) -> np.ndarray:
    """
    Detect and highlight duplicated regions in one call, for use in a filter
    chain where only an image can be returned.

    Args:
        image: Input image
        block_size: Side length of each compared block
        step: Stride between blocks
        min_matches: Pairs required before a shift counts
        min_variance: Featureless-block cutoff
        color: RGB overlay color
        alpha: Overlay opacity

    Returns:
        RGB image with any duplicated regions tinted
    """
    result = detect_copy_move(
        image,
        block_size=block_size,
        step=step,
        min_matches=min_matches,
        min_variance=min_variance,
    )
    return draw_clone_regions(image, result, color=color, alpha=alpha)
