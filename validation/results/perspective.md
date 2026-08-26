# perspective - validation result

**Rectify a quadrilateral from four corners**  
`src.filters.perspective_correction` | family: Correct | 2026-08-21T12:45:36

## Verdict

**PASS** - 33 runs, no invariant broken, 2 specific checks passed.

11 run(s) refused bad parameters with a clear message, which is the wanted behaviour.

## What this filter specifically promises

- PASS - rectifies a grid warped from known corners: straightness 57.572 -> 71.156
- PASS - the result resembles the grid it was warped from: mean absolute difference 13.6/255

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], interpolation=auto` on `cctv/brightest.jpg`: refused: Unknown interpolation 'auto'. Available: bicubic, bilinear, lanczos, nearest
- `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], interpolation=auto` on `cctv/darkest.jpg`: refused: Unknown interpolation 'auto'. Available: bicubic, bilinear, lanczos, nearest
- `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], interpolation=auto` on `cctv/event_fall.jpg`: refused: Unknown interpolation 'auto'. Available: bicubic, bilinear, lanczos, nearest
- `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], interpolation=auto` on `cctv/event_optflow.jpg`: refused: Unknown interpolation 'auto'. Available: bicubic, bilinear, lanczos, nearest
- `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], interpolation=auto` on `cctv/event_tamper.jpg`: refused: Unknown interpolation 'auto'. Available: bicubic, bilinear, lanczos, nearest
- `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], interpolation=auto` on `cctv/flattest.jpg`: refused: Unknown interpolation 'auto'. Available: bicubic, bilinear, lanczos, nearest
- `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], interpolation=auto` on `cctv/most_blown.jpg`: refused: Unknown interpolation 'auto'. Available: bicubic, bilinear, lanczos, nearest
- `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], interpolation=auto` on `cctv/sharpest.jpg`: refused: Unknown interpolation 'auto'. Available: bicubic, bilinear, lanczos, nearest
- `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], interpolation=auto` on `cctv/softest.jpg`: refused: Unknown interpolation 'auto'. Available: bicubic, bilinear, lanczos, nearest
- `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], interpolation=auto` on `ground_truth/grid_perspective.png`: refused: Unknown interpolation 'auto'. Available: bicubic, bilinear, lanczos, nearest
- `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], interpolation=auto` on `reference/perspective_sudoku.png`: refused: Unknown interpolation 'auto'. Available: bicubic, bilinear, lanczos, nearest

## Refused parameters

Rejected on purpose, with the message the user would see.

- `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], interpolation=auto` -> ValueError: Unknown interpolation 'auto'. Available: bicubic, bilinear, lanczos, nearest

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]]` | 5.0 | [362, 561, 3] uint8 mean 138.49 | ok |
| `cctv/brightest.jpg` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], int...` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: bicubic, bilinear, |
| `cctv/brightest.jpg` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], int...` | 0.7 | [362, 561, 3] uint8 mean 138.47 | ok |
| `cctv/darkest.jpg` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]]` | 4.8 | [362, 561, 3] uint8 mean 92.24 | ok |
| `cctv/darkest.jpg` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], int...` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: bicubic, bilinear, |
| `cctv/darkest.jpg` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], int...` | 0.6 | [362, 561, 3] uint8 mean 92.23 | ok |
| `cctv/event_fall.jpg` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]]` | 4.8 | [362, 561, 3] uint8 mean 107.84 | ok |
| `cctv/event_fall.jpg` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], int...` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: bicubic, bilinear, |
| `cctv/event_fall.jpg` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], int...` | 0.7 | [362, 561, 3] uint8 mean 107.8 | ok |
| `cctv/event_optflow.jpg` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]]` | 4.9 | [362, 561, 3] uint8 mean 105.78 | ok |
| `cctv/event_optflow.jpg` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], int...` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: bicubic, bilinear, |
| `cctv/event_optflow.jpg` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], int...` | 0.7 | [362, 561, 3] uint8 mean 105.76 | ok |
| `cctv/event_tamper.jpg` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]]` | 4.9 | [362, 561, 3] uint8 mean 135.78 | ok |
| `cctv/event_tamper.jpg` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], int...` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: bicubic, bilinear, |
| `cctv/event_tamper.jpg` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], int...` | 0.7 | [362, 561, 3] uint8 mean 135.76 | ok |
| `cctv/flattest.jpg` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]]` | 4.8 | [362, 561, 3] uint8 mean 102.71 | ok |
| `cctv/flattest.jpg` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], int...` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: bicubic, bilinear, |
| `cctv/flattest.jpg` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], int...` | 0.7 | [362, 561, 3] uint8 mean 102.69 | ok |
| `cctv/most_blown.jpg` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]]` | 4.8 | [362, 561, 3] uint8 mean 116.1 | ok |
| `cctv/most_blown.jpg` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], int...` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: bicubic, bilinear, |
| `cctv/most_blown.jpg` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], int...` | 0.6 | [362, 561, 3] uint8 mean 116.06 | ok |
| `cctv/sharpest.jpg` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]]` | 4.8 | [362, 561, 3] uint8 mean 111.03 | ok |
| `cctv/sharpest.jpg` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], int...` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: bicubic, bilinear, |
| `cctv/sharpest.jpg` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], int...` | 0.7 | [362, 561, 3] uint8 mean 111.0 | ok |
| `cctv/softest.jpg` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]]` | 4.7 | [362, 561, 3] uint8 mean 105.36 | ok |
| `cctv/softest.jpg` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], int...` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: bicubic, bilinear, |
| `cctv/softest.jpg` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], int...` | 0.7 | [362, 561, 3] uint8 mean 105.34 | ok |
| `ground_truth/grid_perspective.png` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]]` | 4.8 | [362, 561, 3] uint8 mean 233.41 | ok |
| `ground_truth/grid_perspective.png` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], int...` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: bicubic, bilinear, |
| `ground_truth/grid_perspective.png` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], int...` | 0.6 | [362, 561, 3] uint8 mean 234.08 | ok |
| `reference/perspective_sudoku.png` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]]` | 4.8 | [362, 561, 3] uint8 mean 103.82 | ok |
| `reference/perspective_sudoku.png` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], int...` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: bicubic, bilinear, |
| `reference/perspective_sudoku.png` | `corners=[[80, 40], [560, 90], [600, 430], [40, 400]], int...` | 0.6 | [362, 561, 3] uint8 mean 103.81 | ok |

## Artifacts

Outputs written to `validation/artifacts/perspective/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
- `ground_truth_grid_perspective.png`
- `reference_perspective_sudoku.png`
