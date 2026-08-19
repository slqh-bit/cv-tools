"""
Analysis registry - the report-producing counterpart to ``filters.registry``.

The registry maps a name to a function that measures an image and returns a
dict. Those reports never enter a filter chain: they describe the evidence
rather than change it, which is why they are kept apart from
``FILTER_REGISTRY``.

Each spec also carries the presentation of its report - a header line and a
list of rows - so the CLI, the Tkinter GUI and the web dashboard show the same
numbers, in the same order, with the same caveat attached. A report added here
appears in all three without any front end being edited.

Severity on a row is 'flag' (worth investigating), 'info' (worth knowing) or
'' (a plain measurement). None of them is a conclusion; the caveat on every
spec says what the measure cannot tell you.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np

from .clone_detection import detect_copy_move
from .compression_analysis import compression_report
from .ela import ela_stats
from .jpeg_ghost import ghost_report
from .metadata_forensics import metadata_report
from .noise_analysis import noise_report


@dataclass(frozen=True)
class Row:
    """One line of a rendered report."""
    label: str = ''
    value: str = ''
    severity: str = ''      # '', 'info' or 'flag'
    indent: int = 0         # nesting depth, for per-item detail under a total


@dataclass(frozen=True)
class AnalysisSpec:
    """A named measurement, with the presentation of its own report."""
    name: str
    fn: Callable[..., Dict[str, Any]]
    module: str
    title: str
    description: str
    header: Callable[[Dict[str, Any]], str]
    rows: Callable[[Dict[str, Any]], List[Row]]
    caveat: str = ''
    needs_image: bool = True
    needs_path: bool = False
    # Parameters a generated form should not offer: ``path`` is supplied from
    # the loaded file, not typed by hand
    skip_params: Tuple[str, ...] = field(default_factory=tuple)


# ---- per-report formatting ------------------------------------------------
# Each pair below is one report's presentation. They read the same keys the
# analysis functions document, and produce rows rather than printed lines so
# that a text console and a widget can both render them.

def _noise_header(report: Dict[str, Any]) -> str:
    return 'Noise analysis'


def _noise_rows(report: Dict[str, Any]) -> List[Row]:
    snr = report['snr_db']
    blocks = report['blocks']
    noisiest = report['noisiest_block']
    quietest = report['quietest_block']
    uniformity = report['uniformity']
    return [
        Row('global sigma', f"{report['noise_sigma']:.2f}"),
        Row('SNR', 'infinite' if snr == float('inf') else f'{snr:.1f} dB'),
        Row('blocks', f"{blocks['rows']}x{blocks['cols']} of {report['block_size']}px, "
                      f"mean={report['block_mean']:.2f} std={report['block_std']:.2f}"),
        Row('uniformity',
            f"{uniformity:.2f} ({'uneven - inspect' if uniformity > 0.6 else 'fairly even'})",
            'flag' if uniformity > 0.6 else ''),
        Row('noisiest block', f"({noisiest['x']}, {noisiest['y']}): "
                              f"sigma={noisiest['sigma']:.2f}"),
        Row('quietest block', f"({quietest['x']}, {quietest['y']}): "
                              f"sigma={quietest['sigma']:.2f}"),
    ]


def _ela_header(stats: Dict[str, Any]) -> str:
    return (f"Error Level Analysis (JPEG quality {stats['quality']}, "
            f"{stats['block_size']}px blocks)")


def _ela_rows(stats: Dict[str, Any]) -> List[Row]:
    hottest = stats['hottest_block']
    return [
        Row('mean error', f"{stats['mean_error']:.2f}, max: {stats['max_error']:.2f}"),
        Row('block mean', f"{stats['block_mean']:.2f}, std: {stats['block_std']:.2f}"),
        Row('hottest block', f"({hottest['x']}, {hottest['y']}): "
                             f"mean={hottest['mean_error']:.2f}, "
                             f"z-score={hottest['z_score']:.2f}",
            'flag' if hottest['z_score'] >= 3.0 else ''),
    ]


def _clone_header(result: Dict[str, Any]) -> str:
    return 'Copy-move detection'


def _clone_rows(result: Dict[str, Any]) -> List[Row]:
    rows = [Row('blocks analyzed', f"{result['blocks_analyzed']} "
                                   f"({result['blocks_skipped']} skipped as featureless)")]
    if not result['detected']:
        rows.append(Row(value='no duplicated regions found'))
        return rows

    rows.append(Row('duplicated regions found',
                    f"{result['match_count']} matching block pairs", 'flag'))
    for shift in result['shifts'][:5]:
        rows.append(Row(value=f"shift dx={shift['dx']:+d} dy={shift['dy']:+d}: "
                              f"{shift['matches']} pairs", indent=1))
    return rows


def _compression_header(report: Dict[str, Any]) -> str:
    return 'Compression analysis'


def _compression_rows(report: Dict[str, Any]) -> List[Row]:
    rows = [
        Row('blockiness', f"{report['blockiness']:.1f}/100 "
                          f"(boundary step {report['boundary_step']:.2f} vs "
                          f"interior {report['interior_step']:.2f})"),
        Row('likely JPEG-compressed', 'yes' if report['likely_jpeg'] else 'no'),
        Row('region uniformity', f"{report['region_uniformity']:.2f}"),
    ]

    quality = report.get('jpeg_quality')
    if quality:
        rows.append(Row('quantisation tables',
                        f"{quality['tables']}, estimated quality {quality['quality']}"))
    elif 'jpeg_quality' in report:
        rows.append(Row(value='no quantisation tables (not a JPEG, or already re-saved)'))
    return rows


def _ghost_header(report: Dict[str, Any]) -> str:
    return (f"JPEG ghost detection (qualities {report['qualities'][0]}-"
            f"{report['qualities'][-1]}, {report['block_size']}px blocks)")


def _ghost_rows(report: Dict[str, Any]) -> List[Row]:
    rows = [
        Row('dominant quality', str(report['dominant_quality'])),
        Row('outlier blocks', f"{report['outlier_count']} "
                              f"({report['outlier_fraction'] * 100:.1f}% of blocks)",
            'flag' if report['outlier_count'] else ''),
    ]
    for outlier in report['outliers'][:5]:
        rows.append(Row(value=f"block at ({outlier['x']}, {outlier['y']}): "
                              f"best match quality {outlier['quality']}", indent=1))
    return rows


def _metadata_header(report: Dict[str, Any]) -> str:
    return f"Metadata forensics ({report['filename']})"


def _metadata_rows(report: Dict[str, Any]) -> List[Row]:
    rows: List[Row] = []
    if report['has_exif']:
        rows.append(Row('EXIF', f"{report['exif_tag_count']} tags, camera "
                                f"{report['make'] or '?'} {report['model'] or '?'}"))
        rows.append(Row('software', report['software'] or 'not recorded'))
        rows.append(Row('captured',
                        f"{report['datetime_original'] or 'not recorded'}, last written: "
                        f"{report['datetime_modified'] or 'not recorded'}"))
    else:
        rows.append(Row('EXIF', 'none'))

    if report['has_thumbnail']:
        rows.append(Row('embedded thumbnail', 'present'))
    if report['segments']:
        rows.append(Row('segments', ', '.join(report['segments'])))

    # Flags first: a reader who stops after two lines should have seen the
    # findings that are hardest to produce by accident
    findings = sorted(report['findings'], key=lambda f: f['severity'] != 'flag')
    if not findings:
        rows.append(Row(value='nothing inconsistent found'))
    for finding in findings:
        marker = 'FLAG' if finding['severity'] == 'flag' else 'info'
        rows.append(Row(f"[{marker}] {finding['check']}", finding['detail'],
                        finding['severity']))
    return rows


# ---- Registry -------------------------------------------------------------

ANALYSIS_REGISTRY: Dict[str, AnalysisSpec] = {
    spec.name: spec
    for spec in [
        AnalysisSpec(
            'noise', noise_report, 'src.filters.noise_analysis',
            'Noise', 'Global and per-block noise level, and how evenly it is spread',
            _noise_header, _noise_rows,
            caveat='uneven noise can also come from content: flat sky against '
                   'detailed foreground reads as non-uniform',
        ),
        AnalysisSpec(
            'ela', ela_stats, 'src.filters.ela',
            'Error Level Analysis', 'Block-level recompression error and its outliers',
            _ela_header, _ela_rows,
            caveat='only meaningful on JPEG originals; texture raises error levels too',
        ),
        AnalysisSpec(
            'clone', detect_copy_move, 'src.filters.clone_detection',
            'Copy-move', 'Duplicated regions and the shifts that relate them',
            _clone_header, _clone_rows,
            caveat='genuine repetition (tiles, windows, text) also matches',
        ),
        AnalysisSpec(
            'compression', compression_report, 'src.filters.compression_analysis',
            'Compression', 'Blocking measures, plus the quality read from the file',
            _compression_header, _compression_rows,
            caveat='blocking indicates compression strength, not manipulation',
            needs_path=True, skip_params=('path',),
        ),
        AnalysisSpec(
            'ghost', ghost_report, 'src.filters.jpeg_ghost',
            'JPEG ghost', 'Per-block prior JPEG quality, and blocks that disagree',
            _ghost_header, _ghost_rows,
            caveat='only meaningful on a single-JPEG composite; any re-save erases it',
        ),
        AnalysisSpec(
            'metadata', metadata_report, 'src.filters.metadata_forensics',
            'Metadata', 'EXIF tags, JPEG segments and the contradictions between them',
            _metadata_header, _metadata_rows,
            caveat='metadata is trivially edited or stripped; a clean header proves '
                   'nothing',
            needs_image=False, needs_path=True, skip_params=('path',),
        ),
    ]
}


def resolve_analysis(name: str) -> AnalysisSpec:
    """
    Look up an analysis by registry name.

    Raises:
        KeyError: If the name is not registered
    """
    try:
        return ANALYSIS_REGISTRY[name]
    except KeyError:
        available = ', '.join(sorted(ANALYSIS_REGISTRY))
        raise KeyError(f"Unknown analysis '{name}'. Available: {available}") from None


def run_analysis(
    spec: AnalysisSpec,
    image: Optional[np.ndarray] = None,
    path: Optional[Union[str, Path]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Run one analysis, supplying whichever of image and path it asks for.

    Args:
        spec: An ``AnalysisSpec`` from the registry
        image: The image to measure, for specs with ``needs_image``
        path: The source file, for specs with ``needs_path``. Metadata and
            quantisation tables live in the container, not the pixels, so
            those checks describe the file on disk rather than the chain's
            output
        params: Extra keyword arguments for the analysis function

    Returns:
        The analysis function's report dict

    Raises:
        ValueError: If the spec needs an image or a path that was not given
    """
    call: Dict[str, Any] = dict(params or {})

    if spec.needs_path:
        if path is None:
            raise ValueError(f"'{spec.name}' needs the source file, which is not "
                             f"available here")
        call['path'] = str(path)

    if not spec.needs_image:
        return spec.fn(**call)

    if image is None:
        raise ValueError(f"'{spec.name}' needs an image")
    return spec.fn(image, **call)


def render_report(spec: AnalysisSpec, report: Dict[str, Any]) -> List[Row]:
    """Header, rows and caveat as one list, ready to display."""
    rows = [Row(value=spec.header(report) + ':', indent=-1)]
    rows.extend(spec.rows(report))
    if spec.caveat:
        rows.append(Row('note', spec.caveat, 'info'))
    return rows


def report_lines(spec: AnalysisSpec, report: Dict[str, Any]) -> List[str]:
    """
    Render a report as plain indented text.

    This is what the CLI prints, and what the GUI puts in its analysis pane.
    """
    lines = []
    for row in render_report(spec, report):
        pad = '  ' * (row.indent + 1)
        lines.append(f'{pad}{row.label}: {row.value}' if row.label
                     else f'{pad}{row.value}')
    return lines


def list_analyses() -> List[Tuple[str, str]]:
    """Return (name, description) pairs for every registered analysis."""
    return [(spec.name, spec.description) for spec in ANALYSIS_REGISTRY.values()]
