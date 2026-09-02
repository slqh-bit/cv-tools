"""
Metadata Forensics - read what a file says about its own history.

Every other tool here reads pixels. This one reads the container: EXIF tags,
JPEG application segments, and the relationship between what the metadata
claims and what the image actually is.

That makes it the cheapest check available and the easiest to defeat. Metadata
is plain text in a header; anyone can edit or strip it, and most social
platforms strip it wholesale on upload. So:

    - A finding here is a *lead*, never proof. An editor's name in the Software
      tag means the file passed through that editor - which cropping, rotating,
      or converting also does.
    - A clean header means nothing at all. Absence of evidence is the normal
      state of a file that has been through a messaging app.
    - Contradictions are the interesting part. A tag that disagrees with the
      pixels (claimed dimensions that do not match the actual ones) or with
      another tag (a digitised time before the capture time) is harder to
      produce by accident than a suspicious-looking name.

Findings carry a severity of 'info' (worth knowing) or 'flag' (worth
investigating). Neither is a conclusion.
"""

import io
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
from PIL import ExifTags, Image

# Software strings that indicate an image editor rather than camera firmware.
# Matched case-insensitively as substrings, because versions are appended.
EDITOR_SIGNATURES = (
    'photoshop', 'lightroom', 'gimp', 'paint.net', 'paintshop', 'affinity',
    'pixelmator', 'snapseed', 'krita', 'imagemagick', 'graphicconverter',
    'picasa', 'photoscape', 'luminar', 'capture one', 'darktable', 'rawtherapee',
    'inkscape', 'photopea', 'canva', 'facetune', 'adobe',
)

# EXIF's timestamp format
EXIF_TIME_FORMAT = '%Y:%m:%d %H:%M:%S'

# Formats that normally carry EXIF, so its absence is worth remarking on.
# PNG and BMP do not, and a missing header there means nothing.
EXIF_BEARING_FORMATS = {'.jpg', '.jpeg', '.tif', '.tiff', '.heic', '.webp'}

# IFD1 tags pointing at the embedded thumbnail JPEG.
_THUMBNAIL_OFFSET_TAG = 0x0201  # JPEGInterchangeFormat
_THUMBNAIL_LENGTH_TAG = 0x0202  # JPEGInterchangeFormatLength

# Hamming distance (out of 64 bits) above which a thumbnail's content is
# treated as disagreeing with the main image rather than merely recompressed.
# A thumbnail regenerated from the same pixels lands at 0-2 even after heavy
# JPEG recompression; an unrelated image or a materially different crop lands
# above 25 (see tests). 12 sits with a wide margin on both sides.
THUMBNAIL_HASH_THRESHOLD = 12


def parse_exif_datetime(value: Any) -> Optional[datetime]:
    """
    Parse an EXIF timestamp, returning None if it is absent or malformed.

    EXIF writes ``YYYY:MM:DD HH:MM:SS``. Cameras and editors both produce
    variants that do not parse; those are not findings in themselves, so this
    fails quietly.
    """
    if not value:
        return None
    try:
        return datetime.strptime(str(value).strip(), EXIF_TIME_FORMAT)
    except (ValueError, TypeError):
        return None


def read_exif(path: Union[str, Path]) -> Dict[str, Any]:
    """
    Read a file's EXIF tags into a name-keyed dict.

    Returns an empty dict when the file has no EXIF or cannot be opened, which
    is a normal outcome rather than an error.
    """
    try:
        with Image.open(path) as img:
            raw = img._getexif()
    except Exception:
        return {}

    if not raw:
        return {}

    return {ExifTags.TAGS.get(tag_id, tag_id): value for tag_id, value in raw.items()}


def _jpeg_segments(path: Union[str, Path]) -> List[str]:
    """Names of the JPEG application segments present, or [] for other formats."""
    try:
        with Image.open(path) as img:
            return [marker for marker, _ in getattr(img, 'applist', [])]
    except Exception:
        return []


def _segment_payloads(path: Union[str, Path]) -> Dict[str, bytes]:
    """Concatenated payload per application segment marker."""
    try:
        with Image.open(path) as img:
            payloads: Dict[str, bytes] = {}
            for marker, data in getattr(img, 'applist', []):
                payloads[marker] = payloads.get(marker, b'') + data
            return payloads
    except Exception:
        return {}


