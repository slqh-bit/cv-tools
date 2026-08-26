# undistort - validation result

**Calibration-based lens correction**  
`src.filters.undistort` | family: Correct | 2026-08-21T12:45:41

## Verdict

**PASS** - 40 runs, no invariant broken, 6 specific checks passed.

40 run(s) refused bad parameters with a clear message, which is the wanted behaviour.

## What this filter specifically promises

- PASS - calibrates within a sane reprojection error: 0.4087 px over 13 views
- PASS - recovers the barrel distortion this lens has: k1=-0.2651, k2=-0.0467
- PASS - straightens every chessboard row it was given: row bow 3.56 -> 0.56 px mean, improved on 13/13 views
- PASS - leaves rows straight to within about a pixel: worst remaining bow 1.08 px, was 5.34 px
- PASS - a saved calibration reloads unchanged: camera matrix and distortion survive the JSON round trip
- PASS - undistort_with_file matches the direct call: the preset path and the library path agree

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `calibration_path=None` on `cctv/brightest.jpg`: refused: undistort needs a calibration file. Produce one with calibrate_from_chessboard() over photos of a chessboard taken on this camera, then save it with save_calibration().
- `calibration_path=None, alpha=0.0` on `cctv/brightest.jpg`: refused: undistort needs a calibration file. Produce one with calibrate_from_chessboard() over photos of a chessboard taken on this camera, then save it with save_calibration().
- `calibration_path=None, alpha=1.0` on `cctv/brightest.jpg`: refused: undistort needs a calibration file. Produce one with calibrate_from_chessboard() over photos of a chessboard taken on this camera, then save it with save_calibration().
- `calibration_path=None, crop=False` on `cctv/brightest.jpg`: refused: undistort needs a calibration file. Produce one with calibrate_from_chessboard() over photos of a chessboard taken on this camera, then save it with save_calibration().
- `calibration_path=None` on `cctv/darkest.jpg`: refused: undistort needs a calibration file. Produce one with calibrate_from_chessboard() over photos of a chessboard taken on this camera, then save it with save_calibration().
- `calibration_path=None, alpha=0.0` on `cctv/darkest.jpg`: refused: undistort needs a calibration file. Produce one with calibrate_from_chessboard() over photos of a chessboard taken on this camera, then save it with save_calibration().
- `calibration_path=None, alpha=1.0` on `cctv/darkest.jpg`: refused: undistort needs a calibration file. Produce one with calibrate_from_chessboard() over photos of a chessboard taken on this camera, then save it with save_calibration().
- `calibration_path=None, crop=False` on `cctv/darkest.jpg`: refused: undistort needs a calibration file. Produce one with calibrate_from_chessboard() over photos of a chessboard taken on this camera, then save it with save_calibration().
- `calibration_path=None` on `cctv/event_fall.jpg`: refused: undistort needs a calibration file. Produce one with calibrate_from_chessboard() over photos of a chessboard taken on this camera, then save it with save_calibration().
- `calibration_path=None, alpha=0.0` on `cctv/event_fall.jpg`: refused: undistort needs a calibration file. Produce one with calibrate_from_chessboard() over photos of a chessboard taken on this camera, then save it with save_calibration().
- `calibration_path=None, alpha=1.0` on `cctv/event_fall.jpg`: refused: undistort needs a calibration file. Produce one with calibrate_from_chessboard() over photos of a chessboard taken on this camera, then save it with save_calibration().
- `calibration_path=None, crop=False` on `cctv/event_fall.jpg`: refused: undistort needs a calibration file. Produce one with calibrate_from_chessboard() over photos of a chessboard taken on this camera, then save it with save_calibration().

## Refused parameters

Rejected on purpose, with the message the user would see.

- `calibration_path=None` -> ValueError: undistort needs a calibration file. Produce one with calibrate_from_chessboard() over photos of a chessboard taken on this camera, then save it with save_calibration().

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `calibration_path=None` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/brightest.jpg` | `calibration_path=None, alpha=0.0` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/brightest.jpg` | `calibration_path=None, alpha=1.0` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/brightest.jpg` | `calibration_path=None, crop=False` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/darkest.jpg` | `calibration_path=None` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/darkest.jpg` | `calibration_path=None, alpha=0.0` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/darkest.jpg` | `calibration_path=None, alpha=1.0` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/darkest.jpg` | `calibration_path=None, crop=False` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/event_fall.jpg` | `calibration_path=None` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/event_fall.jpg` | `calibration_path=None, alpha=0.0` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/event_fall.jpg` | `calibration_path=None, alpha=1.0` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/event_fall.jpg` | `calibration_path=None, crop=False` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/event_optflow.jpg` | `calibration_path=None` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/event_optflow.jpg` | `calibration_path=None, alpha=0.0` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/event_optflow.jpg` | `calibration_path=None, alpha=1.0` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/event_optflow.jpg` | `calibration_path=None, crop=False` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/event_tamper.jpg` | `calibration_path=None` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/event_tamper.jpg` | `calibration_path=None, alpha=0.0` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/event_tamper.jpg` | `calibration_path=None, alpha=1.0` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/event_tamper.jpg` | `calibration_path=None, crop=False` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/flattest.jpg` | `calibration_path=None` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/flattest.jpg` | `calibration_path=None, alpha=0.0` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/flattest.jpg` | `calibration_path=None, alpha=1.0` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/flattest.jpg` | `calibration_path=None, crop=False` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/most_blown.jpg` | `calibration_path=None` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/most_blown.jpg` | `calibration_path=None, alpha=0.0` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/most_blown.jpg` | `calibration_path=None, alpha=1.0` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/most_blown.jpg` | `calibration_path=None, crop=False` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/sharpest.jpg` | `calibration_path=None` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/sharpest.jpg` | `calibration_path=None, alpha=0.0` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/sharpest.jpg` | `calibration_path=None, alpha=1.0` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/sharpest.jpg` | `calibration_path=None, crop=False` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/softest.jpg` | `calibration_path=None` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/softest.jpg` | `calibration_path=None, alpha=0.0` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/softest.jpg` | `calibration_path=None, alpha=1.0` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `cctv/softest.jpg` | `calibration_path=None, crop=False` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `calibration/left01.jpg` | `calibration_path=None` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `calibration/left01.jpg` | `calibration_path=None, alpha=0.0` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `calibration/left01.jpg` | `calibration_path=None, alpha=1.0` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
| `calibration/left01.jpg` | `calibration_path=None, crop=False` | 0.0 | - | refused: ValueError: undistort needs a calibration file. Produce one with calibr |
