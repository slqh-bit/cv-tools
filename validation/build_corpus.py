"""
Build the validation corpus.

Three sources, because no one of them proves what the others do:

    cctv/         Real frames from the camera on this desk - real sensor
                  noise, real JPEG history, real lighting. What the tool is
                  for, and the only images whose failures are the ones that
                  matter here.
    reference/    Published test images with a property the CCTV frames do
                  not have on demand: known motion blur, a known chessboard,
                  a known perspective, real camera EXIF.
    ground_truth/ Forgeries built here from the CCTV frames, so the answer is
                  known. A forensic filter that reports something can only be
                  checked against an image whose history was chosen.

Run:  python validation/build_corpus.py
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent
CORPUS = ROOT / 'corpus'
SNAPSHOTS = Path.home() / 'Desktop' / 'ai cam' / 'snapshots'
SAMPLES = ROOT.parent / 'samples'

# Published images with a property that has to be known rather than assumed.
# OpenCV's sample data is BSD-licensed; the Wikimedia files are for the EXIF
# their originals carry, which no generated file can stand in for.
DOWNLOADS = {
    'reference/motion_blur_plate.jpg':
        'https://raw.githubusercontent.com/opencv/opencv/4.x/samples/data/licenseplate_motion.jpg',
    'reference/motion_blur_text.jpg':
        'https://raw.githubusercontent.com/opencv/opencv/4.x/samples/data/text_motionblur.jpg',
    'reference/defocus_text.jpg':
        'https://raw.githubusercontent.com/opencv/opencv/4.x/samples/data/text_defocus.jpg',
    'reference/perspective_sudoku.png':
        'https://raw.githubusercontent.com/opencv/opencv/4.x/samples/data/sudoku.png',
    'reference/chessboard_flat.png':
        'https://raw.githubusercontent.com/opencv/opencv/4.x/samples/data/chessboard.png',
    'reference/building.jpg':
        'https://raw.githubusercontent.com/opencv/opencv/4.x/samples/data/building.jpg',
    'reference/baboon.png':
        'https://raw.githubusercontent.com/opencv/opencv/4.x/samples/data/baboon.jpg',
    'reference/lena.png':
        'https://raw.githubusercontent.com/opencv/opencv/4.x/samples/data/lena.jpg',
}

# Chessboard views for the calibration undistort needs; one view cannot
# calibrate a camera, so the whole set comes down
CALIBRATION = [f'https://raw.githubusercontent.com/opencv/opencv/4.x/samples/data/left{n:02d}.jpg'
               for n in range(1, 15)]

# Real camera EXIF, including an editor's Software tag - metadata forensics
# has nothing to read in a file this repo generated
EXIF_FILES = {
    'reference/exif_camera.jpg':
        'https://upload.wikimedia.org/wikipedia/commons/4/4d/Cat_November_2010-1a.jpg',
    'reference/exif_edited.jpg':
        'https://upload.wikimedia.org/wikipedia/commons/e/e0/Cape_may.jpg',
}


def fetch(url: str, target: Path) -> bool:
    """Download one file, reporting rather than raising if it is unavailable."""
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.stat().st_size > 1024:
        return True

    result = subprocess.run(
        ['curl', '-sL', '-m', '60', '-o', str(target), url],
        capture_output=True, text=True)
    ok = result.returncode == 0 and target.exists() and target.stat().st_size > 1024
    if not ok:
        print(f'  MISSING {target.name} <- {url}')
        target.unlink(missing_ok=True)
    return ok


def pick_cctv() -> dict:
    """
    Choose frames that differ in the ways a filter can fail on.

    Every snapshot is the same room, so picking at random would test one
    exposure eight times. These are chosen by measurement: the darkest, the
    one with the most blown highlights, the noisiest, the flattest.
    """
    files = sorted(SNAPSHOTS.glob('*.jpg'))
    if not files:
        raise SystemExit(f'No snapshots under {SNAPSHOTS}')

    measured = []
    for path in files:
        image = cv2.imread(str(path))
        if image is None:
            continue
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blown = float((gray >= 250).mean())
        crushed = float((gray <= 5).mean())
        # Laplacian variance is the usual focus proxy; low means blurred
        focus = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        measured.append({
            'path': path, 'mean': float(gray.mean()), 'std': float(gray.std()),
            'blown': blown, 'crushed': crushed, 'focus': focus,
            'event': path.stem.split('_')[-1],
        })

    chosen = {
        'darkest': min(measured, key=lambda m: m['mean']),
        'brightest': max(measured, key=lambda m: m['mean']),
        'most_blown': max(measured, key=lambda m: m['blown']),
        'flattest': min(measured, key=lambda m: m['std']),
        'softest': min(measured, key=lambda m: m['focus']),
        'sharpest': max(measured, key=lambda m: m['focus']),
    }
    # One of each event type the camera raises, whatever their statistics
    for event in ('fall', 'tamper', 'optflow'):
        match = next((m for m in measured if m['event'] == event), None)
        if match is not None:
            chosen[f'event_{event}'] = match
    return chosen


def build_ground_truth(frames: dict) -> dict:
    """
    Forgeries with a known answer, from real frames.

    A forensic filter that reports 'something happened here' can only be
    checked against an image where the something was chosen. Built from CCTV
    frames rather than synthetic patterns so the sensor noise, the lens and
    the compression underneath are real.
    """
    out = CORPUS / 'ground_truth'
    out.mkdir(parents=True, exist_ok=True)
    truth = {}

    base = cv2.imread(str(frames['sharpest']['path']))
    height, width = base.shape[:2]

    # 1. Copy-move: a patch pasted elsewhere in the same frame
    clone = base.copy()
    src = (60, 40, 120, 90)                     # x, y, w, h
    dst = (320, 180)
    patch = clone[src[1]:src[1] + src[3], src[0]:src[0] + src[2]].copy()
    clone[dst[1]:dst[1] + src[3], dst[0]:dst[0] + src[2]] = patch
    cv2.imwrite(str(out / 'copy_move.png'), clone)
    truth['copy_move.png'] = {
        'forgery': 'copy-move', 'source': list(src), 'pasted_at': list(dst),
        'expected': 'clone_detect finds a shift of '
                    f'dx={dst[0] - src[0]:+d} dy={dst[1] - src[1]:+d}',
    }

    # 2. Splice at a different JPEG quality: the ghost's whole premise
    high = out / '_tmp_high.jpg'
    cv2.imwrite(str(high), base, [cv2.IMWRITE_JPEG_QUALITY, 95])
    reloaded = cv2.imread(str(high))
    region = (200, 120, 200, 140)
    inset = reloaded[region[1]:region[1] + region[3],
                     region[0]:region[0] + region[2]].copy()
    low = out / '_tmp_low.jpg'
    cv2.imwrite(str(low), inset, [cv2.IMWRITE_JPEG_QUALITY, 55])
    spliced = reloaded.copy()
    spliced[region[1]:region[1] + region[3],
            region[0]:region[0] + region[2]] = cv2.imread(str(low))
    cv2.imwrite(str(out / 'quality_splice.jpg'), spliced,
                [cv2.IMWRITE_JPEG_QUALITY, 95])
    high.unlink(missing_ok=True)
    low.unlink(missing_ok=True)
    truth['quality_splice.jpg'] = {
        'forgery': 'region re-encoded at a lower quality',
        'region': list(region), 'outer_quality': 95, 'inner_quality': 55,
        'expected': 'ghost flags blocks in the region; ela shows raised error there',
    }

    # 3. Untouched control at the same quality, so a report that fires on
    #    everything is caught rather than believed
    cv2.imwrite(str(out / 'clean_control.jpg'), base,
                [cv2.IMWRITE_JPEG_QUALITY, 95])
    truth['clean_control.jpg'] = {
        'forgery': 'none', 'expected': 'no clone shifts; ghost outliers near zero',
    }

    # 4. Known geometry: a straight-line grid the geometric filters must
    #    return to straight
    grid = np.full((480, 640, 3), 245, dtype=np.uint8)
    for x in range(0, 640, 40):
        cv2.line(grid, (x, 0), (x, 480), (20, 20, 20), 1)
    for y in range(0, 480, 40):
        cv2.line(grid, (0, y), (640, y), (20, 20, 20), 1)
    cv2.imwrite(str(out / 'grid_straight.png'), grid)

    # ...and the same grid pushed through a known barrel distortion
    k1 = -0.28
    map_x = np.zeros((480, 640), np.float32)
    map_y = np.zeros((480, 640), np.float32)
    cx, cy = 320.0, 240.0
    norm = max(cx, cy)
    for y in range(480):
        for x in range(640):
            dx, dy = (x - cx) / norm, (y - cy) / norm
            r2 = dx * dx + dy * dy
            factor = 1 + k1 * r2
            map_x[y, x] = cx + dx * factor * norm
            map_y[y, x] = cy + dy * factor * norm
    cv2.imwrite(str(out / 'grid_barrel.png'),
                cv2.remap(grid, map_x, map_y, cv2.INTER_LINEAR))
    truth['grid_barrel.png'] = {
        'forgery': 'none - a known lens distortion',
        'k1_applied': k1,
        'expected': f'barrel with k1 near {-k1:+.2f} straightens it; '
                    'estimate_straightness improves',
    }

    # 5. A known perspective: the grid seen from an angle, corners recorded
    corners = np.float32([[80, 40], [560, 90], [600, 430], [40, 400]])
    target = np.float32([[0, 0], [640, 0], [640, 480], [0, 480]])
    warped = cv2.warpPerspective(grid, cv2.getPerspectiveTransform(target, corners),
                                 (640, 480), borderValue=(255, 255, 255))
    cv2.imwrite(str(out / 'grid_perspective.png'), warped)
    truth['grid_perspective.png'] = {
        'forgery': 'none - a known projective warp',
        'corners': corners.tolist(),
        'expected': 'perspective with those corners returns a square grid',
    }

    return truth


def main() -> int:
    CORPUS.mkdir(parents=True, exist_ok=True)
    manifest = {'cctv': {}, 'reference': [], 'calibration': [], 'ground_truth': {},
                'samples': []}

    print('CCTV frames, chosen by measurement:')
    frames = pick_cctv()
    cctv_dir = CORPUS / 'cctv'
    cctv_dir.mkdir(parents=True, exist_ok=True)
    for role, info in frames.items():
        target = cctv_dir / f'{role}.jpg'
        shutil.copy2(info['path'], target)
        manifest['cctv'][role] = {
            'source': info['path'].name,
            'mean': round(info['mean'], 1), 'std': round(info['std'], 1),
            'blown_pct': round(info['blown'] * 100, 2),
            'crushed_pct': round(info['crushed'] * 100, 2),
            'focus': round(info['focus'], 1),
        }
        print(f"  {role:16s} {info['path'].name}  mean={info['mean']:.0f} "
              f"std={info['std']:.0f} blown={info['blown'] * 100:.1f}%")

    print('Reference images:')
    for name, url in DOWNLOADS.items():
        if fetch(url, CORPUS / name):
            manifest['reference'].append(name)
            print(f'  {name}')

    for url in CALIBRATION:
        name = f'calibration/{Path(url).name}'
        if fetch(url, CORPUS / name):
            manifest['calibration'].append(name)
    print(f"  calibration: {len(manifest['calibration'])} chessboard views")

    for name, url in EXIF_FILES.items():
        if fetch(url, CORPUS / name):
            manifest['reference'].append(name)
            print(f'  {name} (for EXIF)')

    print('Ground truth, built from the CCTV frames:')
    manifest['ground_truth'] = build_ground_truth(frames)
    for name, info in manifest['ground_truth'].items():
        print(f"  {name:22s} {info['forgery']}")

    if SAMPLES.exists():
        target = CORPUS / 'samples'
        target.mkdir(parents=True, exist_ok=True)
        for path in SAMPLES.glob('*.png'):
            shutil.copy2(path, target / path.name)
            manifest['samples'].append(f'samples/{path.name}')
        for path in SAMPLES.glob('*.jpg'):
            shutil.copy2(path, target / path.name)
            manifest['samples'].append(f'samples/{path.name}')

    (CORPUS / 'manifest.json').write_text(json.dumps(manifest, indent=2),
                                          encoding='utf-8')
    total = sum(1 for _ in CORPUS.rglob('*') if _.is_file())
    print(f'\nCorpus: {total} files under {CORPUS}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