def _actual_size(path: Union[str, Path]) -> Optional[tuple]:
    """The image's real (width, height), or None if it cannot be read."""
    try:
        with Image.open(path) as img:
            return img.size
    except Exception:
        return None


def extract_thumbnail(path: Union[str, Path]) -> Optional[bytes]:
    """
    Pull the raw embedded JPEG thumbnail (EXIF IFD1) out of a file, if present.

    Pillow exposes IFD1's tags through ``Exif.get_ifd`` but has no method to hand
    back the thumbnail bytes themselves - and no way to *write* them either
    (``Exif.tobytes()`` errors on a populated IFD1), so this only ever reads.
    The bytes are found by hand: ``JPEGInterchangeFormat`` is an offset relative
    to the start of the TIFF header inside the raw APP1 payload Pillow keeps in
    ``img.info['exif']``.
    """
    try:
        with Image.open(path) as img:
            ifd1 = img.getexif().get_ifd(ExifTags.IFD.IFD1)
            offset = ifd1.get(_THUMBNAIL_OFFSET_TAG)
            length = ifd1.get(_THUMBNAIL_LENGTH_TAG)
            raw = img.info.get('exif')
    except Exception:
        return None

    if offset is None or length is None or not raw:
        return None

    tiff_start = raw.find(b'II*\x00')
    if tiff_start == -1:
        tiff_start = raw.find(b'MM\x00*')
    if tiff_start == -1:
        return None

    data = raw[tiff_start + offset: tiff_start + offset + length]
    return data if data[:2] == b'\xff\xd8' else None


def _average_hash(image: Image.Image, hash_size: int = 8) -> int:
    """Cheap perceptual hash: which cells of a small grayscale grid sit above its mean."""
    small = image.convert('L').resize((hash_size, hash_size), Image.LANCZOS)
    pixels = np.asarray(small, dtype=np.float64)
    bits = pixels > pixels.mean()
    return int(''.join('1' if bit else '0' for bit in bits.flatten()), 2)


def check_thumbnail_mismatch(path: Union[str, Path]) -> List[Dict[str, str]]:
    """
    Compare the embedded EXIF thumbnail's content against the main image's.

    Editors regularly update the pixels without regenerating the thumbnail, so
    a splice or a swapped subject can leave the thumbnail still showing the
    original scene - a discrepancy that survives casual re-saving because
    nothing prompts an editor to touch IFD1. Absence of a thumbnail is not
    itself a finding: plenty of ordinary files never had one.
    """
    thumbnail = extract_thumbnail(path)
    if thumbnail is None:
        return []

    try:
        thumb_hash = _average_hash(Image.open(io.BytesIO(thumbnail)))
        with Image.open(path) as main_img:
            main_hash = _average_hash(main_img)
    except Exception:
        return []

    distance = bin(thumb_hash ^ main_hash).count('1')
    if distance <= THUMBNAIL_HASH_THRESHOLD:
        return []

    return [_finding(
        'thumbnail_mismatch', 'flag',
        f'The embedded thumbnail disagrees with the image content (hash distance '
        f'{distance}/64) - the image was likely edited without regenerating the '
        f'thumbnail')]


def _finding(check: str, severity: str, detail: str) -> Dict[str, str]:
    return {'check': check, 'severity': severity, 'detail': detail}


def detect_editing_software(exif: Dict[str, Any]) -> Optional[str]:
    """
    Return the editor named in the EXIF Software tags, if it is a known one.

    Camera firmware also populates ``Software`` (often just a version string),
    so this matches against known editor names rather than treating any value
    as significant.
    """
    for tag in ('Software', 'ProcessingSoftware'):
        value = exif.get(tag)
        if not value:
            continue
        lowered = str(value).lower()
        for signature in EDITOR_SIGNATURES:
            if signature in lowered:
                return str(value).strip()
    return None


