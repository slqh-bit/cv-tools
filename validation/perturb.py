"""
Perturbing mutation: filters that work, but subtly wrongly.

`mutate.py` replaces a filter with an identity, which catches a check that
notices nothing at all. It cannot catch a check that measures the right
quantity while ignoring where, or to which channel, the filter applied it - a
sharpen that sharpens the blue channel raises the same Laplacian variance a
correct one does.

Each perturbation here runs the real filter and then damages its output in a
way a real defect would:

    channels    red and blue swapped - the BGR/RGB confusion every OpenCV
                codebase produces at least once
    shift       the result rolled four pixels - an off-by-N in a coordinate
    gain        every value scaled by 1.1 and clipped - a normalisation error
    half        the filter applied to the left half only - a region bug

A check that passes under one of these is not verifying that property. That
may be fine, and it may be the whole point of the check; what matters is
knowing which.

Run:  python validation/perturb.py
"""

import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import checks as checks_module                                  # noqa: E402
from harness import load_corpus                                 # noqa: E402
from mutate import image_returning_names, patch_registry        # noqa: E402


def _swap_channels(result: np.ndarray) -> np.ndarray:
    if result.ndim == 3 and result.shape[2] >= 3:
        out = result.copy()
        out[:, :, [0, 2]] = out[:, :, [2, 0]]
        return out
    return result


def _shift(result: np.ndarray) -> np.ndarray:
    return np.roll(np.roll(result, 4, axis=0), 4, axis=1)


def _gain(result: np.ndarray) -> np.ndarray:
    return np.clip(result.astype(np.float32) * 1.1, 0, 255).astype(result.dtype)


PERTURBATIONS: Dict[str, Callable[[np.ndarray], np.ndarray]] = {
    'channels': _swap_channels,
    'shift': _shift,
    'gain': _gain,
}


def wrap(function: Callable, damage: Callable[[np.ndarray], np.ndarray],
         half_only: bool = False) -> Callable:
    """Run the real filter, then damage what it produced."""

    def damaged(image: np.ndarray, *args: Any, **kwargs: Any) -> Any:
        result = function(image, *args, **kwargs)
        if not isinstance(result, np.ndarray) or result.size == 0:
            return result
        if half_only:
            # The filter reached only the left half; the rest is untouched
            if result.shape == np.asarray(image).shape:
                out = np.asarray(image).copy()
                width = result.shape[1] // 2
                out[:, :width] = result[:, :width]
                return out
            return result
        return damage(result)

    return damaged


def run_mode(corpus: Dict[str, np.ndarray], label: str,
             damage: Callable, half_only: bool = False) -> List[Tuple[str, str]]:
    """Run every check against filters damaged this way; return what survived."""
    originals = {name: getattr(checks_module, name)
                 for name in image_returning_names()}
    survivors: List[Tuple[str, str]] = []
    total = failed = 0

    for filter_name, check in sorted(checks_module.CHECKS.items()):
        if filter_name in {'noise', 'ela:report', 'compression', 'metadata'}:
            continue        # measurements, not image filters - mutate.py covers them
        for name, value in originals.items():
            setattr(checks_module, name, wrap(value, damage, half_only))
        restore = patch_registry(lambda fn: wrap(fn, damage, half_only))
        try:
            results = check(corpus)
        except Exception:
            results = [('raised', False, '')]
        finally:
            restore()
            for name, value in originals.items():
                setattr(checks_module, name, value)

        for what, ok, _detail in results:
            total += 1
            if ok:
                survivors.append((filter_name, what))
            else:
                failed += 1

    print(f'{label:10s} {failed:3d}/{total:3d} checks noticed the damage')
    return survivors


def main() -> int:
    corpus = load_corpus()
    if not corpus:
        raise SystemExit('No corpus - run validation/build_corpus.py first')

    print('Checks that FAIL have noticed the damage. Checks that pass have '
          'not.\n')
    results = {}
    for label, damage in PERTURBATIONS.items():
        results[label] = run_mode(corpus, label, damage)
    results['half'] = run_mode(corpus, 'half', lambda r: r, half_only=True)

    print()
    for label, survivors in results.items():
        blind = sorted({f'{name}: {what}' for name, what in survivors})
        print(f'--- survived "{label}" ({len(blind)}) ---')
        for item in blind[:14]:
            print(f'  {item}')
        if len(blind) > 14:
            print(f'  ... and {len(blind) - 14} more')
        print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
