"""
Compare a validation run against the last recorded one.

The campaign has been run by hand, and its value decays between runs: a result
file from three weeks ago says what the code did three weeks ago. Worse, a
clean campaign is not evidence unless something compares it to the previous
clean campaign - 2386 runs all passing looks identical whether or not a filter
quietly stopped being exercised.

This reads the committed ``summary.json`` first, runs the campaign over it, and
says what changed. It exits non-zero when something got worse, so it can gate a
push.

Why this is not a GitHub Actions job: the corpus is nine real frames from the
camera on this desk, chosen by measurement from two hundred, plus forgeries
built from them so the answer is known. ``build_corpus.py`` reads them from
outside the repository and they are not redistributable, so a hosted runner
cannot assemble the corpus that makes the campaign worth running. The unit
suite runs in CI; this runs where the evidence is.

Run:
    python validation/regress.py                  # run the campaign, then diff
    python validation/regress.py --no-run         # diff what is already there
    python validation/regress.py --baseline b.json --no-run
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent
SUMMARY = ROOT / 'summary.json'

# A run this much slower than the baseline is worth mentioning. Not a failure:
# the campaign shares a machine with whatever else is running, so the threshold
# is set where noise stops being a plausible explanation.
SLOWDOWN_FACTOR = 3.0
SLOWDOWN_FLOOR_SECONDS = 2.0


def load(path: Path) -> Dict[str, Any]:
    """Read a summary file.

    Raises:
        SystemExit: If it is missing or unreadable, since there is nothing to
            compare against and silently treating that as "no change" is the
            failure this script exists to prevent
    """
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError:
        raise SystemExit(
            f'No summary at {path}. Run validation/harness.py --all --analyses '
            f'first, or pass --baseline.') from None
    except json.JSONDecodeError as exc:
        raise SystemExit(f'{path} is not readable JSON: {exc}') from None


def by_name(summary: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Index a summary's results by name, keeping filters and reports apart."""
    indexed = {}
    for result in summary.get('results', []):
        key = result['name']
        if result.get('kind') == 'analysis':
            key = f"{key}:report"
        indexed[key] = result
    return indexed


def failing(result: Dict[str, Any]) -> bool:
    """Whether an entry counts as failing."""
    return bool(result.get('failures', 0) or result.get('failed_checks', 0))


def compare(
    before: Dict[str, Any],
    after: Dict[str, Any],
) -> Tuple[List[str], List[str]]:
    """
    Diff two campaign summaries.

    Returns:
        (regressions, notes) - regressions are what should fail a gate, notes
        are everything else worth printing
    """
    old, new = by_name(before), by_name(after)
    regressions: List[str] = []
    notes: List[str] = []

    for name in sorted(set(old) | set(new)):
        was, now = old.get(name), new.get(name)

        if was is None:
            state = 'failing' if failing(now) else 'clean'
            notes.append(f'new: {name} ({now["runs"]} runs, {state})')
            if failing(now):
                regressions.append(
                    f'{name} is new and already failing '
                    f'({now["failures"]} defects, {now["failed_checks"]} '
                    f'failed checks)')
            continue

        if now is None:
            # Something that used to be covered no longer is. A campaign that
            # stopped exercising a filter reads exactly like one where the
            # filter is fine.
            regressions.append(
                f'{name} was validated before ({was["runs"]} runs) and is '
                f'missing from this run')
            continue

        if failing(now) and not failing(was):
            regressions.append(
                f'{name} broke: {now["failures"]} defects, '
                f'{now["failed_checks"]}/{now["checks"]} checks failing '
                f'(was clean)')
        elif failing(was) and not failing(now):
            notes.append(f'fixed: {name} was failing and is now clean')
        elif failing(now) and failing(was):
            if (now['failures'] > was['failures']
                    or now['failed_checks'] > was['failed_checks']):
                regressions.append(
                    f'{name} got worse: {was["failures"]}->{now["failures"]} '
                    f'defects, {was["failed_checks"]}->{now["failed_checks"]} '
                    f'failed checks')
            else:
                notes.append(f'still failing: {name}')

        if now['runs'] < was['runs']:
            # Fewer runs at the same pass rate means less was checked, which a
            # pass count alone will not show
            regressions.append(
                f'{name} ran {was["runs"] - now["runs"]} fewer cases than '
                f'before ({was["runs"]} -> {now["runs"]})')
        elif now['runs'] > was['runs']:
            notes.append(f'{name}: {was["runs"]} -> {now["runs"]} runs')

        if now['checks'] < was['checks']:
            regressions.append(
                f'{name} lost {was["checks"] - now["checks"]} specific checks '
                f'({was["checks"]} -> {now["checks"]})')

        old_seconds, new_seconds = was.get('seconds', 0), now.get('seconds', 0)
        if (new_seconds > SLOWDOWN_FLOOR_SECONDS
                and old_seconds > 0
                and new_seconds > old_seconds * SLOWDOWN_FACTOR):
            notes.append(
                f'slower: {name} {old_seconds}s -> {new_seconds}s')

    return regressions, notes


