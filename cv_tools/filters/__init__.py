"""
Image processing filters, grouped by function.

Sprint 1: Adjust (CLAHE, levels, contrast/brightness, histogram equalization)
and Correct (crop, resize, rotate, flip) plus the ROI analysis tool.

Sprint 2: Enhance (sharpen, gaussian/median/bilateral smoothing) and Analyze
(edge detection, histogram display).

Sprint 3: Forensic (ELA, FFT analysis, noise analysis, clone detection) and
Special (Wiener deblurring, multi-frame integration).

The remainder of the plan's catalogue: curves, white balance, saturation,
colour balance and inversion; non-local means denoising, super-resolution and
detail enhancement; perspective, fisheye, aspect-ratio and calibration-based
geometric correction; compression analysis; colour deconvolution, component
separation, redaction and annotation.
"""

from .annotate import (
    Scale,
    draw_arrow,
    draw_text,
    draw_shape,
    draw_measurement,
    draw_scale_bar,
    measure_distance,
    measure_area,
    scale_from_reference,
)
from .aspect_ratio import (
    PIXEL_ASPECT_RATIOS,
    correct_pixel_aspect,
    correct_pixel_aspect_named,
    fit_to_aspect,
    describe_aspect,
)
from .clahe import apply_clahe, apply_clahe_grid
from .clone_detection import detect_copy_move, draw_clone_regions, highlight_clones
from .color_balance import adjust_color_balance, adjust_cmyk, channel_mixer
from .color_deconvolution import (
    STAIN_PRESETS,
    deconvolve_colors,
    extract_stain,
    estimate_stain_vector,
    normalize_vectors,
)
from .component_separation import (
    COLOR_SPACES,
    separate_channels,
    extract_component,
    separate_frequency,
    separate_bit_planes,
    extract_bit_plane,
    channel_grid,
)
from .compression_analysis import (
    blockiness_score,
    blocking_map,
    estimate_jpeg_quality,
    compression_report,
    deblock,
)
from .contrast_brightness import adjust_contrast_brightness, auto_contrast
from .crop_resize import crop, resize, resize_one_to_one, rotate, flip
from .curves import CURVE_PRESETS, apply_curve, build_lut, s_curve, curve_from_string
from .detail_enhancement import (
    local_contrast,
    enhance_detail,
    multiscale_detail,
    texture_boost,
)
from .ela import error_level_analysis, ela_stats, recompress
from .fisheye_correction import (
    correct_barrel_distortion,
    correct_fisheye,
    apply_barrel_distortion,
    estimate_straightness,
)
from .invert import invert, invert_channel, invert_luminance, solarize
from .jpeg_ghost import DEFAULT_QUALITIES as GHOST_QUALITIES, ghost_map, ghost_report
from .metadata_forensics import (
    EDITOR_SIGNATURES,
    check_timestamps,
    detect_editing_software,
    metadata_report,
    parse_exif_datetime,
    read_exif,
)
from .measure_3d import (
    VERTICAL_AT_INFINITY,
    draw_height_measurement,
    horizon_from_vanishing_points,
    line_through,
    measure_height,
    resolve_horizon,
    vanishing_point,
)
from .nl_means_denoise import (
    nl_means_denoise,
    nl_means_denoise_auto,
    nl_means_denoise_frames,
    estimate_h,
)
from .perspective_correction import (
    KNOWN_RATIOS,
    order_corners,
    correct_perspective,
    correct_perspective_named,
    find_document_corners,
    auto_correct_perspective,
)
from .redaction import redact, redact_region, verify_redaction, is_reversible
from .saturation import (
    adjust_saturation,
    adjust_vibrance,
    desaturate,
    selective_saturation,
)
from .super_resolution import (
    upscale,
    estimate_shifts,
    super_resolve,
    super_resolve_report,
)
from .undistort import (
    CameraCalibration,
    calibrate_from_chessboard,
    undistort,
    undistort_with_file,
    save_calibration,
    load_calibration,
)
from .white_balance import (
    auto_white_balance,
    white_balance_from_patch,
    adjust_temperature,
    compute_gains,
)
from .edge_detection import (
    canny_edges,
    auto_canny,
    sobel_edges,
    laplacian_edges,
    edge_density,
)
from .fft_analysis import (
    fft_magnitude_spectrum,
    fft_filter,
    detect_periodic_peaks,
    remove_periodic_noise,
)
from .frame_averaging import (
    average_frames,
    median_frames,
    integrate_frames,
    frame_difference,
    sharpest_frames,
)
from .histogram import (
    compute_histogram,
    histogram_stats,
    dynamic_range_used,
    render_histogram,
)
from .motion_deblur import (
    motion_blur_psf,
    defocus_psf,
    apply_psf,
    wiener_deconvolution,
    deblur_motion,
    deblur_defocus,
    deblur_sweep,
    focus_score,
)
from .noise_analysis import estimate_noise, estimate_snr, noise_map, noise_report
from .histogram_equalization import histogram_equalization, adaptive_histogram_equalization
from .levels import adjust_levels, auto_levels
from .roi import (
    ROI,
    extract_roi,
    apply_to_roi,
    draw_roi,
    analyze_roi,
    get_centered_roi,
    roi_from_ratio,
)
from .sharpen import unsharp_mask, laplacian_sharpen, sharpen_grid
from .smoothing import gaussian_blur, median_filter, bilateral_filter
from .registry import (
    FILTER_REGISTRY,
    FilterSpec,
    CATEGORY_ORDER,
    resolve_filter,
    filter_function,
    list_filters,
    apply_preset,
)

