"""
Validation harness: run one filter against the corpus and write up what it did.

A filter that returns an array is not a filter that works. Every run here is
checked against the invariants the whole toolkit rests on - a real uint8
image, no NaN, the same answer twice, the parameters actually doing something
- and against whatever that filter specifically promises, which is the part
the type system cannot see.

Run:
    python validation/harness.py clahe              # one filter
    python validation/harness.py --all              # every registered filter
    python validation/harness.py --analyses         # the report registry
"""

import argparse
import json
import platform
import sys
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cv_tools.core import Pipeline                                       # noqa: E402
from cv_tools.filters import (                                           # noqa: E402
    ANALYSIS_REGISTRY,
    FILTER_REGISTRY,
    dynamic_range_used,
    histogram_stats,
    render_report,
    resolve_analysis,
    resolve_filter,
    run_analysis,
)
from cv_tools.gui.widgets import SLIDER_RANGES                           # noqa: E402

ROOT = Path(__file__).resolve().parent
CORPUS = ROOT / 'corpus'
RESULTS = ROOT / 'results'
ARTIFACTS = ROOT / 'artifacts'

# Parameters with no default: a signature cannot say what a sensible region or
# corner set is, and a filter cannot be run without one
REQUIRED_VALUES: Dict[str, Any] = {
    'x': 120, 'y': 80, 'width': 200, 'height': 140,
    'low_threshold': 50, 'high_threshold': 150,
    'corners': [[80, 40], [560, 90], [600, 430], [40, 400]],
    'space': 'HSV', 'channel': 'H', 'plane': 3, 'preset': 'lift_shadows',
    'calibration_path': None,
    'base': [320, 400], 'top': [320, 200],
    'reference_base': [200, 400], 'reference_top': [200, 240],
    'reference_height': 1.8,
    'angle': 15.0, 'length': 15.0, 'radius': 5.0, 'factor': 1.5,
    'strength': 0.5, 'quality': 90, 'amount': 1.0, 'scale': 2.0,
    'ratio': 1.5, 'target_size': [320, 240], 'size': [320, 240],
    'points': [[0, 0], [128, 170], [255, 255]],
    'horizon': 180.0,
    # Without these two, fit_aspect and selective_saturation could not be
    # driven at all and were silently absent from every sweep
    'target_ratio': 16 / 9,
    'hue_center': 30.0,
    # The measurement and annotation steps. Without these they recorded one
    # 'no drivable parameter set' run each and reported PASS - an unexercised
    # filter reading exactly like a clean one, which is the failure the
    # campaign exists to make impossible.
    'point_a': [180, 300], 'point_b': [420, 300],
    'reference_a': [180, 180], 'reference_b': [380, 180],
    'reference_length': 520.0,
    'start': [500, 120], 'end': [340, 260],
    'position': [60, 60],
    'text': 'exhibit A',
}


# Required values that mean different things to different filters. One flat map
# cannot serve both: 'points' is three curve control points to `curves` and a
# pair of opposite corners to `shape`, and the curve triple makes `shape`
# refuse. Narrowed per filter, the way the GUI's choices_for narrows CHOICES.
REQUIRED_BY_FILTER: Dict[str, Dict[str, Any]] = {
    'shape': {'shape': 'rectangle', 'points': [[80, 60], [420, 320]]},
    # Vertices that are actually a region of the frame, rather than the curve
    # control points the shared name would otherwise supply
    'measure_area': {'points': [[120, 100], [420, 100], [420, 300], [120, 300]]},
}


# A run's outcome. The distinction is the whole point of the harness: a
# filter that refuses black_point=255 with a clear message is working, and
# counting that as a failure buries the runs that are not.
DEFECT = 'defect'       # broke a promise the toolkit makes
REFUSED = 'refused'     # rejected bad input on purpose, with a message
NOTE = 'note'           # worth recording, not wrong

# Exceptions that mean the filter validated its input. Anything else reached
# OpenCV or numpy unguarded, which is a defect however sensible the value was.
CLEAN_REFUSALS = (ValueError, KeyError, FileNotFoundError, NotImplementedError)

