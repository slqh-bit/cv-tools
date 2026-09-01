# scale_bar - validation result

**Draw a calibrated scale bar, so sizes can be read off directly**  
`src.filters.annotate` | family: Special | 2026-09-01T16:37:19

## Verdict

**PASS** - 45 runs, no invariant broken.

9 run(s) refused bad parameters with a clear message, which is the wanted behaviour.

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `reference_a=[180, 180], reference_b=[380, 180], reference_length=520.0, length_units=1.0` on `cctv/brightest.jpg`: refused: A 1.0 mm bar is only 0px at this scale; choose a larger length
- `reference_a=[180, 180], reference_b=[380, 180], reference_length=520.0, length_units=1.0` on `cctv/darkest.jpg`: refused: A 1.0 mm bar is only 0px at this scale; choose a larger length
- `reference_a=[180, 180], reference_b=[380, 180], reference_length=520.0, length_units=1.0` on `cctv/event_fall.jpg`: refused: A 1.0 mm bar is only 0px at this scale; choose a larger length
- `reference_a=[180, 180], reference_b=[380, 180], reference_length=520.0, length_units=1.0` on `cctv/event_optflow.jpg`: refused: A 1.0 mm bar is only 0px at this scale; choose a larger length
- `reference_a=[180, 180], reference_b=[380, 180], reference_length=520.0, length_units=1.0` on `cctv/event_tamper.jpg`: refused: A 1.0 mm bar is only 0px at this scale; choose a larger length
- `reference_a=[180, 180], reference_b=[380, 180], reference_length=520.0, length_units=1.0` on `cctv/flattest.jpg`: refused: A 1.0 mm bar is only 0px at this scale; choose a larger length
- `reference_a=[180, 180], reference_b=[380, 180], reference_length=520.0, length_units=1.0` on `cctv/most_blown.jpg`: refused: A 1.0 mm bar is only 0px at this scale; choose a larger length
- `reference_a=[180, 180], reference_b=[380, 180], reference_length=520.0, length_units=1.0` on `cctv/sharpest.jpg`: refused: A 1.0 mm bar is only 0px at this scale; choose a larger length
- `reference_a=[180, 180], reference_b=[380, 180], reference_length=520.0, length_units=1.0` on `cctv/softest.jpg`: refused: A 1.0 mm bar is only 0px at this scale; choose a larger length

## Refused parameters

Rejected on purpose, with the message the user would see.

- `reference_a=[180, 180], reference_b=[380, 180], reference_length=520.0, length_units=1.0` -> ValueError: A 1.0 mm bar is only 0px at this scale; choose a larger length

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.2 | [362, 640, 3] uint8 mean 162.71 | ok |
| `cctv/brightest.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.0 | - | refused: ValueError: A 1.0 mm bar is only 0px at this scale; choose a larger len |
| `cctv/brightest.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.1 | [362, 640, 3] uint8 mean 155.85 | ok |
| `cctv/brightest.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.1 | [362, 640, 3] uint8 mean 162.41 | ok |
| `cctv/brightest.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.1 | [362, 640, 3] uint8 mean 162.43 | ok |
| `cctv/darkest.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.2 | [362, 640, 3] uint8 mean 110.54 | ok |
| `cctv/darkest.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.0 | - | refused: ValueError: A 1.0 mm bar is only 0px at this scale; choose a larger len |
| `cctv/darkest.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.1 | [362, 640, 3] uint8 mean 107.82 | ok |
| `cctv/darkest.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.1 | [362, 640, 3] uint8 mean 110.62 | ok |
| `cctv/darkest.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.2 | [362, 640, 3] uint8 mean 110.75 | ok |
| `cctv/event_fall.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.2 | [362, 640, 3] uint8 mean 125.14 | ok |
| `cctv/event_fall.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.0 | - | refused: ValueError: A 1.0 mm bar is only 0px at this scale; choose a larger len |
| `cctv/event_fall.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.1 | [362, 640, 3] uint8 mean 120.12 | ok |
| `cctv/event_fall.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.1 | [362, 640, 3] uint8 mean 125.39 | ok |
| `cctv/event_fall.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.1 | [362, 640, 3] uint8 mean 125.25 | ok |
| `cctv/event_optflow.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.2 | [362, 640, 3] uint8 mean 125.04 | ok |
| `cctv/event_optflow.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.0 | - | refused: ValueError: A 1.0 mm bar is only 0px at this scale; choose a larger len |
| `cctv/event_optflow.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.1 | [362, 640, 3] uint8 mean 120.17 | ok |
| `cctv/event_optflow.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.1 | [362, 640, 3] uint8 mean 125.47 | ok |
| `cctv/event_optflow.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.1 | [362, 640, 3] uint8 mean 125.1 | ok |
| `cctv/event_tamper.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.2 | [362, 640, 3] uint8 mean 159.82 | ok |
| `cctv/event_tamper.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.0 | - | refused: ValueError: A 1.0 mm bar is only 0px at this scale; choose a larger len |
| `cctv/event_tamper.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.1 | [362, 640, 3] uint8 mean 153.09 | ok |
| `cctv/event_tamper.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.1 | [362, 640, 3] uint8 mean 159.57 | ok |
| `cctv/event_tamper.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.1 | [362, 640, 3] uint8 mean 159.53 | ok |
| `cctv/flattest.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.2 | [362, 640, 3] uint8 mean 121.15 | ok |
| `cctv/flattest.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.0 | - | refused: ValueError: A 1.0 mm bar is only 0px at this scale; choose a larger len |
| `cctv/flattest.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.1 | [362, 640, 3] uint8 mean 116.39 | ok |
| `cctv/flattest.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.1 | [362, 640, 3] uint8 mean 121.56 | ok |
| `cctv/flattest.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.1 | [362, 640, 3] uint8 mean 121.21 | ok |
| `cctv/most_blown.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.2 | [362, 640, 3] uint8 mean 137.47 | ok |
| `cctv/most_blown.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.0 | - | refused: ValueError: A 1.0 mm bar is only 0px at this scale; choose a larger len |
| `cctv/most_blown.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.1 | [362, 640, 3] uint8 mean 133.3 | ok |
| `cctv/most_blown.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.1 | [362, 640, 3] uint8 mean 137.54 | ok |
| `cctv/most_blown.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.1 | [362, 640, 3] uint8 mean 137.74 | ok |
| `cctv/sharpest.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.2 | [362, 640, 3] uint8 mean 131.07 | ok |
| `cctv/sharpest.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.0 | - | refused: ValueError: A 1.0 mm bar is only 0px at this scale; choose a larger len |
| `cctv/sharpest.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.1 | [362, 640, 3] uint8 mean 127.21 | ok |
| `cctv/sharpest.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.1 | [362, 640, 3] uint8 mean 131.34 | ok |
| `cctv/sharpest.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.1 | [362, 640, 3] uint8 mean 131.3 | ok |
| `cctv/softest.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.2 | [362, 640, 3] uint8 mean 124.9 | ok |
| `cctv/softest.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.0 | - | refused: ValueError: A 1.0 mm bar is only 0px at this scale; choose a larger len |
| `cctv/softest.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.1 | [362, 640, 3] uint8 mean 120.3 | ok |
| `cctv/softest.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.2 | [362, 640, 3] uint8 mean 124.77 | ok |
| `cctv/softest.jpg` | `reference_a=[180, 180], reference_b=[380, 180], reference...` | 0.1 | [362, 640, 3] uint8 mean 124.6 | ok |

## Artifacts

Outputs written to `validation/artifacts/scale_bar/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
