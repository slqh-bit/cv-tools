"""
Video output - write a processed sequence back out as video.

Everything else here reduces video to a still. This is the other direction: a
chain applied to every frame of a range, written to a file that can be played.

**The codec is a forensic decision, not a convenience.** Writing an exhibit
through a lossy codec adds compression artefacts to the evidence, and this
toolkit contains filters - ``ela``, ``ghost``, ``compression_analysis`` - whose
whole job is reading compression history. Re-encoding lossily corrupts exactly
what they read. Measured on this build, writing ten frames and reading frame
zero back:

    FFV1  (.avi)   exact round trip, 178 KB
    RGBA  (.avi)   exact round trip, 211 KB  (uncompressed)
    MJPG  (.avi)   lossy, 47 KB
    XVID  (.avi)   lossy, 41 KB
    mp4v  (.mp4)   lossy, 36 KB

So the default is FFV1: lossless, intra-frame, and smaller than uncompressed.
A lossy codec can be asked for, and says so when it is.
"""

from pathlib import Path
from typing import Iterable, Optional, Sequence, Union

import cv2
import numpy as np

# Codecs whose output is bit-for-bit what went in. Verified by round trip
# rather than assumed: a fourcc a build accepts is not a fourcc it honours.
LOSSLESS_CODECS = frozenset({'FFV1', 'RGBA'})

# What each container gets when no codec is named. MP4 has no lossless option
# that OpenCV writes reliably, so asking for .mp4 is asking for a lossy file.
DEFAULT_CODECS = {
    '.avi': 'FFV1',
    '.mkv': 'FFV1',
    '.mp4': 'mp4v',
    '.mov': 'mp4v',
}


def codec_for(path: Union[str, Path]) -> str:
    """
    The default codec for an output path's container.

    Raises:
        ValueError: If the extension is not one we write
    """
    suffix = Path(path).suffix.lower()
    try:
        return DEFAULT_CODECS[suffix]
    except KeyError:
        available = ', '.join(sorted(DEFAULT_CODECS))
        raise ValueError(
            f"Cannot write video to '{suffix}'. Containers: {available}"
        ) from None


def is_lossless(codec: str) -> bool:
    """Whether a codec preserves the pixels exactly."""
    return codec.upper() in LOSSLESS_CODECS


class VideoWriter:
    """
    Write RGB frames to a video file.

    The first frame fixes the size; a later frame of a different size is an
    error rather than a silent rescale, because a chain that resizes some
    frames and not others has produced a sequence that does not mean one thing.

    Example:
        >>> with VideoWriter('out.avi', fps=25) as writer:
        ...     for frame in frames:
        ...         writer.write(frame)
    """

    def __init__(
        self,
        path: Union[str, Path],
        fps: float = 25.0,
        codec: Optional[str] = None,
    ):
        """
        Args:
            path: Destination file; its extension chooses the container
            fps: Output frame rate
            codec: Four-character code, or None for the container's default

        Raises:
            ValueError: If fps is not positive, or the container is unknown
        """
        if fps <= 0:
            raise ValueError(f"fps must be positive, got {fps}")

        self.path = Path(path)
        self.fps = float(fps)
        self.codec = (codec or codec_for(self.path)).upper()
        self._writer: Optional[cv2.VideoWriter] = None
        self._size: Optional[tuple] = None
        self._count = 0

        self.path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def frames_written(self) -> int:
        """How many frames have gone in so far."""
        return self._count

    @property
    def lossless(self) -> bool:
        """Whether this writer's codec preserves the pixels exactly."""
        return is_lossless(self.codec)

    def _open(self, width: int, height: int) -> None:
        # OpenCV's fourcc wants exactly four characters; 'MJPG' and 'mp4v' are
        # four, but a user-supplied three-character code would silently mangle
        code = self.codec.ljust(4)[:4]
        writer = cv2.VideoWriter(
            str(self.path), cv2.VideoWriter_fourcc(*code), self.fps,
            (width, height),
        )
        if not writer.isOpened():
            raise RuntimeError(
                f"Could not open {self.path} for writing with codec "
                f"'{self.codec}'. The codec may not be available in this "
                f"OpenCV build; try --codec MJPG, or a different container.")
        self._writer = writer
        self._size = (width, height)

    def write(self, frame: np.ndarray) -> None:
        """
        Append one RGB frame.

        Args:
            frame: RGB or grayscale, uint8

        Raises:
            ValueError: If the frame is empty, or a different size from the first
            RuntimeError: If the file could not be opened
        """
        if frame is None or frame.size == 0:
            raise ValueError("Cannot write an empty frame")

        image = frame if frame.dtype == np.uint8 else np.clip(frame, 0, 255).astype(np.uint8)

        if image.ndim == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:
            image = image[:, :, :3]

        height, width = image.shape[:2]

        if self._writer is None:
            self._open(width, height)
        elif (width, height) != self._size:
            raise ValueError(
                f"Frame {self._count} is {width}x{height} but the video is "
                f"{self._size[0]}x{self._size[1]}. A chain that resizes some "
                f"frames and not others cannot be written as one video - "
                f"give the geometric steps fixed parameters.")

        self._writer.write(cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        self._count += 1

    def close(self) -> None:
        """Finish the file. Safe to call twice."""
        if self._writer is not None:
            self._writer.release()
            self._writer = None

    def __enter__(self) -> 'VideoWriter':
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()


def save_video(
    frames: Sequence[np.ndarray],
    path: Union[str, Path],
    fps: float = 25.0,
    codec: Optional[str] = None,
) -> int:
    """
    Write a sequence of RGB frames to a video file.

    Args:
        frames: Frames to write, all the same size
        path: Destination; its extension chooses the container
        fps: Output frame rate
        codec: Four-character code, or None for the container's default

    Returns:
        How many frames were written

    Raises:
        ValueError: If there are no frames, or they disagree about size
    """
    if frames is None or len(frames) == 0:
        raise ValueError("No frames to write")

    with VideoWriter(path, fps=fps, codec=codec) as writer:
        for frame in frames:
            writer.write(frame)
        return writer.frames_written
