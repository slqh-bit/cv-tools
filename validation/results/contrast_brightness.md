# contrast_brightness - validation result

**Linear contrast, brightness and gamma adjustment**  
`src.filters.contrast_brightness` | family: Adjust | 2026-09-01T16:34:44

## Verdict

**PASS** - 63 runs, no invariant broken, 8 specific checks passed.

At default parameters this filter is an identity: contrast 1.0 and brightness 0 change nothing. An unchanged image there is correct, not a fault.

## What this filter specifically promises

- PASS - defaults are an identity: contrast 1.0, brightness 0
- PASS - brightness lifts the mean by about what was asked: asked +40, got +39.0 (clipping accounts for the rest)
- PASS - contrast above 1 widens the spread: std 47.3 -> 67.9
- PASS - contrast_brightness does not move content: the marker centred at (163.5, 163.5) reads centred at (163.5, 163.5)
- PASS - contrast_brightness keeps the red block red: channel 0 dominates, expected 0
- PASS - contrast_brightness keeps the green block green: channel 1 dominates, expected 1
- PASS - contrast_brightness keeps the blue block blue: channel 2 dominates, expected 2
- PASS - contrast_brightness reaches both halves of the frame: mean change 21.72 left against 21.69 right

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `` on `cctv/brightest.jpg`: output identical to input
- `brightness=-255.0` on `cctv/brightest.jpg`: flat output - every pixel is 0
- `brightness=255.0` on `cctv/brightest.jpg`: flat output - every pixel is 255
- `contrast=0.0` on `cctv/brightest.jpg`: flat output - every pixel is 128
- `` on `cctv/darkest.jpg`: output identical to input
- `brightness=-255.0` on `cctv/darkest.jpg`: flat output - every pixel is 0
- `brightness=255.0` on `cctv/darkest.jpg`: flat output - every pixel is 255
- `contrast=0.0` on `cctv/darkest.jpg`: flat output - every pixel is 128
- `` on `cctv/event_fall.jpg`: output identical to input
- `brightness=-255.0` on `cctv/event_fall.jpg`: flat output - every pixel is 0
- `brightness=255.0` on `cctv/event_fall.jpg`: flat output - every pixel is 255
- `contrast=0.0` on `cctv/event_fall.jpg`: flat output - every pixel is 128

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 5.9 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/brightest.jpg` | `brightness=-255.0` | 5.2 | [362, 640, 3] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/brightest.jpg` | `brightness=255.0` | 4.9 | [362, 640, 3] uint8 mean 255.0 | flat output - every pixel is 255 |
| `cctv/brightest.jpg` | `contrast=0.0` | 5.2 | [362, 640, 3] uint8 mean 128.0 | flat output - every pixel is 128 |
| `cctv/brightest.jpg` | `contrast=3.0` | 5.8 | [362, 640, 3] uint8 mean 166.36 | ok |
| `cctv/brightest.jpg` | `gamma=0.1` | 14.3 | [362, 640, 3] uint8 mean 44.96 | ok |
| `cctv/brightest.jpg` | `gamma=3.0` | 15.1 | [362, 640, 3] uint8 mean 214.8 | ok |
| `cctv/darkest.jpg` | `defaults` | 5.0 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/darkest.jpg` | `brightness=-255.0` | 6.0 | [362, 640, 3] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/darkest.jpg` | `brightness=255.0` | 5.8 | [362, 640, 3] uint8 mean 255.0 | flat output - every pixel is 255 |
| `cctv/darkest.jpg` | `contrast=0.0` | 4.9 | [362, 640, 3] uint8 mean 128.0 | flat output - every pixel is 128 |
| `cctv/darkest.jpg` | `contrast=3.0` | 5.2 | [362, 640, 3] uint8 mean 82.69 | ok |
| `cctv/darkest.jpg` | `gamma=0.1` | 14.7 | [362, 640, 3] uint8 mean 12.83 | ok |
| `cctv/darkest.jpg` | `gamma=3.0` | 13.9 | [362, 640, 3] uint8 mean 188.23 | ok |
| `cctv/event_fall.jpg` | `defaults` | 4.9 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_fall.jpg` | `brightness=-255.0` | 8.7 | [362, 640, 3] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/event_fall.jpg` | `brightness=255.0` | 5.6 | [362, 640, 3] uint8 mean 255.0 | flat output - every pixel is 255 |
| `cctv/event_fall.jpg` | `contrast=0.0` | 4.8 | [362, 640, 3] uint8 mean 128.0 | flat output - every pixel is 128 |
| `cctv/event_fall.jpg` | `contrast=3.0` | 5.4 | [362, 640, 3] uint8 mean 124.7 | ok |
| `cctv/event_fall.jpg` | `gamma=0.1` | 14.1 | [362, 640, 3] uint8 mean 14.93 | ok |
| `cctv/event_fall.jpg` | `gamma=3.0` | 14.7 | [362, 640, 3] uint8 mean 193.43 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 5.1 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_optflow.jpg` | `brightness=-255.0` | 5.1 | [362, 640, 3] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/event_optflow.jpg` | `brightness=255.0` | 5.3 | [362, 640, 3] uint8 mean 255.0 | flat output - every pixel is 255 |
| `cctv/event_optflow.jpg` | `contrast=0.0` | 6.1 | [362, 640, 3] uint8 mean 128.0 | flat output - every pixel is 128 |
| `cctv/event_optflow.jpg` | `contrast=3.0` | 5.0 | [362, 640, 3] uint8 mean 123.74 | ok |
| `cctv/event_optflow.jpg` | `gamma=0.1` | 14.8 | [362, 640, 3] uint8 mean 8.98 | ok |
| `cctv/event_optflow.jpg` | `gamma=3.0` | 14.4 | [362, 640, 3] uint8 mean 196.69 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 6.8 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/event_tamper.jpg` | `brightness=-255.0` | 5.6 | [362, 640, 3] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/event_tamper.jpg` | `brightness=255.0` | 8.3 | [362, 640, 3] uint8 mean 255.0 | flat output - every pixel is 255 |
| `cctv/event_tamper.jpg` | `contrast=0.0` | 6.0 | [362, 640, 3] uint8 mean 128.0 | flat output - every pixel is 128 |
| `cctv/event_tamper.jpg` | `contrast=3.0` | 7.4 | [362, 640, 3] uint8 mean 163.82 | ok |
| `cctv/event_tamper.jpg` | `gamma=0.1` | 16.3 | [362, 640, 3] uint8 mean 39.09 | ok |
| `cctv/event_tamper.jpg` | `gamma=3.0` | 17.1 | [362, 640, 3] uint8 mean 213.48 | ok |
| `cctv/flattest.jpg` | `defaults` | 5.7 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/flattest.jpg` | `brightness=-255.0` | 7.4 | [362, 640, 3] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/flattest.jpg` | `brightness=255.0` | 5.4 | [362, 640, 3] uint8 mean 255.0 | flat output - every pixel is 255 |
| `cctv/flattest.jpg` | `contrast=0.0` | 5.6 | [362, 640, 3] uint8 mean 128.0 | flat output - every pixel is 128 |
| `cctv/flattest.jpg` | `contrast=3.0` | 7.4 | [362, 640, 3] uint8 mean 115.23 | ok |
| `cctv/flattest.jpg` | `gamma=0.1` | 15.3 | [362, 640, 3] uint8 mean 7.84 | ok |
| `cctv/flattest.jpg` | `gamma=3.0` | 14.6 | [362, 640, 3] uint8 mean 194.71 | ok |
| `cctv/most_blown.jpg` | `defaults` | 6.3 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/most_blown.jpg` | `brightness=-255.0` | 5.6 | [362, 640, 3] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/most_blown.jpg` | `brightness=255.0` | 5.4 | [362, 640, 3] uint8 mean 255.0 | flat output - every pixel is 255 |
| `cctv/most_blown.jpg` | `contrast=0.0` | 5.3 | [362, 640, 3] uint8 mean 128.0 | flat output - every pixel is 128 |
| `cctv/most_blown.jpg` | `contrast=3.0` | 5.1 | [362, 640, 3] uint8 mean 135.16 | ok |
| `cctv/most_blown.jpg` | `gamma=0.1` | 14.9 | [362, 640, 3] uint8 mean 29.18 | ok |
| `cctv/most_blown.jpg` | `gamma=3.0` | 15.3 | [362, 640, 3] uint8 mean 202.74 | ok |
| `cctv/sharpest.jpg` | `defaults` | 5.3 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/sharpest.jpg` | `brightness=-255.0` | 5.3 | [362, 640, 3] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/sharpest.jpg` | `brightness=255.0` | 5.4 | [362, 640, 3] uint8 mean 255.0 | flat output - every pixel is 255 |
| `cctv/sharpest.jpg` | `contrast=0.0` | 6.0 | [362, 640, 3] uint8 mean 128.0 | flat output - every pixel is 128 |
| `cctv/sharpest.jpg` | `contrast=3.0` | 5.3 | [362, 640, 3] uint8 mean 131.5 | ok |
| `cctv/sharpest.jpg` | `gamma=0.1` | 15.1 | [362, 640, 3] uint8 mean 24.49 | ok |
| `cctv/sharpest.jpg` | `gamma=3.0` | 15.1 | [362, 640, 3] uint8 mean 196.94 | ok |
| `cctv/softest.jpg` | `defaults` | 5.5 | [362, 640, 3] uint8 mean 125.38 | output identical to input |
| `cctv/softest.jpg` | `brightness=-255.0` | 6.6 | [362, 640, 3] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/softest.jpg` | `brightness=255.0` | 5.2 | [362, 640, 3] uint8 mean 255.0 | flat output - every pixel is 255 |
| `cctv/softest.jpg` | `contrast=0.0` | 5.1 | [362, 640, 3] uint8 mean 128.0 | flat output - every pixel is 128 |
| `cctv/softest.jpg` | `contrast=3.0` | 5.7 | [362, 640, 3] uint8 mean 125.95 | ok |
| `cctv/softest.jpg` | `gamma=0.1` | 13.7 | [362, 640, 3] uint8 mean 4.01 | ok |
| `cctv/softest.jpg` | `gamma=3.0` | 14.5 | [362, 640, 3] uint8 mean 196.76 | ok |

## Artifacts

Outputs written to `validation/artifacts/contrast_brightness/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
