# measure_3d - validation result

**Estimate object height from one view, against a known reference**  
`cv_tools.filters.measure_3d` | family: Special | 2026-09-01T16:37:19

## Verdict

**PASS** - 27 runs, no invariant broken, 4 specific checks passed.

## What this filter specifically promises

- PASS - the reference measured against itself returns its own height: 1800.00mm against a 1800mm reference
- PASS - reports a height and an uncertainty: height 1027mm, uncertainty 14.7mm/px
- PASS - a shorter image height measures shorter: 587mm < 1027mm
- PASS - uncertainty grows towards the horizon: 14.7 -> 132.0 mm/px nearer the horizon

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 1.1 | [362, 640, 3] uint8 mean 157.85 | ok |
| `cctv/brightest.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.9 | [362, 640, 3] uint8 mean 157.91 | ok |
| `cctv/brightest.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.8 | [362, 640, 3] uint8 mean 160.99 | ok |
| `cctv/darkest.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.9 | [362, 640, 3] uint8 mean 108.02 | ok |
| `cctv/darkest.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.9 | [362, 640, 3] uint8 mean 107.99 | ok |
| `cctv/darkest.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.8 | [362, 640, 3] uint8 mean 109.19 | ok |
| `cctv/event_fall.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 1.2 | [362, 640, 3] uint8 mean 122.18 | ok |
| `cctv/event_fall.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.9 | [362, 640, 3] uint8 mean 122.13 | ok |
| `cctv/event_fall.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.8 | [362, 640, 3] uint8 mean 124.44 | ok |
| `cctv/event_optflow.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 1.0 | [362, 640, 3] uint8 mean 122.27 | ok |
| `cctv/event_optflow.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.9 | [362, 640, 3] uint8 mean 122.23 | ok |
| `cctv/event_optflow.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.9 | [362, 640, 3] uint8 mean 124.38 | ok |
| `cctv/event_tamper.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 1.2 | [362, 640, 3] uint8 mean 155.11 | ok |
| `cctv/event_tamper.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.9 | [362, 640, 3] uint8 mean 155.16 | ok |
| `cctv/event_tamper.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.8 | [362, 640, 3] uint8 mean 158.18 | ok |
| `cctv/flattest.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.9 | [362, 640, 3] uint8 mean 118.51 | ok |
| `cctv/flattest.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 1.2 | [362, 640, 3] uint8 mean 118.47 | ok |
| `cctv/flattest.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.9 | [362, 640, 3] uint8 mean 120.52 | ok |
| `cctv/most_blown.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.9 | [362, 640, 3] uint8 mean 133.82 | ok |
| `cctv/most_blown.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 1.6 | [362, 640, 3] uint8 mean 133.82 | ok |
| `cctv/most_blown.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.8 | [362, 640, 3] uint8 mean 135.5 | ok |
| `cctv/sharpest.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.9 | [362, 640, 3] uint8 mean 127.98 | ok |
| `cctv/sharpest.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.9 | [362, 640, 3] uint8 mean 127.98 | ok |
| `cctv/sharpest.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.8 | [362, 640, 3] uint8 mean 129.7 | ok |
| `cctv/softest.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.8 | [362, 640, 3] uint8 mean 121.29 | ok |
| `cctv/softest.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.9 | [362, 640, 3] uint8 mean 121.29 | ok |
| `cctv/softest.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.8 | [362, 640, 3] uint8 mean 123.69 | ok |

## Artifacts

Outputs written to `validation/artifacts/measure_3d/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
