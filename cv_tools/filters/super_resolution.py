"""
Super-Resolution - Single-frame upscaling and multi-frame reconstruction.

The distinction between the two matters more here than anywhere else in the
toolkit:

    - **Single-frame** upscaling interpolates. It makes an image bigger and can
      make edges look cleaner, but it adds **no information**. A plate that
      cannot be read at native resolution cannot be read by enlarging it. Use
      it for presentation, never to justify a reading.

    - **Multi-frame** reconstruction genuinely recovers detail, and is the
      method worth reaching for. When a camera and subject move slightly
      between frames, each frame samples the scene on a slightly different
      grid. Those sub-pixel offsets carry real information the individual
      frames do not, and combining them onto a finer grid recovers detail that
      was never present in any single frame.

Multi-frame needs genuine sub-pixel motion. Frames that are perfectly aligned,
or offset by whole pixels, add nothing beyond noise reduction.
"""

from typing import Dict, List, Optional, Sequence, Tuple

import cv2
import numpy as np

_INTERPOLATIONS = {
    'nearest': cv2.INTER_NEAREST,
    'bilinear': cv2.INTER_LINEAR,
    'bicubic': cv2.INTER_CUBIC,
    'lanczos': cv2.INTER_LANCZOS4,
}


def _to_gray(image: np.ndarray) -> np.ndarray:
    """Single-channel float32 view, for motion estimation."""
    img = image.astype(np.uint8) if image.dtype != np.uint8 else image
    if img.ndim == 3:
        if img.shape[2] == 4:
            img = img[:, :, :3]
        if img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            img = img[:, :, 0]
    return img.astype(np.float32)


