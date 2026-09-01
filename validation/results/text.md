# text - validation result

**Draw a text label on a dark plate**  
`src.filters.annotate` | family: Special | 2026-09-01T16:37:20

## Verdict

**PASS** - 18 runs, no invariant broken.

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `text=exhibit A, position=[60, 60]` | 0.1 | [362, 640, 3] uint8 mean 161.64 | ok |
| `cctv/brightest.jpg` | `text=exhibit A, position=[60, 60], background=False` | 0.1 | [362, 640, 3] uint8 mean 163.59 | ok |
| `cctv/darkest.jpg` | `text=exhibit A, position=[60, 60]` | 0.1 | [362, 640, 3] uint8 mean 109.02 | ok |
| `cctv/darkest.jpg` | `text=exhibit A, position=[60, 60], background=False` | 0.1 | [362, 640, 3] uint8 mean 110.97 | ok |
| `cctv/event_fall.jpg` | `text=exhibit A, position=[60, 60]` | 0.2 | [362, 640, 3] uint8 mean 124.48 | ok |
| `cctv/event_fall.jpg` | `text=exhibit A, position=[60, 60], background=False` | 0.1 | [362, 640, 3] uint8 mean 125.66 | ok |
| `cctv/event_optflow.jpg` | `text=exhibit A, position=[60, 60]` | 0.2 | [362, 640, 3] uint8 mean 124.26 | ok |
| `cctv/event_optflow.jpg` | `text=exhibit A, position=[60, 60], background=False` | 0.1 | [362, 640, 3] uint8 mean 125.55 | ok |
| `cctv/event_tamper.jpg` | `text=exhibit A, position=[60, 60]` | 0.1 | [362, 640, 3] uint8 mean 158.78 | ok |
| `cctv/event_tamper.jpg` | `text=exhibit A, position=[60, 60], background=False` | 0.1 | [362, 640, 3] uint8 mean 160.68 | ok |
| `cctv/flattest.jpg` | `text=exhibit A, position=[60, 60]` | 0.2 | [362, 640, 3] uint8 mean 120.36 | ok |
| `cctv/flattest.jpg` | `text=exhibit A, position=[60, 60], background=False` | 0.2 | [362, 640, 3] uint8 mean 121.63 | ok |
| `cctv/most_blown.jpg` | `text=exhibit A, position=[60, 60]` | 0.1 | [362, 640, 3] uint8 mean 135.92 | ok |
| `cctv/most_blown.jpg` | `text=exhibit A, position=[60, 60], background=False` | 0.1 | [362, 640, 3] uint8 mean 138.11 | ok |
| `cctv/sharpest.jpg` | `text=exhibit A, position=[60, 60]` | 0.1 | [362, 640, 3] uint8 mean 129.69 | ok |
| `cctv/sharpest.jpg` | `text=exhibit A, position=[60, 60], background=False` | 0.2 | [362, 640, 3] uint8 mean 131.79 | ok |
| `cctv/softest.jpg` | `text=exhibit A, position=[60, 60]` | 0.1 | [362, 640, 3] uint8 mean 123.94 | ok |
| `cctv/softest.jpg` | `text=exhibit A, position=[60, 60], background=False` | 0.1 | [362, 640, 3] uint8 mean 125.48 | ok |

## Artifacts

Outputs written to `validation/artifacts/text/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
