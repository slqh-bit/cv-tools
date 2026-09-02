"""
Run every registered filter over one image and write the results.

The unit tests prove the filters are *correct*; this shows you what they
*look like*, which is the other half of knowing a toolkit. Each filter runs
with its default parameters, so the output is the starting point you would get
before tuning anything.

    python scripts/filter_gallery.py
    python scripts/filter_gallery.py samples/cloned_region.png -o out/
    python scripts/filter_gallery.py --only clahe,sharpen,curves

Filters needing arguments a signature cannot supply - a region, a set of
corners, a calibration file - are listed in ARGUMENTS below. Any such filter
missing from that table is reported as skipped with its reason, rather than
counted as a failure.

A few filters read a property the default sample does not have, and render
blank on it however correct they are. Those are listed in SOURCES, which
overrides the input image for that filter alone.
"""

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np

# Import from the project root regardless of where this is run from
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from cv_tools.core import ImageLoader, save_image                      # noqa: E402
from cv_tools.filters import FILTER_REGISTRY, CameraCalibration        # noqa: E402
from cv_tools.filters import save_calibration                          # noqa: E402

# Parameters that have no usable default. Scaled to the sample at run time
# where they are fractions of the image.
ARGUMENTS: Dict[str, Dict[str, Any]] = {
    'crop': {'x': 0.15, 'y': 0.25, 'width': 0.5, 'height': 0.4, '_relative': True},
    'roi_crop': {'x': 0.15, 'y': 0.25, 'width': 0.5, 'height': 0.4, '_relative': True},
    'roi_draw': {'x': 0.15, 'y': 0.25, 'width': 0.5, 'height': 0.4, '_relative': True},
    # Runs another filter inside the region, so it needs one named as well
    'roi_filter': {'x': 0.15, 'y': 0.25, 'width': 0.5, 'height': 0.4,
                   'filter_name': 'clahe', '_relative': True},
    'redact': {'x': 0.15, 'y': 0.25, 'width': 0.5, 'height': 0.4, '_relative': True},
    'white_balance_patch': {'x': 0.4, 'y': 0.4, 'width': 0.15, 'height': 0.15,
                            '_relative': True},
    'resize': {'scale': 0.5},
    'rotate': {'angle': 8.0},
    'flip': {'direction': 'horizontal'},
    'canny': {'low_threshold': 50, 'high_threshold': 150},
    'levels': {'black_point': 15, 'gamma': 1.1, 'white_point': 235},
    'curves': {'preset': 'lift_shadows'},
    'invert_channel': {'channel': 'r'},
    'selective_saturation': {'hue_center': 200.0},
    'component': {'space': 'lab', 'channel': 'a'},
    'stain': {'preset': 'h_e'},
    'fit_aspect': {'target_ratio': 16 / 9},
    'perspective': {'corners': [[0.1, 0.1], [0.9, 0.05], [0.95, 0.9], [0.05, 0.95]],
                    '_relative_corners': True},
    'measure_3d': {'base': [0.55, 0.85], 'top': [0.55, 0.55],
                   'reference_base': [0.25, 0.78], 'reference_top': [0.25, 0.52],
                   'horizon': 0.30, 'reference_height': 1800.0,
                   '_relative_points': ('base', 'top', 'reference_base',
                                        'reference_top'),
                   '_relative_rows': ('horizon',)},
    # The reference spans 0.3 of the width and is called 520mm, so the gallery's
    # numbers are at least self-consistent even though the sample has no ruler
    'measure': {'point_a': [0.2, 0.62], 'point_b': [0.72, 0.62],
                'reference_a': [0.2, 0.3], 'reference_b': [0.5, 0.3],
                'reference_length': 520.0,
                '_relative_points': ('point_a', 'point_b',
                                     'reference_a', 'reference_b')},
    'measure_area': {'points': [[0.15, 0.2], [0.62, 0.2],
                                [0.62, 0.52], [0.15, 0.52]],
                     'reference_a': [0.15, 0.75], 'reference_b': [0.45, 0.75],
                     'reference_length': 520.0,
                     '_relative_points': ('reference_a', 'reference_b'),
                     '_relative_polygons': ('points',)},
    'scale_bar': {'reference_a': [0.2, 0.3], 'reference_b': [0.5, 0.3],
                  'reference_length': 520.0, 'length_units': 300.0,
                  '_relative_points': ('reference_a', 'reference_b')},
    'arrow': {'start': [0.72, 0.24], 'end': [0.45, 0.46], 'label': 'detail',
              '_relative_points': ('start', 'end')},
    'text': {'text': 'Exhibit A', 'position': [0.08, 0.14],
             '_relative_points': ('position',)},
    'shape': {'shape': 'rectangle', 'points': [[0.2, 0.25], [0.7, 0.66]],
              'label': 'region', '_relative_polygons': ('points',)},
    'undistort': {'calibration_path': None},   # written during the run
}

