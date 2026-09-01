# roi_filter - validation result

**Run another filter inside one region only, with a softened edge**  
`src.filters.roi` | family: Adjust | 2026-09-01T16:34:48

## Verdict

**PASS** - 9 runs, no invariant broken.

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `x=120, y=80, width=200, height=140` | 3.3 | [362, 640, 3] uint8 mean 163.43 | ok |
| `cctv/darkest.jpg` | `x=120, y=80, width=200, height=140` | 3.0 | [362, 640, 3] uint8 mean 112.24 | ok |
| `cctv/event_fall.jpg` | `x=120, y=80, width=200, height=140` | 2.9 | [362, 640, 3] uint8 mean 125.83 | ok |
| `cctv/event_optflow.jpg` | `x=120, y=80, width=200, height=140` | 2.7 | [362, 640, 3] uint8 mean 125.93 | ok |
| `cctv/event_tamper.jpg` | `x=120, y=80, width=200, height=140` | 2.7 | [362, 640, 3] uint8 mean 160.71 | ok |
| `cctv/flattest.jpg` | `x=120, y=80, width=200, height=140` | 2.8 | [362, 640, 3] uint8 mean 122.08 | ok |
| `cctv/most_blown.jpg` | `x=120, y=80, width=200, height=140` | 2.9 | [362, 640, 3] uint8 mean 138.83 | ok |
| `cctv/sharpest.jpg` | `x=120, y=80, width=200, height=140` | 2.8 | [362, 640, 3] uint8 mean 132.81 | ok |
| `cctv/softest.jpg` | `x=120, y=80, width=200, height=140` | 3.3 | [362, 640, 3] uint8 mean 126.96 | ok |

## Artifacts

Outputs written to `validation/artifacts/roi_filter/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
