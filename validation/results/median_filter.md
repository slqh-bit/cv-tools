# median_filter - validation result

**Median filter for salt-and-pepper noise**  
`cv_tools.filters.smoothing` | family: Enhance | 2026-09-01T16:35:02

## Verdict

**PASS** - 9 runs, no invariant broken.

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 0.2 | [362, 640, 3] uint8 mean 163.82 | ok |
| `cctv/darkest.jpg` | `defaults` | 0.3 | [362, 640, 3] uint8 mean 111.13 | ok |
| `cctv/event_fall.jpg` | `defaults` | 0.3 | [362, 640, 3] uint8 mean 125.66 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 0.2 | [362, 640, 3] uint8 mean 125.54 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 0.2 | [362, 640, 3] uint8 mean 160.9 | ok |
| `cctv/flattest.jpg` | `defaults` | 0.2 | [362, 640, 3] uint8 mean 121.59 | ok |
| `cctv/most_blown.jpg` | `defaults` | 0.2 | [362, 640, 3] uint8 mean 138.33 | ok |
| `cctv/sharpest.jpg` | `defaults` | 0.2 | [362, 640, 3] uint8 mean 131.93 | ok |
| `cctv/softest.jpg` | `defaults` | 0.2 | [362, 640, 3] uint8 mean 125.51 | ok |

## Artifacts

Outputs written to `validation/artifacts/median_filter/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
