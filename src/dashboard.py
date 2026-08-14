"""
cv-tools web dashboard - a Streamlit front end for the same Pipeline and
filter registry the CLI and Tkinter GUI use.

Run with:

    streamlit run src/dashboard.py --server.address=0.0.0.0

Nothing here reimplements a filter: it drives ``core.pipeline.Pipeline``
through ``filters.registry`` exactly like the CLI and GUI do, and reuses the
GUI's parameter metadata (slider ranges, choice lists) so every registered
filter gets a usable form.
"""

import hmac
import inspect
import io
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import cv2
import numpy as np
import streamlit as st
from PIL import Image

from src.core import FilterStep, Pipeline, ReportGenerator, save_image
from src.filters import (
    FILTER_REGISTRY,
    dynamic_range_used,
    filter_function,
    histogram_stats,
    render_histogram,
    resolve_filter,
)
from src.gui.widgets import CHOICES, SLIDER_RANGES, _dynamic_choices, to_display
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

st.set_page_config(page_title='cv-tools', layout='wide')


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

def _init_state() -> None:
    st.session_state.setdefault('pipeline', None)
    st.session_state.setdefault('metadata', {})
    st.session_state.setdefault('source_name', None)
    st.session_state.setdefault('selected_filter', sorted(FILTER_REGISTRY)[0])
    st.session_state.setdefault('picks', [])
    st.session_state.setdefault('last_tap', None)


def _load_image(data: bytes, name: str) -> None:
    image = np.array(Image.open(io.BytesIO(data)).convert('RGB'))
    image = image[:, :, ::-1].copy()  # RGB -> BGR, filters are OpenCV-shaped
    st.session_state.pipeline = Pipeline(image)
    st.session_state.metadata = {'filename': name, 'width': image.shape[1],
                                  'height': image.shape[0]}
    st.session_state.source_name = name


# ---- parameter form, mirrors gui.widgets.ParameterPanel ----------------

def _choices_for(spec) -> Dict[str, Any]:
    """
    Valid values per parameter, narrowed to the filter being configured.

    The Tkinter panel used one global map because its comboboxes were
    editable - a wrong suggestion could always be typed over. A Streamlit
    selectbox offers only what it lists, so a global 'channel' list of
    r/g/b makes ``component`` impossible to drive: it needs the channel
    names of the chosen colour space, and matches them case-sensitively.
    """
    from src.filters import COLOR_SPACES, CURVE_PRESETS, STAIN_PRESETS

    merged = dict(CHOICES)
    merged.update(_dynamic_choices())

    if spec.name == 'component':
        names = []
        for _code, channels in COLOR_SPACES.values():
            names.extend(channels)
        merged['channel'] = sorted(dict.fromkeys(names))
    elif spec.name == 'curves':
        merged['preset'] = [''] + sorted(CURVE_PRESETS)
    elif spec.name == 'stain':
        merged['preset'] = sorted(STAIN_PRESETS)

    return merged


