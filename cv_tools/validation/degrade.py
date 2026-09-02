"""
A degradation model for CCTV footage, for validating filters against ground truth.

The filter tests assert that the arithmetic is right. They cannot say whether a
filter's defaults *help* on the material this toolkit exists for, because a
clean synthetic chart is not a night-time DVR frame. Answering that needs an
image whose undegraded form is known, so the two can be compared.

That is what this module builds: it takes a clean image and applies degradations
that a real camera and recorder impose, each parameterised and reproducible, so
``benchmark.py`` can measure how far a filter moves the result back toward the
original.

**What this is not.** Simulated degradation is a model, and a model is not
evidence. It reproduces the *mechanisms* - shot noise, quantised transform
blocks, lost resolution, non-square pixels - with the physics of each written
out below, and a filter that fails here would certainly fail on real footage.
But agreement here does not establish that a filter's defaults are right on any
particular recorder, whose encoder, denoiser and sharpener are proprietary and
applied before anything reaches a file. Real footage is the only thing that
settles that, and this module is built so it drops in as ground truth the moment
a labelled corpus exists.

**On the codec.** ``codec_generations`` encodes through OpenCV's own writers.
H.264 is usually unavailable in a headless build, so it falls back to MPEG-4
Part 2 or MJPEG - which is less of a compromise than it sounds, since a large
part of the installed DVR base records exactly those two.
"""

import os
from typing import Any, Dict, List, Optional, Sequence, Tuple

import cv2
import numpy as np

# Probing encoders means opening ones this build does not have, and libav logs
# each failure straight to stderr - below OpenCV's own logger, so setting that
# alone does not silence it. AV_LOG_QUIET is -8. setdefault, so anyone
# debugging a codec problem can still ask for the output.
os.environ.setdefault('OPENCV_FFMPEG_LOGLEVEL', '-8')

# Encoders tried in order of preference. H.264 first because it is what modern
# recorders use; the MPEG-4 and MJPEG fallbacks are what older DVRs write, so a
# fallback is still a realistic recorder rather than a substitute for one.
_CODECS: List[Tuple[str, str]] = [
    ('avc1', '.mp4'),
    ('mp4v', '.mp4'),
    ('XVID', '.avi'),
    ('MJPG', '.avi'),
]

# The luminance quantisation table from the JPEG specification (Annex K). Real
# 8x8 transform codecs quantise more coarsely toward high frequencies, and this
# is the canonical statement of that shape.
_JPEG_LUMA_Q = np.array([
    [16, 11, 10, 16, 24, 40, 51, 61],
    [12, 12, 14, 19, 26, 58, 60, 55],
    [14, 13, 16, 24, 40, 57, 69, 56],
    [14, 17, 22, 29, 51, 87, 80, 62],
    [18, 22, 37, 56, 68, 109, 103, 77],
    [24, 35, 55, 64, 81, 104, 113, 92],
    [49, 64, 78, 87, 103, 121, 120, 101],
    [72, 92, 95, 98, 112, 100, 103, 99],
], dtype=np.float32)


def _as_float(image: np.ndarray) -> np.ndarray:
    return image.astype(np.float32)


def _to_uint8(image: np.ndarray) -> np.ndarray:
    return np.clip(image, 0, 255).astype(np.uint8)


def sensor_noise(
    image: np.ndarray,
    photon_scale: float = 40.0,
    read_sigma: float = 3.0,
    seed: Optional[int] = None,
) -> np.ndarray:
    """
    Add Poisson shot noise and Gaussian read noise, the way a sensor makes them.

    Noise on a real frame is not additive Gaussian at a single level. Photon
    arrival is Poisson, so the noise **scales with the square root of the
    signal** - shadows are proportionally far noisier than highlights, which is
    exactly why night footage falls apart in the dark areas first. Read noise on
    top of that is signal-independent and Gaussian.

    Modelling it as uniform Gaussian, as most test fixtures do, makes denoisers
    look better than they are: it hands them a stationary noise field, when the
    hard part of the real problem is that the noise level varies across the
    frame.

    Args:
        image: Clean image, uint8
        photon_scale: Full-well electrons at white. Lower is noisier; 40 is a
            small sensor at high gain, 400 a well-exposed one
        read_sigma: Standard deviation of read noise, in 8-bit levels
        seed: Seed for reproducibility

    Returns:
        Noisy image, uint8
    """
    rng = np.random.default_rng(seed)
    signal = _as_float(image) / 255.0

    # Poisson in electrons, back to levels. photon_scale is the electron count
    # a full-white pixel collects.
    electrons = rng.poisson(np.clip(signal, 0.0, None) * photon_scale)
    shot = electrons.astype(np.float32) / max(photon_scale, 1e-6) * 255.0

    return _to_uint8(shot + rng.normal(0.0, read_sigma, size=signal.shape))


