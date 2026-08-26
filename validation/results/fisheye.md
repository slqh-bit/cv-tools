# fisheye - validation result

**Equidistant fisheye correction**  
`src.filters.fisheye_correction` | family: Correct | 2026-08-21T12:45:38

## Verdict

**PASS** - 70 runs, no invariant broken, 4 specific checks passed.

10 run(s) refused bad parameters with a clear message, which is the wanted behaviour.

## What this filter specifically promises

- PASS - some strength straightens a distorted grid: straightness 20.550 -> 26.609 over strength 0.2-0.6
- PASS - border mode constant fills the empty corners: (480, 640, 3), corner value [245, 245, 245]
- PASS - border mode replicate fills the empty corners: (480, 640, 3), corner value [245, 245, 245]
- PASS - border mode reflect fills the empty corners: (480, 640, 3), corner value [245, 245, 245]

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `strength=0.0` on `cctv/brightest.jpg`: output identical to input
- `strength=2.0` on `cctv/brightest.jpg`: refused: strength must be between 0 and 1, got 2.0
- `strength=0.0` on `cctv/darkest.jpg`: output identical to input
- `strength=2.0` on `cctv/darkest.jpg`: refused: strength must be between 0 and 1, got 2.0
- `strength=0.0` on `cctv/event_fall.jpg`: output identical to input
- `strength=2.0` on `cctv/event_fall.jpg`: refused: strength must be between 0 and 1, got 2.0
- `strength=0.0` on `cctv/event_optflow.jpg`: output identical to input
- `strength=2.0` on `cctv/event_optflow.jpg`: refused: strength must be between 0 and 1, got 2.0
- `strength=0.0` on `cctv/event_tamper.jpg`: output identical to input
- `strength=2.0` on `cctv/event_tamper.jpg`: refused: strength must be between 0 and 1, got 2.0
- `strength=0.0` on `cctv/flattest.jpg`: output identical to input
- `strength=2.0` on `cctv/flattest.jpg`: refused: strength must be between 0 and 1, got 2.0

## Refused parameters

Rejected on purpose, with the message the user would see.

