"""
What each filter specifically promises.

The harness checks what every filter owes: a uint8 image, no NaN, the same
answer twice. That catches a crash, not a lie - a sharpen that quietly blurs
passes all three. These are the promises worth the deep dive: measured on the
image the filter is aimed at, with a number attached rather than an opinion.

Each check takes the corpus and returns (ok, detail). Detail is written into
the result file whether it passed or failed, because the number is the point.
"""

import tempfile
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import cv2
import numpy as np

from src.filters import (
    CLAHE_COLOR_MODES,
    adjust_temperature,
    auto_canny,
    canny_edges,
    correct_pixel_aspect,
    fit_to_aspect,
    noise_map,
    auto_contrast,
    auto_levels,
    invert_channel,
    invert_luminance,
    solarize,
    gaussian_blur,
    median_filter,
    sobel_edges,
    crop,
    deblock,
    detect_periodic_peaks,
    fft_filter,
    flip,
    invert,
    remove_periodic_noise,
    resize,
    rotate,
    blockiness_score,
    check_timestamps,
    detect_editing_software,
    ela_stats,
    error_level_analysis,
    estimate_jpeg_quality,
    metadata_report,
    noise_report,
    calibrate_from_chessboard,
    load_calibration,
    save_calibration,
    undistort,
    undistort_with_file,
    COLOR_SPACES,
    DESATURATE_METHODS,
    FISHEYE_BORDER_MODES,
    WHITE_BALANCE_METHODS,
    adjust_saturation,
    auto_white_balance,
    correct_fisheye,
    desaturate,
    extract_bit_plane,
    extract_component,
    measure_height,
    white_balance_from_patch,
    adjust_contrast_brightness,
    adjust_levels,
    apply_clahe,
    apply_curve,
    correct_barrel_distortion,
    correct_perspective,
    deblur_defocus,
    deblur_motion,
    detect_copy_move,
    edge_density,
    estimate_noise,
    estimate_straightness,
    extract_roi,
    ghost_report,
    ghost_sweep,
    GHOST_QUALITIES,
    histogram_equalization,
    is_reversible,
    local_contrast,
    nl_means_denoise,
    redact_region,
    unsharp_mask,
    upscale,
    verify_redaction,
    ROI,
)

Check = Callable[[Dict[str, np.ndarray]], Tuple[bool, str]]


def _gray(image: np.ndarray) -> np.ndarray:
    # RGB2GRAY, matching every _to_gray in src/filters. The corpus goes
    # through ImageLoader, so these arrays are RGB; BGR2GRAY would weight the
    # channels backwards and quietly change every luminance number here.
    return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if image.ndim == 3 else image


def _local_contrast_score(image: np.ndarray, window: int = 15) -> float:
    """Mean local standard deviation - what CLAHE and clarity claim to raise."""
    gray = _gray(image).astype(np.float32)
    mean = cv2.blur(gray, (window, window))
    sq = cv2.blur(gray * gray, (window, window))
    return float(np.sqrt(np.maximum(sq - mean * mean, 0)).mean())


def _high_frequency_energy(image: np.ndarray) -> float:
    """Laplacian variance - the standard focus / acutance proxy."""
    return float(cv2.Laplacian(_gray(image), cv2.CV_64F).var())


# ---- Adjust ---------------------------------------------------------------

def check_clahe(corpus) -> List[Tuple[str, bool, str]]:
    dark = corpus['cctv/darkest.jpg']
    out = []

    before = _local_contrast_score(dark)
    after = _local_contrast_score(apply_clahe(dark, clip_limit=2.0))
    out.append(('raises local contrast on the darkest frame', after > before,
                f'{before:.2f} -> {after:.2f} mean local sigma'))

    # The clip limit is the whole point of CLAHE over plain equalization: it
    # is what stops noise in a flat region being amplified without bound
    scores = [_local_contrast_score(apply_clahe(dark, clip_limit=c))
              for c in (1.0, 2.0, 4.0, 8.0)]
    out.append(('clip_limit raises contrast monotonically',
                all(b >= a - 0.01 for a, b in zip(scores, scores[1:])),
                ' -> '.join(f'{s:.2f}' for s in scores) + ' for clip 1/2/4/8'))

    # A CCTV frame is mostly noise in the shadows; CLAHE must not turn that
    # into a wall of grain
    noise_before = estimate_noise(dark)
    noise_after = estimate_noise(apply_clahe(dark, clip_limit=2.0))
    out.append(('does not multiply shadow noise beyond 3x',
                noise_after < noise_before * 3,
                f'sigma {noise_before:.2f} -> {noise_after:.2f}'))

    # Every mode this filter says it implements, from its own constant rather
    # than a list written here - the two disagreeing is what started this
    for mode in CLAHE_COLOR_MODES:
        result = apply_clahe(dark, color_mode=mode)
        out.append((f'colour mode {mode} returns a usable image',
                    result.dtype == np.uint8 and float(result.std()) > 1,
                    f'std {float(result.std()):.1f}'))
    return out


def check_levels(corpus) -> List[Tuple[str, bool, str]]:
    frame = corpus['cctv/flattest.jpg']
    out = []

    identity = adjust_levels(frame)
    out.append(('defaults are an exact identity',
                np.array_equal(identity, frame),
                'black 0, white 255, gamma 1 changes nothing'))

    stretched = adjust_levels(frame, black_point=40, white_point=200)
    out.append(('a stretch widens the dynamic range',
                float(stretched.std()) > float(frame.std()),
                f'std {float(frame.std()):.1f} -> {float(stretched.std()):.1f}'))

    # Everything at or below the black point has to land on 0, or the black
    # point does not mean what the panel says it means. Measured on a ramp
    # rather than the frame: levels works per channel, so a pixel whose
    # luminance is under the point can still have a channel above it.
    ramp = np.tile(np.arange(256, dtype=np.uint8), (8, 1))
    ramp = cv2.cvtColor(ramp, cv2.COLOR_GRAY2BGR)
    mapped = adjust_levels(ramp, black_point=64, white_point=192)[0, :, 0]
    out.append(('every value at or below the black point maps to 0',
                bool((mapped[:65] == 0).all()),
                f'ramp values 0-64 map to {sorted(set(mapped[:65].tolist()))}'))
    out.append(('every value at or above the white point maps to 255',
                bool((mapped[192:] == 255).all()),
                f'ramp values 192-255 map to {sorted(set(mapped[192:].tolist()))}'))

    dark = adjust_levels(frame, gamma=0.5)
    bright = adjust_levels(frame, gamma=2.0)
    out.append(('gamma below 1 darkens and above 1 brightens',
                float(dark.mean()) < float(frame.mean()) < float(bright.mean()),
                f'{float(dark.mean()):.0f} < {float(frame.mean()):.0f} '
                f'< {float(bright.mean()):.0f}'))
    return out


def check_contrast_brightness(corpus) -> List[Tuple[str, bool, str]]:
    frame = corpus['cctv/flattest.jpg']
    out = []

    out.append(('defaults are an identity',
                np.array_equal(adjust_contrast_brightness(frame), frame),
                'contrast 1.0, brightness 0'))

    lifted = adjust_contrast_brightness(frame, brightness=40)
    out.append(('brightness lifts the mean by about what was asked',
                abs((float(lifted.mean()) - float(frame.mean())) - 40) < 12,
                f'asked +40, got {float(lifted.mean()) - float(frame.mean()):+.1f} '
                '(clipping accounts for the rest)'))

    harder = adjust_contrast_brightness(frame, contrast=1.6)
    out.append(('contrast above 1 widens the spread',
                float(harder.std()) > float(frame.std()),
                f'std {float(frame.std()):.1f} -> {float(harder.std()):.1f}'))
    return out


def check_curves(corpus) -> List[Tuple[str, bool, str]]:
    frame = corpus['cctv/darkest.jpg']
    out = []

    straight = apply_curve(frame, points=[[0, 0], [255, 255]])
    out.append(('a straight line is an identity',
                np.array_equal(straight, frame),
                'the 0,0 - 255,255 curve changes nothing'))

    lifted = apply_curve(frame, preset='lift_shadows')
    shadows_before = float(_gray(frame)[_gray(frame) < 64].mean())
    shadows_after = float(_gray(lifted)[_gray(frame) < 64].mean())
    out.append(('lift_shadows raises the shadows',
                shadows_after > shadows_before,
                f'mean of pixels under 64: {shadows_before:.1f} -> {shadows_after:.1f}'))

    # A curve is a lookup table, so it cannot invert the order of two tones
    # unless the curve itself does
    tone_in = np.arange(256, dtype=np.uint8).reshape(1, 256)
    tone_out = apply_curve(cv2.cvtColor(tone_in, cv2.COLOR_GRAY2BGR),
                           preset='lift_shadows')[0, :, 0]
    out.append(('a monotonic preset stays monotonic',
                bool((np.diff(tone_out.astype(int)) >= 0).all()),
                'no tone reversal across the 0-255 ramp'))
    return out


def check_histeq(corpus) -> List[Tuple[str, bool, str]]:
    frame = corpus['cctv/flattest.jpg']
    out = []
    result = histogram_equalization(frame)

    before = float(np.percentile(_gray(frame), 99) - np.percentile(_gray(frame), 1))
    after = float(np.percentile(_gray(result), 99) - np.percentile(_gray(result), 1))
    out.append(('spreads the histogram wider than it found it',
                after >= before,
                f'1-99 percentile span {before:.0f} -> {after:.0f}'))

    noise_before, noise_after = estimate_noise(frame), estimate_noise(result)
    out.append(('global equalization amplifies noise (expected, documented)',
                True,
                f'sigma {noise_before:.2f} -> {noise_after:.2f} - this is why '
                'CLAHE exists'))
    return out


# ---- Enhance --------------------------------------------------------------

def check_sharpen(corpus) -> List[Tuple[str, bool, str]]:
    frame = corpus['cctv/softest.jpg']
    out = []

    before = _high_frequency_energy(frame)
    after = _high_frequency_energy(unsharp_mask(frame, amount=1.0))
    out.append(('raises high-frequency energy on the softest frame',
                after > before,
                f'Laplacian variance {before:.0f} -> {after:.0f}'))

    scores = [_high_frequency_energy(unsharp_mask(frame, amount=a))
              for a in (0.5, 1.0, 2.0)]
    out.append(('amount raises it monotonically',
                all(b > a for a, b in zip(scores, scores[1:])),
                ' -> '.join(f'{s:.0f}' for s in scores) + ' for amount 0.5/1/2'))

    heavy = unsharp_mask(frame, amount=2.5)
    clipped = float(((heavy == 0) | (heavy == 255)).mean() * 100)
    out.append(('heavy sharpening does not clip most of the frame',
                clipped < 15,
                f'{clipped:.1f}% of pixels driven to 0 or 255 at amount 2.5'))
    return out


