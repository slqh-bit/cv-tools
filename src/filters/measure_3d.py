"""
Measure 3D - object height from a single view, by single-view metrology.

``annotate.py`` measures within one rectified plane: lay a scale on the ground
and you can measure along the ground. That approach cannot give you the height
of a person standing on that ground, because height runs out of the plane the
scale was calibrated in.

This module recovers that third dimension the way Criminisi, Reid and Zisserman
set out in *Single View Metrology* (IJCV 40(2), 2000). Given the horizon of the
ground plane, the vanishing point of the scene's vertical direction, and one
reference object of known height standing on that ground, the height of any
other object standing on the same ground follows from a cross-ratio - a
quantity projection leaves unchanged.

    Z / Z_ref = [ |b x t| / ((l.b) |t x v|) ] / [ |b_r x t_r| / ((l.b_r) |t_r x v|) ]

with b, t the base and top of the target, b_r, t_r those of the reference, l
the horizon and v the vertical vanishing point, all homogeneous. The unknown
overall scale factor cancels, and so do the scales of l and v, which is why
neither needs normalising.

**What this cannot do.** The number it returns is an estimate carrying real
uncertainty, not a measurement:

- The target and the reference must stand on the *same* ground plane. A person
  on a kerb, a step, or a slope is measured against the wrong plane.
- Lens distortion must be corrected first (``undistort.py``,
  ``fisheye_correction.py``). Straight lines that image as curves put the
  vanishing geometry wrong before the arithmetic starts.
- The base point is the ground contact. A visible gap under a heel, or feet
  hidden behind an object, biases the result directly.
- Accuracy collapses as the base approaches the horizon: the same one-pixel
  error spans a rapidly growing real distance. ``measure_height`` reports a
  per-pixel sensitivity for exactly this reason - read it before quoting the
  height.
- Leaving ``vertical_point`` unset assumes scene verticals image as parallel.
  That is exact only for a camera with no pitch or roll. Against a synthetic
  camera 2.5 m up with a 1.8 m reference, the assumption cost roughly +16 mm
  at 5 degrees of pitch and +33 mm at 18 degrees, always over-reading. Supply
  the vertical vanishing point for a tilted camera - most CCTV is tilted.
"""

from typing import Any, Dict, Optional, Sequence, Tuple, Union

import cv2
import numpy as np

from .annotate import _draw_label, _prepare

# The vertical vanishing point for a camera with no roll, where scene
# verticals image as parallel lines: the point at infinity straight up.
VERTICAL_AT_INFINITY = np.array([0.0, 1.0, 0.0])


def _homogeneous(point: Sequence[float]) -> np.ndarray:
    """Convert an (x, y) image point to a homogeneous 3-vector."""
    if point is None or len(point) < 2:
        raise ValueError(f"Expected an (x, y) point, got {point!r}")
    return np.array([float(point[0]), float(point[1]), 1.0])


def line_through(point_a: Sequence[float], point_b: Sequence[float]) -> np.ndarray:
    """
    The homogeneous line through two image points.

    Example:
        >>> line_through((0, 10), (100, 10)).tolist()   # 100y - 1000 = 0, i.e. y = 10
        [0.0, 100.0, -1000.0]
    """
    line = np.cross(_homogeneous(point_a), _homogeneous(point_b))
    if not np.any(line):
        raise ValueError("The two points are identical, so they define no line")
    return line


def vanishing_point(lines: Sequence[Sequence[float]]) -> np.ndarray:
    """
    The common intersection of a set of scene-parallel lines.

    Each line is given by two points on it as ``(x1, y1, x2, y2)``. Two lines
    intersect exactly; more are solved in the least-squares sense, which is
    what you want from hand-clicked points. Lines that are parallel in the
    image yield the point at infinity in their direction - a valid homogeneous
    result that the height formula handles without special-casing, so it is
    returned unnormalised.

    Args:
        lines: Two or more lines, each ``(x1, y1, x2, y2)``

    Returns:
        Homogeneous 3-vector, unit length

    Raises:
        ValueError: If fewer than two lines are given

    Example:
        >>> v = vanishing_point([(0, 0, 10, 10), (20, 0, 10, 10)])
        >>> (v[:2] / v[2]).round().tolist()
        [10.0, 10.0]
    """
    if lines is None or len(lines) < 2:
        raise ValueError(
            f"A vanishing point needs at least 2 lines, got {len(lines or [])}"
        )

    rows = []
    for entry in lines:
        if len(entry) != 4:
            raise ValueError(f"Expected a line as (x1, y1, x2, y2), got {entry!r}")
        rows.append(line_through(entry[:2], entry[2:]))

    # The point lying on every line is the null space of the stacked lines
    _u, _s, vt = np.linalg.svd(np.asarray(rows, dtype=np.float64))
    return vt[-1]


