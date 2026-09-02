# deblock - validation result

**Soften JPEG block edges**  
`cv_tools.filters.compression_analysis` | family: Analyze | 2026-09-01T16:35:59

## Verdict

**PASS** - 27 runs, no invariant broken, 1 specific checks passed.

9 run(s) refused bad parameters with a clear message, which is the wanted behaviour.

## What this filter specifically promises

- PASS - lowers the blocking it was given: blockiness 5.01 -> 3.78 on a Q25 frame

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
| `cctv/brightest.jpg` | `defaults` | 12.2 | [362, 640, 3] uint8 mean 163.18 | ok |
| `cctv/brightest.jpg` | `strength=0.0` | 0.1 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/brightest.jpg` | `strength=2.0` | 0.0 | - | refused: ValueError: strength must be between 0 and 1, got 2.0 |
| `cctv/darkest.jpg` | `defaults` | 12.0 | [362, 640, 3] uint8 mean 110.61 | ok |
| `cctv/darkest.jpg` | `strength=0.0` | 0.1 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/darkest.jpg` | `strength=2.0` | 0.0 | - | refused: ValueError: strength must be between 0 and 1, got 2.0 |
| `cctv/event_fall.jpg` | `defaults` | 11.3 | [362, 640, 3] uint8 mean 125.11 | ok |
| `cctv/event_fall.jpg` | `strength=0.0` | 0.1 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_fall.jpg` | `strength=2.0` | 0.0 | - | refused: ValueError: strength must be between 0 and 1, got 2.0 |
| `cctv/event_optflow.jpg` | `defaults` | 11.7 | [362, 640, 3] uint8 mean 125.08 | ok |
| `cctv/event_optflow.jpg` | `strength=0.0` | 0.1 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_optflow.jpg` | `strength=2.0` | 0.0 | - | refused: ValueError: strength must be between 0 and 1, got 2.0 |
| `cctv/event_tamper.jpg` | `defaults` | 12.4 | [362, 640, 3] uint8 mean 160.27 | ok |
| `cctv/event_tamper.jpg` | `strength=0.0` | 0.1 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/event_tamper.jpg` | `strength=2.0` | 0.0 | - | refused: ValueError: strength must be between 0 and 1, got 2.0 |
| `cctv/flattest.jpg` | `defaults` | 12.0 | [362, 640, 3] uint8 mean 121.17 | ok |
| `cctv/flattest.jpg` | `strength=0.0` | 0.1 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/flattest.jpg` | `strength=2.0` | 0.0 | - | refused: ValueError: strength must be between 0 and 1, got 2.0 |
| `cctv/most_blown.jpg` | `defaults` | 11.0 | [362, 640, 3] uint8 mean 137.76 | ok |
| `cctv/most_blown.jpg` | `strength=0.0` | 0.1 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/most_blown.jpg` | `strength=2.0` | 0.0 | - | refused: ValueError: strength must be between 0 and 1, got 2.0 |
| `cctv/sharpest.jpg` | `defaults` | 11.9 | [362, 640, 3] uint8 mean 131.36 | ok |
| `cctv/sharpest.jpg` | `strength=0.0` | 0.1 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/sharpest.jpg` | `strength=2.0` | 0.0 | - | refused: ValueError: strength must be between 0 and 1, got 2.0 |
| `cctv/softest.jpg` | `defaults` | 11.4 | [362, 640, 3] uint8 mean 125.05 | ok |
| `cctv/softest.jpg` | `strength=0.0` | 0.1 | [362, 640, 3] uint8 mean 125.38 | output identical to input |
| `cctv/softest.jpg` | `strength=2.0` | 0.0 | - | refused: ValueError: strength must be between 0 and 1, got 2.0 |

## Artifacts

Outputs written to `validation/artifacts/deblock/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
