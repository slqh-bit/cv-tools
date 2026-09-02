"""
One palette for the whole GUI.

Tk's default look mixes a light chrome with the dark image canvas this tool
needs - a bright surround biases the eye when judging shadow detail, which is
most of what a CCTV frame is. So the window follows the canvas rather than the
other way round, and every colour comes from here instead of being spelled out
at each widget.

Classic Tk widgets (Listbox, Text, Canvas, Menu) take no part in ttk styling,
so their colours are set from the same palette by the code that builds them:
``apply_theme`` returns the palette for exactly that reason.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Tuple

# Widget fonts. Sizes are in points, so they follow the DPI scaling that
# ``app.enable_dpi_awareness`` asks the OS for.
# The palette itself lives in utils, importable without tkinter, because the
# Streamlit dashboard draws from it too and is served from headless boxes.
# Re-exported here so existing ``from .theme import DARK`` callers still work.
from ..utils.palette import (          # noqa: F401
    DARK,
    FONT,
    FONT_BOLD,
    FONT_HEADING,
    FONT_MONO,
    HISTOGRAM_BACKGROUND,
    LIGHT,
    PALETTES,
)


def apply_theme(root: tk.Misc, name: str = 'dark') -> Dict[str, str]:
    """
    Style every ttk widget class from one palette.

    Args:
        root: The application window
        name: 'dark' or 'light'

    Returns:
        The palette, for the classic Tk widgets that have to colour themselves
    """
    palette = PALETTES.get(name, DARK)
    style = ttk.Style(root)

    # clam is the only bundled theme that honours background and border colour
    # on every class; the native Windows theme draws its own chrome and would
    # ignore most of what follows
    style.theme_use('clam')

    root.configure(background=palette['window'])
    root.option_add('*Font', FONT)

    # Classic widgets Tk creates for us - the combobox popup list and the menus
    root.option_add('*TCombobox*Listbox.background', palette['field'])
    root.option_add('*TCombobox*Listbox.foreground', palette['text'])
    root.option_add('*TCombobox*Listbox.selectBackground', palette['accent'])
    root.option_add('*TCombobox*Listbox.selectForeground', palette['accent_text'])
    root.option_add('*Menu.background', palette['panel'])
    root.option_add('*Menu.foreground', palette['text'])
    root.option_add('*Menu.activeBackground', palette['accent'])
    root.option_add('*Menu.activeForeground', palette['accent_text'])
    root.option_add('*Menu.relief', 'flat')

    style.configure('.', background=palette['panel'], foreground=palette['text'],
                    fieldbackground=palette['field'], bordercolor=palette['border'],
                    lightcolor=palette['panel'], darkcolor=palette['panel'],
                    focuscolor=palette['accent'], font=FONT)

    style.configure('TFrame', background=palette['panel'])
    style.configure('Window.TFrame', background=palette['window'])

    style.configure('TLabel', background=palette['panel'], foreground=palette['text'])
    style.configure('Heading.TLabel', font=FONT_HEADING)
    style.configure('Muted.TLabel', foreground=palette['muted'])
    style.configure('Flag.TLabel', foreground=palette['flag'])
    style.configure('Status.TLabel', background=palette['window'],
                    foreground=palette['muted'])

    style.configure('TButton', background=palette['field'], foreground=palette['text'],
                    bordercolor=palette['border'], relief='flat', padding=(8, 4))
    style.map('TButton',
              background=[('pressed', palette['select']), ('active', palette['hover']),
                          ('disabled', palette['panel'])],
              foreground=[('disabled', palette['muted'])])

    style.configure('Accent.TButton', background=palette['accent'],
                    foreground=palette['accent_text'], font=FONT_BOLD)
    style.map('Accent.TButton',
              background=[('pressed', palette['accent']), ('active', palette['accent']),
                          ('disabled', palette['panel'])],
              foreground=[('disabled', palette['muted'])])

    style.configure('TEntry', fieldbackground=palette['field'],
                    foreground=palette['text'], insertcolor=palette['text'],
                    bordercolor=palette['border'], padding=3)
    style.map('TEntry', bordercolor=[('focus', palette['accent'])])

    style.configure('TCombobox', fieldbackground=palette['field'],
                    background=palette['field'], foreground=palette['text'],
                    arrowcolor=palette['text'], bordercolor=palette['border'],
                    padding=3)
    style.map('TCombobox',
              fieldbackground=[('readonly', palette['field'])],
              bordercolor=[('focus', palette['accent'])])

    style.configure('TCheckbutton', background=palette['panel'],
                    foreground=palette['text'], indicatorcolor=palette['field'])
    style.map('TCheckbutton',
              indicatorcolor=[('selected', palette['accent'])],
              background=[('active', palette['panel'])])

    style.configure('TScale', background=palette['panel'],
                    troughcolor=palette['field'], bordercolor=palette['border'])
    style.map('TScale', background=[('active', palette['panel'])])

    style.configure('TSeparator', background=palette['border'])

    style.configure('TPanedWindow', background=palette['window'])
    style.configure('Sash', sashthickness=6, gripcount=0,
                    background=palette['window'], bordercolor=palette['window'])

    style.configure('TNotebook', background=palette['window'], borderwidth=0,
                    tabmargins=(2, 4, 2, 0))
    style.configure('TNotebook.Tab', background=palette['window'],
                    foreground=palette['muted'], padding=(12, 5), borderwidth=0)
    # The selected tab has to read as part of the panel below it, and the
    # rest as part of the window behind it
    style.map('TNotebook.Tab',
              background=[('selected', palette['panel']),
                          ('active', palette['hover']),
                          ('!selected', palette['window'])],
              foreground=[('selected', palette['text'])],
              expand=[('selected', (0, 0, 0, 0))])

    for orient in ('Vertical', 'Horizontal'):
        style.configure(f'{orient}.TScrollbar', background=palette['field'],
                        troughcolor=palette['window'], bordercolor=palette['window'],
                        arrowcolor=palette['muted'], relief='flat')
        style.map(f'{orient}.TScrollbar',
                  background=[('active', palette['hover'])])

    return palette


def listbox_options(palette: Dict[str, str]) -> Dict[str, object]:
    """Colours for a classic ``tk.Listbox``, which ttk cannot style."""
    return {
        'background': palette['field'],
        'foreground': palette['text'],
        'selectbackground': palette['accent'],
        'selectforeground': palette['accent_text'],
        'highlightthickness': 0,
        'borderwidth': 0,
        'font': FONT,
    }


def text_options(palette: Dict[str, str]) -> Dict[str, object]:
    """Colours for a classic ``tk.Text``, which ttk cannot style."""
    return {
        'background': palette['field'],
        'foreground': palette['text'],
        'insertbackground': palette['text'],
        'selectbackground': palette['select'],
        'highlightthickness': 0,
        'borderwidth': 0,
        'relief': 'flat',
        'font': FONT_MONO,
    }
