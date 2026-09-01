# fit_aspect - validation result

**Pad, crop or stretch to a display aspect ratio**  
`src.filters.aspect_ratio` | family: Correct | 2026-09-01T16:35:56

## Verdict

**PASS** - 45 runs, no invariant broken.

9 run(s) refused bad parameters with a clear message, which is the wanted behaviour.

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `target_ratio=1.7777777777777777, interpolation=auto` on `cctv/brightest.jpg`: refused: Unknown interpolation 'auto'. Available: area, bicubic, bilinear, lanczos, nearest
- `target_ratio=1.7777777777777777, interpolation=auto` on `cctv/darkest.jpg`: refused: Unknown interpolation 'auto'. Available: area, bicubic, bilinear, lanczos, nearest
- `target_ratio=1.7777777777777777, interpolation=auto` on `cctv/event_fall.jpg`: refused: Unknown interpolation 'auto'. Available: area, bicubic, bilinear, lanczos, nearest
- `target_ratio=1.7777777777777777, interpolation=auto` on `cctv/event_optflow.jpg`: refused: Unknown interpolation 'auto'. Available: area, bicubic, bilinear, lanczos, nearest
- `target_ratio=1.7777777777777777, interpolation=auto` on `cctv/event_tamper.jpg`: refused: Unknown interpolation 'auto'. Available: area, bicubic, bilinear, lanczos, nearest
- `target_ratio=1.7777777777777777, interpolation=auto` on `cctv/flattest.jpg`: refused: Unknown interpolation 'auto'. Available: area, bicubic, bilinear, lanczos, nearest
- `target_ratio=1.7777777777777777, interpolation=auto` on `cctv/most_blown.jpg`: refused: Unknown interpolation 'auto'. Available: area, bicubic, bilinear, lanczos, nearest
- `target_ratio=1.7777777777777777, interpolation=auto` on `cctv/sharpest.jpg`: refused: Unknown interpolation 'auto'. Available: area, bicubic, bilinear, lanczos, nearest
- `target_ratio=1.7777777777777777, interpolation=auto` on `cctv/softest.jpg`: refused: Unknown interpolation 'auto'. Available: area, bicubic, bilinear, lanczos, nearest

## Refused parameters

Rejected on purpose, with the message the user would see.

