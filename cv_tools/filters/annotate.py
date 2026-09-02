"""
Annotate - Marks, callouts, and measurements.

Two distinct jobs live here. Drawing arrows and labels is presentation: it
points a reader at something without claiming anything about it. Measurement is
different - it produces numbers that may be relied on, so it carries the
constraints that make those numbers meaningful.

Measuring from an image requires a scale, and a scale is only valid for the
plane it was measured in. A ruler laid on the ground calibrates distances on
the ground; it says nothing about a sign three metres behind, which is further
from the camera and therefore smaller per pixel. Perspective must be corrected
first (``perspective_correction.py``), and even then the calibration holds only
within that rectified plane.

Annotations are drawn onto a copy. Keep the unannotated original: a marked-up
image is a figure, not evidence.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import cv2
import numpy as np

_FONT = cv2.FONT_HERSHEY_SIMPLEX


def _prepare(image: np.ndarray) -> np.ndarray:
    """Return a writable 3-channel copy, so annotations can be coloured."""
    img = image.astype(np.uint8) if image.dtype != np.uint8 else image

    if img.ndim == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    if img.shape[2] == 1:
        return cv2.cvtColor(img[:, :, 0], cv2.COLOR_GRAY2RGB)
    if img.shape[2] == 4:
        return img[:, :, :3].copy()
    return img.copy()


def _as_points(points: Sequence[Any]) -> List[Tuple[float, float]]:
    """
    Normalise a point list, accepting pairs or a flat run of coordinates.

    A form field or a command line hands over ``x1,y1,x2,y2`` as four numbers,
    while library callers pass ``[(x1, y1), (x2, y2)]``. Both mean the same
    thing, and resolving it here rather than in each caller means the two front
    ends and the CLI do not need three copies of the same rule.

    Raises:
        ValueError: If the list is empty, has an odd number of flat
            coordinates, or contains something that is not an (x, y) pair
    """
    if points is None or len(points) == 0:
        raise ValueError("No points given")

    if isinstance(points[0], (int, float, np.integer, np.floating)):
        if len(points) % 2 != 0:
            raise ValueError(
                f"A flat coordinate list needs an even number of values, "
                f"got {len(points)}"
            )
        return [(float(points[i]), float(points[i + 1]))
                for i in range(0, len(points), 2)]

    pairs = []
    for index, point in enumerate(points):
        try:
            x, y = point
        except (TypeError, ValueError):
            raise ValueError(
                f"Point {index} is not an (x, y) pair: {point!r}"
            ) from None
        pairs.append((float(x), float(y)))
    return pairs


def _draw_label(
    image: np.ndarray,
    text: str,
    position: Tuple[int, int],
    color: Tuple[int, int, int],
    scale: float,
    thickness: int,
    background: bool = True,
) -> None:
    """Draw text with an optional plate behind it, so it stays readable."""
    x, y = position
    (text_w, text_h), baseline = cv2.getTextSize(text, _FONT, scale, thickness)

    if background:
        cv2.rectangle(
            image,
            (x - 4, y - text_h - 4),
            (x + text_w + 4, y + baseline + 2),
            (0, 0, 0), -1,
        )

    cv2.putText(image, text, (x, y), _FONT, scale, color, thickness, cv2.LINE_AA)


def draw_arrow(
    image: np.ndarray,
    start: Sequence[int],
    end: Sequence[int],
    color: Tuple[int, int, int] = (255, 40, 40),
    thickness: int = 2,
    tip_length: float = 0.15,
    label: Optional[str] = None,
    font_scale: float = 0.5,
) -> np.ndarray:
    """
    Draw an arrow, optionally labelled at its tail.

    Args:
        image: Input image
        start: Tail (x, y)
        end: Head (x, y) - the thing being pointed at
        color: RGB colour
        thickness: Line thickness
        tip_length: Arrowhead length as a fraction of the shaft
        label: Optional text at the tail
        font_scale: Label size

    Returns:
        Annotated RGB copy

    Example:
        >>> marked = draw_arrow(frame, (400, 300), (280, 210), label='plate')
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if thickness < 1:
        raise ValueError(f"thickness must be at least 1, got {thickness}")

    result = _prepare(image)
    p1 = (int(start[0]), int(start[1]))
    p2 = (int(end[0]), int(end[1]))

    cv2.arrowedLine(result, p1, p2, color, thickness, cv2.LINE_AA, tipLength=tip_length)

    if label:
        _draw_label(result, label, (p1[0] + 6, p1[1] - 6), color, font_scale, thickness)

    return result


