"""
Perspective Correction - Four-point rectification.

A surface photographed at an angle appears as a trapezoid, and measurements
taken from it are meaningless. Mapping four known corners onto a rectangle
restores the surface to a face-on view, which makes text legible and distances
proportional again.

The output geometry is only as good as the corners you supply. When the true
aspect ratio of the surface is known - A4 paper, a number plate, a door - pass
it, because estimating it from a perspective view is unreliable.

Note that rectification resamples: every output pixel is interpolated from the
original. It repositions evidence, it does not add any.
"""

from typing import List, Optional, Sequence, Tuple

import cv2
import numpy as np

# Real-world width:height ratios worth having to hand
KNOWN_RATIOS = {
    'a4_portrait': 210.0 / 297.0,
    'a4_landscape': 297.0 / 210.0,
    'us_letter': 8.5 / 11.0,
    'credit_card': 85.60 / 53.98,
    'plate_eu': 520.0 / 110.0,
    'plate_us': 12.0 / 6.0,
    'square': 1.0,
}


def order_corners(points: Sequence[Sequence[float]]) -> np.ndarray:
    """
    Sort four points into top-left, top-right, bottom-right, bottom-left.

    Corners clicked in any order therefore map correctly, instead of producing
    a mirrored or twisted result.

    Args:
        points: Four (x, y) pairs

    Returns:
        (4, 2) float32 array in the fixed order
    """
    array = np.asarray(points, dtype=np.float32)
    if array.shape != (4, 2):
        raise ValueError(f"Expected 4 (x, y) points, got shape {array.shape}")

    ordered = np.zeros((4, 2), dtype=np.float32)

    # The top-left has the smallest coordinate sum, the bottom-right the largest
    coordinate_sum = array.sum(axis=1)
    ordered[0] = array[np.argmin(coordinate_sum)]
    ordered[2] = array[np.argmax(coordinate_sum)]

    # The top-right has the smallest y - x difference, the bottom-left the largest
    difference = np.diff(array, axis=1).ravel()
    ordered[1] = array[np.argmin(difference)]
    ordered[3] = array[np.argmax(difference)]

    return ordered


def _output_size(
    corners: np.ndarray,
    aspect_ratio: Optional[float],
) -> Tuple[int, int]:
    """Choose an output size from the corner spacing and any known ratio."""
    top_left, top_right, bottom_right, bottom_left = corners

    width = max(np.linalg.norm(top_right - top_left),
                np.linalg.norm(bottom_right - bottom_left))
    height = max(np.linalg.norm(bottom_left - top_left),
                 np.linalg.norm(bottom_right - top_right))

    width = max(1.0, float(width))
    height = max(1.0, float(height))

    if aspect_ratio is not None and aspect_ratio > 0:
        # Keep the longer measured side and derive the other from the known
        # ratio, since the foreshortened side is the less reliable measurement
        if width >= height:
            height = width / aspect_ratio
        else:
            width = height * aspect_ratio

    return int(round(width)), int(round(height))


