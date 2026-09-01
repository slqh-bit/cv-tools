# nl_means - validation result

**Non-local means denoising**  
`src.filters.nl_means_denoise` | family: Enhance | 2026-09-01T16:35:03

## Verdict

**PASS** - 27 runs, no invariant broken, 6 specific checks passed.

## What this filter specifically promises

- PASS - lowers the measured noise: sigma 1.68 -> 0.94
- PASS - keeps most of the edge structure: edge density 0.0848 -> 0.0493
- PASS - h lowers noise monotonically: 1.58 -> 0.94 -> 0.51 for h 3/10/20
- PASS - nl_means: h moves the result down across its whole range: 1:47.34, 10.8:46.31, 20.6:45.04, 30.4:44.10, 40.2:43.55, 50:43.19
- PASS - nl_means: the measure still separates values in the upper half of the h range: the top half moves 0.91 of a total 4.15
- PASS - nl_means: no h on the slider flattens the image: all 6 sampled values keep image structure

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 390.6 | [362, 640, 3] uint8 mean 163.27 | ok |
| `cctv/brightest.jpg` | `h=1.0` | 383.3 | [362, 640, 3] uint8 mean 163.33 | ok |
| `cctv/brightest.jpg` | `h=50.0` | 376.8 | [362, 640, 3] uint8 mean 163.02 | ok |
| `cctv/darkest.jpg` | `defaults` | 377.5 | [362, 640, 3] uint8 mean 110.59 | ok |
| `cctv/darkest.jpg` | `h=1.0` | 387.4 | [362, 640, 3] uint8 mean 110.62 | ok |
| `cctv/darkest.jpg` | `h=50.0` | 386.9 | [362, 640, 3] uint8 mean 109.98 | ok |
| `cctv/event_fall.jpg` | `defaults` | 373.6 | [362, 640, 3] uint8 mean 124.96 | ok |
| `cctv/event_fall.jpg` | `h=1.0` | 372.7 | [362, 640, 3] uint8 mean 125.19 | ok |
| `cctv/event_fall.jpg` | `h=50.0` | 392.0 | [362, 640, 3] uint8 mean 123.08 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 377.0 | [362, 640, 3] uint8 mean 124.95 | ok |
| `cctv/event_optflow.jpg` | `h=1.0` | 376.0 | [362, 640, 3] uint8 mean 125.12 | ok |
| `cctv/event_optflow.jpg` | `h=50.0` | 382.8 | [362, 640, 3] uint8 mean 124.41 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 380.4 | [362, 640, 3] uint8 mean 160.39 | ok |
| `cctv/event_tamper.jpg` | `h=1.0` | 377.7 | [362, 640, 3] uint8 mean 160.46 | ok |
| `cctv/event_tamper.jpg` | `h=50.0` | 394.5 | [362, 640, 3] uint8 mean 160.15 | ok |
| `cctv/flattest.jpg` | `defaults` | 382.2 | [362, 640, 3] uint8 mean 121.01 | ok |
| `cctv/flattest.jpg` | `h=1.0` | 370.6 | [362, 640, 3] uint8 mean 121.2 | ok |
| `cctv/flattest.jpg` | `h=50.0` | 380.7 | [362, 640, 3] uint8 mean 120.51 | ok |
| `cctv/most_blown.jpg` | `defaults` | 380.9 | [362, 640, 3] uint8 mean 137.84 | ok |
| `cctv/most_blown.jpg` | `h=1.0` | 379.3 | [362, 640, 3] uint8 mean 137.83 | ok |
| `cctv/most_blown.jpg` | `h=50.0` | 375.4 | [362, 640, 3] uint8 mean 137.36 | ok |
| `cctv/sharpest.jpg` | `defaults` | 380.3 | [362, 640, 3] uint8 mean 131.52 | ok |
| `cctv/sharpest.jpg` | `h=1.0` | 385.1 | [362, 640, 3] uint8 mean 131.5 | ok |
| `cctv/sharpest.jpg` | `h=50.0` | 382.2 | [362, 640, 3] uint8 mean 129.5 | ok |
| `cctv/softest.jpg` | `defaults` | 376.5 | [362, 640, 3] uint8 mean 124.97 | ok |
| `cctv/softest.jpg` | `h=1.0` | 380.8 | [362, 640, 3] uint8 mean 125.12 | ok |
| `cctv/softest.jpg` | `h=50.0` | 386.1 | [362, 640, 3] uint8 mean 124.74 | ok |

## Artifacts

Outputs written to `validation/artifacts/nl_means/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
