"""
Does every check that was written actually get run?

Twice in this campaign a group of checks was written, registered, and never
executed - report checks in hour 10, the differential group in hour 15. Both
times the symptom was the same: a clean sweep that had quietly tested less
than it claimed, with nothing anywhere saying so.

This compares what `checks.py` registers against what the last sweep recorded
in `summary.json`, and fails if anything registered was not run. A check that
does not run is worse than a check that does not exist, because the absence
looks like a pass.

Run:  python validation/coverage.py     (after a --all --analyses sweep)
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import checks as checks_module                                  # noqa: E402
from src.filters import ANALYSIS_REGISTRY, FILTER_REGISTRY      # noqa: E402

ROOT = Path(__file__).resolve().parent


def main() -> int:
    summary_path = ROOT / 'summary.json'
    if not summary_path.exists():
        raise SystemExit('No summary.json - run the harness with --all --analyses')

    summary = json.loads(summary_path.read_text(encoding='utf-8'))
    ran: Dict[str, int] = {}
    for entry in summary['results']:
        key = (f"{entry['name']}:report" if entry['kind'] == 'analysis'
               and f"{entry['name']}:report" in checks_module.CHECKS
               else entry['name'])
        ran[key] = max(ran.get(key, 0), entry['checks'])

    registered = sorted(checks_module.CHECKS)
    never_run: List[str] = []
    empty: List[str] = []

    for name in registered:
        if name not in ran:
            never_run.append(name)
        elif ran[name] == 0:
            empty.append(name)

    total_registered = 0
    for name, check in checks_module.CHECKS.items():
        # Counting the assertions needs the check to run, which the sweep has
        # already done; the recorded number is what matters here
        total_registered += ran.get(name, 0)

    print(f'{len(registered)} check groups registered in checks.py')
    print(f'{sum(1 for n in registered if ran.get(n, 0))} of them ran in the '
          f'last sweep, contributing {total_registered} assertions\n')

    unchecked = [n for n in FILTER_REGISTRY if n not in checks_module.CHECKS]
    unchecked_reports = [n for n in ANALYSIS_REGISTRY
                         if n not in checks_module.CHECKS
                         and f'{n}:report' not in checks_module.CHECKS]
    print(f'{len(unchecked)} of {len(FILTER_REGISTRY)} filters have no specific '
          f'checks, and {len(unchecked_reports)} of {len(ANALYSIS_REGISTRY)} '
          f'reports')
    if unchecked:
        print(f'  filters: {", ".join(sorted(unchecked))}')

    if never_run or empty:
        print()
        if never_run:
            print('REGISTERED BUT NEVER RUN - the sweep does not reach these:')
            for name in never_run:
                print(f'  {name}')
        if empty:
            print('RAN BUT CONTRIBUTED NOTHING - the group returned no '
                  'assertions:')
            for name in empty:
                print(f'  {name}')
        return 1

    print('\nEvery registered check group ran in the last sweep.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