# Filters whose output is meaningless on the default sample. `ghost` reads JPEG
# quantisation history, which a never-compressed PNG simply has none of: every
# block matches best at the top quality and the map comes out uniformly white.
SOURCES: Dict[str, str] = {
    'ghost': 'samples/jpeg_ghost.png',
}


def _scale_arguments(name: str, shape: Tuple[int, int]) -> Dict[str, Any]:
    """Turn the relative placeholders above into pixel values for this image."""
    spec = dict(ARGUMENTS.get(name, {}))
    height, width = shape[:2]

    if spec.pop('_relative', False):
        spec['x'] = int(spec['x'] * width)
        spec['y'] = int(spec['y'] * height)
        spec['width'] = int(spec['width'] * width)
        spec['height'] = int(spec['height'] * height)

    if spec.pop('_relative_corners', False):
        spec['corners'] = [[int(x * width), int(y * height)]
                           for x, y in spec['corners']]

    for key in spec.pop('_relative_points', ()):
        x, y = spec[key]
        spec[key] = [int(x * width), int(y * height)]

    for key in spec.pop('_relative_polygons', ()):
        spec[key] = [[int(x * width), int(y * height)] for x, y in spec[key]]

    for key in spec.pop('_relative_rows', ()):
        spec[key] = spec[key] * height

    return spec


def _write_calibration(directory: Path, shape: Tuple[int, int]) -> Path:
    """A plausible calibration, so the undistort filter has something to use."""
    height, width = shape[:2]
    path = directory / '_calibration.json'
    save_calibration(
        CameraCalibration(
            camera_matrix=np.array([[width * 0.9, 0, width / 2],
                                    [0, width * 0.9, height / 2],
                                    [0, 0, 1]], dtype=np.float64),
            distortion=np.array([-0.22, 0.06, 0.0, 0.0, 0.0]),
            image_size=(width, height),
            reprojection_error=0.45,
        ),
        path,
    )
    return path


