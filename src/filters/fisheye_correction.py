"""
Fisheye and Lens Distortion Correction.

Wide-angle and dome cameras bend straight lines, and the effect grows with
distance from the optical centre. Left uncorrected it distorts apparent
positions and proportions, so anything measured near the frame edge is wrong.

Two models are offered:

    - ``correct_barrel_distortion`` uses the polynomial radial model, tuned by
      hand. Enough for moderate wide-angle lenses.
    - ``correct_fisheye`` uses the equidistant fisheye model, for the strong
      curvature of a true fisheye or dome camera.

Both estimate the distortion rather than measure it. When the camera is
available, calibrate it instead - ``undistort.py`` derives the real
coefficients from chessboard images, which is the defensible route.
"""

from typing import Optional, Tuple

import cv2
import numpy as np


def _distortion_maps(
    shape: Tuple[int, int],
    k1: float,
    k2: float,
    zoom: float,
    center: Optional[Tuple[float, float]] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Build the remap tables for a polynomial radial model.

    Computed backwards - for each output pixel, where in the input does it come
    from - which is what cv2.remap needs and guarantees no holes in the result.
    """
    height, width = shape
    cx, cy = center if center is not None else (width / 2.0, height / 2.0)

    yy, xx = np.indices((height, width), dtype=np.float32)

    # Normalise by half the diagonal so the coefficients behave the same way
    # regardless of frame size
    norm = np.sqrt(width ** 2 + height ** 2) / 2.0

    x = (xx - cx) / norm
    y = (yy - cy) / norm
    r2 = x * x + y * y

    scale = 1.0 + k1 * r2 + k2 * r2 * r2

    map_x = (x * scale / zoom) * norm + cx
    map_y = (y * scale / zoom) * norm + cy

    return map_x.astype(np.float32), map_y.astype(np.float32)


def correct_barrel_distortion(
    image: np.ndarray,
    k1: float = -0.2,
    k2: float = 0.0,
    zoom: float = 1.0,
    border_mode: str = 'constant',
) -> np.ndarray:
    """
    Correct barrel or pincushion distortion with a polynomial radial model.

    Args:
        image: Input image
        k1: First radial coefficient. Negative corrects barrel distortion
            (lines bowing outwards, the usual wide-angle case); positive
            corrects pincushion.
        k2: Second radial coefficient, for residual curvature k1 leaves behind
        zoom: Scale applied while remapping. Above 1 crops into the frame,
              hiding the blank corners correction introduces.
        border_mode: 'constant', 'replicate', or 'reflect'

    Returns:
        Corrected image, same size as the input

    Example:
        >>> straightened = correct_barrel_distortion(wide_frame, k1=-0.25, zoom=1.15)
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if zoom <= 0:
        raise ValueError(f"zoom must be positive, got {zoom}")

    borders = {
        'constant': cv2.BORDER_CONSTANT,
        'replicate': cv2.BORDER_REPLICATE,
        'reflect': cv2.BORDER_REFLECT,
    }
    if border_mode not in borders:
        available = ', '.join(sorted(borders))
        raise ValueError(f"Unknown border_mode '{border_mode}'. Available: {available}")

    map_x, map_y = _distortion_maps(image.shape[:2], k1, k2, zoom)

    return cv2.remap(
        image, map_x, map_y,
        interpolation=cv2.INTER_LANCZOS4,
        borderMode=borders[border_mode],
    )


def correct_fisheye(
    image: np.ndarray,
    strength: float = 0.5,
    zoom: float = 1.0,
    border_mode: str = 'constant',
) -> np.ndarray:
    """
    Correct strong fisheye curvature with the equidistant model.

    A true fisheye maps angle to radius linearly rather than by a tangent, so
    the polynomial model fits it poorly at the edges. This inverts that
    projection directly.

    Args:
        image: Input image
        strength: Distortion amount, 0 (no change) to 1 (extreme). Around 0.5
                  suits a typical dome camera.
        zoom: Scale applied while remapping; above 1 crops away blank corners
        border_mode: 'constant', 'replicate', or 'reflect'

    Returns:
        Corrected image

    Example:
        >>> flat = correct_fisheye(dome_frame, strength=0.6, zoom=1.2)
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if not 0 <= strength <= 1:
        raise ValueError(f"strength must be between 0 and 1, got {strength}")
    if zoom <= 0:
        raise ValueError(f"zoom must be positive, got {zoom}")

    borders = {
        'constant': cv2.BORDER_CONSTANT,
        'replicate': cv2.BORDER_REPLICATE,
        'reflect': cv2.BORDER_REFLECT,
    }
    if border_mode not in borders:
        available = ', '.join(sorted(borders))
        raise ValueError(f"Unknown border_mode '{border_mode}'. Available: {available}")

    if strength == 0:
        return image.copy()

    height, width = image.shape[:2]
    cx, cy = width / 2.0, height / 2.0

    yy, xx = np.indices((height, width), dtype=np.float32)
    norm = np.sqrt(width ** 2 + height ** 2) / 2.0

    x = (xx - cx) / norm / zoom
    y = (yy - cy) / norm / zoom
    r = np.sqrt(x * x + y * y)

    # Equidistant projection: radius is proportional to the incident angle.
    # theta = atan(r) for the rectified ray, and the fisheye samples at theta.
    theta = np.arctan(r * strength * np.pi / 2.0)
    factor = np.divide(
        theta / (strength * np.pi / 2.0), r,
        out=np.ones_like(r), where=r > 1e-6,
    )

    map_x = (x * factor) * norm + cx
    map_y = (y * factor) * norm + cy

    return cv2.remap(
        image, map_x.astype(np.float32), map_y.astype(np.float32),
        interpolation=cv2.INTER_LANCZOS4,
        borderMode=borders[border_mode],
    )


def apply_barrel_distortion(
    image: np.ndarray,
    k1: float = 0.2,
    k2: float = 0.0,
) -> np.ndarray:
    """
    Apply distortion rather than remove it.

    Useful for building a test case with a known distortion, and for matching
    an undistorted overlay back onto original footage.

    Args:
        image: Input image
        k1: First radial coefficient; positive bows lines outwards
        k2: Second radial coefficient

    Returns:
        Distorted image
    """
    return correct_barrel_distortion(image, k1=k1, k2=k2, zoom=1.0,
                                     border_mode='constant')


def estimate_straightness(image: np.ndarray, min_line_length: int = 60) -> float:
    """
    Score how straight the long edges in an image are.

    Lens distortion bends straight lines into arcs, so a scene rich in straight
    edges scores lower before correction than after. Sweep a coefficient and
    keep the value that scores highest.

    The measure is only meaningful on scenes that contain straight lines -
    buildings, doorways, road markings - and says nothing about a natural
    scene without them.

    Args:
        image: Input image
        min_line_length: Shortest line segment counted, in pixels

    Returns:
        Score from 0 upwards; higher means more and longer straight lines

    Example:
        >>> best = max((estimate_straightness(correct_barrel_distortion(f, k1=k)), k)
        ...            for k in (-0.3, -0.2, -0.1, 0.0))
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if min_line_length < 2:
        raise ValueError(f"min_line_length must be at least 2, got {min_line_length}")

    img = image.astype(np.uint8) if image.dtype != np.uint8 else image
    if img.ndim == 3:
        gray = cv2.cvtColor(img[:, :, :3], cv2.COLOR_RGB2GRAY)
    else:
        gray = img

    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(
        edges, 1, np.pi / 180, threshold=50,
        minLineLength=min_line_length, maxLineGap=5,
    )

    if lines is None:
        return 0.0

    total = sum(
        float(np.hypot(x2 - x1, y2 - y1))
        for x1, y1, x2, y2 in lines.reshape(-1, 4)
    )
    return total / float(gray.shape[0] * gray.shape[1]) * 1000.0
