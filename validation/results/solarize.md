# solarize - validation result

**Invert only values above a threshold**  
`cv_tools.filters.invert` | family: Adjust | 2026-09-01T16:34:55

## Verdict

**PASS** - 27 runs, no invariant broken, 3 specific checks passed.

## What this filter specifically promises

- PASS - values at or below the threshold pass through untouched: 0-128 unchanged
- PASS - values above the threshold are inverted: 129-255 become 255 minus themselves
- PASS - and the threshold actually moves the boundary: two thresholds give two different results

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `threshold=255` on `cctv/brightest.jpg`: output identical to input
- `threshold=255` on `cctv/darkest.jpg`: output identical to input
- `threshold=255` on `cctv/event_fall.jpg`: output identical to input
- `threshold=255` on `cctv/event_optflow.jpg`: output identical to input
- `threshold=255` on `cctv/event_tamper.jpg`: output identical to input
- `threshold=255` on `cctv/flattest.jpg`: output identical to input
- `threshold=255` on `cctv/most_blown.jpg`: output identical to input
- `threshold=255` on `cctv/sharpest.jpg`: output identical to input
- `threshold=255` on `cctv/softest.jpg`: output identical to input

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 0.9 | [362, 640, 3] uint8 mean 65.75 | ok |
| `cctv/brightest.jpg` | `threshold=0` | 1.1 | [362, 640, 3] uint8 mean 91.44 | ok |
| `cctv/brightest.jpg` | `threshold=255` | 0.8 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/darkest.jpg` | `defaults` | 0.9 | [362, 640, 3] uint8 mean 85.99 | ok |
| `cctv/darkest.jpg` | `threshold=0` | 0.9 | [362, 640, 3] uint8 mean 144.06 | ok |
| `cctv/darkest.jpg` | `threshold=255` | 0.9 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/event_fall.jpg` | `defaults` | 0.9 | [362, 640, 3] uint8 mean 80.52 | ok |
| `cctv/event_fall.jpg` | `threshold=0` | 0.9 | [362, 640, 3] uint8 mean 127.39 | ok |
| `cctv/event_fall.jpg` | `threshold=255` | 0.8 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_optflow.jpg` | `defaults` | 0.9 | [362, 640, 3] uint8 mean 89.4 | ok |
| `cctv/event_optflow.jpg` | `threshold=0` | 0.9 | [362, 640, 3] uint8 mean 129.5 | ok |
| `cctv/event_optflow.jpg` | `threshold=255` | 0.8 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_tamper.jpg` | `defaults` | 0.9 | [362, 640, 3] uint8 mean 67.12 | ok |
| `cctv/event_tamper.jpg` | `threshold=0` | 0.9 | [362, 640, 3] uint8 mean 94.35 | ok |
| `cctv/event_tamper.jpg` | `threshold=255` | 0.8 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/flattest.jpg` | `defaults` | 0.9 | [362, 640, 3] uint8 mean 90.63 | ok |
| `cctv/flattest.jpg` | `threshold=0` | 0.9 | [362, 640, 3] uint8 mean 133.43 | ok |
| `cctv/flattest.jpg` | `threshold=255` | 0.8 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/most_blown.jpg` | `defaults` | 0.9 | [362, 640, 3] uint8 mean 81.54 | ok |
| `cctv/most_blown.jpg` | `threshold=0` | 1.2 | [362, 640, 3] uint8 mean 116.9 | ok |
| `cctv/most_blown.jpg` | `threshold=255` | 0.8 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/sharpest.jpg` | `defaults` | 0.9 | [362, 640, 3] uint8 mean 81.19 | ok |
| `cctv/sharpest.jpg` | `threshold=0` | 0.9 | [362, 640, 3] uint8 mean 121.36 | ok |
| `cctv/sharpest.jpg` | `threshold=255` | 0.9 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/softest.jpg` | `defaults` | 0.9 | [362, 640, 3] uint8 mean 84.72 | ok |
| `cctv/softest.jpg` | `threshold=0` | 0.9 | [362, 640, 3] uint8 mean 129.58 | ok |
| `cctv/softest.jpg` | `threshold=255` | 1.0 | [362, 640, 3] uint8 mean 125.38 | output identical to input |

## Artifacts

Outputs written to `validation/artifacts/solarize/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
