"""Unit tests for the Sprint 3 forensic filters."""

import io
import struct
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from src.filters import (
    check_thumbnail_mismatch,
    check_timestamps,
    detect_editing_software,
    extract_thumbnail,
    metadata_report,
    parse_exif_datetime,
    read_exif,
)
from src.filters import (
    apply_psf,
    average_frames,
    deblur_defocus,
    deblur_motion,
    deblur_sweep,
    defocus_psf,
    detect_copy_move,
    detect_periodic_peaks,
    draw_clone_regions,
    ela_stats,
    error_level_analysis,
    estimate_noise,
    estimate_snr,
    fft_filter,
    fft_magnitude_spectrum,
    focus_score,
    frame_difference,
    ghost_map,
    ghost_report,
    highlight_clones,
    integrate_frames,
    median_frames,
    motion_blur_psf,
    noise_map,
    noise_report,
    recompress,
    remove_periodic_noise,
    sharpest_frames,
    wiener_deconvolution,
)


def textured(height: int = 128, width: int = 160, seed: int = 3) -> np.ndarray:
    """Textured RGB image with enough structure for block matching."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:height, 0:width]
    image = np.zeros((height, width, 3), dtype=np.float32)
    image[:, :, 0] = 120 + 40 * np.sin(xx / 11.0) + 20 * np.cos(yy / 13.0)
    image[:, :, 1] = 130 + 35 * np.sin((xx + yy) / 9.0)
    image[:, :, 2] = 110 + 30 * np.cos(xx / 7.0) + 25 * np.sin(yy / 17.0)
    image += rng.normal(0, 4.0, image.shape)
    return np.clip(image, 0, 255).astype(np.uint8)


def cloned(shift_y: int = 40, shift_x: int = 60) -> np.ndarray:
    """Textured image with a 32x32 patch duplicated at a known offset."""
    image = textured()
    patch = image[10:42, 10:42].copy()
    image[10 + shift_y:42 + shift_y, 10 + shift_x:42 + shift_x] = patch
    return image


def detailed(height: int = 128, width: int = 160) -> np.ndarray:
    """
    Sharp, noise-free structure for deconvolution tests.

    Deliberately without random noise: noise is not recoverable information, so
    an image whose only high-frequency content is noise cannot demonstrate that
    deblurring works - the blur removes the noise and deconvolution cannot put
    it back.
    """
    image = np.full((height, width, 3), 40, dtype=np.uint8)

    for index in range(4, width - 8, 16):
        cv2.rectangle(image, (index, 12), (index + 7, height - 12), (215, 215, 215), -1)
    for index in range(20, height - 20, 24):
        cv2.line(image, (0, index), (width, index), (90, 160, 220), 2)

    cv2.circle(image, (width // 3, height // 2), 18, (240, 90, 60), -1)
    cv2.putText(image, 'AB 123', (12, height - 18), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (250, 250, 250), 1, cv2.LINE_AA)

    return image


def flat_gray(height: int = 64, width: int = 64, value: int = 128) -> np.ndarray:
    return np.full((height, width, 3), value, dtype=np.uint8)


def noisy(sigma: float = 20.0, seed: int = 1) -> np.ndarray:
    rng = np.random.default_rng(seed)
    base = np.full((96, 96, 3), 128.0)
    return np.clip(base + rng.normal(0, sigma, base.shape), 0, 255).astype(np.uint8)


class TestELA(unittest.TestCase):

    def test_recompress_preserves_shape(self):
        image = textured()
        result = recompress(image, quality=90)
        self.assertEqual(result.shape, image.shape)
        self.assertEqual(result.dtype, np.uint8)

    def test_recompress_changes_pixels(self):
        image = textured()
        self.assertFalse(np.array_equal(recompress(image, quality=40), image))

    def test_recompress_rejects_bad_quality(self):
        for quality in (0, 101):
            with self.subTest(quality=quality):
                with self.assertRaises(ValueError):
                    recompress(textured(), quality=quality)

    def test_lower_quality_produces_more_error(self):
        image = textured()
        high = error_level_analysis(image, quality=95, scale=1.0, grayscale=True)
        low = error_level_analysis(image, quality=30, scale=1.0, grayscale=True)
        self.assertGreater(low.mean(), high.mean())

    def test_returns_rgb_by_default(self):
        result = error_level_analysis(textured())
        self.assertEqual(result.ndim, 3)
        self.assertEqual(result.shape[2], 3)

    def test_grayscale_returns_single_channel(self):
        result = error_level_analysis(textured(), grayscale=True)
        self.assertEqual(result.ndim, 2)

    def test_auto_scale_uses_full_range(self):
        result = error_level_analysis(textured(), quality=60)
        self.assertEqual(result.max(), 255)

    def test_accepts_grayscale_input(self):
        gray = cv2.cvtColor(textured(), cv2.COLOR_RGB2GRAY)
        self.assertEqual(error_level_analysis(gray).shape[:2], gray.shape)

    def test_stats_locate_hottest_block(self):
        stats = ela_stats(textured(), quality=90, block_size=16)
        self.assertIn('hottest_block', stats)
        self.assertGreaterEqual(stats['max_error'], stats['mean_error'])
        self.assertEqual(stats['block_grid'].ndim, 2)

    def test_stats_reject_oversized_block(self):
        with self.assertRaises(ValueError):
            ela_stats(textured(64, 64), block_size=128)

    def test_stats_reject_tiny_block(self):
        with self.assertRaises(ValueError):
            ela_stats(textured(), block_size=1)


class TestFFT(unittest.TestCase):

    def test_spectrum_shape_and_dtype(self):
        image = textured()
        spectrum = fft_magnitude_spectrum(image)
        self.assertEqual(spectrum.shape, image.shape[:2])
        self.assertEqual(spectrum.dtype, np.uint8)

    def test_dc_dominates_a_flat_image(self):
        spectrum = fft_magnitude_spectrum(flat_gray(64, 64), log_scale=False)
        h, w = spectrum.shape
        self.assertEqual(spectrum[h // 2, w // 2], 255)
        self.assertEqual(spectrum[0, 0], 0)

    def test_empty_input_raises(self):
        with self.assertRaises(ValueError):
            fft_magnitude_spectrum(np.array([], dtype=np.uint8))

    def test_lowpass_smooths(self):
        image = textured()
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        filtered = fft_filter(image, 'lowpass', cutoff=8)
        # High-frequency texture is gone, so the Laplacian energy drops
        self.assertLess(cv2.Laplacian(filtered, cv2.CV_32F).var(),
                        cv2.Laplacian(gray, cv2.CV_32F).var())

    def test_highpass_removes_the_mean(self):
        filtered = fft_filter(textured(), 'highpass', cutoff=8)
        gray = cv2.cvtColor(textured(), cv2.COLOR_RGB2GRAY)
        # A highpass strips the DC level, so the result centres much lower
        self.assertLess(abs(float(filtered.mean()) - 128), abs(float(gray.mean()) - 128) + 60)
        self.assertEqual(filtered.ndim, 2)

    def test_bandpass_runs(self):
        filtered = fft_filter(textured(), 'bandpass', cutoff=5, cutoff_high=20)
        self.assertEqual(filtered.shape, textured().shape[:2])

    def test_bandpass_rejects_inverted_cutoffs(self):
        with self.assertRaises(ValueError):
            fft_filter(textured(), 'bandpass', cutoff=20, cutoff_high=5)

    def test_unknown_filter_type_raises(self):
        with self.assertRaises(ValueError):
            fft_filter(textured(), 'notch', cutoff=10)

    def test_non_positive_cutoff_raises(self):
        with self.assertRaises(ValueError):
            fft_filter(textured(), 'lowpass', cutoff=0)

    def test_detects_a_sinusoid(self):
        image = textured().astype(np.float32)
        h, w = image.shape[:2]
        yy, xx = np.mgrid[0:h, 0:w]
        image += (30 * np.sin(2 * np.pi * (xx * 0.25 + yy * 0.15)))[:, :, np.newaxis]
        image = np.clip(image, 0, 255).astype(np.uint8)

        peaks = detect_periodic_peaks(image)
        self.assertGreaterEqual(len(peaks), 1)
        self.assertGreater(peaks[0]['z_score'], 4.0)

    def test_no_peaks_in_a_flat_image(self):
        self.assertEqual(detect_periodic_peaks(flat_gray(64, 64)), [])

    def test_removing_periodic_noise_reduces_variance(self):
        base = textured()
        h, w = base.shape[:2]
        yy, xx = np.mgrid[0:h, 0:w]
        pattern = (34 * np.sin(2 * np.pi * (xx * 0.25 + yy * 0.15)))[:, :, np.newaxis]
        contaminated = np.clip(base.astype(np.float32) + pattern, 0, 255).astype(np.uint8)

        cleaned = remove_periodic_noise(contaminated)
        gray_base = cv2.cvtColor(base, cv2.COLOR_RGB2GRAY).astype(np.float32)
        gray_bad = cv2.cvtColor(contaminated, cv2.COLOR_RGB2GRAY).astype(np.float32)

        before = float(np.abs(gray_bad - gray_base).mean())
        after = float(np.abs(cleaned.astype(np.float32) - gray_base).mean())
        self.assertLess(after, before)

    def test_removal_is_a_no_op_without_peaks(self):
        flat = flat_gray(64, 64)
        cleaned = remove_periodic_noise(flat)
        self.assertEqual(cleaned.shape, flat.shape[:2])

    def test_invalid_notch_radius_raises(self):
        with self.assertRaises(ValueError):
            remove_periodic_noise(textured(), notch_radius=0)


class TestJpegGhost(unittest.TestCase):

    def test_map_matches_input_size(self):
        image = textured()
        result = ghost_map(image, block_size=16)
        self.assertEqual(result.shape[:2], image.shape[:2])
        self.assertEqual(result.dtype, np.uint8)

    def test_map_without_upscale_is_a_block_grid(self):
        image = textured()  # 128x160
        result = ghost_map(image, block_size=16, upscale=False)
        self.assertEqual(result.shape, (128 // 16, 160 // 16))

    def test_rejects_too_few_qualities(self):
        with self.assertRaises(ValueError):
            ghost_map(textured(), qualities=[80])

    def test_rejects_tiny_block(self):
        with self.assertRaises(ValueError):
            ghost_map(textured(), block_size=1)

    def test_rejects_oversized_block(self):
        with self.assertRaises(ValueError):
            ghost_map(textured(64, 64), block_size=128)

    def test_report_finds_the_prior_compression_quality(self):
        # Requantising an already-JPEG'd image at its own quality is nearly
        # lossless, so that quality should stand out as the block minimum.
        image = recompress(textured(256, 256), quality=70)
        report = ghost_report(image, qualities=(50, 60, 70, 80, 90, 100), block_size=16)
        self.assertEqual(report['dominant_quality'], 70)

    def test_report_flags_a_spliced_region(self):
        # A patch pasted straight in from a differently-compressed source,
        # with no unifying resave afterwards - each region keeps its own
        # single-generation quantisation history intact.
        background = recompress(textured(128, 128, seed=2), quality=60)
        patch_source = recompress(textured(128, 128, seed=11), quality=95)
        composite = background.copy()
        composite[48:96, 48:96] = patch_source[48:96, 48:96]

        report = ghost_report(composite, qualities=(40, 50, 60, 70, 80, 90, 100), block_size=16)
        dominant_index = report['qualities'].index(report['dominant_quality'])
        patch_index = report['block_grid'][48 // 16, 48 // 16]
        self.assertEqual(report['dominant_quality'], 60)
        self.assertNotEqual(int(patch_index), dominant_index)

    def test_outlier_blocks_include_coordinates(self):
        background = recompress(textured(128, 128, seed=2), quality=60)
        patch_source = recompress(textured(128, 128, seed=11), quality=95)
        composite = background.copy()
        composite[48:96, 48:96] = patch_source[48:96, 48:96]

        report = ghost_report(composite, qualities=(40, 50, 60, 70, 80, 90, 100), block_size=16)
        self.assertGreater(report['outlier_count'], 0)
        self.assertIn('x', report['outliers'][0])
        self.assertIn('y', report['outliers'][0])


def build_thumbnail_exif(thumbnail_jpeg: bytes) -> bytes:
    """
    Hand-roll a minimal little-endian TIFF/EXIF blob with an IFD1 thumbnail
    pointer, appended after the IFDs (empty IFD0, three-tag IFD1).

    Pillow's own ``Exif.tobytes()`` cannot serialize a populated IFD1 (see
    ``metadata_forensics.extract_thumbnail``'s docstring), so there is no
    library path to attach a real thumbnail to a fixture. Writing the TIFF
    structure by hand avoids adding a dependency for one test fixture.
    """
    ifd0_offset = 8
    ifd1_offset = ifd0_offset + 2 + 0 * 12 + 4  # count + 0 entries + next-IFD ptr
    thumb_offset = ifd1_offset + 2 + 3 * 12 + 4  # count + 3 entries + next-IFD ptr

    tiff_header = b'II' + struct.pack('<HL', 42, ifd0_offset)
    ifd0 = struct.pack('<H', 0) + struct.pack('<L', ifd1_offset)

    entries = [
        (0x0103, 3, 1, 6),                     # Compression: SHORT, JPEG
        (0x0201, 4, 1, thumb_offset),           # JPEGInterchangeFormat: LONG, offset
        (0x0202, 4, 1, len(thumbnail_jpeg)),    # JPEGInterchangeFormatLength: LONG
    ]
    ifd1 = struct.pack('<H', len(entries))
    for tag, kind, count, value in entries:
        ifd1 += struct.pack('<HHL', tag, kind, count) + struct.pack('<L', value)
    ifd1 += struct.pack('<L', 0)  # no further IFDs

    return b'Exif\x00\x00' + tiff_header + ifd0 + ifd1 + thumbnail_jpeg


class TestMetadataForensics(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.array = textured(120, 160)

    def tearDown(self):
        self.tmp.cleanup()

    def write_jpeg(self, name, software=None, original=None, digitized=None,
                   modified=None, make='TestCam', model='Model X',
                   claimed_size=None, exif=True):
        """Write a JPEG with the EXIF tags a test needs, omitting the rest."""
        path = self.dir / name
        image = Image.fromarray(self.array)

        if not exif:
            image.save(path, 'JPEG', quality=90)
            return path

        tags = image.getexif()
        if make:
            tags[271] = make
        if model:
            tags[272] = model
        if software:
            tags[305] = software
        if modified:
            tags[306] = modified

        sub = tags.get_ifd(0x8769)
        if original:
            sub[36867] = original
        if digitized:
            sub[36868] = digitized
        if claimed_size:
            sub[40962], sub[40963] = claimed_size

        image.save(path, 'JPEG', exif=tags, quality=90)
        return path

    def write_jpeg_with_thumbnail(self, name, main_array, thumb_array):
        """Write a JPEG whose embedded IFD1 thumbnail is ``thumb_array``."""
        path = self.dir / name
        thumb_buf = io.BytesIO()
        Image.fromarray(thumb_array).save(thumb_buf, 'JPEG', quality=80)
        exif_blob = build_thumbnail_exif(thumb_buf.getvalue())
        Image.fromarray(main_array).save(path, 'JPEG', exif=exif_blob, quality=90)
        return path

    def checks(self, report):
        return {finding['check'] for finding in report['findings']}

    def test_reads_camera_tags(self):
        path = self.write_jpeg('cam.jpg', original='2024:03:01 10:00:00')
        report = metadata_report(path)
        self.assertTrue(report['has_exif'])
        self.assertEqual(report['make'], 'TestCam')
        self.assertEqual(report['model'], 'Model X')

    def test_clean_camera_file_raises_no_flags(self):
        path = self.write_jpeg('clean.jpg', software='Ver.1.00',
                               original='2024:03:01 10:00:00',
                               digitized='2024:03:01 10:00:00',
                               modified='2024:03:01 10:00:00',
                               claimed_size=(160, 120))
        self.assertEqual(metadata_report(path)['flag_count'], 0)

    def test_camera_firmware_is_not_an_editor(self):
        # Cameras populate Software too; only known editors should register
        self.assertIsNone(detect_editing_software({'Software': 'Ver.1.00'}))
        self.assertIsNone(detect_editing_software({}))

    def test_detects_editing_software(self):
        path = self.write_jpeg('edited.jpg', software='Adobe Photoshop 25.0')
        report = metadata_report(path)
        self.assertIn('editing_software', self.checks(report))
        self.assertGreaterEqual(report['flag_count'], 1)

    def test_editor_match_is_case_insensitive(self):
        self.assertEqual(detect_editing_software({'Software': 'GIMP 2.10'}), 'GIMP 2.10')

    def test_flags_modification_after_capture(self):
        path = self.write_jpeg('late.jpg', original='2024:03:01 10:00:00',
                               modified='2024:03:05 18:30:00')
        self.assertIn('modified_after_capture', self.checks(metadata_report(path)))

    def test_matching_timestamps_are_not_flagged(self):
        findings = check_timestamps({
            'DateTimeOriginal': '2024:03:01 10:00:00',
            'DateTimeDigitized': '2024:03:01 10:00:00',
            'DateTime': '2024:03:01 10:00:00',
        })
        self.assertEqual([f for f in findings if f['severity'] == 'flag'], [])

    def test_flags_digitized_before_captured(self):
        findings = check_timestamps({
            'DateTimeOriginal': '2024:03:01 10:00:00',
            'DateTimeDigitized': '2024:02:01 10:00:00',
        })
        self.assertIn('timestamp_disorder', {f['check'] for f in findings})

    def test_flags_dimension_mismatch(self):
        path = self.write_jpeg('resized.jpg', claimed_size=(4000, 3000))
        report = metadata_report(path)
        self.assertIn('dimension_mismatch', self.checks(report))

    def test_matching_dimensions_are_not_flagged(self):
        path = self.write_jpeg('sized.jpg', claimed_size=(160, 120))
        self.assertNotIn('dimension_mismatch', self.checks(metadata_report(path)))

    def test_missing_exif_on_jpeg_is_noted(self):
        path = self.write_jpeg('bare.jpg', exif=False)
        report = metadata_report(path)
        self.assertFalse(report['has_exif'])
        self.assertIn('no_exif', self.checks(report))

    def test_missing_exif_on_png_is_not_noted(self):
        # PNG does not normally carry EXIF, so its absence means nothing
        path = self.dir / 'plain.png'
        Image.fromarray(self.array).save(path)
        self.assertNotIn('no_exif', self.checks(metadata_report(path)))

    def test_notes_absent_camera_identification(self):
        path = self.write_jpeg('anon.jpg', make=None, model=None,
                               original='2024:03:01 10:00:00')
        self.assertIn('no_camera_identification', self.checks(metadata_report(path)))

    def test_detects_photoshop_segment(self):
        path = self.write_jpeg('irb.jpg', exif=False)
        payload = b'Photoshop 3.0\x00' + b'8BIM' + b'\x04\x04' + b'\x00\x00\x00\x00'
        segment = b'\xff\xed' + struct.pack('>H', len(payload) + 2) + payload
        raw = path.read_bytes()
        path.write_bytes(raw[:2] + segment + raw[2:])

        report = metadata_report(path)
        self.assertIn('photoshop_segment', self.checks(report))
        self.assertIn('APP13', report['segments'])

    def test_detects_xmp_packet(self):
        path = self.dir / 'xmp.jpg'
        xmp = (b'<?xpacket begin=""?><x:xmpmeta xmlns:x="adobe:ns:meta/">'
               b'</x:xmpmeta><?xpacket end="w"?>')
        Image.fromarray(self.array).save(path, 'JPEG', xmp=xmp, quality=90)
        self.assertIn('xmp_segment', self.checks(metadata_report(path)))

    def test_parse_exif_datetime(self):
        parsed = parse_exif_datetime('2024:03:01 10:30:00')
        self.assertEqual((parsed.year, parsed.month, parsed.hour), (2024, 3, 10))

    def test_parse_exif_datetime_tolerates_junk(self):
        for value in (None, '', 'not a date', '2024-03-01', 0):
            with self.subTest(value=value):
                self.assertIsNone(parse_exif_datetime(value))

    def test_read_exif_is_empty_for_a_file_without_it(self):
        self.assertEqual(read_exif(self.write_jpeg('bare2.jpg', exif=False)), {})

    def test_read_exif_is_empty_for_a_missing_file(self):
        self.assertEqual(read_exif(self.dir / 'nope.jpg'), {})

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            metadata_report(self.dir / 'nope.jpg')

    def test_findings_carry_a_severity_and_detail(self):
        path = self.write_jpeg('multi.jpg', software='Adobe Photoshop 25.0',
                               claimed_size=(4000, 3000))
        for finding in metadata_report(path)['findings']:
            self.assertIn(finding['severity'], ('info', 'flag'))
            self.assertTrue(finding['detail'])

    def test_extracts_a_real_thumbnail(self):
        thumb_array = cv2.resize(self.array, (40, 30))
        path = self.write_jpeg_with_thumbnail('thumb.jpg', self.array, thumb_array)
        thumbnail = extract_thumbnail(path)
        self.assertIsNotNone(thumbnail)
        self.assertEqual(thumbnail[:2], b'\xff\xd8')

    def test_no_thumbnail_extracts_nothing(self):
        path = self.write_jpeg('bare3.jpg', exif=False)
        self.assertIsNone(extract_thumbnail(path))

    def test_thumbnail_matching_the_image_is_not_flagged(self):
        # The way a camera actually builds one: a downscaled, recompressed
        # copy of the same pixels.
        thumb_array = cv2.resize(self.array, (40, 30))
        path = self.write_jpeg_with_thumbnail('match.jpg', self.array, thumb_array)
        self.assertEqual(check_thumbnail_mismatch(path), [])

    def test_thumbnail_disagreeing_with_the_image_is_flagged(self):
        unrelated = textured(30, 40, seed=99)
        path = self.write_jpeg_with_thumbnail('mismatch.jpg', self.array, unrelated)
        findings = check_thumbnail_mismatch(path)
        self.assertEqual({f['check'] for f in findings}, {'thumbnail_mismatch'})
        self.assertEqual(findings[0]['severity'], 'flag')

    def test_report_reflects_thumbnail_presence(self):
        thumb_array = cv2.resize(self.array, (40, 30))
        with_thumb = self.write_jpeg_with_thumbnail('present.jpg', self.array, thumb_array)
        without_thumb = self.write_jpeg('absent.jpg')
        self.assertTrue(metadata_report(with_thumb)['has_thumbnail'])
        self.assertFalse(metadata_report(without_thumb)['has_thumbnail'])

    def test_report_includes_thumbnail_mismatch_finding(self):
        unrelated = textured(30, 40, seed=99)
        path = self.write_jpeg_with_thumbnail('report_mismatch.jpg', self.array, unrelated)
        self.assertIn('thumbnail_mismatch', self.checks(metadata_report(path)))


class TestNoiseAnalysis(unittest.TestCase):

    def test_estimate_tracks_actual_noise(self):
        low = estimate_noise(noisy(sigma=5.0))
        high = estimate_noise(noisy(sigma=25.0))
        self.assertLess(low, high)

    def test_estimate_is_roughly_accurate(self):
        # The estimator should land near the true sigma on flat noise
        estimated = estimate_noise(noisy(sigma=20.0))
        self.assertGreater(estimated, 12.0)
        self.assertLess(estimated, 28.0)

    def test_flat_image_has_no_noise(self):
        self.assertAlmostEqual(estimate_noise(flat_gray()), 0.0, places=4)

    def test_tiny_image_raises(self):
        with self.assertRaises(ValueError):
            estimate_noise(np.zeros((2, 2), dtype=np.uint8))

    def test_snr_is_infinite_without_noise(self):
        self.assertEqual(estimate_snr(flat_gray()), float('inf'))

    def test_snr_drops_as_noise_rises(self):
        # Needs a textured base: on a flat image the "signal" std IS the noise,
        # so the ratio sits at 0 dB no matter how much noise is added
        base = textured(96, 96).astype(np.float32)
        rng = np.random.default_rng(12)
        clean = np.clip(base + rng.normal(0, 3.0, base.shape), 0, 255).astype(np.uint8)
        dirty = np.clip(base + rng.normal(0, 30.0, base.shape), 0, 255).astype(np.uint8)

        self.assertGreater(estimate_snr(clean), estimate_snr(dirty))

    def test_noise_map_matches_input_size(self):
        image = noisy()
        mapped = noise_map(image, block_size=16)
        self.assertEqual(mapped.shape, image.shape[:2])
        self.assertEqual(mapped.ndim, 2)

    def test_noise_map_without_upscale_is_a_block_grid(self):
        mapped = noise_map(noisy(), block_size=16, upscale=False)
        self.assertEqual(mapped.shape, (96 // 16, 96 // 16))

    def test_noise_map_highlights_the_noisy_half(self):
        rng = np.random.default_rng(4)
        image = np.full((96, 96), 128.0)
        image[:, 48:] += rng.normal(0, 30, (96, 48))
        image = np.clip(image, 0, 255).astype(np.uint8)

        mapped = noise_map(image, block_size=16, upscale=False)
        self.assertGreater(mapped[:, 3:].mean(), mapped[:, :3].mean())

    def test_noise_map_rejects_oversized_block(self):
        with self.assertRaises(ValueError):
            noise_map(noisy(), block_size=256)

    def test_noise_map_rejects_tiny_block(self):
        with self.assertRaises(ValueError):
            noise_map(noisy(), block_size=2)

    def test_report_flags_uneven_noise(self):
        rng = np.random.default_rng(6)
        image = np.full((96, 96), 128.0)
        image[:, 48:] += rng.normal(0, 35, (96, 48))
        image = np.clip(image, 0, 255).astype(np.uint8)

        uneven = noise_report(image, block_size=16)
        even = noise_report(noisy(sigma=20.0), block_size=16)
        self.assertGreater(uneven['uniformity'], even['uniformity'])

    def test_report_includes_block_locations(self):
        report = noise_report(noisy(), block_size=16)
        self.assertIn('noisiest_block', report)
        self.assertIn('quietest_block', report)
        self.assertGreaterEqual(report['noisiest_block']['sigma'],
                                report['quietest_block']['sigma'])


class TestCloneDetection(unittest.TestCase):

    def test_finds_a_known_duplicate(self):
        result = detect_copy_move(cloned(shift_y=40, shift_x=60))
        self.assertTrue(result['detected'])
        shifts = [(s['dy'], s['dx']) for s in result['shifts']]
        self.assertIn((40, 60), shifts)

    def test_reports_no_duplicates_in_a_clean_image(self):
        self.assertFalse(detect_copy_move(textured())['detected'])

    def test_mask_covers_both_copies(self):
        result = detect_copy_move(cloned(shift_y=40, shift_x=60))
        mask = result['mask']
        self.assertTrue(mask[20:40, 20:40].any())   # source region
        self.assertTrue(mask[60:80, 80:100].any())  # pasted region

    def test_step_larger_than_shift_misses_it(self):
        # Documented limitation: only shifts that are multiples of step are
        # visible, because the copy is sampled at a different phase
        image = cloned(shift_y=40, shift_x=60)
        self.assertTrue(detect_copy_move(image, step=1)['detected'])
        self.assertFalse(detect_copy_move(image, step=16)['detected'])

    def test_flat_image_is_skipped_entirely(self):
        result = detect_copy_move(flat_gray(96, 96))
        self.assertFalse(result['detected'])
        self.assertEqual(result['blocks_analyzed'], 0)
        self.assertGreater(result['blocks_skipped'], 0)

    def test_max_blocks_guard_raises(self):
        with self.assertRaises(ValueError) as ctx:
            detect_copy_move(textured(), max_blocks=10)
        self.assertIn('max_blocks', str(ctx.exception))

    def test_rejects_image_smaller_than_block(self):
        with self.assertRaises(ValueError):
            detect_copy_move(textured(8, 8), block_size=16)

    def test_rejects_invalid_parameters(self):
        image = textured()
        for kwargs in ({'block_size': 2}, {'step': 0}, {'coefficients': 0},
                       {'quantization': 0}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    detect_copy_move(image, **kwargs)

    def test_draw_regions_tints_only_the_matches(self):
        image = cloned()
        result = detect_copy_move(image)
        overlay = draw_clone_regions(image, result)
        self.assertEqual(overlay.shape, image.shape)
        self.assertFalse(np.array_equal(overlay, image))

    def test_draw_regions_is_a_no_op_without_matches(self):
        image = textured()
        overlay = draw_clone_regions(image, detect_copy_move(image))
        np.testing.assert_array_equal(overlay, image)

    def test_draw_rejects_bad_alpha(self):
        image = textured()
        with self.assertRaises(ValueError):
            draw_clone_regions(image, detect_copy_move(image), alpha=1.5)

    def test_highlight_returns_an_image(self):
        result = highlight_clones(cloned())
        self.assertEqual(result.shape, cloned().shape)
        self.assertEqual(result.dtype, np.uint8)


class TestMotionDeblur(unittest.TestCase):

    def test_motion_psf_is_normalized(self):
        psf = motion_blur_psf(length=15, angle=0)
        self.assertAlmostEqual(float(psf.sum()), 1.0, places=5)
        self.assertEqual(psf.shape[0] % 2, 1)

    def test_motion_psf_angle_changes_orientation(self):
        horizontal = motion_blur_psf(15, 0)
        vertical = motion_blur_psf(15, 90)
        centre = horizontal.shape[0] // 2
        self.assertGreater(horizontal[centre, :].sum(), horizontal[:, centre].sum())
        self.assertGreater(vertical[:, centre].sum(), vertical[centre, :].sum())

    def test_motion_psf_rejects_short_length(self):
        with self.assertRaises(ValueError):
            motion_blur_psf(length=0)

    def test_defocus_psf_is_a_normalized_disc(self):
        psf = defocus_psf(radius=5)
        self.assertAlmostEqual(float(psf.sum()), 1.0, places=5)
        centre = psf.shape[0] // 2
        self.assertGreater(psf[centre, centre], 0)
        self.assertEqual(psf[0, 0], 0)

    def test_defocus_psf_rejects_small_radius(self):
        with self.assertRaises(ValueError):
            defocus_psf(radius=0)

    def test_apply_psf_blurs(self):
        image = textured()
        blurred = apply_psf(image, motion_blur_psf(15, 0))
        self.assertEqual(blurred.shape, image.shape)
        self.assertLess(focus_score(blurred), focus_score(image))

    def test_motion_deblur_recovers_detail(self):
        image = detailed()
        blurred = apply_psf(image, motion_blur_psf(11, 0))
        restored = deblur_motion(blurred, length=11, angle=0, noise_power=0.005)

        error = lambda a, b: float(np.abs(a.astype(float) - b.astype(float)).mean())
        self.assertLess(error(restored, image), error(blurred, image))

    def test_defocus_deblur_recovers_detail(self):
        image = detailed()
        blurred = apply_psf(image, defocus_psf(3))
        restored = deblur_defocus(blurred, radius=3, noise_power=0.005)

        error = lambda a, b: float(np.abs(a.astype(float) - b.astype(float)).mean())
        self.assertLess(error(restored, image), error(blurred, image))

    def test_deblur_with_the_wrong_psf_does_not_help(self):
        # Guessing the PSF wrong produces detail that was never there
        image = detailed()
        blurred = apply_psf(image, motion_blur_psf(11, 0))
        error = lambda a, b: float(np.abs(a.astype(float) - b.astype(float)).mean())

        correct = deblur_motion(blurred, length=11, angle=0, noise_power=0.005)
        wrong = deblur_motion(blurred, length=11, angle=90, noise_power=0.005)
        self.assertLess(error(correct, image), error(wrong, image))

    def test_deblur_increases_sharpness(self):
        blurred = apply_psf(detailed(), motion_blur_psf(11, 0))
        restored = deblur_motion(blurred, length=11, angle=0, noise_power=0.005)
        self.assertGreater(focus_score(restored), focus_score(blurred))

    def test_larger_noise_power_leaves_more_blur(self):
        blurred = apply_psf(detailed(), motion_blur_psf(11, 0))
        gentle = deblur_motion(blurred, 11, 0, noise_power=0.5)
        aggressive = deblur_motion(blurred, 11, 0, noise_power=0.001)
        self.assertLess(focus_score(gentle), focus_score(aggressive))

    def test_deconvolution_preserves_shape_and_alpha(self):
        rgb = textured()
        alpha = np.full((*rgb.shape[:2], 1), 200, dtype=np.uint8)
        rgba = np.concatenate([rgb, alpha], axis=2)
        result = wiener_deconvolution(rgba, motion_blur_psf(9, 0))
        self.assertEqual(result.shape[2], 4)
        np.testing.assert_array_equal(result[:, :, 3], alpha[:, :, 0])

    def test_deconvolution_handles_grayscale(self):
        gray = cv2.cvtColor(textured(), cv2.COLOR_RGB2GRAY)
        result = wiener_deconvolution(gray, motion_blur_psf(9, 0))
        self.assertEqual(result.shape, gray.shape)

    def test_deconvolution_rejects_bad_noise_power(self):
        with self.assertRaises(ValueError):
            wiener_deconvolution(textured(), motion_blur_psf(9, 0), noise_power=0)

    def test_psf_larger_than_image_raises(self):
        with self.assertRaises(ValueError):
            wiener_deconvolution(textured(16, 16), motion_blur_psf(51, 0))

    def test_sweep_returns_a_grid(self):
        grid = deblur_sweep(textured(), lengths=[9, 15], angles=[0, 45])
        self.assertEqual(grid.ndim, 3)
        self.assertGreater(grid.size, 0)

    def test_sweep_rejects_empty_parameters(self):
        with self.assertRaises(ValueError):
            deblur_sweep(textured(), lengths=[], angles=[0])

    def test_focus_score_ranks_blur_correctly(self):
        image = textured()
        self.assertGreater(focus_score(image), focus_score(apply_psf(image, defocus_psf(4))))


class TestFrameAveraging(unittest.TestCase):

    def setUp(self):
        rng = np.random.default_rng(9)
        self.base = textured(64, 64)
        self.frames = [
            np.clip(self.base.astype(np.float32) + rng.normal(0, 20, self.base.shape),
                    0, 255).astype(np.uint8)
            for _ in range(16)
        ]

    def test_averaging_reduces_noise(self):
        averaged = average_frames(self.frames)
        self.assertLess(estimate_noise(averaged), estimate_noise(self.frames[0]))

    def test_averaging_approaches_the_clean_source(self):
        averaged = average_frames(self.frames)
        error = lambda a: float(np.abs(a.astype(float) - self.base.astype(float)).mean())
        self.assertLess(error(averaged), error(self.frames[0]))

    def test_average_of_one_frame_is_itself(self):
        np.testing.assert_array_equal(average_frames([self.base]), self.base)

    def test_weighted_average_respects_weights(self):
        dark = np.zeros((8, 8, 3), dtype=np.uint8)
        bright = np.full((8, 8, 3), 200, dtype=np.uint8)
        # All weight on the bright frame
        result = average_frames([dark, bright], weights=[0.0, 1.0])
        np.testing.assert_array_equal(result, bright)

    def test_mismatched_weight_count_raises(self):
        with self.assertRaises(ValueError):
            average_frames(self.frames, weights=[1.0, 2.0])

    def test_zero_weights_raise(self):
        with self.assertRaises(ValueError):
            average_frames([self.base, self.base], weights=[0.0, 0.0])

    def test_empty_frame_list_raises(self):
        with self.assertRaises(ValueError):
            average_frames([])

    def test_mismatched_shapes_raise(self):
        with self.assertRaises(ValueError):
            average_frames([textured(64, 64), textured(32, 32)])

    def test_median_removes_a_transient_object(self):
        frames = [self.base.copy() for _ in range(9)]
        # A bright block appearing in only two of nine frames
        for index in (3, 4):
            frames[index][20:40, 20:40] = 255

        result = median_frames(frames)
        np.testing.assert_array_equal(result[20:40, 20:40], self.base[20:40, 20:40])

    def test_median_keeps_a_persistent_object(self):
        frames = [self.base.copy() for _ in range(9)]
        for frame in frames:
            frame[20:40, 20:40] = 255
        self.assertTrue((median_frames(frames)[20:40, 20:40] == 255).all())

    def test_integrate_brightens_dark_footage(self):
        dark = [np.full((16, 16, 3), 12, dtype=np.uint8) for _ in range(10)]
        self.assertGreater(integrate_frames(dark).mean(), dark[0].mean())

    def test_integrate_rejects_bad_gain(self):
        with self.assertRaises(ValueError):
            integrate_frames(self.frames, gain=0)

    def test_frame_difference_isolates_change(self):
        before = self.base.copy()
        after = self.base.copy()
        after[10:20, 10:20] = 255

        difference = frame_difference(before, after)
        self.assertGreater(difference[10:20, 10:20].mean(), difference[40:60, 40:60].mean())

    def test_frame_difference_of_identical_frames_is_zero(self):
        self.assertEqual(frame_difference(self.base, self.base).max(), 0)

    def test_frame_difference_rejects_shape_mismatch(self):
        with self.assertRaises(ValueError):
            frame_difference(textured(64, 64), textured(32, 32))

    def test_sharpest_frames_ranks_by_focus(self):
        sharp = textured(64, 64)
        blurred = cv2.GaussianBlur(sharp, (0, 0), 3)
        frames = [blurred, sharp, blurred, blurred]

        self.assertEqual(sharpest_frames(frames, count=1), [1])

    def test_sharpest_frames_rejects_bad_count(self):
        with self.assertRaises(ValueError):
            sharpest_frames(self.frames, count=0)

    def test_sharpest_frames_on_empty_raises(self):
        with self.assertRaises(ValueError):
            sharpest_frames([])


if __name__ == '__main__':
    unittest.main()
