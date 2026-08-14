"""
FFT Analysis - Frequency domain inspection and filtering.

The magnitude spectrum makes periodic structure visible: interlacing, halftone
screens, scanner banding and compression grids all appear as discrete bright
points away from the centre. Those points can then be notched out and the image
transformed back, removing the pattern with far less damage than a blur.

Convention used throughout: spectra are centred (DC at the middle), and
"radius" is measured in pixels from that centre.
"""

from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np


def _to_gray_float(image: np.ndarray) -> np.ndarray:
    """Reduce any supported input to a float32 single-channel image."""
    img = image.astype(np.uint8) if image.dtype not in (np.uint8, np.float32, np.float64) else image

    if img.ndim == 3:
        if img.shape[2] == 1:
            img = img[:, :, 0]
        elif img.shape[2] == 4:
            img = cv2.cvtColor(img[:, :, :3].astype(np.uint8), cv2.COLOR_RGB2GRAY)
        else:
            img = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_RGB2GRAY)

    return img.astype(np.float32)


def fft_magnitude_spectrum(
    image: np.ndarray,
    log_scale: bool = True,
    normalize: bool = True,
) -> np.ndarray:
    """
    Compute the centred magnitude spectrum.

    Args:
        image: Input image (color is converted to luminance first)
        log_scale: Plot log(1 + magnitude). Without it the DC term dwarfs
                   everything else and the result looks like a single dot.
        normalize: Stretch the output to fill 0-255

    Returns:
        Spectrum as single-channel uint8, DC at the centre

    Example:
        >>> spectrum = fft_magnitude_spectrum(scanned_page)
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")

    gray = _to_gray_float(image)
    spectrum = np.fft.fftshift(np.fft.fft2(gray))
    magnitude = np.abs(spectrum)

    if log_scale:
        magnitude = np.log1p(magnitude)

    if normalize:
        peak = magnitude.max()
        if peak > 0:
            magnitude = magnitude * (255.0 / peak)

    return np.clip(magnitude, 0, 255).astype(np.uint8)


def _radius_grid(shape: Tuple[int, int]) -> np.ndarray:
    """Distance in pixels from the centre of a centred spectrum."""
    h, w = shape
    cy, cx = h / 2.0, w / 2.0
    yy, xx = np.ogrid[0:h, 0:w]
    return np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)


def fft_filter(
    image: np.ndarray,
    filter_type: str = 'lowpass',
    cutoff: float = 30.0,
    cutoff_high: float = 0.0,
    soft: bool = True,
) -> np.ndarray:
    """
    Filter an image in the frequency domain.

    Args:
        image: Input image (converted to luminance)
        filter_type: 'lowpass' (keep detail below cutoff), 'highpass' (keep
                     detail above it), or 'bandpass' (keep between cutoff and
                     cutoff_high)
        cutoff: Radius in pixels from DC
        cutoff_high: Upper radius, bandpass only
        soft: Use a Gaussian-edged mask. A hard-edged mask causes ringing
              artefacts (Gibbs phenomenon) that look like real image content.

    Returns:
        Filtered image as single-channel uint8
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if cutoff <= 0:
        raise ValueError(f"cutoff must be positive, got {cutoff}")
    if filter_type == 'bandpass' and cutoff_high <= cutoff:
        raise ValueError(
            f"cutoff_high ({cutoff_high}) must exceed cutoff ({cutoff}) for a bandpass"
        )

    gray = _to_gray_float(image)
    spectrum = np.fft.fftshift(np.fft.fft2(gray))
    radius = _radius_grid(gray.shape)

    if soft:
        low = np.exp(-(radius ** 2) / (2.0 * cutoff ** 2))
    else:
        low = (radius <= cutoff).astype(np.float32)

    if filter_type == 'lowpass':
        mask = low
    elif filter_type == 'highpass':
        mask = 1.0 - low
    elif filter_type == 'bandpass':
        if soft:
            high = np.exp(-(radius ** 2) / (2.0 * cutoff_high ** 2))
        else:
            high = (radius <= cutoff_high).astype(np.float32)
        mask = high - low
    else:
        raise ValueError(f"Unknown filter_type: {filter_type}")

    filtered = np.fft.ifft2(np.fft.ifftshift(spectrum * mask))
    result = np.real(filtered)

    # A highpass or bandpass result is centred on zero, so shift it into range
    if filter_type in ('highpass', 'bandpass'):
        result = result - result.min()
        peak = result.max()
        if peak > 0:
            result = result * (255.0 / peak)

    return np.clip(result, 0, 255).astype(np.uint8)


