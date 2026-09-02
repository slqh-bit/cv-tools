"""
Comparison rendering: side-by-side panels and difference maps
(Amped FIVE's original-vs-processed views).
"""

from typing import Dict, Optional, Tuple

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


def difference_map(
    original: np.ndarray,
    processed: np.ndarray,
    amplify: Optional[float] = None,
    label: bool = True,
) -> Tuple[np.ndarray, Dict[str, float]]:
    """
    Per-channel absolute difference between the two images, scaled to be seen.

    This is how you *see* what a filter did instead of measuring it. On a night
    scene it shows at once that most of a contrast filter's action happened in
    the sky - that is, nowhere anyone wanted it - which no single noise number
    conveys. Because the difference is per channel, an operation that shifted
    colour shows up coloured, which is the tell for channelwise enhancement on
    an exhibit.

    A raw difference is almost always too dark to read, so it is scaled. That
    scaling is the catch: it makes a 2-level difference and a 200-level one
    look alike. The true peak and mean are therefore returned, and by default
    written onto the image, so a screenshot of this view cannot overstate what
    it shows.

    Images of different sizes are allowed - a crop or resize step makes them
    differ - and are padded onto a common canvas first, so everything the crop
    removed reads as changed, which it is.

    Args:
        original: Reference image
        processed: Image to compare against it
        amplify: Fixed scale factor; by default the difference is scaled so its
            peak reaches full brightness
        label: Draw the scale factor and the true peak and mean on the image

    Returns:
        (difference image as RGB uint8, stats with 'peak', 'mean', 'scale'
        and 'labelled' - 0.0 when the caption did not fit and was dropped)
    """
    left = _to_rgb(original)
    right = _to_rgb(processed)

    height = max(left.shape[0], right.shape[0])
    width = max(left.shape[1], right.shape[1])

    def padded(img: np.ndarray) -> np.ndarray:
        canvas = np.zeros((height, width, 3), dtype=np.uint8)
        canvas[:img.shape[0], :img.shape[1]] = img
        return canvas

    diff = cv2.absdiff(padded(left), padded(right))
    peak = float(diff.max())
    mean = float(diff.mean())

    if amplify is not None:
        scale = float(amplify)
    elif peak > 0:
        scale = 255.0 / peak
    else:
        scale = 1.0

    shown = np.clip(diff.astype(np.float32) * scale, 0, 255).astype(np.uint8)
    stats = {'peak': peak, 'mean': mean, 'scale': scale}

    if label:
        caption = f"DIFFERENCE  x{scale:.1f}   peak {peak:.0f}   mean {mean:.2f}"
        text_scale = max(0.4, min(1.0, width / 800.0))
        thickness = max(1, int(text_scale * 2))
        (text_w, text_h), _ = cv2.getTextSize(caption, cv2.FONT_HERSHEY_SIMPLEX,
                                              text_scale, thickness)
        # On a small frame the caption would cover the thing it is annotating,
        # so it is dropped rather than allowed to bury the picture. Callers
        # that need the numbers regardless have them in the returned stats.
        if text_w + 20 <= width and (text_h + 20) * 4 <= height:
            x, y = 10, text_h + 10
            cv2.rectangle(shown, (x - 5, y - text_h - 5), (x + text_w + 5, y + 5),
                          (0, 0, 0), -1)
            cv2.putText(shown, caption, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                        text_scale, (255, 255, 255), thickness, cv2.LINE_AA)
            stats['labelled'] = 1.0
        else:
            stats['labelled'] = 0.0
    else:
        stats['labelled'] = 0.0

    return shown, stats
