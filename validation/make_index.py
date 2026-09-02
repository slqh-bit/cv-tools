"""Roll the per-filter result files up into one index."""
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
summary = json.loads((ROOT / 'summary.json').read_text(encoding='utf-8'))

rows = sorted(summary['results'], key=lambda r: (-r['failures'], -r['failed_checks'], r['name']))
clean = [r for r in rows if not r['failures'] and not r['failed_checks']]
dirty = [r for r in rows if r['failures'] or r['failed_checks']]

lines = [
    '# Validation campaign - index',
    '',
    f"Run {summary['when']} | Python {summary['python']} | OpenCV {summary['opencv']}  ",
    f"{len(rows)} filters and reports, "
    f"{sum(r['runs'] for r in rows)} runs, "
    f"{sum(r['checks'] for r in rows)} specific checks.",
    '',
    'Corpus: 9 CCTV frames chosen by measurement from the 200 on this desk, '
    'published reference images with a known property, and forgeries built '
    'here from the CCTV frames so the answer is known. See `corpus/manifest.json`.',
    '',
    '## Needs attention',
    '',
    '| filter | runs | defects | checks | seconds | result |',
    '|---|---|---|---|---|---|',
]
for r in dirty:
    suffix = '-report' if r['kind'] == 'analysis' else ''
    lines.append(f"| **{r['name']}**{' (report)' if suffix else ''} | {r['runs']} | {r['failures']} | "
                 f"{r['checks'] - r['failed_checks']}/{r['checks']} | {r['seconds']} | "
                 f"[result](results/{r['name']}{suffix}.md) |")

lines += ['', '## Clean', '', '| filter | runs | checks | seconds | result |',
          '|---|---|---|---|---|']
for r in clean:
    suffix = '-report' if r['kind'] == 'analysis' else ''
    lines.append(f"| {r['name']}{' (report)' if suffix else ''} | {r['runs']} | "
                 f"{r['checks']}/{r['checks']} | "
                 f"{r['seconds']} | [result](results/{r['name']}{suffix}.md) |")

(ROOT / 'RESULTS.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'{len(rows)} entries -> validation/RESULTS.md ({len(dirty)} need attention)')