def horizon_from_vanishing_points(
    point_a: Sequence[float],
    point_b: Sequence[float],
) -> np.ndarray:
    """
    The ground plane's vanishing line, through two of its vanishing points.

    Both arguments are homogeneous 3-vectors as returned by
    ``vanishing_point`` - typically one from each of two sets of ground lines
    running in different directions.
    """
    line = np.cross(np.asarray(point_a, dtype=np.float64),
                    np.asarray(point_b, dtype=np.float64))
    if not np.any(line):
        raise ValueError("The two vanishing points coincide, so they define no horizon")
    return line


def _flat_floats(values) -> list:
    """Flatten a mix of scalars and (x, y) pairs into one list of floats."""
    out = []
    for value in values:
        if isinstance(value, (list, tuple, np.ndarray)):
            out.extend(float(item) for item in value)
        else:
            out.append(float(value))
    return out


def horizon_from_lines(
    lines: Sequence[Sequence[float]],
    cross_lines: Optional[Sequence[Sequence[float]]] = None,
) -> np.ndarray:
    """
    The horizon from lines that are parallel in the scene, not on the horizon.

    This exists because asking someone for "two points on the horizon" asks
    them for the answer. The horizon is rarely visible indoors, and eyeballing
    it is the single largest error in a single-view height: put it on a ceiling
    rather than the vanishing point and the estimate moves by hundreds of
    millimetres while every reported sensitivity stays small and reassuring.

    Lines that are parallel in the scene meet at their vanishing point in the
    image, and the vanishing point of any direction parallel to the ground lies
    on the ground's horizon. So a corridor's floor edge and ceiling edge - both
    running the way the corridor runs - give a point the horizon passes
    through, and they are things you can actually see and click along.

    Args:
        lines: Two or more lines along one scene direction, each as
            ``(x1, y1, x2, y2)``. Their vanishing point is found by least
            squares. With only this set the horizon is taken horizontal through
            that point, which is exact for a camera with no roll.
        cross_lines: Two or more lines along a second, different scene
            direction. Supply these when the camera is rolled: the horizon then
            runs through both vanishing points and no levelness is assumed.

    Returns:
        Homogeneous 3-vector

    Raises:
        ValueError: If a set has fewer than two lines, or the two vanishing
            points coincide

    Example:
        >>> # two lines converging on (100, 50), camera level
        >>> h = horizon_from_lines([(0, 0, 100, 50), (0, 100, 100, 50)])
        >>> [round(v, 6) for v in (h / h[1])]
        [0.0, 1.0, -50.0]
    """
    point = vanishing_point(lines)

    if cross_lines is None:
        if abs(point[2]) < 1e-12:
            raise ValueError(
                "The lines are parallel in the image, so their vanishing point "
                "is at infinity and its height cannot place a level horizon. "
                "Supply cross_lines, or give the horizon directly")
        # Level camera: the horizon is the image row through the vanishing point
        return np.array([0.0, 1.0, -float(point[1] / point[2])])

    return horizon_from_vanishing_points(point, vanishing_point(cross_lines))


