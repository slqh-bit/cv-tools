"""
Optional Tkinter GUI.

Launch it with ``cv-tools-gui [image]``. Everything it does runs through
``core.Pipeline`` and the filter registry, so chains built here are the same
objects the CLI produces and the presets interchange.
"""

from .app import CVToolsApp, main
from .widgets import ImageCanvas, ParameterPanel

__all__ = ['CVToolsApp', 'main', 'ImageCanvas', 'ParameterPanel']