# Filters whose default parameters are a documented identity, and why. Without
# this the harness calls a correct no-op a defect: levels at black 0 / white
# 255 / gamma 1 *must* return the image untouched, and its own check asserts
# so. The last two return the input when they find nothing, which is worth
# recording but is not a fault either.
IDENTITY_AT_DEFAULTS: Dict[str, str] = {
    'levels': 'black 0, white 255, gamma 1 is the identity mapping',
    'contrast_brightness': 'contrast 1.0 and brightness 0 change nothing',
    'temperature': 'temperature 0 and tint 0 change nothing',
    'color_balance': 'no shift requested on any tonal range',
    'cmyk': 'no ink adjustment requested',
    'channel_mixer': 'the identity matrix reproduces the channels',
    'pixel_aspect': 'a pixel aspect of 1.0 is already square',
    'auto_perspective': 'returns the input when it finds no quadrilateral',
    'clone_detect': 'returns the input when it finds no duplicated region',
}


@dataclass
class Run:
    """One invocation of a filter, and everything worth knowing about it."""
    image: str
    params: Dict[str, Any]
    ok: bool = False
    outcome: str = 'ok'
    elapsed_ms: float = 0.0
    note: str = ''
    error: str = ''
    stats: Dict[str, Any] = field(default_factory=dict)
    problems: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


def load_corpus() -> Dict[str, np.ndarray]:
    """
    Every corpus image, loaded the way the product loads images.

    Not `cv2.imread`. That returns BGR; `core.ImageLoader` returns RGB - it
    converts on load, and `save_image` converts back. Feeding filters BGR
    arrays meant every colour-sensitive measurement in this campaign was taken
    on channel-swapped data for sixteen hours, and it only came to light
    because a channel check disagreed with the filter about which index red
    lives in.

    A harness that does not load images the way the product does is not
    testing the product.
    """
    from cv_tools.core import ImageLoader

    images = {}
    for path in sorted(CORPUS.rglob('*')):
        if path.suffix.lower() not in ('.png', '.jpg', '.jpeg'):
            continue
        try:
            with ImageLoader(path) as loader:
                image = loader.load()
        except Exception:
            continue
        if image is not None:
            images[str(path.relative_to(CORPUS)).replace('\\', '/')] = image
    return images


def default_images(corpus: Dict[str, np.ndarray], filter_name: str) -> List[str]:
    """
    The images a filter is judged on.

    The CCTV frames always, because that is the job; plus whichever reference
    image was downloaded for this filter's specific promise.
    """
    chosen = [name for name in corpus if name.startswith('cctv/')]

    specific = {
        'deblur_motion': ['reference/motion_blur_plate.jpg'],
        'deblur_defocus': ['reference/defocus_text.jpg'],
        'perspective': ['ground_truth/grid_perspective.png',
                        'reference/perspective_sudoku.png'],
        'auto_perspective': ['reference/perspective_sudoku.png'],
        'barrel': ['ground_truth/grid_barrel.png'],
        'fisheye': ['ground_truth/grid_barrel.png'],
        'undistort': ['calibration/left01.jpg'],
        'clone_detect': ['ground_truth/copy_move.png', 'ground_truth/clean_control.jpg'],
        'ghost': ['ground_truth/quality_splice.jpg', 'ground_truth/clean_control.jpg'],
        'ela': ['ground_truth/quality_splice.jpg', 'ground_truth/clean_control.jpg'],
        'upscale': ['reference/baboon.png'],
        'stain': ['reference/lena.png'],
    }
    for name in specific.get(filter_name, []):
        if name in corpus and name not in chosen:
            chosen.append(name)
    return chosen


