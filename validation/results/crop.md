# crop - validation result

**Crop to x, y, width, height**  
`cv_tools.filters.crop_resize` | family: Adjust | 2026-09-01T16:34:49

## Verdict

**PASS** - 9 runs, no invariant broken, 3 specific checks passed.

## What this filter specifically promises

- PASS - crop returns exactly the region asked for: 200x140 for a 200x140 request
- PASS - the cropped pixels are the pixels that were there: identical to the same slice of the input
- PASS - a region entirely outside the frame is refused: crop raises where roi_crop would clip

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `x=120, y=80, width=200, height=140` | 0.0 | [140, 200, 3] uint8 mean 161.8 | ok |
| `cctv/darkest.jpg` | `x=120, y=80, width=200, height=140` | 0.0 | [140, 200, 3] uint8 mean 138.63 | ok |
| `cctv/event_fall.jpg` | `x=120, y=80, width=200, height=140` | 0.0 | [140, 200, 3] uint8 mean 119.01 | ok |
| `cctv/event_optflow.jpg` | `x=120, y=80, width=200, height=140` | 0.0 | [140, 200, 3] uint8 mean 126.91 | ok |
| `cctv/event_tamper.jpg` | `x=120, y=80, width=200, height=140` | 0.0 | [140, 200, 3] uint8 mean 158.93 | ok |
| `cctv/flattest.jpg` | `x=120, y=80, width=200, height=140` | 0.0 | [140, 200, 3] uint8 mean 123.72 | ok |
| `cctv/most_blown.jpg` | `x=120, y=80, width=200, height=140` | 0.0 | [140, 200, 3] uint8 mean 165.09 | ok |
| `cctv/sharpest.jpg` | `x=120, y=80, width=200, height=140` | 0.0 | [140, 200, 3] uint8 mean 150.2 | ok |
| `cctv/softest.jpg` | `x=120, y=80, width=200, height=140` | 0.0 | [140, 200, 3] uint8 mean 123.51 | ok |

## Artifacts

Outputs written to `validation/artifacts/crop/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
