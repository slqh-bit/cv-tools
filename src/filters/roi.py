"""
ROI Tool - Region of Interest selection, extraction, and analysis.

Inspired by Amped FIVE's selector tool for focusing on specific regions.
"""

from typing import Tuple, Optional, Union, List, Dict, Any
from dataclasses import dataclass
import numpy as np
import cv2


@dataclass
class ROI:
    """Represents a Region of Interest."""
    x: int
    y: int
    width: int
    height: int

    @property
    def x2(self) -> int:
        return self.x + self.width

    @property
    def y2(self) -> int:
        return self.y + self.height

    @property
    def center(self) -> Tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)

    @property
    def area(self) -> int:
        return self.width * self.height

    @property
    def bbox(self) -> Tuple[int, int, int, int]:
        """Return (x, y, x2, y2)."""
        return (self.x, self.y, self.x2, self.y2)

    @property
    def xywh(self) -> Tuple[int, int, int, int]:
        """Return (x, y, width, height)."""
        return (self.x, self.y, self.width, self.height)

    def __repr__(self) -> str:
        return f"ROI(x={self.x}, y={self.y}, w={self.width}, h={self.height})"

    def to_dict(self) -> Dict[str, int]:
        return {'x': self.x, 'y': self.y, 'width': self.width, 'height': self.height}

    @classmethod
    def from_dict(cls, d: Dict[str, int]) -> 'ROI':
        return cls(d['x'], d['y'], d['width'], d['height'])

    @classmethod
    def from_xyxy(cls, x1: int, y1: int, x2: int, y2: int) -> 'ROI':
        """Create ROI from two corner points."""
        return cls(x1, y1, x2 - x1, y2 - y1)

    def is_valid(self, image_shape: Tuple[int, ...]) -> bool:
        """Check if ROI is within image bounds."""
        h, w = image_shape[:2]
        return (0 <= self.x < w and 0 <= self.y < h and
                self.x2 <= w and self.y2 <= h and
                self.width > 0 and self.height > 0)

    def clip(self, image_shape: Tuple[int, ...]) -> 'ROI':
        """Clip ROI to image boundaries."""
        h, w = image_shape[:2]
        x1 = max(0, self.x)
        y1 = max(0, self.y)
        x2 = min(w, self.x2)
        y2 = min(h, self.y2)
        return ROI.from_xyxy(x1, y1, x2, y2)


def extract_roi(image: np.ndarray, roi: ROI) -> np.ndarray:
    """
    Extract a region of interest from an image.

    Args:
        image: Source image
        roi: Region of Interest

    Returns:
        Cropped image region
    """
    roi = roi.clip(image.shape)
    return image[roi.y:roi.y2, roi.x:roi.x2].copy()


def apply_to_roi(
    image: np.ndarray,
    roi: ROI,
    filter_fn,
    *args,
    **kwargs
) -> np.ndarray:
    """
    Apply a filter function only to the ROI region, leaving the rest unchanged.

    Args:
        image: Source image
        roi: Region to process
        filter_fn: Function that takes (image, *args, **kwargs) and returns processed image
        *args, **kwargs: Arguments passed to filter_fn

    Returns:
        Image with filter applied only within ROI
    """
    roi = roi.clip(image.shape)
    region = extract_roi(image, roi)
    processed_region = filter_fn(region, *args, **kwargs)

    result = image.copy()
    result[roi.y:roi.y2, roi.x:roi.x2] = processed_region
    return result


def draw_roi(
    image: np.ndarray,
    roi: ROI,
    color: Tuple[int, int, int] = (255, 0, 0),
    thickness: int = 2,
    label: Optional[str] = None,
    filled: bool = False,
    alpha: float = 0.3,
) -> np.ndarray:
    """
    Draw a rectangle showing the ROI on the image.

    Args:
        image: Source image
        roi: Region to highlight
        color: RGB tuple for rectangle color
        thickness: Border thickness (use -1 for filled)
        label: Optional text label
        filled: If True, draw semi-transparent fill
        alpha: Transparency for filled overlay

    Returns:
        Image with ROI drawn
    """
    result = image.copy()
    roi = roi.clip(image.shape)

    if filled:
        overlay = result.copy()
        cv2.rectangle(overlay, (roi.x, roi.y), (roi.x2, roi.y2), color, -1)
        result = cv2.addWeighted(overlay, alpha, result, 1 - alpha, 0)
        cv2.rectangle(result, (roi.x, roi.y), (roi.x2, roi.y2), color, thickness)
    else:
        cv2.rectangle(result, (roi.x, roi.y), (roi.x2, roi.y2), color, thickness)

    if label:
        text_y = roi.y - 5 if roi.y > 20 else roi.y2 + 20
        cv2.putText(result, label, (roi.x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    return result


def analyze_roi(image: np.ndarray, roi: ROI) -> Dict[str, Any]:
    """
    Analyze statistics within an ROI.

    Returns:
        Dictionary with mean, std, min, max, histogram info
    """
    region = extract_roi(image, roi)

    if region.ndim == 3:
        # Per-channel stats
        means = [float(region[:, :, c].mean()) for c in range(region.shape[2])]
        stds = [float(region[:, :, c].std()) for c in range(region.shape[2])]
        mins = [int(region[:, :, c].min()) for c in range(region.shape[2])]
        maxs = [int(region[:, :, c].max()) for c in range(region.shape[2])]
        channel_names = ['R', 'G', 'B'] if region.shape[2] >= 3 else [f'Ch{i}' for i in range(region.shape[2])]
    else:
        means = [float(region.mean())]
        stds = [float(region.std())]
        mins = [int(region.min())]
        maxs = [int(region.max())]
        channel_names = ['Gray']

    return {
        'roi': roi.to_dict(),
        'shape': region.shape,
        'pixels': int(region.size),
        'channels': {
            name: {
                'mean': m,
                'std': s,
                'min': mn,
                'max': mx,
            }
            for name, m, s, mn, mx in zip(channel_names, means, stds, mins, maxs)
        },
    }


def get_centered_roi(
    image_shape: Tuple[int, ...],
    width: int,
    height: int,
) -> ROI:
    """Create an ROI centered in the image."""
    h, w = image_shape[:2]
    x = max(0, (w - width) // 2)
    y = max(0, (h - height) // 2)
    # Adjust if ROI exceeds image bounds
    width = min(width, w)
    height = min(height, h)
    return ROI(x, y, width, height)


def roi_from_ratio(
    image_shape: Tuple[int, ...],
    x_ratio: float,
    y_ratio: float,
    w_ratio: float,
    h_ratio: float,
) -> ROI:
    """Create ROI from normalized ratios (0-1)."""
    h, w = image_shape[:2]
    x = int(x_ratio * w)
    y = int(y_ratio * h)
    width = int(w_ratio * w)
    height = int(h_ratio * h)
    return ROI(x, y, width, height).clip(image_shape)
