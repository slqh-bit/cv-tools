# rotate - validation result

**Rotate by an arbitrary angle**  
`src.filters.crop_resize` | family: Adjust | 2026-08-21T12:44:37

## Verdict

**PASS** - 45 runs, no invariant broken, 5 specific checks passed.

## What this filter specifically promises

- PASS - a quarter turn swaps the dimensions, losing no content: 640x362 became 362x640
- PASS - an oblique angle grows the canvas to fit the corners: 45 degrees gave 708x708 from 640x362
- PASS - a full turn returns the image, to interpolation error: mean absolute difference 0.000/255
- PASS - a quarter turn is not the original: the 90 degree result differs from the input
- PASS - four quarter turns come back to the start: mean absolute difference 0.01/255 after four turns (interpolation and corner loss accumulate)

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `angle=15.0` | 0.7 | [515, 711, 3] uint8 mean 103.48 | ok |
| `cctv/brightest.jpg` | `angle=15.0, scale=0.1` | 0.8 | [515, 711, 3] uint8 mean 1.04 | ok |
| `cctv/brightest.jpg` | `angle=15.0, scale=8.0` | 1.0 | [515, 711, 3] uint8 mean 94.87 | ok |
| `cctv/brightest.jpg` | `angle=15.0, border_mode=replicate` | 1.1 | [515, 711, 3] uint8 mean 143.09 | ok |
| `cctv/brightest.jpg` | `angle=15.0, border_mode=reflect` | 1.4 | [515, 711, 3] uint8 mean 165.38 | ok |
| `cctv/darkest.jpg` | `angle=15.0` | 0.9 | [515, 711, 3] uint8 mean 70.19 | ok |
| `cctv/darkest.jpg` | `angle=15.0, scale=0.1` | 0.8 | [515, 711, 3] uint8 mean 0.7 | ok |
| `cctv/darkest.jpg` | `angle=15.0, scale=8.0` | 1.0 | [515, 711, 3] uint8 mean 99.94 | ok |
| `cctv/darkest.jpg` | `angle=15.0, border_mode=replicate` | 1.3 | [515, 711, 3] uint8 mean 95.31 | ok |
| `cctv/darkest.jpg` | `angle=15.0, border_mode=reflect` | 1.4 | [515, 711, 3] uint8 mean 111.03 | ok |
| `cctv/event_fall.jpg` | `angle=15.0` | 1.1 | [515, 711, 3] uint8 mean 79.42 | ok |
| `cctv/event_fall.jpg` | `angle=15.0, scale=0.1` | 0.9 | [515, 711, 3] uint8 mean 0.79 | ok |
| `cctv/event_fall.jpg` | `angle=15.0, scale=8.0` | 1.1 | [515, 711, 3] uint8 mean 93.28 | ok |
| `cctv/event_fall.jpg` | `angle=15.0, border_mode=replicate` | 1.5 | [515, 711, 3] uint8 mean 104.83 | ok |
| `cctv/event_fall.jpg` | `angle=15.0, border_mode=reflect` | 2.0 | [515, 711, 3] uint8 mean 125.37 | ok |
| `cctv/event_optflow.jpg` | `angle=15.0` | 1.1 | [515, 711, 3] uint8 mean 79.36 | ok |
| `cctv/event_optflow.jpg` | `angle=15.0, scale=0.1` | 0.8 | [515, 711, 3] uint8 mean 0.79 | ok |
| `cctv/event_optflow.jpg` | `angle=15.0, scale=8.0` | 1.1 | [515, 711, 3] uint8 mean 84.13 | ok |
| `cctv/event_optflow.jpg` | `angle=15.0, border_mode=replicate` | 1.4 | [515, 711, 3] uint8 mean 110.83 | ok |
| `cctv/event_optflow.jpg` | `angle=15.0, border_mode=reflect` | 2.3 | [515, 711, 3] uint8 mean 125.87 | ok |
| `cctv/event_tamper.jpg` | `angle=15.0` | 1.0 | [515, 711, 3] uint8 mean 101.64 | ok |
| `cctv/event_tamper.jpg` | `angle=15.0, scale=0.1` | 0.8 | [515, 711, 3] uint8 mean 1.02 | ok |
| `cctv/event_tamper.jpg` | `angle=15.0, scale=8.0` | 1.0 | [515, 711, 3] uint8 mean 91.79 | ok |
| `cctv/event_tamper.jpg` | `angle=15.0, border_mode=replicate` | 1.5 | [515, 711, 3] uint8 mean 140.61 | ok |
| `cctv/event_tamper.jpg` | `angle=15.0, border_mode=reflect` | 2.2 | [515, 711, 3] uint8 mean 162.49 | ok |
| `cctv/flattest.jpg` | `angle=15.0` | 1.1 | [515, 711, 3] uint8 mean 76.88 | ok |
| `cctv/flattest.jpg` | `angle=15.0, scale=0.1` | 0.8 | [515, 711, 3] uint8 mean 0.77 | ok |
| `cctv/flattest.jpg` | `angle=15.0, scale=8.0` | 0.9 | [515, 711, 3] uint8 mean 81.33 | ok |
| `cctv/flattest.jpg` | `angle=15.0, border_mode=replicate` | 1.1 | [515, 711, 3] uint8 mean 107.35 | ok |
| `cctv/flattest.jpg` | `angle=15.0, border_mode=reflect` | 1.9 | [515, 711, 3] uint8 mean 121.89 | ok |
| `cctv/most_blown.jpg` | `angle=15.0` | 0.9 | [515, 711, 3] uint8 mean 87.37 | ok |
| `cctv/most_blown.jpg` | `angle=15.0, scale=0.1` | 0.7 | [515, 711, 3] uint8 mean 0.88 | ok |
| `cctv/most_blown.jpg` | `angle=15.0, scale=8.0` | 1.0 | [515, 711, 3] uint8 mean 122.98 | ok |
| `cctv/most_blown.jpg` | `angle=15.0, border_mode=replicate` | 1.3 | [515, 711, 3] uint8 mean 119.58 | ok |
| `cctv/most_blown.jpg` | `angle=15.0, border_mode=reflect` | 2.2 | [515, 711, 3] uint8 mean 137.92 | ok |
| `cctv/sharpest.jpg` | `angle=15.0` | 0.9 | [515, 711, 3] uint8 mean 83.37 | ok |
| `cctv/sharpest.jpg` | `angle=15.0, scale=0.1` | 0.8 | [515, 711, 3] uint8 mean 0.84 | ok |
| `cctv/sharpest.jpg` | `angle=15.0, scale=8.0` | 1.1 | [515, 711, 3] uint8 mean 118.74 | ok |
| `cctv/sharpest.jpg` | `angle=15.0, border_mode=replicate` | 1.5 | [515, 711, 3] uint8 mean 111.91 | ok |
| `cctv/sharpest.jpg` | `angle=15.0, border_mode=reflect` | 1.9 | [515, 711, 3] uint8 mean 132.03 | ok |
| `cctv/softest.jpg` | `angle=15.0` | 1.3 | [515, 711, 3] uint8 mean 79.34 | ok |
| `cctv/softest.jpg` | `angle=15.0, scale=0.1` | 0.8 | [515, 711, 3] uint8 mean 0.79 | ok |
| `cctv/softest.jpg` | `angle=15.0, scale=8.0` | 1.1 | [515, 711, 3] uint8 mean 81.34 | ok |
| `cctv/softest.jpg` | `angle=15.0, border_mode=replicate` | 1.3 | [515, 711, 3] uint8 mean 109.68 | ok |
| `cctv/softest.jpg` | `angle=15.0, border_mode=reflect` | 2.0 | [515, 711, 3] uint8 mean 126.97 | ok |

## Artifacts

Outputs written to `validation/artifacts/rotate/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
