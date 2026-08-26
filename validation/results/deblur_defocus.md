# deblur_defocus - validation result

**Wiener deconvolution of defocus blur**  
`src.filters.motion_deblur` | family: Forensic | 2026-08-21T12:46:36

## Verdict

**PASS** - 50 runs, no invariant broken, 1 specific checks passed.

10 run(s) refused bad parameters with a clear message, which is the wanted behaviour.

## What this filter specifically promises

- PASS - some radius raises high-frequency energy on defocused text: Laplacian variance 11 -> 191 over radius 3-12

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `radius=0.1` on `cctv/brightest.jpg`: refused: radius must be at least 1, got 0.1
- `radius=0.1` on `cctv/darkest.jpg`: refused: radius must be at least 1, got 0.1
- `radius=0.1` on `cctv/event_fall.jpg`: refused: radius must be at least 1, got 0.1
- `radius=0.1` on `cctv/event_optflow.jpg`: refused: radius must be at least 1, got 0.1
- `radius=0.1` on `cctv/event_tamper.jpg`: refused: radius must be at least 1, got 0.1
- `radius=0.1` on `cctv/flattest.jpg`: refused: radius must be at least 1, got 0.1
- `radius=0.1` on `cctv/most_blown.jpg`: refused: radius must be at least 1, got 0.1
- `radius=0.1` on `cctv/sharpest.jpg`: refused: radius must be at least 1, got 0.1
- `radius=0.1` on `cctv/softest.jpg`: refused: radius must be at least 1, got 0.1
- `radius=0.1` on `reference/defocus_text.jpg`: refused: radius must be at least 1, got 0.1

## Refused parameters

Rejected on purpose, with the message the user would see.