def draw_text(
    image: np.ndarray,
    text: str,
    position: Sequence[int],
    color: Tuple[int, int, int] = (255, 255, 255),
    font_scale: float = 0.6,
    thickness: int = 1,
    background: bool = True,
) -> np.ndarray:
    """
    Draw a text label.

    Args:
        image: Input image
        text: The label
        position: Bottom-left (x, y) of the text
        color: RGB colour
        font_scale: Text size
        thickness: Stroke thickness
        background: Draw a dark plate behind the text

    Returns:
        Annotated RGB copy
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if not text:
        raise ValueError("text must not be empty")

    result = _prepare(image)
    _draw_label(
        result, text, (int(position[0]), int(position[1])),
        color, font_scale, thickness, background,
    )
    return result


def draw_shape(
    image: np.ndarray,
    shape: str,
    points: Sequence[Sequence[int]],
    color: Tuple[int, int, int] = (255, 40, 40),
    thickness: int = 2,
    label: Optional[str] = None,
) -> np.ndarray:
    """
    Draw a rectangle, circle, ellipse, line, or polygon.

    Args:
        image: Input image
        shape: 'rectangle', 'circle', 'ellipse', 'line', or 'polygon'
        points: Defining points. Rectangle and line take two corners or ends;
                circle takes a centre and a point on the rim; ellipse takes a
                centre and a point giving both radii; polygon takes three or
                more vertices.
        color: RGB colour
        thickness: Outline thickness; -1 fills the shape
        label: Optional text near the first point

    Returns:
        Annotated RGB copy
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")

    result = _prepare(image)
    array = [(int(round(x)), int(round(y))) for x, y in _as_points(points)]

    if shape in ('rectangle', 'line', 'circle', 'ellipse') and len(array) != 2:
        raise ValueError(f"'{shape}' needs exactly 2 points, got {len(array)}")

    if shape == 'rectangle':
        cv2.rectangle(result, array[0], array[1], color, thickness, cv2.LINE_AA)
    elif shape == 'line':
        cv2.line(result, array[0], array[1], color, thickness, cv2.LINE_AA)
    elif shape == 'circle':
        radius = int(round(np.hypot(array[1][0] - array[0][0],
                                    array[1][1] - array[0][1])))
        cv2.circle(result, array[0], max(1, radius), color, thickness, cv2.LINE_AA)
    elif shape == 'ellipse':
        axes = (max(1, abs(array[1][0] - array[0][0])),
                max(1, abs(array[1][1] - array[0][1])))
        cv2.ellipse(result, array[0], axes, 0, 0, 360, color, thickness, cv2.LINE_AA)
    elif shape == 'polygon':
        if len(array) < 3:
            raise ValueError(f"'polygon' needs at least 3 points, got {len(array)}")
        pts = np.array(array, dtype=np.int32).reshape(-1, 1, 2)
        if thickness < 0:
            cv2.fillPoly(result, [pts], color)
        else:
            cv2.polylines(result, [pts], True, color, thickness, cv2.LINE_AA)
    else:
        raise ValueError(
            f"Unknown shape '{shape}'. Use rectangle, circle, ellipse, line, or polygon"
        )

    if label and array:
        _draw_label(result, label, (array[0][0], array[0][1] - 8), color, 0.5,
                    max(1, thickness))

    return result