def check_nl_means(corpus) -> List[Tuple[str, bool, str]]:
    frame = corpus['cctv/darkest.jpg']
    out = []

    before = estimate_noise(frame)
    result = nl_means_denoise(frame, h=10)
    after = estimate_noise(result)
    out.append(('lowers the measured noise',
                after < before,
                f'sigma {before:.2f} -> {after:.2f}'))

    # Denoising that also erases the edges has not denoised, it has blurred
    edges_before = edge_density(cv2.Canny(_gray(frame), 60, 160))
    edges_after = edge_density(cv2.Canny(_gray(result), 60, 160))
    out.append(('keeps most of the edge structure',
                edges_after > edges_before * 0.4,
                f'edge density {edges_before:.4f} -> {edges_after:.4f}'))

    strengths = [estimate_noise(nl_means_denoise(frame, h=h)) for h in (3, 10, 20)]
    out.append(('h lowers noise monotonically',
                all(b <= a + 0.05 for a, b in zip(strengths, strengths[1:])),
                ' -> '.join(f'{s:.2f}' for s in strengths) + ' for h 3/10/20'))
    return out


def check_local_contrast(corpus) -> List[Tuple[str, bool, str]]:
    frame = corpus['cctv/flattest.jpg']
    out = []

    before = _local_contrast_score(frame, window=31)
    after = _local_contrast_score(local_contrast(frame, strength=0.5), window=31)
    out.append(('raises large-scale local contrast', after > before,
                f'{before:.2f} -> {after:.2f} mean local sigma at 31px'))

    scores = [_local_contrast_score(local_contrast(frame, strength=s), window=31)
              for s in (0.2, 0.5, 1.0)]
    # Strictly rising end to end, not merely non-decreasing: a filter that
    # ignored `strength` produced three identical numbers and passed the
    # non-decreasing form of this check.
    out.append(('strength raises it, and the ends differ materially',
                all(b >= a - 0.01 for a, b in zip(scores, scores[1:]))
                and scores[-1] > scores[0] * 1.05,
                ' -> '.join(f'{s:.2f}' for s in scores)
                + f' for strength 0.2/0.5/1.0 ({scores[-1] / scores[0]:.2f}x end to end)'))

    # Clarity that eats the highlights has not added clarity
    heavy = local_contrast(frame, strength=1.0)
    clipped = float(((heavy == 0) | (heavy == 255)).mean() * 100)
    out.append(('does not clip the frame at full strength', clipped < 10,
                f'{clipped:.1f}% of pixels driven to 0 or 255'))
    return out


def check_upscale(corpus) -> List[Tuple[str, bool, str]]:
    frame = corpus['cctv/sharpest.jpg']
    out = []
    height, width = frame.shape[:2]

    for scale in (2.0, 3.0):
        result = upscale(frame, scale=scale)
        expected = (int(height * scale), int(width * scale))
        out.append((f'{scale:g}x gives exactly the expected size',
                    result.shape[:2] == expected,
                    f'{result.shape[1]}x{result.shape[0]}, expected '
                    f'{expected[1]}x{expected[0]}'))

    # Interpolation cannot add detail that was not recorded. Saying so is the
    # point: an upscale that claimed to would be the dangerous kind.
    small = upscale(frame, scale=2.0)
    back = cv2.resize(small, (width, height), interpolation=cv2.INTER_AREA)
    difference = float(np.abs(back.astype(int) - frame.astype(int)).mean())
    out.append(('a round trip returns close to the original',
                difference < 4.0,
                f'mean absolute difference {difference:.2f}/255 after up and down'))
    return out


def check_deblur_motion(corpus) -> List[Tuple[str, bool, str]]:
    plate = corpus.get('reference/motion_blur_plate.jpg')
    out = []
    if plate is None:
        return [('reference image present', False, 'motion_blur_plate.jpg missing')]

    before = _high_frequency_energy(plate)
    best = max((_high_frequency_energy(deblur_motion(plate, length=length, angle=angle))
                for length in (9, 15, 21) for angle in (0, 90)), default=0.0)
    out.append(('some PSF raises high-frequency energy on a truly blurred plate',
                best > before,
                f'Laplacian variance {before:.0f} -> {best:.0f} at the best of '
                '6 PSF guesses'))

    # Wiener deconvolution with a wrong PSF invents detail; the honest check is
    # that it does not silently return the input either
    same = deblur_motion(plate, length=15, angle=45)
    out.append(('a wrong PSF still changes the image rather than passing it through',
                not np.array_equal(same, plate),
                'output differs from input at 45 degrees'))
    return out


def check_deblur_defocus(corpus) -> List[Tuple[str, bool, str]]:
    text = corpus.get('reference/defocus_text.jpg')
    if text is None:
        return [('reference image present', False, 'defocus_text.jpg missing')]
    before = _high_frequency_energy(text)
    best = max(_high_frequency_energy(deblur_defocus(text, radius=r))
               for r in (3, 5, 8, 12))
    return [('some radius raises high-frequency energy on defocused text',
             best > before,
             f'Laplacian variance {before:.0f} -> {best:.0f} over radius 3-12')]


# ---- Correct --------------------------------------------------------------

def check_perspective(corpus) -> List[Tuple[str, bool, str]]:
    warped = corpus['ground_truth/grid_perspective.png']
    straight = corpus['ground_truth/grid_straight.png']
    corners = [[80, 40], [560, 90], [600, 430], [40, 400]]

    result = correct_perspective(warped, corners)
    resized = cv2.resize(result, (straight.shape[1], straight.shape[0]))

    # The grid was warped from a known square; rectifying it has to bring the
    # lines back to horizontal and vertical
    before = estimate_straightness(warped)
    after = estimate_straightness(resized)
    difference = float(np.abs(resized.astype(int) - straight.astype(int)).mean())
    return [
        ('rectifies a grid warped from known corners',
         after >= before,
         f'straightness {before:.3f} -> {after:.3f}'),
        ('the result resembles the grid it was warped from',
         difference < 40,
         f'mean absolute difference {difference:.1f}/255'),
    ]


def check_barrel(corpus) -> List[Tuple[str, bool, str]]:
    distorted = corpus['ground_truth/grid_barrel.png']
    before = estimate_straightness(distorted)
    corrected = correct_barrel_distortion(distorted, k1=0.28)
    after = estimate_straightness(corrected)
    return [('the inverse of a known k1 straightens the grid',
             after >= before,
             f'straightness {before:.3f} -> {after:.3f} '
             '(grid was distorted at k1=-0.28)')]


# ---- Special --------------------------------------------------------------

def check_redact(corpus) -> List[Tuple[str, bool, str]]:
    frame = corpus['cctv/sharpest.jpg']
    regions = [(120, 80, 200, 140)]
    out = []

    for method in ('fill', 'noise'):
        result = redact_region(frame, 120, 80, 200, 140, method=method)
        reversible = is_reversible(method)
        verified = verify_redaction(frame, result, regions)
        out.append((f'{method} destroys the region beyond recovery',
                    not reversible and verified['safe'],
                    f'is_reversible={reversible}, safe={verified["safe"]}, '
                    f'residual correlation with the original '
                    f'{verified["max_correlation"]:.4f}'))

    # The pair that matters legally: blur and pixelate leave the structure in
    # place, and a report that called them redaction would be wrong
    for method in ('blur', 'pixelate'):
        result = redact_region(frame, 120, 80, 200, 140, method=method)
        verified = verify_redaction(frame, result, regions)
        out.append((f'{method} is correctly reported as not safe',
                    not verified['safe'],
                    f'residual correlation {verified["max_correlation"]:.4f} - '
                    'recoverable, which is why it is not offered as redaction'))

    # Noise redaction draws fresh noise every run, which makes a chain
    # unreproducible unless it is seeded. Both halves matter: the seed has to
    # pin the output, and seeding must not weaken the redaction.
    seeded = redact_region(frame, 120, 80, 200, 140, method='noise', seed=42)
    again = redact_region(frame, 120, 80, 200, 140, method='noise', seed=42)
    unseeded_a = redact_region(frame, 120, 80, 200, 140, method='noise')
    unseeded_b = redact_region(frame, 120, 80, 200, 140, method='noise')

    out.append(('a seed makes noise redaction replay identically',
                np.array_equal(seeded, again)
                and not np.array_equal(unseeded_a, unseeded_b),
                'the same seed reproduces the frame exactly; without one the '
                'noise differs every run'))

    verified = verify_redaction(frame, seeded, regions)
    out.append(('seeding does not weaken the redaction',
                verified['safe'],
                f"residual correlation {verified['max_correlation']:.4f} with "
                f'a known seed - the original pixels are discarded either way'))

    # The rest of the frame must be untouched, or the redaction has altered
    # evidence outside the region it was asked to cover
    result = redact_region(frame, 120, 80, 200, 140, method='fill')
    mask = np.ones(frame.shape[:2], bool)
    mask[80:220, 120:320] = False
    out.append(('nothing outside the region changes',
                np.array_equal(result[mask], frame[mask]),
                f'{int(mask.sum())} pixels outside the box compared'))
    return out


# ---- Forensic -------------------------------------------------------------

def check_clone_detect(corpus) -> List[Tuple[str, bool, str]]:
    forged = corpus['ground_truth/copy_move.png']
    clean = corpus['ground_truth/clean_control.jpg']
    out = []

    result = detect_copy_move(forged)
    expected = (260, 140)                       # the shift the corpus applied
    found = [(s['dx'], s['dy']) for s in result.get('shifts', [])[:5]]
    hit = any(abs(dx - expected[0]) <= 2 and abs(dy - expected[1]) <= 2
              for dx, dy in found)
    out.append(('finds the shift that was actually applied',
                hit,
                f'expected dx={expected[0]:+d} dy={expected[1]:+d}, '
                f'top shifts: {found or "none"}'))

    control = detect_copy_move(clean)
    out.append(('does not report a forgery on the untouched control',
                not control['detected'],
                f"detected={control['detected']}, "
                f"{control.get('match_count', 0)} matching pairs"))
    return out


