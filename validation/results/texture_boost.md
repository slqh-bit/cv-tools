# texture_boost - validation result

**Texture contrast with edge protection**  
`src.filters.detail_enhancement` | family: Enhance | 2026-09-01T16:35:50

## Verdict

**PASS** - 36 runs, no invariant broken, 3 specific checks passed.

## What this filter specifically promises

- PASS - texture_boost: amount moves the result up across its whole range: 0:887.83, 0.6:1483.95, 1.2:2065.92, 1.8:2730.33, 2.4:3463.17, 3:4228.78
- PASS - texture_boost: the measure still separates values in the upper half of the amount range: the top half moves 1498.45 of a total 3340.95
- PASS - texture_boost: no amount on the slider flattens the image: all 6 sampled values keep image structure

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `amount=0.0` on `cctv/brightest.jpg`: output identical to input
- `amount=0.0` on `cctv/darkest.jpg`: output identical to input
- `amount=0.0` on `cctv/event_fall.jpg`: output identical to input
- `amount=0.0` on `cctv/event_optflow.jpg`: output identical to input
- `amount=0.0` on `cctv/event_tamper.jpg`: output identical to input
- `amount=0.0` on `cctv/flattest.jpg`: output identical to input
- `amount=0.0` on `cctv/most_blown.jpg`: output identical to input
- `amount=0.0` on `cctv/sharpest.jpg`: output identical to input
- `amount=0.0` on `cctv/softest.jpg`: output identical to input

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 11.5 | [362, 640, 3] uint8 mean 162.98 | ok |
| `cctv/brightest.jpg` | `amount=0.0` | 11.7 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/brightest.jpg` | `amount=3.0` | 11.3 | [362, 640, 3] uint8 mean 162.84 | ok |
| `cctv/brightest.jpg` | `protect_edges=False` | 7.0 | [362, 640, 3] uint8 mean 162.95 | ok |
| `cctv/darkest.jpg` | `defaults` | 11.0 | [362, 640, 3] uint8 mean 110.28 | ok |
| `cctv/darkest.jpg` | `amount=0.0` | 11.5 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/darkest.jpg` | `amount=3.0` | 11.5 | [362, 640, 3] uint8 mean 110.27 | ok |
| `cctv/darkest.jpg` | `protect_edges=False` | 7.3 | [362, 640, 3] uint8 mean 110.18 | ok |
| `cctv/event_fall.jpg` | `defaults` | 11.1 | [362, 640, 3] uint8 mean 125.22 | ok |
| `cctv/event_fall.jpg` | `amount=0.0` | 11.2 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_fall.jpg` | `amount=3.0` | 11.5 | [362, 640, 3] uint8 mean 126.39 | ok |
| `cctv/event_fall.jpg` | `protect_edges=False` | 6.8 | [362, 640, 3] uint8 mean 125.18 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 10.6 | [362, 640, 3] uint8 mean 124.9 | ok |
| `cctv/event_optflow.jpg` | `amount=0.0` | 11.4 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_optflow.jpg` | `amount=3.0` | 11.1 | [362, 640, 3] uint8 mean 125.41 | ok |
| `cctv/event_optflow.jpg` | `protect_edges=False` | 6.9 | [362, 640, 3] uint8 mean 124.79 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 17.9 | [362, 640, 3] uint8 mean 160.06 | ok |
| `cctv/event_tamper.jpg` | `amount=0.0` | 14.3 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/event_tamper.jpg` | `amount=3.0` | 11.6 | [362, 640, 3] uint8 mean 159.95 | ok |
| `cctv/event_tamper.jpg` | `protect_edges=False` | 7.2 | [362, 640, 3] uint8 mean 160.04 | ok |
| `cctv/flattest.jpg` | `defaults` | 11.2 | [362, 640, 3] uint8 mean 120.98 | ok |
| `cctv/flattest.jpg` | `amount=0.0` | 12.4 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/flattest.jpg` | `amount=3.0` | 11.4 | [362, 640, 3] uint8 mean 121.47 | ok |
| `cctv/flattest.jpg` | `protect_edges=False` | 7.1 | [362, 640, 3] uint8 mean 120.87 | ok |
| `cctv/most_blown.jpg` | `defaults` | 11.2 | [362, 640, 3] uint8 mean 137.49 | ok |
| `cctv/most_blown.jpg` | `amount=0.0` | 12.7 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/most_blown.jpg` | `amount=3.0` | 11.2 | [362, 640, 3] uint8 mean 137.67 | ok |
| `cctv/most_blown.jpg` | `protect_edges=False` | 6.6 | [362, 640, 3] uint8 mean 137.39 | ok |
| `cctv/sharpest.jpg` | `defaults` | 11.7 | [362, 640, 3] uint8 mean 131.57 | ok |
| `cctv/sharpest.jpg` | `amount=0.0` | 12.0 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/sharpest.jpg` | `amount=3.0` | 11.2 | [362, 640, 3] uint8 mean 133.56 | ok |
| `cctv/sharpest.jpg` | `protect_edges=False` | 7.2 | [362, 640, 3] uint8 mean 131.78 | ok |
| `cctv/softest.jpg` | `defaults` | 13.1 | [362, 640, 3] uint8 mean 124.92 | ok |
| `cctv/softest.jpg` | `amount=0.0` | 11.6 | [362, 640, 3] uint8 mean 125.38 | output identical to input |
| `cctv/softest.jpg` | `amount=3.0` | 11.3 | [362, 640, 3] uint8 mean 125.7 | ok |
| `cctv/softest.jpg` | `protect_edges=False` | 7.0 | [362, 640, 3] uint8 mean 124.92 | ok |

## Artifacts

Outputs written to `validation/artifacts/texture_boost/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