def low_light(
    image: np.ndarray,
    exposure: float = 0.25,
    black_level: int = 6,
    photon_scale: float = 30.0,
    read_sigma: float = 3.5,
    seed: Optional[int] = None,
) -> np.ndarray:
    """
    Underexpose the scene, then add the noise that underexposure exposes.

    Order matters and is the whole point. A camera loses light *before* the
    sensor reads it, so the noise is generated against the darkened signal - the
    shot noise is computed from the few photons that actually arrived. Darkening
    an already-noisy image instead would scale the noise down with the signal
    and produce something far cleaner than any real night frame.

    A black level is added last, as recorders do, so the shadows sit above zero
    and no longer clip to true black.

    Args:
        image: Clean image, uint8
        exposure: Fraction of the original light reaching the sensor
        black_level: Pedestal added after exposure, in 8-bit levels
        photon_scale: Full-well electrons at white, as in ``sensor_noise``
        read_sigma: Read noise standard deviation, in levels
        seed: Seed for reproducibility

    Returns:
        Dark, noisy image, uint8
    """
    darkened = _to_uint8(_as_float(image) * float(exposure))
    noisy = sensor_noise(darkened, photon_scale=photon_scale,
                         read_sigma=read_sigma, seed=seed)
    return _to_uint8(_as_float(noisy) + float(black_level))


def ir_night(
    image: np.ndarray,
    exposure: float = 0.5,
    falloff: float = 0.65,
    photon_scale: float = 35.0,
    read_sigma: float = 3.0,
    seed: Optional[int] = None,
) -> np.ndarray:
    """
    Simulate an infra-red illuminated night frame.

    Three things happen when a camera switches to night mode, and all three
    matter to a filter:

    1. The IR-cut filter swings away and the image becomes **monochrome**. Any
       colour-based filter has nothing to work with from here on.
    2. The scene is lit by the camera's own IR LEDs, so illumination falls off
       from the centre and with distance - a strong vignette that is *part of
       the lighting*, not a lens artefact, and which local contrast operators
       will happily amplify into a halo.
    3. Gain rises, so noise rises with it.

    Args:
        image: Clean image, uint8
        exposure: Overall light level before falloff
        falloff: Illumination remaining at the frame corners, 0-1. Lower is a
            tighter IR beam
        photon_scale: Full-well electrons at white
        read_sigma: Read noise standard deviation, in levels
        seed: Seed for reproducibility

    Returns:
        Monochrome, vignetted, noisy 3-channel image, uint8
    """
    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    signal = _as_float(grey) * float(exposure)

    height, width = signal.shape[:2]
    ys, xs = np.mgrid[0:height, 0:width].astype(np.float32)
    cy, cx = (height - 1) / 2.0, (width - 1) / 2.0
    radius = np.sqrt(((xs - cx) / max(cx, 1)) ** 2 + ((ys - cy) / max(cy, 1)) ** 2)
    # Normalised so the centre keeps full illumination and the corners keep
    # `falloff` of it.
    illumination = 1.0 - (1.0 - float(falloff)) * np.clip(radius / np.sqrt(2.0), 0.0, 1.0)

    lit = sensor_noise(_to_uint8(signal * illumination),
                       photon_scale=photon_scale, read_sigma=read_sigma, seed=seed)
    return cv2.cvtColor(lit, cv2.COLOR_GRAY2BGR)


