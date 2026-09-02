# s_curve - validation result

**Symmetric S-curve contrast**  
`cv_tools.filters.curves` | family: Adjust | 2026-09-01T16:34:50

## Verdict

**PASS** - 27 runs, no invariant broken.

9 run(s) refused bad parameters with a clear message, which is the wanted behaviour.

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `strength=0.0` on `cctv/brightest.jpg`: output identical to input
- `strength=2.0` on `cctv/brightest.jpg`: refused: strength must be between 0 and 1, got 2.0
- `strength=0.0` on `cctv/darkest.jpg`: output identical to input
- `strength=2.0` on `cctv/darkest.jpg`: refused: strength must be between 0 and 1, got 2.0
- `strength=0.0` on `cctv/event_fall.jpg`: output identical to input
- `strength=2.0` on `cctv/event_fall.jpg`: refused: strength must be between 0 and 1, got 2.0
- `strength=0.0` on `cctv/event_optflow.jpg`: output identical to input
- `strength=2.0` on `cctv/event_optflow.jpg`: refused: strength must be between 0 and 1, got 2.0
- `strength=0.0` on `cctv/event_tamper.jpg`: output identical to input
- `strength=2.0` on `cctv/event_tamper.jpg`: refused: strength must be between 0 and 1, got 2.0
- `strength=0.0` on `cctv/flattest.jpg`: output identical to input
- `strength=2.0` on `cctv/flattest.jpg`: refused: strength must be between 0 and 1, got 2.0

## Refused parameters

Rejected on purpose, with the message the user would see.

- `strength=2.0` -> ValueError: strength must be between 0 and 1, got 2.0

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 0.8 | [362, 640, 3] uint8 mean 165.88 | ok |
| `cctv/brightest.jpg` | `strength=0.0` | 1.0 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/brightest.jpg` | `strength=2.0` | 0.0 | - | refused: ValueError: strength must be between 0 and 1, got 2.0 |
| `cctv/darkest.jpg` | `defaults` | 0.7 | [362, 640, 3] uint8 mean 105.39 | ok |
| `cctv/darkest.jpg` | `strength=0.0` | 0.8 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/darkest.jpg` | `strength=2.0` | 0.0 | - | refused: ValueError: strength must be between 0 and 1, got 2.0 |
| `cctv/event_fall.jpg` | `defaults` | 0.7 | [362, 640, 3] uint8 mean 125.06 | ok |
| `cctv/event_fall.jpg` | `strength=0.0` | 0.8 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_fall.jpg` | `strength=2.0` | 0.0 | - | refused: ValueError: strength must be between 0 and 1, got 2.0 |
| `cctv/event_optflow.jpg` | `defaults` | 0.7 | [362, 640, 3] uint8 mean 124.74 | ok |
| `cctv/event_optflow.jpg` | `strength=0.0` | 0.8 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_optflow.jpg` | `strength=2.0` | 0.0 | - | refused: ValueError: strength must be between 0 and 1, got 2.0 |
| `cctv/event_tamper.jpg` | `defaults` | 0.8 | [362, 640, 3] uint8 mean 163.09 | ok |
| `cctv/event_tamper.jpg` | `strength=0.0` | 0.8 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/event_tamper.jpg` | `strength=2.0` | 0.0 | - | refused: ValueError: strength must be between 0 and 1, got 2.0 |
| `cctv/flattest.jpg` | `defaults` | 0.9 | [362, 640, 3] uint8 mean 119.89 | ok |
| `cctv/flattest.jpg` | `strength=0.0` | 1.1 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/flattest.jpg` | `strength=2.0` | 0.0 | - | refused: ValueError: strength must be between 0 and 1, got 2.0 |
| `cctv/most_blown.jpg` | `defaults` | 1.0 | [362, 640, 3] uint8 mean 137.45 | ok |
| `cctv/most_blown.jpg` | `strength=0.0` | 1.2 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/most_blown.jpg` | `strength=2.0` | 0.0 | - | refused: ValueError: strength must be between 0 and 1, got 2.0 |
| `cctv/sharpest.jpg` | `defaults` | 2.9 | [362, 640, 3] uint8 mean 131.39 | ok |
| `cctv/sharpest.jpg` | `strength=0.0` | 0.8 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/sharpest.jpg` | `strength=2.0` | 0.0 | - | refused: ValueError: strength must be between 0 and 1, got 2.0 |
| `cctv/softest.jpg` | `defaults` | 0.9 | [362, 640, 3] uint8 mean 125.15 | ok |
| `cctv/softest.jpg` | `strength=0.0` | 0.8 | [362, 640, 3] uint8 mean 125.38 | output identical to input |
| `cctv/softest.jpg` | `strength=2.0` | 0.0 | - | refused: ValueError: strength must be between 0 and 1, got 2.0 |

## Artifacts

Outputs written to `validation/artifacts/s_curve/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