def parameter_matrix(spec, limit: int = 14) -> List[Dict[str, Any]]:
    """
    Defaults, then one parameter moved at a time to each end of its range.

    One at a time rather than every combination: a filter that breaks at a
    slider's extreme breaks there whatever the other sliders say, and the
    combinations run to millions.
    """
    import inspect

    signature = inspect.signature(spec.fn)
    parameters = list(signature.parameters.values())[1:]
    skip = set(getattr(spec, 'skip_params', ()))
    parameters = [p for p in parameters if p.name not in skip]

    required = dict(REQUIRED_VALUES)
    required.update(REQUIRED_BY_FILTER.get(getattr(spec, 'name', ''), {}))

    base: Dict[str, Any] = {}
    for parameter in parameters:
        if parameter.default is inspect.Parameter.empty:
            if parameter.name not in required:
                return []                       # cannot be driven from here
            base[parameter.name] = required[parameter.name]

    matrix = [dict(base)]

    for parameter in parameters:
        name = parameter.name
        default = parameter.default
        if default is inspect.Parameter.empty:
            continue

        values: List[Any] = []
        if isinstance(default, bool):
            values = [not default]
        elif isinstance(default, (int, float)) and name in SLIDER_RANGES:
            low, high = SLIDER_RANGES[name]
            cast = int if isinstance(default, int) else float
            values = [cast(low), cast(high)]
        elif isinstance(default, str) and default:
            from cv_tools.gui.widgets import CHOICES, _dynamic_choices
            options = dict(CHOICES)
            options.update(_dynamic_choices())
            values = [v for v in options.get(name, []) if v and v != default][:2]

        for value in values:
            variant = dict(base)
            variant[name] = value
            matrix.append(variant)

    return matrix[:limit]


def inspect_output(before: np.ndarray, after: Any, elapsed: float,
                   is_default: bool) -> Tuple[Dict[str, Any], List[str], List[str]]:
    """
    Measure a filter's output, separating broken promises from observations.

    A flat frame or an unchanged frame is a defect at default parameters and
    an observation at a slider's extreme: output_black=255 is white by
    definition, and reporting that as a failure hides the ones that are.
    """
    problems: List[str] = []
    notes: List[str] = []

    if not isinstance(after, np.ndarray):
        return {}, [f'returned {type(after).__name__}, not an array'], notes

    stats: Dict[str, Any] = {
        'shape': list(after.shape), 'dtype': str(after.dtype),
        'min': float(after.min()) if after.size else 0.0,
        'max': float(after.max()) if after.size else 0.0,
        'mean': round(float(after.mean()), 2) if after.size else 0.0,
        'std': round(float(after.std()), 2) if after.size else 0.0,
        'ms': round(elapsed * 1000, 1),
    }

    if after.size == 0:
        problems.append('empty output')
        return stats, problems, notes

    if after.dtype.kind == 'f' and not np.isfinite(after).all():
        problems.append('output contains NaN or infinity')
    if after.dtype != np.uint8:
        problems.append(f'dtype {after.dtype}, not uint8')
    if after.ndim not in (2, 3):
        problems.append(f'{after.ndim} dimensions')

    flat = float(after.std()) == 0.0
    unchanged = after.shape == before.shape and np.array_equal(after, before)

    if flat:
        target = problems if is_default else notes
        target.append(f'flat output - every pixel is {after.flat[0]}')
    if unchanged:
        target = problems if is_default else notes
        target.append('output identical to input')

    return stats, problems, notes


