"""
Undistort - Calibration-based lens correction.

The defensible way to remove lens distortion. Rather than tuning a coefficient
until lines look straight, this derives the camera's actual intrinsic matrix
and distortion coefficients from photographs of a chessboard of known
geometry, then inverts exactly that.

The workflow:

    1. Photograph a chessboard from a dozen or more angles with the camera in
       question, at the same zoom and focus as the evidence footage.
    2. ``calibrate_from_chessboard`` recovers the camera model and reports the
       reprojection error, which tells you whether to trust it.
    3. ``save_calibration`` stores it; ``undistort`` applies it to the footage.

A calibration is specific to one camera at one zoom and focus setting. Applying
another camera's calibration is worse than applying none, because the result
looks plausible while being geometrically wrong.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import cv2
import numpy as np


class CameraCalibration:
    """A camera's intrinsic matrix and distortion coefficients."""

    def __init__(
        self,
        camera_matrix: np.ndarray,
        distortion: np.ndarray,
        image_size: Tuple[int, int],
        reprojection_error: float = 0.0,
    ):
        self.camera_matrix = np.asarray(camera_matrix, dtype=np.float64)
        self.distortion = np.asarray(distortion, dtype=np.float64).ravel()
        self.image_size = (int(image_size[0]), int(image_size[1]))
        self.reprojection_error = float(reprojection_error)

        if self.camera_matrix.shape != (3, 3):
            raise ValueError(
                f"camera_matrix must be 3x3, got {self.camera_matrix.shape}"
            )

    @property
    def is_reliable(self) -> bool:
        """
        Whether the reprojection error is low enough to trust.

        Under one pixel is the usual acceptance threshold; above it the model
        does not describe the camera well and correction will be inaccurate.
        """
        return 0 < self.reprojection_error < 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'camera_matrix': self.camera_matrix.tolist(),
            'distortion': self.distortion.tolist(),
            'image_size': list(self.image_size),
            'reprojection_error': self.reprojection_error,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CameraCalibration':
        return cls(
            camera_matrix=np.array(data['camera_matrix']),
            distortion=np.array(data['distortion']),
            image_size=tuple(data['image_size']),
            reprojection_error=data.get('reprojection_error', 0.0),
        )

    def __repr__(self) -> str:
        return (
            f"CameraCalibration(size={self.image_size[0]}x{self.image_size[1]}, "
            f"error={self.reprojection_error:.3f}px)"
        )


def calibrate_from_chessboard(
    images: Sequence[np.ndarray],
    pattern_size: Tuple[int, int] = (9, 6),
    square_size: float = 1.0,
) -> CameraCalibration:
    """
    Derive a camera model from chessboard photographs.

    Args:
        images: Photographs of the chessboard from varied angles. A dozen or
                more, covering the frame corners as well as the centre, gives a
                usable model - distortion is strongest at the edges, so a set
                shot only in the middle constrains it poorly.
        pattern_size: Interior corner counts (columns, rows) - one less than
                      the number of squares in each direction
        square_size: Physical square edge length. Its unit becomes the unit of
                     the translation vectors; leave at 1 if only undistorting.

    Returns:
        The calibration, including its reprojection error

    Raises:
        ValueError: If the chessboard was not found in at least three images

    Example:
        >>> calibration = calibrate_from_chessboard(board_shots, (9, 6))
        >>> calibration.is_reliable
        True
    """
    if images is None or len(images) == 0:
        raise ValueError("No calibration images provided")
    if len(pattern_size) != 2 or pattern_size[0] < 2 or pattern_size[1] < 2:
        raise ValueError(f"pattern_size must be two counts of at least 2, got {pattern_size}")
    if square_size <= 0:
        raise ValueError(f"square_size must be positive, got {square_size}")

    # The chessboard's corners in its own coordinate frame, z = 0
    object_template = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
    object_template[:, :2] = np.mgrid[
        0:pattern_size[0], 0:pattern_size[1]
    ].T.reshape(-1, 2) * square_size

    object_points: List[np.ndarray] = []
    image_points: List[np.ndarray] = []
    image_size: Optional[Tuple[int, int]] = None

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    for frame in images:
        img = frame.astype(np.uint8) if frame.dtype != np.uint8 else frame
        gray = cv2.cvtColor(img[:, :, :3], cv2.COLOR_RGB2GRAY) if img.ndim == 3 else img

        if image_size is None:
            image_size = (gray.shape[1], gray.shape[0])

        found, corners = cv2.findChessboardCorners(gray, pattern_size, None)
        if not found:
            continue

        # Refine to sub-pixel accuracy; whole-pixel corners give a visibly
        # worse model
        refined = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        object_points.append(object_template)
        image_points.append(refined)

    if len(object_points) < 3:
        raise ValueError(
            f"Found the chessboard in only {len(object_points)} of {len(images)} "
            f"images; at least 3 are needed, and 10 or more is recommended"
        )

    error, camera_matrix, distortion, _, _ = cv2.calibrateCamera(
        object_points, image_points, image_size, None, None
    )

    return CameraCalibration(camera_matrix, distortion, image_size, error)


