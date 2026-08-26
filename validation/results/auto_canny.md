# auto_canny - validation result

**Canny with thresholds derived from image median**  
`src.filters.edge_detection` | family: Analyze | 2026-08-21T12:45:41

## Verdict

**PASS** - 45 runs, no invariant broken.

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `blur_sigma=10.0` on `cctv/brightest.jpg`: flat output - every pixel is 0
- `blur_sigma=10.0` on `cctv/darkest.jpg`: flat output - every pixel is 0
- `blur_sigma=10.0` on `cctv/event_fall.jpg`: flat output - every pixel is 0
- `blur_sigma=10.0` on `cctv/event_optflow.jpg`: flat output - every pixel is 0
- `blur_sigma=10.0` on `cctv/event_tamper.jpg`: flat output - every pixel is 0
- `blur_sigma=10.0` on `cctv/flattest.jpg`: flat output - every pixel is 0
- `blur_sigma=10.0` on `cctv/most_blown.jpg`: flat output - every pixel is 0
- `blur_sigma=10.0` on `cctv/sharpest.jpg`: flat output - every pixel is 0
- `blur_sigma=10.0` on `cctv/softest.jpg`: flat output - every pixel is 0

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 1.1 | [362, 640] uint8 mean 10.1 | ok |
| `cctv/brightest.jpg` | `sigma=0.01` | 1.1 | [362, 640] uint8 mean 9.01 | ok |
| `cctv/brightest.jpg` | `sigma=1.0` | 1.4 | [362, 640] uint8 mean 20.88 | ok |
| `cctv/brightest.jpg` | `blur_sigma=0.0` | 1.4 | [362, 640] uint8 mean 10.1 | ok |
| `cctv/brightest.jpg` | `blur_sigma=10.0` | 3.6 | [362, 640] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/darkest.jpg` | `defaults` | 1.1 | [362, 640] uint8 mean 21.18 | ok |
| `cctv/darkest.jpg` | `sigma=0.01` | 1.0 | [362, 640] uint8 mean 19.25 | ok |
| `cctv/darkest.jpg` | `sigma=1.0` | 1.3 | [362, 640] uint8 mean 29.38 | ok |
| `cctv/darkest.jpg` | `blur_sigma=0.0` | 1.1 | [362, 640] uint8 mean 21.18 | ok |
| `cctv/darkest.jpg` | `blur_sigma=10.0` | 2.8 | [362, 640] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/event_fall.jpg` | `defaults` | 1.6 | [362, 640] uint8 mean 32.27 | ok |
| `cctv/event_fall.jpg` | `sigma=0.01` | 1.6 | [362, 640] uint8 mean 29.99 | ok |
| `cctv/event_fall.jpg` | `sigma=1.0` | 2.0 | [362, 640] uint8 mean 46.76 | ok |
| `cctv/event_fall.jpg` | `blur_sigma=0.0` | 1.6 | [362, 640] uint8 mean 32.27 | ok |
| `cctv/event_fall.jpg` | `blur_sigma=10.0` | 3.3 | [362, 640] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/event_optflow.jpg` | `defaults` | 1.2 | [362, 640] uint8 mean 16.82 | ok |
| `cctv/event_optflow.jpg` | `sigma=0.01` | 1.2 | [362, 640] uint8 mean 15.5 | ok |
| `cctv/event_optflow.jpg` | `sigma=1.0` | 1.7 | [362, 640] uint8 mean 22.93 | ok |
| `cctv/event_optflow.jpg` | `blur_sigma=0.0` | 1.3 | [362, 640] uint8 mean 16.82 | ok |
| `cctv/event_optflow.jpg` | `blur_sigma=10.0` | 2.9 | [362, 640] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/event_tamper.jpg` | `defaults` | 0.9 | [362, 640] uint8 mean 10.12 | ok |
| `cctv/event_tamper.jpg` | `sigma=0.01` | 1.0 | [362, 640] uint8 mean 9.15 | ok |
| `cctv/event_tamper.jpg` | `sigma=1.0` | 1.3 | [362, 640] uint8 mean 20.22 | ok |
| `cctv/event_tamper.jpg` | `blur_sigma=0.0` | 0.9 | [362, 640] uint8 mean 10.12 | ok |
| `cctv/event_tamper.jpg` | `blur_sigma=10.0` | 2.8 | [362, 640] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/flattest.jpg` | `defaults` | 1.1 | [362, 640] uint8 mean 16.27 | ok |
| `cctv/flattest.jpg` | `sigma=0.01` | 1.1 | [362, 640] uint8 mean 15.11 | ok |
| `cctv/flattest.jpg` | `sigma=1.0` | 1.4 | [362, 640] uint8 mean 21.08 | ok |
| `cctv/flattest.jpg` | `blur_sigma=0.0` | 1.1 | [362, 640] uint8 mean 16.27 | ok |
| `cctv/flattest.jpg` | `blur_sigma=10.0` | 3.2 | [362, 640] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/most_blown.jpg` | `defaults` | 1.1 | [362, 640] uint8 mean 18.79 | ok |
| `cctv/most_blown.jpg` | `sigma=0.01` | 1.0 | [362, 640] uint8 mean 17.15 | ok |
| `cctv/most_blown.jpg` | `sigma=1.0` | 1.2 | [362, 640] uint8 mean 24.51 | ok |
| `cctv/most_blown.jpg` | `blur_sigma=0.0` | 1.0 | [362, 640] uint8 mean 18.79 | ok |
| `cctv/most_blown.jpg` | `blur_sigma=10.0` | 3.4 | [362, 640] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/sharpest.jpg` | `defaults` | 2.0 | [362, 640] uint8 mean 33.14 | ok |
| `cctv/sharpest.jpg` | `sigma=0.01` | 2.4 | [362, 640] uint8 mean 31.01 | ok |
| `cctv/sharpest.jpg` | `sigma=1.0` | 2.0 | [362, 640] uint8 mean 41.46 | ok |
| `cctv/sharpest.jpg` | `blur_sigma=0.0` | 1.9 | [362, 640] uint8 mean 33.14 | ok |
| `cctv/sharpest.jpg` | `blur_sigma=10.0` | 3.4 | [362, 640] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/softest.jpg` | `defaults` | 1.1 | [362, 640] uint8 mean 11.05 | ok |
| `cctv/softest.jpg` | `sigma=0.01` | 1.1 | [362, 640] uint8 mean 10.02 | ok |
| `cctv/softest.jpg` | `sigma=1.0` | 1.6 | [362, 640] uint8 mean 16.06 | ok |
| `cctv/softest.jpg` | `blur_sigma=0.0` | 1.1 | [362, 640] uint8 mean 11.05 | ok |
| `cctv/softest.jpg` | `blur_sigma=10.0` | 3.2 | [362, 640] uint8 mean 0.0 | flat output - every pixel is 0 |

## Artifacts

Outputs written to `validation/artifacts/auto_canny/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
