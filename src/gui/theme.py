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