def block_compression(image: np.ndarray, severity: float = 4.0) -> np.ndarray:
    """
    Quantise 8x8 DCT blocks, producing the blocking a starved encoder produces.

    This is the controllable counterpart to ``codec_generations``: a real
    encoder gives realistic artefacts but almost no control over how severe they
    are, since OpenCV's writers expose no bitrate. Quantising the transform
    directly gives a severity dial, which is what a benchmark sweep needs.

    The quantisation table is JPEG's Annex K luminance table scaled by
    ``severity``, so coarseness grows toward high frequencies exactly as it does
    in a real codec. What this does *not* model is motion compensation: the
    smearing of a P-frame that referenced a badly coded neighbour has no
    equivalent here.

    Args:
        image: Input image, uint8
        severity: Multiplier on the quantisation table. 1.0 is roughly JPEG
            quality 50; 8.0 is severe blocking

    Returns:
        Blocked image, uint8
    """
    if severity <= 0:
        return image.copy()

    table = _JPEG_LUMA_Q * float(severity)
    working = image if image.ndim == 3 else image[:, :, None]
    height, width = working.shape[:2]

    # Pad to whole blocks, then trim back, so edge blocks quantise like any
    # other rather than being left untouched.
    pad_y, pad_x = (-height) % 8, (-width) % 8
    padded = cv2.copyMakeBorder(working, 0, pad_y, 0, pad_x, cv2.BORDER_REPLICATE)
    if padded.ndim == 2:
        padded = padded[:, :, None]

    out = np.empty_like(padded, dtype=np.float32)
    for channel in range(padded.shape[2]):
        # Centre on zero the way JPEG does before the transform.
        plane = padded[:, :, channel].astype(np.float32) - 128.0
        for y in range(0, plane.shape[0], 8):
            for x in range(0, plane.shape[1], 8):
                block = cv2.dct(plane[y:y + 8, x:x + 8])
                block = np.round(block / table) * table
                out[y:y + 8, x:x + 8, channel] = cv2.idct(block)

    result = _to_uint8(out[:height, :width] + 128.0)
    return result if image.ndim == 3 else result[:, :, 0]


def codec_generations(
    image: np.ndarray,
    generations: int = 1,
    fps: int = 12,
    frames: int = 6,
    workdir: Optional[str] = None,
) -> np.ndarray:
    """
    Encode and decode the frame through a real video codec, N times over.

    Evidence rarely reaches an examiner in the form the recorder wrote. It is
    exported from the DVR, re-wrapped by whatever software the officer had,
    perhaps emailed and re-encoded again. Each generation quantises what the
    last one already quantised, and the damage compounds in a way a single pass
    does not show.

    Which encoder is used depends on the build - H.264 is often absent from a
    headless OpenCV. The fallbacks, MPEG-4 Part 2 and MJPEG, are what a large
    part of the installed DVR base records anyway. The codec actually used is
    reported by ``last_codec``.

    Args:
        image: Input image, uint8, 3-channel
        generations: How many encode/decode passes to apply
        fps: Frame rate written into the container
        frames: Frames written per pass; some encoders need a short run-up
            before they emit a decodable frame
        workdir: Directory for the intermediate files. A temporary one is used
            and removed if omitted

    Returns:
        The frame after ``generations`` passes, uint8

    Raises:
        RuntimeError: If no encoder in this build could be opened
    """
    import shutil
    import tempfile
    from pathlib import Path

    if generations <= 0:
        return image.copy()

    frame = image if image.ndim == 3 else cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    height, width = frame.shape[:2]
    # Most encoders reject odd dimensions; crop rather than pad so no invented
    # pixels enter the measurement.
    frame = frame[:height - (height % 2), :width - (width % 2)]
    height, width = frame.shape[:2]

    owned = workdir is None
    directory = Path(tempfile.mkdtemp(prefix='cvtools-codec-') if owned else workdir)

    # Probing encoders is expected to fail down the list until one opens, and
    # OpenCV logs each failure at ERROR. Quieten it so a normal fallback does
    # not look like a fault, and restore the level afterwards.
    try:
        previous_log_level = cv2.utils.logging.getLogLevel()
        cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_SILENT)
    except AttributeError:                  # pragma: no cover - older OpenCV
        previous_log_level = None

    try:
        current = frame
        for generation in range(int(generations)):
            written = None
            for fourcc, suffix in _CODECS:
                path = directory / f'gen{generation}{suffix}'
                writer = cv2.VideoWriter(
                    str(path), cv2.VideoWriter_fourcc(*fourcc), fps, (width, height))
                if not writer.isOpened():
                    writer.release()
                    continue
                for _ in range(int(frames)):
                    writer.write(current)
                writer.release()

                capture = cv2.VideoCapture(str(path))
                ok, decoded = capture.read()
                capture.release()
                if ok and decoded is not None:
                    written = decoded
                    codec_generations.last_codec = fourcc
                    break

            if written is None:
                raise RuntimeError(
                    'No usable video encoder in this OpenCV build; tried '
                    + ', '.join(name for name, _ in _CODECS))
            current = written
        return current
    finally:
        if previous_log_level is not None:
            cv2.utils.logging.setLogLevel(previous_log_level)
        if owned:
            shutil.rmtree(directory, ignore_errors=True)


