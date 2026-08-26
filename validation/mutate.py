"""
Mutation test for the checks themselves.

A check that passes tells you nothing until you know what would make it fail.
This replaces each filter with an identity - it returns its input untouched -
and runs that filter's checks against the broken version. Anything still
passing is not testing the filter.

Some passes are correct and expected: `levels` promises that its *defaults*
are an identity, and an identity filter honours that. Those are listed
separately from the ones that need a look.

Run:  python validation/mutate.py
"""

import sys
from pathlib import Path
from typing import Any, Callable, Dict, List

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import checks as checks_module                                  # noqa: E402
from harness import load_corpus                                 # noqa: E402

# Checks that an identity filter should legitimately satisfy, because the
# thing being promised is genuinely true of an identity
EXPECTED_UNDER_IDENTITY = {
    'defaults are an exact identity',
    'defaults are an identity',
    'a straight line is an identity',
    'factor 1.0 is an identity',
    'factor 1.0 returns the image within colour-space rounding',
    'a monotonic preset stays monotonic',
    'a round trip returns close to the original',
    'nothing outside the region changes',
    'global equalization amplifies noise (expected, documented)',
    'a full turn returns the image, to interpolation error',
    'four quarter turns come back to the start',
}

# The cross-cutting invariants assert that a filter *preserves* something -
# position, channel order. An identity preserves both, necessarily. They pair
# with 'reaches both halves of the frame', which an identity fails, so the set
# as a whole still discriminates.
PRESERVATION_PHRASES = (
    'does not move content',
    'keeps the red block red',
    'keeps the green block green',
    'keeps the blue block blue',
)

# Guards rather than discriminators: they assert a filter does NOT do
# something harmful, which a filter doing nothing also satisfies. They cannot
# fail under this mutation by construction, and that is not a defect - but
# each one needs a positive check beside it, or the filter has only been
# tested for what it avoids.
# Checks that verify a report's shape rather than its content: the keys are
# present and named as the renderer expects. A frozen measurement satisfies
# them, correctly - the contract being tested is structural.
STRUCTURAL = {
    'reports the block statistics the report renders',
}

# Phrases marking a negative guard wherever they appear, so a family of
# generated checks does not have to be listed filter by filter
GUARD_PHRASES = (
    'on the slider flattens the image',
)

NEGATIVE_GUARDS = {
    'does not clip the frame at full strength',
    'heavy sharpening does not clip most of the frame',
    'does not multiply shadow noise beyond 3x',
    'keeps most of the edge structure',
}


def identity(image: np.ndarray, *_args: Any, **_kwargs: Any) -> np.ndarray:
    """A filter that does nothing, for finding checks that notice nothing."""
    return image.copy()


def freeze(function: Callable) -> Callable:
    """
    A measurement that stops responding to its input.

    The identity mutation cannot break a function that returns a dict - there
    is no "do nothing" version of `noise_report`. Freezing is the equivalent:
    it answers one real call and then returns that same answer for every
    input afterwards. A check that verifies the number *changes with the
    image* fails; a check that only verifies the keys exist passes, and is
    thereby shown to be structural.
    """
    cache = {}

    def frozen(*args: Any, **kwargs: Any) -> Any:
        if 'value' not in cache:
            cache['value'] = function(*args, **kwargs)
        return cache['value']

    return frozen


def patch_registry(make_broken: Callable[[Callable], Callable]) -> Callable[[], None]:
    """
    Damage every filter as the registry serves it, and return an undo.

    Patching the names a check imported is not enough: a check that calls
    `resolve_filter(name).fn` reaches the real function whatever those names
    hold. The cross-cutting invariants do exactly that, so without this they
    ran against undamaged filters and every mutation reported them as blind.
    """
    from dataclasses import replace

    from src.filters.registry import FILTER_REGISTRY

    originals = dict(FILTER_REGISTRY)
    for name, spec in originals.items():
        FILTER_REGISTRY[name] = replace(spec, fn=make_broken(spec.fn))

    def restore() -> None:
        FILTER_REGISTRY.clear()
        FILTER_REGISTRY.update(originals)

    return restore


def image_returning_names() -> List[str]:
    """Every filter function the checks module holds a reference to."""
    names = []
    for name, value in vars(checks_module).items():
        if not callable(value) or name.startswith('_'):
            continue
        if getattr(value, '__module__', '').startswith('src.filters'):
            names.append(name)
    return names