def run_filter(name: str, corpus: Dict[str, np.ndarray],
               budget_seconds: float = 0.0) -> Dict[str, Any]:
    """Run one filter across its images and parameter matrix."""
    spec = resolve_filter(name)
    images = default_images(corpus, name)
    matrix = parameter_matrix(spec)
    started = time.time()

    report: Dict[str, Any] = {
        'name': name, 'kind': 'filter', 'category': spec.category,
        'description': spec.description, 'module': spec.module,
        'runs': [], 'checks': [], 'started': datetime.now().isoformat(timespec='seconds'),
    }

    if not matrix:
        report['runs'].append(Run('-', {}, note='no drivable parameter set').__dict__)
        # Its specific checks still apply - they drive the filter themselves
        report['checks'] = run_checks(name, corpus)
        return report

    artifacts = ARTIFACTS / name
    artifacts.mkdir(parents=True, exist_ok=True)

    for image_name in images:
        image = corpus[image_name]
        for index, params in enumerate(matrix):
            run = Run(image=image_name, params=params)
            try:
                start = time.perf_counter()
                result = spec.fn(image, **params)
                run.elapsed_ms = (time.perf_counter() - start)
                run.stats, run.problems, run.notes = inspect_output(
                    image, result, run.elapsed_ms,
                    is_default=index == 0 and name not in IDENTITY_AT_DEFAULTS)
                run.elapsed_ms = round(run.elapsed_ms * 1000, 1)
                run.ok = not run.problems
                run.outcome = 'ok' if run.ok else DEFECT

                # Determinism: the same input twice has to give the same answer
                if index == 0 and isinstance(result, np.ndarray):
                    again = spec.fn(image, **params)
                    if not np.array_equal(result, again):
                        run.problems.append('not deterministic - two runs differ')
                        run.ok = False

                if index == 0 and isinstance(result, np.ndarray) and result.size:
                    stem = image_name.replace('/', '_').rsplit('.', 1)[0]
                    cv2.imwrite(str(artifacts / f'{stem}.png'), result)

            except CLEAN_REFUSALS as exc:
                # Validated and refused: the filter did its job
                run.outcome = REFUSED
                run.ok = True
                run.error = f'{type(exc).__name__}: {exc}'
                run.notes.append(f'refused: {exc}')
            except Exception as exc:
                # Anything else got through the filter's own checks and blew up
                # somewhere it could not explain itself
                run.outcome = DEFECT
                run.error = f'{type(exc).__name__}: {exc}'
                run.problems.append(f'unguarded {type(exc).__name__}: {exc}')
                run.note = traceback.format_exc(limit=2).strip().splitlines()[-1]

            report['runs'].append(run.__dict__)

            if budget_seconds and time.time() - started > budget_seconds:
                report['note'] = 'stopped at the time budget'
                return report

    report['checks'] = run_checks(name, corpus)
    if name in IDENTITY_AT_DEFAULTS:
        report['identity'] = IDENTITY_AT_DEFAULTS[name]
    return report


def run_checks(name: str, corpus: Dict[str, np.ndarray]) -> List[Dict[str, Any]]:
    """Run whatever this filter specifically promises, if anything is written."""
    from checks import CHECKS

    check = CHECKS.get(name)
    if check is None:
        return []

    try:
        return [{'what': what, 'ok': bool(ok), 'detail': detail}
                for what, ok, detail in check(corpus)]
    except Exception as exc:
        return [{'what': 'the specific checks ran at all', 'ok': False,
                 'detail': f'{type(exc).__name__}: {exc}'}]


def run_analysis_spec(name: str, corpus: Dict[str, np.ndarray]) -> Dict[str, Any]:
    """Run one analysis report across the images that can answer for it."""
    spec = resolve_analysis(name)
    report: Dict[str, Any] = {
        'name': name, 'kind': 'analysis', 'category': 'Analysis',
        'description': spec.description, 'module': spec.module,
        'runs': [], 'checks': [], 'started': datetime.now().isoformat(timespec='seconds'),
    }

    targets = [n for n in corpus if n.startswith(('ground_truth/', 'cctv/'))][:8]
    if spec.needs_path:
        targets = [n for n in corpus
                   if n.startswith(('ground_truth/', 'cctv/', 'reference/exif'))][:8]

    for image_name in targets:
        path = CORPUS / image_name
        run = Run(image=image_name, params={})
        try:
            start = time.perf_counter()
            result = run_analysis(spec, image=corpus[image_name], path=path)
            run.elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
            run.ok = True
            rows = render_report(spec, result)
            run.stats = {'rows': len(rows),
                         'flags': sum(1 for r in rows if r.severity == 'flag'),
                         'header': rows[0].value,
                         'body': [f'{r.label}: {r.value}' if r.label else r.value
                                  for r in rows[1:]]}
        except Exception as exc:
            run.error = f'{type(exc).__name__}: {exc}'
            run.problems.append(run.error)
        report['runs'].append(run.__dict__)

    # 'ela' and 'ghost' name both a filter and a report, so a report's checks
    # are keyed '<name>:report' to keep them off the filter's result
    report['checks'] = (run_checks(f'{name}:report', corpus)
                        or run_checks(name, corpus))
    return report


