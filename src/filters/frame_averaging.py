"""
Frame Averaging - Multi-frame integration for video.

Combining several frames of a static scene trades time for signal quality:

    - ``average_frames`` suppresses random sensor noise. Noise falls with the
      square root of the frame count, so 16 frames halve it twice over. Any
      object that moved will smear.
    - ``median_frames`` removes transient objects entirely, reconstructing the
      empty background behind passing traffic or pedestrians.
    - ``integrate_frames`` accumulates light from very dark footage, brightening
      the scene without the noise amplification that gain would bring.

All three assume the frames are aligned. Handheld or PTZ footage needs
stabilising first; the camera moving turns averaging into a blur.
"""

from typing import List, Optional, Sequence

import cv2
import numpy as np


def _validate_stack(frames: Sequence[np.ndarray]) -> np.ndarray:
    """Check frames are compatible and return them stacked as float32."""
    if frames is None or len(frames) == 0:
        raise ValueError("No frames provided")

    first = frames[0]
    for index, frame in enumerate(frames):
        if frame.shape != first.shape:
            raise ValueError(
                f"Frame {index} has shape {frame.shape}, expected {first.shape}. "
                "All frames must share dimensions."
            )

    return np.stack([frame.astype(np.float32) for frame in frames], axis=0)


def average_frames(
    frames: Sequence[np.ndarray],
    weights: Optional[Sequence[float]] = None,
) -> np.ndarray:
    """
    Average frames to suppress random noise.

    Args:
        frames: Frames of the same size and channel count
        weights: Optional per-frame weights, e.g. to favour the sharpest
                 frames. Normalized internally.

    Returns:
        Averaged image in uint8

    Example:
        >>> clean = average_frames(frames[:16])
    """
    stack = _validate_stack(frames)

    if weights is None:
        result = stack.mean(axis=0)
    else:
        if len(weights) != len(frames):
            raise ValueError(
                f"Got {len(weights)} weights for {len(frames)} frames"
            )
        weight_array = np.asarray(weights, dtype=np.float32)
        if weight_array.sum() <= 0:
            raise ValueError("Weights must sum to a positive value")
        weight_array = weight_array / weight_array.sum()
        result = (stack * weight_array.reshape(-1, *([1] * (stack.ndim - 1)))).sum(axis=0)

    return np.clip(result, 0, 255).astype(np.uint8)


def median_frames(frames: Sequence[np.ndarray]) -> np.ndarray:
    """
    Take the per-pixel median across frames.

    Anything present in fewer than half the frames disappears, which
    reconstructs the background of a scene with moving objects in it.

    Args:
        frames: Frames of the same size and channel count

    Returns:
        Median image in uint8
    """
    stack = _validate_stack(frames)
    return np.clip(np.median(stack, axis=0), 0, 255).astype(np.uint8)


def integrate_frames(
    frames: Sequence[np.ndarray],
    gain: float = 1.0,
    auto_scale: bool = True,
) -> np.ndarray:
    """
    Sum frames to brighten very dark footage.

    Unlike raising exposure or gain on a single frame, this accumulates real
    signal, so the noise does not scale with the brightening.

    Args:
        frames: Frames of the same size and channel count
        gain: Multiplier applied after summing
        auto_scale: Normalize the sum to fill 0-255. With this off, the sum is
                    simply clipped, which blows out anything already bright.

    Returns:
        Integrated image in uint8
    """
    if gain <= 0:
        raise ValueError(f"gain must be positive, got {gain}")

    stack = _validate_stack(frames)
    total = stack.sum(axis=0) * gain

    if auto_scale:
        peak = float(total.max())
        if peak > 0:
            total = total * (255.0 / peak)

    return np.clip(total, 0, 255).astype(np.uint8)


def frame_difference(
    frame_a: np.ndarray,
    frame_b: np.ndarray,
    amplify: float = 1.0,
) -> np.ndarray:
    """
    Absolute difference between two frames, for isolating what moved.

    Args:
        frame_a: First frame
        frame_b: Second frame, same shape
        amplify: Brightness multiplier for the difference

    Returns:
        Difference image in uint8
    """
    if frame_a.shape != frame_b.shape:
        raise ValueError(
            f"Frames differ in shape: {frame_a.shape} vs {frame_b.shape}"
        )
    if amplify <= 0:
        raise ValueError(f"amplify must be positive, got {amplify}")

    difference = cv2.absdiff(
        frame_a.astype(np.uint8) if frame_a.dtype != np.uint8 else frame_a,
        frame_b.astype(np.uint8) if frame_b.dtype != np.uint8 else frame_b,
    )
    return np.clip(difference.astype(np.float32) * amplify, 0, 255).astype(np.uint8)


def sharpest_frames(
    frames: Sequence[np.ndarray],
    count: int = 5,
) -> List[int]:
    """
    Rank frames by focus and return the indices of the sharpest ones.

    Focus is scored by the variance of the Laplacian, the standard cheap
    autofocus measure. Averaging only the sharpest frames of a sequence beats
    averaging all of them when some are motion-blurred.

    Args:
        frames: Frames to score
        count: How many indices to return

    Returns:
        Frame indices, sharpest first

    Example:
        >>> best = sharpest_frames(frames, count=8)
        >>> clean = average_frames([frames[i] for i in best])
    """
    if frames is None or len(frames) == 0:
        raise ValueError("No frames provided")
    if count < 1:
        raise ValueError(f"count must be at least 1, got {count}")

    scores = []
    for frame in frames:
        img = frame.astype(np.uint8) if frame.dtype != np.uint8 else frame
        if img.ndim == 3:
            gray = cv2.cvtColor(img[:, :, :3], cv2.COLOR_RGB2GRAY)
        else:
            gray = img
        scores.append(float(cv2.Laplacian(gray, cv2.CV_32F).var()))

    ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    return ranked[:count]
