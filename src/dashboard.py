"""
cv-tools web dashboard - a Streamlit front end for the same Pipeline, filter
registry and analysis registry the CLI and Tkinter GUI use.

Run with:

    streamlit run src/dashboard.py --server.address=0.0.0.0

Nothing here reimplements a filter or a measurement: it drives
``core.pipeline.Pipeline`` through ``filters.registry`` exactly like the CLI
and GUI do, reuses the GUI's parameter metadata (slider ranges, choice lists)
so every registered filter gets a usable form, and renders
``filters.analysis`` reports so the numbers match what the CLI prints.

Layout:

    Sidebar   source, the chain, the filter picker, presets
    Viewer    the image, its histogram and its statistics
    Analysis  the forensic reports, run on demand
    Export    preset, report and processed image downloads
"""

import hmac
import html
import inspect
import io
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
import streamlit as st
from PIL import Image

from src.core import FilterStep, Pipeline, ReportGenerator
from src.filters import (
    ANALYSIS_REGISTRY,
    CATEGORY_ORDER,
    POINT_PARAMETERS,
    FILTER_REGISTRY,
    dynamic_range_used,
    filter_description,
    filter_function,
    histogram_stats,
    render_histogram,
    render_report,
    resolve_analysis,
    resolve_filter,
    run_analysis,
)
from src.gui.theme import DARK, HISTOGRAM_BACKGROUND
from src.gui.widgets import SLIDER_RANGES, choices_for, to_display
from src.utils.compare import difference_map
from src.utils.parsing import parse_value

# streamlit-image-coordinates 0.4.0 (the latest) imports UseColumnWith, a type
# alias Streamlit removed. It appears only in an annotation, never in logic, so
# supplying the name is enough to load an otherwise working component. Tap-to-
# pick degrades to the coordinate grid if the package is absent.
try:
    import streamlit.elements.image as _st_image_module
    if not hasattr(_st_image_module, 'UseColumnWith'):
        _st_image_module.UseColumnWith = str
    from streamlit_image_coordinates import streamlit_image_coordinates
    TAP_TO_PICK = True
except Exception:                                   # pragma: no cover
    streamlit_image_coordinates = None
    TAP_TO_PICK = False

SAMPLES_DIR = Path(__file__).resolve().parent.parent / 'samples'

IMAGE_TYPES = ['png', 'jpg', 'jpeg', 'jfif', 'bmp', 'tif', 'tiff', 'webp']

st.set_page_config(page_title='cv-tools', page_icon='🔍', layout='wide')


# ---- chrome -----------------------------------------------------------
# The palette comes from the desktop GUI so the two front ends match; only
# the handful of things Streamlit's own theme cannot reach are set here.

