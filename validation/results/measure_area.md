# measure_area - validation result

**Measure the area of a polygon, against a reference of known length in the same plane**  
`cv_tools.filters.annotate` | family: Special | 2026-09-01T16:37:19

## Verdict

**PASS** - 18 runs, no invariant broken.

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `points=[[120, 100], [420, 100], [420, 300], [120, 300]]` | 0.4 | [362, 640, 3] uint8 mean 162.71 | ok |
| `cctv/brightest.jpg` | `points=[[120, 100], [420, 100], [420, 300], [120, 300]], ...` | 0.4 | [362, 640, 3] uint8 mean 162.23 | ok |
| `cctv/darkest.jpg` | `points=[[120, 100], [420, 100], [420, 300], [120, 300]]` | 0.3 | [362, 640, 3] uint8 mean 110.68 | ok |
| `cctv/darkest.jpg` | `points=[[120, 100], [420, 100], [420, 300], [120, 300]], ...` | 0.4 | [362, 640, 3] uint8 mean 110.08 | ok |
| `cctv/event_fall.jpg` | `points=[[120, 100], [420, 100], [420, 300], [120, 300]]` | 0.3 | [362, 640, 3] uint8 mean 125.34 | ok |
| `cctv/event_fall.jpg` | `points=[[120, 100], [420, 100], [420, 300], [120, 300]], ...` | 0.4 | [362, 640, 3] uint8 mean 125.0 | ok |
| `cctv/event_optflow.jpg` | `points=[[120, 100], [420, 100], [420, 300], [120, 300]]` | 0.3 | [362, 640, 3] uint8 mean 125.33 | ok |
| `cctv/event_optflow.jpg` | `points=[[120, 100], [420, 100], [420, 300], [120, 300]], ...` | 0.6 | [362, 640, 3] uint8 mean 124.99 | ok |
| `cctv/event_tamper.jpg` | `points=[[120, 100], [420, 100], [420, 300], [120, 300]]` | 0.3 | [362, 640, 3] uint8 mean 159.89 | ok |
| `cctv/event_tamper.jpg` | `points=[[120, 100], [420, 100], [420, 300], [120, 300]], ...` | 0.4 | [362, 640, 3] uint8 mean 159.42 | ok |
| `cctv/flattest.jpg` | `points=[[120, 100], [420, 100], [420, 300], [120, 300]]` | 0.3 | [362, 640, 3] uint8 mean 121.5 | ok |
| `cctv/flattest.jpg` | `points=[[120, 100], [420, 100], [420, 300], [120, 300]], ...` | 0.6 | [362, 640, 3] uint8 mean 121.17 | ok |
| `cctv/most_blown.jpg` | `points=[[120, 100], [420, 100], [420, 300], [120, 300]]` | 0.3 | [362, 640, 3] uint8 mean 137.02 | ok |
| `cctv/most_blown.jpg` | `points=[[120, 100], [420, 100], [420, 300], [120, 300]], ...` | 0.4 | [362, 640, 3] uint8 mean 136.26 | ok |
| `cctv/sharpest.jpg` | `points=[[120, 100], [420, 100], [420, 300], [120, 300]]` | 0.3 | [362, 640, 3] uint8 mean 130.9 | ok |
| `cctv/sharpest.jpg` | `points=[[120, 100], [420, 100], [420, 300], [120, 300]], ...` | 0.6 | [362, 640, 3] uint8 mean 130.27 | ok |
| `cctv/softest.jpg` | `points=[[120, 100], [420, 100], [420, 300], [120, 300]]` | 0.3 | [362, 640, 3] uint8 mean 125.34 | ok |
| `cctv/softest.jpg` | `points=[[120, 100], [420, 100], [420, 300], [120, 300]], ...` | 0.4 | [362, 640, 3] uint8 mean 124.96 | ok |

## Artifacts

Outputs written to `validation/artifacts/measure_area/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
