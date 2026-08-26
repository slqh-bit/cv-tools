# auto_contrast - validation result

**Automatic histogram stretch on luminance**  
`src.filters.contrast_brightness` | family: Adjust | 2026-08-21T12:44:34

## Verdict

**PASS** - 27 runs, no invariant broken.

9 run(s) refused bad parameters with a clear message, which is the wanted behaviour.

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `cutoff=200.0` on `cctv/brightest.jpg`: refused: Percentiles must be in the range [0, 100]
- `cutoff=200.0` on `cctv/darkest.jpg`: refused: Percentiles must be in the range [0, 100]
- `cutoff=200.0` on `cctv/event_fall.jpg`: refused: Percentiles must be in the range [0, 100]
- `cutoff=200.0` on `cctv/event_optflow.jpg`: refused: Percentiles must be in the range [0, 100]
- `cutoff=200.0` on `cctv/event_tamper.jpg`: refused: Percentiles must be in the range [0, 100]
- `cutoff=200.0` on `cctv/flattest.jpg`: refused: Percentiles must be in the range [0, 100]
- `cutoff=200.0` on `cctv/most_blown.jpg`: refused: Percentiles must be in the range [0, 100]
- `cutoff=200.0` on `cctv/sharpest.jpg`: refused: Percentiles must be in the range [0, 100]
- `cutoff=200.0` on `cctv/softest.jpg`: refused: Percentiles must be in the range [0, 100]

## Refused parameters

Rejected on purpose, with the message the user would see.

- `cutoff=200.0` -> ValueError: Percentiles must be in the range [0, 100]

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 2.1 | [362, 640, 3] uint8 mean 162.56 | ok |
| `cctv/brightest.jpg` | `cutoff=1.0` | 2.4 | [362, 640, 3] uint8 mean 155.03 | ok |
| `cctv/brightest.jpg` | `cutoff=200.0` | 0.0 | - | refused: ValueError: Percentiles must be in the range [0, 100] |
| `cctv/darkest.jpg` | `defaults` | 2.1 | [362, 640, 3] uint8 mean 110.95 | ok |
| `cctv/darkest.jpg` | `cutoff=1.0` | 2.7 | [362, 640, 3] uint8 mean 92.92 | ok |
| `cctv/darkest.jpg` | `cutoff=200.0` | 0.0 | - | refused: ValueError: Percentiles must be in the range [0, 100] |
| `cctv/event_fall.jpg` | `defaults` | 2.2 | [362, 640, 3] uint8 mean 125.49 | ok |
| `cctv/event_fall.jpg` | `cutoff=1.0` | 3.0 | [362, 640, 3] uint8 mean 123.52 | ok |
| `cctv/event_fall.jpg` | `cutoff=200.0` | 0.0 | - | refused: ValueError: Percentiles must be in the range [0, 100] |
| `cctv/event_optflow.jpg` | `defaults` | 2.2 | [362, 640, 3] uint8 mean 124.4 | ok |
| `cctv/event_optflow.jpg` | `cutoff=1.0` | 2.6 | [362, 640, 3] uint8 mean 111.08 | ok |
| `cctv/event_optflow.jpg` | `cutoff=200.0` | 0.0 | - | refused: ValueError: Percentiles must be in the range [0, 100] |
| `cctv/event_tamper.jpg` | `defaults` | 2.1 | [362, 640, 3] uint8 mean 160.61 | ok |
| `cctv/event_tamper.jpg` | `cutoff=1.0` | 3.0 | [362, 640, 3] uint8 mean 152.36 | ok |
| `cctv/event_tamper.jpg` | `cutoff=200.0` | 0.0 | - | refused: ValueError: Percentiles must be in the range [0, 100] |
| `cctv/flattest.jpg` | `defaults` | 2.2 | [362, 640, 3] uint8 mean 121.45 | ok |
| `cctv/flattest.jpg` | `cutoff=1.0` | 2.7 | [362, 640, 3] uint8 mean 106.64 | ok |
| `cctv/flattest.jpg` | `cutoff=200.0` | 0.0 | - | refused: ValueError: Percentiles must be in the range [0, 100] |
| `cctv/most_blown.jpg` | `defaults` | 2.2 | [362, 640, 3] uint8 mean 138.09 | ok |
| `cctv/most_blown.jpg` | `cutoff=1.0` | 2.9 | [362, 640, 3] uint8 mean 119.08 | ok |
| `cctv/most_blown.jpg` | `cutoff=200.0` | 0.0 | - | refused: ValueError: Percentiles must be in the range [0, 100] |
| `cctv/sharpest.jpg` | `defaults` | 2.2 | [362, 640, 3] uint8 mean 131.76 | ok |
| `cctv/sharpest.jpg` | `cutoff=1.0` | 2.7 | [362, 640, 3] uint8 mean 130.32 | ok |
| `cctv/sharpest.jpg` | `cutoff=200.0` | 0.0 | - | refused: ValueError: Percentiles must be in the range [0, 100] |
| `cctv/softest.jpg` | `defaults` | 2.6 | [362, 640, 3] uint8 mean 125.39 | ok |
| `cctv/softest.jpg` | `cutoff=1.0` | 2.8 | [362, 640, 3] uint8 mean 136.72 | ok |
| `cctv/softest.jpg` | `cutoff=200.0` | 0.0 | - | refused: ValueError: Percentiles must be in the range [0, 100] |

## Artifacts

Outputs written to `validation/artifacts/auto_contrast/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