__all__ = [
    # clahe
    'apply_clahe', 'apply_clahe_grid',
    # contrast / brightness
    'adjust_contrast_brightness', 'auto_contrast',
    # crop / resize
    'crop', 'resize', 'resize_one_to_one', 'rotate', 'flip',
    # histogram
    'histogram_equalization', 'adaptive_histogram_equalization',
    # levels
    'adjust_levels', 'auto_levels',
    # roi
    'ROI', 'extract_roi', 'apply_to_roi', 'draw_roi', 'analyze_roi',
    'get_centered_roi', 'roi_from_ratio',
    # sharpen
    'unsharp_mask', 'laplacian_sharpen', 'sharpen_grid',
    # smoothing
    'gaussian_blur', 'median_filter', 'bilateral_filter',
    # edge detection
    'canny_edges', 'auto_canny', 'sobel_edges', 'laplacian_edges', 'edge_density',
    # histogram
    'compute_histogram', 'histogram_stats', 'dynamic_range_used', 'render_histogram',
    # ela
    'error_level_analysis', 'ela_stats', 'recompress',
    # fft
    'fft_magnitude_spectrum', 'fft_filter', 'detect_periodic_peaks', 'remove_periodic_noise',
    # noise
    'estimate_noise', 'estimate_snr', 'noise_map', 'noise_report',
    # clone detection
    'detect_copy_move', 'draw_clone_regions', 'highlight_clones',
    # deblur
    'motion_blur_psf', 'defocus_psf', 'apply_psf', 'wiener_deconvolution',
    'deblur_motion', 'deblur_defocus', 'deblur_sweep', 'focus_score',
    # frame averaging
    'average_frames', 'median_frames', 'integrate_frames', 'frame_difference',
    'sharpest_frames',
    # curves
    'CURVE_PRESETS', 'apply_curve', 'build_lut', 's_curve', 'curve_from_string',
    # white balance
    'auto_white_balance', 'white_balance_from_patch', 'adjust_temperature',
    'compute_gains',
    # saturation
    'adjust_saturation', 'adjust_vibrance', 'desaturate', 'selective_saturation',
    # colour balance
    'adjust_color_balance', 'adjust_cmyk', 'channel_mixer',
    # invert
    'invert', 'invert_channel', 'invert_luminance', 'solarize',
    # jpeg ghost
    'GHOST_QUALITIES', 'ghost_map', 'ghost_report',
    # metadata forensics
    'EDITOR_SIGNATURES', 'check_timestamps', 'detect_editing_software',
    'metadata_report', 'parse_exif_datetime', 'read_exif',
    # nl means
    'nl_means_denoise', 'nl_means_denoise_auto', 'nl_means_denoise_frames',
    'estimate_h',
    # super resolution
    'upscale', 'estimate_shifts', 'super_resolve', 'super_resolve_report',
    # detail enhancement
    'local_contrast', 'enhance_detail', 'multiscale_detail', 'texture_boost',
    # perspective
    'KNOWN_RATIOS', 'order_corners', 'correct_perspective',
    'correct_perspective_named', 'find_document_corners', 'auto_correct_perspective',
    # fisheye
    'correct_barrel_distortion', 'correct_fisheye', 'apply_barrel_distortion',
    'estimate_straightness',
    # aspect ratio
    'PIXEL_ASPECT_RATIOS', 'correct_pixel_aspect', 'correct_pixel_aspect_named',
    'fit_to_aspect', 'describe_aspect',
    # undistort
    'CameraCalibration', 'calibrate_from_chessboard', 'undistort',
    'undistort_with_file', 'save_calibration', 'load_calibration',
    # compression analysis
    'blockiness_score', 'blocking_map', 'estimate_jpeg_quality',
    'compression_report', 'deblock',
    # colour deconvolution
    'STAIN_PRESETS', 'deconvolve_colors', 'extract_stain', 'estimate_stain_vector',
    'normalize_vectors',
    # component separation
    'COLOR_SPACES', 'separate_channels', 'extract_component', 'separate_frequency',
    'separate_bit_planes', 'extract_bit_plane', 'channel_grid',
    # redaction
    'redact', 'redact_region', 'verify_redaction', 'is_reversible',
    # annotate
    'Scale', 'draw_arrow', 'draw_text', 'draw_shape', 'draw_measurement',
    'draw_scale_bar', 'measure_distance', 'measure_area', 'scale_from_reference',
    # measure 3d
    'VERTICAL_AT_INFINITY', 'draw_height_measurement',
    'horizon_from_vanishing_points', 'line_through', 'measure_height',
    'resolve_horizon', 'vanishing_point',
    # registry
    'FILTER_REGISTRY', 'FilterSpec', 'CATEGORY_ORDER', 'resolve_filter', 'filter_function',
    'list_filters', 'apply_preset',
]
