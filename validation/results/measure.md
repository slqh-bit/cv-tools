# measure - validation result

**Measure between two points, against a reference of known length in the same plane**  
`cv_tools.filters.annotate` | family: Special | 2026-09-01T16:37:19

## Verdict

**PASS** - 9 runs, no invariant broken.

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `point_a=[180, 300], point_b=[420, 300]` | 0.2 | [362, 640, 3] uint8 mean 162.74 | ok |
| `cctv/darkest.jpg` | `point_a=[180, 300], point_b=[420, 300]` | 0.2 | [362, 640, 3] uint8 mean 110.47 | ok |
| `cctv/event_fall.jpg` | `point_a=[180, 300], point_b=[420, 300]` | 0.2 | [362, 640, 3] uint8 mean 124.47 | ok |
| `cctv/event_optflow.jpg` | `point_a=[180, 300], point_b=[420, 300]` | 0.2 | [362, 640, 3] uint8 mean 124.43 | ok |
| `cctv/event_tamper.jpg` | `point_a=[180, 300], point_b=[420, 300]` | 0.2 | [362, 640, 3] uint8 mean 159.86 | ok |
| `cctv/flattest.jpg` | `point_a=[180, 300], point_b=[420, 300]` | 0.2 | [362, 640, 3] uint8 mean 120.55 | ok |
| `cctv/most_blown.jpg` | `point_a=[180, 300], point_b=[420, 300]` | 0.2 | [362, 640, 3] uint8 mean 137.31 | ok |
| `cctv/sharpest.jpg` | `point_a=[180, 300], point_b=[420, 300]` | 0.2 | [362, 640, 3] uint8 mean 130.96 | ok |
| `cctv/softest.jpg` | `point_a=[180, 300], point_b=[420, 300]` | 0.2 | [362, 640, 3] uint8 mean 124.94 | ok |

## Artifacts

Outputs written to `validation/artifacts/measure/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