def _prime(wrappers: Dict[str, Callable]) -> None:
    """
    Fill each frozen cache from an input the checks never ask about.

    Running the check twice does not work: the cache fills from the same first
    call both times, so whichever assertion calls a measurement first still
    receives the right answer to its own question. The value has to come from
    somewhere else entirely - a flat grey frame, an unrelated file, an empty
    tag set - so that every answer the check then receives is foreign to it.
    """
    import tempfile

    flat = np.full((64, 96, 3), 96, np.uint8)
    with tempfile.TemporaryDirectory() as directory:
        decoy = Path(directory) / 'decoy.jpg'
        cv2.imwrite(str(decoy), flat, [cv2.IMWRITE_JPEG_QUALITY, 10])

        primers = {
            'estimate_noise': lambda fn: fn(flat),
            'noise_report': lambda fn: fn(flat),
            'ela_stats': lambda fn: fn(flat, quality=10),
            'error_level_analysis': lambda fn: fn(flat, quality=10),
            'blockiness_score': lambda fn: fn(flat),
            'estimate_jpeg_quality': lambda fn: fn(decoy),
            'metadata_report': lambda fn: fn(decoy),
            'check_timestamps': lambda fn: fn({}),
            'detect_editing_software': lambda fn: fn({}),
        }
        for name, prime in primers.items():
            wrapper = wrappers.get(name)
            if wrapper is None:
                continue
            try:
                prime(wrapper)
            except Exception:
                # A measurement that refuses the decoy is fine; the check will
                # then get a real answer and has to earn its pass anyway
                pass


def main() -> int:
    corpus = load_corpus()
    if not corpus:
        raise SystemExit('No corpus - run validation/build_corpus.py first')

    originals = {name: getattr(checks_module, name)
                 for name in image_returning_names()}
    print(f'{len(originals)} filter functions reachable from the checks\n')

    survived: Dict[str, List[str]] = {}
    expected: Dict[str, List[str]] = {}
    guards: Dict[str, List[str]] = {}
    total_checks = total_failed = 0

    report_checks = {'noise', 'ela:report', 'compression', 'metadata'}

    for filter_name, check in sorted(checks_module.CHECKS.items()):
        # Break everything the check can reach, then ask what it still
        # believes. Measurements are frozen rather than emptied: a report that
        # returns nothing is caught by a KeyError, which proves less than a
        # report that looks right and is simply not listening.
        frozen = filter_name in report_checks
        broken = freeze if frozen else (lambda f: identity)
        wrappers = {}
        for name, value in originals.items():
            wrapper = broken(value)
            wrappers[name] = wrapper
            setattr(checks_module, name, wrapper)
        restore = patch_registry(broken)
        try:
            if frozen:
                _prime(wrappers)
            results = check(corpus)
        except Exception as exc:
            # A check that cannot even run against a broken filter is fine:
            # it noticed
            results = [(f'raised {type(exc).__name__}', False, str(exc)[:70])]
        finally:
            restore()
            for name, value in originals.items():
                setattr(checks_module, name, value)

        for what, ok, _detail in results:
            total_checks += 1
            if not ok:
                total_failed += 1
                continue
            if (what in EXPECTED_UNDER_IDENTITY
                    or any(phrase in what for phrase in PRESERVATION_PHRASES)):
                bucket = expected
            elif (what in NEGATIVE_GUARDS or what in STRUCTURAL
                  or any(phrase in what for phrase in GUARD_PHRASES)):
                bucket = guards
            else:
                bucket = survived
            bucket.setdefault(filter_name, []).append(what)

    print(f'{total_failed} of {total_checks} checks failed against a filter '
          f'that does nothing.\n')

    if expected:
        print('Passed, and should have - these promise something an identity '
              'genuinely keeps:')
        for filter_name, items in sorted(expected.items()):
            for what in items:
                print(f'  {filter_name:20s} {what}')
        print()

    if guards:
        print('Guards - they assert the filter does not do something harmful, '
              'which doing nothing also satisfies:')
        for filter_name, items in sorted(guards.items()):
            for what in items:
                print(f'  {filter_name:20s} {what}')
        print()

    if survived:
        print('Passed against a filter that does nothing - these are not '
              'testing what they claim:')
        for filter_name, items in sorted(survived.items()):
            for what in items:
                print(f'  {filter_name:20s} {what}')
    else:
        print('Nothing else survived.')

    return 0


if __name__ == '__main__':
    sys.exit(main())