# ---- Measurement ----

@dataclass
class Scale:
    """
    A pixels-to-units calibration, valid only in one image plane.

    Build it from a reference of known length in the scene - a ruler, a
    standard sign, a number plate.
    """
    pixels: float
    units: float
    unit_name: str = 'mm'

    def __post_init__(self):
        if self.pixels <= 0:
            raise ValueError(f"pixels must be positive, got {self.pixels}")
        if self.units <= 0:
            raise ValueError(f"units must be positive, got {self.units}")

    @property
    def units_per_pixel(self) -> float:
        return self.units / self.pixels

    def convert(self, pixel_distance: float) -> float:
        """Convert a pixel distance into calibrated units."""
        return float(pixel_distance) * self.units_per_pixel

    def __repr__(self) -> str:
        return (
            f"Scale({self.units_per_pixel:.4f} {self.unit_name}/px)"
        )


def measure_distance(
    point_a: Sequence[float],
    point_b: Sequence[float],
    scale: Optional[Scale] = None,
) -> Dict[str, Any]:
    """
    Measure the straight-line distance between two points (1D).

    Args:
        point_a: First (x, y)
        point_b: Second (x, y)
        scale: Calibration; without it only the pixel distance is returned

    Returns:
        Dict with the pixel distance and, if calibrated, the real distance

    Example:
        >>> scale = Scale(pixels=240, units=520, unit_name='mm')  # plate width
        >>> measure_distance((100, 200), (340, 200), scale)['distance']
        520.0
    """
    dx = float(point_b[0]) - float(point_a[0])
    dy = float(point_b[1]) - float(point_a[1])
    pixels = float(np.hypot(dx, dy))

    result: Dict[str, Any] = {
        'pixel_distance': pixels,
        'dx': dx,
        'dy': dy,
        'angle_degrees': float(np.degrees(np.arctan2(-dy, dx)) % 360.0),
    }

    if scale is not None:
        result['distance'] = scale.convert(pixels)
        result['unit'] = scale.unit_name

    return result


def measure_area(
    points: Sequence[Sequence[float]],
    scale: Optional[Scale] = None,
) -> Dict[str, Any]:
    """
    Measure the area of a polygon (2D), by the shoelace formula.

    Args:
        points: Three or more (x, y) vertices
        scale: Calibration; area converts by the square of the linear scale

    Returns:
        Dict with the pixel area, perimeter, and calibrated equivalents

    Example:
        >>> measure_area([(0, 0), (100, 0), (100, 50), (0, 50)])['pixel_area']
        5000.0
    """
    if points is None or len(points) == 0:
        raise ValueError("An area needs at least 3 points, got 0")

    array = np.asarray(_as_points(points), dtype=np.float64)
    if len(array) < 3:
        raise ValueError(f"An area needs at least 3 points, got {len(array)}")

    x, y = array[:, 0], array[:, 1]
    # Shoelace formula, absolute so vertex order does not matter
    pixel_area = float(abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))) / 2.0)

    edges = np.roll(array, -1, axis=0) - array
    perimeter = float(np.hypot(edges[:, 0], edges[:, 1]).sum())

    result: Dict[str, Any] = {
        'pixel_area': pixel_area,
        'pixel_perimeter': perimeter,
        'vertices': len(array),
    }

    if scale is not None:
        result['area'] = pixel_area * (scale.units_per_pixel ** 2)
        result['perimeter'] = perimeter * scale.units_per_pixel
        result['unit'] = scale.unit_name
        result['area_unit'] = f"{scale.unit_name}^2"

    return result


