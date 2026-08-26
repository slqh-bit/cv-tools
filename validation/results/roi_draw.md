# roi_draw - validation result

**Draw a region of interest rectangle**  
`src.filters.roi` | family: Adjust | 2026-08-21T12:44:36

## Verdict

**PASS** - 36 runs, no invariant broken.

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `x=120, y=80, width=200, height=140` | 0.1 | [362, 640, 3] uint8 mean 162.92 | ok |
| `cctv/brightest.jpg` | `x=120, y=80, width=200, height=140, filled=True` | 0.4 | [362, 640, 3] uint8 mean 160.23 | ok |
| `cctv/brightest.jpg` | `x=120, y=80, width=200, height=140, alpha=0.0` | 0.1 | [362, 640, 3] uint8 mean 162.92 | ok |
| `cctv/brightest.jpg` | `x=120, y=80, width=200, height=140, alpha=1.0` | 0.2 | [362, 640, 3] uint8 mean 162.92 | ok |
| `cctv/darkest.jpg` | `x=120, y=80, width=200, height=140` | 0.2 | [362, 640, 3] uint8 mean 110.44 | ok |
| `cctv/darkest.jpg` | `x=120, y=80, width=200, height=140, filled=True` | 0.5 | [362, 640, 3] uint8 mean 108.57 | ok |
| `cctv/darkest.jpg` | `x=120, y=80, width=200, height=140, alpha=0.0` | 0.1 | [362, 640, 3] uint8 mean 110.44 | ok |
| `cctv/darkest.jpg` | `x=120, y=80, width=200, height=140, alpha=1.0` | 0.1 | [362, 640, 3] uint8 mean 110.44 | ok |
| `cctv/event_fall.jpg` | `x=120, y=80, width=200, height=140` | 0.1 | [362, 640, 3] uint8 mean 125.29 | ok |
| `cctv/event_fall.jpg` | `x=120, y=80, width=200, height=140, filled=True` | 0.4 | [362, 640, 3] uint8 mean 124.1 | ok |
| `cctv/event_fall.jpg` | `x=120, y=80, width=200, height=140, alpha=0.0` | 0.1 | [362, 640, 3] uint8 mean 125.29 | ok |
| `cctv/event_fall.jpg` | `x=120, y=80, width=200, height=140, alpha=1.0` | 0.1 | [362, 640, 3] uint8 mean 125.29 | ok |
| `cctv/event_optflow.jpg` | `x=120, y=80, width=200, height=140` | 0.1 | [362, 640, 3] uint8 mean 125.16 | ok |
| `cctv/event_optflow.jpg` | `x=120, y=80, width=200, height=140, filled=True` | 0.3 | [362, 640, 3] uint8 mean 123.69 | ok |
| `cctv/event_optflow.jpg` | `x=120, y=80, width=200, height=140, alpha=0.0` | 0.1 | [362, 640, 3] uint8 mean 125.16 | ok |
| `cctv/event_optflow.jpg` | `x=120, y=80, width=200, height=140, alpha=1.0` | 0.1 | [362, 640, 3] uint8 mean 125.16 | ok |
| `cctv/event_tamper.jpg` | `x=120, y=80, width=200, height=140` | 0.1 | [362, 640, 3] uint8 mean 160.03 | ok |
| `cctv/event_tamper.jpg` | `x=120, y=80, width=200, height=140, filled=True` | 0.3 | [362, 640, 3] uint8 mean 157.45 | ok |
| `cctv/event_tamper.jpg` | `x=120, y=80, width=200, height=140, alpha=0.0` | 0.1 | [362, 640, 3] uint8 mean 160.03 | ok |
| `cctv/event_tamper.jpg` | `x=120, y=80, width=200, height=140, alpha=1.0` | 0.1 | [362, 640, 3] uint8 mean 160.03 | ok |
| `cctv/flattest.jpg` | `x=120, y=80, width=200, height=140` | 0.1 | [362, 640, 3] uint8 mean 121.27 | ok |
| `cctv/flattest.jpg` | `x=120, y=80, width=200, height=140, filled=True` | 0.3 | [362, 640, 3] uint8 mean 119.9 | ok |
| `cctv/flattest.jpg` | `x=120, y=80, width=200, height=140, alpha=0.0` | 0.1 | [362, 640, 3] uint8 mean 121.27 | ok |
| `cctv/flattest.jpg` | `x=120, y=80, width=200, height=140, alpha=1.0` | 0.1 | [362, 640, 3] uint8 mean 121.27 | ok |
| `cctv/most_blown.jpg` | `x=120, y=80, width=200, height=140` | 0.1 | [362, 640, 3] uint8 mean 137.29 | ok |
| `cctv/most_blown.jpg` | `x=120, y=80, width=200, height=140, filled=True` | 0.4 | [362, 640, 3] uint8 mean 134.51 | ok |
| `cctv/most_blown.jpg` | `x=120, y=80, width=200, height=140, alpha=0.0` | 0.1 | [362, 640, 3] uint8 mean 137.29 | ok |
| `cctv/most_blown.jpg` | `x=120, y=80, width=200, height=140, alpha=1.0` | 0.1 | [362, 640, 3] uint8 mean 137.29 | ok |
| `cctv/sharpest.jpg` | `x=120, y=80, width=200, height=140` | 0.2 | [362, 640, 3] uint8 mean 131.04 | ok |
| `cctv/sharpest.jpg` | `x=120, y=80, width=200, height=140, filled=True` | 0.4 | [362, 640, 3] uint8 mean 128.79 | ok |
| `cctv/sharpest.jpg` | `x=120, y=80, width=200, height=140, alpha=0.0` | 0.1 | [362, 640, 3] uint8 mean 131.04 | ok |
| `cctv/sharpest.jpg` | `x=120, y=80, width=200, height=140, alpha=1.0` | 0.1 | [362, 640, 3] uint8 mean 131.04 | ok |
| `cctv/softest.jpg` | `x=120, y=80, width=200, height=140` | 0.2 | [362, 640, 3] uint8 mean 125.09 | ok |
| `cctv/softest.jpg` | `x=120, y=80, width=200, height=140, filled=True` | 0.4 | [362, 640, 3] uint8 mean 123.74 | ok |
| `cctv/softest.jpg` | `x=120, y=80, width=200, height=140, alpha=0.0` | 0.1 | [362, 640, 3] uint8 mean 125.09 | ok |
| `cctv/softest.jpg` | `x=120, y=80, width=200, height=140, alpha=1.0` | 0.1 | [362, 640, 3] uint8 mean 125.09 | ok |

## Artifacts

Outputs written to `validation/artifacts/roi_draw/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
