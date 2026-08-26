# barrel - validation result

**Polynomial radial distortion correction**  
`src.filters.fisheye_correction` | family: Correct | 2026-08-21T12:45:36

## Verdict

**PASS** - 90 runs, no invariant broken, 1 specific checks passed.

## What this filter specifically promises

- PASS - the inverse of a known k1 straightens the grid: straightness 20.550 -> 21.520 (grid was distorted at k1=-0.28)

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 13.7 | [362, 640, 3] uint8 mean 164.54 | ok |
| `cctv/brightest.jpg` | `k1=-1.0` | 13.0 | [362, 640, 3] uint8 mean 139.51 | ok |
| `cctv/brightest.jpg` | `k1=1.0` | 12.3 | [362, 640, 3] uint8 mean 85.12 | ok |
| `cctv/brightest.jpg` | `k2=-1.0` | 15.3 | [362, 640, 3] uint8 mean 146.02 | ok |
| `cctv/brightest.jpg` | `k2=1.0` | 13.1 | [362, 640, 3] uint8 mean 118.54 | ok |
| `cctv/brightest.jpg` | `zoom=0.5` | 12.0 | [362, 640, 3] uint8 mean 44.46 | ok |
| `cctv/brightest.jpg` | `zoom=3.0` | 13.1 | [362, 640, 3] uint8 mean 112.25 | ok |
| `cctv/brightest.jpg` | `border_mode=replicate` | 12.8 | [362, 640, 3] uint8 mean 164.54 | ok |
| `cctv/brightest.jpg` | `border_mode=reflect` | 13.3 | [362, 640, 3] uint8 mean 164.54 | ok |
| `cctv/darkest.jpg` | `defaults` | 13.6 | [362, 640, 3] uint8 mean 109.63 | ok |
| `cctv/darkest.jpg` | `k1=-1.0` | 13.0 | [362, 640, 3] uint8 mean 99.65 | ok |
| `cctv/darkest.jpg` | `k1=1.0` | 12.2 | [362, 640, 3] uint8 mean 60.41 | ok |
| `cctv/darkest.jpg` | `k2=-1.0` | 13.0 | [362, 640, 3] uint8 mean 109.91 | ok |
| `cctv/darkest.jpg` | `k2=1.0` | 13.0 | [362, 640, 3] uint8 mean 83.58 | ok |
| `cctv/darkest.jpg` | `zoom=0.5` | 12.3 | [362, 640, 3] uint8 mean 29.98 | ok |
| `cctv/darkest.jpg` | `zoom=3.0` | 13.5 | [362, 640, 3] uint8 mean 98.02 | ok |
| `cctv/darkest.jpg` | `border_mode=replicate` | 13.2 | [362, 640, 3] uint8 mean 109.63 | ok |
| `cctv/darkest.jpg` | `border_mode=reflect` | 13.3 | [362, 640, 3] uint8 mean 109.63 | ok |
| `cctv/event_fall.jpg` | `defaults` | 13.2 | [362, 640, 3] uint8 mean 129.1 | ok |
| `cctv/event_fall.jpg` | `k1=-1.0` | 13.0 | [362, 640, 3] uint8 mean 122.56 | ok |
| `cctv/event_fall.jpg` | `k1=1.0` | 12.2 | [362, 640, 3] uint8 mean 68.98 | ok |
| `cctv/event_fall.jpg` | `k2=-1.0` | 13.2 | [362, 640, 3] uint8 mean 122.44 | ok |
| `cctv/event_fall.jpg` | `k2=1.0` | 12.7 | [362, 640, 3] uint8 mean 96.04 | ok |
| `cctv/event_fall.jpg` | `zoom=0.5` | 12.1 | [362, 640, 3] uint8 mean 33.83 | ok |
| `cctv/event_fall.jpg` | `zoom=3.0` | 13.5 | [362, 640, 3] uint8 mean 110.67 | ok |
| `cctv/event_fall.jpg` | `border_mode=replicate` | 13.2 | [362, 640, 3] uint8 mean 129.1 | ok |
| `cctv/event_fall.jpg` | `border_mode=reflect` | 16.8 | [362, 640, 3] uint8 mean 129.1 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 13.3 | [362, 640, 3] uint8 mean 128.27 | ok |
| `cctv/event_optflow.jpg` | `k1=-1.0` | 14.8 | [362, 640, 3] uint8 mean 119.52 | ok |
| `cctv/event_optflow.jpg` | `k1=1.0` | 12.1 | [362, 640, 3] uint8 mean 68.17 | ok |
| `cctv/event_optflow.jpg` | `k2=-1.0` | 13.6 | [362, 640, 3] uint8 mean 122.36 | ok |
| `cctv/event_optflow.jpg` | `k2=1.0` | 12.9 | [362, 640, 3] uint8 mean 95.14 | ok |
| `cctv/event_optflow.jpg` | `zoom=0.5` | 12.1 | [362, 640, 3] uint8 mean 33.85 | ok |
| `cctv/event_optflow.jpg` | `zoom=3.0` | 13.6 | [362, 640, 3] uint8 mean 100.3 | ok |
| `cctv/event_optflow.jpg` | `border_mode=replicate` | 13.1 | [362, 640, 3] uint8 mean 128.27 | ok |
| `cctv/event_optflow.jpg` | `border_mode=reflect` | 13.1 | [362, 640, 3] uint8 mean 128.27 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 16.9 | [362, 640, 3] uint8 mean 161.64 | ok |
| `cctv/event_tamper.jpg` | `k1=-1.0` | 13.2 | [362, 640, 3] uint8 mean 136.71 | ok |
| `cctv/event_tamper.jpg` | `k1=1.0` | 13.3 | [362, 640, 3] uint8 mean 83.53 | ok |
| `cctv/event_tamper.jpg` | `k2=-1.0` | 13.8 | [362, 640, 3] uint8 mean 143.1 | ok |
| `cctv/event_tamper.jpg` | `k2=1.0` | 14.3 | [362, 640, 3] uint8 mean 116.36 | ok |
| `cctv/event_tamper.jpg` | `zoom=0.5` | 11.7 | [362, 640, 3] uint8 mean 43.68 | ok |
| `cctv/event_tamper.jpg` | `zoom=3.0` | 14.0 | [362, 640, 3] uint8 mean 108.69 | ok |
| `cctv/event_tamper.jpg` | `border_mode=replicate` | 15.0 | [362, 640, 3] uint8 mean 161.64 | ok |
| `cctv/event_tamper.jpg` | `border_mode=reflect` | 13.6 | [362, 640, 3] uint8 mean 161.64 | ok |
| `cctv/flattest.jpg` | `defaults` | 12.8 | [362, 640, 3] uint8 mean 124.5 | ok |
| `cctv/flattest.jpg` | `k1=-1.0` | 13.5 | [362, 640, 3] uint8 mean 115.39 | ok |
| `cctv/flattest.jpg` | `k1=1.0` | 13.5 | [362, 640, 3] uint8 mean 66.06 | ok |
| `cctv/flattest.jpg` | `k2=-1.0` | 13.6 | [362, 640, 3] uint8 mean 118.58 | ok |
| `cctv/flattest.jpg` | `k2=1.0` | 12.7 | [362, 640, 3] uint8 mean 92.23 | ok |
| `cctv/flattest.jpg` | `zoom=0.5` | 14.3 | [362, 640, 3] uint8 mean 32.79 | ok |
| `cctv/flattest.jpg` | `zoom=3.0` | 13.4 | [362, 640, 3] uint8 mean 97.0 | ok |
| `cctv/flattest.jpg` | `border_mode=replicate` | 13.9 | [362, 640, 3] uint8 mean 124.5 | ok |
| `cctv/flattest.jpg` | `border_mode=reflect` | 13.2 | [362, 640, 3] uint8 mean 124.5 | ok |
| `cctv/most_blown.jpg` | `defaults` | 13.3 | [362, 640, 3] uint8 mean 137.38 | ok |
| `cctv/most_blown.jpg` | `k1=-1.0` | 13.2 | [362, 640, 3] uint8 mean 123.76 | ok |
| `cctv/most_blown.jpg` | `k1=1.0` | 14.1 | [362, 640, 3] uint8 mean 75.26 | ok |
| `cctv/most_blown.jpg` | `k2=-1.0` | 12.9 | [362, 640, 3] uint8 mean 137.26 | ok |
| `cctv/most_blown.jpg` | `k2=1.0` | 13.3 | [362, 640, 3] uint8 mean 104.27 | ok |
| `cctv/most_blown.jpg` | `zoom=0.5` | 12.0 | [362, 640, 3] uint8 mean 37.3 | ok |
| `cctv/most_blown.jpg` | `zoom=3.0` | 14.0 | [362, 640, 3] uint8 mean 119.92 | ok |
| `cctv/most_blown.jpg` | `border_mode=replicate` | 14.3 | [362, 640, 3] uint8 mean 137.38 | ok |
| `cctv/most_blown.jpg` | `border_mode=reflect` | 13.3 | [362, 640, 3] uint8 mean 137.38 | ok |
| `cctv/sharpest.jpg` | `defaults` | 14.1 | [362, 640, 3] uint8 mean 130.44 | ok |
| `cctv/sharpest.jpg` | `k1=-1.0` | 14.7 | [362, 640, 3] uint8 mean 118.4 | ok |
| `cctv/sharpest.jpg` | `k1=1.0` | 15.0 | [362, 640, 3] uint8 mean 71.89 | ok |
| `cctv/sharpest.jpg` | `k2=-1.0` | 17.5 | [362, 640, 3] uint8 mean 131.01 | ok |
| `cctv/sharpest.jpg` | `k2=1.0` | 15.9 | [362, 640, 3] uint8 mean 99.59 | ok |
| `cctv/sharpest.jpg` | `zoom=0.5` | 12.1 | [362, 640, 3] uint8 mean 35.61 | ok |
| `cctv/sharpest.jpg` | `zoom=3.0` | 13.8 | [362, 640, 3] uint8 mean 113.45 | ok |
| `cctv/sharpest.jpg` | `border_mode=replicate` | 13.4 | [362, 640, 3] uint8 mean 130.44 | ok |
| `cctv/sharpest.jpg` | `border_mode=reflect` | 13.5 | [362, 640, 3] uint8 mean 130.44 | ok |
| `cctv/softest.jpg` | `defaults` | 13.4 | [362, 640, 3] uint8 mean 125.73 | ok |
| `cctv/softest.jpg` | `k1=-1.0` | 13.8 | [362, 640, 3] uint8 mean 107.26 | ok |
| `cctv/softest.jpg` | `k1=1.0` | 12.2 | [362, 640, 3] uint8 mean 65.49 | ok |
| `cctv/softest.jpg` | `k2=-1.0` | 13.4 | [362, 640, 3] uint8 mean 111.64 | ok |
| `cctv/softest.jpg` | `k2=1.0` | 13.1 | [362, 640, 3] uint8 mean 90.95 | ok |
| `cctv/softest.jpg` | `zoom=0.5` | 11.7 | [362, 640, 3] uint8 mean 34.1 | ok |
| `cctv/softest.jpg` | `zoom=3.0` | 13.2 | [362, 640, 3] uint8 mean 92.11 | ok |
| `cctv/softest.jpg` | `border_mode=replicate` | 13.3 | [362, 640, 3] uint8 mean 125.73 | ok |
| `cctv/softest.jpg` | `border_mode=reflect` | 13.5 | [362, 640, 3] uint8 mean 125.73 | ok |
| `ground_truth/grid_barrel.png` | `defaults` | 17.4 | [480, 640, 3] uint8 mean 233.81 | ok |
| `ground_truth/grid_barrel.png` | `k1=-1.0` | 17.7 | [480, 640, 3] uint8 mean 233.72 | ok |
| `ground_truth/grid_barrel.png` | `k1=1.0` | 15.9 | [480, 640, 3] uint8 mean 128.26 | ok |
| `ground_truth/grid_barrel.png` | `k2=-1.0` | 17.3 | [480, 640, 3] uint8 mean 233.12 | ok |
| `ground_truth/grid_barrel.png` | `k2=1.0` | 17.0 | [480, 640, 3] uint8 mean 178.19 | ok |
| `ground_truth/grid_barrel.png` | `zoom=0.5` | 15.5 | [480, 640, 3] uint8 mean 62.85 | ok |
| `ground_truth/grid_barrel.png` | `zoom=3.0` | 17.1 | [480, 640, 3] uint8 mean 233.13 | ok |
| `ground_truth/grid_barrel.png` | `border_mode=replicate` | 21.3 | [480, 640, 3] uint8 mean 233.81 | ok |
| `ground_truth/grid_barrel.png` | `border_mode=reflect` | 17.1 | [480, 640, 3] uint8 mean 233.81 | ok |

## Artifacts

Outputs written to `validation/artifacts/barrel/`:

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
