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


# Filters whose parameters are points on the image, and the order to collect
# them in: (parameter, how many points, what to click).
#
# measure_3d is the case that needs it most - five required parameters, all
# coordinates, and single-view metrology is unforgiving about which point is
# which: a reference top confused with an object top gives a confidently wrong
# height. Naming each click removes that.
#
# Lives here rather than in a front end because both of them need it, and two
# copies would drift.
POINT_PARAMETERS: Dict[str, Tuple[Tuple[str, int, str], ...]] = {
    'measure_3d': (
        ('reference_base', 1, 'the FOOT of the reference object'),
        ('reference_top', 1, 'the TOP of the reference object'),
        ('base', 1, 'the FOOT of the object to measure'),
        ('top', 1, 'the TOP of the object to measure'),
        ('horizon', 2, 'two points on the HORIZON'),
    ),
    'perspective': (
        ('corners', 4, 'the four corners, clockwise from top-left'),
    ),
}


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
        FilterSpec('clahe', apply_clahe, 'src.filters.clahe',
                   'Contrast Limited Adaptive Histogram Equalization', 'Adjust'),
        FilterSpec('contrast_brightness', adjust_contrast_brightness,
                   'src.filters.contrast_brightness',
                   'Linear contrast, brightness and gamma adjustment', 'Adjust'),
        FilterSpec('auto_contrast', auto_contrast, 'src.filters.contrast_brightness',
                   'Automatic histogram stretch on luminance', 'Adjust'),
        FilterSpec('levels', adjust_levels, 'src.filters.levels',
                   'Black point / gamma / white point adjustment', 'Adjust'),
        FilterSpec('auto_levels', auto_levels, 'src.filters.levels',
                   'Automatic levels stretch', 'Adjust'),
        FilterSpec('histeq', histogram_equalization, 'src.filters.histogram_equalization',
                   'Global histogram equalization', 'Adjust'),
        FilterSpec('roi_crop', roi_crop, 'src.filters.roi',
                   'Crop to a region of interest', 'Adjust'),
        FilterSpec('roi_draw', roi_draw, 'src.filters.roi',
                   'Draw a region of interest rectangle', 'Adjust'),
        FilterSpec('crop', crop, 'src.filters.crop_resize',
                   'Crop to x, y, width, height', 'Adjust'),
        FilterSpec('resize', resize, 'src.filters.crop_resize',
                   'Resize by target size or scale factor', 'Adjust'),
        FilterSpec('rotate', rotate, 'src.filters.crop_resize',
                   'Rotate by an arbitrary angle', 'Adjust'),
        FilterSpec('flip', flip, 'src.filters.crop_resize',
                   'Flip horizontally, vertically or both', 'Adjust'),
        FilterSpec('curves', apply_curve, 'src.filters.curves',
                   'Tonal curve from control points or a preset', 'Adjust'),
        FilterSpec('s_curve', s_curve, 'src.filters.curves',
                   'Symmetric S-curve contrast', 'Adjust'),
        FilterSpec('white_balance', auto_white_balance, 'src.filters.white_balance',
                   'Automatic colour cast removal', 'Adjust'),
        FilterSpec('white_balance_patch', white_balance_from_patch,
                   'src.filters.white_balance',
                   'White balance from a known neutral region', 'Adjust'),
        FilterSpec('temperature', adjust_temperature, 'src.filters.white_balance',
                   'Manual colour temperature and tint', 'Adjust'),
        FilterSpec('saturation', adjust_saturation, 'src.filters.saturation',
                   'Uniform saturation scaling', 'Adjust'),
        FilterSpec('vibrance', adjust_vibrance, 'src.filters.saturation',
                   'Saturation weighted towards muted colours', 'Adjust'),
        FilterSpec('desaturate', desaturate, 'src.filters.saturation',
                   'Grayscale conversion by a chosen rule', 'Adjust'),
        FilterSpec('selective_saturation', selective_saturation,
                   'src.filters.saturation',
                   'Saturate only colours near a target hue', 'Adjust'),
        FilterSpec('color_balance', adjust_color_balance, 'src.filters.color_balance',
                   'Per-tonal-range RGB shifts', 'Adjust'),
        FilterSpec('cmyk', adjust_cmyk, 'src.filters.color_balance',
                   'Subtractive CMYK adjustment', 'Adjust'),
        FilterSpec('channel_mixer', channel_mixer, 'src.filters.color_balance',
                   'Rebuild channels as weighted mixes', 'Adjust'),
        FilterSpec('invert', invert, 'src.filters.invert',
                   'Invert all colour channels', 'Adjust'),
        FilterSpec('invert_channel', invert_channel, 'src.filters.invert',
                   'Invert one colour channel', 'Adjust'),
        FilterSpec('invert_luminance', invert_luminance, 'src.filters.invert',
                   'Invert brightness, keeping hue', 'Adjust'),
        FilterSpec('solarize', solarize, 'src.filters.invert',
                   'Invert only values above a threshold', 'Adjust'),
        # ---- Enhance ----
        FilterSpec('sharpen', unsharp_mask, 'src.filters.sharpen',
                   'Unsharp mask sharpening', 'Enhance'),
        FilterSpec('sharpen_laplacian', laplacian_sharpen, 'src.filters.sharpen',
                   'Laplacian sharpening', 'Enhance'),
        FilterSpec('gaussian_blur', gaussian_blur, 'src.filters.smoothing',
                   'Gaussian smoothing', 'Enhance'),
        FilterSpec('median_filter', median_filter, 'src.filters.smoothing',
                   'Median filter for salt-and-pepper noise', 'Enhance'),
        FilterSpec('bilateral_filter', bilateral_filter, 'src.filters.smoothing',
                   'Edge-preserving noise reduction', 'Enhance'),
        FilterSpec('nl_means', nl_means_denoise, 'src.filters.nl_means_denoise',
                   'Non-local means denoising', 'Enhance'),
        FilterSpec('nl_means_auto', nl_means_denoise_auto,
                   'src.filters.nl_means_denoise',
                   'Non-local means with strength from measured noise', 'Enhance'),
        FilterSpec('upscale', upscale, 'src.filters.super_resolution',
                   'Single-frame interpolated enlargement', 'Enhance'),
        FilterSpec('local_contrast', local_contrast, 'src.filters.detail_enhancement',
                   'Large-radius local contrast (clarity)', 'Enhance'),
        FilterSpec('detail_enhance', enhance_detail, 'src.filters.detail_enhancement',
                   'Edge-preserving texture enhancement', 'Enhance'),
        FilterSpec('multiscale_detail', multiscale_detail,
                   'src.filters.detail_enhancement',
                   'Per-frequency-band detail boost', 'Enhance'),
        FilterSpec('texture_boost', texture_boost, 'src.filters.detail_enhancement',
                   'Texture contrast with edge protection', 'Enhance'),
        # ---- Correct ----
        FilterSpec('perspective', correct_perspective,
                   'src.filters.perspective_correction',
                   'Rectify a quadrilateral from four corners', 'Correct'),
        FilterSpec('auto_perspective', auto_correct_perspective,
                   'src.filters.perspective_correction',
                   'Detect and rectify a rectangular surface', 'Correct'),
        FilterSpec('barrel', correct_barrel_distortion,
                   'src.filters.fisheye_correction',
                   'Polynomial radial distortion correction', 'Correct'),
        FilterSpec('fisheye', correct_fisheye, 'src.filters.fisheye_correction',
                   'Equidistant fisheye correction', 'Correct'),
        FilterSpec('pixel_aspect', correct_pixel_aspect, 'src.filters.aspect_ratio',
                   'Rescale non-square pixels to square', 'Correct'),
        FilterSpec('fit_aspect', fit_to_aspect, 'src.filters.aspect_ratio',
                   'Pad, crop or stretch to a display aspect ratio', 'Correct'),
        FilterSpec('undistort', undistort_with_file, 'src.filters.undistort',
                   'Calibration-based lens correction', 'Correct'),
        # ---- Analyze ----
        FilterSpec('canny', canny_edges, 'src.filters.edge_detection',
                   'Canny edge detection', 'Analyze'),
        FilterSpec('auto_canny', auto_canny, 'src.filters.edge_detection',
                   'Canny with thresholds derived from image median', 'Analyze'),
        FilterSpec('sobel', sobel_edges, 'src.filters.edge_detection',
                   'Sobel gradient magnitude', 'Analyze'),
        FilterSpec('laplacian', laplacian_edges, 'src.filters.edge_detection',
                   'Laplacian edge map', 'Analyze'),
        FilterSpec('blocking_map', blocking_map, 'src.filters.compression_analysis',
                   'Per-region JPEG blocking map', 'Analyze'),
        FilterSpec('deblock', deblock, 'src.filters.compression_analysis',
                   'Soften JPEG block edges', 'Analyze'),
        # ---- Forensic ----
        FilterSpec('ela', error_level_analysis, 'src.filters.ela',
                   'Error Level Analysis map', 'Forensic'),
        FilterSpec('fft_spectrum', fft_magnitude_spectrum, 'src.filters.fft_analysis',
                   'FFT magnitude spectrum', 'Forensic'),
        FilterSpec('fft_filter', fft_filter, 'src.filters.fft_analysis',
                   'Frequency domain low/high/bandpass filter', 'Forensic'),
        FilterSpec('remove_periodic', remove_periodic_noise, 'src.filters.fft_analysis',
                   'Notch out periodic pattern noise', 'Forensic'),
        FilterSpec('noise_map', noise_map, 'src.filters.noise_analysis',
                   'Per-block noise level map', 'Forensic'),
        FilterSpec('clone_detect', highlight_clones, 'src.filters.clone_detection',
                   'Highlight copy-move duplicated regions', 'Forensic'),
        FilterSpec('deblur_motion', deblur_motion, 'src.filters.motion_deblur',
                   'Wiener deconvolution of linear motion blur', 'Forensic'),
        FilterSpec('deblur_defocus', deblur_defocus, 'src.filters.motion_deblur',
                   'Wiener deconvolution of defocus blur', 'Forensic'),
        FilterSpec('ghost', ghost_map, 'src.filters.jpeg_ghost',
                   'JPEG ghost: the recompression sweep frame with the most '
                   'structure, dark where the pixels match that quality',
                   'Forensic'),
        # ---- Special ----
        FilterSpec('stain', extract_stain, 'src.filters.color_deconvolution',
                   'Extract one colorant by colour deconvolution', 'Special'),
        FilterSpec('component', extract_component,
                   'src.filters.component_separation',
                   'Extract one colour-space channel', 'Special'),
        FilterSpec('bit_plane', extract_bit_plane,
                   'src.filters.component_separation',
                   'Extract one bit plane of the intensity', 'Special'),
        FilterSpec('redact', redact_region, 'src.filters.redaction',
                   'Obscure a region (fill/noise destroy, blur/pixelate do not)', 'Special'),
        FilterSpec('measure_3d', draw_height_measurement, 'src.filters.measure_3d',
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