def check_ghost(corpus) -> List[Tuple[str, bool, str]]:
    out = []

    # A PNG composite of JPEG sources - the case the technique reads. The
    # corpus splice is re-saved as JPEG, which is the documented blind spot.
    base = corpus['cctv/sharpest.jpg']
    region = (152, 104, 296, 200)
    outer = _jpeg(base, 95)
    inner = _jpeg(base[104:304, 152:448], 55)
    composite = outer.copy()
    composite[104:304, 152:448] = inner

    report = ghost_report(composite, region=region)
    out.append(('recovers the quality a named region was saved at',
                report['detected'] and abs(report['ghost_quality'] - 55) <= 5,
                f"reported {report['ghost_quality']} for a Q55 paste, "
                f"separation {report['separation']:+.3f}"))

    control = ghost_report(outer, region=region)
    out.append(('the same region of an untouched frame does not fire',
                not control['detected'],
                f"separation {control['separation']:+.3f} against a "
                f"{-report['threshold']:+.2f} threshold"))

    out.append(('claims nothing when no region is given',
                not ghost_report(outer)['detected'],
                'searching for the region does not work and is not offered'))

    sweep = ghost_sweep(outer, block_size=16)
    out.append(('the sweep is exposed for inspection',
                sweep.shape[0] == len(GHOST_QUALITIES),
                f'{sweep.shape[0]} normalised frames of '
                f'{sweep.shape[1]}x{sweep.shape[2]} blocks'))

    # The control that separates a compression finding from a content one.
    # A region cut from a different scene entirely, pasted at the *same*
    # quality, differs in texture in every way a real forgery would - but
    # shares the host's compression history. It must not fire. Without this,
    # a detector that merely notices "this part looks different" would pass
    # every other check here.
    donor = corpus['cctv/darkest.jpg']
    if donor.shape == base.shape:
        same_quality = outer.copy()
        same_quality[104:304, 152:448] = _jpeg(donor, 95)[104:304, 152:448]
        control = ghost_report(same_quality, region=region)
        out.append(('a different scene at the same quality does not fire',
                    not control['detected'],
                    f"dip {control['dip']:+.3f} against a "
                    f"-{control['threshold']:.2f} threshold - texture alone "
                    f"is not read as compression history"))

        # The same donor at a lower quality has to dip deeper than the same
        # donor at the host's own quality. Ordering rather than detection:
        # the measured rate is 59%, so asserting this one pair must cross the
        # threshold would be asserting something the filter does not promise.
        cross = outer.copy()
        cross[104:304, 152:448] = _jpeg(donor, 55)[104:304, 152:448]
        crossed = ghost_report(cross, region=region)
        out.append(('a quality difference dips deeper than texture alone',
                    crossed['dip'] < control['dip'],
                    f"same donor at Q55 dips {crossed['dip']:+.3f} against "
                    f"{control['dip']:+.3f} at Q95 - the compression "
                    f"difference is what moves it"))

    # The other direction, from the repository's own purpose-built sample: a
    # Q95 region inside a Q60 frame. Everything else measured here puts a
    # *lower* quality inside a higher one, and a technique that only worked
    # one way round would pass all of it.
    sample = corpus.get('samples/jpeg_ghost.png')
    if sample is not None:
        high_in_low = ghost_report(sample, region=(176, 128, 160, 128))
        out.append(('finds a higher-quality region inside a lower-quality frame',
                    high_in_low['detected'] and high_in_low['ghost_quality'] == 95,
                    f"reported {high_in_low['ghost_quality']} for a Q95 region "
                    f"pasted into a Q60 frame, dip {high_in_low['dip']:+.3f}"))
    return out


def _jpeg(image: np.ndarray, quality: int) -> np.ndarray:
    """Round-trip through a real JPEG encoder, so the history is real."""
    ok, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise RuntimeError('JPEG encoding failed')
    return cv2.imdecode(buffer, cv2.IMREAD_COLOR)


CHECKS: Dict[str, Callable] = {
    'clahe': check_clahe,
    'levels': check_levels,
    'contrast_brightness': check_contrast_brightness,
    'curves': check_curves,
    'histeq': check_histeq,
    'sharpen': check_sharpen,
    'nl_means': check_nl_means,
    'local_contrast': check_local_contrast,
    'upscale': check_upscale,
    'deblur_motion': check_deblur_motion,
    'deblur_defocus': check_deblur_defocus,
    'perspective': check_perspective,
    'barrel': check_barrel,
    'redact': check_redact,
    'clone_detect': check_clone_detect,
    'ghost': check_ghost,
}

def check_white_balance(corpus) -> List[Tuple[str, bool, str]]:
    """
    A CCTV frame under mixed lighting is the case this is for.

    The cast tests run on the frame with the fewest blown highlights.
    white_patch normalises by the brightest pixel in each channel, so on a
    frame where every channel already reaches 255 - the tamper frame has 6.1%
    of its pixels at 250 or above - every gain is exactly 1.0 and the method
    is a no-op. That is a property of the method, not a fault, and it gets its
    own assertion below rather than being allowed to fail this one.
    """
    frame = corpus['cctv/softest.jpg']
    blown_frame = corpus['cctv/event_tamper.jpg']
    out = []

    def cast(image):
        """How far the channel means sit apart; a neutral frame sits near 0."""
        means = [float(image[:, :, c].mean()) for c in range(3)]
        return max(means) - min(means)

    # This frame is nearly neutral already (spread 3.1), so "reduces the
    # cast" is not a fair question of it. Give it a cast worth removing.
    tinted = frame.astype(np.float32)
    tinted[:, :, 0] *= 1.35          # index 0 is red in the RGB the loader gives
    tinted = np.clip(tinted, 0, 255).astype(np.uint8)

    before = cast(tinted)
    for method in WHITE_BALANCE_METHODS:
        after = cast(auto_white_balance(tinted, method=method))
        out.append((f'{method} reduces a deliberate red cast',
                    after < before,
                    f'channel spread {before:.1f} -> {after:.1f}'))

    # white_patch normalises by the brightest pixel per channel, so a blown
    # highlight is its blind spot. Recorded rather than asserted.
    blown = float((_gray(blown_frame) >= 250).mean() * 100)
    patch_after = cast(auto_white_balance(blown_frame, method='white_patch'))
    gray_after = cast(auto_white_balance(blown_frame, method='gray_world'))
    # Asserted, not merely recorded. The first version of this passed `True`,
    # which cannot fail and so was a comment with a tick beside it.
    # Not "does nothing at all": that holds when every channel reaches 255, as
    # on the tinted frame where all three gains come out exactly 1.0. On this
    # one it still acts, just far worse than the alternative.
    out.append(('white_patch is the one that struggles with blown highlights',
                patch_after > gray_after,
                f'{blown:.1f}% of this frame is at 250 or above; white_patch '
                f'leaves a spread of {patch_after:.1f} against gray_world\'s '
                f'{gray_after:.1f}'))

    # A patch the user declares neutral has to come out neutral. Measured on
    # the *tinted* frame: on the untouched one the patch is already near
    # neutral, so a filter that did nothing passed this.
    before_patch = cast(tinted[40:80, 300:360])
    patched = white_balance_from_patch(tinted, 300, 40, 60, 40)
    region = patched[40:80, 300:360]
    means = [float(region[:, :, c].mean()) for c in range(3)]
    spread = max(means) - min(means)
    out.append(('a patch declared neutral comes out neutral, from a cast frame',
                spread < 12 and spread < before_patch,
                f'channel spread inside the patch {before_patch:.1f} -> '
                f'{spread:.1f}'))
    return out


def check_saturation(corpus) -> List[Tuple[str, bool, str]]:
    frame = corpus['cctv/sharpest.jpg']
    out = []

    def chroma(image):
        return float(cv2.cvtColor(image, cv2.COLOR_RGB2HSV)[:, :, 1].mean())

    base = chroma(frame)
    low, high = chroma(adjust_saturation(frame, 0.5)), chroma(adjust_saturation(frame, 1.5))

    # Not exactly the identity, and correctly so: the filter works in HSV,
    # and a BGR -> HSV -> BGR round trip at 8 bits costs up to 2 levels on its
    # own. Worth knowing before chaining several saturation steps.
    unchanged = adjust_saturation(frame, 1.0)
    drift = int(np.abs(unchanged.astype(int) - frame.astype(int)).max())
    out.append(('factor 1.0 returns the image within colour-space rounding',
                drift <= 2,
                f'largest difference {drift}/255, from the HSV round trip '
                f'rather than the scaling'))
    out.append(('above 1 raises saturation, below 1 lowers it',
                low < base < high,
                f'{low:.1f} < {base:.1f} < {high:.1f} mean S'))
    out.append(('zero saturation leaves no colour at all',
                chroma(adjust_saturation(frame, 0.0)) < 1.0,
                f'mean S {chroma(adjust_saturation(frame, 0.0)):.2f}'))

    for method in DESATURATE_METHODS:
        grey = desaturate(frame, method=method)
        if grey.ndim == 2:
            # Single channel carries no colour by construction
            out.append((f'desaturate {method} produces a neutral image',
                        True, f'single channel {grey.shape}, no chroma to hold'))
            continue
        means = [float(grey[:, :, c].mean()) for c in range(3)]
        out.append((f'desaturate {method} produces a neutral image',
                    max(means) - min(means) < 1.0,
                    f'channel spread {max(means) - min(means):.3f}'))
    return out


def check_component(corpus) -> List[Tuple[str, bool, str]]:
    frame = corpus['cctv/sharpest.jpg']
    out = []

    # Every channel of every space the filter offers must come back usable.
    # "usable" has to mean more than uint8 and non-empty: a filter that
    # returned its input unchanged satisfied that, which is how this check
    # passed mutation testing while proving nothing.
    for space, (_code, channels) in COLOR_SPACES.items():
        planes = {}
        for channel in channels:
            result = extract_component(frame, space=space, channel=channel)
            planes[channel] = result
            single = result.ndim == 2 or (result.ndim == 3 and result.shape[2] == 1)
            out.append((f'{space}:{channel} is a single plane, not the image',
                        single and result.dtype == np.uint8
                        and result.shape[:2] == frame.shape[:2],
                        f'{result.shape}, std {float(result.std()):.1f}'))

        # Two channels of one space describe different things
        names = list(planes)
        if len(names) > 1:
            first, second = planes[names[0]], planes[names[1]]
            differ = not np.array_equal(first, second)
            out.append((f'{space} channels differ from one another',
                        differ,
                        f'{names[0]} and {names[1]} '
                        f'{"differ" if differ else "are identical"}'))

    for plane in (0, 7):
        values = np.unique(extract_bit_plane(frame, plane))
        out.append((f'bit plane {plane} is binary',
                    len(values) <= 2,
                    f'distinct values {values.tolist()}'))
    return out


def check_fisheye(corpus) -> List[Tuple[str, bool, str]]:
    distorted = corpus['ground_truth/grid_barrel.png']
    out = []

    before = estimate_straightness(distorted)
    best = max(estimate_straightness(correct_fisheye(distorted, strength=s))
               for s in (0.2, 0.4, 0.6))
    out.append(('some strength straightens a distorted grid',
                best >= before,
                f'straightness {before:.3f} -> {best:.3f} over strength 0.2-0.6'))

    for border in FISHEYE_BORDER_MODES:
        result = correct_fisheye(distorted, strength=0.4, border_mode=border)
        out.append((f'border mode {border} fills the empty corners',
                    result.dtype == np.uint8,
                    f'{result.shape}, corner value {result[2, 2].tolist()}'))
    return out


