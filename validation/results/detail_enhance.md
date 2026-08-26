# detail_enhance - validation result

**Edge-preserving texture enhancement**  
`src.filters.detail_enhancement` | family: Enhance | 2026-08-21T12:45:31

## Verdict

**PASS** - 45 runs, no invariant broken, 5 specific checks passed.

## What this filter specifically promises

- PASS - detail_enhance does not move content: the marker centred at (163.5, 163.5) reads centred at (163.5, 163.5)
- PASS - detail_enhance keeps the red block red: channel 0 dominates, expected 0
- PASS - detail_enhance keeps the green block green: channel 1 dominates, expected 1
- PASS - detail_enhance keeps the blue block blue: channel 2 dominates, expected 2
- PASS - detail_enhance reaches both halves of the frame: mean change 13.73 left against 12.82 right

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 37.7 | [362, 640, 3] uint8 mean 163.77 | ok |
| `cctv/brightest.jpg` | `sigma_s=1.0` | 39.8 | [362, 640, 3] uint8 mean 163.23 | ok |
| `cctv/brightest.jpg` | `sigma_s=200.0` | 41.8 | [362, 640, 3] uint8 mean 164.97 | ok |
| `cctv/brightest.jpg` | `sigma_r=0.01` | 37.0 | [362, 640, 3] uint8 mean 163.27 | ok |
| `cctv/brightest.jpg` | `sigma_r=1.0` | 40.1 | [362, 640, 3] uint8 mean 164.71 | ok |
| `cctv/darkest.jpg` | `defaults` | 35.8 | [362, 640, 3] uint8 mean 111.64 | ok |
| `cctv/darkest.jpg` | `sigma_s=1.0` | 37.1 | [362, 640, 3] uint8 mean 110.71 | ok |
| `cctv/darkest.jpg` | `sigma_s=200.0` | 40.9 | [362, 640, 3] uint8 mean 118.25 | ok |
| `cctv/darkest.jpg` | `sigma_r=0.01` | 36.4 | [362, 640, 3] uint8 mean 110.75 | ok |
| `cctv/darkest.jpg` | `sigma_r=1.0` | 37.4 | [362, 640, 3] uint8 mean 112.4 | ok |
| `cctv/event_fall.jpg` | `defaults` | 39.0 | [362, 640, 3] uint8 mean 127.4 | ok |
| `cctv/event_fall.jpg` | `sigma_s=1.0` | 39.9 | [362, 640, 3] uint8 mean 125.45 | ok |
| `cctv/event_fall.jpg` | `sigma_s=200.0` | 44.4 | [362, 640, 3] uint8 mean 131.32 | ok |
| `cctv/event_fall.jpg` | `sigma_r=0.01` | 39.8 | [362, 640, 3] uint8 mean 125.31 | ok |
| `cctv/event_fall.jpg` | `sigma_r=1.0` | 39.1 | [362, 640, 3] uint8 mean 130.55 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 39.2 | [362, 640, 3] uint8 mean 126.54 | ok |
| `cctv/event_optflow.jpg` | `sigma_s=1.0` | 38.4 | [362, 640, 3] uint8 mean 125.27 | ok |
| `cctv/event_optflow.jpg` | `sigma_s=200.0` | 43.7 | [362, 640, 3] uint8 mean 135.16 | ok |
| `cctv/event_optflow.jpg` | `sigma_r=0.01` | 40.7 | [362, 640, 3] uint8 mean 125.26 | ok |
| `cctv/event_optflow.jpg` | `sigma_r=1.0` | 37.7 | [362, 640, 3] uint8 mean 128.47 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 37.6 | [362, 640, 3] uint8 mean 160.8 | ok |
| `cctv/event_tamper.jpg` | `sigma_s=1.0` | 37.6 | [362, 640, 3] uint8 mean 160.33 | ok |
| `cctv/event_tamper.jpg` | `sigma_s=200.0` | 41.6 | [362, 640, 3] uint8 mean 161.89 | ok |
| `cctv/event_tamper.jpg` | `sigma_r=0.01` | 38.6 | [362, 640, 3] uint8 mean 160.36 | ok |
| `cctv/event_tamper.jpg` | `sigma_r=1.0` | 39.0 | [362, 640, 3] uint8 mean 161.84 | ok |
| `cctv/flattest.jpg` | `defaults` | 39.5 | [362, 640, 3] uint8 mean 122.54 | ok |
| `cctv/flattest.jpg` | `sigma_s=1.0` | 38.3 | [362, 640, 3] uint8 mean 121.33 | ok |
| `cctv/flattest.jpg` | `sigma_s=200.0` | 43.8 | [362, 640, 3] uint8 mean 131.21 | ok |
| `cctv/flattest.jpg` | `sigma_r=0.01` | 37.5 | [362, 640, 3] uint8 mean 121.33 | ok |
| `cctv/flattest.jpg` | `sigma_r=1.0` | 38.5 | [362, 640, 3] uint8 mean 124.41 | ok |
| `cctv/most_blown.jpg` | `defaults` | 39.1 | [362, 640, 3] uint8 mean 139.07 | ok |
| `cctv/most_blown.jpg` | `sigma_s=1.0` | 36.6 | [362, 640, 3] uint8 mean 137.91 | ok |
| `cctv/most_blown.jpg` | `sigma_s=200.0` | 41.7 | [362, 640, 3] uint8 mean 146.21 | ok |
| `cctv/most_blown.jpg` | `sigma_r=0.01` | 36.9 | [362, 640, 3] uint8 mean 137.94 | ok |
| `cctv/most_blown.jpg` | `sigma_r=1.0` | 37.2 | [362, 640, 3] uint8 mean 140.4 | ok |
| `cctv/sharpest.jpg` | `defaults` | 38.9 | [362, 640, 3] uint8 mean 134.08 | ok |
| `cctv/sharpest.jpg` | `sigma_s=1.0` | 40.9 | [362, 640, 3] uint8 mean 131.77 | ok |
| `cctv/sharpest.jpg` | `sigma_s=200.0` | 45.0 | [362, 640, 3] uint8 mean 137.95 | ok |
| `cctv/sharpest.jpg` | `sigma_r=0.01` | 40.2 | [362, 640, 3] uint8 mean 131.58 | ok |
| `cctv/sharpest.jpg` | `sigma_r=1.0` | 38.5 | [362, 640, 3] uint8 mean 138.07 | ok |
| `cctv/softest.jpg` | `defaults` | 37.2 | [362, 640, 3] uint8 mean 126.21 | ok |
| `cctv/softest.jpg` | `sigma_s=1.0` | 37.9 | [362, 640, 3] uint8 mean 125.24 | ok |
| `cctv/softest.jpg` | `sigma_s=200.0` | 40.5 | [362, 640, 3] uint8 mean 128.38 | ok |
| `cctv/softest.jpg` | `sigma_r=0.01` | 39.3 | [362, 640, 3] uint8 mean 125.25 | ok |
| `cctv/softest.jpg` | `sigma_r=1.0` | 36.7 | [362, 640, 3] uint8 mean 128.24 | ok |

## Artifacts

Outputs written to `validation/artifacts/detail_enhance/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
