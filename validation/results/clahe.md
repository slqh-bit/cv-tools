# clahe - validation result

**Contrast Limited Adaptive Histogram Equalization**  
`src.filters.clahe` | family: Adjust | 2026-08-21T12:44:32

## Verdict

**PASS** - 45 runs, no invariant broken, 16 specific checks passed.

## What this filter specifically promises

- PASS - raises local contrast on the darkest frame: 13.56 -> 22.09 mean local sigma
- PASS - clip_limit raises contrast monotonically: 18.25 -> 22.09 -> 26.45 -> 30.25 for clip 1/2/4/8
- PASS - does not multiply shadow noise beyond 3x: sigma 1.68 -> 3.20
- PASS - colour mode lab returns a usable image: std 49.9
- PASS - colour mode hsv returns a usable image: std 50.2
- PASS - colour mode yuv returns a usable image: std 50.1
- PASS - colour mode channelwise returns a usable image: std 50.1
- PASS - colour mode luminance returns a usable image: std 50.1
- PASS - clahe does not move content: the marker centred at (163.5, 163.5) reads centred at (163.5, 163.5)
- PASS - clahe keeps the red block red: channel 0 dominates, expected 0
- PASS - clahe keeps the green block green: channel 1 dominates, expected 1
- PASS - clahe keeps the blue block blue: channel 2 dominates, expected 2
- PASS - clahe reaches both halves of the frame: mean change 23.50 left against 23.39 right
- PASS - clahe: clip_limit moves the result up across its whole range: 0.1:13.74, 2.08:20.59, 4.06:24.28, 6.04:26.52, 8.02:28.13, 10:29.33
- PASS - clahe: the measure still separates values in the upper half of the clip_limit range: the top half moves 2.81 of a total 15.58
- PASS - clahe: no clip_limit on the slider flattens the image: all 6 sampled values keep image structure

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 31.1 | [362, 640, 3] uint8 mean 153.41 | ok |
| `cctv/brightest.jpg` | `clip_limit=0.1` | 2.6 | [362, 640, 3] uint8 mean 164.06 | ok |
| `cctv/brightest.jpg` | `clip_limit=10.0` | 1.9 | [362, 640, 3] uint8 mean 134.62 | ok |
| `cctv/brightest.jpg` | `color_mode=hsv` | 1.3 | [362, 640, 3] uint8 mean 153.89 | ok |
| `cctv/brightest.jpg` | `color_mode=yuv` | 1.1 | [362, 640, 3] uint8 mean 154.85 | ok |
| `cctv/darkest.jpg` | `defaults` | 1.9 | [362, 640, 3] uint8 mean 119.52 | ok |
| `cctv/darkest.jpg` | `clip_limit=0.1` | 1.7 | [362, 640, 3] uint8 mean 112.72 | ok |
| `cctv/darkest.jpg` | `clip_limit=10.0` | 2.1 | [362, 640, 3] uint8 mean 125.12 | ok |
| `cctv/darkest.jpg` | `color_mode=hsv` | 1.2 | [362, 640, 3] uint8 mean 118.83 | ok |
| `cctv/darkest.jpg` | `color_mode=yuv` | 1.0 | [362, 640, 3] uint8 mean 121.2 | ok |
| `cctv/event_fall.jpg` | `defaults` | 1.8 | [362, 640, 3] uint8 mean 126.44 | ok |
| `cctv/event_fall.jpg` | `clip_limit=0.1` | 2.0 | [362, 640, 3] uint8 mean 127.7 | ok |
| `cctv/event_fall.jpg` | `clip_limit=10.0` | 1.9 | [362, 640, 3] uint8 mean 122.86 | ok |
| `cctv/event_fall.jpg` | `color_mode=hsv` | 1.0 | [362, 640, 3] uint8 mean 125.95 | ok |
| `cctv/event_fall.jpg` | `color_mode=yuv` | 1.1 | [362, 640, 3] uint8 mean 130.08 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 2.0 | [362, 640, 3] uint8 mean 126.7 | ok |
| `cctv/event_optflow.jpg` | `clip_limit=0.1` | 2.3 | [362, 640, 3] uint8 mean 126.8 | ok |
| `cctv/event_optflow.jpg` | `clip_limit=10.0` | 2.0 | [362, 640, 3] uint8 mean 123.57 | ok |
| `cctv/event_optflow.jpg` | `color_mode=hsv` | 1.3 | [362, 640, 3] uint8 mean 124.51 | ok |
| `cctv/event_optflow.jpg` | `color_mode=yuv` | 1.0 | [362, 640, 3] uint8 mean 129.02 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 1.6 | [362, 640, 3] uint8 mean 150.63 | ok |
| `cctv/event_tamper.jpg` | `clip_limit=0.1` | 2.1 | [362, 640, 3] uint8 mean 161.13 | ok |
| `cctv/event_tamper.jpg` | `clip_limit=10.0` | 1.9 | [362, 640, 3] uint8 mean 133.05 | ok |
| `cctv/event_tamper.jpg` | `color_mode=hsv` | 1.3 | [362, 640, 3] uint8 mean 150.94 | ok |
| `cctv/event_tamper.jpg` | `color_mode=yuv` | 1.0 | [362, 640, 3] uint8 mean 152.5 | ok |
| `cctv/flattest.jpg` | `defaults` | 2.0 | [362, 640, 3] uint8 mean 124.38 | ok |
| `cctv/flattest.jpg` | `clip_limit=0.1` | 2.1 | [362, 640, 3] uint8 mean 122.91 | ok |
| `cctv/flattest.jpg` | `clip_limit=10.0` | 2.3 | [362, 640, 3] uint8 mean 123.92 | ok |
| `cctv/flattest.jpg` | `color_mode=hsv` | 1.2 | [362, 640, 3] uint8 mean 122.26 | ok |
| `cctv/flattest.jpg` | `color_mode=yuv` | 1.1 | [362, 640, 3] uint8 mean 127.01 | ok |
| `cctv/most_blown.jpg` | `defaults` | 2.1 | [362, 640, 3] uint8 mean 139.92 | ok |
| `cctv/most_blown.jpg` | `clip_limit=0.1` | 2.2 | [362, 640, 3] uint8 mean 139.42 | ok |
| `cctv/most_blown.jpg` | `clip_limit=10.0` | 2.1 | [362, 640, 3] uint8 mean 135.32 | ok |
| `cctv/most_blown.jpg` | `color_mode=hsv` | 1.2 | [362, 640, 3] uint8 mean 140.06 | ok |
| `cctv/most_blown.jpg` | `color_mode=yuv` | 1.2 | [362, 640, 3] uint8 mean 141.77 | ok |
| `cctv/sharpest.jpg` | `defaults` | 1.9 | [362, 640, 3] uint8 mean 135.03 | ok |
| `cctv/sharpest.jpg` | `clip_limit=0.1` | 2.2 | [362, 640, 3] uint8 mean 134.31 | ok |
| `cctv/sharpest.jpg` | `clip_limit=10.0` | 2.0 | [362, 640, 3] uint8 mean 130.11 | ok |
| `cctv/sharpest.jpg` | `color_mode=hsv` | 1.2 | [362, 640, 3] uint8 mean 135.62 | ok |
| `cctv/sharpest.jpg` | `color_mode=yuv` | 1.1 | [362, 640, 3] uint8 mean 138.07 | ok |
| `cctv/softest.jpg` | `defaults` | 2.0 | [362, 640, 3] uint8 mean 128.95 | ok |
| `cctv/softest.jpg` | `clip_limit=0.1` | 2.4 | [362, 640, 3] uint8 mean 126.64 | ok |
| `cctv/softest.jpg` | `clip_limit=10.0` | 2.1 | [362, 640, 3] uint8 mean 126.22 | ok |
| `cctv/softest.jpg` | `color_mode=hsv` | 1.3 | [362, 640, 3] uint8 mean 127.42 | ok |
| `cctv/softest.jpg` | `color_mode=yuv` | 1.1 | [362, 640, 3] uint8 mean 131.12 | ok |

## Artifacts

Outputs written to `validation/artifacts/clahe/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
