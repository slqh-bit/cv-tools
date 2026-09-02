"""
Command-line interface for cv-tools.

Filters are applied in the order they appear on the command line, so
``--brightness 20 --clahe clip=3.0`` and ``--clahe clip=3.0 --brightness 20``
produce different results, exactly like reordering steps in a filter chain.

Usage:
    cv-tools input.jpg --clahe clip=2.0 tile=8x8 -o output.jpg
"""

import argparse
import inspect
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .core.loader import ImageLoader, save_image
from .core.pipeline import Pipeline
from .core.report import ReportGenerator
from .core.video import DEFAULT_CODECS, VideoWriter
from .filters.aspect_ratio import PIXEL_ASPECT_RATIOS
from .filters.analysis import (
    ANALYSIS_REGISTRY,
    list_analyses,
    report_lines,
    resolve_analysis,
    run_analysis,
)
from .filters.curves import curve_from_string
from .filters.perspective_correction import KNOWN_RATIOS
from .filters.frame_averaging import (
    average_frames,
    integrate_frames,
    median_frames,
    sharpest_frames,
)
from .filters.stabilise import (
    DEFAULT_MIN_CONFIDENCE,
    METHODS as STABILISE_METHODS,
    MOTION_MODELS,
    align_frames,
    alignment_report,
)
from .filters.histogram import dynamic_range_used, histogram_stats, render_histogram
from .filters.registry import resolve_filter, list_filters, filter_description
from .filters.super_resolution import super_resolve, super_resolve_report
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
        description='Modular forensic image enhancement toolkit.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  cv-tools in.jpg --clahe clip=2.0 tile=8x8 -o out.jpg\n"
            "  cv-tools in.jpg --roi 100,100,300,200 -o crop.jpg\n"
            "  cv-tools in.jpg --brightness 20 --contrast 1.5 -o out.jpg\n"
            "  cv-tools in.jpg --levels 20,1.0,220 --report report.md -o out.jpg\n"
            "  cv-tools frames/ --clahe --batch -o enhanced/\n"
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

    # ---- Measurement and annotation ----
    # The calibration is a modifier rather than a per-measurement parameter
    # because a scale belongs to an image plane, not to one measurement: every
    # measurement taken in that plane shares it, and two in the same plane
    # disagreeing about the scale would be a defect, not a feature.
    measure_group = parser.add_argument_group('measurement and annotation')
    measure_group.add_argument('--scale-ref', metavar='X1,Y1,X2,Y2',
                               help='The two ends of something of known length, '
                                    'calibrating --measure, --measure-area and '
                                    '--scale-bar. Correct perspective first: a '
                                    'scale is valid only in its own plane')
    measure_group.add_argument('--scale-length', type=float, metavar='LENGTH',
                               help='True length of --scale-ref, e.g. 520 for an '
                                    'EU number plate')
    measure_group.add_argument('--scale-unit', default='mm', metavar='UNIT',
                               help='Unit of --scale-length (default: mm)')
    measure_group.add_argument('--measure', metavar='X1,Y1,X2,Y2',
                               action=ChainAction,
                               help='Measure between two points and draw the '
                                    'dimension line. Uncalibrated, the label is '
                                    'in pixels')
    measure_group.add_argument('--measure-area', metavar='X1,Y1,X2,Y2,...',
                               action=ChainAction,
                               help='Measure the area of a polygon of three or '
                                    'more vertices, and draw it labelled')
    measure_group.add_argument('--scale-bar', nargs='?', type=float, const=100.0,
                               metavar='LENGTH', action=ChainAction,
                               help='Draw a calibrated scale bar of LENGTH units '
                                    '(default: 100); needs --scale-ref')
    measure_group.add_argument('--scale-bar-position', default='bottom_right',
                               choices=['bottom_right', 'bottom_left',
                                        'top_right', 'top_left'],
                               help='Which corner --scale-bar sits in '
                                    '(default: bottom_right)')
    measure_group.add_argument('--arrow', nargs='*', metavar='KEY=VALUE',
                               action=ChainAction,
                               help='Draw an arrow. Params: start, end (X,Y), '
                                    'label, thickness, tip_length')
    measure_group.add_argument('--text', nargs='*', metavar='KEY=VALUE',
                               action=ChainAction,
                               help='Draw a text label. Params: text, position '
                                    '(X,Y), font_scale, thickness, background')
    measure_group.add_argument('--shape', nargs='*', metavar='KEY=VALUE',
                               action=ChainAction,
                               help='Draw a shape. Params: shape (rectangle, '
                                    'circle, ellipse, line, polygon), points, label')

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
    # One flag per registered analysis, so a report added to the registry is
    # reachable from the command line without this file being edited - the
    # same property the GUI's Analysis tab and the dashboard already have
    for spec in ANALYSIS_REGISTRY.values():
        if spec.cli_value is None:
            out.add_argument(spec.cli_flag, action='store_true', help=spec.cli_help())
            continue

        # A bare value is shorthand for one parameter, and the parameter's own
        # default is what the flag means when given without one
        default = inspect.signature(spec.fn).parameters[spec.cli_value].default
        out.add_argument(spec.cli_flag, nargs='?', type=type(default), const=default,
                         metavar=spec.cli_value.upper(),
                         help=f'{spec.cli_help()} '
                              f'(default {spec.cli_value} {default})')
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
                     help='Combine N frames into the source image: from a video '
                          'starting at --frame, or from a directory of stills. '
                          'Averaging only reduces noise where the scene holds '
                          'still - use median where it does not')
    out.add_argument('--frame-step', type=int, default=1, metavar='N',
                     help='Stride between the frames gathered by --frames (default: 1)')
    out.add_argument('--frame-method', default='mean',
                     choices=['mean', 'median', 'integrate', 'sharpest',
                              'superres'],
                     help='How --frames are combined: mean denoises, median removes moving '
                          'objects, integrate brightens dark footage, sharpest averages only '
                          'the best-focused half, superres reconstructs a larger image from '
                          'their sub-pixel offsets (default: mean)')
    out.add_argument('--sr-scale', type=float, default=2.0, metavar='FACTOR',
                     help='Magnification for --frame-method superres (default: 2.0)')
    out.add_argument('--sr-sharpen', type=float, default=0.6, metavar='AMOUNT',
                     help='Unsharp amount applied after reconstruction, '
                          '0 to disable (default: 0.6)')
    out.add_argument('--sr-max-shift', type=float, default=8.0, metavar='PIXELS',
                     help='Frames displaced further than this are dropped as '
                          'mis-registered rather than smeared in (default: 8.0)')
    out.add_argument('--stabilise', '--stabilize', nargs='?',
                     const='euclidean', choices=sorted(MOTION_MODELS),
                     metavar='MODEL',
                     help='Align --frames before combining them. Every method '
                          'assumes the frames line up and none can tell that '
                          'they do not. Pick the least freedom the camera had: '
                          'translation for a shaky mount, euclidean for '
                          'handheld (default), homography for a pan across a '
                          'flat scene. The result is cropped to the area every '
                          'frame covers')
    out.add_argument('--stabilise-method', '--stabilize-method', default='auto',
                     choices=list(STABILISE_METHODS),
                     help='features survives large motion, ecc is sub-pixel but '
                          'local, auto seeds ecc from features (default: auto)')
    out.add_argument('--stabilise-reference', '--stabilize-reference', type=int,
                     default=0, metavar='N',
                     help='Index within the gathered frames that the others are '
                          'aligned to (default: 0)')
    out.add_argument('--stabilise-min-confidence', '--stabilize-min-confidence',
                     type=float, default=DEFAULT_MIN_CONFIDENCE, metavar='C',
                     help=f'Frames matching below this are left out rather than '
                          f'warped on a guess (default: {DEFAULT_MIN_CONFIDENCE})')
    out.add_argument('--video', action='store_true',
                     help='Apply the chain to every frame of a range and write '
                          'video, instead of reducing the input to one still. '
                          'Needs a video input and an output file')
    out.add_argument('--video-frames', type=int, default=0, metavar='N',
                     help='How many frames --video processes, from --frame '
                          'onward (default: to the end)')
    out.add_argument('--fps', type=float, default=0.0, metavar='RATE',
                     help="Output frame rate for --video (default: the "
                          "source's, divided by --frame-step)")
    out.add_argument('--codec', metavar='FOURCC',
                     help='Video codec, e.g. FFV1 (lossless), MJPG, mp4v. '
                          'Default depends on the output container: '
                          + ', '.join(f'{ext} -> {code}'
                                      for ext, code in DEFAULT_CODECS.items()))
    out.add_argument('--batch', action='store_true',
                     help='Process every image in the input directory')
    out.add_argument('--recursive', action='store_true',
                     help='With --batch, also descend into subdirectories')
    out.add_argument('--quality', type=int, default=95, metavar='Q',
                     help='JPEG quality 1-100 (default: 95)')
    out.add_argument('--list-filters', action='store_true',
                     help='List registered filters and exit')
    out.add_argument('--list-analyses', action='store_true',
                     help='List the analysis reports and exit')
    out.add_argument('-v', '--verbose', action='store_true',
                     help='Print each step as it is applied')

    return parser


