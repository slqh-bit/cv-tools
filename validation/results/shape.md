# shape - validation result

**Draw a rectangle, circle, ellipse, line or polygon**  
`src.filters.annotate` | family: Special | 2026-09-01T16:37:20

## Verdict

**PASS** - 9 runs, no invariant broken.

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `shape=rectangle, points=[[80, 60], [420, 320]]` | 0.2 | [362, 640, 3] uint8 mean 162.64 | ok |
| `cctv/darkest.jpg` | `shape=rectangle, points=[[80, 60], [420, 320]]` | 0.3 | [362, 640, 3] uint8 mean 110.81 | ok |
| `cctv/event_fall.jpg` | `shape=rectangle, points=[[80, 60], [420, 320]]` | 0.3 | [362, 640, 3] uint8 mean 125.16 | ok |
| `cctv/event_optflow.jpg` | `shape=rectangle, points=[[80, 60], [420, 320]]` | 0.2 | [362, 640, 3] uint8 mean 125.18 | ok |
| `cctv/event_tamper.jpg` | `shape=rectangle, points=[[80, 60], [420, 320]]` | 0.2 | [362, 640, 3] uint8 mean 159.79 | ok |
| `cctv/flattest.jpg` | `shape=rectangle, points=[[80, 60], [420, 320]]` | 0.2 | [362, 640, 3] uint8 mean 121.33 | ok |
| `cctv/most_blown.jpg` | `shape=rectangle, points=[[80, 60], [420, 320]]` | 0.2 | [362, 640, 3] uint8 mean 137.4 | ok |
| `cctv/sharpest.jpg` | `shape=rectangle, points=[[80, 60], [420, 320]]` | 0.4 | [362, 640, 3] uint8 mean 131.32 | ok |
| `cctv/softest.jpg` | `shape=rectangle, points=[[80, 60], [420, 320]]` | 0.2 | [362, 640, 3] uint8 mean 125.21 | ok |

## Artifacts

Outputs written to `validation/artifacts/shape/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