def check_measure_3d(corpus) -> List[Tuple[str, bool, str]]:
    """
    Metrology against a case whose answer is fixed by construction.

    The strongest available check is self-consistency: a reference measured
    against itself has to return its own height, whatever the geometry.
    """
    out = []
    horizon_y = 180.0
    ref_base, ref_top = (200.0, 400.0), (200.0, 250.0)

    same = measure_height(base=ref_base, top=ref_top,
                          reference_base=ref_base, reference_top=ref_top,
                          horizon=horizon_y, reference_height=1800.0)
    out.append(('the reference measured against itself returns its own height',
                abs(same['height'] - 1800.0) < 1.0,
                f"{same['height']:.2f}mm against a 1800mm reference"))

    result = measure_height(base=(450.0, 360.0), top=(450.0, 290.0),
                            reference_base=ref_base, reference_top=ref_top,
                            horizon=horizon_y, reference_height=1800.0)
    out.append(('reports a height and an uncertainty',
                'height' in result and 'uncertainty_per_pixel' in result,
                f"height {result['height']:.0f}mm, uncertainty "
                f"{result['uncertainty_per_pixel']:.1f}mm/px"))

    # A shorter object in the image has to measure shorter
    shorter = measure_height(base=(450.0, 360.0), top=(450.0, 320.0),
                             reference_base=ref_base, reference_top=ref_top,
                             horizon=horizon_y, reference_height=1800.0)
    out.append(('a shorter image height measures shorter',
                shorter['height'] < result['height'],
                f"{shorter['height']:.0f}mm < {result['height']:.0f}mm"))

    # Nearer the horizon, one pixel spans more real distance - the warning
    # the documentation gives, checked rather than repeated
    near = measure_height(base=(450.0, 200.0), top=(450.0, 190.0),
                          reference_base=ref_base, reference_top=ref_top,
                          horizon=horizon_y, reference_height=1800.0)
    out.append(('uncertainty grows towards the horizon',
                near['uncertainty_per_pixel'] > result['uncertainty_per_pixel'],
                f"{result['uncertainty_per_pixel']:.1f} -> "
                f"{near['uncertainty_per_pixel']:.1f} mm/px nearer the horizon"))
    return out


CHECKS.update({
    'white_balance': check_white_balance,
    'saturation': check_saturation,
    'component': check_component,
    'fisheye': check_fisheye,
    'measure_3d': check_measure_3d,
})

def check_undistort(corpus) -> List[Tuple[str, bool, str]]:
    """
    Calibration measured against something known to be straight.

    A chessboard row is straight in the world, so after correction its
    detected corners have to be collinear. That is real ground truth, unlike
    `estimate_straightness`, which is a content-dependent proxy and improved
    on only 7 of these 13 views while the corner geometry improved on all 13.
    """
    import glob
    out = []

    paths = sorted(glob.glob('validation/corpus/calibration/*.jpg'))
    images = [cv2.imread(path) for path in paths]
    images = [image for image in images if image is not None]
    if len(images) < 8:
        return [('the chessboard views are present', False,
                 f'{len(images)} views found, need at least 8 to calibrate')]

    calibration = calibrate_from_chessboard(images, pattern_size=(9, 6))
    out.append(('calibrates within a sane reprojection error',
                calibration.reprojection_error < 1.0,
                f'{calibration.reprojection_error:.4f} px over '
                f'{len(images)} views'))

    distortion = np.asarray(calibration.distortion).ravel()
    out.append(('recovers the barrel distortion this lens has',
                distortion[0] < 0,
                f'k1={distortion[0]:+.4f}, k2={distortion[1]:+.4f}'))

    before, after = [], []
    for image in images:
        b = _row_bow(image)
        a = _row_bow(undistort(image, calibration, alpha=1.0, crop=False))
        if b is not None and a is not None:
            before.append(b)
            after.append(a)

    before_a, after_a = np.array(before), np.array(after)
    out.append(('straightens every chessboard row it was given',
                bool((after_a < before_a).all()),
                f'row bow {before_a.mean():.2f} -> {after_a.mean():.2f} px mean, '
                f'improved on {int((after_a < before_a).sum())}/{len(before_a)} views'))
    out.append(('leaves rows straight to within about a pixel',
                after_a.max() < 1.5,
                f'worst remaining bow {after_a.max():.2f} px, was '
                f'{before_a.max():.2f} px'))

    # The chain-friendly path a preset actually replays
    with tempfile.TemporaryDirectory() as directory:
        path = str(Path(directory) / 'calibration.json')
        save_calibration(calibration, path)
        reloaded = load_calibration(path)
        out.append(('a saved calibration reloads unchanged',
                    np.allclose(reloaded.camera_matrix, calibration.camera_matrix),
                    'camera matrix and distortion survive the JSON round trip'))
        out.append(('undistort_with_file matches the direct call',
                    np.array_equal(undistort_with_file(images[0], path),
                                   undistort(images[0], calibration)),
                    'the preset path and the library path agree'))
    return out


def _row_bow(image: np.ndarray) -> Optional[float]:
    """Largest deviation of any chessboard row from a straight line, in pixels."""
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    found, corners = cv2.findChessboardCorners(gray, (9, 6), None)
    if not found:
        return None

    points = corners.reshape(6, 9, 2)
    worst = 0.0
    for row in points:
        (x0, y0), (x1, y1) = row[0], row[-1]
        dx, dy = x1 - x0, y1 - y0
        length = np.hypot(dx, dy)
        deviation = np.abs(dy * (row[:, 0] - x0) - dx * (row[:, 1] - y0)) / max(length, 1e-6)
        worst = max(worst, float(deviation.max()))
    return worst


CHECKS['undistort'] = check_undistort

# ---- the analysis reports -------------------------------------------------

def check_noise(corpus) -> List[Tuple[str, bool, str]]:
    """
    Noise estimation against noise that was added on purpose.

    A clean synthetic base plus Gaussian noise of a chosen sigma is the only
    way to ask whether the estimate is right rather than merely stable.
    """
    out = []
    rng = np.random.default_rng(7)
    base = np.full((320, 480, 3), 128, np.uint8)

    # Single channel, so the ground truth is exact. Adding independent noise
    # to three channels and comparing against the per-channel sigma would be
    # wrong by construction: _to_gray weights the channels 0.114/0.587/0.299,
    # so luminance noise is sqrt(0.114^2 + 0.587^2 + 0.299^2) = 0.669 of it.
    # A 35% tolerance hides that, and hid it here until the ratio came out
    # identical at three sigmas.
    flat = np.full((320, 480), 128.0)
    for sigma in (2.0, 5.0, 10.0, 20.0):
        noisy = np.clip(flat + rng.normal(0, sigma, flat.shape), 0, 255).astype(np.uint8)
        measured = estimate_noise(noisy)
        out.append((f'recovers a known sigma of {sigma:g} to within 5%',
                    abs(measured - sigma) < max(0.15, sigma * 0.05),
                    f'measured {measured:.2f} against {sigma:g} added'))

    # And the luminance weighting itself, stated rather than assumed
    colour = np.clip(base + rng.normal(0, 10.0, base.shape), 0, 255).astype(np.uint8)
    expected = 10.0 * float(np.sqrt(0.114 ** 2 + 0.587 ** 2 + 0.299 ** 2))
    out.append(('per-channel noise reads through the luminance weighting',
                abs(estimate_noise(colour) - expected) < 1.0,
                f'{estimate_noise(colour):.2f} measured, {expected:.2f} expected '
                f'from sigma 10 on three independent channels'))

    # Uniformity is the forensic part: noise that differs across the frame is
    # what a splice from another source leaves behind
    half = np.clip(base + rng.normal(0, 2, base.shape), 0, 255).astype(np.uint8)
    half[:, 240:] = np.clip(base[:, 240:] + rng.normal(0, 12, base[:, 240:].shape),
                            0, 255).astype(np.uint8)
    even = np.clip(base + rng.normal(0, 2, base.shape), 0, 255).astype(np.uint8)

    uneven_score = noise_report(half)['uniformity']
    even_score = noise_report(even)['uniformity']
    out.append(('reads a frame with two noise levels as less uniform',
                uneven_score > even_score,
                f'uniformity {even_score:.2f} even vs {uneven_score:.2f} split'))

    # Asserting noisiest >= quietest is a tautology - a maximum is never
    # below a minimum. Put the noise somewhere known and ask where it says.
    planted = np.clip(base + rng.normal(0, 1.5, base.shape), 0, 255).astype(np.uint8)
    px, py, pw, ph = 288, 192, 96, 96
    planted[py:py+ph, px:px+pw] = np.clip(
        base[py:py+ph, px:px+pw] + rng.normal(0, 18, (ph, pw, 3)),
        0, 255).astype(np.uint8)

    located = noise_report(planted)['noisiest_block']
    inside = (px <= located['x'] < px + pw) and (py <= located['y'] < py + ph)
    out.append(('points at the block where the noise actually is',
                inside,
                f"noisiest block reported at ({located['x']}, {located['y']}), "
                f"sigma {located['sigma']:.2f}; the noise was planted in "
                f"x {px}-{px+pw}, y {py}-{py+ph}"))
    return out


def check_ela(corpus) -> List[Tuple[str, bool, str]]:
    """Error level analysis against a region whose history was chosen."""
    out = []
    base = corpus['cctv/sharpest.jpg']
    region = (152, 104, 296, 200)
    x, y, w, h = region

    outer = _jpeg(base, 95)
    composite = outer.copy()
    composite[y:y+h, x:x+w] = _jpeg(base[y:y+h, x:x+w], 55)

    # A region re-encoded harder has lost more detail, so re-encoding the
    # whole frame again changes it less - a lower error, not a higher one
    stats = ela_stats(composite, quality=95)
    error = error_level_analysis(composite, quality=95)
    inside = float(_gray(error)[y:y+h, x:x+w].mean())
    outside_mask = np.ones(error.shape[:2], bool)
    outside_mask[y:y+h, x:x+w] = False
    outside = float(_gray(error)[outside_mask].mean())

    # The same region of an untouched frame, as a control: inside-versus-
    # outside on one image alone would be satisfied by any image with
    # structure in it
    clean_error = error_level_analysis(outer, quality=95)
    clean_inside = float(_gray(clean_error)[y:y+h, x:x+w].mean())
    clean_outside = float(_gray(clean_error)[outside_mask].mean())
    spliced_gap = abs(inside - outside)
    clean_gap = abs(clean_inside - clean_outside)

    out.append(('a region with a different history stands out more than an '
                'untouched one',
                spliced_gap > clean_gap,
                f'inside-outside gap {spliced_gap:.2f} on the splice against '
                f'{clean_gap:.2f} on the same region of an untouched frame'))

    out.append(('reports the block statistics the report renders',
                all(k in stats for k in ('mean_error', 'max_error', 'block_mean',
                                         'block_std', 'hottest_block')),
                f"mean {stats['mean_error']:.2f}, hottest block at "
                f"({stats['hottest_block']['x']}, {stats['hottest_block']['y']})"))

    # Quality is the knob, and it has to move the answer
    errors = [ela_stats(outer, quality=q)['mean_error'] for q in (70, 85, 95)]
    out.append(('the comparison quality changes the error level',
                len(set(round(e, 2) for e in errors)) > 1,
                ' -> '.join(f'{e:.2f}' for e in errors) + ' at quality 70/85/95'))
    return out