def _param_form(spec) -> Dict[str, Any]:
    """Build Streamlit controls from a filter's signature and collect values."""
    signature = inspect.signature(spec.fn)
    parameters = list(signature.parameters.values())[1:]  # skip `image`
    choices = _choices_for(spec)
    params: Dict[str, Any] = {}
    missing_required = []

    if not parameters:
        st.caption('No parameters.')
        return params

    for parameter in parameters:
        name = parameter.name
        required = parameter.default is inspect.Parameter.empty
        default = parameter.default if not required else None
        label = name + (' *' if required else '')
        key = f'param_{spec.name}_{name}'

        if isinstance(default, bool):
            params[name] = st.checkbox(label, value=default, key=key)
            continue

        if name in choices:
            options = choices[name]
            index = options.index(default) if default in options else 0
            # accept_new_options keeps the editable-combobox behaviour the
            # Tkinter panel had, so a value the list does not anticipate can
            # still be typed rather than being unreachable
            value = st.selectbox(label, options, index=index, key=key,
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
                params[name] = st.slider(label, int(low), int(high), int(default), key=key)
            else:
                params[name] = st.slider(label, float(low), float(high), float(default), key=key)
            continue

        text_default = '' if default is None else (
            ','.join(str(v) for v in default) if isinstance(default, (tuple, list))
            else str(default)
        )
        text = st.text_input(label, value=text_default, key=key)
        text = text.strip()
        if not text:
            if required:
                missing_required.append(name)
            continue
        params[name] = _parse_text(text)

    if missing_required:
        st.warning(f"Required: {', '.join(missing_required)}")
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
    st.sidebar.header('Source')

    upload = st.sidebar.file_uploader('Upload image', type=[
        'png', 'jpg', 'jpeg', 'jfif', 'bmp', 'tif', 'tiff', 'webp'])
    if upload is not None and upload.name != st.session_state.source_name:
        _load_image(upload.getvalue(), upload.name)

    samples = sorted(p.name for p in SAMPLES_DIR.glob('*') if p.suffix.lower()
                      in ('.png', '.jpg', '.jpeg', '.jfif'))
    if samples:
        chosen = st.sidebar.selectbox('...or a sample image', ['(none)'] + samples)
        if chosen != '(none)' and st.sidebar.button('Load sample'):
            _load_image((SAMPLES_DIR / chosen).read_bytes(), chosen)

    pipeline: Pipeline = st.session_state.pipeline
    if pipeline is None:
        return

    st.sidebar.divider()
    st.sidebar.header('Filter chain')

    for index, step in enumerate(pipeline.chain, start=1):
        summary = ', '.join(f'{k}={v}' for k, v in step.params.items())
        cols = st.sidebar.columns([5, 1])
        cols[0].write(f'{index}. **{step.name}**  \n`{summary[:60]}`' if summary
                       else f'{index}. **{step.name}**')
        if cols[1].button('x', key=f'remove_{index}'):
            chain = pipeline.chain
            del chain[index - 1]
            pipeline.replace_chain(chain, filter_function)
            st.rerun()

    action_cols = st.sidebar.columns(3)
    if action_cols[0].button('Undo', disabled=len(pipeline) == 0):
        pipeline.undo()
        st.rerun()
    if action_cols[1].button('Redo'):
        pipeline.redo()
        st.rerun()
    if action_cols[2].button('Reset'):
        pipeline.reset()
        st.rerun()

    st.sidebar.divider()
    st.sidebar.header('Add filter')

    query = st.sidebar.text_input('Search filters')
    names = sorted(FILTER_REGISTRY)
    if query:
        q = query.lower()
        names = [n for n in names
                  if q in n.lower() or q in FILTER_REGISTRY[n].description.lower()]

    if not names:
        st.sidebar.caption('No matching filters.')
        return

    if st.session_state.selected_filter not in names:
        st.session_state.selected_filter = names[0]
    name = st.sidebar.selectbox('Filter', names,
                                 index=names.index(st.session_state.selected_filter),
                                 key='selected_filter')
    spec = resolve_filter(name)
    st.sidebar.caption(spec.description)

    params = _param_form(spec)

    if st.sidebar.button('Apply filter', type='primary', disabled=params is None):
        try:
            pipeline.apply(spec.fn, spec.name, spec.module, params)
            st.sidebar.success(f'Applied {spec.name}')
        except Exception as exc:
            st.sidebar.error(str(exc))
        st.rerun()

    st.sidebar.divider()
    st.sidebar.header('Presets')

    preset_file = st.sidebar.file_uploader('Load preset', type=['json'], key='preset_upload')
    if preset_file is not None and st.sidebar.button('Apply preset'):
        import json
        preset = json.loads(preset_file.getvalue())
        steps = [FilterStep.from_dict(step) for step in preset.get('filters', [])]
        try:
            pipeline.replace_chain(steps, filter_function)
            st.sidebar.success('Preset applied')
        except Exception as exc:
            st.sidebar.error(str(exc))
        st.rerun()


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


# ---- main: viewer + histogram + info -----------------------------------

def _main() -> None:
    st.title('cv-tools dashboard')

    pipeline: Pipeline = st.session_state.pipeline
    if pipeline is None:
        st.info('Upload an image or pick a sample from the sidebar to get started.')
        return

    original, current = pipeline.compare()
    view = st.radio('View', ['Processed', 'Original', 'Side by side'],
                     horizontal=True, label_visibility='collapsed')

    grid_cols = st.columns([2, 1])
    show_grid = grid_cols[0].checkbox(
        'Coordinate grid', value=False,
        help='Read x,y off the image for crop, roi_crop, redact, perspective '
             'and measure_3d. Overlay only - the download stays clean.')
    spacing = grid_cols[1].selectbox('Spacing', [20, 25, 50, 100], index=2,
                                      disabled=not show_grid)

    tap = st.checkbox(
        'Tap to pick coordinates', value=False, disabled=not TAP_TO_PICK,
        help='Tap the image to read off x,y for crop, roi_crop, redact, '
             'perspective and measure_3d.' if TAP_TO_PICK else
             'Needs streamlit-image-coordinates; use the grid instead.')

    def shown(image: np.ndarray) -> np.ndarray:
        rgb = to_display(image)[:, :, ::-1]
        return _draw_coordinate_grid(rgb, spacing) if show_grid else rgb

    if tap and TAP_TO_PICK:
        # One tappable image: a side-by-side pair has no unambiguous target
        source = original if view == 'Original' else current
        frame = shown(source)
        picked = streamlit_image_coordinates(
            Image.fromarray(frame), use_column_width='always', key='tap_picker')
        _record_tap(picked, frame.shape)
        _render_picks()
    elif view == 'Side by side':
        cols = st.columns(2)
        cols[0].image(shown(original), caption='Original', width='stretch')
        cols[1].image(shown(current), caption='Processed', width='stretch')
    elif view == 'Original':
        st.image(shown(original), width='stretch')
    else:
        st.image(shown(current), width='stretch')

    buffer = io.BytesIO()
    Image.fromarray(to_display(current)[:, :, ::-1]).save(buffer, format='PNG')
    st.download_button('Download processed PNG', buffer.getvalue(),
                        file_name='processed.png', mime='image/png')

    col_hist, col_info = st.columns(2)

    with col_hist:
        st.subheader('Histogram')
        try:
            chart = render_histogram(current, width=480, height=200)
            st.image(chart, width='stretch')
        except ValueError:
            st.caption('No histogram available.')

    with col_info:
        st.subheader('Source and statistics')
        meta = st.session_state.metadata
        lines = [f'**{k}**: {v}' for k, v in meta.items()]
        lines.append(f'**shape**: {current.shape}')
        lines.append(f'**filters applied**: {len(pipeline)}')
        try:
            stats = histogram_stats(current)
            lines.append(f'**dynamic range used**: {dynamic_range_used(current) * 100:.1f}%')
            for name, values in stats['channels'].items():
                clipped = values['clipped_shadows_pct'] + values['clipped_highlights_pct']
                lines.append(f'**{name}**: mean {values["mean"]:.1f}, '
                              f'std {values["std"]:.1f}, clipped {clipped:.2f}%')
        except ValueError:
            pass
        st.markdown('  \n'.join(lines))

    st.divider()
    exp_cols = st.columns(3)

    if exp_cols[0].button('Export preset (JSON)'):
        import json
        preset = {
            'name': f'preset_{st.session_state.source_name or "image"}',
            'filters': [step.to_dict() for step in pipeline.chain],
        }
        st.download_button('Download preset.json', json.dumps(preset, indent=2),
                            file_name='preset.json', mime='application/json',
                            key='preset_dl')

    if exp_cols[1].button('Export report (Markdown)'):
        report = ReportGenerator(pipeline.generate_report(), st.session_state.metadata)
        md_path = Path('_dashboard_report.md')
        report.save(str(md_path), format='markdown')
        st.download_button('Download report.md', md_path.read_text(encoding='utf-8'),
                            file_name='report.md', mime='text/markdown', key='report_dl')
        md_path.unlink(missing_ok=True)


_require_auth()
_init_state()
_sidebar()
_main()