def expand_point_params(
    params: Dict[str, Any],
    keys: Tuple[str, ...],
) -> Dict[str, Any]:
    """
    Turn ``key=X,Y`` values into coordinate lists, in place.

    ``parse_value`` leaves "352,408" as text, since a comma means nothing to it.
    Which keys hold coordinates is filter knowledge, so the caller names them.

    Args:
        params: Parsed key=value parameters
        keys: The parameter names that hold coordinates

    Returns:
        The same dict, with those values converted

    Raises:
        ValueError: If a named value is not a list of numbers
    """
    for key in keys:
        value = params.get(key)
        if not isinstance(value, str) or ',' not in value:
            continue
        parts = [part.strip() for part in value.split(',')]
        try:
            params[key] = [float(part) for part in parts]
        except ValueError:
            raise ValueError(
                f"{key} should be comma-separated numbers, got {value!r}"
            ) from None
    return params


def translate_measurement(
    dest: str,
    value: Any,
    scale_ref: Optional[str],
    scale_length: Optional[float],
    scale_unit: str,
    scale_bar_position: str,
) -> Tuple[str, Dict[str, Any]]:
    """
    Build a measurement step, attaching the shared calibration if one was given.

    Raises:
        ValueError: If the flag's coordinates are malformed, if the calibration
            is only half given, or if a scale bar was asked for without one
    """
    calibration: Dict[str, Any] = {}
    if scale_ref is not None or scale_length is not None:
        if scale_ref is None or scale_length is None:
            raise ValueError(
                "a calibration needs both --scale-ref and --scale-length")
        x1, y1, x2, y2 = parse_float_list(scale_ref, 4)
        calibration = {
            'reference_a': [x1, y1],
            'reference_b': [x2, y2],
            'reference_length': scale_length,
            'unit_name': scale_unit,
        }

    if dest == 'measure':
        x1, y1, x2, y2 = parse_float_list(value, 4)
        return 'measure', {'point_a': [x1, y1], 'point_b': [x2, y2],
                           **calibration}

    if dest == 'measure_area':
        parts = [part.strip() for part in str(value).split(',')]
        if len(parts) < 6 or len(parts) % 2 != 0:
            raise ValueError(
                f"an area needs at least 3 X,Y vertices, got {len(parts)} values")
        try:
            flat = [float(part) for part in parts]
        except ValueError:
            raise ValueError(f"expected numbers in: {value!r}") from None
        return 'measure_area', {
            'points': [[flat[i], flat[i + 1]] for i in range(0, len(flat), 2)],
            **calibration,
        }

    # scale_bar
    if not calibration:
        raise ValueError(
            "--scale-bar needs --scale-ref and --scale-length; a bar with no "
            "calibration would be a ruler with no units")
    return 'scale_bar', {
        'length_units': float(value if value is not None else 100.0),
        'position': scale_bar_position,
        **calibration,
    }