- `strength=2.0` -> ValueError: strength must be between 0 and 1, got 2.0

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 15.9 | [362, 640, 3] uint8 mean 165.23 | ok |
| `cctv/brightest.jpg` | `strength=0.0` | 0.1 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/brightest.jpg` | `strength=2.0` | 0.0 | - | refused: ValueError: strength must be between 0 and 1, got 2.0 |
| `cctv/brightest.jpg` | `zoom=0.5` | 14.4 | [362, 640, 3] uint8 mean 58.07 | ok |
| `cctv/brightest.jpg` | `zoom=3.0` | 15.2 | [362, 640, 3] uint8 mean 115.57 | ok |
| `cctv/brightest.jpg` | `border_mode=replicate` | 15.2 | [362, 640, 3] uint8 mean 165.23 | ok |
| `cctv/brightest.jpg` | `border_mode=reflect` | 15.2 | [362, 640, 3] uint8 mean 165.23 | ok |
| `cctv/darkest.jpg` | `defaults` | 15.6 | [362, 640, 3] uint8 mean 110.07 | ok |
| `cctv/darkest.jpg` | `strength=0.0` | 0.1 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/darkest.jpg` | `strength=2.0` | 0.0 | - | refused: ValueError: strength must be between 0 and 1, got 2.0 |
| `cctv/darkest.jpg` | `zoom=0.5` | 14.1 | [362, 640, 3] uint8 mean 38.51 | ok |
| `cctv/darkest.jpg` | `zoom=3.0` | 14.8 | [362, 640, 3] uint8 mean 98.28 | ok |
| `cctv/darkest.jpg` | `border_mode=replicate` | 14.8 | [362, 640, 3] uint8 mean 110.07 | ok |
| `cctv/darkest.jpg` | `border_mode=reflect` | 15.4 | [362, 640, 3] uint8 mean 110.07 | ok |
| `cctv/event_fall.jpg` | `defaults` | 15.6 | [362, 640, 3] uint8 mean 128.05 | ok |
| `cctv/event_fall.jpg` | `strength=0.0` | 0.1 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_fall.jpg` | `strength=2.0` | 0.0 | - | refused: ValueError: strength must be between 0 and 1, got 2.0 |
| `cctv/event_fall.jpg` | `zoom=0.5` | 15.3 | [362, 640, 3] uint8 mean 43.04 | ok |
| `cctv/event_fall.jpg` | `zoom=3.0` | 19.4 | [362, 640, 3] uint8 mean 113.37 | ok |
| `cctv/event_fall.jpg` | `border_mode=replicate` | 20.8 | [362, 640, 3] uint8 mean 128.05 | ok |
| `cctv/event_fall.jpg` | `border_mode=reflect` | 18.5 | [362, 640, 3] uint8 mean 128.05 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 15.1 | [362, 640, 3] uint8 mean 127.45 | ok |
| `cctv/event_optflow.jpg` | `strength=0.0` | 0.1 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_optflow.jpg` | `strength=2.0` | 0.0 | - | refused: ValueError: strength must be between 0 and 1, got 2.0 |
| `cctv/event_optflow.jpg` | `zoom=0.5` | 14.1 | [362, 640, 3] uint8 mean 43.24 | ok |
| `cctv/event_optflow.jpg` | `zoom=3.0` | 14.6 | [362, 640, 3] uint8 mean 103.73 | ok |
| `cctv/event_optflow.jpg` | `border_mode=replicate` | 15.4 | [362, 640, 3] uint8 mean 127.45 | ok |
| `cctv/event_optflow.jpg` | `border_mode=reflect` | 15.4 | [362, 640, 3] uint8 mean 127.45 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 15.2 | [362, 640, 3] uint8 mean 162.33 | ok |
| `cctv/event_tamper.jpg` | `strength=0.0` | 0.1 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/event_tamper.jpg` | `strength=2.0` | 0.0 | - | refused: ValueError: strength must be between 0 and 1, got 2.0 |
| `cctv/event_tamper.jpg` | `zoom=0.5` | 14.3 | [362, 640, 3] uint8 mean 57.06 | ok |
| `cctv/event_tamper.jpg` | `zoom=3.0` | 20.3 | [362, 640, 3] uint8 mean 112.22 | ok |
| `cctv/event_tamper.jpg` | `border_mode=replicate` | 20.9 | [362, 640, 3] uint8 mean 162.33 | ok |
| `cctv/event_tamper.jpg` | `border_mode=reflect` | 19.3 | [362, 640, 3] uint8 mean 162.33 | ok |
| `cctv/flattest.jpg` | `defaults` | 16.5 | [362, 640, 3] uint8 mean 123.68 | ok |
| `cctv/flattest.jpg` | `strength=0.0` | 0.1 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/flattest.jpg` | `strength=2.0` | 0.0 | - | refused: ValueError: strength must be between 0 and 1, got 2.0 |
| `cctv/flattest.jpg` | `zoom=0.5` | 14.8 | [362, 640, 3] uint8 mean 41.86 | ok |
| `cctv/flattest.jpg` | `zoom=3.0` | 15.4 | [362, 640, 3] uint8 mean 100.14 | ok |
| `cctv/flattest.jpg` | `border_mode=replicate` | 16.1 | [362, 640, 3] uint8 mean 123.68 | ok |
| `cctv/flattest.jpg` | `border_mode=reflect` | 16.4 | [362, 640, 3] uint8 mean 123.68 | ok |
| `cctv/most_blown.jpg` | `defaults` | 19.6 | [362, 640, 3] uint8 mean 137.71 | ok |
| `cctv/most_blown.jpg` | `strength=0.0` | 0.1 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/most_blown.jpg` | `strength=2.0` | 0.0 | - | refused: ValueError: strength must be between 0 and 1, got 2.0 |
| `cctv/most_blown.jpg` | `zoom=0.5` | 14.4 | [362, 640, 3] uint8 mean 47.84 | ok |
| `cctv/most_blown.jpg` | `zoom=3.0` | 14.7 | [362, 640, 3] uint8 mean 120.42 | ok |
| `cctv/most_blown.jpg` | `border_mode=replicate` | 15.1 | [362, 640, 3] uint8 mean 137.71 | ok |
| `cctv/most_blown.jpg` | `border_mode=reflect` | 15.3 | [362, 640, 3] uint8 mean 137.71 | ok |
| `cctv/sharpest.jpg` | `defaults` | 14.9 | [362, 640, 3] uint8 mean 131.08 | ok |
| `cctv/sharpest.jpg` | `strength=0.0` | 0.1 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/sharpest.jpg` | `strength=2.0` | 0.0 | - | refused: ValueError: strength must be between 0 and 1, got 2.0 |
| `cctv/sharpest.jpg` | `zoom=0.5` | 13.8 | [362, 640, 3] uint8 mean 45.66 | ok |
| `cctv/sharpest.jpg` | `zoom=3.0` | 14.9 | [362, 640, 3] uint8 mean 114.02 | ok |
| `cctv/sharpest.jpg` | `border_mode=replicate` | 14.9 | [362, 640, 3] uint8 mean 131.08 | ok |
| `cctv/sharpest.jpg` | `border_mode=reflect` | 14.9 | [362, 640, 3] uint8 mean 131.08 | ok |
| `cctv/softest.jpg` | `defaults` | 14.9 | [362, 640, 3] uint8 mean 126.43 | ok |
| `cctv/softest.jpg` | `strength=0.0` | 0.2 | [362, 640, 3] uint8 mean 125.38 | output identical to input |
| `cctv/softest.jpg` | `strength=2.0` | 0.0 | - | refused: ValueError: strength must be between 0 and 1, got 2.0 |
| `cctv/softest.jpg` | `zoom=0.5` | 14.0 | [362, 640, 3] uint8 mean 44.52 | ok |
| `cctv/softest.jpg` | `zoom=3.0` | 15.1 | [362, 640, 3] uint8 mean 93.64 | ok |
| `cctv/softest.jpg` | `border_mode=replicate` | 15.3 | [362, 640, 3] uint8 mean 126.43 | ok |
| `cctv/softest.jpg` | `border_mode=reflect` | 15.0 | [362, 640, 3] uint8 mean 126.43 | ok |
| `ground_truth/grid_barrel.png` | `defaults` | 20.0 | [480, 640, 3] uint8 mean 233.88 | ok |
| `ground_truth/grid_barrel.png` | `strength=0.0` | 0.1 | [480, 640, 3] uint8 mean 234.18 | output identical to input |
| `ground_truth/grid_barrel.png` | `strength=2.0` | 0.0 | - | refused: ValueError: strength must be between 0 and 1, got 2.0 |
| `ground_truth/grid_barrel.png` | `zoom=0.5` | 18.4 | [480, 640, 3] uint8 mean 79.8 | ok |
| `ground_truth/grid_barrel.png` | `zoom=3.0` | 19.5 | [480, 640, 3] uint8 mean 234.71 | ok |
| `ground_truth/grid_barrel.png` | `border_mode=replicate` | 22.7 | [480, 640, 3] uint8 mean 233.88 | ok |
| `ground_truth/grid_barrel.png` | `border_mode=reflect` | 22.2 | [480, 640, 3] uint8 mean 233.88 | ok |

## Artifacts

Outputs written to `validation/artifacts/fisheye/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
- `ground_truth_grid_barrel.png`
