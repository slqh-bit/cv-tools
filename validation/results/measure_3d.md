# measure_3d - validation result

**Estimate object height from one view, against a known reference**  
`src.filters.measure_3d` | family: Special | 2026-08-21T12:46:51

## Verdict

**PASS** - 18 runs, no invariant broken, 4 specific checks passed.

## What this filter specifically promises

- PASS - the reference measured against itself returns its own height: 1800.00mm against a 1800mm reference
- PASS - reports a height and an uncertainty: height 1027mm, uncertainty 14.7mm/px
- PASS - a shorter image height measures shorter: 587mm < 1027mm
- PASS - uncertainty grows towards the horizon: 14.7 -> 132.0 mm/px nearer the horizon

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.8 | [362, 640, 3] uint8 mean 160.99 | ok |
| `cctv/brightest.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.6 | [362, 640, 3] uint8 mean 161.05 | ok |
| `cctv/darkest.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.6 | [362, 640, 3] uint8 mean 109.19 | ok |
| `cctv/darkest.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.6 | [362, 640, 3] uint8 mean 109.16 | ok |
| `cctv/event_fall.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.6 | [362, 640, 3] uint8 mean 124.44 | ok |
| `cctv/event_fall.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.6 | [362, 640, 3] uint8 mean 124.39 | ok |
| `cctv/event_optflow.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.7 | [362, 640, 3] uint8 mean 124.38 | ok |
| `cctv/event_optflow.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.6 | [362, 640, 3] uint8 mean 124.34 | ok |
| `cctv/event_tamper.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.6 | [362, 640, 3] uint8 mean 158.18 | ok |
| `cctv/event_tamper.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.6 | [362, 640, 3] uint8 mean 158.23 | ok |
| `cctv/flattest.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.7 | [362, 640, 3] uint8 mean 120.52 | ok |
| `cctv/flattest.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.6 | [362, 640, 3] uint8 mean 120.47 | ok |
| `cctv/most_blown.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.6 | [362, 640, 3] uint8 mean 135.5 | ok |
| `cctv/most_blown.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.6 | [362, 640, 3] uint8 mean 135.51 | ok |
| `cctv/sharpest.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.6 | [362, 640, 3] uint8 mean 129.7 | ok |
| `cctv/sharpest.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.6 | [362, 640, 3] uint8 mean 129.7 | ok |
| `cctv/softest.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.7 | [362, 640, 3] uint8 mean 123.69 | ok |
| `cctv/softest.jpg` | `base=[320, 400], top=[320, 200], reference_base=[200, 400...` | 0.6 | [362, 640, 3] uint8 mean 123.68 | ok |

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