def _inject_css() -> None:
    st.markdown(
        f"""
        <style>
        .block-container {{ padding-top: 2.2rem; padding-bottom: 3rem; }}
        section[data-testid="stSidebar"] {{ border-right: 1px solid {DARK['border']}; }}
        section[data-testid="stSidebar"] .stButton button {{ width: 100%; }}

        /* Chain steps: a numbered row that stays readable at a glance */
        .cv-step {{
            background: {DARK['field']};
            border-left: 3px solid {DARK['accent']};
            border-radius: 3px;
            padding: 5px 8px;
            margin-bottom: 2px;
            font-size: 0.82rem;
            line-height: 1.35;
        }}
        .cv-step .cv-params {{
            color: {DARK['muted']};
            font-family: Consolas, monospace;
            font-size: 0.74rem;
            word-break: break-all;
        }}
        .cv-empty {{ color: {DARK['muted']}; font-size: 0.85rem; }}

        /* Analysis reports, rendered row by row with their severity */
        .cv-report {{
            background: {DARK['panel']};
            border: 1px solid {DARK['border']};
            border-radius: 4px;
            padding: 12px 16px;
            font-family: Consolas, monospace;
            font-size: 0.82rem;
            line-height: 1.6;
        }}
        .cv-report .cv-head {{ color: {DARK['accent']}; font-weight: 600; }}
        .cv-report .cv-label {{ color: {DARK['muted']}; }}
        .cv-report .cv-flag {{ color: {DARK['flag']}; }}
        .cv-report .cv-info {{ color: {DARK['muted']}; }}
        .cv-caption {{ color: {DARK['muted']}; font-size: 0.8rem; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---- access gate ------------------------------------------------------
# Only active when CVTOOLS_PASSWORD is set, so running locally stays
# frictionless. It is set when the app is published over a tunnel.

def _require_auth() -> None:
    secret = os.environ.get('CVTOOLS_PASSWORD')
    if not secret:
        return
    if st.session_state.get('authed'):
        return

    st.title('cv-tools')
    st.caption('This instance is published over a tunnel. Enter the password to continue.')
    entered = st.text_input('Password', type='password')
    if entered:
        if hmac.compare_digest(entered, secret):
            st.session_state.authed = True
            st.rerun()
        else:
            st.error('Incorrect password.')
    st.stop()


# ---- state ------------------------------------------------------------

def _ordered_filter_names() -> list:
    """Registry names grouped by function family, A-Z within each family."""
    return [name for category in CATEGORY_ORDER
            for name in sorted(n for n, spec in FILTER_REGISTRY.items()
                                if spec.category == category)]


def _init_state() -> None:
    st.session_state.setdefault('pipeline', None)
    st.session_state.setdefault('metadata', {})
    st.session_state.setdefault('source_name', None)
    st.session_state.setdefault('source_bytes', None)
    st.session_state.setdefault('source_path', None)
    st.session_state.setdefault('source_dir', None)
    st.session_state.setdefault('selected_filter', _ordered_filter_names()[0])
    st.session_state.setdefault('picks', [])
    st.session_state.setdefault('last_tap', None)
    st.session_state.setdefault('analysis', None)
    # The filter a guided pick is collecting points for, or None
    st.session_state.setdefault('picking_for', None)


def _load_image(data: bytes, name: str) -> None:
    # The previous image's temp copy is no longer referenced by anything
    previous = st.session_state.get('source_dir')
    if previous:
        shutil.rmtree(previous, ignore_errors=True)

    # Kept as RGB, which is what the filters expect: core.ImageLoader
    # converts BGR to RGB on load and save_image converts back, so RGB is the
    # pipeline's colour order throughout. Converting to BGR here fed every
    # filter its channels reversed - harmless for a luminance operation like
    # CLAHE, and wrong for every colour one. Inverting the red channel
    # inverted blue instead.
    image = np.array(Image.open(io.BytesIO(data)).convert('RGB'))
    st.session_state.pipeline = Pipeline(image)
    st.session_state.metadata = {'filename': name, 'width': image.shape[1],
                                  'height': image.shape[0]}
    st.session_state.source_name = name
    st.session_state.source_bytes = data
    st.session_state.source_path = None
    st.session_state.source_dir = None
    st.session_state.analysis = None
    st.session_state.picks = []


def _source_file() -> Optional[Path]:
    """
    The uploaded bytes as a file on disk, written once per image.

    Metadata and quantisation tables live in the container rather than the
    pixels, so those checks need the original file - which a browser upload
    only ever gives us in memory.

    The copy keeps the uploaded name inside a temporary directory of its own,
    because the metadata report quotes the filename back, and a report headed
    ``tmp8f3a1.jpg`` is no use as a record of what was examined.
    """
    if st.session_state.source_bytes is None:
        return None

    existing = st.session_state.source_path
    if existing and Path(existing).exists():
        return Path(existing)

    directory = Path(tempfile.mkdtemp(prefix='cvtools_'))
    # Path().name only, so an uploaded name can never point outside it
    target = directory / Path(st.session_state.source_name or 'image.png').name
    target.write_bytes(st.session_state.source_bytes)

    st.session_state.source_dir = str(directory)
    st.session_state.source_path = str(target)
    return target


# ---- parameter form, mirrors gui.widgets.ParameterPanel ----------------

def _param_form(spec, container=None, key_prefix: str = 'param') -> Dict[str, Any]:
    """
    Build Streamlit controls from a filter's signature and collect values.

    Args:
        spec: A ``FilterSpec`` or ``AnalysisSpec``
        container: Where to draw, defaulting to the sidebar
        key_prefix: Namespace for the widget keys, so a filter and an analysis
            sharing a parameter name do not share a widget

    Returns:
        The collected parameters, or None when a required one is still blank
    """
    target = container if container is not None else st.sidebar
    signature = inspect.signature(spec.fn)
    parameters = list(signature.parameters.values())[1:]  # skip `image`

    # An analysis can name parameters the form should not offer, such as the
    # source path, which comes from the loaded file
    skip = set(getattr(spec, 'skip_params', ()))
    parameters = [p for p in parameters if p.name not in skip]

    choices = choices_for(spec)
    params: Dict[str, Any] = {}
    missing_required = []

    if not parameters:
        target.caption('No parameters.')
        return params

    for parameter in parameters:
        name = parameter.name
        required = parameter.default is inspect.Parameter.empty
        default = parameter.default if not required else None
        label = name + (' *' if required else '')
        key = f'{key_prefix}_{spec.name}_{name}'

        if isinstance(default, bool):
            params[name] = target.checkbox(label, value=default, key=key)
            continue

        if name in choices:
            options = choices[name]
            index = options.index(default) if default in options else 0
            # accept_new_options keeps the editable-combobox behaviour the
            # Tkinter panel had, so a value the list does not anticipate can
            # still be typed rather than being unreachable
            value = target.selectbox(label, options, index=index, key=key,
                                     accept_new_options=True)
            if value is None or value == '':
                if required:
                    missing_required.append(name)
                continue
            params[name] = value
            continue

        if isinstance(default, (int, float)) and name in SLIDER_RANGES:
            low, high = SLIDER_RANGES[name]
            is_integer = isinstance(default, int)
            if is_integer:
                params[name] = target.slider(label, int(low), int(high), int(default),
                                             key=key)
            else:
                params[name] = target.slider(label, float(low), float(high),
                                             float(default), key=key)
            continue

        text_default = '' if default is None else (
            ','.join(str(v) for v in default) if isinstance(default, (tuple, list))
            else str(default)
        )
        text = target.text_input(label, value=text_default, key=key)
        text = text.strip()
        if not text:
            if required:
                missing_required.append(name)
            continue
        params[name] = _parse_text(text)

    if missing_required:
        target.warning(f"Required: {', '.join(missing_required)}")
        return None
    return params


def _parse_text(text: str) -> Any:
    if ',' in text:
        parts = [part.strip() for part in text.split(',')]
        parsed = [parse_value(part) for part in parts]
        if len(parsed) == 8 and all(isinstance(v, (int, float)) for v in parsed):
            return [[parsed[i], parsed[i + 1]] for i in range(0, 8, 2)]
        return parsed
    return parse_value(text)


# ---- sidebar: source + chain -------------------------------------------

def _sidebar() -> None:
    st.sidebar.markdown('### cv-tools')
    st.sidebar.caption('Forensic image enhancement, one ordered chain')

    with st.sidebar.expander('Source', expanded=st.session_state.pipeline is None):
        upload = st.file_uploader('Upload image', type=IMAGE_TYPES)
        if upload is not None and upload.name != st.session_state.source_name:
            _load_image(upload.getvalue(), upload.name)
            st.rerun()

        samples = sorted(p.name for p in SAMPLES_DIR.glob('*') if p.suffix.lower()
                          in ('.png', '.jpg', '.jpeg', '.jfif'))
        if samples:
            chosen = st.selectbox('...or a sample image', ['(none)'] + samples)
            if chosen != '(none)' and st.button('Load sample'):
                _load_image((SAMPLES_DIR / chosen).read_bytes(), chosen)
                st.rerun()

    pipeline: Pipeline = st.session_state.pipeline
    if pipeline is None:
        return

    _chain_panel(pipeline)
    _add_filter_panel(pipeline)
    _preset_panel(pipeline)


def _chain_panel(pipeline: Pipeline) -> None:
    st.sidebar.divider()
    st.sidebar.markdown(f'**Filter chain** &nbsp; `{len(pipeline)}`',
                        unsafe_allow_html=True)

    if not pipeline.chain:
        st.sidebar.markdown('<div class="cv-empty">No filters applied yet.</div>',
                            unsafe_allow_html=True)

    for index, step in enumerate(pipeline.chain):
        summary = html.escape(', '.join(f'{k}={v}' for k, v in step.params.items()))
        cols = st.sidebar.columns([6, 1, 1, 1], vertical_alignment='center')
        cols[0].markdown(
            f'<div class="cv-step">{index + 1}. <b>{html.escape(step.name)}</b>'
            + (f'<br><span class="cv-params">{summary[:70]}</span>' if summary else '')
            + '</div>',
            unsafe_allow_html=True)

        # Reordering matters as much as the filters themselves: sharpening
        # before or after denoising is a different result, and this is the
        # only way to try both without rebuilding the chain
        if cols[1].button('↑', key=f'up_{index}', disabled=index == 0,
                          help='Move earlier'):
            _reorder(pipeline, index, index - 1)
        if cols[2].button('↓', key=f'down_{index}',
                          disabled=index == len(pipeline.chain) - 1,
                          help='Move later'):
            _reorder(pipeline, index, index + 1)
        if cols[3].button('✕', key=f'remove_{index}', help='Remove'):
            chain = pipeline.chain
            del chain[index]
            _replace(pipeline, chain)

    action_cols = st.sidebar.columns(3)
    if action_cols[0].button('Undo', disabled=not pipeline.can_undo):
        pipeline.undo()
        st.rerun()
    if action_cols[1].button('Redo', disabled=not pipeline.can_redo):
        pipeline.redo()
        st.rerun()
    if action_cols[2].button('Reset', disabled=len(pipeline) == 0):
        pipeline.reset()
        st.rerun()


def _reorder(pipeline: Pipeline, index: int, target: int) -> None:
    chain = pipeline.chain
    chain[index], chain[target] = chain[target], chain[index]
    _replace(pipeline, chain)


def _replace(pipeline: Pipeline, chain: List[FilterStep]) -> None:
    """Re-process from the original with a modified chain."""
    try:
        pipeline.replace_chain(chain, filter_function)
    except Exception as exc:
        # replace_chain restores the previous state on failure, so the
        # pipeline is still the one that worked
        st.sidebar.error(str(exc))
    st.rerun()


def _add_filter_panel(pipeline: Pipeline) -> None:
    st.sidebar.divider()
    st.sidebar.markdown('**Add filter**')

    query = st.sidebar.text_input('Search filters')
    names = _ordered_filter_names()
    if query:
        q = query.lower()
        names = [n for n in names
                  if q in n.lower() or q in FILTER_REGISTRY[n].description.lower()]

    categories = ['All'] + [c for c in CATEGORY_ORDER
                             if any(FILTER_REGISTRY[n].category == c for n in names)]
    category = st.sidebar.selectbox('Category', categories, key='filter_category')
    if category != 'All':
        names = [n for n in names if FILTER_REGISTRY[n].category == category]

    if not names:
        st.sidebar.caption('No matching filters.')
        return

    if st.session_state.selected_filter not in names:
        st.session_state.selected_filter = names[0]
    # Prefix with the family when showing every category, so the flat list
    # still reads as grouped - a selectbox has no option groups.
    label = ((lambda n: f'{FILTER_REGISTRY[n].category} - {n}') if category == 'All'
             else (lambda n: n))
    name = st.sidebar.selectbox('Filter', names, format_func=label,
                                 index=names.index(st.session_state.selected_filter),
                                 key='selected_filter')
    spec = resolve_filter(name)
    st.sidebar.caption(spec.description)

    plan = POINT_PARAMETERS.get(name)
    if plan is not None:
        _picking_controls(name, plan)

    params = _param_form(spec)

    if st.sidebar.button('Apply filter', type='primary', disabled=params is None):
        try:
            pipeline.apply(spec.fn, spec.name, spec.module, params)
            st.sidebar.success(f'Applied {spec.name}')
        except Exception as exc:
            st.sidebar.error(str(exc))
        st.rerun()


def _picking_controls(name: str, plan) -> None:
    """
    Collect a filter's coordinate parameters from taps on the image.

    The desktop viewer fills these from clicks; without the same thing here,
    the dashboard's answer to "where is the object's foot" was read four
    numbers off a grid overlay and type them. The tap component already
    existed - what was missing was knowing which point each tap is *for*.
    """
    wanted = [prompt if count == 1 else f'{prompt} ({index + 1}/{count})'
              for _parameter, count, prompt in plan
              for index in range(count)]
    picks = st.session_state.picks
    active = st.session_state.picking_for == name

    if not active:
        if st.sidebar.button(f'Pick {len(wanted)} points on the image',
                             key=f'pick_{name}'):
            st.session_state.picking_for = name
            st.session_state.picks = []
            st.session_state.last_tap = None
            st.rerun()
        return

    if len(picks) < len(wanted):
        st.sidebar.info(f'Tap **{wanted[len(picks)]}**  \n'
                        f'({len(wanted) - len(picks)} of {len(wanted)} left)')
        st.sidebar.caption('Turn on "Tap to pick coordinates" over the image.')
    else:
        # Every point collected: write them into the parameter fields
        filled = _fill_from_picks(name, plan, picks)
        st.session_state.picking_for = None
        st.sidebar.success(f'Filled {", ".join(filled)}')

    if st.sidebar.button('Cancel picking', key=f'cancel_{name}'):
        st.session_state.picking_for = None
        st.rerun()


def _fill_from_picks(name: str, plan, picks) -> List[str]:
    """
    Distribute collected points across the parameters that wanted them.

    Written into the widgets' own session-state keys, which is how a value
    reaches a Streamlit control that has already been created once.
    """
    filled, index = [], 0
    for parameter, count, _prompt in plan:
        taken = picks[index:index + count]
        index += count
        if len(taken) < count:
            break
        flat = [coordinate for point in taken for coordinate in point]
        st.session_state[f'param_{name}_{parameter}'] = ','.join(
            str(v) for v in flat)
        filled.append(parameter)
    return filled


def _preset_panel(pipeline: Pipeline) -> None:
    st.sidebar.divider()
    with st.sidebar.expander('Presets'):
        preset_file = st.file_uploader('Load preset', type=['json'],
                                       key='preset_upload')
        if preset_file is not None and st.button('Apply preset'):
            preset = json.loads(preset_file.getvalue())
            steps = [FilterStep.from_dict(step) for step in preset.get('filters', [])]
            _replace(pipeline, steps)


# ---- coordinate grid ---------------------------------------------------

def _draw_coordinate_grid(display: np.ndarray, spacing: int = 50) -> np.ndarray:
    """
    Overlay labelled gridlines so pixel coordinates can be read off the image.

    Every filter that takes a position - crop, roi_crop, redact, perspective,
    measure_3d - needs coordinates the web viewer otherwise gives no way to
    find. The desktop GUI reports them on hover; a browser cannot, so the
    numbers are drawn into the image instead.

    Display only. It is applied after ``to_display`` and never touches the
    pipeline, so the download and every measurement stay clean.

    Args:
        display: 3-channel RGB image as shown in the viewer
        spacing: Pixels between gridlines

    Returns:
        A copy with the grid drawn on it
    """
    canvas = display.copy()
    height, width = canvas.shape[:2]
    spacing = max(int(spacing), 5)

    # Lines and text scale with the image, so they stay legible once the
    # browser has shrunk a 640px frame onto a phone
    line_thickness = max(1, round(min(width, height) / 700))
    font_scale = max(0.34, min(width, height) / 1400)
    text_thickness = max(1, round(font_scale * 2))

    # White lines disappear on a bright image and black on a dark one, so pick
    # against the overall tone rather than assuming dark CCTV footage
    tone = (255, 255, 255) if float(canvas.mean()) < 128.0 else (0, 0, 0)

    # Label roughly every 120px whatever the spacing, so there is always a
    # number near the point being read. Labelled lines are drawn heavier.
    label_every = max(1, round(120.0 / spacing))
    label_step = spacing * label_every

    overlay = canvas.copy()
    for x in range(spacing, width, spacing):
        major = x % label_step == 0
        cv2.line(overlay, (x, 0), (x, height), tone,
                 line_thickness + (1 if major else 0), cv2.LINE_AA)
    for y in range(spacing, height, spacing):
        major = y % label_step == 0
        cv2.line(overlay, (0, y), (width, y), tone,
                 line_thickness + (1 if major else 0), cv2.LINE_AA)

    canvas = cv2.addWeighted(overlay, 0.35, canvas, 0.65, 0.0)

    for x in range(label_step, width, label_step):
        _grid_label(canvas, str(x), (x + 3, 3), font_scale, text_thickness)
    for y in range(label_step, height, label_step):
        _grid_label(canvas, str(y), (3, y + 3), font_scale, text_thickness)

    _grid_label(canvas, f'{spacing}px grid', (3, height - 18),
                font_scale, text_thickness)
    return canvas


def _grid_label(canvas: np.ndarray, text: str, top_left: Tuple[int, int],
                font_scale: float, thickness: int) -> None:
    """Draw a grid number on a dark plate, so it reads over any content."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    x, y = top_left
    x = min(x, canvas.shape[1] - text_w - 3)
    y = min(y, canvas.shape[0] - text_h - baseline - 3)

    cv2.rectangle(canvas, (x - 2, y),
                  (x + text_w + 2, y + text_h + baseline + 2), (0, 0, 0), -1)
    cv2.putText(canvas, text, (x, y + text_h + 1), font, font_scale,
                (255, 235, 120), thickness, cv2.LINE_AA)


# ---- tap to pick -------------------------------------------------------

def _record_tap(picked: Optional[Dict[str, Any]], shape: Tuple[int, int]) -> None:
    """
    Store a tap, converted from displayed pixels back to image pixels.

    The component reports the click against the rendered <img>, together with
    the size it was rendered at. Scaling by that reported size - rather than by
    an assumed display width - keeps the mapping exact however the browser
    chose to lay the image out, which matters on a phone where the image is
    always scaled down.

    Each click carries a unix_time; the component replays its last value on
    every rerun, so that timestamp is what distinguishes a new tap from a
    redraw of the old one.
    """
    if not picked:
        return

    stamp = picked.get('unix_time')
    if stamp is not None and stamp == st.session_state.get('last_tap'):
        return
    st.session_state.last_tap = stamp

    shown_width = picked.get('width') or 0
    shown_height = picked.get('height') or 0
    if shown_width <= 0 or shown_height <= 0:
        return

    height, width = shape[:2]
    x = int(round(picked['x'] * width / shown_width))
    y = int(round(picked['y'] * height / shown_height))
    x = max(0, min(x, width - 1))
    y = max(0, min(y, height - 1))

    st.session_state.picks.append((x, y))


def _render_picks() -> None:
    """Show picked points in the forms the parameter fields actually take."""
    picks = st.session_state.picks
    if not picks:
        st.caption('Tap the image to pick a point.')
        return

    st.text_area(
        f'Picked points ({len(picks)})',
        '\n'.join(f'{index}. {x},{y}' for index, (x, y) in enumerate(picks, 1)),
        height=min(40 + 24 * len(picks), 200), key='picks_text')

    if len(picks) >= 2:
        (x1, y1), (x2, y2) = picks[-2], picks[-1]
        left, top = min(x1, x2), min(y1, y2)
        box = f'{left},{top},{abs(x2 - x1)},{abs(y2 - y1)}'
        st.caption(f'Last two as a region (x,y,w,h) for crop / roi_crop / '
                   f'redact / white_balance_patch: **{box}**')

    if st.button('Clear picks'):
        st.session_state.picks = []
        st.session_state.last_tap = None
        st.rerun()


# ---- viewer ------------------------------------------------------------

def _viewer_tab(pipeline: Pipeline) -> None:
    original, current = pipeline.compare()

    controls = st.columns([3, 2, 2, 3], vertical_alignment='center')
    view = controls[0].radio('View',
                             ['Processed', 'Original', 'Side by side', 'Difference'],
                             horizontal=True, label_visibility='collapsed')
    show_grid = controls[1].checkbox(
        'Coordinate grid', value=False,
        help='Read x,y off the image for any filter that takes coordinates. '
             'Overlay only - the download stays clean.')
    spacing = controls[2].selectbox('Spacing', [20, 25, 50, 100], index=2,
                                    disabled=not show_grid,
                                    label_visibility='collapsed')
    # Named from the registry rather than listed by hand, which went stale the
    # first time a filter with coordinates was added
    guided = ', '.join(sorted(POINT_PARAMETERS))
    tap = controls[3].checkbox(
        'Tap to pick coordinates', value=False, disabled=not TAP_TO_PICK,
        help=f'Tap the image to read off x,y. Guided picking, which names each '
             f'point as it asks for it, covers: {guided}.' if TAP_TO_PICK else
             'Needs streamlit-image-coordinates; use the grid instead.')

    def shown(image: np.ndarray) -> np.ndarray:
        rgb = to_display(image)
        return _draw_coordinate_grid(rgb, spacing) if show_grid else rgb

    if tap and TAP_TO_PICK:
        # One tappable image: a side-by-side pair has no unambiguous target
        source = original if view == 'Original' else current
        frame = shown(source)
        target = st.session_state.picking_for
        if target:
            plan = POINT_PARAMETERS.get(target, ())
            wanted = [prompt if count == 1 else f'{prompt} ({i + 1}/{count})'
                      for _p, count, prompt in plan for i in range(count)]
            done = len(st.session_state.picks)
            if done < len(wanted):
                st.info(f'Tap **{wanted[done]}** '
                        f'({len(wanted) - done} of {len(wanted)} left)')

        picked = streamlit_image_coordinates(
            Image.fromarray(frame), use_column_width='always', key='tap_picker')
        _record_tap(picked, frame.shape)
        _render_picks()
    elif view == 'Side by side':
        cols = st.columns(2)
        cols[0].image(shown(original), caption='Original', width='stretch')
        cols[1].image(shown(current), caption='Processed', width='stretch')
    elif view == 'Difference':
        # Scaled so a small change is visible at all, which means the picture
        # cannot say how large the change was - so the numbers go beside it
        diff, stats = difference_map(original, current, label=False)
        st.image(shown(diff), width='stretch')
        st.caption(f"Peak {stats['peak']:.0f}, mean {stats['mean']:.2f}, "
                   f"shown at ×{stats['scale']:.1f}")
    elif view == 'Original':
        st.image(shown(original), width='stretch')
    else:
        st.image(shown(current), width='stretch')

    _statistics(pipeline, current)


def _statistics(pipeline: Pipeline, current: np.ndarray) -> None:
    """Tonal statistics: the tiles first, then the histogram they summarise."""
    meta = st.session_state.metadata
    try:
        stats = histogram_stats(current)
    except ValueError:
        stats = None

    tiles = st.columns(4)
    tiles[0].metric('Size', f"{current.shape[1]} x {current.shape[0]}")
    tiles[1].metric('Filters applied', len(pipeline))
    if stats is not None:
        tiles[2].metric('Dynamic range used', f'{dynamic_range_used(current) * 100:.1f}%')
        clipped = sum(v['clipped_shadows_pct'] + v['clipped_highlights_pct']
                      for v in stats['channels'].values()) / len(stats['channels'])
        # Clipped pixels have lost their values for good, so this is the one
        # number that says whether enhancement still has anything to work with
        tiles[3].metric('Clipped', f'{clipped:.2f}%',
                        help='Mean across channels. Pixels stuck at 0 or 255 have '
                             'lost their original values, and no enhancement '
                             'recovers them.')

    col_hist, col_info = st.columns([3, 2])

    with col_hist:
        try:
            chart = render_histogram(current, width=640, height=220,
                                     background=HISTOGRAM_BACKGROUND)
            st.image(chart, width='stretch')
        except ValueError:
            st.caption('No histogram available.')

    with col_info:
        lines = [f'**{k}**: {v}' for k, v in meta.items()]
        if stats is not None:
            for name, values in stats['channels'].items():
                lines.append(f'**{name}**: mean {values["mean"]:.1f}, '
                              f'std {values["std"]:.1f}, clipped '
                              f'{values["clipped_shadows_pct"] + values["clipped_highlights_pct"]:.2f}%')
        st.markdown('  \n'.join(lines))


# ---- analysis ----------------------------------------------------------

def _analysis_tab(pipeline: Pipeline) -> None:
    """
    The measurements that describe an image without changing it.

    Driven by ``ANALYSIS_REGISTRY``, so this shows the same reports the CLI
    prints - and a report added to the registry appears here with no work in
    this file.
    """
    st.caption('Measurements, not conclusions. Each report ends with what it '
               'cannot tell you.')

    left, right = st.columns([1, 2])

    with left:
        name = st.selectbox('Report', list(ANALYSIS_REGISTRY),
                            format_func=lambda n: ANALYSIS_REGISTRY[n].title,
                            key='analysis_name')
        spec = resolve_analysis(name)
        st.caption(spec.description)

        params = _param_form(spec, container=st, key_prefix='analysis')
        source = _source_file()

        blocked = spec.needs_path and source is None
        if blocked:
            st.info(f"'{spec.name}' reads the file itself rather than the pixels, "
                    f"so it needs an uploaded or sample image.")

        if st.button('Run report', type='primary',
                     disabled=params is None or blocked):
            with st.spinner(f'Running {spec.name}...'):
                try:
                    report = run_analysis(spec, image=pipeline.current,
                                          path=source, params=params)
                    st.session_state.analysis = (spec.name,
                                                 render_report(spec, report))
                except Exception as exc:
                    st.session_state.analysis = None
                    st.error(str(exc))

    with right:
        result = st.session_state.analysis
        if result is None:
            st.markdown('<div class="cv-empty">Run a report to see it here.</div>',
                        unsafe_allow_html=True)
            return
        st.markdown(_report_html(result[1]), unsafe_allow_html=True)


def _report_html(rows) -> str:
    """
    Render report rows, colouring each by its severity.

    Report values quote the file's own strings - a Software tag, an XMP
    fragment - so every one of them is escaped before it reaches the page.
    """
    parts = ['<div class="cv-report">']
    for row in rows:
        if row.indent < 0:                      # the report's header line
            parts.append(f'<div class="cv-head">{html.escape(row.value)}</div>')
            continue

        pad = '&nbsp;' * (4 * (row.indent + 1))
        severity = f' class="cv-{row.severity}"' if row.severity else ''
        label = (f'<span class="cv-label">{html.escape(row.label)}:</span> '
                 if row.label else '')
        parts.append(f'<div>{pad}{label}'
                     f'<span{severity}>{html.escape(row.value)}</span></div>')
    parts.append('</div>')
    return ''.join(parts)


# ---- export ------------------------------------------------------------

def _export_tab(pipeline: Pipeline) -> None:
    name = Path(st.session_state.source_name or 'image').stem

    buffer = io.BytesIO()
    Image.fromarray(to_display(pipeline.current)).save(buffer, format='PNG')

    preset = {
        'name': f'preset_{st.session_state.source_name or "image"}',
        'filters': [step.to_dict() for step in pipeline.chain],
    }
    report = ReportGenerator(pipeline.generate_report(), st.session_state.metadata,
                             describe=filter_description)

    cols = st.columns(4)
    cols[0].download_button('Processed PNG', buffer.getvalue(),
                            file_name=f'{name}_processed.png', mime='image/png',
                            width='stretch')
    cols[1].download_button('Preset (JSON)', json.dumps(preset, indent=2),
                            file_name=f'{name}_preset.json',
                            mime='application/json', width='stretch')
    cols[2].download_button('Report (Markdown)', report.to_markdown(),
                            file_name=f'{name}_report.md', mime='text/markdown',
                            width='stretch')
    cols[3].download_button('Report (JSON)', json.dumps(report.to_dict(), indent=2),
                            file_name=f'{name}_report.json',
                            mime='application/json', width='stretch')

    st.caption('A preset saved here replays in the CLI and the desktop GUI: '
               'the chain, not the pixels, is the record of what was done.')
    st.markdown('#### Processing report')
    st.markdown(report.to_markdown())


# ---- main --------------------------------------------------------------

def _main() -> None:
    pipeline: Pipeline = st.session_state.pipeline
    if pipeline is None:
        st.title('cv-tools dashboard')
        st.info('Upload an image or pick a sample from the sidebar to get started.')
        return

    header = st.columns([4, 1], vertical_alignment='center')
    header[0].markdown(f"#### {st.session_state.source_name or 'Untitled'}")
    header[1].markdown(
        f'<div class="cv-caption" style="text-align:right">'
        f'{len(pipeline)} filter{"" if len(pipeline) == 1 else "s"} applied</div>',
        unsafe_allow_html=True)

    viewer, analysis, export = st.tabs(['Viewer', 'Analysis', 'Export'])
    with viewer:
        _viewer_tab(pipeline)
    with analysis:
        _analysis_tab(pipeline)
    with export:
        _export_tab(pipeline)


_inject_css()
_require_auth()
_init_state()
_sidebar()
_main()
