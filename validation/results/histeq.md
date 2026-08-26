# histeq - validation result

**Global histogram equalization**  
`src.filters.histogram_equalization` | family: Adjust | 2026-08-21T12:44:36

## Verdict

**PASS** - 27 runs, no invariant broken, 7 specific checks passed.

## What this filter specifically promises

- PASS - spreads the histogram wider than it found it: 1-99 percentile span 228 -> 249
- PASS - global equalization amplifies noise (expected, documented): sigma 1.59 -> 2.86 - this is why CLAHE exists
- PASS - histeq does not move content: the marker centred at (163.5, 163.5) reads centred at (163.5, 163.5)
- PASS - histeq keeps the red block red: channel 0 dominates, expected 0
- PASS - histeq keeps the green block green: channel 1 dominates, expected 1
- PASS - histeq keeps the blue block blue: channel 2 dominates, expected 2
- PASS - histeq reaches both halves of the frame: mean change 61.79 left against 62.64 right

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 1.7 | [362, 640, 3] uint8 mean 122.42 | ok |
| `cctv/brightest.jpg` | `color_mode=hsv` | 0.9 | [362, 640, 3] uint8 mean 124.17 | ok |
| `cctv/brightest.jpg` | `color_mode=yuv` | 0.7 | [362, 640, 3] uint8 mean 127.29 | ok |
| `cctv/darkest.jpg` | `defaults` | 1.4 | [362, 640, 3] uint8 mean 123.01 | ok |
| `cctv/darkest.jpg` | `color_mode=hsv` | 0.8 | [362, 640, 3] uint8 mean 123.51 | ok |
| `cctv/darkest.jpg` | `color_mode=yuv` | 0.9 | [362, 640, 3] uint8 mean 128.11 | ok |
| `cctv/event_fall.jpg` | `defaults` | 1.3 | [362, 640, 3] uint8 mean 119.88 | ok |
| `cctv/event_fall.jpg` | `color_mode=hsv` | 0.9 | [362, 640, 3] uint8 mean 117.65 | ok |
| `cctv/event_fall.jpg` | `color_mode=yuv` | 0.7 | [362, 640, 3] uint8 mean 125.66 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 1.3 | [362, 640, 3] uint8 mean 120.09 | ok |
| `cctv/event_optflow.jpg` | `color_mode=hsv` | 0.8 | [362, 640, 3] uint8 mean 116.44 | ok |
| `cctv/event_optflow.jpg` | `color_mode=yuv` | 0.7 | [362, 640, 3] uint8 mean 125.57 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 1.3 | [362, 640, 3] uint8 mean 122.7 | ok |
| `cctv/event_tamper.jpg` | `color_mode=hsv` | 0.8 | [362, 640, 3] uint8 mean 123.87 | ok |
| `cctv/event_tamper.jpg` | `color_mode=yuv` | 0.7 | [362, 640, 3] uint8 mean 127.65 | ok |
| `cctv/flattest.jpg` | `defaults` | 1.3 | [362, 640, 3] uint8 mean 120.55 | ok |
| `cctv/flattest.jpg` | `color_mode=hsv` | 0.8 | [362, 640, 3] uint8 mean 116.53 | ok |
| `cctv/flattest.jpg` | `color_mode=yuv` | 0.7 | [362, 640, 3] uint8 mean 126.03 | ok |
| `cctv/most_blown.jpg` | `defaults` | 1.3 | [362, 640, 3] uint8 mean 123.22 | ok |
| `cctv/most_blown.jpg` | `color_mode=hsv` | 0.8 | [362, 640, 3] uint8 mean 124.85 | ok |
| `cctv/most_blown.jpg` | `color_mode=yuv` | 0.7 | [362, 640, 3] uint8 mean 128.04 | ok |
| `cctv/sharpest.jpg` | `defaults` | 1.3 | [362, 640, 3] uint8 mean 122.44 | ok |
| `cctv/sharpest.jpg` | `color_mode=hsv` | 0.8 | [362, 640, 3] uint8 mean 124.36 | ok |
| `cctv/sharpest.jpg` | `color_mode=yuv` | 0.7 | [362, 640, 3] uint8 mean 127.6 | ok |
| `cctv/softest.jpg` | `defaults` | 1.3 | [362, 640, 3] uint8 mean 122.68 | ok |
| `cctv/softest.jpg` | `color_mode=hsv` | 0.8 | [362, 640, 3] uint8 mean 122.04 | ok |
| `cctv/softest.jpg` | `color_mode=yuv` | 0.7 | [362, 640, 3] uint8 mean 127.66 | ok |

## Artifacts

Outputs written to `validation/artifacts/histeq/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