def undistort(
    image: np.ndarray,
    calibration: CameraCalibration,
    alpha: float = 0.0,
    crop: bool = True,
) -> np.ndarray:
    """
    Remove lens distortion using a calibration.

    Args:
        image: Input image
        calibration: Model from ``calibrate_from_chessboard`` or a file
        alpha: 0 keeps only pixels valid in the corrected image; 1 keeps every
               original pixel and leaves blank wedges at the edges. Values
               between trade one against the other.
        crop: With alpha above 0, trim to the valid region

    Returns:
        Corrected image

    Example:
        >>> straight = undistort(frame, calibration)
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if not 0 <= alpha <= 1:
        raise ValueError(f"alpha must be between 0 and 1, got {alpha}")

    height, width = image.shape[:2]
    size = (width, height)

    camera_matrix = calibration.camera_matrix
    if (width, height) != calibration.image_size:
        # Rescale the intrinsics so a calibration made at one resolution still
        # applies to footage at another
        scale_x = width / calibration.image_size[0]
        scale_y = height / calibration.image_size[1]
        camera_matrix = camera_matrix.copy()
        camera_matrix[0, 0] *= scale_x
        camera_matrix[0, 2] *= scale_x
        camera_matrix[1, 1] *= scale_y
        camera_matrix[1, 2] *= scale_y

    new_matrix, roi = cv2.getOptimalNewCameraMatrix(
        camera_matrix, calibration.distortion, size, alpha, size
    )

    corrected = cv2.undistort(
        image, camera_matrix, calibration.distortion, None, new_matrix
    )

    if crop and alpha > 0:
        x, y, w, h = roi
        if w > 0 and h > 0:
            corrected = corrected[y:y + h, x:x + w]

    return corrected


def save_calibration(calibration: CameraCalibration, path: Union[str, Path]) -> None:
    """
    Write a calibration to JSON.

    Args:
        calibration: The model to store
        path: Destination file
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'w', encoding='utf-8') as handle:
        json.dump(calibration.to_dict(), handle, indent=2)


def load_calibration(path: Union[str, Path]) -> CameraCalibration:
    """
    Read a calibration from JSON.

    Args:
        path: Source file

    Returns:
        The stored calibration
    """
    with open(path, 'r', encoding='utf-8') as handle:
        return CameraCalibration.from_dict(json.load(handle))


def undistort_with_file(
    image: np.ndarray,
    calibration_path: str,
    alpha: float = 0.0,
    crop: bool = True,
) -> np.ndarray:
    """
    Undistort using a calibration stored on disk.

    The chain-friendly form, since a file path survives a JSON preset while a
    calibration object does not.

    Args:
        image: Input image
        calibration_path: Path to a JSON calibration
        alpha: Valid-pixel trade-off, 0 to 1
        crop: Trim to the valid region when alpha is above 0

    Returns:
        Corrected image

    Raises:
        ValueError: If no calibration path was given
        FileNotFoundError: If the path does not exist
    """
    # A blank field in a generated form arrives here as None, and passing that
    # to open() raises a TypeError about os.PathLike that says nothing about
    # what the user actually has to do
    if not calibration_path:
        raise ValueError(
            "undistort needs a calibration file. Produce one with "
            "calibrate_from_chessboard() over photos of a chessboard taken "
            "on this camera, then save it with save_calibration().")

    return undistort(image, load_calibration(calibration_path), alpha=alpha, crop=crop)