def resolve_horizon(horizon: Union[float, Sequence[float]]) -> np.ndarray:
    """
    Accept the several ways a horizon is naturally specified.

    Args:
        horizon: One of

            - a number ``y``: a level camera, horizon horizontal at that row
            - ``(a, b, c)``: the homogeneous line directly
            - ``(x1, y1, x2, y2)``: two points lying on the horizon
            - 8 numbers: two lines along one scene direction, as
              ``(x1, y1, x2, y2, x3, y3, x4, y4)``. Their vanishing point is
              solved for and the horizon taken horizontal through it - which is
              what you want indoors, where the horizon is not visible but the
              floor and ceiling edges are. Assumes the camera has no roll.
            - 16 numbers: four lines, the first two along one scene direction
              and the last two along another. The horizon runs through both
              vanishing points, so no levelness is assumed.

        Points may be given flat or as (x, y) pairs; both are accepted, because
        the parameter forms hand back whichever they parsed.

    Returns:
        Homogeneous 3-vector
    """
    if horizon is None:
        raise ValueError("A horizon is required; it cannot be guessed safely")

    if isinstance(horizon, (int, float, np.integer, np.floating)):
        # ax + by + c = 0 with a=0, b=1 is the horizontal row y = value
        return np.array([0.0, 1.0, -float(horizon)])

    values = _flat_floats(horizon)
    if len(values) == 4:
        return line_through(values[:2], values[2:])
    if len(values) == 3:
        line = np.asarray(values)
        if not np.any(line):
            raise ValueError("The horizon line is all zeros")
        return line
    if len(values) == 8:
        return horizon_from_lines([values[0:4], values[4:8]])
    if len(values) == 16:
        return horizon_from_lines([values[0:4], values[4:8]],
                                  [values[8:12], values[12:16]])

    raise ValueError(
        f"Expected a y value, (a, b, c), (x1, y1, x2, y2), 8 numbers for two "
        f"receding lines, or 16 for four; got {len(values)} numbers"
    )


def _height_term(
    base: np.ndarray,
    top: np.ndarray,
    horizon: np.ndarray,
    vertical: np.ndarray,
) -> float:
    """
    The projective quantity proportional to real height.

    Height is this term times a single scene-wide constant, so dividing the
    target's term by the reference's cancels the constant.
    """
    denominator = float(horizon @ base) * float(np.linalg.norm(np.cross(top, vertical)))

    if abs(denominator) < 1e-12:
        if abs(float(horizon @ base)) < 1e-12:
            raise ValueError(
                "The base point lies on the horizon, which is infinitely far "
                "away: no height can be recovered there"
            )
        raise ValueError(
            "The top point coincides with the vertical vanishing point, so the "
            "segment carries no measurable extent"
        )

    return float(np.linalg.norm(np.cross(base, top))) / denominator


