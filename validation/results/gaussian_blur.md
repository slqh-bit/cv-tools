# gaussian_blur - validation result

**Gaussian smoothing**  
`src.filters.smoothing` | family: Enhance | 2026-09-01T16:34:59

## Verdict

**PASS** - 27 runs, no invariant broken, 8 specific checks passed.

## What this filter specifically promises

- PASS - gaussian_blur does not move content: the marker centred at (163.5, 163.5) reads centred at (163.5, 163.5)
- PASS - gaussian_blur keeps the red block red: channel 0 dominates, expected 0
- PASS - gaussian_blur keeps the green block green: channel 1 dominates, expected 1
- PASS - gaussian_blur keeps the blue block blue: channel 2 dominates, expected 2
- PASS - gaussian_blur reaches both halves of the frame: mean change 8.33 left against 8.49 right
- PASS - gaussian_blur: radius moves the result down across its whole range: 0.1:47.30, 10.08:39.69, 20.06:34.20, 30.04:29.24, 40.02:25.02, 50:21.58
- PASS - gaussian_blur: the measure still separates values in the upper half of the radius range: the top half moves 7.65 of a total 25.72
- PASS - gaussian_blur: no radius on the slider flattens the image: all 6 sampled values keep image structure

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `radius=0.1` on `cctv/brightest.jpg`: output identical to input
- `radius=0.1` on `cctv/darkest.jpg`: output identical to input
- `radius=0.1` on `cctv/event_fall.jpg`: output identical to input
- `radius=0.1` on `cctv/event_optflow.jpg`: output identical to input
- `radius=0.1` on `cctv/event_tamper.jpg`: output identical to input
- `radius=0.1` on `cctv/flattest.jpg`: output identical to input
- `radius=0.1` on `cctv/most_blown.jpg`: output identical to input
- `radius=0.1` on `cctv/sharpest.jpg`: output identical to input
- `radius=0.1` on `cctv/softest.jpg`: output identical to input

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 0.6 | [362, 640, 3] uint8 mean 163.73 | ok |
| `cctv/brightest.jpg` | `radius=0.1` | 0.2 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/brightest.jpg` | `radius=50.0` | 254.9 | [362, 640, 3] uint8 mean 163.84 | ok |
| `cctv/darkest.jpg` | `defaults` | 0.3 | [362, 640, 3] uint8 mean 111.08 | ok |
| `cctv/darkest.jpg` | `radius=0.1` | 0.2 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/darkest.jpg` | `radius=50.0` | 239.8 | [362, 640, 3] uint8 mean 111.12 | ok |
| `cctv/event_fall.jpg` | `defaults` | 0.5 | [362, 640, 3] uint8 mean 125.74 | ok |
| `cctv/event_fall.jpg` | `radius=0.1` | 0.2 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_fall.jpg` | `radius=50.0` | 224.6 | [362, 640, 3] uint8 mean 125.78 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 0.3 | [362, 640, 3] uint8 mean 125.59 | ok |
| `cctv/event_optflow.jpg` | `radius=0.1` | 0.1 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_optflow.jpg` | `radius=50.0` | 239.9 | [362, 640, 3] uint8 mean 125.63 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 0.7 | [362, 640, 3] uint8 mean 160.81 | ok |
| `cctv/event_tamper.jpg` | `radius=0.1` | 0.2 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/event_tamper.jpg` | `radius=50.0` | 231.0 | [362, 640, 3] uint8 mean 160.92 | ok |
| `cctv/flattest.jpg` | `defaults` | 0.6 | [362, 640, 3] uint8 mean 121.66 | ok |
| `cctv/flattest.jpg` | `radius=0.1` | 0.1 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/flattest.jpg` | `radius=50.0` | 273.5 | [362, 640, 3] uint8 mean 121.7 | ok |
| `cctv/most_blown.jpg` | `defaults` | 0.6 | [362, 640, 3] uint8 mean 138.27 | ok |
| `cctv/most_blown.jpg` | `radius=0.1` | 0.2 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/most_blown.jpg` | `radius=50.0` | 240.4 | [362, 640, 3] uint8 mean 138.31 | ok |
| `cctv/sharpest.jpg` | `defaults` | 0.3 | [362, 640, 3] uint8 mean 131.94 | ok |
| `cctv/sharpest.jpg` | `radius=0.1` | 0.2 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/sharpest.jpg` | `radius=50.0` | 238.7 | [362, 640, 3] uint8 mean 131.99 | ok |
| `cctv/softest.jpg` | `defaults` | 0.6 | [362, 640, 3] uint8 mean 125.53 | ok |
| `cctv/softest.jpg` | `radius=0.1` | 0.2 | [362, 640, 3] uint8 mean 125.38 | output identical to input |
| `cctv/softest.jpg` | `radius=50.0` | 249.9 | [362, 640, 3] uint8 mean 125.62 | ok |

## Artifacts

Outputs written to `validation/artifacts/gaussian_blur/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