def totals(summary: Dict[str, Any]) -> Dict[str, int]:
    """Campaign-wide counts, for the one-line headline."""
    results = summary.get('results', [])
    return {
        'entries': len(results),
        'runs': sum(r.get('runs', 0) for r in results),
        'checks': sum(r.get('checks', 0) for r in results),
        'failing': sum(1 for r in results if failing(r)),
    }


def run_campaign() -> int:
    """
    Run the whole campaign, leaving summary.json and the result files.

    From the repository root, which is where the campaign has always been run
    by hand and therefore what the recorded baseline was measured under. The
    checks no longer depend on it - two of them used to reach the corpus
    through a relative path and silently found nothing from anywhere else -
    but running it anywhere else would compare two things measured differently.
    """
    print('Running the campaign (this takes a few minutes)...', flush=True)
    repository = ROOT.parent
    completed = subprocess.run(
        [sys.executable, str(ROOT / 'harness.py'), '--all', '--analyses', '--quiet'],
        cwd=str(repository),
    )
    if completed.returncode == 0:
        subprocess.run([sys.executable, str(ROOT / 'make_index.py')],
                       cwd=str(repository))
    return completed.returncode


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--no-run', action='store_true',
                        help='Diff the summary already on disk instead of '
                             'running the campaign again')
    parser.add_argument('--baseline', type=Path,
                        help='Summary to compare against (default: the one at '
                             'validation/summary.json before this run)')
    args = parser.parse_args(argv)

    baseline_path = args.baseline or SUMMARY
    before = load(baseline_path)

    if not args.no_run:
        if args.baseline is None:
            # The campaign overwrites summary.json, so the comparison has to
            # hold the previous contents before it starts
            before = json.loads(json.dumps(before))
        code = run_campaign()
        if code != 0:
            print(f'harness.py exited {code}', file=sys.stderr)
            return code

    after = load(SUMMARY)

    if before is after or before == after:
        print('No change since the recorded run.')
        return 0

    # A baseline covering a fraction of what just ran is not a baseline. The
    # harness now keeps partial runs out of summary.json, but an older file may
    # predate that, and reporting eighty filters as "new" buries any real
    # finding among them.
    if before.get('partial') or (
            len(before.get('results', [])) * 2 < len(after.get('results', []))):
        print(f"warning: the baseline has "
              f"{len(before.get('results', []))} entries against this run's "
              f"{len(after.get('results', []))}. It looks like a partial run "
              f"rather than a full campaign, so the comparison below is not "
              f"meaningful. Pass --baseline with a full summary.",
              file=sys.stderr)

    regressions, notes = compare(before, after)
    old_totals, new_totals = totals(before), totals(after)

    print()
    print(f"Baseline {before.get('when', '?')}  "
          f"{old_totals['entries']} entries, {old_totals['runs']} runs, "
          f"{old_totals['checks']} checks, {old_totals['failing']} failing")
    print(f"This run {after.get('when', '?')}  "
          f"{new_totals['entries']} entries, {new_totals['runs']} runs, "
          f"{new_totals['checks']} checks, {new_totals['failing']} failing")

    if notes:
        print()
        for note in notes:
            print(f'  {note}')

    if regressions:
        print()
        print(f'{len(regressions)} regression(s):')
        for regression in regressions:
            print(f'  ! {regression}')
        print()
        print('Nothing was committed. Fix these, or re-run to accept the new '
              'summary.json as the baseline once they are understood.')
        return 1

    print()
    print('No regressions.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