def measure_height(
    base: Sequence[float],
    top: Sequence[float],
    reference_base: Sequence[float],
    reference_top: Sequence[float],
    reference_height: float,
    horizon: Union[float, Sequence[float]],
    vertical_point: Optional[Sequence[float]] = None,
    unit_name: str = 'mm',
) -> Dict[str, Any]:
    """
    Estimate the height of an object from one view (3D).

    Args:
        base: Target's ground contact point (x, y)
        top: Target's highest point (x, y)
        reference_base: Reference object's ground contact
        reference_top: Reference object's top
        reference_height: The reference's true height, in ``unit_name``
        horizon: Ground plane vanishing line - see ``resolve_horizon``
        vertical_point: Vanishing point of scene verticals, homogeneous or
                        (x, y). Defaults to the point at infinity, correct when
                        the camera has no roll and verticals image as parallel.
        unit_name: Unit the reference height is given in

    Returns:
        Dict with ``height``, ``unit``, ``ratio`` against the reference, and two
        sensitivities: ``uncertainty_per_pixel`` for a one-pixel error in the
        clicked base and top, and ``horizon_uncertainty_per_pixel`` for a
        one-pixel shift of the horizon. Read the second one first. A base and a
        top are clicked on features you can see and are rarely more than a
        pixel or two out; a horizon is inferred and is easily ten pixels out,
        so the smaller per-pixel figure is usually the larger real error.

    Raises:
        ValueError: If the reference height is not positive, the two bases
                    straddle the horizon, or the geometry is degenerate (base
                    on the horizon, top at the vanishing point)

    Example:
        >>> result = measure_height(
        ...     base=(300, 400), top=(300, 250),
        ...     reference_base=(150, 380), reference_top=(150, 250),
        ...     reference_height=1800, horizon=200)
        >>> round(result['height'])
        1869
    """
    if reference_height <= 0:
        raise ValueError(f"reference_height must be positive, got {reference_height}")

    line = resolve_horizon(horizon)
    vertical = (VERTICAL_AT_INFINITY if vertical_point is None
                else np.asarray([float(v) for v in vertical_point], dtype=np.float64))
    if vertical.shape == (2,):
        vertical = np.array([vertical[0], vertical[1], 1.0])
    if vertical.shape != (3,) or not np.any(vertical):
        raise ValueError(f"Invalid vertical vanishing point: {vertical_point!r}")

    base_h, top_h = _homogeneous(base), _homogeneous(top)
    reference_base_h, reference_top_h = (_homogeneous(reference_base),
                                         _homogeneous(reference_top))

    # Two objects standing on one ground plane image on one side of that
    # plane's horizon. Bases that straddle it are not a hard measurement, they
    # are an impossible one - almost always a horizon drawn somewhere else,
    # such as along a ceiling.
    side_target = float(line @ base_h)
    side_reference = float(line @ reference_base_h)
    if side_target * side_reference < 0:
        raise ValueError(
            "The target and reference bases fall on opposite sides of the "
            "horizon, which cannot happen for two objects on one ground plane. "
            "Check the horizon: it is usually drawn through the scene's "
            "vanishing point, not along a ceiling or a wall top")

    target_term = _height_term(base_h, top_h, line, vertical)
    reference_term = _height_term(reference_base_h, reference_top_h, line, vertical)

    if abs(reference_term) < 1e-12:
        raise ValueError("The reference segment has no measurable extent")

    ratio = target_term / reference_term
    height = ratio * float(reference_height)

    # Sensitivity: nudge each clicked point by a pixel along the measured
    # direction and see how far the answer moves. Near the horizon this grows
    # sharply, which is the single most useful warning this function can give.
    spread = 0.0
    for point_index, delta in ((0, 1.0), (0, -1.0), (1, 1.0), (1, -1.0)):
        points = [list(map(float, base)), list(map(float, top))]
        points[point_index][1] += delta
        try:
            nudged = _height_term(
                _homogeneous(points[0]), _homogeneous(points[1]), line, vertical)
        except ValueError:
            continue
        spread = max(spread, abs(nudged / reference_term * reference_height - height))

    # The horizon deserves its own figure. It is the input the estimate is most
    # sensitive to and the one a person is least able to place accurately: a
    # base and a top are clicked on visible features, while the horizon is
    # inferred from converging lines and is easily ten pixels out. Reporting
    # only the click sensitivity flatters the result, because it is the small
    # error on the input that is nearly always right.
    #
    # The nudge is perpendicular to the line, so it means one pixel however the
    # horizon is tilted: shifting a line by d perpendicular moves c by
    # d * hypot(a, b).
    horizon_spread = 0.0
    normal = float(np.hypot(line[0], line[1]))
    if normal > 1e-12:
        for delta in (1.0, -1.0):
            shifted = np.array([line[0], line[1], line[2] + delta * normal])
            try:
                nudged_target = _height_term(base_h, top_h, shifted, vertical)
                nudged_reference = _height_term(
                    reference_base_h, reference_top_h, shifted, vertical)
            except ValueError:
                continue
            if abs(nudged_reference) < 1e-12:
                continue
            horizon_spread = max(horizon_spread, abs(
                nudged_target / nudged_reference * reference_height - height))

    return {
        'height': float(height),
        'unit': unit_name,
        'ratio': float(ratio),
        'reference_height': float(reference_height),
        'uncertainty_per_pixel': float(spread),
        'horizon_uncertainty_per_pixel': float(horizon_spread),
    }


def _draw_dashed_line(
    image: np.ndarray,
    start: Tuple[int, int],
    end: Tuple[int, int],
    color: Tuple[int, int, int],
    thickness: int,
    dash: int = 12,
) -> None:
    """Draw a dashed line, so construction reads as construction."""
    x1, y1 = start
    x2, y2 = end
    length = float(np.hypot(x2 - x1, y2 - y1))
    if length < 1.0:
        return

    steps = max(int(length / dash), 1)
    for step in range(0, steps, 2):
        a = step / steps
        b = min((step + 1) / steps, 1.0)
        cv2.line(
            image,
            (int(round(x1 + (x2 - x1) * a)), int(round(y1 + (y2 - y1) * a))),
            (int(round(x1 + (x2 - x1) * b)), int(round(y1 + (y2 - y1) * b))),
            color, thickness, cv2.LINE_AA,
        )