def correct_perspective(
    image: np.ndarray,
    corners: Sequence[Sequence[float]],
    aspect_ratio: Optional[float] = None,
    output_width: Optional[int] = None,
    output_height: Optional[int] = None,
    interpolation: str = 'lanczos',
) -> np.ndarray:
    """
    Rectify a quadrilateral region to a face-on rectangle.

    Args:
        image: Input image
        corners: The region's four corners as (x, y) pairs, any order
        aspect_ratio: Known width:height of the real surface. Names from
                      ``KNOWN_RATIOS`` may be passed to
                      ``correct_perspective_named`` instead.
        output_width: Force an output width; height follows the ratio
        output_height: Force an output height; width follows the ratio
        interpolation: 'nearest', 'bilinear', 'bicubic', or 'lanczos'.
                       'nearest' avoids inventing intermediate values.

    Returns:
        The rectified region

    Example:
        >>> flat = correct_perspective(frame, [(120, 80), (500, 60),
        ...                                    (530, 300), (100, 320)],
        ...                            aspect_ratio=KNOWN_RATIOS['plate_eu'])
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")

    interpolations = {
        'nearest': cv2.INTER_NEAREST,
        'bilinear': cv2.INTER_LINEAR,
        'bicubic': cv2.INTER_CUBIC,
        'lanczos': cv2.INTER_LANCZOS4,
    }
    if interpolation not in interpolations:
        available = ', '.join(sorted(interpolations))
        raise ValueError(f"Unknown interpolation '{interpolation}'. Available: {available}")

    ordered = order_corners(corners)
    width, height = _output_size(ordered, aspect_ratio)

    if output_width is not None and output_height is not None:
        width, height = int(output_width), int(output_height)
    elif output_width is not None:
        ratio = width / height if height else 1.0
        width = int(output_width)
        height = max(1, int(round(width / ratio)))
    elif output_height is not None:
        ratio = width / height if height else 1.0
        height = int(output_height)
        width = max(1, int(round(height * ratio)))

    if width < 1 or height < 1:
        raise ValueError(f"Computed output size is degenerate: {width}x{height}")

    destination = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1],
    ], dtype=np.float32)

    matrix = cv2.getPerspectiveTransform(ordered, destination)
    return cv2.warpPerspective(
        image, matrix, (width, height),
        flags=interpolations[interpolation],
        borderMode=cv2.BORDER_CONSTANT,
    )


def correct_perspective_named(
    image: np.ndarray,
    corners: Sequence[Sequence[float]],
    ratio_name: str,
    interpolation: str = 'lanczos',
) -> np.ndarray:
    """
    Rectify using a named real-world aspect ratio.

    Args:
        image: Input image
        corners: The region's four corners
        ratio_name: Key from ``KNOWN_RATIOS``
        interpolation: Resampling method

    Returns:
        The rectified region
    """
    if ratio_name not in KNOWN_RATIOS:
        available = ', '.join(sorted(KNOWN_RATIOS))
        raise ValueError(f"Unknown ratio '{ratio_name}'. Available: {available}")

    return correct_perspective(
        image, corners,
        aspect_ratio=KNOWN_RATIOS[ratio_name],
        interpolation=interpolation,
    )


def find_document_corners(
    image: np.ndarray,
    min_area_ratio: float = 0.1,
    blur_sigma: float = 2.0,
) -> Optional[np.ndarray]:
    """
    Try to locate a rectangular surface automatically.

    Looks for the largest four-sided contour. Works on a document or sign
    against a contrasting background; it will fail on a cluttered scene, and
    returning None is the expected outcome there rather than an error.

    Args:
        image: Input image
        min_area_ratio: Ignore quadrilaterals covering less than this fraction
                        of the frame
        blur_sigma: Pre-blur before edge detection, to suppress texture

    Returns:
        Four ordered corners, or None if no suitable quadrilateral was found

    Example:
        >>> corners = find_document_corners(scan)
        >>> flat = correct_perspective(scan, corners) if corners is not None else scan
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if not 0 < min_area_ratio <= 1:
        raise ValueError(f"min_area_ratio must be in (0, 1], got {min_area_ratio}")

    img = image.astype(np.uint8) if image.dtype != np.uint8 else image
    if img.ndim == 3:
        gray = cv2.cvtColor(img[:, :, :3], cv2.COLOR_RGB2GRAY)
    else:
        gray = img

    if blur_sigma > 0:
        gray = cv2.GaussianBlur(gray, (0, 0), sigmaX=blur_sigma, sigmaY=blur_sigma)

    median = float(np.median(gray))
    low = max(0.0, 0.66 * median)
    high = min(255.0, 1.33 * median)
    if high <= low:
        low, high = 50.0, 150.0

    edges = cv2.Canny(gray, low, high)
    # Close small gaps so a broken outline still forms one contour
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    frame_area = float(gray.shape[0] * gray.shape[1])
    for contour in sorted(contours, key=cv2.contourArea, reverse=True):
        area = cv2.contourArea(contour)
        if area < frame_area * min_area_ratio:
            break

        perimeter = cv2.arcLength(contour, True)
        approximation = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        if len(approximation) == 4:
            return order_corners(approximation.reshape(4, 2))

    return None


def auto_correct_perspective(
    image: np.ndarray,
    aspect_ratio: Optional[float] = None,
    min_area_ratio: float = 0.1,
) -> np.ndarray:
    """
    Detect a rectangular surface and rectify it, or return the image unchanged.

    Args:
        image: Input image
        aspect_ratio: Known width:height of the surface, if any
        min_area_ratio: Minimum fraction of the frame the surface must cover

    Returns:
        The rectified region, or the original image when nothing was found
    """
    corners = find_document_corners(image, min_area_ratio=min_area_ratio)
    if corners is None:
        return image.copy()
    return correct_perspective(image, corners, aspect_ratio=aspect_ratio)