- `target_ratio=1.7777777777777777, interpolation=auto` -> ValueError: Unknown interpolation 'auto'. Available: area, bicubic, bilinear, lanczos, nearest

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `target_ratio=1.7777777777777777` | 0.1 | [362, 644, 3] uint8 mean 162.52 | ok |
| `cctv/brightest.jpg` | `target_ratio=1.7777777777777777, mode=crop` | 0.2 | [360, 640, 3] uint8 mean 163.75 | ok |
| `cctv/brightest.jpg` | `target_ratio=1.7777777777777777, mode=stretch` | 1.3 | [362, 644, 3] uint8 mean 163.52 | ok |
| `cctv/brightest.jpg` | `target_ratio=1.7777777777777777, interpolation=auto` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: area, bicubic, bil |
| `cctv/brightest.jpg` | `target_ratio=1.7777777777777777, interpolation=nearest` | 0.2 | [362, 644, 3] uint8 mean 162.52 | ok |
| `cctv/darkest.jpg` | `target_ratio=1.7777777777777777` | 0.2 | [362, 644, 3] uint8 mean 110.24 | ok |
| `cctv/darkest.jpg` | `target_ratio=1.7777777777777777, mode=crop` | 0.1 | [360, 640, 3] uint8 mean 111.12 | ok |
| `cctv/darkest.jpg` | `target_ratio=1.7777777777777777, mode=stretch` | 1.5 | [362, 644, 3] uint8 mean 110.91 | ok |
| `cctv/darkest.jpg` | `target_ratio=1.7777777777777777, interpolation=auto` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: area, bicubic, bil |
| `cctv/darkest.jpg` | `target_ratio=1.7777777777777777, interpolation=nearest` | 0.2 | [362, 644, 3] uint8 mean 110.24 | ok |
| `cctv/event_fall.jpg` | `target_ratio=1.7777777777777777` | 0.3 | [362, 644, 3] uint8 mean 124.73 | ok |
| `cctv/event_fall.jpg` | `target_ratio=1.7777777777777777, mode=crop` | 0.1 | [360, 640, 3] uint8 mean 125.9 | ok |
| `cctv/event_fall.jpg` | `target_ratio=1.7777777777777777, mode=stretch` | 2.1 | [362, 644, 3] uint8 mean 125.51 | ok |
| `cctv/event_fall.jpg` | `target_ratio=1.7777777777777777, interpolation=auto` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: area, bicubic, bil |
| `cctv/event_fall.jpg` | `target_ratio=1.7777777777777777, interpolation=nearest` | 0.2 | [362, 644, 3] uint8 mean 124.73 | ok |
| `cctv/event_optflow.jpg` | `target_ratio=1.7777777777777777` | 0.2 | [362, 644, 3] uint8 mean 124.64 | ok |
| `cctv/event_optflow.jpg` | `target_ratio=1.7777777777777777, mode=crop` | 0.1 | [360, 640, 3] uint8 mean 125.71 | ok |
| `cctv/event_optflow.jpg` | `target_ratio=1.7777777777777777, mode=stretch` | 2.2 | [362, 644, 3] uint8 mean 125.42 | ok |
| `cctv/event_optflow.jpg` | `target_ratio=1.7777777777777777, interpolation=auto` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: area, bicubic, bil |
| `cctv/event_optflow.jpg` | `target_ratio=1.7777777777777777, interpolation=nearest` | 0.2 | [362, 644, 3] uint8 mean 124.64 | ok |
| `cctv/event_tamper.jpg` | `target_ratio=1.7777777777777777` | 0.3 | [362, 644, 3] uint8 mean 159.63 | ok |
| `cctv/event_tamper.jpg` | `target_ratio=1.7777777777777777, mode=crop` | 0.1 | [360, 640, 3] uint8 mean 160.84 | ok |
| `cctv/event_tamper.jpg` | `target_ratio=1.7777777777777777, mode=stretch` | 2.0 | [362, 644, 3] uint8 mean 160.61 | ok |
| `cctv/event_tamper.jpg` | `target_ratio=1.7777777777777777, interpolation=auto` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: area, bicubic, bil |
| `cctv/event_tamper.jpg` | `target_ratio=1.7777777777777777, interpolation=nearest` | 0.2 | [362, 644, 3] uint8 mean 159.63 | ok |
| `cctv/flattest.jpg` | `target_ratio=1.7777777777777777` | 0.3 | [362, 644, 3] uint8 mean 120.74 | ok |
| `cctv/flattest.jpg` | `target_ratio=1.7777777777777777, mode=crop` | 0.1 | [360, 640, 3] uint8 mean 121.77 | ok |
| `cctv/flattest.jpg` | `target_ratio=1.7777777777777777, mode=stretch` | 1.3 | [362, 644, 3] uint8 mean 121.49 | ok |
| `cctv/flattest.jpg` | `target_ratio=1.7777777777777777, interpolation=auto` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: area, bicubic, bil |
| `cctv/flattest.jpg` | `target_ratio=1.7777777777777777, interpolation=nearest` | 0.2 | [362, 644, 3] uint8 mean 120.74 | ok |
| `cctv/most_blown.jpg` | `target_ratio=1.7777777777777777` | 0.2 | [362, 644, 3] uint8 mean 137.22 | ok |
| `cctv/most_blown.jpg` | `target_ratio=1.7777777777777777, mode=crop` | 0.1 | [360, 640, 3] uint8 mean 138.3 | ok |
| `cctv/most_blown.jpg` | `target_ratio=1.7777777777777777, mode=stretch` | 1.4 | [362, 644, 3] uint8 mean 138.07 | ok |
| `cctv/most_blown.jpg` | `target_ratio=1.7777777777777777, interpolation=auto` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: area, bicubic, bil |
| `cctv/most_blown.jpg` | `target_ratio=1.7777777777777777, interpolation=nearest` | 0.4 | [362, 644, 3] uint8 mean 137.22 | ok |
| `cctv/sharpest.jpg` | `target_ratio=1.7777777777777777` | 0.3 | [362, 644, 3] uint8 mean 130.94 | ok |
| `cctv/sharpest.jpg` | `target_ratio=1.7777777777777777, mode=crop` | 0.1 | [360, 640, 3] uint8 mean 132.03 | ok |
| `cctv/sharpest.jpg` | `target_ratio=1.7777777777777777, mode=stretch` | 1.6 | [362, 644, 3] uint8 mean 131.74 | ok |
| `cctv/sharpest.jpg` | `target_ratio=1.7777777777777777, interpolation=auto` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: area, bicubic, bil |
| `cctv/sharpest.jpg` | `target_ratio=1.7777777777777777, interpolation=nearest` | 0.2 | [362, 644, 3] uint8 mean 130.94 | ok |
| `cctv/softest.jpg` | `target_ratio=1.7777777777777777` | 0.2 | [362, 644, 3] uint8 mean 124.61 | ok |
| `cctv/softest.jpg` | `target_ratio=1.7777777777777777, mode=crop` | 0.1 | [360, 640, 3] uint8 mean 125.56 | ok |
| `cctv/softest.jpg` | `target_ratio=1.7777777777777777, mode=stretch` | 1.3 | [362, 644, 3] uint8 mean 125.38 | ok |
| `cctv/softest.jpg` | `target_ratio=1.7777777777777777, interpolation=auto` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: area, bicubic, bil |
| `cctv/softest.jpg` | `target_ratio=1.7777777777777777, interpolation=nearest` | 0.3 | [362, 644, 3] uint8 mean 124.61 | ok |

## Artifacts

Outputs written to `validation/artifacts/fit_aspect/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