def draw_height_measurement(
    image: np.ndarray,
    base: Sequence[float],
    top: Sequence[float],
    reference_base: Sequence[float],
    reference_top: Sequence[float],
    horizon: Union[float, Sequence[float]],
    reference_height: float = 1800.0,
    vertical_point: Optional[Sequence[float]] = None,
    unit_name: str = 'mm',
    color: Tuple[int, int, int] = (255, 220, 40),
    reference_color: Tuple[int, int, int] = (80, 200, 255),
    thickness: int = 2,
    font_scale: float = 0.5,
    precision: int = 0,
    show_horizon: bool = True,
    show_uncertainty: bool = True,
) -> np.ndarray:
    """
    Measure an object's height from one view and draw the result.

    The reference is drawn in its own colour and labelled with the height you
    supplied; the target is labelled with the height that was computed from it.
    Read ``measure_height``'s caveats before relying on the number - in
    particular, both objects must stand on the same ground plane.

    Args:
        image: Input image
        base: Target's ground contact (x, y)
        top: Target's top (x, y)
        reference_base: Reference's ground contact
        reference_top: Reference's top
        horizon: Ground vanishing line - a y value for a level camera,
                 ``(x1, y1, x2, y2)``, or ``(a, b, c)``
        reference_height: True height of the reference, in ``unit_name``
        vertical_point: Vertical vanishing point; omit when verticals are
                        parallel in the image
        unit_name: Unit label
        color: Target colour
        reference_color: Reference colour
        thickness: Line thickness
        font_scale: Label size
        precision: Decimal places in the labels
        show_horizon: Draw the horizon, which is what the estimate rests on
        show_uncertainty: Write the two per-pixel sensitivities under the
            height. The number on its own reads like a measurement; these say
            how far it moves when the inputs move, which is the difference
            between an estimate and a claim

    Returns:
        Annotated copy of the image
    """
    result = measure_height(
        base, top, reference_base, reference_top, reference_height,
        horizon, vertical_point, unit_name,
    )

    canvas = _prepare(image)
    height_px, width_px = canvas.shape[:2]

    if show_horizon:
        line = resolve_horizon(horizon)
        # Solve the line for y at each image edge; near-vertical horizons are
        # not drawable this way and are simply left out
        if abs(line[1]) > 1e-9:
            y_left = -(line[0] * 0 + line[2]) / line[1]
            y_right = -(line[0] * width_px + line[2]) / line[1]
            _draw_dashed_line(canvas, (0, int(round(y_left))),
                              (width_px, int(round(y_right))), (140, 140, 150), 1)

    for (start, end, tone, text) in (
        (reference_base, reference_top, reference_color,
         f"ref {reference_height:.{precision}f} {unit_name}"),
        (base, top, color,
         f"{result['height']:.{precision}f} {unit_name}"),
    ):
        p1 = (int(round(float(start[0]))), int(round(float(start[1]))))
        p2 = (int(round(float(end[0]))), int(round(float(end[1]))))
        cv2.line(canvas, p1, p2, tone, thickness, cv2.LINE_AA)

        # End caps, so the exact clicked points are visible for review
        for point in (p1, p2):
            cv2.circle(canvas, point, thickness + 2, tone, -1, cv2.LINE_AA)

        label_x = min(max(p2[0] + 8, 2), max(width_px - 4, 2))
        label_y = min(max(p2[1] - 6, 14), height_px - 4)
        _draw_label(canvas, text, (label_x, label_y), tone, font_scale, 1)

        if show_uncertainty and tone is color:
            note = (f"+/-{result['uncertainty_per_pixel']:.0f} per px clicked, "
                    f"+/-{result['horizon_uncertainty_per_pixel']:.0f} per px horizon")
            note_y = min(label_y + int(round(font_scale * 34)), height_px - 4)
            _draw_label(canvas, note, (label_x, note_y), tone,
                        font_scale * 0.8, 1)

    return canvas