def check_timestamps(exif: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Compare EXIF's three timestamps against each other.

    ``DateTimeOriginal`` is when the shutter fired, ``DateTimeDigitized`` when
    it became a file, and ``DateTime`` when it was last written. A file
    straight out of a camera has all three equal or near enough.
    """
    findings: List[Dict[str, str]] = []

    original = parse_exif_datetime(exif.get('DateTimeOriginal'))
    digitized = parse_exif_datetime(exif.get('DateTimeDigitized'))
    modified = parse_exif_datetime(exif.get('DateTime'))

    if original and modified and modified > original:
        delta = modified - original
        findings.append(_finding(
            'modified_after_capture', 'flag',
            f'DateTime is {delta} after DateTimeOriginal - the file was written '
            f'again after the shutter fired'))

    if original and digitized and digitized < original:
        findings.append(_finding(
            'timestamp_disorder', 'flag',
            f'DateTimeDigitized ({digitized}) precedes DateTimeOriginal '
            f'({original}), which cannot happen in capture order'))

    if original and not modified and not digitized:
        findings.append(_finding(
            'partial_timestamps', 'info',
            'Only DateTimeOriginal is present; the other two timestamps were '
            'stripped or never written'))

    return findings


def metadata_report(path: Union[str, Path]) -> Dict[str, Any]:
    """
    Inspect a file's metadata and report anything inconsistent.

    Args:
        path: Path to an image file

    Returns:
        Dict with the identifying tags, the timestamps, the JPEG segments
        present, and a list of findings. Each finding has a ``check`` name, a
        ``severity`` of 'info' or 'flag', and a human-readable ``detail``.

    Example:
        >>> report = metadata_report('evidence.jpg')
        >>> report['flag_count']
        2
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No such file: {path}")

    exif = read_exif(path)
    segments = _jpeg_segments(path)
    suffix = path.suffix.lower()

    findings: List[Dict[str, str]] = []

    if not exif:
        if suffix in EXIF_BEARING_FORMATS:
            findings.append(_finding(
                'no_exif', 'info',
                f'A {suffix} file normally carries EXIF; this one has none, so it '
                f'was stripped, re-encoded, or never written by a camera'))
    else:
        if not exif.get('Make') and not exif.get('Model'):
            findings.append(_finding(
                'no_camera_identification', 'info',
                'EXIF is present but names no camera make or model'))

        editor = detect_editing_software(exif)
        if editor:
            findings.append(_finding(
                'editing_software', 'flag',
                f'Software tag names an image editor: {editor}'))

        findings.extend(check_timestamps(exif))

        # Claimed versus actual dimensions. The EXIF pair records the size the
        # camera wrote; a resize that does not update them leaves the two
        # disagreeing, which is hard to do on purpose and easy to do by editing.
        claimed_w = exif.get('ExifImageWidth')
        claimed_h = exif.get('ExifImageHeight')
        actual = _actual_size(path)
        if claimed_w and claimed_h and actual:
            if (int(claimed_w), int(claimed_h)) != actual:
                findings.append(_finding(
                    'dimension_mismatch', 'flag',
                    f'EXIF claims {claimed_w}x{claimed_h} but the image is '
                    f'{actual[0]}x{actual[1]} - it was resized or cropped after capture'))

    payloads = _segment_payloads(path)
    if 'APP13' in payloads and b'Photoshop' in payloads['APP13']:
        findings.append(_finding(
            'photoshop_segment', 'flag',
            'An APP13 Photoshop resource block is embedded, which Photoshop '
            'writes on save'))

    xmp = payloads.get('APP1', b'')
    if b'ns.adobe.com/xap' in xmp or b'<x:xmpmeta' in xmp:
        findings.append(_finding(
            'xmp_segment', 'info',
            'An XMP packet is embedded; it often records an editing history '
            'that the EXIF tags do not'))

    thumbnail = extract_thumbnail(path)
    if thumbnail is not None:
        findings.extend(check_thumbnail_mismatch(path))

    return {
        'filename': path.name,
        'format': suffix,
        'has_exif': bool(exif),
        'has_thumbnail': thumbnail is not None,
        'exif_tag_count': len(exif),
        'make': exif.get('Make'),
        'model': exif.get('Model'),
        'software': exif.get('Software'),
        'datetime_original': exif.get('DateTimeOriginal'),
        'datetime_digitized': exif.get('DateTimeDigitized'),
        'datetime_modified': exif.get('DateTime'),
        'segments': segments,
        'findings': findings,
        'flag_count': sum(1 for f in findings if f['severity'] == 'flag'),
    }
