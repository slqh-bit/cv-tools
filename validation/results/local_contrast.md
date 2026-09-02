# local_contrast - validation result

**Large-radius local contrast (clarity)**  
`cv_tools.filters.detail_enhancement` | family: Enhance | 2026-09-01T16:35:41

## Verdict

**PASS** - 45 runs, no invariant broken, 11 specific checks passed.

## What this filter specifically promises

- PASS - raises large-scale local contrast: 19.19 -> 25.80 mean local sigma at 31px
- PASS - strength raises it, and the ends differ materially: 21.96 -> 25.80 -> 31.19 for strength 0.2/0.5/1.0 (1.42x end to end)
- PASS - does not clip the frame at full strength: 7.7% of pixels driven to 0 or 255
- PASS - local_contrast does not move content: the marker centred at (163.5, 163.5) reads centred at (163.5, 163.5)
- PASS - local_contrast keeps the red block red: channel 0 dominates, expected 0
- PASS - local_contrast keeps the green block green: channel 1 dominates, expected 1
- PASS - local_contrast keeps the blue block blue: channel 2 dominates, expected 2
- PASS - local_contrast reaches both halves of the frame: mean change 8.94 left against 8.95 right
- PASS - local_contrast: strength moves the result up across its whole range: 0:19.19, 0.4:24.55, 0.8:29.18, 1.2:33.03, 1.6:36.31, 2:39.20
- PASS - local_contrast: the measure still separates values in the upper half of the strength range: the top half moves 6.17 of a total 20.01
- PASS - local_contrast: no strength on the slider flattens the image: all 6 sampled values keep image structure

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `radius=0.1` on `cctv/brightest.jpg`: output identical to input
- `strength=0.0` on `cctv/brightest.jpg`: output identical to input
- `radius=0.1` on `cctv/darkest.jpg`: output identical to input
- `strength=0.0` on `cctv/darkest.jpg`: output identical to input
- `radius=0.1` on `cctv/event_fall.jpg`: output identical to input
- `strength=0.0` on `cctv/event_fall.jpg`: output identical to input
- `radius=0.1` on `cctv/event_optflow.jpg`: output identical to input
- `strength=0.0` on `cctv/event_optflow.jpg`: output identical to input
- `radius=0.1` on `cctv/event_tamper.jpg`: output identical to input
- `strength=0.0` on `cctv/event_tamper.jpg`: output identical to input
- `radius=0.1` on `cctv/flattest.jpg`: output identical to input
- `strength=0.0` on `cctv/flattest.jpg`: output identical to input

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 35.6 | [362, 640, 3] uint8 mean 162.8 | ok |
| `cctv/brightest.jpg` | `radius=0.1` | 6.0 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/brightest.jpg` | `radius=50.0` | 271.7 | [362, 640, 3] uint8 mean 162.29 | ok |
| `cctv/brightest.jpg` | `strength=0.0` | 30.5 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/brightest.jpg` | `strength=2.0` | 30.0 | [362, 640, 3] uint8 mean 160.52 | ok |
| `cctv/darkest.jpg` | `defaults` | 35.7 | [362, 640, 3] uint8 mean 109.61 | ok |
| `cctv/darkest.jpg` | `radius=0.1` | 5.8 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/darkest.jpg` | `radius=50.0` | 278.4 | [362, 640, 3] uint8 mean 109.05 | ok |
| `cctv/darkest.jpg` | `strength=0.0` | 29.7 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/darkest.jpg` | `strength=2.0` | 31.9 | [362, 640, 3] uint8 mean 108.49 | ok |
| `cctv/event_fall.jpg` | `defaults` | 32.9 | [362, 640, 3] uint8 mean 124.93 | ok |
| `cctv/event_fall.jpg` | `radius=0.1` | 5.8 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_fall.jpg` | `radius=50.0` | 263.6 | [362, 640, 3] uint8 mean 124.63 | ok |
| `cctv/event_fall.jpg` | `strength=0.0` | 28.9 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_fall.jpg` | `strength=2.0` | 30.6 | [362, 640, 3] uint8 mean 125.99 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 29.9 | [362, 640, 3] uint8 mean 124.54 | ok |
| `cctv/event_optflow.jpg` | `radius=0.1` | 5.2 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_optflow.jpg` | `radius=50.0` | 253.3 | [362, 640, 3] uint8 mean 124.05 | ok |
| `cctv/event_optflow.jpg` | `strength=0.0` | 29.7 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_optflow.jpg` | `strength=2.0` | 34.3 | [362, 640, 3] uint8 mean 124.92 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 28.8 | [362, 640, 3] uint8 mean 159.92 | ok |
| `cctv/event_tamper.jpg` | `radius=0.1` | 5.5 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/event_tamper.jpg` | `radius=50.0` | 263.8 | [362, 640, 3] uint8 mean 159.46 | ok |
| `cctv/event_tamper.jpg` | `strength=0.0` | 30.7 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/event_tamper.jpg` | `strength=2.0` | 36.3 | [362, 640, 3] uint8 mean 157.74 | ok |
| `cctv/flattest.jpg` | `defaults` | 29.6 | [362, 640, 3] uint8 mean 120.63 | ok |
| `cctv/flattest.jpg` | `radius=0.1` | 5.1 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/flattest.jpg` | `radius=50.0` | 241.6 | [362, 640, 3] uint8 mean 120.15 | ok |
| `cctv/flattest.jpg` | `strength=0.0` | 28.9 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/flattest.jpg` | `strength=2.0` | 29.9 | [362, 640, 3] uint8 mean 121.09 | ok |
| `cctv/most_blown.jpg` | `defaults` | 28.1 | [362, 640, 3] uint8 mean 136.96 | ok |
| `cctv/most_blown.jpg` | `radius=0.1` | 5.9 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/most_blown.jpg` | `radius=50.0` | 238.5 | [362, 640, 3] uint8 mean 136.15 | ok |
| `cctv/most_blown.jpg` | `strength=0.0` | 28.1 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/most_blown.jpg` | `strength=2.0` | 28.9 | [362, 640, 3] uint8 mean 136.06 | ok |
| `cctv/sharpest.jpg` | `defaults` | 29.1 | [362, 640, 3] uint8 mean 131.48 | ok |
| `cctv/sharpest.jpg` | `radius=0.1` | 5.2 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/sharpest.jpg` | `radius=50.0` | 251.5 | [362, 640, 3] uint8 mean 130.69 | ok |
| `cctv/sharpest.jpg` | `strength=0.0` | 30.2 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/sharpest.jpg` | `strength=2.0` | 33.8 | [362, 640, 3] uint8 mean 134.28 | ok |
| `cctv/softest.jpg` | `defaults` | 27.1 | [362, 640, 3] uint8 mean 125.16 | ok |
| `cctv/softest.jpg` | `radius=0.1` | 5.9 | [362, 640, 3] uint8 mean 125.38 | output identical to input |
| `cctv/softest.jpg` | `radius=50.0` | 246.3 | [362, 640, 3] uint8 mean 125.16 | ok |
| `cctv/softest.jpg` | `strength=0.0` | 29.1 | [362, 640, 3] uint8 mean 125.38 | output identical to input |
| `cctv/softest.jpg` | `strength=2.0` | 30.8 | [362, 640, 3] uint8 mean 125.73 | ok |

## Artifacts

Outputs written to `validation/artifacts/local_contrast/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