def draw_measurement(
    image: np.ndarray,
    point_a: Sequence[int],
    point_b: Sequence[int],
    scale: Optional[Scale] = None,
    color: Tuple[int, int, int] = (255, 220, 40),
    thickness: int = 2,
    font_scale: float = 0.5,
    precision: int = 1,
) -> np.ndarray:
    """
    Draw a dimension line between two points, labelled with its length.

    Args:
        image: Input image
        point_a: First (x, y)
        point_b: Second (x, y)
        scale: Calibration; without it the label is in pixels
        color: RGB colour
        thickness: Line thickness
        font_scale: Label size
        precision: Decimal places in the label

    Returns:
        Annotated RGB copy

    Example:
        >>> marked = draw_measurement(flat_plate, (40, 90), (280, 90),
        ...                           Scale(240, 520, 'mm'))
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")

    result = _prepare(image)
    p1 = (int(point_a[0]), int(point_a[1]))
    p2 = (int(point_b[0]), int(point_b[1]))

    measurement = measure_distance(p1, p2, scale)

    # A line with end ticks, so the exact endpoints are unambiguous
    cv2.line(result, p1, p2, color, thickness, cv2.LINE_AA)

    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    length = float(np.hypot(dx, dy))
    if length > 0:
        # Tick marks perpendicular to the measurement line
        nx, ny = -dy / length, dx / length
        tick = 6
        for point in (p1, p2):
            cv2.line(
                result,
                (int(point[0] - nx * tick), int(point[1] - ny * tick)),
                (int(point[0] + nx * tick), int(point[1] + ny * tick)),
                color, thickness, cv2.LINE_AA,
            )

    if scale is not None:
        text = f"{measurement['distance']:.{precision}f} {scale.unit_name}"
    else:
        text = f"{measurement['pixel_distance']:.{precision}f} px"

    midpoint = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)
    _draw_label(result, text, (midpoint[0] + 8, midpoint[1] - 8), color,
                font_scale, max(1, thickness - 1))

    return result


def draw_area_measurement(
    image: np.ndarray,
    points: Sequence[Sequence[float]],
    scale: Optional[Scale] = None,
    color: Tuple[int, int, int] = (255, 220, 40),
    thickness: int = 2,
    font_scale: float = 0.5,
    precision: int = 1,
    show_perimeter: bool = False,
) -> np.ndarray:
    """
    Draw a closed polygon, labelled with its area.

    The 2D counterpart of ``draw_measurement``. Area converts by the *square* of
    the linear scale, which is why a calibration that is slightly wrong is
    twice as wrong here - read the caveats on ``Scale`` before quoting the
    number.

    Args:
        image: Input image
        points: Three or more (x, y) vertices, or a flat run of coordinates
        scale: Calibration; without it the label is in square pixels
        color: RGB colour
        thickness: Outline thickness
        font_scale: Label size
        precision: Decimal places in the label
        show_perimeter: Add the perimeter on a second line

    Returns:
        Annotated RGB copy

    Example:
        >>> marked = draw_area_measurement(flat, [(10, 10), (90, 10), (90, 60),
        ...                                       (10, 60)], Scale(240, 520, 'mm'))
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")

    measurement = measure_area(points, scale)
    array = _as_points(points)
    vertices = [(int(round(x)), int(round(y))) for x, y in array]

    result = _prepare(image)
    polygon = np.array(vertices, dtype=np.int32).reshape(-1, 1, 2)
    cv2.polylines(result, [polygon], True, color, thickness, cv2.LINE_AA)

    # Mark the vertices, so a reader can see exactly which points were clicked
    for vertex in vertices:
        cv2.circle(result, vertex, max(2, thickness + 1), color, -1, cv2.LINE_AA)

    if scale is not None:
        text = f"{measurement['area']:.{precision}f} {measurement['area_unit']}"
    else:
        text = f"{measurement['pixel_area']:.{precision}f} px^2"

    # Mean of the vertices, not the true centroid: both can fall outside a
    # concave polygon, and this one does not need the area to compute it
    centre_x = int(round(sum(x for x, _ in array) / len(array)))
    centre_y = int(round(sum(y for _, y in array) / len(array)))
    label_thickness = max(1, thickness - 1)
    _draw_label(result, text, (centre_x, centre_y), color, font_scale,
                label_thickness)

    if show_perimeter:
        if scale is not None:
            perimeter = f"{measurement['perimeter']:.{precision}f} {measurement['unit']}"
        else:
            perimeter = f"{measurement['pixel_perimeter']:.{precision}f} px"
        _draw_label(result, perimeter, (centre_x, centre_y + 18), color,
                    font_scale, label_thickness)

    return result