def _label(image: np.ndarray, text: str) -> np.ndarray:
    """Caption a thumbnail so the contact sheet is readable."""
    if image.ndim == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    elif image.shape[2] == 4:
        image = image[:, :, :3]

    labelled = image.copy()
    (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
    cv2.rectangle(labelled, (0, 0), (min(text_w + 8, labelled.shape[1]), text_h + 8),
                  (0, 0, 0), -1)
    cv2.putText(labelled, text, (4, text_h + 2), cv2.FONT_HERSHEY_SIMPLEX,
                0.4, (255, 255, 255), 1, cv2.LINE_AA)
    return labelled


def build_contact_sheet(results: List[Tuple[str, np.ndarray]],
                        thumb_width: int = 200) -> Optional[np.ndarray]:
    """Tile every successful result into one labelled sheet."""
    if not results:
        return None

    columns = math.ceil(math.sqrt(len(results)))
    rows = math.ceil(len(results) / columns)
    thumb_height = int(thumb_width * 0.75)

    sheet = np.full((rows * thumb_height, columns * thumb_width, 3), 24, dtype=np.uint8)

    for index, (name, image) in enumerate(results):
        thumb = cv2.resize(image, (thumb_width, thumb_height),
                           interpolation=cv2.INTER_AREA)
        thumb = _label(thumb, name)
        row, column = divmod(index, columns)
        sheet[row * thumb_height:(row + 1) * thumb_height,
              column * thumb_width:(column + 1) * thumb_width] = thumb

    return sheet


def run(source: Path, output_dir: Path, only: Optional[List[str]] = None,
        sheet: bool = True) -> int:
    """
    Run the filters and write the outputs.

    Returns:
        Process exit code: non-zero if any filter failed
    """
    with ImageLoader(source) as loader:
        image = loader.load()

    output_dir.mkdir(parents=True, exist_ok=True)
    calibration_path = _write_calibration(output_dir, image.shape)
    ARGUMENTS['undistort']['calibration_path'] = str(calibration_path)

    names = sorted(FILTER_REGISTRY)
    if only:
        unknown = [n for n in only if n not in FILTER_REGISTRY]
        if unknown:
            print(f"error: unknown filter(s): {', '.join(unknown)}", file=sys.stderr)
            return 2
        names = [n for n in names if n in only]

    print(f"Source: {source}  ({image.shape[1]}x{image.shape[0]})")
    print(f"Output: {output_dir}\n")
    print(f"{'filter':<24}{'status':<10}{'output':<18}{'ms':>7}")
    print('-' * 60)

    successes: List[Tuple[str, np.ndarray]] = []
    failures: List[Tuple[str, str]] = []

    for name in names:
        spec = FILTER_REGISTRY[name]

        source_image = image
        override = SOURCES.get(name)
        if override is not None:
            override_path = ROOT / override
            if override_path.exists():
                with ImageLoader(override_path) as loader:
                    source_image = loader.load()
            else:
                failures.append((name, f'needs {override}, run samples/generate_samples.py'))
                print(f"{name:<24}{'skipped':<10}needs {override_path.name}")
                continue

        params = _scale_arguments(name, source_image.shape)

        start = time.perf_counter()
        try:
            result = spec.fn(source_image, **params)
            elapsed = (time.perf_counter() - start) * 1000

            save_image(result, output_dir / f'{name}.png')
            successes.append((name, result))
            shape = 'x'.join(str(v) for v in result.shape)
            print(f"{name:<24}{'ok':<10}{shape:<18}{elapsed:>7.0f}")

        except TypeError as exc:
            # Missing a required argument this script has no entry for
            failures.append((name, f'needs arguments: {exc}'))
            print(f"{name:<24}{'skipped':<10}needs arguments")
        except Exception as exc:
            failures.append((name, f'{type(exc).__name__}: {exc}'))
            print(f"{name:<24}{'FAILED':<10}{type(exc).__name__}")

    print('-' * 60)
    print(f"{len(successes)} ok, {len(failures)} skipped or failed, "
          f"of {len(names)} filters")

    for name, reason in failures:
        print(f"  {name}: {reason}")

    if sheet and successes:
        composite = build_contact_sheet(successes)
        sheet_path = output_dir / '_contact_sheet.png'
        save_image(composite, sheet_path)
        print(f"\nContact sheet: {sheet_path}")

    return 1 if failures else 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description='Run every registered filter over one image.')
    parser.add_argument('input', nargs='?', default='samples/cctv_dark.png',
                        help='Source image (default: samples/cctv_dark.png)')
    parser.add_argument('-o', '--output', default='gallery',
                        help='Output directory (default: gallery)')
    parser.add_argument('--only', help='Comma-separated filter names to run')
    parser.add_argument('--no-sheet', action='store_true',
                        help='Skip the contact sheet')

    args = parser.parse_args(argv)
    only = [n.strip() for n in args.only.split(',')] if args.only else None

    source = Path(args.input)
    if not source.exists():
        print(f"error: no such file: {source}", file=sys.stderr)
        return 2

    return run(source, Path(args.output), only=only, sheet=not args.no_sheet)


if __name__ == '__main__':
    sys.exit(main())
