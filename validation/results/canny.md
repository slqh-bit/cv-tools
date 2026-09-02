# canny - validation result

**Canny edge detection**  
`cv_tools.filters.edge_detection` | family: Analyze | 2026-09-01T16:35:57

## Verdict

**PASS** - 72 runs, no invariant broken, 7 specific checks passed.

18 run(s) refused bad parameters with a clear message, which is the wanted behaviour.

## What this filter specifically promises

- PASS - canny returns a binary map: distinct values [0, 255]
- PASS - canny puts the edge where the edge is: edge pixels centred on column 63, the step is at 64
- PASS - canny finds nothing in a flat frame: 0 edge pixels in a uniform image
- PASS - auto_canny returns a binary map: distinct values [0, 255]
- PASS - auto_canny puts the edge where the edge is: edge pixels centred on column 63, the step is at 64
- PASS - auto_canny finds nothing in a flat frame: 0 edge pixels in a uniform image
- PASS - a higher canny threshold finds fewer edges: 52594 -> 32319 -> 21955 edge pixels at low threshold 20/60/120

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `low_threshold=255` on `cctv/brightest.jpg`: refused: low_threshold (255) must not exceed high_threshold (200)
- `high_threshold=0` on `cctv/brightest.jpg`: refused: low_threshold (100) must not exceed high_threshold (0)
- `blur_sigma=10.0` on `cctv/brightest.jpg`: flat output - every pixel is 0
- `low_threshold=255` on `cctv/darkest.jpg`: refused: low_threshold (255) must not exceed high_threshold (200)
- `high_threshold=0` on `cctv/darkest.jpg`: refused: low_threshold (100) must not exceed high_threshold (0)
- `blur_sigma=10.0` on `cctv/darkest.jpg`: flat output - every pixel is 0
- `low_threshold=255` on `cctv/event_fall.jpg`: refused: low_threshold (255) must not exceed high_threshold (200)
- `high_threshold=0` on `cctv/event_fall.jpg`: refused: low_threshold (100) must not exceed high_threshold (0)
- `blur_sigma=10.0` on `cctv/event_fall.jpg`: flat output - every pixel is 0
- `low_threshold=255` on `cctv/event_optflow.jpg`: refused: low_threshold (255) must not exceed high_threshold (200)
- `high_threshold=0` on `cctv/event_optflow.jpg`: refused: low_threshold (100) must not exceed high_threshold (0)
- `blur_sigma=10.0` on `cctv/event_optflow.jpg`: flat output - every pixel is 0

## Refused parameters

Rejected on purpose, with the message the user would see.

