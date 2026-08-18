"""
Command-line interface for cv-tools.

Filters are applied in the order they appear on the command line, so
``--brightness 20 --clahe clip=3.0`` and ``--clahe clip=3.0 --brightness 20``
produce different results, exactly like reordering steps in a filter chain.

Usage:
    python -m src.cli input.jpg --clahe clip=2.0 tile=8x8 -o output.jpg
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .core.loader import ImageLoader, save_image
from .core.pipeline import Pipeline
from .core.report import ReportGenerator
from .filters.aspect_ratio import PIXEL_ASPECT_RATIOS
from .filters.clone_detection import detect_copy_move
from .filters.compression_analysis import compression_report
from .filters.curves import curve_from_string
from .filters.ela import ela_stats
from .filters.jpeg_ghost import ghost_report
from .filters.perspective_correction import KNOWN_RATIOS
from .filters.frame_averaging import (
    average_frames,
    integrate_frames,
    median_frames,
    sharpest_frames,
)
from .filters.histogram import dynamic_range_used, histogram_stats, render_histogram
from .filters.noise_analysis import noise_report
from .filters.registry import resolve_filter, list_filters
from .filters.roi import ROI, analyze_roi
from .utils.compare import side_by_side
from .utils.parsing import (
    parse_float_list,
    parse_int_list,
    parse_kv,
    parse_resize_spec,
)


# Report format chosen by the output file's extension
REPORT_FORMATS = {'.json': 'json', '.pdf': 'pdf', '.md': 'markdown'}


class ChainAction(argparse.Action):
    """Record filter flags into a single ordered list on the namespace."""

    def __call__(self, parser, namespace, values, option_string=None):
        chain = getattr(namespace, 'chain', None)
        if chain is None:
            chain = []
            setattr(namespace, 'chain', chain)
        chain.append((self.dest, values, option_string))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='cv-tools',
        description='Modular forensic image enhancement toolkit (Sprint 1 filters).',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python -m src.cli in.jpg --clahe clip=2.0 tile=8x8 -o out.jpg\n"
            "  python -m src.cli in.jpg --roi 100,100,300,200 -o crop.jpg\n"
            "  python -m src.cli in.jpg --brightness 20 --contrast 1.5 -o out.jpg\n"
            "  python -m src.cli in.jpg --levels 20,1.0,220 --report report.md -o out.jpg\n"
            "  python -m src.cli frames/ --clahe --batch -o enhanced/\n"
        ),
    )

    parser.add_argument('input', nargs='?',
                        help='Input image, video, or directory (with --batch)')
    parser.add_argument('-o', '--output',
                        help='Output file, or output directory with --batch')

    # ---- Adjust filters ----
    adjust = parser.add_argument_group('adjust filters')
    adjust.add_argument('--clahe', nargs='*', metavar='KEY=VALUE', action=ChainAction,
                        help='CLAHE. Params: clip (float), tile (int or WxH), mode '
                             '(lab|hsv|yuv|channelwise|luminance)')
    adjust.add_argument('--brightness', type=float, metavar='VALUE', action=ChainAction,
                        help='Brightness offset (-255 to 255)')
    adjust.add_argument('--contrast', type=float, metavar='FACTOR', action=ChainAction,
                        help='Contrast factor (1.0 = unchanged)')
    adjust.add_argument('--gamma', type=float, metavar='VALUE', action=ChainAction,
                        help='Gamma correction (<1 brighter, >1 darker)')
    adjust.add_argument('--auto-contrast', nargs='?', type=float, const=0.0, metavar='CUTOFF',
                        action=ChainAction,
                        help='Auto contrast, ignoring CUTOFF%% outliers (default 0)')
    adjust.add_argument('--levels', metavar='BLACK,GAMMA,WHITE', action=ChainAction,
                        help='Levels adjustment, e.g. 20,1.0,220')
    adjust.add_argument('--auto-levels', nargs=0, action=ChainAction,
                        help='Automatic levels stretch')
    adjust.add_argument('--histeq', nargs='*', metavar='KEY=VALUE', action=ChainAction,
                        help='Global histogram equalization. Params: mode '
                             '(lab|hsv|yuv|channelwise|grayscale)')

    adjust.add_argument('--curves', nargs='*', metavar='KEY=VALUE', action=ChainAction,
                        help='Tonal curve. Params: preset (name), points '
                             '(in:out,in:out,...), channel (r|g|b)')
    adjust.add_argument('--s-curve', nargs='?', type=float, const=0.25, metavar='STRENGTH',
                        action=ChainAction,
                        help='Symmetric S-curve contrast (default strength 0.25)')
    adjust.add_argument('--white-balance', nargs='*', metavar='KEY=VALUE',
                        action=ChainAction,
                        help='Auto white balance. Params: method '
                             '(gray_world|white_patch|shades_of_gray)')
    adjust.add_argument('--wb-patch', metavar='X,Y,W,H', action=ChainAction,
                        help='White balance from a region known to be neutral')
    adjust.add_argument('--temperature', nargs='*', metavar='KEY=VALUE',
                        action=ChainAction,
                        help='Manual white balance. Params: temperature, tint (-100..100)')
    adjust.add_argument('--saturation', type=float, metavar='FACTOR', action=ChainAction,
                        help='Saturation multiplier (1.0 = unchanged)')
    adjust.add_argument('--vibrance', type=float, metavar='FACTOR', action=ChainAction,
                        help='Saturation weighted towards muted colours')
    adjust.add_argument('--desaturate', nargs='?', const='luminance', metavar='METHOD',
                        action=ChainAction,
                        help='Grayscale: luminance|average|lightness|max|min')
    adjust.add_argument('--color-balance', nargs='*', metavar='KEY=VALUE',
                        action=ChainAction,
                        help='Per-range RGB shift. Params: shadows, midtones, '
                             'highlights as r:g:b, each -100..100')
    adjust.add_argument('--cmyk', nargs='*', metavar='KEY=VALUE', action=ChainAction,
                        help='Subtractive adjustment. Params: cyan, magenta, yellow, black')
    adjust.add_argument('--invert', nargs='?', const='all', metavar='WHAT',
                        action=ChainAction,
                        help='Invert: all|luminance|r|g|b')
    adjust.add_argument('--solarize', nargs='?', type=int, const=128, metavar='THRESHOLD',
                        action=ChainAction,
                        help='Invert values above a threshold (default 128)')

    # ---- Enhance filters ----
    enhance = parser.add_argument_group('enhance filters')
    enhance.add_argument('--sharpen', nargs='*', metavar='KEY=VALUE', action=ChainAction,
                         help='Unsharp mask. Params: amount (float), radius (float), '
                              'threshold (int, protects flat areas)')
    enhance.add_argument('--sharpen-laplacian', nargs='*', metavar='KEY=VALUE',
                         action=ChainAction,
                         help='Laplacian sharpening. Params: strength (float), kernel (odd int)')
    enhance.add_argument('--gaussian', nargs='?', type=float, const=2.0, metavar='RADIUS',
                         action=ChainAction,
                         help='Gaussian blur with the given sigma (default 2.0)')
    enhance.add_argument('--median', nargs='?', type=int, const=3, metavar='KSIZE',
                         action=ChainAction,
                         help='Median filter, odd window >= 3 (default 3)')
    enhance.add_argument('--bilateral', nargs='*', metavar='KEY=VALUE', action=ChainAction,
                         help='Edge-preserving denoise. Params: d (int), color (float), '
                              'space (float)')

    enhance.add_argument('--nl-means', nargs='*', metavar='KEY=VALUE', action=ChainAction,
                         help='Non-local means denoise. Params: h, h_color, template, search')
    enhance.add_argument('--nl-means-auto', nargs='?', type=float, const=1.0,
                         metavar='AGGRESSIVENESS', action=ChainAction,
                         help='Non-local means with strength from measured noise')
    enhance.add_argument('--upscale', nargs='*', metavar='KEY=VALUE', action=ChainAction,
                         help='Interpolated enlargement (adds no information). '
                              'Params: scale, method, sharpen')
    enhance.add_argument('--local-contrast', nargs='*', metavar='KEY=VALUE',
                         action=ChainAction,
                         help='Clarity. Params: radius, strength')
    enhance.add_argument('--detail-enhance', nargs='*', metavar='KEY=VALUE',
                         action=ChainAction,
                         help='Edge-preserving texture boost. Params: sigma_s, sigma_r')
    enhance.add_argument('--texture-boost', nargs='?', type=float, const=0.6,
                         metavar='AMOUNT', action=ChainAction,
                         help='Texture contrast with edge protection')

    # ---- Geometric correction ----
    correct = parser.add_argument_group('geometric correction')
    correct.add_argument('--perspective', metavar='X1,Y1,X2,Y2,X3,Y3,X4,Y4',
                         action=ChainAction,
                         help='Rectify the quadrilateral through these four corners')
    correct.add_argument('--perspective-ratio', metavar='NAME',
                         help='Known aspect for --perspective: a4_portrait, plate_eu, ...')
    correct.add_argument('--auto-perspective', nargs='*', metavar='KEY=VALUE',
                         action=ChainAction,
                         help='Detect a rectangular surface and rectify it')
    correct.add_argument('--barrel', nargs='*', metavar='KEY=VALUE', action=ChainAction,
                         help='Radial distortion correction. Params: k1, k2, zoom')
    correct.add_argument('--fisheye', nargs='*', metavar='KEY=VALUE', action=ChainAction,
                         help='Fisheye correction. Params: strength, zoom')
    correct.add_argument('--pixel-aspect', metavar='RATIO_OR_NAME', action=ChainAction,
                         help='Square up non-square pixels, e.g. 1.09 or pal_43')
    correct.add_argument('--fit-aspect', nargs='*', metavar='KEY=VALUE',
                         action=ChainAction,
                         help='Fit to a display aspect. Params: ratio, mode '
                              '(pad|crop|stretch)')
    correct.add_argument('--undistort', metavar='CALIBRATION.json', action=ChainAction,
                         help='Lens correction from a saved camera calibration')

    # ---- Separation and redaction ----
    special = parser.add_argument_group('separation and redaction')
    special.add_argument('--component', metavar='SPACE:CHANNEL', action=ChainAction,
                         help='Extract a colour component, e.g. lab:a or hsv:S')
    special.add_argument('--bit-plane', type=int, metavar='N', action=ChainAction,
                         help='Extract bit plane 0 (lowest) to 7 (highest)')
    special.add_argument('--stain', nargs='*', metavar='KEY=VALUE', action=ChainAction,
                         help='Colour deconvolution. Params: preset, index, invert')
    special.add_argument('--redact', metavar='X,Y,W,H', action=ChainAction,
                         help='Obscure a region; see --redact-method')
    special.add_argument('--redact-method', default='fill',
                         choices=['fill', 'noise', 'blur', 'pixelate'],
                         help='How --redact obscures. fill and noise destroy the '
                              'content; blur and pixelate are reversible (default: fill)')
    special.add_argument('--measure-3d', nargs='*', metavar='KEY=VALUE',
                         action=ChainAction,
                         help='Object height from one view. Params: base, top, '
                              'reference_base, reference_top (all X,Y), horizon '
                              '(a row, or X1,Y1,X2,Y2), reference_height, '
                              'vertical_point, unit_name')
    special.add_argument('--blocking-map', nargs='?', type=int, const=32,
                         metavar='BLOCK', action=ChainAction,
                         help='Per-region JPEG blocking map')
    special.add_argument('--deblock', nargs='?', type=float, const=0.5,
                         metavar='STRENGTH', action=ChainAction,
                         help='Soften JPEG block edges')

    # ---- Edge detection ----
    edges = parser.add_argument_group('edge detection')
    edges.add_argument('--canny', metavar='LOW,HIGH', action=ChainAction,
                       help='Canny edge detection, e.g. 50,150')
    edges.add_argument('--auto-canny', nargs='?', type=float, const=0.33, metavar='SIGMA',
                       action=ChainAction,
                       help='Canny with thresholds from the image median (default sigma 0.33)')
    edges.add_argument('--sobel', nargs='*', metavar='KEY=VALUE', action=ChainAction,
                       help='Sobel gradients. Params: dx (0|1), dy (0|1), kernel (odd int)')
    edges.add_argument('--laplacian', nargs='*', metavar='KEY=VALUE', action=ChainAction,
                       help='Laplacian edge map. Params: kernel (odd int), blur (float)')
    edges.add_argument('--blur-first', type=float, default=0.0, metavar='SIGMA',
                       help='Gaussian pre-blur applied inside --canny/--auto-canny/--laplacian')

    # ---- Forensic filters ----
    forensic = parser.add_argument_group('forensic filters')
    forensic.add_argument('--ela', nargs='*', metavar='KEY=VALUE', action=ChainAction,
                          help='Error Level Analysis. Params: quality (1-100), scale '
                               '(0 = auto), gray (bool). JPEG originals only.')
    forensic.add_argument('--fft', nargs='*', metavar='KEY=VALUE', action=ChainAction,
                          help='FFT magnitude spectrum. Params: log (bool)')
    forensic.add_argument('--fft-filter', nargs='*', metavar='KEY=VALUE', action=ChainAction,
                          help='Frequency filter. Params: type (lowpass|highpass|bandpass), '
                               'cutoff (float), cutoff_high (float), soft (bool)')
    forensic.add_argument('--remove-periodic', nargs='*', metavar='KEY=VALUE',
                          action=ChainAction,
                          help='Notch out periodic pattern noise. Params: notch (float), '
                               'min_radius (float), threshold (float)')
    forensic.add_argument('--noise-map', nargs='?', type=int, const=32, metavar='BLOCK',
                          action=ChainAction,
                          help='Per-block noise level map (default block 32)')
    forensic.add_argument('--clone-detect', nargs='*', metavar='KEY=VALUE', action=ChainAction,
                          help='Highlight copy-move regions. Params: block (int), step (int), '
                               'matches (int), variance (float)')
    forensic.add_argument('--deblur', nargs='*', metavar='KEY=VALUE', action=ChainAction,
                          help='Wiener motion deblur. Params: length (float), angle (float), '
                               'noise (float)')
    forensic.add_argument('--deblur-defocus', nargs='*', metavar='KEY=VALUE',
                          action=ChainAction,
                          help='Wiener defocus deblur. Params: radius (float), noise (float)')
    forensic.add_argument('--ghost', nargs='*', metavar='KEY=VALUE', action=ChainAction,
                          help='JPEG ghost map: best-match quality per block. Params: '
                               'block (int), min (int), max (int), step (int) for the '
                               'quality sweep. JPEG originals only.')

    # ---- Geometric filters ----
    geom = parser.add_argument_group('geometric filters')
    geom.add_argument('--roi', metavar='X,Y,W,H', action=ChainAction,
                      help='Crop to region of interest')
    geom.add_argument('--draw-roi', metavar='X,Y,W,H', action=ChainAction,
                      help='Draw a region of interest rectangle')
    geom.add_argument('--crop', metavar='X,Y,W,H', action=ChainAction,
                      help='Crop to region')
    geom.add_argument('--resize', metavar='SPEC', action=ChainAction,
                      help='Resize: WxH, 800x, x600, 50%% or 0.5')
    geom.add_argument('--interpolation', default='auto',
                      choices=['auto', 'nearest', 'bilinear', 'bicubic', 'lanczos', 'area'],
                      help='Interpolation for --resize (default: auto)')
    geom.add_argument('--rotate', type=float, metavar='DEGREES', action=ChainAction,
                      help='Rotate by angle (counter-clockwise)')
    geom.add_argument('--flip', choices=['horizontal', 'vertical', 'both'], action=ChainAction,
                      help='Flip image')

    # ---- Analysis & output ----
    out = parser.add_argument_group('analysis and output')
    out.add_argument('--analyze-roi', metavar='X,Y,W,H',
                     help='Print statistics for a region of the processed image')
    out.add_argument('--histogram', metavar='PATH',
                     help='Write a histogram chart of the processed image')
    out.add_argument('--histogram-log', action='store_true',
                     help='Plot --histogram on a log scale')
    out.add_argument('--hist-stats', action='store_true',
                     help='Print tonal statistics and clipping percentages')
    out.add_argument('--noise-stats', action='store_true',
                     help='Print noise sigma, SNR, and per-block uniformity')
    out.add_argument('--ela-stats', nargs='?', type=int, const=90, metavar='QUALITY',
                     help='Print Error Level Analysis block statistics (default quality 90)')
    out.add_argument('--clone-stats', action='store_true',
                     help='Print copy-move detection results without altering the image')
    out.add_argument('--compression-stats', action='store_true',
                     help='Print JPEG blocking measures and, for a JPEG source, its quality')
    out.add_argument('--ghost-stats', action='store_true',
                     help='Print JPEG ghost detection results without altering the image')
    out.add_argument('--info', action='store_true',
                     help='Print source metadata (dimensions, EXIF, SHA-256)')
    out.add_argument('--report', metavar='PATH',
                     help='Write a processing report (.md or .json)')
    out.add_argument('--compare', metavar='PATH',
                     help='Write a side-by-side original vs processed image')
    out.add_argument('--save-preset', metavar='PATH',
                     help='Save the applied filter chain as a JSON preset')
    out.add_argument('--load-preset', metavar='PATH',
                     help='Apply a JSON preset before any command-line filters')
    out.add_argument('--frame', type=int, default=0, metavar='N',
                     help='Frame index for video input (default: 0)')
    out.add_argument('--frames', type=int, default=0, metavar='N',
                     help='Combine N video frames into the source image, starting at --frame')
    out.add_argument('--frame-step', type=int, default=1, metavar='N',
                     help='Stride between the frames gathered by --frames (default: 1)')
    out.add_argument('--frame-method', default='mean',
                     choices=['mean', 'median', 'integrate', 'sharpest'],
                     help='How --frames are combined: mean denoises, median removes moving '
                          'objects, integrate brightens dark footage, sharpest averages only '
                          'the best-focused half (default: mean)')
    out.add_argument('--batch', action='store_true',
                     help='Process every image in the input directory')
    out.add_argument('--recursive', action='store_true',
                     help='With --batch, also descend into subdirectories')
    out.add_argument('--quality', type=int, default=95, metavar='Q',
                     help='JPEG quality 1-100 (default: 95)')
    out.add_argument('--list-filters', action='store_true',
                     help='List registered filters and exit')
    out.add_argument('-v', '--verbose', action='store_true',
                     help='Print each step as it is applied')

    return parser


def translate_step(
    dest: str,
    value: Any,
    interpolation: str = 'auto',
    blur_first: float = 0.0,
    perspective_ratio: Optional[str] = None,
    redact_method: str = 'fill',
) -> Tuple[str, Dict[str, Any]]:
    """
    Convert one parsed command-line filter flag into (registry_name, params).

    Args:
        dest: argparse destination name of the filter flag
        value: The flag's parsed value
        interpolation: Interpolation mode to attach to a resize step
        blur_first: Gaussian pre-blur sigma for the edge detectors
        perspective_ratio: Named aspect ratio applied to a perspective step
        redact_method: How a redaction step obscures its region

    Raises:
        ValueError: If the flag's value is malformed
    """
    if dest == 'clahe':
        params = parse_kv(value or [])
        mapped: Dict[str, Any] = {}
        if 'clip' in params:
            mapped['clip_limit'] = float(params.pop('clip'))
        if 'tile' in params:
            mapped['tile_grid_size'] = params.pop('tile')
        if 'mode' in params:
            mapped['color_mode'] = params.pop('mode')
        mapped.update(params)
        return 'clahe', mapped

    if dest == 'brightness':
        return 'contrast_brightness', {'brightness': float(value)}

    if dest == 'contrast':
        return 'contrast_brightness', {'contrast': float(value)}

    if dest == 'gamma':
        return 'contrast_brightness', {'gamma': float(value)}

    if dest == 'auto_contrast':
        return 'auto_contrast', {'cutoff': float(value if value is not None else 0.0)}

    if dest == 'levels':
        black, gamma, white = parse_float_list(value, 3)
        return 'levels', {'black_point': black, 'gamma': gamma, 'white_point': white}

    if dest == 'auto_levels':
        return 'auto_levels', {}

    if dest == 'histeq':
        params = parse_kv(value or [])
        if 'mode' in params:
            params['color_mode'] = params.pop('mode')
        return 'histeq', params

    if dest in ('roi', 'crop'):
        x, y, w, h = parse_int_list(value, 4)
        # --roi clips to image bounds; --crop rejects an out-of-bounds region
        name = 'roi_crop' if dest == 'roi' else 'crop'
        return name, {'x': x, 'y': y, 'width': w, 'height': h}

    if dest == 'draw_roi':
        x, y, w, h = parse_int_list(value, 4)
        return 'roi_draw', {'x': x, 'y': y, 'width': w, 'height': h}

    if dest == 'resize':
        params = parse_resize_spec(value)
        params['interpolation'] = interpolation
        return 'resize', params

    if dest == 'rotate':
        return 'rotate', {'angle': float(value)}

    if dest == 'flip':
        return 'flip', {'direction': value}

    if dest == 'sharpen':
        params = parse_kv(value or [])
        return 'sharpen', params

    if dest == 'sharpen_laplacian':
        params = parse_kv(value or [])
        if 'kernel' in params:
            params['kernel_size'] = int(params.pop('kernel'))
        return 'sharpen_laplacian', params

    if dest == 'gaussian':
        return 'gaussian_blur', {'radius': float(value if value is not None else 2.0)}

    if dest == 'median':
        return 'median_filter', {'kernel_size': int(value if value is not None else 3)}

    if dest == 'bilateral':
        params = parse_kv(value or [])
        if 'd' in params:
            params['diameter'] = int(params.pop('d'))
        if 'color' in params:
            params['sigma_color'] = float(params.pop('color'))
        if 'space' in params:
            params['sigma_space'] = float(params.pop('space'))
        return 'bilateral_filter', params

    if dest == 'canny':
        low, high = parse_float_list(value, 2)
        params = {'low_threshold': low, 'high_threshold': high}
        if blur_first > 0:
            params['blur_sigma'] = blur_first
        return 'canny', params

    if dest == 'auto_canny':
        params = {'sigma': float(value if value is not None else 0.33)}
        if blur_first > 0:
            params['blur_sigma'] = blur_first
        return 'auto_canny', params

    if dest == 'sobel':
        params = parse_kv(value or [])
        if 'kernel' in params:
            params['kernel_size'] = int(params.pop('kernel'))
        return 'sobel', params

    if dest == 'laplacian':
        params = parse_kv(value or [])
        if 'kernel' in params:
            params['kernel_size'] = int(params.pop('kernel'))
        if 'blur' in params:
            params['blur_sigma'] = float(params.pop('blur'))
        elif blur_first > 0:
            params['blur_sigma'] = blur_first
        return 'laplacian', params

    if dest == 'ela':
        params = parse_kv(value or [])
        if 'gray' in params:
            params['grayscale'] = bool(params.pop('gray'))
        return 'ela', params

    if dest == 'fft':
        params = parse_kv(value or [])
        if 'log' in params:
            params['log_scale'] = bool(params.pop('log'))
        return 'fft_spectrum', params

    if dest == 'fft_filter':
        params = parse_kv(value or [])
        if 'type' in params:
            params['filter_type'] = params.pop('type')
        return 'fft_filter', params

    if dest == 'remove_periodic':
        params = parse_kv(value or [])
        if 'notch' in params:
            params['notch_radius'] = float(params.pop('notch'))
        return 'remove_periodic', params

    if dest == 'noise_map':
        return 'noise_map', {'block_size': int(value if value is not None else 32)}

    if dest == 'clone_detect':
        params = parse_kv(value or [])
        if 'block' in params:
            params['block_size'] = int(params.pop('block'))
        if 'matches' in params:
            params['min_matches'] = int(params.pop('matches'))
        if 'variance' in params:
            params['min_variance'] = float(params.pop('variance'))
        return 'clone_detect', params

    if dest == 'deblur':
        params = parse_kv(value or [])
        if 'noise' in params:
            params['noise_power'] = float(params.pop('noise'))
        return 'deblur_motion', params

    if dest == 'deblur_defocus':
        params = parse_kv(value or [])
        if 'noise' in params:
            params['noise_power'] = float(params.pop('noise'))
        return 'deblur_defocus', params

    if dest == 'ghost':
        params = parse_kv(value or [])
        mapped: Dict[str, Any] = {}
        if 'block' in params:
            mapped['block_size'] = int(params.pop('block'))
        low = int(params.pop('min', 50))
        high = int(params.pop('max', 100))
        step = int(params.pop('step', 5))
        mapped['qualities'] = list(range(low, high + 1, step))
        mapped.update(params)
        return 'ghost', mapped

    # ---- Adjust ----
    if dest == 'curves':
        params = parse_kv(value or [])
        if 'points' in params:
            params['points'] = curve_from_string(str(params.pop('points')))
        return 'curves', params

    if dest == 's_curve':
        return 's_curve', {'strength': float(value if value is not None else 0.25)}

    if dest == 'white_balance':
        return 'white_balance', parse_kv(value or [])

    if dest == 'wb_patch':
        x, y, w, h = parse_int_list(value, 4)
        return 'white_balance_patch', {'x': x, 'y': y, 'width': w, 'height': h}

    if dest == 'temperature':
        return 'temperature', parse_kv(value or [])

    if dest == 'saturation':
        return 'saturation', {'factor': float(value)}

    if dest == 'vibrance':
        return 'vibrance', {'factor': float(value)}

    if dest == 'desaturate':
        return 'desaturate', {'method': value or 'luminance'}

    if dest == 'color_balance':
        params = parse_kv(value or [])
        mapped: Dict[str, Any] = {}
        for key in ('shadows', 'midtones', 'highlights'):
            if key in params:
                mapped[key] = parse_float_list(str(params.pop(key)).replace(':', ','), 3)
        mapped.update(params)
        return 'color_balance', mapped

    if dest == 'cmyk':
        return 'cmyk', parse_kv(value or [])

    if dest == 'invert':
        what = (value or 'all').lower()
        if what == 'all':
            return 'invert', {}
        if what in ('luminance', 'luma'):
            return 'invert_luminance', {}
        if what in ('r', 'g', 'b', 'red', 'green', 'blue'):
            return 'invert_channel', {'channel': what}
        raise ValueError(f"Expected all, luminance, or a channel; got {what!r}")

    if dest == 'solarize':
        return 'solarize', {'threshold': int(value if value is not None else 128)}

    # ---- Enhance ----
    if dest == 'nl_means':
        params = parse_kv(value or [])
        if 'template' in params:
            params['template_window'] = int(params.pop('template'))
        if 'search' in params:
            params['search_window'] = int(params.pop('search'))
        return 'nl_means', params

    if dest == 'nl_means_auto':
        return 'nl_means_auto', {
            'aggressiveness': float(value if value is not None else 1.0)
        }

    if dest == 'upscale':
        return 'upscale', parse_kv(value or [])

    if dest == 'local_contrast':
        return 'local_contrast', parse_kv(value or [])

    if dest == 'detail_enhance':
        return 'detail_enhance', parse_kv(value or [])

    if dest == 'texture_boost':
        return 'texture_boost', {'amount': float(value if value is not None else 0.6)}

    # ---- Geometric correction ----
    if dest == 'perspective':
        numbers = parse_float_list(value, 8)
        corners = [[numbers[i], numbers[i + 1]] for i in range(0, 8, 2)]
        params = {'corners': corners}
        if perspective_ratio:
            if perspective_ratio not in KNOWN_RATIOS:
                available = ', '.join(sorted(KNOWN_RATIOS))
                raise ValueError(
                    f"Unknown ratio '{perspective_ratio}'. Available: {available}"
                )
            params['aspect_ratio'] = KNOWN_RATIOS[perspective_ratio]
        return 'perspective', params

    if dest == 'auto_perspective':
        return 'auto_perspective', parse_kv(value or [])

    if dest == 'barrel':
        return 'barrel', parse_kv(value or [])

    if dest == 'fisheye':
        return 'fisheye', parse_kv(value or [])

    if dest == 'pixel_aspect':
        text = str(value)
        if text in PIXEL_ASPECT_RATIOS:
            return 'pixel_aspect', {'pixel_aspect': PIXEL_ASPECT_RATIOS[text]}
        try:
            return 'pixel_aspect', {'pixel_aspect': float(text)}
        except ValueError:
            available = ', '.join(sorted(PIXEL_ASPECT_RATIOS))
            raise ValueError(
                f"Expected a ratio or a format name. Available: {available}"
            ) from None

    if dest == 'fit_aspect':
        params = parse_kv(value or [])
        if 'ratio' in params:
            params['target_ratio'] = float(params.pop('ratio'))
        if 'target_ratio' not in params:
            raise ValueError("--fit-aspect needs ratio=<width/height>, e.g. ratio=1.777")
        return 'fit_aspect', params

    if dest == 'undistort':
        return 'undistort', {'calibration_path': str(value)}

    # ---- Separation and redaction ----
    if dest == 'component':
        text = str(value)
        if ':' not in text:
            raise ValueError(f"Expected SPACE:CHANNEL, e.g. lab:a; got {text!r}")
        space, _, channel = text.partition(':')
        return 'component', {'space': space.lower(), 'channel': channel}

    if dest == 'bit_plane':
        return 'bit_plane', {'bit': int(value)}

    if dest == 'stain':
        return 'stain', parse_kv(value or [])

    if dest == 'redact':
        x, y, w, h = parse_int_list(value, 4)
        return 'redact', {'x': x, 'y': y, 'width': w, 'height': h,
                          'method': redact_method}

    if dest == 'measure_3d':
        params = parse_kv(value or [])
        # Points arrive as "352,408", which parse_value leaves as text
        for key in ('base', 'top', 'reference_base', 'reference_top',
                    'vertical_point', 'horizon'):
            if isinstance(params.get(key), str):
                parts = [p.strip() for p in str(params[key]).split(',')]
                if len(parts) > 1:
                    params[key] = [float(p) for p in parts]
        return 'measure_3d', params

    if dest == 'blocking_map':
        return 'blocking_map', {'block_size': int(value if value is not None else 32)}

    if dest == 'deblock':
        return 'deblock', {'strength': float(value if value is not None else 0.5)}

    raise ValueError(f"Unhandled filter flag: {dest}")


def process_image(
    image: np.ndarray,
    steps: List[Tuple[str, Dict[str, Any]]],
    preset: Optional[Dict[str, Any]] = None,
    verbose: bool = False,
) -> Pipeline:
    """
    Run a pipeline over one image: preset steps first, then command-line steps.

    Returns:
        The pipeline, so the caller can access the chain and report
    """
    pipeline = Pipeline(image)

    all_steps: List[Tuple[str, Dict[str, Any]]] = []
    if preset:
        all_steps.extend((s['name'], s.get('params', {})) for s in preset.get('filters', []))
    all_steps.extend(steps)

    for name, params in all_steps:
        spec = resolve_filter(name)
        if verbose:
            printable = ', '.join(f"{k}={v}" for k, v in params.items()) or 'defaults'
            print(f"  -> {spec.name} ({printable})", file=sys.stderr)
        pipeline.apply(spec.fn, spec.name, spec.module, params)

    return pipeline


def print_metadata(metadata: Dict[str, Any]) -> None:
    """Print source metadata, keeping EXIF as an indented sub-block."""
    print("Source metadata:")
    for key, value in metadata.items():
        if key == 'exif' and isinstance(value, dict):
            print("  exif:")
            for tag, tag_value in value.items():
                text = str(tag_value)
                if len(text) > 80:
                    text = text[:77] + '...'
                print(f"    {tag}: {text}")
        else:
            print(f"  {key}: {value}")


def print_roi_stats(stats: Dict[str, Any]) -> None:
    """Print ROI statistics in a readable block."""
    roi = stats['roi']
    print(f"ROI analysis (x={roi['x']}, y={roi['y']}, w={roi['width']}, h={roi['height']}):")
    print(f"  shape: {stats['shape']}, pixels: {stats['pixels']}")
    for channel, values in stats['channels'].items():
        print(f"  {channel}: mean={values['mean']:.2f} std={values['std']:.2f} "
              f"min={values['min']} max={values['max']}")


def print_histogram_stats(stats: Dict[str, Any], dynamic_range: float) -> None:
    """Print tonal statistics, flagging channels that have lost data to clipping."""
    print(f"Histogram statistics ({stats['pixels']} pixels):")
    print(f"  dynamic range used: {dynamic_range * 100:.1f}% of 0-255")
    for channel, values in stats['channels'].items():
        print(f"  {channel}: mean={values['mean']:.2f} median={values['median']:.1f} "
              f"std={values['std']:.2f} range={values['min']}-{values['max']} "
              f"p1={values['p1']:.0f} p99={values['p99']:.0f}")
        shadows = values['clipped_shadows_pct']
        highlights = values['clipped_highlights_pct']
        if shadows > 0.1 or highlights > 0.1:
            print(f"     clipped: {shadows:.2f}% shadows, {highlights:.2f}% highlights")


def combine_frames(frames: List[np.ndarray], method: str) -> np.ndarray:
    """
    Reduce a sequence of video frames to one source image.

    Raises:
        ValueError: If the method is unknown
    """
    if method == 'mean':
        return average_frames(frames)
    if method == 'median':
        return median_frames(frames)
    if method == 'integrate':
        return integrate_frames(frames)
    if method == 'sharpest':
        # Averaging only the better-focused half beats averaging everything
        # when part of the sequence is motion-blurred
        best = sharpest_frames(frames, count=max(1, len(frames) // 2))
        return average_frames([frames[index] for index in best])
    raise ValueError(f"Unknown frame method: {method}")


def print_noise_stats(report: Dict[str, Any]) -> None:
    """Print the noise report, flagging non-uniform noise across the frame."""
    print("Noise analysis:")
    print(f"  global sigma: {report['noise_sigma']:.2f}")
    snr = report['snr_db']
    print(f"  SNR: {'infinite' if snr == float('inf') else f'{snr:.1f} dB'}")
    blocks = report['blocks']
    print(f"  blocks: {blocks['rows']}x{blocks['cols']} of {report['block_size']}px, "
          f"mean={report['block_mean']:.2f} std={report['block_std']:.2f}")
    print(f"  uniformity: {report['uniformity']:.2f} "
          f"({'uneven - inspect' if report['uniformity'] > 0.6 else 'fairly even'})")
    noisiest = report['noisiest_block']
    quietest = report['quietest_block']
    print(f"  noisiest block at ({noisiest['x']}, {noisiest['y']}): "
          f"sigma={noisiest['sigma']:.2f}")
    print(f"  quietest block at ({quietest['x']}, {quietest['y']}): "
          f"sigma={quietest['sigma']:.2f}")


def print_ela_stats(stats: Dict[str, Any]) -> None:
    """Print ELA block statistics with the usual interpretation caveat."""
    print(f"Error Level Analysis (JPEG quality {stats['quality']}, "
          f"{stats['block_size']}px blocks):")
    print(f"  mean error: {stats['mean_error']:.2f}, max: {stats['max_error']:.2f}")
    print(f"  block mean: {stats['block_mean']:.2f}, std: {stats['block_std']:.2f}")
    hottest = stats['hottest_block']
    print(f"  hottest block at ({hottest['x']}, {hottest['y']}): "
          f"mean={hottest['mean_error']:.2f}, z-score={hottest['z_score']:.2f}")
    print("  note: only meaningful on JPEG originals; texture raises error levels too")


def print_clone_stats(result: Dict[str, Any]) -> None:
    """Print copy-move detection results."""
    print("Copy-move detection:")
    print(f"  blocks analyzed: {result['blocks_analyzed']} "
          f"({result['blocks_skipped']} skipped as featureless)")
    if not result['detected']:
        print("  no duplicated regions found")
        return
    print(f"  duplicated regions found: {result['match_count']} matching block pairs")
    for shift in result['shifts'][:5]:
        print(f"    shift dx={shift['dx']:+d} dy={shift['dy']:+d}: "
              f"{shift['matches']} pairs")
    print("  note: genuine repetition (tiles, windows, text) also matches")


def print_compression_stats(report: Dict[str, Any]) -> None:
    """Print blocking measures and any JPEG quality read from the file."""
    print("Compression analysis:")
    print(f"  blockiness: {report['blockiness']:.1f}/100 "
          f"(boundary step {report['boundary_step']:.2f} vs "
          f"interior {report['interior_step']:.2f})")
    print(f"  likely JPEG-compressed: {'yes' if report['likely_jpeg'] else 'no'}")
    print(f"  region uniformity: {report['region_uniformity']:.2f}")

    quality = report.get('jpeg_quality')
    if quality:
        print(f"  quantisation tables: {quality['tables']}, "
              f"estimated quality {quality['quality']}")
    elif 'jpeg_quality' in report:
        print("  no quantisation tables (not a JPEG, or already re-saved)")

    print("  note: blocking indicates compression strength, not manipulation")


def print_ghost_stats(report: Dict[str, Any]) -> None:
    """Print JPEG ghost detection results."""
    print(f"JPEG ghost detection (qualities {report['qualities'][0]}-{report['qualities'][-1]}, "
          f"{report['block_size']}px blocks):")
    print(f"  dominant quality: {report['dominant_quality']}")
    print(f"  outlier blocks: {report['outlier_count']} "
          f"({report['outlier_fraction'] * 100:.1f}% of blocks)")
    for outlier in report['outliers'][:5]:
        print(f"    block at ({outlier['x']}, {outlier['y']}): "
              f"best match quality {outlier['quality']}")
    print("  note: only meaningful on a single-JPEG composite; any re-save erases it")


def resolve_batch_output(
    output: Optional[str],
    source: Path,
    root: Optional[Path] = None,
) -> Path:
    """
    Work out the output path for one file in a batch run.

    With ``root`` given, the input tree's structure is mirrored under the
    output directory. That matters for a recursive run, where two
    subdirectories can hold files of the same name and a flat output directory
    would silently overwrite one with the other.
    """
    if output is None:
        return source.with_name(f"{source.stem}_processed{source.suffix}")

    out_dir = Path(output)
    if root is not None:
        try:
            target = out_dir / source.relative_to(root)
        except ValueError:
            target = out_dir / source.name
    else:
        target = out_dir / source.name

    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def run_one(
    path: Path,
    output_path: Optional[Path],
    steps: List[Tuple[str, Dict[str, Any]]],
    args: argparse.Namespace,
    preset: Optional[Dict[str, Any]],
) -> int:
    """Process a single input file. Returns a process exit code."""
    try:
        with ImageLoader(path) as loader:
            if args.frames > 0:
                if not loader.is_video:
                    raise ValueError(f"--frames requires a video file, got: {path.name}")
                frames = loader.load_frames(args.frames, start=args.frame,
                                            step=args.frame_step)
                image = combine_frames(frames, args.frame_method)
                if args.verbose:
                    print(f"Combined {len(frames)} frames with '{args.frame_method}'",
                          file=sys.stderr)
            else:
                image = loader.load(args.frame if loader.is_video else None)
            metadata = loader.metadata
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.info:
        print_metadata(metadata)

    if args.verbose:
        print(f"Processing {path.name} ({image.shape[1]}x{image.shape[0]})", file=sys.stderr)

    try:
        pipeline = process_image(image, steps, preset=preset, verbose=args.verbose)
    except (RuntimeError, KeyError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = pipeline.current

    if args.analyze_roi:
        x, y, w, h = parse_int_list(args.analyze_roi, 4)
        print_roi_stats(analyze_roi(result, ROI(x, y, w, h)))

    if args.hist_stats:
        print_histogram_stats(histogram_stats(result), dynamic_range_used(result))

    if args.noise_stats:
        print_noise_stats(noise_report(result))

    if args.ela_stats:
        print_ela_stats(ela_stats(result, quality=args.ela_stats))

    if args.clone_stats:
        print_clone_stats(detect_copy_move(result))

    if args.compression_stats:
        print_compression_stats(compression_report(result, path=path))

    if args.ghost_stats:
        print_ghost_stats(ghost_report(result))

    try:
        if output_path is not None:
            save_image(result, output_path, quality=args.quality)
            print(f"Saved: {output_path}")

        if args.compare:
            comparison = side_by_side(*pipeline.compare())
            save_image(comparison, args.compare, quality=args.quality)
            print(f"Saved comparison: {args.compare}")

        if args.histogram:
            chart = render_histogram(result, log_scale=args.histogram_log)
            save_image(chart, args.histogram, quality=args.quality)
            print(f"Saved histogram: {args.histogram}")

        if args.report:
            report = ReportGenerator(pipeline.generate_report(), metadata)
            fmt = REPORT_FORMATS.get(Path(args.report).suffix.lower(), 'markdown')
            report.save(args.report, format=fmt)
            print(f"Saved report: {args.report}")

        if args.save_preset:
            pipeline.save_preset(args.save_preset)
            print(f"Saved preset: {args.save_preset}")
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_filters:
        print("Registered filters:")
        for name, description in sorted(list_filters()):
            print(f"  {name:22s} {description}")
        return 0

    if not args.input:
        parser.error("the following arguments are required: input")

    # Translate ordered flags into registry steps
    steps: List[Tuple[str, Dict[str, Any]]] = []
    for dest, value, option_string in getattr(args, 'chain', []):
        try:
            steps.append(translate_step(
                dest, value, args.interpolation, args.blur_first,
                perspective_ratio=args.perspective_ratio,
                redact_method=args.redact_method,
            ))
        except ValueError as exc:
            parser.error(f"{option_string}: {exc}")

    preset: Optional[Dict[str, Any]] = None
    if args.load_preset:
        try:
            with open(args.load_preset, 'r', encoding='utf-8') as f:
                preset = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"error: could not read preset {args.load_preset}: {exc}", file=sys.stderr)
            return 1

    input_path = Path(args.input)

    if args.batch:
        if not input_path.is_dir():
            print(f"error: --batch requires a directory, got: {input_path}", file=sys.stderr)
            return 1

        sources = ImageLoader.find_images(input_path, recursive=args.recursive)
        if not sources:
            print(f"error: no supported images found in {input_path}", file=sys.stderr)
            return 1

        # Per-file reports/presets would overwrite each other; write them once.
        # Comparisons and histograms have no per-file path, so they are skipped.
        batch_args = argparse.Namespace(**vars(args))
        failures = 0
        for index, source in enumerate(sources):
            batch_args.report = args.report if index == 0 else None
            batch_args.save_preset = args.save_preset if index == 0 else None
            batch_args.compare = None
            batch_args.histogram = None
            failures += run_one(
                source,
                resolve_batch_output(args.output, source, root=input_path),
                steps, batch_args, preset,
            )
        print(f"Batch complete: {len(sources) - failures}/{len(sources)} succeeded")
        return 1 if failures else 0

    analysis_only = (args.info or args.analyze_roi or args.hist_stats or args.histogram
                     or args.noise_stats or args.ela_stats or args.clone_stats
                     or args.compression_stats or args.ghost_stats)
    # Combining frames is a transformation in its own right, so it counts as
    # work even with no filter chain behind it
    if not steps and not preset and not analysis_only and args.frames <= 0:
        parser.error("no filters specified (try --list-filters, or --info)")

    output_path = Path(args.output) if args.output else None
    return run_one(input_path, output_path, steps, args, preset)


if __name__ == '__main__':
    sys.exit(main())
