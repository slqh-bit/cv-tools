"""
Run every enhancement filter against every degradation preset and report.

    python scripts/validate_filters.py
    python scripts/validate_filters.py --image samples/cctv_dark.png
    python scripts/validate_filters.py --presets night_ir,low_light_colour
    python scripts/validate_filters.py --output docs/validation.md

The clean source image is the ground truth, so the numbers say how far each
filter moved the degraded frame back toward it. Read ``docs/validation.md``
before drawing conclusions from them: PSNR and SSIM answer the right question
for denoisers and the wrong one for enhancement, which changes the tonal
distribution on purpose.

Exit status is non-zero if any filter raised, so this doubles as a smoke test
over degraded and monochrome input - material the sample images do not cover.
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cv_tools.filters import FILTER_REGISTRY                    # noqa: E402
from cv_tools.validation import (                               # noqa: E402
    PRESETS, compare, degrade_preset, run_matrix, to_markdown,
)

# Filters worth scoring: those meant to *repair* a degraded frame. Analysis
# filters (ELA, FFT spectra, edge maps) return a diagnostic rather than an
# improved image, so a fidelity metric against the original is meaningless for
# them; geometric filters need coordinates no sweep can invent.
CANDIDATES: List[Tuple[str, Dict[str, Any]]] = [
    ('clahe', {}),
    ('auto_contrast', {}),
    ('auto_levels', {}),
    ('histeq', {}),
    ('gaussian_blur', {}),
    ('median_filter', {}),
    ('bilateral_filter', {}),
    ('nl_means', {}),
    ('nl_means_auto', {}),
    ('sharpen', {}),
    ('sharpen_laplacian', {}),
    ('local_contrast', {}),
    ('detail_enhance', {}),
    ('multiscale_detail', {}),
    ('texture_boost', {}),
    ('deblock', {}),
    ('white_balance', {}),
]


def build(names: List[str]) -> List[Tuple[str, Any, Dict[str, Any]]]:
    """Resolve candidate names against the registry, skipping any that moved."""
    built = []
    for name, params in CANDIDATES:
        if names and name not in names:
            continue
        spec = FILTER_REGISTRY.get(name)
        if spec is None:
            print(f'  ! {name} is not in the registry, skipping', file=sys.stderr)
            continue
        built.append((name, spec.fn, params))
    return built


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[1].strip())
    parser.add_argument('--image', default='samples/cctv_dark.png',
                        help='Clean source used as ground truth')
    parser.add_argument('--presets', default='',
                        help='Comma-separated degradation presets (default: all)')
    parser.add_argument('--filters', default='',
                        help='Comma-separated filters (default: the repair set)')
    parser.add_argument('--seed', type=int, default=7,
                        help='Seed, so a run is reproducible')
    parser.add_argument('--output', help='Write the Markdown report here')
    parser.add_argument('--save-degraded', help='Directory to write degraded frames into')
    args = parser.parse_args(argv)

    clean = cv2.imread(args.image)
    if clean is None:
        print(f'Could not read {args.image}', file=sys.stderr)
        return 2

    preset_names = [p.strip() for p in args.presets.split(',') if p.strip()] or sorted(PRESETS)
    unknown = [p for p in preset_names if p not in PRESETS]
    if unknown:
        print(f'Unknown preset(s): {", ".join(unknown)}', file=sys.stderr)
        return 2

    filter_names = [f.strip() for f in args.filters.split(',') if f.strip()]
    filters = build(filter_names)
    if not filters:
        print('No filters selected', file=sys.stderr)
        return 2

    print(f'Ground truth: {args.image}  {clean.shape[1]}x{clean.shape[0]}')
    print(f'{len(filters)} filters x {len(preset_names)} degradations '
          f'= {len(filters) * len(preset_names)} measurements\n')

    degradations = []
    for name in preset_names:
        degraded = degrade_preset(clean, name, seed=args.seed)
        metrics = compare(clean, degraded)
        print(f'  {name:20} psnr={metrics["psnr"]:6.2f} dB  '
              f'ssim={metrics["ssim"]:.3f}  sharpness={metrics["sharpness"]:.1f}')
        degradations.append((name, degraded))
        if args.save_degraded:
            out_dir = Path(args.save_degraded)
            out_dir.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(out_dir / f'{name}.png'), degraded)

    results = run_matrix(clean, degradations, filters)
    failed = [r for r in results if r.error]

    print(f'\n{len(results) - len(failed)} scored, {len(failed)} raised\n')

    # Best per degradation is the practical answer: which filter to reach for.
    print('Best PSNR gain per degradation:')
    for name in preset_names:
        scored = [r for r in results if r.degradation == name and not r.error]
        if not scored:
            continue
        best = max(scored, key=lambda r: r.psnr_delta)
        print(f'  {name:20} {best.filter_name:20} {best.psnr_delta:+.2f} dB  '
              f'ssim {best.ssim_delta:+.3f}')

    report = to_markdown(results)
    if args.output:
        Path(args.output).write_text(report + '\n')
        print(f'\nWrote {args.output}')
    else:
        print('\n' + report)

    for result in failed:
        print(f'  ! {result.filter_name} on {result.degradation}: {result.error}',
              file=sys.stderr)
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
