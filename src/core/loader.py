"""
Image Loader - Handles loading images and video frames with metadata extraction.
"""

import os
from pathlib import Path
from typing import Union, Optional, Tuple, Dict, Any, Iterator, List
import hashlib

import cv2
import numpy as np
from PIL import Image, ExifTags

# Camera raw formats are decoded by rawpy, which is an optional import: it
# carries a large binary dependency and most workflows never touch raw files.
DEFAULT_RAW_OPTIONS: Dict[str, Any] = {
    # Keep the camera's own white balance rather than guessing one
    'use_camera_wb': True,
    # Do not silently stretch exposure - a raw file's brightness is evidence
    'no_auto_bright': True,
    'output_bps': 8,
}


class ImageLoader:
    """Load images from various formats and extract metadata."""

    SUPPORTED_IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.jfif', '.bmp', '.tiff', '.tif', '.webp', '.pbm', '.pgm', '.ppm'}
    SUPPORTED_VIDEO_EXTS = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.mpeg', '.mpg'}
    SUPPORTED_RAW_EXTS = {
        '.cr2', '.cr3', '.crw',   # Canon
        '.nef', '.nrw',           # Nikon
        '.arw', '.srf', '.sr2',   # Sony
        '.orf',                   # Olympus
        '.rw2',                   # Panasonic
        '.raf',                   # Fujifilm
        '.pef',                   # Pentax
        '.srw',                   # Samsung
        '.dng',                   # Adobe / open
        '.3fr', '.erf', '.kdc', '.mrw', '.x3f', '.raw',
    }

    def __init__(
        self,
        path: Union[str, Path],
        raw_options: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            path: Image, camera raw, or video file
            raw_options: Overrides for rawpy's ``postprocess``. Defaults keep
                         the camera white balance and leave exposure alone.
        """
        self.path = Path(path)
        self._image: Optional[np.ndarray] = None
        self._metadata: Dict[str, Any] = {}
        self._is_video = False
        self._is_raw = False
        self._video_capture: Optional[cv2.VideoCapture] = None
        self._frame_index = 0
        self._raw_options = {**DEFAULT_RAW_OPTIONS, **(raw_options or {})}

        if not self.path.exists():
            raise FileNotFoundError(f"File not found: {self.path}")

        ext = self.path.suffix.lower()
        if ext in self.SUPPORTED_VIDEO_EXTS:
            self._is_video = True
        elif ext in self.SUPPORTED_RAW_EXTS:
            self._is_raw = True
        elif ext not in self.SUPPORTED_IMAGE_EXTS:
            raise ValueError(f"Unsupported file format: {ext}")

    # ---- Directory discovery ----

    @classmethod
    def supported_still_exts(cls) -> set:
        """Every extension that can be loaded as a still image, raw included."""
        return cls.SUPPORTED_IMAGE_EXTS | cls.SUPPORTED_RAW_EXTS

    @classmethod
    def find_images(
        cls,
        directory: Union[str, Path],
        recursive: bool = False,
    ) -> List[Path]:
        """
        List the loadable still images in a directory, sorted by name.

        Args:
            directory: Directory to scan
            recursive: Descend into subdirectories

        Returns:
            Sorted list of paths

        Raises:
            NotADirectoryError: If the path is not a directory
        """
        directory = Path(directory)
        if not directory.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory}")

        candidates = directory.rglob('*') if recursive else directory.iterdir()
        extensions = cls.supported_still_exts()

        return sorted(
            path for path in candidates
            if path.is_file() and path.suffix.lower() in extensions
        )

    @classmethod
    def load_directory(
        cls,
        directory: Union[str, Path],
        recursive: bool = False,
        raw_options: Optional[Dict[str, Any]] = None,
    ) -> Iterator[Tuple[Path, np.ndarray]]:
        """
        Load every still image in a directory, one at a time.

        Yields rather than returning a list so a directory of large frames does
        not have to fit in memory at once.

        Args:
            directory: Directory to scan
            recursive: Descend into subdirectories
            raw_options: Passed through to each loader for raw files

        Yields:
            ``(path, image)`` pairs in sorted order

        Example:
            >>> for path, image in ImageLoader.load_directory('frames/'):
            ...     print(path.name, image.shape)
        """
        for path in cls.find_images(directory, recursive=recursive):
            with cls(path, raw_options=raw_options) as loader:
                yield path, loader.load()

    def load(self, frame_index: Optional[int] = None) -> np.ndarray:
        """Load image or a specific video frame."""
        if self._is_video:
            return self._load_video_frame(frame_index or 0)
        if self._is_raw:
            return self._load_raw()
        return self._load_image()

    def _load_raw(self) -> np.ndarray:
        """
        Decode a camera raw file via rawpy.

        ``postprocess`` returns RGB, which is this pipeline's colour order, so
        unlike the still and video paths nothing is converted here. That is
        the one loader path with no test behind it - there is no raw file in
        the repository to test against - so it rests on rawpy's documented
        output rather than on a measurement. See tests/test_colour_pipeline.py
        for the paths that are measured.
        """
        try:
            import rawpy
        except ImportError:
            raise RuntimeError(
                f"Reading {self.path.suffix} files requires rawpy, which is not "
                f"installed. Install it with: pip install rawpy"
            ) from None

        try:
            with rawpy.imread(str(self.path)) as raw:
                img = raw.postprocess(**self._raw_options)
                raw_info = {
                    'raw_width': int(raw.sizes.raw_width),
                    'raw_height': int(raw.sizes.raw_height),
                    'camera_whitebalance': list(raw.camera_whitebalance),
                    'black_level': list(raw.black_level_per_channel),
                    'color_description': raw.color_desc.decode()
                    if isinstance(raw.color_desc, bytes) else str(raw.color_desc),
                }
        except Exception as exc:
            raise RuntimeError(f"Failed to decode raw file {self.path}: {exc}") from exc

        self._image = img
        self._extract_metadata()
        # Recorded after _extract_metadata, which rebuilds the dict
        self._metadata['raw'] = raw_info
        self._metadata['raw_options'] = dict(self._raw_options)
        return img.copy()

    def _load_image(self) -> np.ndarray:
        """Load a still image with BGR -> RGB conversion."""
        img = cv2.imread(str(self.path), cv2.IMREAD_UNCHANGED)
        if img is None:
            raise RuntimeError(f"Failed to load image: {self.path}")

        # Convert BGR/BGRA to RGB/RGBA
        if img.ndim == 3:
            if img.shape[2] == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            elif img.shape[2] == 4:
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)

        self._image = img
        self._extract_metadata()
        return img.copy()

    def _load_video_frame(self, frame_index: int) -> np.ndarray:
        """Load a specific frame from video."""
        if self._video_capture is None:
            self._video_capture = cv2.VideoCapture(str(self.path))
            if not self._video_capture.isOpened():
                raise RuntimeError(f"Failed to open video: {self.path}")

        self._video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = self._video_capture.read()
        if not ret:
            raise RuntimeError(f"Failed to read frame {frame_index} from video")

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self._frame_index = frame_index
        self._extract_video_metadata()
        return frame

    # ---- Frame navigation ----

    @property
    def current_frame_index(self) -> int:
        """Index of the most recently read video frame."""
        return self._frame_index

    def goto_frame(self, index: int) -> np.ndarray:
        """
        Seek to a specific video frame and read it.

        Args:
            index: Zero-based frame index

        Returns:
            The frame as RGB

        Raises:
            ValueError: If this loader holds a still image, or the index is
                        negative or past the end
        """
        if not self._is_video:
            raise ValueError(f"Not a video file: {self.path}")
        if index < 0:
            raise ValueError(f"Frame index must be non-negative, got {index}")

        total = self.get_video_frame_count()
        if total > 0 and index >= total:
            raise ValueError(f"Frame {index} is past the end of the video ({total} frames)")

        return self._load_video_frame(index)

    def next_frame(self) -> Optional[np.ndarray]:
        """
        Read the frame after the current one.

        Returns:
            The next frame, or None at the end of the video
        """
        if not self._is_video:
            raise ValueError(f"Not a video file: {self.path}")

        total = self.get_video_frame_count()
        if total > 0 and self._frame_index + 1 >= total:
            return None

        try:
            return self._load_video_frame(self._frame_index + 1)
        except RuntimeError:
            # Some containers report a frame count they cannot actually deliver
            return None

    def previous_frame(self) -> Optional[np.ndarray]:
        """
        Read the frame before the current one.

        Returns:
            The previous frame, or None if already at the start
        """
        if not self._is_video:
            raise ValueError(f"Not a video file: {self.path}")
        if self._frame_index <= 0:
            return None

        return self._load_video_frame(self._frame_index - 1)

    def load_frames(
        self,
        count: int,
        start: int = 0,
        step: int = 1,
    ) -> list:
        """
        Load a sequence of video frames for multi-frame processing.

        Args:
            count: How many frames to read
            start: Index of the first frame
            step: Stride between frames. Above 1 spreads the sample over a
                  longer span, which helps a median composite clear a slow
                  moving object.

        Returns:
            List of RGB frames. Shorter than ``count`` if the video ends first.

        Raises:
            ValueError: If this loader holds a still image, or the arguments
                        are out of range
        """
        if not self._is_video:
            raise ValueError(f"Not a video file: {self.path}")
        if count < 1:
            raise ValueError(f"count must be at least 1, got {count}")
        if step < 1:
            raise ValueError(f"step must be at least 1, got {step}")
        if start < 0:
            raise ValueError(f"start must be non-negative, got {start}")

        if self._video_capture is None:
            self._video_capture = cv2.VideoCapture(str(self.path))
            if not self._video_capture.isOpened():
                raise RuntimeError(f"Failed to open video: {self.path}")

        frames = []
        for index in range(count):
            position = start + index * step
            self._video_capture.set(cv2.CAP_PROP_POS_FRAMES, position)
            ret, frame = self._video_capture.read()
            if not ret:
                break
            frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            # Keep the navigation cursor in step with what was actually read
            self._frame_index = position

        if not frames:
            raise RuntimeError(
                f"No frames read from {self.path} starting at index {start}"
            )

        self._extract_video_metadata()
        return frames

    def _extract_metadata(self) -> None:
        """Extract EXIF and basic metadata from image."""
        self._metadata = {
            'filename': self.path.name,
            'filepath': str(self.path.absolute()),
            'filesize_bytes': self.path.stat().st_size,
            'format': self.path.suffix.lower(),
            'sha256': self._compute_hash(),
        }

        # Try PIL for EXIF
        try:
            with Image.open(self.path) as pil_img:
                self._metadata['mode'] = pil_img.mode
                self._metadata['width'] = pil_img.width
                self._metadata['height'] = pil_img.height

                exif = pil_img._getexif()
                if exif:
                    exif_data = {}
                    for tag_id, value in exif.items():
                        tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                        exif_data[tag_name] = value
                    self._metadata['exif'] = exif_data
        except Exception:
            # Fallback to cv2 dimensions
            if self._image is not None:
                self._metadata['width'] = self._image.shape[1]
                self._metadata['height'] = self._image.shape[0]
                self._metadata['channels'] = self._image.shape[2] if self._image.ndim == 3 else 1

    def _extract_video_metadata(self) -> None:
        """Extract metadata from video file."""
        cap = self._video_capture
        if cap is None:
            return

        self._metadata = {
            'filename': self.path.name,
            'filepath': str(self.path.absolute()),
            'format': self.path.suffix.lower(),
            'sha256': self._compute_hash(),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'duration_sec': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS) if cap.get(cv2.CAP_PROP_FPS) > 0 else 0,
        }

    def _compute_hash(self) -> str:
        """Compute SHA-256 hash of the file."""
        sha256 = hashlib.sha256()
        with open(self.path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    @property
    def metadata(self) -> Dict[str, Any]:
        return self._metadata.copy()

    @property
    def is_video(self) -> bool:
        return self._is_video

    @property
    def is_raw(self) -> bool:
        """True if this is a camera raw file, decoded via rawpy."""
        return self._is_raw

    def get_video_frame_count(self) -> int:
        """Get total frame count for video files."""
        if not self._is_video:
            return 1
        if self._video_capture is None:
            cap = cv2.VideoCapture(str(self.path))
            count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            return count
        return int(self._video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

    def close(self) -> None:
        """Release video resources."""
        if self._video_capture is not None:
            self._video_capture.release()
            self._video_capture = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


def save_image(image: np.ndarray, path: Union[str, Path], quality: int = 95) -> None:
    """
    Save image to file, handling RGB -> BGR conversion.

    Raises:
        OSError: If the file could not be written (bad path, permissions,
                 unknown format). cv2.imwrite signals these two different ways
                 - returning False, or raising cv2.error - and neither should
                 be mistaken for a successful save.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if image.ndim == 3 and image.shape[2] == 3:
        save_img = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    elif image.ndim == 3 and image.shape[2] == 4:
        save_img = cv2.cvtColor(image, cv2.COLOR_RGBA2BGRA)
    else:
        save_img = image

    ext = path.suffix.lower()
    try:
        if ext == '.jfif':
            # JFIF is JPEG, but OpenCV registers no writer for the extension,
            # so encode as JPEG and write the bytes directly
            written, buffer = cv2.imencode(
                '.jpg', save_img, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
            if written:
                path.write_bytes(buffer.tobytes())
        elif ext in ('.jpg', '.jpeg'):
            written = cv2.imwrite(str(path), save_img, [cv2.IMWRITE_JPEG_QUALITY, quality])
        else:
            written = cv2.imwrite(str(path), save_img)
    except cv2.error as exc:
        raise OSError(f"Failed to write image {path}: {exc}") from exc

    if not written:
        raise OSError(f"Failed to write image: {path}")