def write_result(report: Dict[str, Any]) -> Path:
    """Write one filter's result.md."""
    RESULTS.mkdir(parents=True, exist_ok=True)
    name = report['name']
    runs = report['runs']
    failures = [r for r in runs if r['problems']]
    refusals = [r for r in runs if r.get('outcome') == REFUSED]
    observations = [r for r in runs if r.get('notes') and not r['problems']]
    checks = report.get('checks', [])
    failed_checks = [c for c in checks if not c['ok']]

    lines = [
        f"# {name} - validation result",
        '',
        f"**{report['description']}**  ",
        f"`{report['module']}` | family: {report['category']} | "
        f"{report['started']}",
        '',
        '## Verdict',
        '',
    ]

    if not runs:
        lines.append('No runs - the filter could not be driven from the harness.')
    elif not failures and not failed_checks:
        lines.append(f'**PASS** - {len(runs)} runs, no invariant broken'
                     + (f', {len(checks)} specific checks passed' if checks else '')
                     + '.')
    else:
        parts = []
        if failures:
            parts.append(f'{len(failures)} of {len(runs)} runs broke an invariant')
        if failed_checks:
            parts.append(f'{len(failed_checks)} of {len(checks)} specific checks failed')
        lines.append('**FAIL** - ' + '; '.join(parts) + '.')

    if refusals:
        lines += ['', f'{len(refusals)} run(s) refused bad parameters with a clear '
                      'message, which is the wanted behaviour.']

    if report.get('identity'):
        lines += ['', f"At default parameters this filter is an identity: "
                      f"{report['identity']}. An unchanged image there is "
                      f"correct, not a fault."]

    if report.get('note'):
        lines += ['', f"_{report['note']}_"]

    if failures:
        lines += ['', '## Problems', '']
        seen = {}
        for run in failures:
            for problem in run['problems']:
                seen.setdefault(problem, []).append(run)
        for problem, cases in seen.items():
            example = cases[0]
            lines.append(f'- **{problem}** ({len(cases)} run'
                         f"{'' if len(cases) == 1 else 's'}) - "
                         f"first on `{example['image']}` with "
                         f"`{example['params'] or 'defaults'}`")

    if checks:
        lines += ['', '## What this filter specifically promises', '']
        for check in checks:
            mark = 'PASS' if check['ok'] else '**FAIL**'
            lines.append(f"- {mark} - {check['what']}: {check['detail']}")

    if observations:
        lines += ['', '## Observations', '',
                  'Not defects: a parameter at the end of its range doing '
                  'exactly what it says.', '']
        for run in observations[:12]:
            params = ', '.join(f'{k}={v}' for k, v in run['params'].items())
            lines.append(f"- `{params}` on `{run['image']}`: "
                         f"{'; '.join(run['notes'])}")

    if refusals:
        lines += ['', '## Refused parameters', '',
                  'Rejected on purpose, with the message the user would see.', '']
        seen = set()
        for run in refusals:
            message = run['error']
            if message in seen:
                continue
            seen.add(message)
            params = ', '.join(f'{k}={v}' for k, v in run['params'].items())
            lines.append(f'- `{params}` -> {message}')

    lines += ['', '## Runs', '', '| image | parameters | ms | output | note |',
              '|---|---|---|---|---|']
    for run in runs:
        params = ', '.join(f'{k}={v}' for k, v in run['params'].items()) or 'defaults'
        if len(params) > 60:
            params = params[:57] + '...'
        stats = run['stats']
        summary = (f"{stats.get('shape')} {stats.get('dtype')} "
                   f"mean {stats.get('mean')}" if stats else '-')
        note = ('; '.join(run['problems']) if run['problems']
                else ('refused: ' + run['error'] if run.get('outcome') == REFUSED
                      else '; '.join(run.get('notes', [])) or 'ok'))
        lines.append(f"| `{run['image']}` | `{params}` | {run['elapsed_ms']} | "
                     f"{summary} | {note[:80]} |")

    if report['kind'] == 'analysis':
        lines += ['', '## Reports', '']
        for run in runs:
            if not run['stats']:
                continue
            lines += [f"### `{run['image']}`", '', '```',
                      run['stats']['header']]
            lines += [f"  {row}" for row in run['stats']['body']]
            lines += ['```', '']

    artifacts = ARTIFACTS / name
    if artifacts.exists() and any(artifacts.iterdir()):
        lines += ['', '## Artifacts', '',
                  f'Outputs written to `validation/artifacts/{name}/`:', '']
        for path in sorted(artifacts.glob('*.png'))[:12]:
            lines.append(f'- `{path.name}`')

    # 'ela' and 'ghost' are each both a chain filter and a report; without
    # the suffix the second one written silently replaced the first
    suffix = '-report' if report['kind'] == 'analysis' else ''
    target = RESULTS / f'{name}{suffix}.md'
    target.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return target


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('names', nargs='*', help='Filter or analysis names')
    parser.add_argument('--all', action='store_true', help='Every registered filter')
    parser.add_argument('--analyses', action='store_true', help='Every analysis report')
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args(argv)

    corpus = load_corpus()
    if not corpus:
        raise SystemExit('No corpus - run validation/build_corpus.py first')

    targets: List[Tuple[str, str]] = []
    if args.all:
        targets += [(n, 'filter') for n in FILTER_REGISTRY]
    if args.analyses:
        targets += [(n, 'analysis') for n in ANALYSIS_REGISTRY]
    for name in args.names:
        # 'ela' and 'ghost' are each both a filter and a report; a bare name
        # means the filter, and '<name>:report' asks for the other one
        if name.endswith(':report'):
            targets.append((name.split(':')[0], 'analysis'))
        elif name in FILTER_REGISTRY:
            targets.append((name, 'filter'))
        else:
            targets.append((name, 'analysis'))

    # Check groups that belong to no single filter - the differential
    # comparisons span several - would otherwise be collected and never run
    if args.all:
        from checks import CHECKS
        known = set(FILTER_REGISTRY) | set(ANALYSIS_REGISTRY)
        known |= {f'{n}:report' for n in ANALYSIS_REGISTRY}
        targets += [(n, 'standalone') for n in sorted(CHECKS) if n not in known]

    summary = []
    for name, kind in targets:
        started = time.time()
        if kind == 'standalone':
            report = {'name': name, 'kind': 'standalone', 'category': 'Cross-cutting',
                      'description': 'Checks spanning several filters',
                      'module': 'validation.checks', 'runs': [],
                      'checks': run_checks(name, corpus),
                      'started': datetime.now().isoformat(timespec='seconds')}
        elif kind == 'analysis':
            report = run_analysis_spec(name, corpus)
        else:
            report = run_filter(name, corpus)
        path = write_result(report)
        failures = sum(1 for r in report['runs'] if r['problems'])
        failed_checks = sum(1 for c in report.get('checks', []) if not c['ok'])
        summary.append({'name': name, 'kind': kind, 'runs': len(report['runs']),
                        'failures': failures, 'checks': len(report.get('checks', [])),
                        'failed_checks': failed_checks,
                        'seconds': round(time.time() - started, 1)})
        if not args.quiet:
            mark = 'ok  ' if not (failures or failed_checks) else 'FAIL'
            checks = report.get('checks', [])
            print(f"{mark} {name:22s} {len(report['runs']):3d} runs  "
                  f"{failures:2d} defects  "
                  f"{len(checks) - failed_checks}/{len(checks)} checks  "
                  f"{time.time() - started:5.1f}s")

    # A partial run must not land in summary.json. That file is the recorded
    # baseline regress.py compares against, and a seven-filter run overwriting
    # an eighty-four-filter record does not read as damage - it reads as
    # seventy-seven filters having vanished, or on the next comparison, as
    # every one of them being brand new.
    whole = args.all and args.analyses
    destination = ROOT / ('summary.json' if whole else 'summary-partial.json')
    destination.write_text(json.dumps(
        {'when': datetime.now().isoformat(timespec='seconds'),
         'python': platform.python_version(), 'opencv': cv2.__version__,
         'partial': not whole,
         'results': summary}, indent=2), encoding='utf-8')
    if not whole and not args.quiet:
        print(f"\nPartial run: wrote {destination.name}, leaving summary.json "
              f"(the baseline) alone.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