- `radius=0.1` -> ValueError: radius must be at least 1, got 0.1

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 131.2 | [362, 640, 3] uint8 mean 159.49 | ok |
| `cctv/brightest.jpg` | `radius=0.1` | 0.0 | - | refused: ValueError: radius must be at least 1, got 0.1 |
| `cctv/brightest.jpg` | `radius=50.0` | 322.2 | [362, 640, 3] uint8 mean 157.92 | ok |
| `cctv/brightest.jpg` | `noise_power=0.0001` | 128.3 | [362, 640, 3] uint8 mean 142.19 | ok |
| `cctv/brightest.jpg` | `noise_power=0.5` | 128.7 | [362, 640, 3] uint8 mean 108.65 | ok |
| `cctv/darkest.jpg` | `defaults` | 129.1 | [362, 640, 3] uint8 mean 108.61 | ok |
| `cctv/darkest.jpg` | `radius=0.1` | 0.0 | - | refused: ValueError: radius must be at least 1, got 0.1 |
| `cctv/darkest.jpg` | `radius=50.0` | 326.9 | [362, 640, 3] uint8 mean 108.23 | ok |
| `cctv/darkest.jpg` | `noise_power=0.0001` | 131.8 | [362, 640, 3] uint8 mean 118.12 | ok |
| `cctv/darkest.jpg` | `noise_power=0.5` | 130.9 | [362, 640, 3] uint8 mean 73.55 | ok |
| `cctv/event_fall.jpg` | `defaults` | 129.6 | [362, 640, 3] uint8 mean 123.63 | ok |
| `cctv/event_fall.jpg` | `radius=0.1` | 0.0 | - | refused: ValueError: radius must be at least 1, got 0.1 |
| `cctv/event_fall.jpg` | `radius=50.0` | 324.2 | [362, 640, 3] uint8 mean 124.57 | ok |
| `cctv/event_fall.jpg` | `noise_power=0.0001` | 128.7 | [362, 640, 3] uint8 mean 126.41 | ok |
| `cctv/event_fall.jpg` | `noise_power=0.5` | 129.5 | [362, 640, 3] uint8 mean 83.34 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 128.2 | [362, 640, 3] uint8 mean 123.25 | ok |
| `cctv/event_optflow.jpg` | `radius=0.1` | 0.0 | - | refused: ValueError: radius must be at least 1, got 0.1 |
| `cctv/event_optflow.jpg` | `radius=50.0` | 320.4 | [362, 640, 3] uint8 mean 124.16 | ok |
| `cctv/event_optflow.jpg` | `noise_power=0.0001` | 128.4 | [362, 640, 3] uint8 mean 125.2 | ok |
| `cctv/event_optflow.jpg` | `noise_power=0.5` | 129.9 | [362, 640, 3] uint8 mean 83.23 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 129.9 | [362, 640, 3] uint8 mean 156.78 | ok |
| `cctv/event_tamper.jpg` | `radius=0.1` | 0.0 | - | refused: ValueError: radius must be at least 1, got 0.1 |
| `cctv/event_tamper.jpg` | `radius=50.0` | 345.5 | [362, 640, 3] uint8 mean 155.59 | ok |
| `cctv/event_tamper.jpg` | `noise_power=0.0001` | 128.8 | [362, 640, 3] uint8 mean 141.18 | ok |
| `cctv/event_tamper.jpg` | `noise_power=0.5` | 128.8 | [362, 640, 3] uint8 mean 106.71 | ok |
| `cctv/flattest.jpg` | `defaults` | 129.4 | [362, 640, 3] uint8 mean 119.49 | ok |
| `cctv/flattest.jpg` | `radius=0.1` | 0.0 | - | refused: ValueError: radius must be at least 1, got 0.1 |
| `cctv/flattest.jpg` | `radius=50.0` | 323.7 | [362, 640, 3] uint8 mean 120.82 | ok |
| `cctv/flattest.jpg` | `noise_power=0.0001` | 129.8 | [362, 640, 3] uint8 mean 123.31 | ok |
| `cctv/flattest.jpg` | `noise_power=0.5` | 129.8 | [362, 640, 3] uint8 mean 80.61 | ok |
| `cctv/most_blown.jpg` | `defaults` | 129.4 | [362, 640, 3] uint8 mean 134.88 | ok |
| `cctv/most_blown.jpg` | `radius=0.1` | 0.0 | - | refused: ValueError: radius must be at least 1, got 0.1 |
| `cctv/most_blown.jpg` | `radius=50.0` | 321.9 | [362, 640, 3] uint8 mean 132.87 | ok |
| `cctv/most_blown.jpg` | `noise_power=0.0001` | 129.4 | [362, 640, 3] uint8 mean 130.76 | ok |
| `cctv/most_blown.jpg` | `noise_power=0.5` | 129.4 | [362, 640, 3] uint8 mean 91.67 | ok |
| `cctv/sharpest.jpg` | `defaults` | 128.6 | [362, 640, 3] uint8 mean 130.01 | ok |
| `cctv/sharpest.jpg` | `radius=0.1` | 0.0 | - | refused: ValueError: radius must be at least 1, got 0.1 |
| `cctv/sharpest.jpg` | `radius=50.0` | 328.5 | [362, 640, 3] uint8 mean 126.93 | ok |
| `cctv/sharpest.jpg` | `noise_power=0.0001` | 130.6 | [362, 640, 3] uint8 mean 128.04 | ok |
| `cctv/sharpest.jpg` | `noise_power=0.5` | 130.5 | [362, 640, 3] uint8 mean 87.46 | ok |
| `cctv/softest.jpg` | `defaults` | 130.0 | [362, 640, 3] uint8 mean 123.75 | ok |
| `cctv/softest.jpg` | `radius=0.1` | 0.0 | - | refused: ValueError: radius must be at least 1, got 0.1 |
| `cctv/softest.jpg` | `radius=50.0` | 323.4 | [362, 640, 3] uint8 mean 125.99 | ok |
| `cctv/softest.jpg` | `noise_power=0.0001` | 129.6 | [362, 640, 3] uint8 mean 126.39 | ok |
| `cctv/softest.jpg` | `noise_power=0.5` | 130.1 | [362, 640, 3] uint8 mean 83.19 | ok |
| `reference/defocus_text.jpg` | `defaults` | 193.3 | [472, 697, 3] uint8 mean 177.06 | ok |
| `reference/defocus_text.jpg` | `radius=0.1` | 0.0 | - | refused: ValueError: radius must be at least 1, got 0.1 |
| `reference/defocus_text.jpg` | `radius=50.0` | 379.1 | [472, 697, 3] uint8 mean 177.05 | ok |
| `reference/defocus_text.jpg` | `noise_power=0.0001` | 191.3 | [472, 697, 3] uint8 mean 178.37 | ok |
| `reference/defocus_text.jpg` | `noise_power=0.5` | 190.5 | [472, 697, 3] uint8 mean 119.06 | ok |

## Artifacts

Outputs written to `validation/artifacts/deblur_defocus/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
- `reference_defocus_text.png`
