# arrow - validation result

**Draw a labelled arrow pointing at something**  
`cv_tools.filters.annotate` | family: Special | 2026-09-01T16:37:20

## Verdict

**PASS** - 9 runs, no invariant broken.

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `start=[500, 120], end=[340, 260]` | 0.1 | [362, 640, 3] uint8 mean 163.53 | ok |
| `cctv/darkest.jpg` | `start=[500, 120], end=[340, 260]` | 0.1 | [362, 640, 3] uint8 mean 111.03 | ok |
| `cctv/event_fall.jpg` | `start=[500, 120], end=[340, 260]` | 0.2 | [362, 640, 3] uint8 mean 125.51 | ok |
| `cctv/event_optflow.jpg` | `start=[500, 120], end=[340, 260]` | 0.2 | [362, 640, 3] uint8 mean 125.41 | ok |
| `cctv/event_tamper.jpg` | `start=[500, 120], end=[340, 260]` | 0.2 | [362, 640, 3] uint8 mean 160.63 | ok |
| `cctv/flattest.jpg` | `start=[500, 120], end=[340, 260]` | 0.2 | [362, 640, 3] uint8 mean 121.5 | ok |
| `cctv/most_blown.jpg` | `start=[500, 120], end=[340, 260]` | 0.2 | [362, 640, 3] uint8 mean 138.11 | ok |
| `cctv/sharpest.jpg` | `start=[500, 120], end=[340, 260]` | 0.2 | [362, 640, 3] uint8 mean 131.76 | ok |
| `cctv/softest.jpg` | `start=[500, 120], end=[340, 260]` | 0.2 | [362, 640, 3] uint8 mean 125.46 | ok |

## Artifacts

Outputs written to `validation/artifacts/arrow/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
