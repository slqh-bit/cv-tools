# sharpen - validation result

**Unsharp mask sharpening**  
`src.filters.sharpen` | family: Enhance | 2026-09-01T16:34:55

## Verdict

**PASS** - 63 runs, no invariant broken, 11 specific checks passed.

## What this filter specifically promises

- PASS - raises high-frequency energy on the softest frame: Laplacian variance 667 -> 1922
- PASS - amount raises it monotonically: 1277 -> 1922 -> 3340 for amount 0.5/1/2
- PASS - heavy sharpening does not clip most of the frame: 1.8% of pixels driven to 0 or 255 at amount 2.5
- PASS - sharpen does not move content: the marker centred at (163.5, 163.5) reads centred at (163.5, 163.5)
- PASS - sharpen keeps the red block red: channel 0 dominates, expected 0
- PASS - sharpen keeps the green block green: channel 1 dominates, expected 1
- PASS - sharpen keeps the blue block blue: channel 2 dominates, expected 2
- PASS - sharpen reaches both halves of the frame: mean change 7.13 left against 7.15 right
- PASS - sharpen: amount moves the result up across its whole range: 0:887.83, 0.6:1927.74, 1.2:3083.08, 1.8:4282.29, 2.4:5534.21, 3:6790.18
- PASS - sharpen: the measure still separates values in the upper half of the amount range: the top half moves 2507.89 of a total 5902.35
- PASS - sharpen: no amount on the slider flattens the image: all 6 sampled values keep image structure

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `amount=0.0` on `cctv/brightest.jpg`: output identical to input
- `radius=0.1` on `cctv/brightest.jpg`: output identical to input
- `threshold=255` on `cctv/brightest.jpg`: output identical to input
- `amount=0.0` on `cctv/darkest.jpg`: output identical to input
- `radius=0.1` on `cctv/darkest.jpg`: output identical to input
- `threshold=255` on `cctv/darkest.jpg`: output identical to input
- `amount=0.0` on `cctv/event_fall.jpg`: output identical to input
- `radius=0.1` on `cctv/event_fall.jpg`: output identical to input
- `threshold=255` on `cctv/event_fall.jpg`: output identical to input
- `amount=0.0` on `cctv/event_optflow.jpg`: output identical to input
- `radius=0.1` on `cctv/event_optflow.jpg`: output identical to input
- `threshold=255` on `cctv/event_optflow.jpg`: output identical to input

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 5.4 | [362, 640, 3] uint8 mean 163.43 | ok |
| `cctv/brightest.jpg` | `amount=0.0` | 6.6 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/brightest.jpg` | `amount=3.0` | 5.9 | [362, 640, 3] uint8 mean 163.33 | ok |
| `cctv/brightest.jpg` | `radius=0.1` | 5.8 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/brightest.jpg` | `radius=50.0` | 225.4 | [362, 640, 3] uint8 mean 160.99 | ok |
| `cctv/brightest.jpg` | `threshold=0` | 5.2 | [362, 640, 3] uint8 mean 163.43 | ok |
| `cctv/brightest.jpg` | `threshold=255` | 7.5 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/darkest.jpg` | `defaults` | 6.5 | [362, 640, 3] uint8 mean 110.77 | ok |
| `cctv/darkest.jpg` | `amount=0.0` | 6.0 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/darkest.jpg` | `amount=3.0` | 6.3 | [362, 640, 3] uint8 mean 110.87 | ok |
| `cctv/darkest.jpg` | `radius=0.1` | 5.9 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/darkest.jpg` | `radius=50.0` | 252.7 | [362, 640, 3] uint8 mean 107.85 | ok |
| `cctv/darkest.jpg` | `threshold=0` | 5.2 | [362, 640, 3] uint8 mean 110.77 | ok |
| `cctv/darkest.jpg` | `threshold=255` | 6.9 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/event_fall.jpg` | `defaults` | 5.5 | [362, 640, 3] uint8 mean 125.69 | ok |
| `cctv/event_fall.jpg` | `amount=0.0` | 5.3 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_fall.jpg` | `amount=3.0` | 6.0 | [362, 640, 3] uint8 mean 126.2 | ok |
| `cctv/event_fall.jpg` | `radius=0.1` | 5.8 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_fall.jpg` | `radius=50.0` | 247.3 | [362, 640, 3] uint8 mean 125.26 | ok |
| `cctv/event_fall.jpg` | `threshold=0` | 5.4 | [362, 640, 3] uint8 mean 125.69 | ok |
| `cctv/event_fall.jpg` | `threshold=255` | 6.8 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_optflow.jpg` | `defaults` | 5.4 | [362, 640, 3] uint8 mean 125.34 | ok |
| `cctv/event_optflow.jpg` | `amount=0.0` | 5.9 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_optflow.jpg` | `amount=3.0` | 6.9 | [362, 640, 3] uint8 mean 125.58 | ok |
| `cctv/event_optflow.jpg` | `radius=0.1` | 5.2 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_optflow.jpg` | `radius=50.0` | 230.7 | [362, 640, 3] uint8 mean 124.34 | ok |
| `cctv/event_optflow.jpg` | `threshold=0` | 5.2 | [362, 640, 3] uint8 mean 125.34 | ok |
| `cctv/event_optflow.jpg` | `threshold=255` | 7.3 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_tamper.jpg` | `defaults` | 5.5 | [362, 640, 3] uint8 mean 160.53 | ok |
| `cctv/event_tamper.jpg` | `amount=0.0` | 6.0 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/event_tamper.jpg` | `amount=3.0` | 5.1 | [362, 640, 3] uint8 mean 160.45 | ok |
| `cctv/event_tamper.jpg` | `radius=0.1` | 5.1 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/event_tamper.jpg` | `radius=50.0` | 244.2 | [362, 640, 3] uint8 mean 158.29 | ok |
| `cctv/event_tamper.jpg` | `threshold=0` | 5.4 | [362, 640, 3] uint8 mean 160.53 | ok |
| `cctv/event_tamper.jpg` | `threshold=255` | 7.6 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/flattest.jpg` | `defaults` | 9.4 | [362, 640, 3] uint8 mean 121.43 | ok |
| `cctv/flattest.jpg` | `amount=0.0` | 5.6 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/flattest.jpg` | `amount=3.0` | 5.2 | [362, 640, 3] uint8 mean 121.64 | ok |
| `cctv/flattest.jpg` | `radius=0.1` | 5.3 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/flattest.jpg` | `radius=50.0` | 256.7 | [362, 640, 3] uint8 mean 120.48 | ok |
| `cctv/flattest.jpg` | `threshold=0` | 5.5 | [362, 640, 3] uint8 mean 121.43 | ok |
| `cctv/flattest.jpg` | `threshold=255` | 8.0 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/most_blown.jpg` | `defaults` | 6.6 | [362, 640, 3] uint8 mean 137.96 | ok |
| `cctv/most_blown.jpg` | `amount=0.0` | 5.4 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/most_blown.jpg` | `amount=3.0` | 5.6 | [362, 640, 3] uint8 mean 138.11 | ok |
| `cctv/most_blown.jpg` | `radius=0.1` | 6.3 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/most_blown.jpg` | `radius=50.0` | 229.9 | [362, 640, 3] uint8 mean 134.81 | ok |
| `cctv/most_blown.jpg` | `threshold=0` | 5.2 | [362, 640, 3] uint8 mean 137.96 | ok |
| `cctv/most_blown.jpg` | `threshold=255` | 8.1 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/sharpest.jpg` | `defaults` | 5.4 | [362, 640, 3] uint8 mean 132.18 | ok |
| `cctv/sharpest.jpg` | `amount=0.0` | 5.4 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/sharpest.jpg` | `amount=3.0` | 5.3 | [362, 640, 3] uint8 mean 132.98 | ok |
| `cctv/sharpest.jpg` | `radius=0.1` | 9.3 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/sharpest.jpg` | `radius=50.0` | 225.4 | [362, 640, 3] uint8 mean 131.3 | ok |
| `cctv/sharpest.jpg` | `threshold=0` | 8.2 | [362, 640, 3] uint8 mean 132.18 | ok |
| `cctv/sharpest.jpg` | `threshold=255` | 7.8 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/softest.jpg` | `defaults` | 5.4 | [362, 640, 3] uint8 mean 125.43 | ok |
| `cctv/softest.jpg` | `amount=0.0` | 5.9 | [362, 640, 3] uint8 mean 125.38 | output identical to input |
| `cctv/softest.jpg` | `amount=3.0` | 5.5 | [362, 640, 3] uint8 mean 125.78 | ok |
| `cctv/softest.jpg` | `radius=0.1` | 6.6 | [362, 640, 3] uint8 mean 125.38 | output identical to input |
| `cctv/softest.jpg` | `radius=50.0` | 278.2 | [362, 640, 3] uint8 mean 125.52 | ok |
| `cctv/softest.jpg` | `threshold=0` | 7.8 | [362, 640, 3] uint8 mean 125.43 | ok |
| `cctv/softest.jpg` | `threshold=255` | 10.1 | [362, 640, 3] uint8 mean 125.38 | output identical to input |

## Artifacts

Outputs written to `validation/artifacts/sharpen/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
