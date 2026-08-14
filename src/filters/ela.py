"""
ELA - Error Level Analysis.

Re-compresses the image as JPEG and amplifies the difference from the original.
Areas that have been through a different compression history than their
surroundings - a pasted region, for instance - can show a different error
level.

Read the result with care. ELA is a *screening* tool, not proof of anything:

    - It only means anything on a JPEG original. Re-saving a manipulated image
      as PNG, or a second full-image JPEG save, erases the signal entirely.
    - Bright areas in an ELA map track edge density and local texture as much
      as editing history, so busy regions always look "hot".
    - A clean map does not mean the image is authentic.

Treat a suspicious region as a pointer to look closer, never as a finding.
"""

from typing import Any, Dict, Optional

import cv2
import numpy as np


def _to_bgr(image: np.ndarray) -> np.ndarray:
    """Convert a toolkit RGB/RGBA/gray image to the BGR that cv2 encodes."""
    img = image.astype(np.uint8) if image.dtype != np.uint8 else image

    if img.ndim == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    if img.shape[2] == 1:
        return cv2.cvtColor(img[:, :, 0], cv2.COLOR_GRAY2BGR)
    if img.shape[2] == 4:
        return cv2.cvtColor(img[:, :, :3], cv2.COLOR_RGB2BGR)
    return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)


def recompress(image: np.ndarray, quality: int = 90) -> np.ndarray:
    """
    Re-encode an image as JPEG at the given quality and decode it back.

    Args:
        image: Input image
        quality: JPEG quality, 1-100

    Returns:
        The round-tripped image as RGB uint8
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if not 1 <= quality <= 100:
        raise ValueError(f"quality must be between 1 and 100, got {quality}")

    bgr = _to_bgr(image)
    ok, buffer = cv2.imencode('.jpg', bgr, [int(cv2.IMWRITE_JPEG_QUALITY), int(quality)])
    if not ok:
        raise RuntimeError("JPEG re-encoding failed")

    decoded = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    return cv2.cvtColor(decoded, cv2.COLOR_BGR2RGB)


def error_level_analysis(
    image: np.ndarray,
    quality: int = 90,
    scale: float = 0.0,
    grayscale: bool = False,
) -> np.ndarray:
    """
    Compute an Error Level Analysis map.

    Args:
        image: Input image - meaningful only if it came from a JPEG
        quality: JPEG quality used for the re-compression pass. Should sit near
                 the original's quality; 90 to 95 is the usual starting point.
        scale: Brightness multiplier for the difference. 0 auto-scales so the
               largest error reaches 255, which is what makes the map legible.
        grayscale: Collapse the per-channel error into one channel

    Returns:
        Amplified error map as RGB uint8, or single-channel if grayscale

    Example:
        >>> ela_map = error_level_analysis(photo, quality=90)
    """
    original = _to_bgr(image)
    compressed = _to_bgr(recompress(image, quality=quality))

    difference = cv2.absdiff(original, compressed).astype(np.float32)

    if grayscale:
        difference = difference.max(axis=2)

    if scale <= 0:
        peak = float(difference.max())
        factor = 255.0 / peak if peak > 0 else 1.0
    else:
        factor = scale

    amplified = np.clip(difference * factor, 0, 255).astype(np.uint8)

    if grayscale:
        return amplified
    return cv2.cvtColor(amplified, cv2.COLOR_BGR2RGB)


def ela_stats(image: np.ndarray, quality: int = 90, block_size: int = 16) -> Dict[str, Any]:
    """
    Summarize an ELA map block by block.

    A region whose mean error stands far above the image's own distribution is
    worth inspecting - though texture alone can produce that, see the module
    docstring.

    Args:
        image: Input image
        quality: JPEG quality for the re-compression pass
        block_size: Side length of the analysis blocks

    Returns:
        Dict with the overall mean/max error, the per-block mean grid, and the
        location and score of the highest-error block
    """
    if block_size < 2:
        raise ValueError(f"block_size must be at least 2, got {block_size}")

    error = error_level_analysis(image, quality=quality, scale=1.0, grayscale=True)
    error = error.astype(np.float32)

    h, w = error.shape
    rows, cols = h // block_size, w // block_size
    if rows < 1 or cols < 1:
        raise ValueError(
            f"block_size {block_size} is larger than the image ({w}x{h})"
        )

    trimmed = error[:rows * block_size, :cols * block_size]
    blocks = trimmed.reshape(rows, block_size, cols, block_size).mean(axis=(1, 3))

    hottest = np.unravel_index(int(np.argmax(blocks)), blocks.shape)

    return {
        'quality': quality,
        'block_size': block_size,
        'mean_error': float(error.mean()),
        'max_error': float(error.max()),
        'block_mean': float(blocks.mean()),
        'block_std': float(blocks.std()),
        'block_grid': blocks,
        'hottest_block': {
            'row': int(hottest[0]),
            'col': int(hottest[1]),
            'x': int(hottest[1] * block_size),
            'y': int(hottest[0] * block_size),
            'mean_error': float(blocks[hottest]),
            # How far the hottest block sits above the rest, in std deviations
            'z_score': float(
                (blocks[hottest] - blocks.mean()) / blocks.std()
            ) if blocks.std() > 0 else 0.0,
        },
    }