def check_compression(corpus) -> List[Tuple[str, bool, str]]:
    """
    Compression analysis, including the one measurement with an exact answer.

    A JPEG carries the quantisation tables it was written with, so the quality
    read back out can be checked against the quality it was saved at - no
    proxy, no threshold.
    """
    out = []
    base = corpus['cctv/sharpest.jpg']

    with tempfile.TemporaryDirectory() as directory:
        for quality in (40, 60, 75, 90):
            path = Path(directory) / f'q{quality}.jpg'
            cv2.imwrite(str(path), base, [cv2.IMWRITE_JPEG_QUALITY, quality])
            estimate = estimate_jpeg_quality(path)
            reported = estimate['quality'] if estimate else None
            out.append((f'reads back a quality of {quality} from the tables',
                        reported is not None and abs(reported - quality) <= 5,
                        f'reported {reported} for a file saved at {quality}'))

        # A PNG has no tables at all, and saying so beats guessing
        png = Path(directory) / 'plain.png'
        cv2.imwrite(str(png), base)
        out.append(('reports no tables for a file that has none',
                    estimate_jpeg_quality(png) is None,
                    'a PNG carries no quantisation tables'))

    # Blocking rises as quality falls - the measure the report leads with
    scores = [blockiness_score(_jpeg(base, q))['blockiness'] for q in (90, 60, 30)]
    # Strictly, and by a margin: a measure frozen at one value satisfies the
    # non-decreasing form, and so would a measure that ignored its input
    out.append(('blockiness rises measurably as quality falls',
                scores[0] < scores[1] < scores[2],
                ' -> '.join(f'{s:.1f}' for s in scores)
                + f' at quality 90/60/30 ({scores[2] - scores[0]:+.1f} end to end)'))
    return out


def check_metadata(corpus) -> List[Tuple[str, bool, str]]:
    """Metadata forensics against files whose history is known."""
    out = []
    root = Path('validation/corpus')

    # A real camera file that really was edited, from outside this project
    nikon = root / 'reference' / 'exif_camera.jpg'
    if nikon.exists():
        report = metadata_report(nikon)
        checks = {finding['check'] for finding in report['findings']}
        out.append(('reads a real camera header',
                    report['has_exif'] and report['make'] == 'NIKON CORPORATION',
                    f"{report['exif_tag_count']} tags, {report['make']} "
                    f"{report['model']}"))
        out.append(('flags the cropped-after-capture contradictions',
                    {'dimension_mismatch', 'thumbnail_mismatch'} <= checks,
                    f'findings: {sorted(checks)}'))

    # A CCTV frame has no EXIF, and a JPEG normally would
    cctv = root / 'cctv' / 'sharpest.jpg'
    if cctv.exists():
        report = metadata_report(cctv)
        checks = {finding['check'] for finding in report['findings']}
        # Tied to the file it is about: 'no_exif' is present in the report of
        # any stripped JPEG, so the finding alone does not show this report
        # describes *this* frame
        out.append(('remarks on this JPEG having no EXIF at all',
                    'no_exif' in checks and report['filename'] == cctv.name,
                    f"findings on {report['filename']}: {sorted(checks)} - "
                    f'absence is normal, and said so'))

    # A PNG is not expected to carry EXIF, so its absence is not a finding
    png = root / 'ground_truth' / 'copy_move.png'
    if png.exists():
        report = metadata_report(png)
        checks = {finding['check'] for finding in report['findings']}
        # Its own identity, not just the absence of a finding: a report about
        # some other file would also lack 'no_exif'
        out.append(('reads the PNG as itself and stays quiet about EXIF',
                    report['format'] == '.png' and not report['has_exif']
                    and 'no_exif' not in checks,
                    f"format {report['format']}, has_exif {report['has_exif']}, "
                    f"findings {sorted(checks) or 'none'} - PNG is not an "
                    f"EXIF-bearing format, so silence is correct"))

    # Timestamp logic, driven directly - the order capture forbids
    disordered = check_timestamps({
        'DateTimeOriginal': '2026:07:27 15:00:00',
        'DateTimeDigitized': '2026:07:26 09:00:00',
        'DateTime': '2026:07:28 11:00:00',
    })
    names = {finding['check'] for finding in disordered}
    out.append(('catches a digitised time before the capture time',
                'timestamp_disorder' in names,
                f'findings: {sorted(names)}'))

    clean = check_timestamps({
        'DateTimeOriginal': '2026:07:27 15:00:00',
        'DateTimeDigitized': '2026:07:27 15:00:00',
        'DateTime': '2026:07:27 15:00:00',
    })
    # Paired with the disordered case in one assertion: "returns nothing" is
    # satisfied by a function that always returns nothing
    out.append(('separates a consistent set of timestamps from a disordered one',
                not clean and len(disordered) > 0,
                f'{len(clean)} findings on three identical timestamps against '
                f'{len(disordered)} on a disordered set'))

    out.append(('names an editor in the Software tag',
                detect_editing_software({'Software': 'Adobe Photoshop 24.0'}) is not None
                and detect_editing_software({'Software': 'NIKON D80 Ver.1.00'}) is None,
                'Photoshop matched, camera firmware not'))
    return out


CHECKS.update({
    'noise': check_noise,
    'ela:report': check_ela,
    'compression': check_compression,
    'metadata': check_metadata,
})

# ---- cross-cutting invariants ---------------------------------------------
# Perturbation testing showed that of 111 checks, 7 noticed red and blue being
# swapped, 11 noticed the output shifted four pixels, 8 noticed a 10% gain and
# 8 noticed the filter reaching only half the frame. That is not a fault in
# each check - a mean local sigma is *supposed* to be invariant to translation
# - but it left three properties nothing verified at all.
#
# These assert them directly, once per filter, for the filters where the
# property should hold. A tone or detail filter must not move content, must
# not permute channels, and must reach the whole frame.

TONE_AND_DETAIL: Dict[str, Dict[str, Any]] = {
    'clahe': {},
    'histeq': {},
    'levels': {'black_point': 20, 'white_point': 235},
    'contrast_brightness': {'contrast': 1.3},
    'curves': {'preset': 'lift_shadows'},
    'sharpen': {'amount': 1.0},
    'gaussian_blur': {'radius': 2.0},
    'bilateral_filter': {},
    'local_contrast': {'strength': 0.6},
    'detail_enhance': {},
    'saturation': {'factor': 1.4},
}


def _marker_frame() -> np.ndarray:
    """A frame with one unmistakable bright dot and three colour blocks."""
    frame = np.full((240, 320, 3), 60, np.uint8)
    rng = np.random.default_rng(3)
    frame = np.clip(frame + rng.normal(0, 12, frame.shape), 0, 255).astype(np.uint8)

    # Distinct colour blocks: which channel dominates is the fingerprint.
    # RGB, matching what ImageLoader gives the filters.
    frame[20:80, 20:100] = (200, 40, 40)        # red-dominant
    frame[20:80, 120:200] = (40, 200, 40)       # green-dominant
    frame[20:80, 220:300] = (40, 40, 200)       # blue-dominant
    # A single bright dot whose position is the fingerprint
    frame[160:168, 160:168] = 255
    return frame


def check_invariants(name: str, params: Dict[str, Any]) -> List[Tuple[str, bool, str]]:
    """Geometry, channel order and coverage for one tone or detail filter."""
    from src.filters import resolve_filter

    frame = _marker_frame()
    result = resolve_filter(name).fn(frame, **params)
    out = []

    if result.shape != frame.shape:
        return [(f'{name} keeps the frame geometry', False,
                 f'{frame.shape} became {result.shape}')]

    # 1. Content must not move. The centroid of the bright marker, not its
    # argmax: argmax returns the first maximum, so a block rolled four pixels
    # still reports a coordinate inside the original block and a tolerance
    # wide enough to survive that is wide enough to miss the bug.
    grey = _gray(result).astype(np.float32)
    hot = grey >= max(float(grey.max()) - 8.0, 200.0)
    if hot.any():
        ys, xs = np.nonzero(hot)
        cx, cy = float(xs.mean()), float(ys.mean())
    else:
        cx = cy = -1.0
    out.append((f'{name} does not move content',
                abs(cx - 163.5) <= 1.5 and abs(cy - 163.5) <= 1.5,
                f'the marker centred at (163.5, 163.5) reads centred at '
                f'({cx:.1f}, {cy:.1f})'))

    # 2. Channel order must survive. Which channel dominates each block is
    #    the thing a BGR/RGB confusion destroys.
    for label, (x0, x1), expected in (('red', (20, 100), 0),
                                      ('green', (120, 200), 1),
                                      ('blue', (220, 300), 2)):
        block = result[20:80, x0:x1]
        dominant = int(np.argmax([float(block[:, :, c].mean()) for c in range(3)]))
        out.append((f'{name} keeps the {label} block {label}',
                    dominant == expected,
                    f'channel {dominant} dominates, expected {expected}'))

    # 3. The filter has to reach the whole frame, not half of it
    left = np.abs(result[:, :160].astype(int) - frame[:, :160].astype(int)).mean()
    right = np.abs(result[:, 160:].astype(int) - frame[:, 160:].astype(int)).mean()
    both = left > 0.01 and right > 0.01
    ratio = min(left, right) / max(max(left, right), 1e-6)
    out.append((f'{name} reaches both halves of the frame',
                both and ratio > 0.05,
                f'mean change {left:.2f} left against {right:.2f} right'))
    return out


def _with_invariants(name: str, params: Dict[str, Any], existing):
    """Append the invariants to whatever check this filter already had."""
    def combined(corpus):
        results = list(existing(corpus)) if existing else []
        results.extend(check_invariants(name, params))
        return results
    return combined


for _name, _params in TONE_AND_DETAIL.items():
    CHECKS[_name] = _with_invariants(_name, _params, CHECKS.get(_name))

# ---- geometry, inversion, frequency ---------------------------------------

def check_flip(corpus) -> List[Tuple[str, bool, str]]:
    frame = corpus['cctv/sharpest.jpg']
    out = []

    for direction, axis in (('horizontal', 1), ('vertical', 0)):
        once = flip(frame, direction=direction)
        twice = flip(once, direction=direction)
        # Involution alone is satisfied by a filter that does nothing, so the
        # single application has to differ from the input as well
        out.append((f'{direction} flip is its own inverse and does something',
                    np.array_equal(twice, frame) and not np.array_equal(once, frame),
                    'flipping twice returns the original; once does not'))
        out.append((f'{direction} flip matches the array operation',
                    np.array_equal(once, np.flip(frame, axis=axis)),
                    f'matches numpy flip on axis {axis}'))
    return out


def check_invert(corpus) -> List[Tuple[str, bool, str]]:
    frame = corpus['cctv/sharpest.jpg']
    once = invert(frame)
    twice = invert(once)
    return [
        ('inverting twice returns the original, and once does not',
         np.array_equal(twice, frame) and not np.array_equal(once, frame),
         'an involution that actually inverts'),
        ('every value becomes its complement',
         np.array_equal(once.astype(int), 255 - frame.astype(int)),
         'output equals 255 minus input, exactly'),
    ]