- `low_threshold=255` -> ValueError: low_threshold (255) must not exceed high_threshold (200)
- `high_threshold=0` -> ValueError: low_threshold (100) must not exceed high_threshold (0)

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 0.9 | [362, 640] uint8 mean 11.4 | ok |
| `cctv/brightest.jpg` | `low_threshold=0` | 1.6 | [362, 640] uint8 mean 25.51 | ok |
| `cctv/brightest.jpg` | `low_threshold=255` | 0.0 | - | refused: ValueError: low_threshold (255) must not exceed high_threshold (200) |
| `cctv/brightest.jpg` | `high_threshold=0` | 0.0 | - | refused: ValueError: low_threshold (100) must not exceed high_threshold (0) |
| `cctv/brightest.jpg` | `high_threshold=255` | 0.4 | [362, 640] uint8 mean 9.83 | ok |
| `cctv/brightest.jpg` | `l2_gradient=True` | 0.7 | [362, 640] uint8 mean 9.26 | ok |
| `cctv/brightest.jpg` | `blur_sigma=0.0` | 0.6 | [362, 640] uint8 mean 11.4 | ok |
| `cctv/brightest.jpg` | `blur_sigma=10.0` | 4.5 | [362, 640] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/darkest.jpg` | `defaults` | 0.6 | [362, 640] uint8 mean 16.69 | ok |
| `cctv/darkest.jpg` | `low_threshold=0` | 0.9 | [362, 640] uint8 mean 30.11 | ok |
| `cctv/darkest.jpg` | `low_threshold=255` | 0.0 | - | refused: ValueError: low_threshold (255) must not exceed high_threshold (200) |
| `cctv/darkest.jpg` | `high_threshold=0` | 0.0 | - | refused: ValueError: low_threshold (100) must not exceed high_threshold (0) |
| `cctv/darkest.jpg` | `high_threshold=255` | 0.5 | [362, 640] uint8 mean 15.04 | ok |
| `cctv/darkest.jpg` | `l2_gradient=True` | 0.6 | [362, 640] uint8 mean 13.6 | ok |
| `cctv/darkest.jpg` | `blur_sigma=0.0` | 0.5 | [362, 640] uint8 mean 16.69 | ok |
| `cctv/darkest.jpg` | `blur_sigma=10.0` | 3.1 | [362, 640] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/event_fall.jpg` | `defaults` | 0.6 | [362, 640] uint8 mean 28.93 | ok |
| `cctv/event_fall.jpg` | `low_threshold=0` | 1.2 | [362, 640] uint8 mean 51.43 | ok |
| `cctv/event_fall.jpg` | `low_threshold=255` | 0.0 | - | refused: ValueError: low_threshold (255) must not exceed high_threshold (200) |
| `cctv/event_fall.jpg` | `high_threshold=0` | 0.0 | - | refused: ValueError: low_threshold (100) must not exceed high_threshold (0) |
| `cctv/event_fall.jpg` | `high_threshold=255` | 0.7 | [362, 640] uint8 mean 26.88 | ok |
| `cctv/event_fall.jpg` | `l2_gradient=True` | 0.6 | [362, 640] uint8 mean 25.01 | ok |
| `cctv/event_fall.jpg` | `blur_sigma=0.0` | 0.8 | [362, 640] uint8 mean 28.93 | ok |
| `cctv/event_fall.jpg` | `blur_sigma=10.0` | 3.8 | [362, 640] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/event_optflow.jpg` | `defaults` | 0.4 | [362, 640] uint8 mean 15.28 | ok |
| `cctv/event_optflow.jpg` | `low_threshold=0` | 0.9 | [362, 640] uint8 mean 25.25 | ok |
| `cctv/event_optflow.jpg` | `low_threshold=255` | 0.0 | - | refused: ValueError: low_threshold (255) must not exceed high_threshold (200) |
| `cctv/event_optflow.jpg` | `high_threshold=0` | 0.0 | - | refused: ValueError: low_threshold (100) must not exceed high_threshold (0) |
| `cctv/event_optflow.jpg` | `high_threshold=255` | 0.5 | [362, 640] uint8 mean 13.76 | ok |
| `cctv/event_optflow.jpg` | `l2_gradient=True` | 0.4 | [362, 640] uint8 mean 13.23 | ok |
| `cctv/event_optflow.jpg` | `blur_sigma=0.0` | 0.5 | [362, 640] uint8 mean 15.28 | ok |
| `cctv/event_optflow.jpg` | `blur_sigma=10.0` | 3.1 | [362, 640] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/event_tamper.jpg` | `defaults` | 0.4 | [362, 640] uint8 mean 10.92 | ok |
| `cctv/event_tamper.jpg` | `low_threshold=0` | 1.1 | [362, 640] uint8 mean 24.08 | ok |
| `cctv/event_tamper.jpg` | `low_threshold=255` | 0.0 | - | refused: ValueError: low_threshold (255) must not exceed high_threshold (200) |
| `cctv/event_tamper.jpg` | `high_threshold=0` | 0.0 | - | refused: ValueError: low_threshold (100) must not exceed high_threshold (0) |
| `cctv/event_tamper.jpg` | `high_threshold=255` | 0.4 | [362, 640] uint8 mean 9.48 | ok |
| `cctv/event_tamper.jpg` | `l2_gradient=True` | 0.4 | [362, 640] uint8 mean 8.99 | ok |
| `cctv/event_tamper.jpg` | `blur_sigma=0.0` | 0.5 | [362, 640] uint8 mean 10.92 | ok |
| `cctv/event_tamper.jpg` | `blur_sigma=10.0` | 3.0 | [362, 640] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/flattest.jpg` | `defaults` | 0.4 | [362, 640] uint8 mean 14.37 | ok |
| `cctv/flattest.jpg` | `low_threshold=0` | 0.9 | [362, 640] uint8 mean 22.84 | ok |
| `cctv/flattest.jpg` | `low_threshold=255` | 0.0 | - | refused: ValueError: low_threshold (255) must not exceed high_threshold (200) |
| `cctv/flattest.jpg` | `high_threshold=0` | 0.0 | - | refused: ValueError: low_threshold (100) must not exceed high_threshold (0) |
| `cctv/flattest.jpg` | `high_threshold=255` | 0.5 | [362, 640] uint8 mean 13.49 | ok |
| `cctv/flattest.jpg` | `l2_gradient=True` | 0.7 | [362, 640] uint8 mean 12.33 | ok |
| `cctv/flattest.jpg` | `blur_sigma=0.0` | 0.7 | [362, 640] uint8 mean 14.37 | ok |
| `cctv/flattest.jpg` | `blur_sigma=10.0` | 3.3 | [362, 640] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/most_blown.jpg` | `defaults` | 0.5 | [362, 640] uint8 mean 17.34 | ok |
| `cctv/most_blown.jpg` | `low_threshold=0` | 1.3 | [362, 640] uint8 mean 27.69 | ok |
| `cctv/most_blown.jpg` | `low_threshold=255` | 0.0 | - | refused: ValueError: low_threshold (255) must not exceed high_threshold (200) |
| `cctv/most_blown.jpg` | `high_threshold=0` | 0.0 | - | refused: ValueError: low_threshold (100) must not exceed high_threshold (0) |
| `cctv/most_blown.jpg` | `high_threshold=255` | 0.4 | [362, 640] uint8 mean 15.63 | ok |
| `cctv/most_blown.jpg` | `l2_gradient=True` | 0.4 | [362, 640] uint8 mean 14.17 | ok |
| `cctv/most_blown.jpg` | `blur_sigma=0.0` | 0.7 | [362, 640] uint8 mean 17.34 | ok |
| `cctv/most_blown.jpg` | `blur_sigma=10.0` | 3.0 | [362, 640] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/sharpest.jpg` | `defaults` | 0.9 | [362, 640] uint8 mean 30.53 | ok |
| `cctv/sharpest.jpg` | `low_threshold=0` | 1.3 | [362, 640] uint8 mean 45.65 | ok |
| `cctv/sharpest.jpg` | `low_threshold=255` | 0.0 | - | refused: ValueError: low_threshold (255) must not exceed high_threshold (200) |
| `cctv/sharpest.jpg` | `high_threshold=0` | 0.0 | - | refused: ValueError: low_threshold (100) must not exceed high_threshold (0) |
| `cctv/sharpest.jpg` | `high_threshold=255` | 0.7 | [362, 640] uint8 mean 28.21 | ok |
| `cctv/sharpest.jpg` | `l2_gradient=True` | 1.0 | [362, 640] uint8 mean 26.53 | ok |
| `cctv/sharpest.jpg` | `blur_sigma=0.0` | 0.9 | [362, 640] uint8 mean 30.53 | ok |
| `cctv/sharpest.jpg` | `blur_sigma=10.0` | 3.0 | [362, 640] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/softest.jpg` | `defaults` | 0.3 | [362, 640] uint8 mean 9.08 | ok |
| `cctv/softest.jpg` | `low_threshold=0` | 1.0 | [362, 640] uint8 mean 19.47 | ok |
| `cctv/softest.jpg` | `low_threshold=255` | 0.0 | - | refused: ValueError: low_threshold (255) must not exceed high_threshold (200) |
| `cctv/softest.jpg` | `high_threshold=0` | 0.0 | - | refused: ValueError: low_threshold (100) must not exceed high_threshold (0) |
| `cctv/softest.jpg` | `high_threshold=255` | 0.4 | [362, 640] uint8 mean 8.2 | ok |
| `cctv/softest.jpg` | `l2_gradient=True` | 0.3 | [362, 640] uint8 mean 7.87 | ok |
| `cctv/softest.jpg` | `blur_sigma=0.0` | 0.4 | [362, 640] uint8 mean 9.08 | ok |
| `cctv/softest.jpg` | `blur_sigma=10.0` | 2.8 | [362, 640] uint8 mean 0.0 | flat output - every pixel is 0 |

## Artifacts

Outputs written to `validation/artifacts/canny/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
