"""
Filter registry - maps filter names to callables so chains can be saved to and
restored from JSON presets.

Every registered callable has the signature ``fn(image, **params)`` where all
params are JSON-serializable, which is what ``core.pipeline.Pipeline`` records.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from .aspect_ratio import correct_pixel_aspect, fit_to_aspect
from .clahe import apply_clahe
from .contrast_brightness import adjust_contrast_brightness, auto_contrast
from .clone_detection import highlight_clones
from .color_balance import adjust_cmyk, adjust_color_balance, channel_mixer
from .color_deconvolution import extract_stain
from .component_separation import extract_bit_plane, extract_component
from .compression_analysis import blocking_map, deblock
from .crop_resize import crop, resize, rotate, flip
from .curves import apply_curve, s_curve
from .detail_enhancement import (
    enhance_detail,
    local_contrast,
    multiscale_detail,
    texture_boost,
)
from .edge_detection import auto_canny, canny_edges, laplacian_edges, sobel_edges
from .ela import error_level_analysis
from .fft_analysis import fft_filter, fft_magnitude_spectrum, remove_periodic_noise
from .fisheye_correction import correct_barrel_distortion, correct_fisheye
from .invert import invert, invert_channel, invert_luminance, solarize
from .jpeg_ghost import ghost_map
from .measure_3d import draw_height_measurement
from .motion_deblur import deblur_defocus, deblur_motion
from .nl_means_denoise import nl_means_denoise, nl_means_denoise_auto
from .noise_analysis import noise_map
from .perspective_correction import auto_correct_perspective, correct_perspective
from .redaction import redact_region
from .saturation import (
    adjust_saturation,
    adjust_vibrance,
    desaturate,
    selective_saturation,
)
from .super_resolution import upscale
from .undistort import undistort_with_file
from .white_balance import (
    adjust_temperature,
    auto_white_balance,
    white_balance_from_patch,
)
from .histogram_equalization import histogram_equalization
from .levels import adjust_levels, auto_levels
from .roi import ROI, extract_roi, draw_roi
from .sharpen import laplacian_sharpen, unsharp_mask
from .smoothing import bilateral_filter, gaussian_blur, median_filter


@dataclass(frozen=True)
class FilterSpec:
    """A named, JSON-serializable filter entry."""
    name: str
    fn: Callable[..., np.ndarray]
    module: str
    description: str
    category: str = 'Special'


# Display order for anything that groups filters by family instead of A-Z,
# e.g. the dashboard's filter picker. Matches docs/filters.md's sections.
CATEGORY_ORDER: List[str] = [
    'Adjust', 'Enhance', 'Correct', 'Analyze', 'Forensic', 'Special',
]


# ---- Adapters -------------------------------------------------------------
# ROI functions take an ROI dataclass, which is not JSON-serializable. These
# thin wrappers keep the registry's flat-params contract.

def roi_crop(image: np.ndarray, x: int, y: int, width: int, height: int) -> np.ndarray:
    """Crop to an ROI, clipped to image bounds."""
    return extract_roi(image, ROI(x, y, width, height))


def roi_draw(
    image: np.ndarray,
    x: int,
    y: int,
    width: int,
    height: int,
    color: Tuple[int, int, int] = (255, 0, 0),
    thickness: int = 2,
    label: Optional[str] = None,
    filled: bool = False,
    alpha: float = 0.3,
) -> np.ndarray:
    """Draw an ROI rectangle on the image."""
    return draw_roi(
        image,
        ROI(x, y, width, height),
        color=tuple(color),
        thickness=thickness,
        label=label,
        filled=filled,
        alpha=alpha,
    )


# ---- Registry -------------------------------------------------------------

FILTER_REGISTRY: Dict[str, FilterSpec] = {
    spec.name: spec
    for spec in [
        # ---- Adjust ----
        FilterSpec('clahe', apply_clahe, 'cv_tools.filters.clahe',
                   'Contrast Limited Adaptive Histogram Equalization', 'Adjust'),
        FilterSpec('contrast_brightness', adjust_contrast_brightness,
                   'cv_tools.filters.contrast_brightness',
                   'Linear contrast, brightness and gamma adjustment', 'Adjust'),
        FilterSpec('auto_contrast', auto_contrast, 'cv_tools.filters.contrast_brightness',
                   'Automatic histogram stretch on luminance', 'Adjust'),
        FilterSpec('levels', adjust_levels, 'cv_tools.filters.levels',
                   'Black point / gamma / white point adjustment', 'Adjust'),
        FilterSpec('auto_levels', auto_levels, 'cv_tools.filters.levels',
                   'Automatic levels stretch', 'Adjust'),
        FilterSpec('histeq', histogram_equalization, 'cv_tools.filters.histogram_equalization',
                   'Global histogram equalization', 'Adjust'),
        FilterSpec('roi_crop', roi_crop, 'cv_tools.filters.roi',
                   'Crop to a region of interest', 'Adjust'),
        FilterSpec('roi_draw', roi_draw, 'cv_tools.filters.roi',
                   'Draw a region of interest rectangle', 'Adjust'),
        FilterSpec('crop', crop, 'cv_tools.filters.crop_resize',
                   'Crop to x, y, width, height', 'Adjust'),
        FilterSpec('resize', resize, 'cv_tools.filters.crop_resize',
                   'Resize by target size or scale factor', 'Adjust'),
        FilterSpec('rotate', rotate, 'cv_tools.filters.crop_resize',
                   'Rotate by an arbitrary angle', 'Adjust'),
        FilterSpec('flip', flip, 'cv_tools.filters.crop_resize',
                   'Flip horizontally, vertically or both', 'Adjust'),
        FilterSpec('curves', apply_curve, 'cv_tools.filters.curves',
                   'Tonal curve from control points or a preset', 'Adjust'),
        FilterSpec('s_curve', s_curve, 'cv_tools.filters.curves',
                   'Symmetric S-curve contrast', 'Adjust'),
        FilterSpec('white_balance', auto_white_balance, 'cv_tools.filters.white_balance',
                   'Automatic colour cast removal', 'Adjust'),
        FilterSpec('white_balance_patch', white_balance_from_patch,
                   'cv_tools.filters.white_balance',
                   'White balance from a known neutral region', 'Adjust'),
        FilterSpec('temperature', adjust_temperature, 'cv_tools.filters.white_balance',
                   'Manual colour temperature and tint', 'Adjust'),
        FilterSpec('saturation', adjust_saturation, 'cv_tools.filters.saturation',
                   'Uniform saturation scaling', 'Adjust'),
        FilterSpec('vibrance', adjust_vibrance, 'cv_tools.filters.saturation',
                   'Saturation weighted towards muted colours', 'Adjust'),
        FilterSpec('desaturate', desaturate, 'cv_tools.filters.saturation',
                   'Grayscale conversion by a chosen rule', 'Adjust'),
        FilterSpec('selective_saturation', selective_saturation,
                   'cv_tools.filters.saturation',
                   'Saturate only colours near a target hue', 'Adjust'),
        FilterSpec('color_balance', adjust_color_balance, 'cv_tools.filters.color_balance',
                   'Per-tonal-range RGB shifts', 'Adjust'),
        FilterSpec('cmyk', adjust_cmyk, 'cv_tools.filters.color_balance',
                   'Subtractive CMYK adjustment', 'Adjust'),
        FilterSpec('channel_mixer', channel_mixer, 'cv_tools.filters.color_balance',
                   'Rebuild channels as weighted mixes', 'Adjust'),
        FilterSpec('invert', invert, 'cv_tools.filters.invert',
                   'Invert all colour channels', 'Adjust'),
        FilterSpec('invert_channel', invert_channel, 'cv_tools.filters.invert',
                   'Invert one colour channel', 'Adjust'),
        FilterSpec('invert_luminance', invert_luminance, 'cv_tools.filters.invert',
                   'Invert brightness, keeping hue', 'Adjust'),
        FilterSpec('solarize', solarize, 'cv_tools.filters.invert',
                   'Invert only values above a threshold', 'Adjust'),
        # ---- Enhance ----
        FilterSpec('sharpen', unsharp_mask, 'cv_tools.filters.sharpen',
                   'Unsharp mask sharpening', 'Enhance'),
        FilterSpec('sharpen_laplacian', laplacian_sharpen, 'cv_tools.filters.sharpen',
                   'Laplacian sharpening', 'Enhance'),
        FilterSpec('gaussian_blur', gaussian_blur, 'cv_tools.filters.smoothing',
                   'Gaussian smoothing', 'Enhance'),
        FilterSpec('median_filter', median_filter, 'cv_tools.filters.smoothing',
                   'Median filter for salt-and-pepper noise', 'Enhance'),
        FilterSpec('bilateral_filter', bilateral_filter, 'cv_tools.filters.smoothing',
                   'Edge-preserving noise reduction', 'Enhance'),
        FilterSpec('nl_means', nl_means_denoise, 'cv_tools.filters.nl_means_denoise',
                   'Non-local means denoising', 'Enhance'),
        FilterSpec('nl_means_auto', nl_means_denoise_auto,
                   'cv_tools.filters.nl_means_denoise',
                   'Non-local means with strength from measured noise', 'Enhance'),
        FilterSpec('upscale', upscale, 'cv_tools.filters.super_resolution',
                   'Single-frame interpolated enlargement', 'Enhance'),
        FilterSpec('local_contrast', local_contrast, 'cv_tools.filters.detail_enhancement',
                   'Large-radius local contrast (clarity)', 'Enhance'),
        FilterSpec('detail_enhance', enhance_detail, 'cv_tools.filters.detail_enhancement',
                   'Edge-preserving texture enhancement', 'Enhance'),
        FilterSpec('multiscale_detail', multiscale_detail,
                   'cv_tools.filters.detail_enhancement',
                   'Per-frequency-band detail boost', 'Enhance'),
        FilterSpec('texture_boost', texture_boost, 'cv_tools.filters.detail_enhancement',
                   'Texture contrast with edge protection', 'Enhance'),
        # ---- Correct ----
        FilterSpec('perspective', correct_perspective,
                   'cv_tools.filters.perspective_correction',
                   'Rectify a quadrilateral from four corners', 'Correct'),
        FilterSpec('auto_perspective', auto_correct_perspective,
                   'cv_tools.filters.perspective_correction',
                   'Detect and rectify a rectangular surface', 'Correct'),
        FilterSpec('barrel', correct_barrel_distortion,
                   'cv_tools.filters.fisheye_correction',
                   'Polynomial radial distortion correction', 'Correct'),
        FilterSpec('fisheye', correct_fisheye, 'cv_tools.filters.fisheye_correction',
                   'Equidistant fisheye correction', 'Correct'),
        FilterSpec('pixel_aspect', correct_pixel_aspect, 'cv_tools.filters.aspect_ratio',
                   'Rescale non-square pixels to square', 'Correct'),
        FilterSpec('fit_aspect', fit_to_aspect, 'cv_tools.filters.aspect_ratio',
                   'Pad, crop or stretch to a display aspect ratio', 'Correct'),
        FilterSpec('undistort', undistort_with_file, 'cv_tools.filters.undistort',
                   'Calibration-based lens correction', 'Correct'),
        # ---- Analyze ----
        FilterSpec('canny', canny_edges, 'cv_tools.filters.edge_detection',
                   'Canny edge detection', 'Analyze'),
        FilterSpec('auto_canny', auto_canny, 'cv_tools.filters.edge_detection',
                   'Canny with thresholds derived from image median', 'Analyze'),
        FilterSpec('sobel', sobel_edges, 'cv_tools.filters.edge_detection',
                   'Sobel gradient magnitude', 'Analyze'),
        FilterSpec('laplacian', laplacian_edges, 'cv_tools.filters.edge_detection',
                   'Laplacian edge map', 'Analyze'),
        FilterSpec('blocking_map', blocking_map, 'cv_tools.filters.compression_analysis',
                   'Per-region JPEG blocking map', 'Analyze'),
        FilterSpec('deblock', deblock, 'cv_tools.filters.compression_analysis',
                   'Soften JPEG block edges', 'Analyze'),
        # ---- Forensic ----
        FilterSpec('ela', error_level_analysis, 'cv_tools.filters.ela',
                   'Error Level Analysis map', 'Forensic'),
        FilterSpec('fft_spectrum', fft_magnitude_spectrum, 'cv_tools.filters.fft_analysis',
                   'FFT magnitude spectrum', 'Forensic'),
        FilterSpec('fft_filter', fft_filter, 'cv_tools.filters.fft_analysis',
                   'Frequency domain low/high/bandpass filter', 'Forensic'),
        FilterSpec('remove_periodic', remove_periodic_noise, 'cv_tools.filters.fft_analysis',
                   'Notch out periodic pattern noise', 'Forensic'),
        FilterSpec('noise_map', noise_map, 'cv_tools.filters.noise_analysis',
                   'Per-block noise level map', 'Forensic'),
        FilterSpec('clone_detect', highlight_clones, 'cv_tools.filters.clone_detection',
                   'Highlight copy-move duplicated regions', 'Forensic'),
        FilterSpec('deblur_motion', deblur_motion, 'cv_tools.filters.motion_deblur',
                   'Wiener deconvolution of linear motion blur', 'Forensic'),
        FilterSpec('deblur_defocus', deblur_defocus, 'cv_tools.filters.motion_deblur',
                   'Wiener deconvolution of defocus blur', 'Forensic'),
        FilterSpec('ghost', ghost_map, 'cv_tools.filters.jpeg_ghost',
                   'JPEG ghost map: best-match recompression quality per block',
                   'Forensic'),
        # ---- Special ----
        FilterSpec('stain', extract_stain, 'cv_tools.filters.color_deconvolution',
                   'Extract one colorant by colour deconvolution', 'Special'),
        FilterSpec('component', extract_component,
                   'cv_tools.filters.component_separation',
                   'Extract one colour-space channel', 'Special'),
        FilterSpec('bit_plane', extract_bit_plane,
                   'cv_tools.filters.component_separation',
                   'Extract one bit plane of the intensity', 'Special'),
        FilterSpec('redact', redact_region, 'cv_tools.filters.redaction',
                   'Obscure a region (fill/noise destroy, blur/pixelate do not)', 'Special'),
        FilterSpec('measure_3d', draw_height_measurement, 'cv_tools.filters.measure_3d',
                   'Estimate object height from one view, against a known reference',
                   'Special'),
    ]
}


def resolve_filter(name: str) -> FilterSpec:
    """
    Look up a filter by registry name.

    Raises:
        KeyError: If the name is not registered
    """
    try:
        return FILTER_REGISTRY[name]
    except KeyError:
        available = ', '.join(sorted(FILTER_REGISTRY))
        raise KeyError(f"Unknown filter '{name}'. Available: {available}") from None


def filter_function(name: str) -> Callable[..., np.ndarray]:
    """
    Look up just the callable for a registry name.

    This is the resolver ``core.pipeline.Pipeline.replace_chain`` expects.

    Raises:
        KeyError: If the name is not registered
    """
    return resolve_filter(name).fn


def list_filters() -> List[Tuple[str, str]]:
    """Return (name, description) pairs for every registered filter."""
    return [(spec.name, spec.description) for spec in FILTER_REGISTRY.values()]


def apply_preset(pipeline, preset: Dict[str, Any]) -> np.ndarray:
    """
    Apply every filter in a preset dict to a pipeline, in order.

    The steps are appended to whatever the pipeline has already applied. To
    discard the existing chain and rebuild from the original image instead,
    use ``Pipeline.replace_chain`` with ``filter_function`` as the resolver.

    Args:
        pipeline: A ``core.pipeline.Pipeline`` instance
        preset: Preset dict as written by ``Pipeline.save_preset``

    Returns:
        The processed image
    """
    for step in preset.get('filters', []):
        spec = resolve_filter(step['name'])
        pipeline.apply(spec.fn, spec.name, spec.module, step.get('params', {}))
    return pipeline.current
