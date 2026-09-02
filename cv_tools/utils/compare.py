"""
Side-by-side comparison rendering (Amped FIVE's original-vs-processed view).
"""

from typing import Optional, Tuple

import cv2
import numpy as np


def _to_rgb(image: np.ndarray) -> np.ndarray:
    """Normalize grayscale / RGBA input to 3-channel uint8 RGB."""
    img = image
    if img.dtype != np.uint8:
        img = np.clip(img, 0, 255).astype(np.uint8) if img.max() > 1.0 else (img * 255).astype(np.uint8)
    if img.ndim == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    if img.shape[2] == 1:
        return cv2.cvtColor(img[:, :, 0], cv2.COLOR_GRAY2RGB)
    if img.shape[2] == 4:
        return img[:, :, :3]
    return img


def side_by_side(
    original: np.ndarray,
    processed: np.ndarray,
    label_left: Optional[str] = "ORIGINAL",
    label_right: Optional[str] = "PROCESSED",
    gap: int = 8,
    background: Tuple[int, int, int] = (0, 0, 0),
) -> np.ndarray:
    """
    Compose two images side by side, vertically centered on a common canvas.

    Images of different sizes are allowed - the canvas is sized to fit both,
    which matters after a crop or resize step.

    Args:
        original: Left-hand image
        processed: Right-hand image
        label_left: Caption drawn on the left image (None to omit)
        label_right: Caption drawn on the right image (None to omit)
        gap: Pixel gap between the two panels
        background: RGB fill color for the canvas

    Returns:
        Composite RGB image
    """
    left = _to_rgb(original)
    right = _to_rgb(processed)

    h_left, w_left = left.shape[:2]
    h_right, w_right = right.shape[:2]

    canvas_h = max(h_left, h_right)
    canvas_w = w_left + gap + w_right

    canvas = np.full((canvas_h, canvas_w, 3), background, dtype=np.uint8)

    y_left = (canvas_h - h_left) // 2
    y_right = (canvas_h - h_right) // 2
    canvas[y_left:y_left + h_left, 0:w_left] = left
    canvas[y_right:y_right + h_right, w_left + gap:w_left + gap + w_right] = right

    for label, x_offset, panel_w in ((label_left, 0, w_left), (label_right, w_left + gap, w_right)):
        if not label:
            continue
        scale = max(0.4, min(1.0, panel_w / 800.0))
        thickness = max(1, int(scale * 2))
        (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, scale, thickness)
        x = x_offset + 10
        y = text_h + 10
        # Dark plate behind the text so it stays readable on bright images
        cv2.rectangle(canvas, (x - 5, y - text_h - 5), (x + text_w + 5, y + 5), (0, 0, 0), -1)
        cv2.putText(canvas, label, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                    scale, (255, 255, 255), thickness, cv2.LINE_AA)

    return canvas
