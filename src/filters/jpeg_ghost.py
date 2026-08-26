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

from typing import Any, Dict, List, Optional, Sequence, Tuple

import cv2
import numpy as np

from .ela import recompress

# How far a region's best quality has to sit below its *own average across
# the sweep* before it counts as a compression history.
#
# Measuring the region against the rest of the frame alone does not work: a
# region that merely differs in texture - a flat wall against a busy desk -
# sits below the rest at every quality equally, and across 32 frames from two
# cameras the worst such untouched region scored -0.364, stronger than the
# mean genuine paste at -0.284. No threshold separated them; false positives
# plateaued at 25%.
#
# A texture difference is a constant offset across the sweep and cancels when
# the region's own mean is subtracted. A compression history is a dip at one
# quality and survives. On the same 32 frames that change moves the achievable
# operating points from 28% detection at zero false positives to:
#
#     threshold   detects   false positives
#       0.20       84.4%        9.4%
#       0.25       59.4%        3.1%     <- in force
#       0.27       46.9%        0.0%
#
# 0.25 is chosen because a false "this region has a different history" invites
# a wrong conclusion, while a miss only leaves the question open. Every one of
# the 19 frames that fired at 0.25 named a quality within one sweep step of
# the truth. Raising sensitivity is a one-line change to this constant.
#
# The number belongs to DEFAULT_QUALITIES and to a wide quality gap. Both
# limits are measured. Against a Q95 frame, over 26 frames:
#
#     inner quality   50-100 sweep   30-100 sweep
#         35              4/26          16/26
#         40              3/26          11/26
#         55             14/26           0/26
#         70              1/26           3/26
#
# Two things follow. A region saved below the bottom of the sweep cannot be
# found there, and the filter names a wrong quality rather than none - which
# is why the sweep reaches down to 50 rather than 70. And widening the sweep
# does not simply add reach: every curve is normalised across whatever range
# it is given, so the low end rescales the dips at the top and Q55 stops being
# detectable at all. A changed sweep needs its own threshold.
#
# It applies only when the region is supplied. Searching for the region
# instead does not work: across 18 real CCTV frames the most separated
# cluster of an *untouched* frame scores -0.53 on average, against -0.44 for
# the same frames carrying a genuine Q55 paste. Flat walls and ceilings form
# large coherent clusters at some quality in every frame, and that swamps the
# compression signal. See validation/reports/hour-02.md for the measurements.
#
# The threshold travels between cameras - 12 of 12 on three cameras it was
# never calibrated on, at a different resolution - but only for a paste that
# landed on the JPEG 8x8 grid. Moved four pixels off it, the same paste in the
# same frames is found once in 12, separating no more than an untouched frame
# does. That is a property of JPEG rather than of this code: a region quantised
# on a grid offset from the one it now sits on carries no recoverable
# signature. See validation/reports/hour-04.md.
REGION_SEPARATION = 0.25

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


def ghost_sweep(
    image: np.ndarray,
    qualities: Sequence[int] = DEFAULT_QUALITIES,
    block_size: int = 16,
) -> np.ndarray:
    """
    The normalised difference at every quality - the ghost method's raw material.

    Each block's difference curve is scaled to 0-1 across the sweep before
    anything is decided, so blocks of wildly different texture become
    comparable: a flat wall and a detailed doorway both run from 0 at their
    best-matching quality to 1 at their worst.

    This is the form the technique was described in, and the form worth
    looking at. Collapsing the sweep to one number per block - the quality
    where its curve is lowest - throws the evidence away, because the curve
    falls monotonically towards 100 for almost every block and the ghost is a
    *local* dip on that slope, not the global minimum.

    Args:
        image: Input image, meaningful only for a JPEG original
        qualities: Ascending quality steps to sweep
        block_size: Side length of the analysis blocks

    Returns:
        Float array shaped ``(len(qualities), rows, cols)``, each frame
        normalised to 0-1. A region that was previously saved at quality q is
        darker than its surroundings in the frame for q.

    Example:
        >>> sweep = ghost_sweep(photo)
        >>> sweep.shape[0] == len(DEFAULT_QUALITIES)
        True
    """
    stack = _block_diffs(image, qualities, block_size)
    low = stack.min(axis=0)
    span = stack.max(axis=0) - low
    return (stack - low) / np.maximum(span, 1e-6)


