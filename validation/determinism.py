"""
Hunt for filters that do not return the same pixels twice.

`sobel` was nondeterministic for eleven hours of this campaign without being
caught, because the harness runs its determinism check once per filter on one
image, and the defect only shows when a pixel sits exactly on an integer
boundary. `cv2.magnitude` differed in the last float bits between calls; one
pixel of one frame happened to be balanced there.

The odds of catching that are a function of how many pixels get examined, so
this runs every registered filter over several images several times. A chain
that does not replay identically cannot back a report, which makes this the
one property worth brute force.

Run:  python validation/determinism.py [--repeats 3] [--images 5]
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.filters import FILTER_REGISTRY                         # noqa: E402
from harness import REQUIRED_VALUES, load_corpus, parameter_matrix  # noqa: E402


def drivable_params(spec, every: bool = False) -> List[Dict[str, Any]]:
    """
    The parameter sets to test for stability.

    Defaults alone leave a real gap: a filter can be reproducible at its
    defaults and not at a slider's extreme, where a different code path or a
    degenerate kernel size comes into play. `--params all` walks the same
    matrix the sweep uses.
    """
    matrix = parameter_matrix(spec, limit=14 if every else 1)
    return matrix if matrix else []


def main(argv: List[str] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--images', type=int, default=5)
    parser.add_argument('--params', choices=('defaults', 'all'),
                        default='defaults',
                        help='test every parameter variant, not just defaults')
    args = parser.parse_args(argv)

    corpus = load_corpus()
    names = [n for n in corpus if n.startswith('cctv/')][:args.images]
    if not names:
        raise SystemExit('No corpus - run validation/build_corpus.py first')

    print(f'{len(FILTER_REGISTRY)} filters x {len(names)} images x '
          f'{args.repeats} runs\n')

    # Filters whose output is random on purpose, with the way to pin it.
    # Flagging these forever would train the reader to ignore the report,
    # which is how a real one gets missed.
    BY_DESIGN = {
        'redact': "method='noise' draws fresh noise each run; pass seed= to "
                  "make a chain replay identically",
    }

    unstable: List[Tuple[str, str, int, int]] = []
    by_design: List[Tuple[str, str]] = []
    skipped: List[str] = []
    started = time.time()

    calls = 0
    for filter_name, spec in FILTER_REGISTRY.items():
        variants = drivable_params(spec, every=args.params == 'all')
        if not variants:
            skipped.append(filter_name)
            continue

        worst = None
        for params in variants:
            for image_name in names:
                image = corpus[image_name]
                try:
                    first = spec.fn(image, **params)
                    calls += 1
                except Exception:
                    break           # a refused parameter set is not the hunt
                if not isinstance(first, np.ndarray):
                    break

                for _ in range(args.repeats - 1):
                    again = spec.fn(image, **params)
                    calls += 1
                    if np.array_equal(first, again):
                        continue
                    difference = np.abs(again.astype(np.int32)
                                        - first.astype(np.int32))
                    pixels = int((difference > 0).sum())
                    worst = (f'{image_name} with {params or "defaults"}',
                             int(difference.max()), pixels)
                    break
                if worst:
                    break
            if worst:
                break

        if worst and filter_name in BY_DESIGN:
            by_design.append((filter_name, worst[0]))
            print(f'by design {filter_name:22s} {BY_DESIGN[filter_name]}')
        elif worst:
            unstable.append((filter_name, *worst))
            print(f'UNSTABLE  {filter_name:22s} on {worst[0]}: '
                  f'{worst[2]} pixel(s) differ by up to {worst[1]}')

    elapsed = time.time() - started
    print(f'\n{len(FILTER_REGISTRY) - len(skipped)} filters exercised in '
          f'{elapsed:.0f}s; {len(skipped)} could not be driven from defaults')
    if skipped:
        print(f'  not driven: {", ".join(sorted(skipped))}')

    if unstable:
        print(f'\n{len(unstable)} filter(s) do not replay identically:')
        for name, image_name, worst_diff, pixels in unstable:
            print(f'  {name:22s} {pixels} pixel(s), up to {worst_diff} levels, '
                  f'on {image_name}')
        return 1

    if by_design:
        print(f'\n{len(by_design)} filter(s) vary on purpose, and say how to '
              f'pin them.')
    print('\nEvery other filter exercised returned identical pixels on every '
          'run.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
