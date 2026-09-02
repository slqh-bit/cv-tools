"""Core engine: image I/O, filter pipeline, and report generation."""

from .loader import ImageLoader, save_image
from .pipeline import Pipeline, FilterStep
from .report import ReportGenerator, hash_image
from .video import (
    DEFAULT_CODECS,
    LOSSLESS_CODECS,
    VideoWriter,
    codec_for,
    is_lossless,
    save_video,
)

__all__ = [
    'ImageLoader',
    'save_image',
    'Pipeline',
    'FilterStep',
    'ReportGenerator',
    'hash_image',
    'VideoWriter',
    'save_video',
    'codec_for',
    'is_lossless',
    'DEFAULT_CODECS',
    'LOSSLESS_CODECS',
]