def _region_mask(shape: Tuple[int, int], region: Sequence[int],
                 block_size: int) -> np.ndarray:
    """Block-grid mask for a pixel-space region, clipped to the grid."""
    rows, cols = shape
    x, y, width, height = (int(v) for v in region)
    c0, r0 = max(0, x // block_size), max(0, y // block_size)
    c1 = min(cols, -(-(x + width) // block_size))
    r1 = min(rows, -(-(y + height) // block_size))
    mask = np.zeros(shape, bool)
    if r1 > r0 and c1 > c0:
        mask[r0:r1, c0:c1] = True
    return mask


def ghost_map(
    image: np.ndarray,
    qualities: Sequence[int] = DEFAULT_QUALITIES,
    block_size: int = 16,
    upscale: bool = True,
) -> np.ndarray:
    """
    The sweep frame in which a region stands out most - the ghost, if there is one.

    Where a previous version of this returned each block's best-matching
    quality, this returns the single normalised difference frame that carries
    the evidence: dark where the pixels match that quality's recompression,
    bright where they do not. A pasted region appears as a dark patch against
    a bright field, at the quality it was originally saved at.

    With no ghost present the frame chosen is simply the most separated one,
    and it looks like noise - which is the correct appearance for an image
    with one compression history.

    Args:
        image: Input image, meaningful only for a JPEG original
        qualities: Ascending quality steps to sweep
        block_size: Side length of the analysis blocks
        upscale: Resize the block grid back to the input's dimensions

    Returns:
        Single-channel uint8 map. Read it with ``ghost_report``, which names
        the quality the frame belongs to.

    Example:
        >>> ghost_map(photo, block_size=16).shape[:2] == photo.shape[:2]
        True
    """
    sweep = ghost_sweep(image, qualities, block_size)

    # The frame with the widest spread between its darkest and lightest
    # blocks: whatever structure the sweep holds is most visible there
    spreads = [float(frame.max() - frame.min()) for frame in sweep]
    frame = sweep[int(np.argmax(spreads))]

    result = np.clip(frame * 255.0, 0, 255).astype(np.uint8)

    if upscale:
        rows, cols = result.shape
        result = cv2.resize(result, (cols * block_size, rows * block_size),
                             interpolation=cv2.INTER_NEAREST)
    return result


def ghost_report(
    image: np.ndarray,
    qualities: Sequence[int] = DEFAULT_QUALITIES,
    block_size: int = 16,
    region: Optional[Sequence[int]] = None,
) -> Dict[str, Any]:
    """
    Recover the JPEG quality a named region was last saved at.

    **A region has to be named.** This does not search for one, and the
    reason is measured rather than assumed: across 18 untouched CCTV frames,
    the most separated cluster an automatic search can find scores -0.53 on
    average, while the same frames carrying a genuine Q55 paste score -0.44.
    Flat walls form large coherent clusters at some quality in every frame,
    so a search returns texture, not history. Given the region, the same
    measurement is decisive: -0.34 at the true quality against -0.02 for the
    untouched control.

    Mark the region on the image - the desktop viewer fills x, y, width and
    height from a drag - and this reports what it was compressed at.

    Args:
        image: Input image
        qualities: Ascending quality steps to sweep
        block_size: Side length of the analysis blocks
        region: ``(x, y, width, height)`` to interrogate. Without it the
            sweep is returned for inspection and nothing is claimed

    Returns:
        Dict reporting whether a ghost was found, at which quality, where,
        and how far that region separated from the rest of its frame. The
        full ``sweep`` and the per-quality ``separations`` are included so
        the verdict can be checked rather than taken.
    """
    sweep = ghost_sweep(image, qualities, block_size)
    rows, cols = sweep.shape[1:]

    report: Dict[str, Any] = {
        'qualities': list(qualities),
        'block_size': block_size,
        'blocks': {'rows': rows, 'cols': cols},
        'sweep': sweep,
        'region': None,
        'ghost_quality': None,
        'separation': 0.0,
        'detected': False,
        'threshold': REGION_SEPARATION,
        'separations': {},
        # The threshold is calibrated for DEFAULT_QUALITIES. Each block's
        # curve is normalised across whatever sweep it is given, so changing
        # the range rescales every dip and the number stops meaning what it
        # was measured to mean.
        'calibrated_sweep': tuple(qualities) == DEFAULT_QUALITIES,
    }

    if region is None:
        return report

    mask = _region_mask((rows, cols), region, block_size)
    rest = ~mask
    if not mask.any() or not rest.any():
        raise ValueError(f"region {tuple(region)} does not fall inside the "
                         f"{cols * block_size}x{rows * block_size} image")

    # How far the named region sits below the rest of the image, at each
    # quality. It dips at the quality it was last saved at.
    separations = {int(q): round(float(frame[mask].mean() - frame[rest].mean()), 4)
                   for q, frame in zip(qualities, sweep)}
    best_quality = min(separations, key=separations.get)
    best = separations[best_quality]

    # The dip below the region's own average, which is what distinguishes a
    # compression history from a region that is simply flatter than the frame
    values = np.array(list(separations.values()), dtype=float)
    dip = float(values.min() - values.mean())
    detected = dip <= -REGION_SEPARATION

    report.update({
        'region': {'x': int(region[0]), 'y': int(region[1]),
                   'width': int(region[2]), 'height': int(region[3])},
        'region_blocks': int(mask.sum()),
        'separations': separations,
        'separation': best,
        'dip': round(dip, 4),
        'ghost_quality': best_quality if detected else None,
        'detected': bool(detected),
    })
    return report