def detect_periodic_peaks(
    image: np.ndarray,
    min_radius: float = 10.0,
    threshold: float = 4.0,
    max_peaks: int = 20,
) -> List[Dict[str, Any]]:
    """
    Find isolated bright points in the spectrum, which indicate a periodic
    pattern overlaid on the image.

    Args:
        image: Input image
        min_radius: Ignore everything within this radius of DC - the low
                    frequencies belong to the image itself
        threshold: How many standard deviations above the local mean a point
                   must sit to count
        max_peaks: Cap on the number returned, strongest first

    Returns:
        List of dicts with the peak's x, y, radius from centre, and z-score

    Example:
        >>> peaks = detect_periodic_peaks(scanned_page)
        >>> cleaned = remove_periodic_noise(scanned_page, peaks=peaks)
    """
    if min_radius < 0:
        raise ValueError(f"min_radius must be non-negative, got {min_radius}")

    gray = _to_gray_float(image)
    spectrum = np.fft.fftshift(np.fft.fft2(gray))
    magnitude = np.log1p(np.abs(spectrum))

    radius = _radius_grid(gray.shape)
    searchable = radius >= min_radius
    if not searchable.any():
        return []

    # Compare each point against its neighbourhood rather than the whole
    # spectrum, whose magnitude falls off steeply with radius
    background = cv2.GaussianBlur(magnitude, (0, 0), sigmaX=8, sigmaY=8)
    residual = magnitude - background

    values = residual[searchable]
    mean, std = float(values.mean()), float(values.std())
    if std <= 0:
        return []

    # Held in float32 throughout: cv2.dilate works in float32, and comparing a
    # float64 array against its float32 dilation can round the neighbourhood
    # maximum above the peak's own value, rejecting the very peak we want.
    z_scores = np.where(searchable, (residual - mean) / std, 0.0).astype(np.float32)

    # Keep only local maxima so one broad peak is not reported many times
    dilated = cv2.dilate(z_scores, np.ones((5, 5), np.uint8))
    is_peak = (z_scores >= dilated) & (z_scores >= threshold)

    ys, xs = np.nonzero(is_peak)
    peaks = [
        {
            'x': int(x),
            'y': int(y),
            'radius': float(radius[y, x]),
            'z_score': float(z_scores[y, x]),
        }
        for y, x in zip(ys, xs)
    ]
    peaks.sort(key=lambda peak: peak['z_score'], reverse=True)
    return peaks[:max_peaks]


def remove_periodic_noise(
    image: np.ndarray,
    peaks: Optional[List[Dict[str, Any]]] = None,
    notch_radius: float = 4.0,
    min_radius: float = 10.0,
    threshold: float = 4.0,
) -> np.ndarray:
    """
    Suppress a periodic pattern by notching its spectral peaks out.

    Args:
        image: Input image
        peaks: Peaks from ``detect_periodic_peaks``. If None, they are detected
               automatically.
        notch_radius: Radius of the Gaussian notch placed on each peak
        min_radius: Passed to detection when peaks is None
        threshold: Passed to detection when peaks is None

    Returns:
        Cleaned image as single-channel uint8. Returns the luminance unchanged
        when no peaks are found.
    """
    if notch_radius <= 0:
        raise ValueError(f"notch_radius must be positive, got {notch_radius}")

    gray = _to_gray_float(image)

    if peaks is None:
        peaks = detect_periodic_peaks(image, min_radius=min_radius, threshold=threshold)

    if not peaks:
        return np.clip(gray, 0, 255).astype(np.uint8)

    spectrum = np.fft.fftshift(np.fft.fft2(gray))
    h, w = gray.shape
    yy, xx = np.ogrid[0:h, 0:w]

    mask = np.ones((h, w), dtype=np.float32)
    for peak in peaks:
        distance_sq = (yy - peak['y']) ** 2 + (xx - peak['x']) ** 2
        mask *= 1.0 - np.exp(-distance_sq / (2.0 * notch_radius ** 2))
        # The spectrum of a real image is symmetric about DC, so the mirrored
        # peak has to go too
        mirror_y, mirror_x = h - 1 - peak['y'], w - 1 - peak['x']
        distance_sq = (yy - mirror_y) ** 2 + (xx - mirror_x) ** 2
        mask *= 1.0 - np.exp(-distance_sq / (2.0 * notch_radius ** 2))

    cleaned = np.real(np.fft.ifft2(np.fft.ifftshift(spectrum * mask)))
    return np.clip(cleaned, 0, 255).astype(np.uint8)
