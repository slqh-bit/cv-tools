"""
Non-Local Means Denoising.

Where a bilateral filter averages a pixel with its near neighbours, non-local
means searches a wider window for patches that *look like* the one around the
pixel, wherever they sit, and averages those. Repeating texture therefore
reinforces itself instead of being smoothed away, which preserves detail the
local filters flatten.

The cost is speed: it is by far the slowest denoiser here, and the search
window drives that cost quadratically.

Set ``h`` from the noise actually present rather than by taste - ``estimate_h``
measures it. Too high and fine detail dissolves into plastic-looking patches;
too low and the noise survives.
"""

from typing import Optional, Sequence, Tuple

import cv2
import numpy as np

from .noise_analysis import estimate_noise


def _split_alpha(image: np.ndarray) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """Separate an alpha channel so it is not denoised."""
    if image.ndim == 3 and image.shape[2] == 4:
        return image[:, :, :3], image[:, :, 3:4]
    return image, None


def estimate_h(image: np.ndarray, aggressiveness: float = 1.0) -> float:
    """
    Suggest a filter strength from the image's measured noise level.

    Args:
        image: Input image
        aggressiveness: Multiplier on the measured sigma. Around 1 preserves
                        detail; above 1.5 starts flattening texture.

    Returns:
        A value suitable for the ``h`` parameter

    Example:
        >>> clean = nl_means_denoise(frame, h=estimate_h(frame))
    """
    if aggressiveness <= 0:
        raise ValueError(f"aggressiveness must be positive, got {aggressiveness}")

    sigma = estimate_noise(image)
    # Roughly 3x sigma is the usual working strength for this filter
    return float(max(1.0, sigma * 3.0 * aggressiveness))


def nl_means_denoise(
    image: np.ndarray,
    h: float = 10.0,
    h_color: Optional[float] = None,
    template_window: int = 7,
    search_window: int = 21,
) -> np.ndarray:
    """
    Denoise with non-local means.

    Args:
        image: Input image (RGB, RGBA, or grayscale)
        h: Filter strength for luminance. Higher removes more noise and more
           detail with it.
        h_color: Strength for the colour channels; defaults to ``h``. Colour
                 noise can usually take a higher value than luminance, since
                 chroma detail is coarser.
        template_window: Odd size of the patch being compared
        search_window: Odd size of the region searched for similar patches.
                       Cost grows with its square.

    Returns:
        Denoised image, alpha preserved

    Example:
        >>> clean = nl_means_denoise(noisy_frame, h=12)
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if h <= 0:
        raise ValueError(f"h must be positive, got {h}")
    if template_window % 2 == 0 or template_window < 3:
        raise ValueError(f"template_window must be an odd number >= 3, got {template_window}")
    if search_window % 2 == 0 or search_window < 3:
        raise ValueError(f"search_window must be an odd number >= 3, got {search_window}")
    if search_window < template_window:
        raise ValueError(
            f"search_window ({search_window}) must be at least "
            f"template_window ({template_window})"
        )

    img = image.astype(np.uint8) if image.dtype != np.uint8 else image

    if img.ndim == 2 or (img.ndim == 3 and img.shape[2] == 1):
        gray = img[:, :, 0] if img.ndim == 3 else img
        return cv2.fastNlMeansDenoising(
            gray, None, float(h), template_window, search_window
        )

    rgb, alpha = _split_alpha(img)
    result = cv2.fastNlMeansDenoisingColored(
        rgb, None, float(h), float(h_color if h_color is not None else h),
        template_window, search_window,
    )

    if alpha is not None:
        result = np.concatenate([result, alpha], axis=2)
    return result


def nl_means_denoise_auto(
    image: np.ndarray,
    aggressiveness: float = 1.0,
    template_window: int = 7,
    search_window: int = 21,
) -> np.ndarray:
    """
    Denoise with the strength chosen from the image's own noise level.

    Args:
        image: Input image
        aggressiveness: Multiplier on the measured noise sigma
        template_window: Odd patch size
        search_window: Odd search size

    Returns:
        Denoised image
    """
    return nl_means_denoise(
        image,
        h=estimate_h(image, aggressiveness),
        template_window=template_window,
        search_window=search_window,
    )


def nl_means_denoise_frames(
    frames: Sequence[np.ndarray],
    index: Optional[int] = None,
    h: float = 10.0,
    temporal_window: int = 3,
    template_window: int = 7,
    search_window: int = 21,
) -> np.ndarray:
    """
    Denoise one frame using its neighbours in time as extra evidence.

    Stronger than single-frame denoising because the same detail appears in
    several frames while the noise does not - and unlike plain frame averaging,
    moving objects do not smear, since patches are matched rather than summed.

    Args:
        frames: Consecutive frames, all the same size
        index: Which frame to denoise; defaults to the middle one
        h: Filter strength
        temporal_window: Odd number of frames used, centred on ``index``
        template_window: Odd patch size
        search_window: Odd search size

    Returns:
        The denoised frame

    Example:
        >>> clean = nl_means_denoise_frames(frames, index=10, h=12)
    """
    if frames is None or len(frames) == 0:
        raise ValueError("No frames provided")
    if temporal_window % 2 == 0 or temporal_window < 1:
        raise ValueError(f"temporal_window must be an odd number >= 1, got {temporal_window}")
    if len(frames) < temporal_window:
        raise ValueError(
            f"Need at least {temporal_window} frames for a temporal window of "
            f"that size, got {len(frames)}"
        )

    first_shape = frames[0].shape
    for position, frame in enumerate(frames):
        if frame.shape != first_shape:
            raise ValueError(
                f"Frame {position} has shape {frame.shape}, expected {first_shape}"
            )

    if index is None:
        index = len(frames) // 2
    if not 0 <= index < len(frames):
        raise ValueError(f"index {index} is outside the {len(frames)} frames given")

    half = temporal_window // 2
    # Slide the window inside the available range rather than failing at the ends
    start = min(max(0, index - half), len(frames) - temporal_window)
    window = [
        f.astype(np.uint8) if f.dtype != np.uint8 else f
        for f in frames[start:start + temporal_window]
    ]
    target = index - start

    is_color = window[0].ndim == 3 and window[0].shape[2] >= 3
    if is_color:
        window = [f[:, :, :3] for f in window]
        return cv2.fastNlMeansDenoisingColoredMulti(
            window, target, temporal_window, None,
            float(h), float(h), template_window, search_window,
        )

    window = [f[:, :, 0] if f.ndim == 3 else f for f in window]
    return cv2.fastNlMeansDenoisingMulti(
        window, target, temporal_window, None,
        float(h), template_window, search_window,
    )