codec_generations.last_codec = None


def motion_blur(image: np.ndarray, length: int = 9, angle: float = 0.0) -> np.ndarray:
    """
    Blur along a direction, as a subject moving during the exposure does.

    A low frame rate implies a long exposure, so CCTV motion blur is usually
    worse than the frame rate alone suggests. Kept deliberately simple and
    linear: it is the point-spread function ``motion_deblur.py`` assumes, so a
    deconvolution benchmark is measuring the deconvolution rather than a
    mismatch between two different blur models.

    Args:
        image: Input image, uint8
        length: Blur length in pixels
        angle: Direction in degrees

    Returns:
        Blurred image, uint8
    """
    length = max(int(length), 1)
    if length == 1:
        return image.copy()

    kernel = np.zeros((length, length), dtype=np.float32)
    kernel[length // 2, :] = 1.0
    matrix = cv2.getRotationMatrix2D((length / 2 - 0.5, length / 2 - 0.5), angle, 1.0)
    kernel = cv2.warpAffine(kernel, matrix, (length, length))
    total = kernel.sum()
    if total <= 0:                       # a rotation that emptied the kernel
        return image.copy()
    return cv2.filter2D(image, -1, kernel / total)


def resolution_loss(image: np.ndarray, factor: float = 0.5) -> np.ndarray:
    """
    Downscale and scale back, the way an under-resolved camera loses detail.

    The frame keeps its stated pixel dimensions and loses the detail behind
    them, which is the usual real situation: a 1080p stream from a camera whose
    optics and encoder never delivered 1080p of actual information. Area
    averaging down, bilinear back up, since that is what a recorder's scaler
    does rather than anything sharper.

    Args:
        image: Input image, uint8
        factor: Fraction of the original resolution to keep, 0-1

    Returns:
        Image at its original size with detail below the cutoff removed, uint8
    """
    factor = float(np.clip(factor, 0.01, 1.0))
    if factor >= 1.0:
        return image.copy()

    height, width = image.shape[:2]
    small = cv2.resize(image, (max(int(width * factor), 1), max(int(height * factor), 1)),
                       interpolation=cv2.INTER_AREA)
    return cv2.resize(small, (width, height), interpolation=cv2.INTER_LINEAR)


def anamorphic(image: np.ndarray, pixel_aspect: float = 1.094) -> np.ndarray:
    """
    Store the frame with non-square pixels, as standard-definition CCTV does.

    D1 and 4CIF footage is 704x480 or 704x576 displayed at 4:3, so its pixels
    are not square. Handed to a measurement tool as if they were, every distance
    is wrong by that ratio - and wrong silently, since nothing about the array
    says so. The default is PAL 4:3.

    Args:
        image: Input image, uint8
        pixel_aspect: Stored pixel width divided by height

    Returns:
        Image resampled to the stored, non-square-pixel geometry, uint8
    """
    height, width = image.shape[:2]
    stored_width = max(int(round(width / float(pixel_aspect))), 1)
    return cv2.resize(image, (stored_width, height), interpolation=cv2.INTER_AREA)


def interlace(image: np.ndarray, shift: int = 3) -> np.ndarray:
    """
    Comb the frame into two fields offset in time.

    An interlaced recorder samples odd and even lines at different instants. On
    anything moving this produces the familiar comb, and it defeats vertical
    gradient operators in particular: an edge detector reads the field boundary
    as a horizontal edge on every other line.

    Args:
        image: Input image, uint8
        shift: Horizontal displacement between the two fields, in pixels

    Returns:
        Combed image, uint8
    """
    if shift == 0:
        return image.copy()
    out = image.copy()
    # Shift the odd field only: the even field is the reference instant.
    out[1::2] = np.roll(image[1::2], int(shift), axis=1)
    return out


# ---- presets ------------------------------------------------------------

# Each preset is an ordered chain, applied in the order given. The order is the
# physical one - light is lost at the lens, noise is added at the sensor, blur
# happens during the exposure, and only then does the recorder scale and encode.
PRESETS: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {
    'daytime_dvr': [
        ('resolution_loss', {'factor': 0.6}),
        ('sensor_noise', {'photon_scale': 200.0, 'read_sigma': 2.0}),
        ('block_compression', {'severity': 3.0}),
    ],
    'night_ir': [
        ('ir_night', {'exposure': 0.5, 'falloff': 0.6}),
        ('resolution_loss', {'factor': 0.55}),
        ('block_compression', {'severity': 5.0}),
    ],
    'low_light_colour': [
        ('low_light', {'exposure': 0.22}),
        ('resolution_loss', {'factor': 0.6}),
        ('block_compression', {'severity': 4.0}),
    ],
    'motion_night': [
        ('low_light', {'exposure': 0.3}),
        ('motion_blur', {'length': 11, 'angle': 15.0}),
        ('block_compression', {'severity': 4.0}),
    ],
    'exported_evidence': [
        ('resolution_loss', {'factor': 0.7}),
        ('sensor_noise', {'photon_scale': 120.0, 'read_sigma': 2.5}),
        ('codec_generations', {'generations': 3}),
    ],
    'interlaced_sd': [
        ('resolution_loss', {'factor': 0.5}),
        ('interlace', {'shift': 3}),
        ('block_compression', {'severity': 3.5}),
    ],
}

DEGRADATIONS = {
    'sensor_noise': sensor_noise,
    'low_light': low_light,
    'ir_night': ir_night,
    'block_compression': block_compression,
    'codec_generations': codec_generations,
    'motion_blur': motion_blur,
    'resolution_loss': resolution_loss,
    'anamorphic': anamorphic,
    'interlace': interlace,
}


def degrade(
    image: np.ndarray,
    chain: Sequence[Tuple[str, Dict[str, Any]]],
    seed: Optional[int] = None,
) -> np.ndarray:
    """
    Apply an ordered degradation chain.

    Args:
        image: Clean image, uint8
        chain: Ordered ``(name, params)`` pairs, names from ``DEGRADATIONS``
        seed: Seed handed to every stage that takes one, so a whole chain is
            reproducible from a single number

    Returns:
        Degraded image, uint8

    Raises:
        KeyError: If a stage names a degradation that does not exist
    """
    result = image
    for index, (name, params) in enumerate(chain):
        if name not in DEGRADATIONS:
            raise KeyError(f"Unknown degradation '{name}'. "
                           f"Available: {', '.join(sorted(DEGRADATIONS))}")
        function = DEGRADATIONS[name]
        arguments = dict(params)
        if seed is not None and 'seed' in function.__code__.co_varnames:
            # Vary per stage, so two noise stages in one chain do not share a
            # realisation, while the chain as a whole stays reproducible.
            arguments.setdefault('seed', seed + index)
        result = function(result, **arguments)
    return result


def degrade_preset(image: np.ndarray, preset: str,
                   seed: Optional[int] = None) -> np.ndarray:
    """
    Apply a named preset from ``PRESETS``.

    Args:
        image: Clean image, uint8
        preset: Preset name
        seed: Seed for reproducibility

    Returns:
        Degraded image, uint8

    Raises:
        KeyError: If the preset does not exist
    """
    if preset not in PRESETS:
        raise KeyError(f"Unknown preset '{preset}'. "
                       f"Available: {', '.join(sorted(PRESETS))}")
    return degrade(image, PRESETS[preset], seed=seed)