def draw_scale_bar(
    image: np.ndarray,
    scale: Scale,
    length_units: float = 100.0,
    position: str = 'bottom_right',
    color: Tuple[int, int, int] = (255, 255, 255),
    margin: int = 20,
    font_scale: float = 0.5,
) -> np.ndarray:
    """
    Draw a calibrated scale bar, so a reader can judge sizes directly.

    Args:
        image: Input image
        scale: Calibration
        length_units: Bar length in calibrated units
        position: 'bottom_right', 'bottom_left', 'top_right', or 'top_left'
        color: RGB colour
        margin: Distance from the frame edge in pixels
        font_scale: Label size

    Returns:
        Annotated RGB copy
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if length_units <= 0:
        raise ValueError(f"length_units must be positive, got {length_units}")

    result = _prepare(image)
    height, width = result.shape[:2]

    bar_pixels = int(round(length_units / scale.units_per_pixel))
    if bar_pixels < 2:
        raise ValueError(
            f"A {length_units} {scale.unit_name} bar is only {bar_pixels}px at this "
            f"scale; choose a larger length"
        )
    if bar_pixels > width - 2 * margin:
        raise ValueError(
            f"A {length_units} {scale.unit_name} bar is {bar_pixels}px, wider than "
            f"the image; choose a smaller length"
        )

    positions = {
        'bottom_right': (width - margin - bar_pixels, height - margin),
        'bottom_left': (margin, height - margin),
        'top_right': (width - margin - bar_pixels, margin + 20),
        'top_left': (margin, margin + 20),
    }
    if position not in positions:
        available = ', '.join(sorted(positions))
        raise ValueError(f"Unknown position '{position}'. Available: {available}")

    x, y = positions[position]

    cv2.rectangle(result, (x - 6, y - 26), (x + bar_pixels + 6, y + 8), (0, 0, 0), -1)
    cv2.line(result, (x, y), (x + bar_pixels, y), color, 3, cv2.LINE_AA)
    for end_x in (x, x + bar_pixels):
        cv2.line(result, (end_x, y - 5), (end_x, y + 5), color, 3, cv2.LINE_AA)

    text = f"{length_units:g} {scale.unit_name}"
    (text_w, _), _ = cv2.getTextSize(text, _FONT, font_scale, 1)
    cv2.putText(
        result, text, (x + (bar_pixels - text_w) // 2, y - 10),
        _FONT, font_scale, color, 1, cv2.LINE_AA,
    )

    return result


def scale_from_reference(
    point_a: Sequence[float],
    point_b: Sequence[float],
    known_length: float,
    unit_name: str = 'mm',
) -> Scale:
    """
    Build a calibration from two points spanning something of known length.

    Args:
        point_a: One end of the reference (x, y)
        point_b: The other end (x, y)
        known_length: The reference's true length
        unit_name: Unit of that length

    Returns:
        The calibration, valid only within the reference's own image plane

    Example:
        >>> # A EU number plate is 520 mm wide
        >>> scale = scale_from_reference((100, 200), (340, 200), 520, 'mm')
    """
    pixels = float(np.hypot(
        float(point_b[0]) - float(point_a[0]),
        float(point_b[1]) - float(point_a[1]),
    ))
    if pixels <= 0:
        raise ValueError("The two reference points are identical")

    return Scale(pixels=pixels, units=known_length, unit_name=unit_name)