def check_rotate(corpus) -> List[Tuple[str, bool, str]]:
    frame = corpus['cctv/sharpest.jpg']
    height, width = frame.shape[:2]
    out = []

    # rotate grows the canvas to the rotated bounding box rather than
    # cropping, so a quarter turn of a non-square frame swaps the dimensions
    # and nothing is lost
    turned = rotate(frame, 90)
    out.append(('a quarter turn swaps the dimensions, losing no content',
                turned.shape[:2] == (width, height),
                f'{width}x{height} became {turned.shape[1]}x{turned.shape[0]}'))

    # 45 degrees needs a canvas larger than either side
    diagonal = rotate(frame, 45)
    out.append(('an oblique angle grows the canvas to fit the corners',
                diagonal.shape[0] > height and diagonal.shape[1] > width,
                f'45 degrees gave {diagonal.shape[1]}x{diagonal.shape[0]} '
                f'from {width}x{height}'))

    full = rotate(frame, 360)
    difference = float(np.abs(full.astype(int) - frame.astype(int)).mean())
    out.append(('a full turn returns the image, to interpolation error',
                full.shape == frame.shape and difference < 2.0,
                f'mean absolute difference {difference:.3f}/255'))

    out.append(('a quarter turn is not the original',
                not np.array_equal(turned, frame),
                'the 90 degree result differs from the input'))

    # Four quarter turns are one full turn
    quarters = frame
    for _ in range(4):
        quarters = rotate(quarters, 90)
    drift = float(np.abs(quarters.astype(int) - frame.astype(int)).mean())
    out.append(('four quarter turns come back to the start',
                drift < 12.0,
                f'mean absolute difference {drift:.2f}/255 after four turns '
                f'(interpolation and corner loss accumulate)'))
    return out


def check_resize(corpus) -> List[Tuple[str, bool, str]]:
    frame = corpus['cctv/sharpest.jpg']
    height, width = frame.shape[:2]
    out = []

    for scale in (0.5, 2.0):
        result = resize(frame, scale=scale)
        expected = (int(height * scale), int(width * scale))
        out.append((f'scale {scale:g} gives exactly the expected size',
                    result.shape[:2] == expected,
                    f'{result.shape[1]}x{result.shape[0]}, expected '
                    f'{expected[1]}x{expected[0]}'))

    exact = resize(frame, width=320, height=240)
    out.append(('an explicit size is honoured exactly',
                exact.shape[:2] == (240, 320),
                f'{exact.shape[1]}x{exact.shape[0]} requested 320x240'))
    return out


def check_crop(corpus) -> List[Tuple[str, bool, str]]:
    frame = corpus['cctv/sharpest.jpg']
    out = []

    region = (120, 80, 200, 140)
    result = crop(frame, *region)
    out.append(('crop returns exactly the region asked for',
                result.shape[:2] == (region[3], region[2]),
                f'{result.shape[1]}x{result.shape[0]} for a '
                f'{region[2]}x{region[3]} request'))
    out.append(('the cropped pixels are the pixels that were there',
                np.array_equal(result, frame[80:220, 120:320]),
                'identical to the same slice of the input'))

    # crop raises where roi_crop clips - the documented difference between them
    try:
        crop(frame, 10_000, 10_000, 50, 50)
        refused = False
    except ValueError:
        refused = True
    out.append(('a region entirely outside the frame is refused',
                refused,
                'crop raises where roi_crop would clip'))
    return out


def check_fft_filter(corpus) -> List[Tuple[str, bool, str]]:
    frame = corpus['cctv/sharpest.jpg']
    out = []

    detail = _high_frequency_energy(frame)
    low = _high_frequency_energy(fft_filter(frame, filter_type='lowpass', cutoff=30))
    high = _high_frequency_energy(fft_filter(frame, filter_type='highpass', cutoff=30))

    out.append(('a lowpass removes high-frequency energy',
                low < detail,
                f'Laplacian variance {detail:.0f} -> {low:.0f}'))
    out.append(('a highpass keeps the detail and drops the rest',
                float(fft_filter(frame, filter_type='highpass',
                                 cutoff=30).mean()) < float(frame.mean()),
                f'mean {float(frame.mean()):.1f} -> '
                f'{float(fft_filter(frame, filter_type="highpass", cutoff=30).mean()):.1f}'))

    cutoffs = [_high_frequency_energy(fft_filter(frame, filter_type='lowpass',
                                                 cutoff=c)) for c in (10, 30, 60)]
    out.append(('a wider lowpass keeps more detail',
                cutoffs[0] < cutoffs[1] < cutoffs[2],
                ' -> '.join(f'{c:.0f}' for c in cutoffs) + ' at cutoff 10/30/60'))
    return out


def check_remove_periodic(corpus) -> List[Tuple[str, bool, str]]:
    """Against the sample built with a known periodic interference."""
    noisy = corpus.get('samples/periodic_noise.png')
    if noisy is None:
        return [('the periodic-noise sample is present', False,
                 'samples/periodic_noise.png missing')]

    cleaned = remove_periodic_noise(noisy)
    before = len(detect_periodic_peaks(noisy))
    after = len(detect_periodic_peaks(cleaned))
    return [
        ('removes the periodic peaks it detects',
         after < before,
         f'{before} peaks before, {after} after'),
        ('and changes the image doing so',
         not np.array_equal(cleaned, noisy),
         'the output differs from the input'),
    ]


def check_deblock(corpus) -> List[Tuple[str, bool, str]]:
    frame = _jpeg(corpus['cctv/sharpest.jpg'], 25)
    before = blockiness_score(frame)['blockiness']
    after = blockiness_score(deblock(frame, strength=0.8))['blockiness']
    return [('lowers the blocking it was given',
             after < before,
             f'blockiness {before:.2f} -> {after:.2f} on a Q25 frame')]


CHECKS.update({
    'flip': check_flip,
    'invert': check_invert,
    'rotate': check_rotate,
    'resize': check_resize,
    'crop': check_crop,
    'fft_filter': check_fft_filter,
    'remove_periodic': check_remove_periodic,
    'deblock': check_deblock,
})

# ---- the full declared range ----------------------------------------------
# Until now the checks asserted behaviour at or near each filter's defaults.
# The parameter matrix ran the extremes, but only to see whether they crashed
# - nothing said what `clahe` at clip_limit 10 or `gaussian_blur` at radius 50
# should actually produce. A slider the interface offers is a promise that
# every value on it does something sensible.
#
# Each entry is (filter, parameter, what to measure, which way it should go).
# The range comes from SLIDER_RANGES - the same numbers the panels offer - so
# widening a slider without re-checking the filter shows up here.

MONOTONE_OVER_RANGE = [
    ('clahe', 'clip_limit', lambda i: _local_contrast_score(i), 'up'),
    ('sharpen', 'amount', _high_frequency_energy, 'up'),
    # Not Laplacian variance: it collapses by radius 10 and is flat from
    # there to 50, so the check would have been vacuous over four fifths of
    # the slider. Global contrast keeps falling the whole way - 42.7 at
    # radius 5 down to 21.6 at 50 - because the blur keeps spreading tone
    # long after the fine detail has gone.
    ('gaussian_blur', 'radius', lambda i: float(i.std()), 'down'),
    ('local_contrast', 'strength', lambda i: _local_contrast_score(i, 31), 'up'),
    ('saturation', 'factor',
     lambda i: float(cv2.cvtColor(i, cv2.COLOR_RGB2HSV)[:, :, 1].mean()), 'up'),
    # Not estimate_noise: by h=30 there is almost no noise left to remove, so
    # the reading floors at 0.4 and the top of the slider looks inert. The
    # images keep changing (h=50 differs from h=30 by up to 109 levels), and
    # global contrast tracks it the whole way. check_nl_means still asserts
    # the noise claim itself over the range where it means something.
    ('nl_means', 'h', lambda i: float(i.std()), 'down'),
    ('texture_boost', 'amount', _high_frequency_energy, 'up'),
]


