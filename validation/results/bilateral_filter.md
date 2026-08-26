# bilateral_filter - validation result

**Edge-preserving noise reduction**  
`src.filters.smoothing` | family: Enhance | 2026-08-21T12:44:49

## Verdict

**PASS** - 45 runs, no invariant broken, 5 specific checks passed.

## What this filter specifically promises

- PASS - bilateral_filter does not move content: the marker centred at (163.5, 163.5) reads centred at (163.5, 163.5)
- PASS - bilateral_filter keeps the red block red: channel 0 dominates, expected 0
- PASS - bilateral_filter keeps the green block green: channel 1 dominates, expected 1
- PASS - bilateral_filter keeps the blue block blue: channel 2 dominates, expected 2
- PASS - bilateral_filter reaches both halves of the frame: mean change 7.26 left against 7.26 right

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 5.0 | [362, 640, 3] uint8 mean 163.64 | ok |
| `cctv/brightest.jpg` | `sigma_color=1.0` | 4.4 | [362, 640, 3] uint8 mean 163.53 | ok |
| `cctv/brightest.jpg` | `sigma_color=200.0` | 4.7 | [362, 640, 3] uint8 mean 163.7 | ok |
| `cctv/brightest.jpg` | `sigma_space=1.0` | 5.1 | [362, 640, 3] uint8 mean 163.57 | ok |
| `cctv/brightest.jpg` | `sigma_space=200.0` | 5.0 | [362, 640, 3] uint8 mean 163.64 | ok |
| `cctv/darkest.jpg` | `defaults` | 4.6 | [362, 640, 3] uint8 mean 111.01 | ok |
| `cctv/darkest.jpg` | `sigma_color=1.0` | 4.6 | [362, 640, 3] uint8 mean 110.93 | ok |
| `cctv/darkest.jpg` | `sigma_color=200.0` | 4.7 | [362, 640, 3] uint8 mean 111.12 | ok |
| `cctv/darkest.jpg` | `sigma_space=1.0` | 4.5 | [362, 640, 3] uint8 mean 110.95 | ok |
| `cctv/darkest.jpg` | `sigma_space=200.0` | 5.0 | [362, 640, 3] uint8 mean 111.01 | ok |
| `cctv/event_fall.jpg` | `defaults` | 4.5 | [362, 640, 3] uint8 mean 125.57 | ok |
| `cctv/event_fall.jpg` | `sigma_color=1.0` | 4.5 | [362, 640, 3] uint8 mean 125.51 | ok |
| `cctv/event_fall.jpg` | `sigma_color=200.0` | 5.9 | [362, 640, 3] uint8 mean 125.79 | ok |
| `cctv/event_fall.jpg` | `sigma_space=1.0` | 4.6 | [362, 640, 3] uint8 mean 125.53 | ok |
| `cctv/event_fall.jpg` | `sigma_space=200.0` | 4.5 | [362, 640, 3] uint8 mean 125.57 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 4.8 | [362, 640, 3] uint8 mean 125.48 | ok |
| `cctv/event_optflow.jpg` | `sigma_color=1.0` | 6.1 | [362, 640, 3] uint8 mean 125.42 | ok |
| `cctv/event_optflow.jpg` | `sigma_color=200.0` | 5.7 | [362, 640, 3] uint8 mean 125.65 | ok |
| `cctv/event_optflow.jpg` | `sigma_space=1.0` | 5.6 | [362, 640, 3] uint8 mean 125.44 | ok |
| `cctv/event_optflow.jpg` | `sigma_space=200.0` | 5.2 | [362, 640, 3] uint8 mean 125.48 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 5.4 | [362, 640, 3] uint8 mean 160.72 | ok |
| `cctv/event_tamper.jpg` | `sigma_color=1.0` | 4.6 | [362, 640, 3] uint8 mean 160.62 | ok |
| `cctv/event_tamper.jpg` | `sigma_color=200.0` | 4.5 | [362, 640, 3] uint8 mean 160.78 | ok |
| `cctv/event_tamper.jpg` | `sigma_space=1.0` | 4.7 | [362, 640, 3] uint8 mean 160.65 | ok |
| `cctv/event_tamper.jpg` | `sigma_space=200.0` | 4.5 | [362, 640, 3] uint8 mean 160.72 | ok |
| `cctv/flattest.jpg` | `defaults` | 4.5 | [362, 640, 3] uint8 mean 121.55 | ok |
| `cctv/flattest.jpg` | `sigma_color=1.0` | 4.6 | [362, 640, 3] uint8 mean 121.5 | ok |
| `cctv/flattest.jpg` | `sigma_color=200.0` | 4.6 | [362, 640, 3] uint8 mean 121.71 | ok |
| `cctv/flattest.jpg` | `sigma_space=1.0` | 4.5 | [362, 640, 3] uint8 mean 121.52 | ok |
| `cctv/flattest.jpg` | `sigma_space=200.0` | 5.4 | [362, 640, 3] uint8 mean 121.55 | ok |
| `cctv/most_blown.jpg` | `defaults` | 4.5 | [362, 640, 3] uint8 mean 138.17 | ok |
| `cctv/most_blown.jpg` | `sigma_color=1.0` | 4.7 | [362, 640, 3] uint8 mean 138.08 | ok |
| `cctv/most_blown.jpg` | `sigma_color=200.0` | 4.4 | [362, 640, 3] uint8 mean 138.31 | ok |
| `cctv/most_blown.jpg` | `sigma_space=1.0` | 4.5 | [362, 640, 3] uint8 mean 138.1 | ok |
| `cctv/most_blown.jpg` | `sigma_space=200.0` | 5.3 | [362, 640, 3] uint8 mean 138.17 | ok |
| `cctv/sharpest.jpg` | `defaults` | 4.5 | [362, 640, 3] uint8 mean 131.79 | ok |
| `cctv/sharpest.jpg` | `sigma_color=1.0` | 4.5 | [362, 640, 3] uint8 mean 131.76 | ok |
| `cctv/sharpest.jpg` | `sigma_color=200.0` | 4.5 | [362, 640, 3] uint8 mean 131.96 | ok |
| `cctv/sharpest.jpg` | `sigma_space=1.0` | 5.5 | [362, 640, 3] uint8 mean 131.75 | ok |
| `cctv/sharpest.jpg` | `sigma_space=200.0` | 4.4 | [362, 640, 3] uint8 mean 131.79 | ok |
| `cctv/softest.jpg` | `defaults` | 4.4 | [362, 640, 3] uint8 mean 125.44 | ok |
| `cctv/softest.jpg` | `sigma_color=1.0` | 4.5 | [362, 640, 3] uint8 mean 125.38 | ok |
| `cctv/softest.jpg` | `sigma_color=200.0` | 4.9 | [362, 640, 3] uint8 mean 125.53 | ok |
| `cctv/softest.jpg` | `sigma_space=1.0` | 6.3 | [362, 640, 3] uint8 mean 125.4 | ok |
| `cctv/softest.jpg` | `sigma_space=200.0` | 4.5 | [362, 640, 3] uint8 mean 125.44 | ok |

## Artifacts

Outputs written to `validation/artifacts/bilateral_filter/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