def upscale(
    image: np.ndarray,
    scale: float = 2.0,
    method: str = 'lanczos',
    sharpen: float = 0.0,
) -> np.ndarray:
    """
    Enlarge a single image by interpolation.

    Adds no information. Any apparent new detail is the interpolator's
    invention, not recovered evidence.

    Args:
        image: Input image
        scale: Magnification factor, greater than 1
        method: 'nearest', 'bilinear', 'bicubic', or 'lanczos'.
                'nearest' is the honest choice for pixel-level inspection - it
                shows the actual samples rather than a smoothed guess.
        sharpen: Optional unsharp amount applied after scaling, 0 to disable

    Returns:
        Enlarged image

    Example:
        >>> bigger = upscale(plate_crop, scale=4, method='nearest')
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if scale <= 0:
        raise ValueError(f"scale must be positive, got {scale}")
    if method not in _INTERPOLATIONS:
        available = ', '.join(sorted(_INTERPOLATIONS))
        raise ValueError(f"Unknown method '{method}'. Available: {available}")

    height, width = image.shape[:2]
    new_size = (max(1, int(round(width * scale))), max(1, int(round(height * scale))))

    result = cv2.resize(image, new_size, interpolation=_INTERPOLATIONS[method])

    if sharpen > 0:
        from .sharpen import unsharp_mask
        result = unsharp_mask(result, amount=sharpen, radius=max(1.0, scale / 2.0))

    return result


def estimate_shifts(
    frames: Sequence[np.ndarray],
    reference: int = 0,
) -> List[Tuple[float, float]]:
    """
    Measure each frame's sub-pixel offset from a reference frame.

    Uses phase correlation, which works in the frequency domain and resolves
    shifts far finer than one pixel.

    It needs broadband detail to lock onto. A strongly periodic scene - floor
    tiles, brickwork, a fence, a halftone screen - produces several correlation
    peaks of similar height, and the measured offset can then be meaningless
    rather than merely imprecise. Check the result against
    ``super_resolve_report`` before trusting a reconstruction built on it.

    Args:
        frames: Frames of identical size
        reference: Index of the frame others are measured against

    Returns:
        List of (dx, dy) offsets in pixels, one per frame

    Example:
        >>> shifts = estimate_shifts(frames)
        >>> max(abs(dx) for dx, _ in shifts) < 1.0   # sub-pixel motion only
        True
    """
    if frames is None or len(frames) == 0:
        raise ValueError("No frames provided")
    if not 0 <= reference < len(frames):
        raise ValueError(f"reference {reference} is outside the {len(frames)} frames given")

    base = _to_gray(frames[reference])
    # A window suppresses the edge discontinuity that would otherwise dominate
    # the correlation peak
    window = cv2.createHanningWindow((base.shape[1], base.shape[0]), cv2.CV_32F)

    shifts = []
    for position, frame in enumerate(frames):
        if frame.shape[:2] != frames[reference].shape[:2]:
            raise ValueError(
                f"Frame {position} is {frame.shape[:2]}, expected {frames[reference].shape[:2]}"
            )
        if position == reference:
            shifts.append((0.0, 0.0))
            continue
        (dx, dy), _ = cv2.phaseCorrelate(base, _to_gray(frame), window)
        shifts.append((float(dx), float(dy)))

    return shifts


def super_resolve(
    frames: Sequence[np.ndarray],
    scale: float = 2.0,
    reference: int = 0,
    sharpen: float = 0.6,
    max_shift: float = 8.0,
) -> np.ndarray:
    """
    Reconstruct a higher-resolution image from several offset frames.

    Each frame is projected onto a finer grid according to its measured
    sub-pixel offset and accumulated; the result is normalised by how much
    evidence landed on each output pixel, gaps are filled, and a mild sharpen
    counteracts the softening the projection introduces.

    Args:
        frames: Frames of the same scene, identical size, with slight motion
        scale: Magnification factor
        reference: Frame whose geometry the output follows
        sharpen: Unsharp amount applied at the end, 0 to disable
        max_shift: Frames displaced further than this are dropped as
                   mis-registered rather than smeared into the result

    Returns:
        Reconstructed image at ``scale`` times the input size

    Example:
        >>> better = super_resolve(frames[:12], scale=2)
    """
    if frames is None or len(frames) == 0:
        raise ValueError("No frames provided")
    if scale <= 1:
        raise ValueError(f"scale must be greater than 1, got {scale}")
    if max_shift <= 0:
        raise ValueError(f"max_shift must be positive, got {max_shift}")

    shifts = estimate_shifts(frames, reference=reference)

    base = frames[reference]
    height, width = base.shape[:2]
    out_h, out_w = int(round(height * scale)), int(round(width * scale))

    channels = 1 if base.ndim == 2 else base.shape[2]
    accumulator = np.zeros((out_h, out_w, channels), dtype=np.float32)
    weights = np.zeros((out_h, out_w, 1), dtype=np.float32)

    used = 0
    for frame, (dx, dy) in zip(frames, shifts):
        if abs(dx) > max_shift or abs(dy) > max_shift:
            continue

        source = frame if frame.ndim == 3 else frame[:, :, np.newaxis]
        source = source.astype(np.float32)

        # Scale up, then shift by the measured offset expressed on the fine
        # grid, so each frame's samples land where they actually belong
        enlarged = cv2.resize(source, (out_w, out_h), interpolation=cv2.INTER_CUBIC)
        if enlarged.ndim == 2:
            enlarged = enlarged[:, :, np.newaxis]

        matrix = np.array([[1, 0, -dx * scale], [0, 1, -dy * scale]], dtype=np.float32)
        aligned = cv2.warpAffine(
            enlarged, matrix, (out_w, out_h),
            flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT,
        )
        if aligned.ndim == 2:
            aligned = aligned[:, :, np.newaxis]

        contribution = cv2.warpAffine(
            np.ones((out_h, out_w), dtype=np.float32), matrix, (out_w, out_h),
            flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT, borderValue=0,
        )

        accumulator += aligned * contribution[:, :, np.newaxis]
        weights += contribution[:, :, np.newaxis]
        used += 1

    # The reference always measures as a zero shift, so it is always kept and
    # `used` can never be 0. One frame is still not a reconstruction, though:
    # it would silently degrade to the plain interpolation this module warns
    # against, so refuse rather than return something that looks like more.
    if used < 2:
        raise ValueError(
            f"Only the reference frame fell within max_shift ({max_shift}px), so "
            f"the result would be a plain upscale rather than a reconstruction. "
            f"The frames may not show the same scene, or may need stabilising first."
        )

    result = np.divide(accumulator, weights, out=np.zeros_like(accumulator),
                       where=weights > 0)

    # Any output pixel no frame reached falls back to a plain upscale
    if (weights <= 0).any():
        fallback = cv2.resize(
            base.astype(np.float32) if base.ndim == 3 else base[:, :, np.newaxis].astype(np.float32),
            (out_w, out_h), interpolation=cv2.INTER_CUBIC,
        )
        if fallback.ndim == 2:
            fallback = fallback[:, :, np.newaxis]
        gaps = np.repeat(weights <= 0, channels, axis=2)
        result[gaps] = fallback[gaps]

    output = np.clip(result, 0, 255).astype(np.uint8)
    if channels == 1:
        output = output[:, :, 0]

    if sharpen > 0:
        from .sharpen import unsharp_mask
        output = unsharp_mask(output, amount=sharpen, radius=max(1.0, scale / 2.0))

    return output


def super_resolve_report(
    frames: Sequence[np.ndarray],
    reference: int = 0,
) -> Dict[str, object]:
    """
    Report whether a sequence carries the sub-pixel motion multi-frame
    reconstruction needs.

    Frames offset only by whole pixels, or not at all, give no extra sampling
    information - reconstruction then reduces to noise averaging.

    Args:
        frames: Frames to inspect
        reference: Frame others are measured against

    Returns:
        Dict with the measured shifts, their range, and whether usable
        sub-pixel motion is present
    """
    shifts = estimate_shifts(frames, reference=reference)

    fractional = [
        (abs(dx - round(dx)), abs(dy - round(dy))) for dx, dy in shifts
    ]
    sub_pixel = sum(1 for fx, fy in fractional if fx > 0.1 or fy > 0.1)

    magnitudes = [float(np.hypot(dx, dy)) for dx, dy in shifts]

    return {
        'frames': len(frames),
        'shifts': shifts,
        'max_shift_px': max(magnitudes) if magnitudes else 0.0,
        'mean_shift_px': float(np.mean(magnitudes)) if magnitudes else 0.0,
        'frames_with_subpixel_motion': sub_pixel,
        'usable': sub_pixel >= max(2, len(frames) // 4),
    }