def check_over_range(filter_name: str, parameter: str, measure, direction: str,
                     corpus) -> List[Tuple[str, bool, str]]:
    """Sample a parameter across its whole slider range and hold it to shape."""
    from src.gui.widgets import SLIDER_RANGES
    from src.filters import resolve_filter

    low, high = SLIDER_RANGES[parameter]
    points = [low + (high - low) * i / 5.0 for i in range(6)]
    frame = corpus['cctv/flattest.jpg']
    spec = resolve_filter(filter_name)

    values, failures = [], []
    for point in points:
        try:
            result = spec.fn(frame, **{parameter: point})
        except ValueError as exc:
            failures.append(f'{parameter}={point:g} refused: {exc}')
            continue
        values.append((point, float(measure(result)), result))

    out: List[Tuple[str, bool, str]] = []
    if failures:
        out.append((f'{filter_name}: every offered {parameter} is accepted',
                    False, '; '.join(failures)))
    if len(values) < 3:
        return out

    readings = [v for _, v, _ in values]
    if direction == 'up':
        ordered = all(b >= a - abs(a) * 0.05 - 0.01
                      for a, b in zip(readings, readings[1:]))
        moved = readings[-1] > readings[0]
    else:
        ordered = all(b <= a + abs(a) * 0.05 + 0.01
                      for a, b in zip(readings, readings[1:]))
        moved = readings[-1] < readings[0]

    trace = ', '.join(f'{p:g}:{v:.2f}' for p, v, _ in values)
    out.append((f'{filter_name}: {parameter} moves the result {direction} '
                f'across its whole range',
                ordered and moved,
                trace))

    # A measure that saturates makes the ordering claim above true and
    # meaningless over the saturated part. The upper half of the slider has
    # to still be doing something the measure can see.
    span = abs(readings[-1] - readings[0])
    upper = abs(readings[-1] - readings[len(readings) // 2])
    out.append((f'{filter_name}: the measure still separates values in the '
                f'upper half of the {parameter} range',
                span > 0 and upper > span * 0.05,
                f'the top half moves {upper:.2f} of a total {span:.2f}'))

    # No point on the slider may produce a dead frame. An interface that
    # offers a value it cannot survive is offering a trap.
    dead = [f'{p:g}' for p, _, r in values if float(r.std()) < 0.5]
    out.append((f'{filter_name}: no {parameter} on the slider flattens the image',
                not dead,
                f'flat at {", ".join(dead)}' if dead
                else f'all {len(values)} sampled values keep image structure'))
    return out


def _range_check(filter_name, parameter, measure, direction, existing):
    def combined(corpus):
        results = list(existing(corpus)) if existing else []
        results.extend(check_over_range(filter_name, parameter, measure,
                                        direction, corpus))
        return results
    return combined


for _filter, _param, _measure, _direction in MONOTONE_OVER_RANGE:
    CHECKS[_filter] = _range_check(_filter, _param, _measure, _direction,
                                   CHECKS.get(_filter))

# ---- against somebody else's implementation -------------------------------
# Every other check in this file is internal: the filter is compared against
# its own documented behaviour, or against ground truth this campaign built.
# Both can be self-consistent and wrong together. These compare against
# scipy and scikit-image, which implement the same standard operations by
# different routes and were written by people who have never seen this code.
#
# Exact agreement is not the bar. OpenCV and scipy differ in border handling,
# kernel truncation and rounding, so the question is whether the results are
# the same operation - correlated above 0.99 and within a few levels - not
# whether they are bit-identical.


def _agreement(a: np.ndarray, b: np.ndarray, margin: int = 2) -> Tuple[float, float]:
    """
    Correlation and mean absolute difference between two greyscale results.

    A margin is trimmed because the border is where the two libraries disagree
    by convention rather than by arithmetic: OpenCV replicates the edge pixel,
    scipy reflects it. Comparing the frame including its border reported
    median_filter at 0.988 against scipy and its interior at 0.99998 - the
    same operation, judged differently by two pixels of edge.
    """
    if margin:
        a, b = a[margin:-margin, margin:-margin], b[margin:-margin, margin:-margin]
    x = _gray(a).astype(np.float64).ravel()
    y = _gray(b).astype(np.float64).ravel()
    if x.std() < 1e-9 or y.std() < 1e-9:
        return (1.0 if np.allclose(x, y) else 0.0, float(np.abs(x - y).mean()))
    return (float(np.corrcoef(x, y)[0, 1]), float(np.abs(x - y).mean()))


def check_against_scipy(corpus) -> List[Tuple[str, bool, str]]:
    """Filters whose operation scipy or scikit-image also implements."""
    from scipy import ndimage
    from skimage import exposure, restoration

    frame = corpus['cctv/sharpest.jpg']
    grey = _gray(frame)
    out = []

    # 1. Gaussian blur. scipy convolves in floating point with its own border
    # rule; OpenCV uses a truncated integer kernel.
    for radius in (2.0, 5.0):
        ours = _gray(gaussian_blur(frame, radius=radius))
        theirs = ndimage.gaussian_filter(grey.astype(np.float64), sigma=radius)
        correlation, difference = _agreement(ours, theirs.astype(np.uint8))
        out.append((f'gaussian_blur at radius {radius:g} matches scipy',
                    correlation > 0.999 and difference < 3.0,
                    f'correlation {correlation:.5f}, mean difference '
                    f'{difference:.2f}/255 against scipy.ndimage'))

    # 2. Median filter. The same operation exactly, so agreement should be
    # close to perfect - any real gap is a defect rather than a convention.
    ours = _gray(median_filter(frame, kernel_size=5))
    theirs = ndimage.median_filter(grey, size=5)
    correlation, difference = _agreement(ours, theirs)
    identical = float((ours[4:-4, 4:-4] == theirs[4:-4, 4:-4]).mean() * 100)
    out.append(('median_filter matches scipy',
                correlation > 0.999 and difference < 2.0,
                f'correlation {correlation:.5f}, mean difference '
                f'{difference:.2f}/255, and {identical:.1f}% of interior '
                f'pixels identical to scipy.ndimage'))

    # The border convention itself, stated rather than trimmed away. A frame
    # processed here and the same frame processed elsewhere differ in their
    # outermost pixels, which matters if either is being compared to the other.
    edge_correlation, _ = _agreement(ours, theirs, margin=0)
    out.append(('the two libraries differ only at the frame border',
                edge_correlation < correlation,
                f'including the border the agreement falls to '
                f'{edge_correlation:.5f} from {correlation:.5f} - OpenCV '
                f'replicates the edge pixel, scipy reflects it'))

    # 3. Gamma. skimage.exposure.adjust_gamma is the textbook formula; levels
    # applies the same curve through its own lookup table.
    for gamma in (0.5, 2.0):
        # levels' gamma is the inverse convention of skimage's
        ours = _gray(adjust_levels(frame, gamma=gamma))
        theirs = exposure.adjust_gamma(grey, gamma=1.0 / gamma)
        correlation, difference = _agreement(ours, theirs)
        out.append((f'levels gamma {gamma:g} matches skimage adjust_gamma',
                    correlation > 0.999 and difference < 3.0,
                    f'correlation {correlation:.5f}, mean difference '
                    f'{difference:.2f}/255 against skimage.exposure'))

    # 4. Histogram equalisation on a single channel
    ours = _gray(histogram_equalization(frame, color_mode='grayscale'))
    theirs = (exposure.equalize_hist(grey) * 255).astype(np.uint8)
    correlation, difference = _agreement(ours, theirs)
    out.append(('histeq matches skimage equalize_hist',
                correlation > 0.99 and difference < 6.0,
                f'correlation {correlation:.5f}, mean difference '
                f'{difference:.2f}/255 against skimage.exposure'))

    # 5. Noise estimation. Immerkaer's kernel here, a wavelet estimator there
    # - genuinely different mathematics for the same quantity, which makes
    # this the strongest of these comparisons.
    rng = np.random.default_rng(19)
    flat = np.full((256, 384), 128.0)
    for sigma in (3.0, 8.0):
        noisy = np.clip(flat + rng.normal(0, sigma, flat.shape),
                        0, 255).astype(np.uint8)
        ours = estimate_noise(noisy)
        try:
            theirs = float(restoration.estimate_sigma(noisy, channel_axis=None))
        except ImportError as exc:
            # skimage's estimator needs PyWavelets, which the toolkit itself
            # does not. Say so rather than reporting a pass nobody earned.
            out.append((f'estimate_noise can be compared at sigma {sigma:g}',
                        False, f'reference unavailable: {exc}'))
            continue
        out.append((f'estimate_noise agrees with skimage at sigma {sigma:g}',
                    abs(ours - theirs) < max(0.5, sigma * 0.15),
                    f'{ours:.2f} here, {theirs:.2f} from '
                    f'skimage.restoration, truth {sigma:g}'))

    # 6. Sobel magnitude
    ours = sobel_edges(frame, normalize=True)
    gx = ndimage.sobel(grey.astype(np.float64), axis=1)
    gy = ndimage.sobel(grey.astype(np.float64), axis=0)
    theirs = np.hypot(gx, gy)
    theirs = (theirs * (255.0 / max(theirs.max(), 1e-9))).astype(np.uint8)
    correlation, difference = _agreement(ours, theirs)
    out.append(('sobel matches scipy in shape, if not in scale',
                correlation > 0.99,
                f'correlation {correlation:.5f}, mean difference '
                f'{difference:.2f}/255 against scipy.ndimage'))
    return out


CHECKS['differential'] = check_against_scipy

def check_against_skimage_denoise(corpus) -> List[Tuple[str, bool, str]]:
    """The denoising and sharpening scikit-image also implements."""
    from skimage import filters, restoration, img_as_float, img_as_ubyte

    frame = corpus['cctv/darkest.jpg']
    grey = _gray(frame)
    out = []

    # Non-local means. Different implementations of the same published
    # algorithm, so the results should track each other closely even though
    # the parameterisation differs.
    ours = _gray(nl_means_denoise(frame, h=10))
    theirs = img_as_ubyte(np.clip(restoration.denoise_nl_means(
        img_as_float(grey), h=10 / 255.0, patch_size=7, patch_distance=11,
        fast_mode=True), 0, 1))
    correlation, difference = _agreement(ours, theirs)
    out.append(('nl_means tracks skimage denoise_nl_means',
                correlation > 0.98,
                f'correlation {correlation:.5f}, mean difference '
                f'{difference:.2f}/255 against skimage.restoration'))

    # Both should reduce measured noise from the same starting point
    before = estimate_noise(grey)
    out.append(('both denoisers lower the noise they were given',
                estimate_noise(ours) < before and estimate_noise(theirs) < before,
                f'sigma {before:.2f} -> {estimate_noise(ours):.2f} here, '
                f'{estimate_noise(theirs):.2f} in skimage'))

    # Unsharp masking is a two-line formula, so agreement should be tight
    sharp = corpus['cctv/softest.jpg']
    ours = _gray(unsharp_mask(sharp, radius=2.0, amount=1.0))
    theirs = img_as_ubyte(np.clip(filters.unsharp_mask(
        img_as_float(_gray(sharp)), radius=2.0, amount=1.0), 0, 1))
    correlation, difference = _agreement(ours, theirs)
    out.append(('unsharp_mask matches skimage unsharp_mask',
                correlation > 0.99,
                f'correlation {correlation:.5f}, mean difference '
                f'{difference:.2f}/255 against skimage.filters'))
    return out


def check_solarize(corpus) -> List[Tuple[str, bool, str]]:
    """Solarize is an exact rule, so it can be checked exactly."""
    ramp = cv2.cvtColor(np.tile(np.arange(256, dtype=np.uint8), (8, 1)),
                        cv2.COLOR_GRAY2RGB)
    threshold = 128
    result = solarize(ramp, threshold=threshold)[0, :, 0].astype(int)
    source = np.arange(256)

    # Strictly above: the documented rule is "invert only values above a
    # threshold", and 128 itself passes through at threshold 128. The first
    # version of this used >= and reported a defect that was an off-by-one in
    # the check.
    below = bool((result[:threshold + 1] == source[:threshold + 1]).all())
    above = bool((result[threshold + 1:] == 255 - source[threshold + 1:]).all())
    return [
        ('values at or below the threshold pass through untouched', below,
         f'0-{threshold} unchanged'),
        ('values above the threshold are inverted', above,
         f'{threshold + 1}-255 become 255 minus themselves'),
        ('and the threshold actually moves the boundary',
         not np.array_equal(solarize(ramp, threshold=64),
                            solarize(ramp, threshold=192)),
         'two thresholds give two different results'),
    ]


def check_invert_variants(corpus) -> List[Tuple[str, bool, str]]:
    """Per-channel and luminance inversion, against their formulas."""
    frame = corpus['cctv/sharpest.jpg']
    out = []

    # RGB, because that is what ImageLoader hands the filters. The first
    # version of this listed the channels in BGR order and reported the
    # filter as broken; the filter was right and the check was reading the
    # array in an order the product never produces.
    for index, channel in enumerate(('r', 'g', 'b')):
        result = invert_channel(frame, channel=channel)
        inverted = np.array_equal(result[:, :, index].astype(int),
                                  255 - frame[:, :, index].astype(int))
        others = all(np.array_equal(result[:, :, c], frame[:, :, c])
                     for c in range(3) if c != index)
        out.append((f'inverting {channel} inverts only {channel}',
                    inverted and others,
                    f'channel {index} complemented, the other two untouched'))

    # Luminance inversion has to change brightness while keeping hue
    result = invert_luminance(frame)
    hsv_before = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    hsv_after = cv2.cvtColor(result, cv2.COLOR_RGB2HSV)
    hue_shift = float(np.abs(hsv_after[:, :, 0].astype(int)
                             - hsv_before[:, :, 0].astype(int)).mean())
    brightness = float(result.mean()) - float(frame.mean())
    out.append(('luminance inversion flips brightness and roughly keeps hue',
                abs(brightness) > 10 and hue_shift < 12,
                f'mean brightness {brightness:+.1f}, mean hue shift '
                f'{hue_shift:.1f} degrees of 180'))
    return out


def check_auto_levels(corpus) -> List[Tuple[str, bool, str]]:
    """The automatic stretches, on a frame that has room to stretch."""
    # Deliberately squeezed into the middle of the range. The corpus frames
    # already span 228 of 255, so on those an automatic stretch has nothing
    # left to do and `after >= before` passes for a filter that does nothing -
    # which is exactly how this check survived mutation.
    squeezed = (corpus['cctv/flattest.jpg'].astype(np.float32) * 0.35
                + 80).clip(0, 255).astype(np.uint8)
    frame = squeezed
    out = []

    def span(image):
        grey = _gray(image)
        return float(np.percentile(grey, 99) - np.percentile(grey, 1))

    before = span(frame)
    for name, result in (('auto_levels', auto_levels(frame)),
                         ('auto_contrast', auto_contrast(frame))):
        after = span(result)
        out.append((f'{name} widens the tonal span of a compressed frame',
                    after > before * 1.5,
                    f'1-99 percentile span {before:.0f} -> {after:.0f}'))

    # Running it twice must not keep stretching without limit
    once = auto_levels(frame)
    twice = auto_levels(once)
    drift = float(np.abs(twice.astype(int) - once.astype(int)).mean())
    out.append(('a second auto_levels barely changes the first',
                drift < 3.0,
                f'mean change on the second pass {drift:.2f}/255'))
    return out


CHECKS['differential_denoise'] = check_against_skimage_denoise
CHECKS['solarize'] = check_solarize
CHECKS['invert_channel'] = check_invert_variants
CHECKS['auto_levels'] = check_auto_levels

def check_per_channel(corpus) -> List[Tuple[str, bool, str]]:
    """
    Every filter that takes a `channel` must act on the channel named.

    This is where a colour-order confusion hides, and it hid one for sixteen
    hours of this campaign - in the harness rather than the filters, but the
    check that would have caught it either way did not exist. Four filters
    take the parameter; only `invert_channel` was verified.

    The image is RGB, because that is what `ImageLoader` produces and what
    every filter here expects.
    """
    from src.filters import resolve_filter

    # A frame where the three channels are unmistakably different, so a
    # filter acting on the wrong one cannot look like acting on the right one
    frame = np.zeros((64, 96, 3), np.uint8)
    frame[:, :, 0] = 200        # R
    frame[:, :, 1] = 120        # G
    frame[:, :, 2] = 60         # B

    cases = [
        ('contrast_brightness', {'brightness': 40}),
        ('levels', {'gamma': 0.5}),
        ('curves', {'preset': 'lift_shadows'}),
        ('invert_channel', {}),
    ]
    names = ('r', 'g', 'b')
    out = []

    for filter_name, params in cases:
        spec = resolve_filter(filter_name)
        for index, channel in enumerate(names):
            try:
                result = spec.fn(frame, channel=channel, **params)
            except Exception as exc:
                out.append((f'{filter_name} accepts channel={channel!r}',
                            False, f'{type(exc).__name__}: {exc}'))
                continue

            moved = [i for i in range(3)
                     if not np.array_equal(result[:, :, i], frame[:, :, i])]
            out.append((f'{filter_name} with channel={channel!r} touches only '
                        f'{channel}',
                        moved == [index],
                        f'array index {moved} changed, expected [{index}] '
                        f'({channel} in the RGB the loader produces)'))
    return out


CHECKS['per_channel'] = check_per_channel

def _step_edge(height: int = 96, width: int = 128, at: int = 64) -> np.ndarray:
    """A frame with one vertical edge at a known column."""
    frame = np.full((height, width, 3), 40, np.uint8)
    frame[:, at:] = 210
    return frame


def check_canny(corpus) -> List[Tuple[str, bool, str]]:
    """Edge maps are binary, and the edge has to be where the edge is."""
    out = []
    edge_at = 64
    frame = _step_edge(at=edge_at)

    for name, result in (('canny', canny_edges(frame, 50, 150)),
                         ('auto_canny', auto_canny(frame))):
        values = np.unique(result)
        out.append((f'{name} returns a binary map',
                    set(values.tolist()) <= {0, 255},
                    f'distinct values {values.tolist()}'))

        columns = np.nonzero(result.any(axis=0))[0]
        found = int(columns.mean()) if columns.size else -1
        out.append((f'{name} puts the edge where the edge is',
                    columns.size > 0 and abs(found - edge_at) <= 2,
                    f'edge pixels centred on column {found}, the step is at '
                    f'{edge_at}'))

        # A flat frame has no edges, and saying so is the other half
        flat = canny_edges(np.full((64, 64, 3), 128, np.uint8), 50, 150) \
            if name == 'canny' else auto_canny(np.full((64, 64, 3), 128, np.uint8))
        out.append((f'{name} finds nothing in a flat frame',
                    int(flat.sum()) == 0,
                    f'{int((flat > 0).sum())} edge pixels in a uniform image'))

    # A higher threshold cannot find more edges than a lower one
    counts = [int((canny_edges(corpus['cctv/sharpest.jpg'], low, low * 3) > 0).sum())
              for low in (20, 60, 120)]
    out.append(('a higher canny threshold finds fewer edges',
                counts[0] > counts[1] > counts[2],
                ' -> '.join(str(c) for c in counts) + ' edge pixels at low '
                'threshold 20/60/120'))
    return out


def check_roi_crop(corpus) -> List[Tuple[str, bool, str]]:
    """roi_crop clips where crop raises - the documented difference."""
    from src.filters import resolve_filter

    # roi_crop is a registry adapter around extract_roi, not a module export
    roi_crop = resolve_filter('roi_crop').fn

    frame = corpus['cctv/sharpest.jpg']
    height, width = frame.shape[:2]
    out = []

    result = roi_crop(frame, 120, 80, 200, 140)
    out.append(('returns exactly the region asked for',
                result.shape[:2] == (140, 200)
                and np.array_equal(result, frame[80:220, 120:320]),
                f'{result.shape[1]}x{result.shape[0]}, identical to the slice'))

    # Oversized: clipped to the frame rather than refused
    clipped = roi_crop(frame, width - 50, height - 30, 500, 500)
    out.append(('an oversized region is clipped, not refused',
                clipped.shape[0] == 30 and clipped.shape[1] == 50,
                f'asked for 500x500 at the corner, got '
                f'{clipped.shape[1]}x{clipped.shape[0]}'))
    return out


def check_bit_plane(corpus) -> List[Tuple[str, bool, str]]:
    """Bit planes are one bit, and the top one tracks brightness."""
    frame = corpus['cctv/sharpest.jpg']
    grey = _gray(frame)
    out = []

    for plane in range(8):
        result = extract_bit_plane(frame, plane)
        values = np.unique(result)
        out.append((f'plane {plane} is binary',
                    len(values) <= 2,
                    f'values {values.tolist()}'))

    # The most significant plane is exactly "is this pixel above 127"
    top = extract_bit_plane(frame, 7)
    expected = ((grey >= 128).astype(np.uint8) * 255)
    agreement = float((_gray(top) == expected).mean() * 100)
    out.append(('plane 7 marks the pixels at or above 128',
                agreement > 99.0,
                f'{agreement:.2f}% of pixels agree with a 128 threshold'))
    return out


def check_noise_map(corpus) -> List[Tuple[str, bool, str]]:
    """The map has to be bright where the noise actually is."""
    rng = np.random.default_rng(5)
    base = np.full((256, 384, 3), 120, np.uint8)
    quiet = np.clip(base + rng.normal(0, 1.5, base.shape), 0, 255).astype(np.uint8)
    planted = quiet.copy()
    x, y, w, h = 240, 128, 96, 96
    planted[y:y+h, x:x+w] = np.clip(
        base[y:y+h, x:x+w] + rng.normal(0, 20, (h, w, 3)), 0, 255).astype(np.uint8)

    result = _gray(noise_map(planted, block_size=16))
    inside = float(result[y:y+h, x:x+w].mean())
    mask = np.ones(result.shape, bool)
    mask[y:y+h, x:x+w] = False
    outside = float(result[mask].mean())

    return [
        ('the map is brighter where the noise was planted',
         inside > outside * 1.5,
         f'mean {inside:.1f} inside the noisy patch against {outside:.1f} '
         f'outside'),
        ('and it covers the frame',
         result.shape == planted.shape[:2],
         f'{result.shape[1]}x{result.shape[0]} for a '
         f'{planted.shape[1]}x{planted.shape[0]} frame'),
    ]


def check_temperature(corpus) -> List[Tuple[str, bool, str]]:
    """Warmer means more red and less blue - in RGB, indices 0 and 2."""
    frame = corpus['cctv/softest.jpg']
    out = []

    warm = adjust_temperature(frame, temperature=60)
    cool = adjust_temperature(frame, temperature=-60)

    def channel(image, index):
        return float(image[:, :, index].mean())

    out.append(('warming raises red and lowers blue',
                channel(warm, 0) > channel(frame, 0)
                and channel(warm, 2) < channel(frame, 2),
                f'R {channel(frame, 0):.1f}->{channel(warm, 0):.1f}, '
                f'B {channel(frame, 2):.1f}->{channel(warm, 2):.1f}'))
    out.append(('cooling does the opposite',
                channel(cool, 0) < channel(frame, 0)
                and channel(cool, 2) > channel(frame, 2),
                f'R {channel(frame, 0):.1f}->{channel(cool, 0):.1f}, '
                f'B {channel(frame, 2):.1f}->{channel(cool, 2):.1f}'))
    out.append(('temperature 0 leaves the frame alone',
                np.array_equal(adjust_temperature(frame, temperature=0), frame),
                'no shift requested'))
    return out


def check_aspect(corpus) -> List[Tuple[str, bool, str]]:
    """Pixel aspect and frame fitting are arithmetic, so check the arithmetic."""
    frame = corpus['cctv/sharpest.jpg']
    height, width = frame.shape[:2]
    out = []

    for ratio in (0.5, 2.0):
        result = correct_pixel_aspect(frame, pixel_aspect=ratio)
        # Non-square pixels are corrected by stretching one axis
        stretched = (result.shape[1] != width) or (result.shape[0] != height)
        out.append((f'pixel aspect {ratio:g} rescales the frame',
                    stretched,
                    f'{width}x{height} became '
                    f'{result.shape[1]}x{result.shape[0]}'))

    out.append(('a pixel aspect of 1.0 is already square',
                np.array_equal(correct_pixel_aspect(frame, pixel_aspect=1.0),
                               frame),
                'nothing to correct'))

    for target in (16 / 9, 4 / 3):
        result = fit_to_aspect(frame, target_ratio=target, mode='pad')
        actual = result.shape[1] / result.shape[0]
        out.append((f'fitting to {target:.2f} gives that ratio',
                    abs(actual - target) < 0.02,
                    f'{result.shape[1]}x{result.shape[0]} is {actual:.3f}'))
    return out


CHECKS.update({
    'canny': check_canny,
    'roi_crop': check_roi_crop,
    'bit_plane': check_bit_plane,
    'noise_map': check_noise_map,
    'temperature': check_temperature,
    'pixel_aspect': check_aspect,
})