def translate_step(
    dest: str,
    value: Any,
    interpolation: str = 'auto',
    blur_first: float = 0.0,
    perspective_ratio: Optional[str] = None,
    redact_method: str = 'fill',
    scale_ref: Optional[str] = None,
    scale_length: Optional[float] = None,
    scale_unit: str = 'mm',
    scale_bar_position: str = 'bottom_right',
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
        scale_ref: ``X1,Y1,X2,Y2`` spanning a reference of known length
        scale_length: That reference's true length
        scale_unit: Unit of scale_length
        scale_bar_position: Which corner a scale bar sits in

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
        return 'measure_3d', expand_point_params(
            params, ('base', 'top', 'reference_base', 'reference_top',
                     'vertical_point', 'horizon'))

    # ---- Measurement and annotation ----
    if dest in ('measure', 'measure_area', 'scale_bar'):
        return translate_measurement(
            dest, value, scale_ref, scale_length, scale_unit,
            scale_bar_position,
        )

    if dest == 'arrow':
        return 'arrow', expand_point_params(parse_kv(value or []),
                                            ('start', 'end'))

    if dest == 'text':
        params = expand_point_params(parse_kv(value or []), ('position',))
        if 'text' not in params:
            raise ValueError("--text needs text=<label>, e.g. text=Exhibit_A")
        # parse_value types a numeric label as a number; the filter wants a string
        params['text'] = str(params['text'])
        return 'text', params

    if dest == 'shape':
        params = expand_point_params(parse_kv(value or []), ('points',))
        if 'shape' not in params:
            raise ValueError(
                "--shape needs shape=<rectangle|circle|ellipse|line|polygon>")
        if 'points' not in params:
            raise ValueError("--shape needs points=X1,Y1,X2,Y2")
        return 'shape', params

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


def stabilise_frames(
    frames: List[np.ndarray],
    args: argparse.Namespace,
) -> Tuple[List[np.ndarray], Optional[Dict[str, Any]]]:
    """
    Align a frame stack, if the run asked for it.

    Every combination method assumes the frames line up, and none of them can
    tell that they do not - averaging a moving camera just returns something
    softer. So this runs before the combination, and says what it did.

    Returns:
        (frames to combine, the alignment report or None if not stabilising)
    """
    if not args.stabilise:
        return frames, None

    aligned, results = align_frames(
        frames,
        reference=args.stabilise_reference,
        model=args.stabilise,
        method=args.stabilise_method,
        min_confidence=args.stabilise_min_confidence,
    )
    report = alignment_report(results)

    if args.verbose:
        print(f"  aligned {report['aligned']}/{report['frames']} frames "
              f"({args.stabilise}, {args.stabilise_method}), "
              f"largest motion {report['max_shift_pixels']}px, "
              f"mean confidence {report['mean_confidence']:.2f}",
              file=sys.stderr)
        for record in report['per_frame']:
            if record['note']:
                print(f"    frame {record['index']}: {record['note']}",
                      file=sys.stderr)
    elif report['dropped']:
        # Quiet runs still need to hear this: frames silently missing from an
        # average is exactly the failure stabilising is meant to prevent
        print(f"note: {report['dropped']} of {report['frames']} frames could "
              f"not be aligned and were left out", file=sys.stderr)

    return aligned, report


def combine_frames(
    frames: List[np.ndarray],
    method: str,
    args: Optional[argparse.Namespace] = None,
) -> np.ndarray:
    """
    Reduce a sequence of video frames to one source image.

    Args:
        frames: The gathered frames
        method: One of the --frame-method choices
        args: The parsed arguments, for the methods that take parameters of
            their own. Optional so the simple methods stay callable with two.

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
    if method == 'superres':
        scale = getattr(args, 'sr_scale', 2.0)
        sharpen = getattr(args, 'sr_sharpen', 0.6)
        max_shift = getattr(args, 'sr_max_shift', 8.0)
        report_super_resolution(frames, args, max_shift)
        return super_resolve(frames, scale=scale, sharpen=sharpen,
                             max_shift=max_shift)
    raise ValueError(f"Unknown frame method: {method}")


def report_super_resolution(
    frames: List[np.ndarray],
    args: Optional[argparse.Namespace],
    max_shift: float,
) -> Dict[str, Any]:
    """
    Say whether the sequence carries the motion reconstruction needs.

    Reconstruction without sub-pixel motion quietly degrades to an interpolated
    upscale of averaged frames - which looks like more detail without being any,
    and is the one outcome this must not produce silently. So the measurement
    goes to stderr either way, and a sequence that cannot support it says so.
    """
    report = super_resolve_report(frames, max_shift=max_shift)
    verbose = getattr(args, 'verbose', False)

    if not report['usable']:
        print(f"warning: these {report['frames']} frames carry little sub-pixel "
              f"motion ({report['frames_with_subpixel_motion']} of "
              f"{report['frames_within_max_shift']} within range have any), so "
              f"the result may be no better than --upscale. Compare the two "
              f"before relying on it.", file=sys.stderr)
    elif verbose:
        print(f"  {report['frames_within_max_shift']}/{report['frames']} frames "
              f"within {max_shift}px, "
              f"{report['frames_with_subpixel_motion']} with sub-pixel motion, "
              f"largest offset {report['max_shift_px']:.2f}px",
              file=sys.stderr)

    return report


def print_analysis(
    name: str,
    image: Optional[np.ndarray] = None,
    path: Optional[Path] = None,
    params: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Run one registered analysis and print its report.

    The header, the rows and the caveat all come from ``filters.analysis``, so
    this prints exactly what the GUI and the dashboard show.

    Args:
        name: Registry name of the analysis
        image: Image to measure, for analyses that read pixels
        path: Source file, for analyses that read the container
        params: Extra keyword arguments for the analysis function
    """
    spec = resolve_analysis(name)
    report = run_analysis(spec, image=image, path=path, params=params)
    for line in report_lines(spec, report):
        print(line)


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


def _combine_stills(directory: Path,
                    args: argparse.Namespace) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Combine a directory of stills into one source image.

    The video path takes frames from a container; this takes them from a
    folder, which is how a camera's exported snapshots and most disclosed
    evidence actually arrive. Frames must share a shape - a folder holding two
    cameras' output is a mistake worth reporting rather than resizing away.

    Raises:
        ValueError: If too few images are found, or they disagree on size
    """
    paths = ImageLoader.find_images(directory, recursive=args.recursive)
    selected = paths[args.frame::max(1, args.frame_step)][:args.frames]
    if len(selected) < 2:
        raise ValueError(
            f"--frames needs at least 2 images, found {len(selected)} in "
            f"{directory}")

    frames, metadata = [], {}
    for index, source in enumerate(selected):
        with ImageLoader(source) as loader:
            frame = loader.load()
            if index == 0:
                metadata = dict(loader.metadata)
        if frames and frame.shape != frames[0].shape:
            raise ValueError(
                f"{source.name} is {frame.shape[1]}x{frame.shape[0]} but "
                f"{selected[0].name} is {frames[0].shape[1]}x{frames[0].shape[0]}; "
                f"frames must share a size to be combined")
        frames.append(frame)

    frames, alignment = stabilise_frames(frames, args)
    image = combine_frames(frames, args.frame_method, args)
    metadata['filename'] = f'{len(frames)} frames from {directory.name}'
    metadata['combined_from'] = [source.name for source in selected]
    metadata['frame_method'] = args.frame_method
    if alignment is not None:
        metadata['alignment'] = alignment
    if args.verbose:
        print(f"Combined {len(frames)} stills with '{args.frame_method}'",
              file=sys.stderr)
    return image, metadata


def run_one(
    path: Path,
    output_path: Optional[Path],
    steps: List[Tuple[str, Dict[str, Any]]],
    args: argparse.Namespace,
    preset: Optional[Dict[str, Any]],
) -> int:
    """Process a single input file. Returns a process exit code."""
    if args.video:
        return _process_video(path, output_path, steps, args, preset)

    try:
        if args.frames > 0 and path.is_dir():
            # A folder of exported stills is how CCTV evidence usually
            # arrives, and it is the case frame integration exists for. Until
            # this branch, --frames took video only, so the one format most
            # likely to be handed over could not be integrated at all.
            image, metadata = _combine_stills(path, args)
        else:
            image, metadata = _load_one(path, args)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.info:
        print_metadata(metadata)

    if args.verbose:
        print(f"Processing {path.name} ({image.shape[1]}x{image.shape[0]})", file=sys.stderr)

    return _process_source(image, metadata, path, output_path, steps, args, preset)


def _load_one(path: Path,
              args: argparse.Namespace) -> Tuple[np.ndarray, Dict[str, Any]]:
    """One still, one video frame, or several video frames combined."""
    with ImageLoader(path) as loader:
        if args.frames > 0:
            if not loader.is_video:
                raise ValueError(
                    f"--frames needs a video or a directory of stills, "
                    f"got: {path.name}")
            frames = loader.load_frames(args.frames, start=args.frame,
                                        step=args.frame_step)
            frames, alignment = stabilise_frames(frames, args)
            image = combine_frames(frames, args.frame_method, args)
            if args.verbose:
                print(f"Combined {len(frames)} frames with '{args.frame_method}'",
                      file=sys.stderr)
            metadata = dict(loader.metadata)
            if alignment is not None:
                metadata['alignment'] = alignment
            return image, metadata
        else:
            image = loader.load(args.frame if loader.is_video else None)
        return image, loader.metadata


def _process_video(
    path: Path,
    output_path: Optional[Path],
    steps: List[Tuple[str, Dict[str, Any]]],
    args: argparse.Namespace,
    preset: Optional[Dict[str, Any]],
) -> int:
    """
    Run the chain over a range of frames and write the result as video.

    One frame is held at a time rather than the whole range, so this works on
    footage longer than memory. The chain is rebuilt per frame, which is what
    keeps every frame's processing identical and independently described in the
    report.
    """
    if output_path is None:
        print("error: --video needs an output file, e.g. -o processed.avi",
              file=sys.stderr)
        return 1

    try:
        with ImageLoader(path) as loader:
            if not loader.is_video:
                raise ValueError(
                    f"--video needs a video input, got: {path.name}")

            total = loader.get_video_frame_count()
            step = max(1, args.frame_step)
            wanted = args.video_frames if args.video_frames > 0 else total
            indices = list(range(args.frame, total, step))[:wanted]
            if not indices:
                raise ValueError(
                    f"No frames selected: the video has {total} frames and "
                    f"--frame is {args.frame}")

            # Dropping frames drops the playback rate with them, so a stride of
            # 5 over 25fps footage plays back at 5fps and keeps real time
            source_fps = loader.get_video_fps()
            fps = args.fps or (source_fps / step if source_fps > 0 else 25.0)

            writer = VideoWriter(output_path, fps=fps, codec=args.codec)
            if not writer.lossless:
                # The toolkit reads compression history elsewhere; adding a
                # generation of it to an exhibit should be a decision, not a
                # default that happened
                print(f"note: '{writer.codec}' is lossy, so the output carries "
                      f"compression this input did not. Write .avi for "
                      f"lossless FFV1 if the result is evidence.",
                      file=sys.stderr)

            pipeline = None
            with writer:
                for position, index in enumerate(indices):
                    frame = loader.goto_frame(index)
                    pipeline = process_image(
                        frame, steps, preset=preset,
                        verbose=args.verbose and position == 0)
                    writer.write(pipeline.current)
                    if args.verbose and position and position % 25 == 0:
                        print(f"  {position}/{len(indices)} frames",
                              file=sys.stderr)

            metadata = dict(loader.metadata)
            metadata['frames_written'] = writer.frames_written
            metadata['frame_range'] = f'{indices[0]}..{indices[-1]} step {step}'
            metadata['output_codec'] = writer.codec
            metadata['output_lossless'] = writer.lossless
            metadata['output_fps'] = round(fps, 3)

    except (FileNotFoundError, ValueError, RuntimeError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Saved: {output_path} ({writer.frames_written} frames, "
          f"{writer.codec}, {fps:.3g} fps)")

    if args.report and pipeline is not None:
        try:
            report = ReportGenerator(pipeline.generate_report(), metadata,
                                     describe=filter_description)
            fmt = REPORT_FORMATS.get(Path(args.report).suffix.lower(), 'markdown')
            report.save(args.report, format=fmt)
            print(f"Saved report: {args.report}")
        except OSError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

    if args.save_preset and pipeline is not None:
        try:
            pipeline.save_preset(args.save_preset)
            print(f"Saved preset: {args.save_preset}")
        except OSError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

    return 0


def _process_source(
    image: np.ndarray,
    metadata: Dict[str, Any],
    path: Path,
    output_path: Optional[Path],
    steps: List[Tuple[str, Dict[str, Any]]],
    args: argparse.Namespace,
    preset: Optional[Dict[str, Any]],
) -> int:
    """Run the chain, the analyses and the outputs over one loaded image."""
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

    # Reports that read the container - metadata, and the quantisation tables
    # behind --compression-stats - are handed the source path, so they
    # describe the input rather than whatever the chain produced
    for name, spec in ANALYSIS_REGISTRY.items():
        value = getattr(args, spec.cli_dest)
        if not value:
            continue
        params = ({spec.cli_value: value}
                  if spec.cli_value is not None and value is not True else {})
        print_analysis(name, result if spec.needs_image else None,
                       path=path, params=params)

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
            report = ReportGenerator(pipeline.generate_report(), metadata,
                                     describe=filter_description)
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

    if args.list_analyses:
        print("Analysis reports:")
        for name, description in list_analyses():
            print(f"  {ANALYSIS_REGISTRY[name].cli_flag:22s} {description}")
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
                scale_ref=args.scale_ref,
                scale_length=args.scale_length,
                scale_unit=args.scale_unit,
                scale_bar_position=args.scale_bar_position,
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
                     or any(getattr(args, spec.cli_dest)
                            for spec in ANALYSIS_REGISTRY.values()))
    # Combining frames is a transformation in its own right, so it counts as
    # work even with no filter chain behind it. So is writing video: extracting
    # a frame range losslessly is a job, and refusing it because no filter was
    # named would be arbitrary.
    if (not steps and not preset and not analysis_only
            and args.frames <= 0 and not args.video):
        parser.error("no filters specified (try --list-filters, or --info)")

    output_path = Path(args.output) if args.output else None
    return run_one(input_path, output_path, steps, args, preset)


if __name__ == '__main__':
    sys.exit(main())
