"""
The colour palette every front end draws from.

Tk's default look mixes a light chrome with the dark image canvas this tool
needs - a bright surround biases the eye when judging shadow detail, which is
most of what a CCTV frame is. The palette that follows from that is not a Tk
concern, though: the Streamlit dashboard renders the same histograms on the
same ground.

So the values live here, importable without a UI toolkit, and ``gui/theme.py``
adds the Tk styling that applies them. Nothing in this module may import
tkinter: the dashboard is served from headless boxes that do not have it.
"""

from typing import Dict, Tuple


FONT = ('Segoe UI', 9)
FONT_BOLD = ('Segoe UI', 9, 'bold')
FONT_HEADING = ('Segoe UI', 10, 'bold')
FONT_MONO = ('Consolas', 9)

DARK: Dict[str, str] = {
    'window': '#17171a',        # behind the panes
    'panel': '#1e1e22',         # panel surfaces
    'field': '#26262b',         # entries, lists, buttons
    'hover': '#32323a',
    'text': '#e6e6ea',
    'muted': '#9a9aa4',
    'accent': '#f0a500',        # matches the split-view divider
    'accent_text': '#17171a',
    'flag': '#ff7a6b',          # a finding worth investigating
    'ok': '#7ecb8f',
    'canvas': '#101012',        # image viewer surround
    'border': '#34343c',
    'select': '#3a3a46',
}

LIGHT: Dict[str, str] = {
    'window': '#ececed',
    'panel': '#f7f7f9',
    'field': '#ffffff',
    'hover': '#e2e2e8',
    'text': '#1c1c22',
    'muted': '#5f5f6b',
    'accent': '#1f6feb',
    'accent_text': '#ffffff',
    'flag': '#c62828',
    'ok': '#1b7f3b',
    'canvas': '#d4d4d9',
    'border': '#c9c9d2',
    'select': '#cfe0fb',
}

PALETTES: Dict[str, Dict[str, str]] = {'dark': DARK, 'light': LIGHT}

# The histogram chart keeps its dark plate in both themes: its curves are drawn
# in fixed channel colours, and the luminance curve is a light grey that would
# disappear on a white background.
HISTOGRAM_BACKGROUND: Tuple[int, int, int] = (18, 18, 20)
