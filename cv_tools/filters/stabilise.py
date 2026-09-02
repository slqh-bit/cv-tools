"""
Stabilise - Bring a sequence of frames into a common alignment.

``frame_averaging`` and ``super_resolution`` both assume their frames already
line up, and both say so: averaging a moving camera turns signal into blur, and
a reconstruction built on frames that do not correspond is not a reconstruction.
Handheld and PTZ footage does not line up. This module is the missing step.

It is not the same job as ``super_resolution.estimate_shifts``, and the two are
not interchangeable:

    - ``estimate_shifts`` measures *translation* to a small fraction of a pixel,
      which is what a reconstruction needs from a nearly-static camera.
    - ``align_frames`` here handles rotation, scale and perspective as well, at
      whole- or near-pixel accuracy, which is what makes a moving camera's
      frames combinable at all.

Stabilise first, then reconstruct: the two compose in that order.

**Alignment fabricates nothing, but a bad alignment smears.** A frame that could
not be matched is worse than a frame left out, because averaging hides it - the
result simply looks softer, with nothing to say why. So every frame comes back
with a confidence, frames below a threshold are dropped rather than warped on a
guess, and the caller is told which. Read ``alignment_report`` before trusting a
combination built on this.

Convention: each frame's matrix maps *reference coordinates to that frame's
coordinates*, which is what OpenCV's ECC returns natively. It is applied with
``WARP_INVERSE_MAP`` to bring the frame into the reference's frame, and its
translation column reads directly as how far the frame sits from the reference.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import cv2
import numpy as np

# Motion models, smallest first. A model with more freedom than the camera
# actually had will happily fit noise, so prefer the simplest one that holds:
# a locked-off camera with a shaky mount is 'translation', a handheld one
# 'euclidean', a PTZ pan across a flat scene 'homography'.
MOTION_MODELS: Dict[str, int] = {
    'translation': cv2.MOTION_TRANSLATION,
    'euclidean': cv2.MOTION_EUCLIDEAN,
    'affine': cv2.MOTION_AFFINE,
    'homography': cv2.MOTION_HOMOGRAPHY,
}

METHODS = ('auto', 'ecc', 'features')

# Below this, a match is not an alignment. Chosen to be permissive: the point is
# to catch frames that failed outright, not to second-guess marginal ones, which
# the per-frame confidences let an operator do for themselves.
DEFAULT_MIN_CONFIDENCE = 0.3


@dataclass
class Alignment:
    """
    What was measured for one frame, and how much to believe it.

    ``confidence`` is not one scale: from ECC it is the enhanced correlation
    coefficient, from features the RANSAC inlier ratio. Both run 0 to 1 and both
    mean "more is better", but a 0.7 from one is not a 0.7 from the other.
    """
    index: int
    model: str
    method: str
    matrix: List[List[float]]
    confidence: float
    converged: bool
    shift: Tuple[float, float]
    inliers: int = 0
    note: str = ''

    def to_dict(self) -> Dict[str, Any]:
        """A JSON-serializable record, for presets and processing reports."""
        return {
            'index': self.index,
            'model': self.model,
            'method': self.method,
            'matrix': self.matrix,
            'confidence': round(self.confidence, 4),
            'converged': self.converged,
            'shift': [round(self.shift[0], 3), round(self.shift[1], 3)],
            'inliers': self.inliers,
            'note': self.note,
        }


def _to_gray(image: np.ndarray) -> np.ndarray:
    """Single-channel float32 in 0-1, which is what ECC wants."""
    img = image
    if img.ndim == 3:
        img = cv2.cvtColor(img[:, :, :3].astype(np.uint8), cv2.COLOR_RGB2GRAY)
    return img.astype(np.float32) / 255.0


def _identity(model: str) -> np.ndarray:
    """The do-nothing warp for a model."""
    if model == 'homography':
        return np.eye(3, dtype=np.float32)
    return np.eye(2, 3, dtype=np.float32)


def _shift_of(matrix: np.ndarray) -> Tuple[float, float]:
    """The translation the matrix carries, in pixels."""
    return (float(matrix[0, 2]), float(matrix[1, 2]))


def _validate(frames: Sequence[np.ndarray], reference: int, model: str,
              method: str) -> None:
    if frames is None or len(frames) == 0:
        raise ValueError("No frames provided")
    if not 0 <= reference < len(frames):
        raise ValueError(
            f"reference {reference} is outside the {len(frames)} frames given")
    if model not in MOTION_MODELS:
        available = ', '.join(MOTION_MODELS)
        raise ValueError(f"Unknown model '{model}'. Available: {available}")
    if method not in METHODS:
        raise ValueError(
            f"Unknown method '{method}'. Available: {', '.join(METHODS)}")

    first = frames[reference].shape[:2]
    for index, frame in enumerate(frames):
        if frame.shape[:2] != first:
            raise ValueError(
                f"Frame {index} is {frame.shape[1]}x{frame.shape[0]}, expected "
                f"{first[1]}x{first[0]}. Frames must share a size to be aligned.")


def _features_estimate(
    reference_gray: np.ndarray,
    frame_gray: np.ndarray,
    model: str,
    max_features: int = 2000,
) -> Tuple[Optional[np.ndarray], float, int, str]:
    """
    Estimate the warp from matched ORB features.

    Robust to large motion, and needs texture: a blank wall or a heavy fog gives
    nothing to match. Points are ordered (reference, frame) so the estimate
    comes out in this module's reference-to-frame convention with no inversion.

    Returns:
        (matrix or None, inlier ratio, inlier count, note)
    """
    reference_u8 = (reference_gray * 255).astype(np.uint8)
    frame_u8 = (frame_gray * 255).astype(np.uint8)

    orb = cv2.ORB_create(nfeatures=max_features)
    kp_ref, des_ref = orb.detectAndCompute(reference_u8, None)
    kp_frame, des_frame = orb.detectAndCompute(frame_u8, None)

    if des_ref is None or des_frame is None or len(kp_ref) < 4 or len(kp_frame) < 4:
        return None, 0.0, 0, 'too few features to match'

    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = matcher.match(des_ref, des_frame)
    if len(matches) < 4:
        return None, 0.0, 0, f'only {len(matches)} feature matches'

    matches = sorted(matches, key=lambda m: m.distance)
    points_ref = np.float32([kp_ref[m.queryIdx].pt for m in matches])
    points_frame = np.float32([kp_frame[m.trainIdx].pt for m in matches])

    if model == 'homography':
        matrix, mask = cv2.findHomography(points_ref, points_frame, cv2.RANSAC,
                                          ransacReprojThreshold=3.0)
    elif model == 'affine':
        matrix, mask = cv2.estimateAffine2D(points_ref, points_frame,
                                            method=cv2.RANSAC,
                                            ransacReprojThreshold=3.0)
    else:
        # Partial affine is rotation, uniform scale and translation
        matrix, mask = cv2.estimateAffinePartial2D(points_ref, points_frame,
                                                   method=cv2.RANSAC,
                                                   ransacReprojThreshold=3.0)

    if matrix is None:
        return None, 0.0, 0, 'no consistent transform among the matches'

    matrix = matrix.astype(np.float32)
    inliers = int(mask.sum()) if mask is not None else len(matches)
    ratio = inliers / max(1, len(matches))

    if model == 'translation':
        # Keep only what a translation model may carry
        translation = _identity('translation')
        translation[0, 2] = matrix[0, 2]
        translation[1, 2] = matrix[1, 2]
        matrix = translation
    elif model == 'euclidean':
        # estimateAffinePartial2D includes a uniform scale; a euclidean model
        # does not, so divide it out rather than letting it through unnoticed
        linear = matrix[:2, :2]
        scale = float(np.sqrt(abs(np.linalg.det(linear))))
        if scale > 1e-6:
            matrix[:2, :2] = linear / scale

    return matrix, float(ratio), inliers, ''


def _ecc_estimate(
    reference_gray: np.ndarray,
    frame_gray: np.ndarray,
    model: str,
    initial: Optional[np.ndarray] = None,
    iterations: int = 100,
    epsilon: float = 1e-5,
) -> Tuple[Optional[np.ndarray], float, str]:
    """
    Refine or find the warp by maximising enhanced correlation.

    Sub-pixel accurate and needs no features, but it is a local search: without
    a starting point it only converges for small motions, which is why ``auto``
    seeds it from the feature estimate.

    Returns:
        (matrix or None, correlation coefficient, note)
    """
    warp = _identity(model) if initial is None else initial.astype(np.float32).copy()
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, iterations, epsilon)

    try:
        correlation, warp = cv2.findTransformECC(
            reference_gray, frame_gray, warp, MOTION_MODELS[model],
            criteria, None, 5,
        )
    except cv2.error as exc:
        # ECC raises rather than returning a failure when it cannot converge
        message = str(exc).strip().splitlines()[-1] if str(exc) else 'ECC failed'
        return None, 0.0, message

    if not np.all(np.isfinite(warp)):
        return None, 0.0, 'ECC produced a non-finite warp'

    return warp.astype(np.float32), float(correlation), ''


def estimate_alignment(
    frame: np.ndarray,
    reference: np.ndarray,
    model: str = 'euclidean',
    method: str = 'auto',
    index: int = 0,
) -> Alignment:
    """
    Measure how one frame sits relative to a reference.

    Args:
        frame: The frame to place
        reference: The frame to place it against
        model: One of MOTION_MODELS - the freedom the camera actually had
        method: 'features' (robust to large motion), 'ecc' (sub-pixel, local),
            or 'auto', which seeds ECC from the feature estimate and so gets
            both. 'auto' falls back to whichever half succeeded.
        index: The frame's position in its sequence, recorded in the result

    Returns:
        An Alignment, whose ``converged`` says whether anything was measured

    Example:
        >>> result = estimate_alignment(frames[3], frames[0], model='euclidean')
        >>> result.confidence > 0.5
        True
    """
    if model not in MOTION_MODELS:
        available = ', '.join(MOTION_MODELS)
        raise ValueError(f"Unknown model '{model}'. Available: {available}")
    if method not in METHODS:
        raise ValueError(
            f"Unknown method '{method}'. Available: {', '.join(METHODS)}")

    reference_gray = _to_gray(reference)
    frame_gray = _to_gray(frame)

    def result(matrix, confidence, used, converged, inliers=0, note=''):
        final = _identity(model) if matrix is None else matrix
        return Alignment(
            index=index, model=model, method=used,
            matrix=[[float(v) for v in row] for row in np.asarray(final)],
            confidence=confidence, converged=converged,
            shift=_shift_of(np.asarray(final)), inliers=inliers, note=note,
        )

    if method == 'ecc':
        matrix, correlation, note = _ecc_estimate(reference_gray, frame_gray, model)
        return result(matrix, correlation, 'ecc', matrix is not None, note=note)

    matrix, ratio, inliers, note = _features_estimate(
        reference_gray, frame_gray, model)

    if method == 'features':
        return result(matrix, ratio, 'features', matrix is not None,
                      inliers=inliers, note=note)

    # auto: the feature estimate is a starting point, not the answer
    refined, correlation, ecc_note = _ecc_estimate(
        reference_gray, frame_gray, model, initial=matrix)

    if refined is not None:
        seeded = 'features+ecc' if matrix is not None else 'ecc'
        return result(refined, correlation, seeded, True, inliers=inliers)

    if matrix is not None:
        # ECC would not converge, but the features agreed on something
        return result(matrix, ratio, 'features', True, inliers=inliers,
                      note=f'ECC did not refine: {ecc_note}')

    return result(None, 0.0, 'auto', False,
                  note=note or ecc_note or 'no transform found')


def warp_frame(
    frame: np.ndarray,
    matrix: Sequence[Sequence[float]],
    model: str = 'euclidean',
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Bring one frame into the reference's coordinates.

    Args:
        frame: The frame to move
        matrix: Its alignment matrix, mapping reference to frame coordinates
        model: The motion model the matrix was built for

    Returns:
        (aligned frame, validity mask) - the mask is 0 where the warp pulled in
        pixels the frame never had, which is the region a combination must not
        treat as data
    """
    array = np.asarray(matrix, dtype=np.float32)
    height, width = frame.shape[:2]
    flags = cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP
    ones = np.ones((height, width), dtype=np.uint8)

    if model == 'homography':
        aligned = cv2.warpPerspective(frame, array, (width, height), flags=flags,
                                      borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        valid = cv2.warpPerspective(ones, array, (width, height),
                                    flags=cv2.INTER_NEAREST | cv2.WARP_INVERSE_MAP,
                                    borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    else:
        aligned = cv2.warpAffine(frame, array, (width, height), flags=flags,
                                 borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        valid = cv2.warpAffine(ones, array, (width, height),
                               flags=cv2.INTER_NEAREST | cv2.WARP_INVERSE_MAP,
                               borderMode=cv2.BORDER_CONSTANT, borderValue=0)

    return aligned, valid


def _largest_rectangle(mask: np.ndarray) -> Tuple[int, int, int, int]:
    """
    The largest axis-aligned rectangle of set pixels in a binary mask.

    The standard histogram scan: for each row, the run of set pixels ending
    there in each column forms a histogram, and the largest rectangle under it
    is found with a monotonic stack. O(width x height) overall.

    A whole-row / whole-column scan would be simpler and is what this started
    as, but it only finds anything when the valid region is itself a rectangle.
    Rotate a frame by a degree and the region becomes a tilted quadrilateral,
    where no row spans the full width - and the simple version reports that the
    frames have nothing in common.

    Returns:
        (x, y, width, height), or a zero-size region if the mask is empty
    """
    height, width = mask.shape
    heights = np.zeros(width + 1, dtype=np.int32)
    best_area = 0
    best = (0, 0, 0, 0)

    for y in range(height):
        heights[:width] = np.where(mask[y], heights[:width] + 1, 0)

        # Sentinel zero at the end flushes the stack at each row's close
        stack: List[Tuple[int, int]] = []
        for x in range(width + 1):
            start = x
            column_height = int(heights[x])
            while stack and stack[-1][1] > column_height:
                left, tall = stack.pop()
                area = tall * (x - left)
                if area > best_area:
                    best_area = area
                    best = (left, y - tall + 1, x - left, tall)
                start = left
            stack.append((start, column_height))

    return best


def common_valid_region(masks: Sequence[np.ndarray]) -> Tuple[int, int, int, int]:
    """
    The largest rectangle every frame actually covers.

    Aligning slides and turns each frame, so its far edge leaves a strip with no
    data behind it. Averaging over that strip mixes real pixels with black and
    darkens the border - a visible artefact that looks like vignetting and is
    not. Cropping to this region is the honest answer: the border is data the
    sequence does not have.

    Args:
        masks: Per-frame validity masks from ``warp_frame``

    Returns:
        (x, y, width, height)

    Raises:
        ValueError: If no region is valid in every frame
    """
    if masks is None or len(masks) == 0:
        raise ValueError("No masks provided")

    combined = masks[0].astype(bool)
    for mask in masks[1:]:
        combined &= mask.astype(bool)

    x, y, width, height = _largest_rectangle(combined)

    if width == 0 or height == 0:
        raise ValueError(
            "The frames have no area in common after alignment. They may not "
            "show the same scene, or the motion may be larger than the frame.")

    return (x, y, width, height)


def align_frames(
    frames: Sequence[np.ndarray],
    reference: int = 0,
    model: str = 'euclidean',
    method: str = 'auto',
    crop: bool = True,
    min_confidence: float = DEFAULT_MIN_CONFIDENCE,
) -> Tuple[List[np.ndarray], List[Alignment]]:
    """
    Align a sequence so it can be averaged, medianed or reconstructed.

    Frames that could not be matched are left out of the returned stack rather
    than warped on a guess: a misaligned frame in an average is exactly the blur
    stabilising exists to prevent, and it would be invisible in the result. The
    reference is always kept.

    Args:
        frames: Frames of a common size
        reference: Index of the frame the others are brought to
        model: The freedom the camera had; see MOTION_MODELS
        method: 'auto', 'features' or 'ecc'
        crop: Trim every frame to the region all of them cover, which avoids
            averaging real pixels against the empty border alignment leaves
        min_confidence: Frames scoring below this are dropped

    Returns:
        (aligned frames, one Alignment per input frame - including the dropped
        ones, so the caller can say what happened to each)

    Raises:
        ValueError: If the inputs are malformed, or nothing but the reference
            could be aligned

    Example:
        >>> aligned, results = align_frames(frames, model='euclidean')
        >>> clean = average_frames(aligned)
    """
    _validate(frames, reference, model, method)

    results: List[Alignment] = []
    kept: List[np.ndarray] = []
    masks: List[np.ndarray] = []

    for index, frame in enumerate(frames):
        if index == reference:
            results.append(Alignment(
                index=index, model=model, method='reference',
                matrix=[[float(v) for v in row] for row in _identity(model)],
                confidence=1.0, converged=True, shift=(0.0, 0.0),
                note='the frame others were aligned to',
            ))
            kept.append(frame)
            masks.append(np.ones(frame.shape[:2], dtype=np.uint8))
            continue

        alignment = estimate_alignment(frame, frames[reference], model=model,
                                       method=method, index=index)

        if not alignment.converged or alignment.confidence < min_confidence:
            if alignment.converged:
                alignment.note = (
                    f'dropped: confidence {alignment.confidence:.2f} below '
                    f'{min_confidence:.2f}')
            results.append(alignment)
            continue

        aligned, mask = warp_frame(frame, alignment.matrix, model)
        results.append(alignment)
        kept.append(aligned)
        masks.append(mask)

    if len(kept) < 2:
        measured = ', '.join(
            f'{r.index}: {r.note or "no match"}' for r in results
            if r.index != reference)
        raise ValueError(
            f"Only the reference frame could be aligned, so combining them "
            f"would return that frame alone. Try model='homography' for a "
            f"panning camera, or method='features' for large motion. "
            f"Frames: {measured}")

    if crop:
        x, y, width, height = common_valid_region(masks)
        kept = [frame[y:y + height, x:x + width] for frame in kept]

    return kept, results


def alignment_report(results: Sequence[Alignment]) -> Dict[str, Any]:
    """
    Summarise an alignment, for a processing report or a verbose run.

    Args:
        results: The per-frame results from ``align_frames``

    Returns:
        Dict with counts, the confidence range, the largest motion seen, and
        the per-frame records
    """
    if results is None or len(results) == 0:
        raise ValueError("No alignment results provided")

    used = [r for r in results if r.converged]
    dropped = [r for r in results if not r.converged
               or r.note.startswith('dropped')]
    confidences = [r.confidence for r in used] or [0.0]
    motions = [float(np.hypot(*r.shift)) for r in used] or [0.0]

    return {
        'frames': len(results),
        'aligned': len(results) - len(dropped),
        'dropped': len(dropped),
        'model': results[0].model,
        'min_confidence': round(min(confidences), 4),
        'mean_confidence': round(float(np.mean(confidences)), 4),
        'max_shift_pixels': round(max(motions), 2),
        'per_frame': [r.to_dict() for r in results],
    }
