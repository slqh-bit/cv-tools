# stain - validation result

**Extract one colorant by colour deconvolution**  
`cv_tools.filters.color_deconvolution` | family: Special | 2026-09-01T16:37:17

## Verdict

**PASS** - 40 runs, no invariant broken.

10 run(s) refused bad parameters with a clear message, which is the wanted behaviour.

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `preset=brighten` on `cctv/brightest.jpg`: refused: Unknown preset 'brighten'. Available: blue_black_ink, h_dab, h_e, h_e_dab, red_blue_ink
- `preset=brighten` on `cctv/darkest.jpg`: refused: Unknown preset 'brighten'. Available: blue_black_ink, h_dab, h_e, h_e_dab, red_blue_ink
- `preset=brighten` on `cctv/event_fall.jpg`: refused: Unknown preset 'brighten'. Available: blue_black_ink, h_dab, h_e, h_e_dab, red_blue_ink
- `preset=brighten` on `cctv/event_optflow.jpg`: refused: Unknown preset 'brighten'. Available: blue_black_ink, h_dab, h_e, h_e_dab, red_blue_ink
- `preset=brighten` on `cctv/event_tamper.jpg`: refused: Unknown preset 'brighten'. Available: blue_black_ink, h_dab, h_e, h_e_dab, red_blue_ink
- `preset=brighten` on `cctv/flattest.jpg`: refused: Unknown preset 'brighten'. Available: blue_black_ink, h_dab, h_e, h_e_dab, red_blue_ink
- `preset=brighten` on `cctv/most_blown.jpg`: refused: Unknown preset 'brighten'. Available: blue_black_ink, h_dab, h_e, h_e_dab, red_blue_ink
- `preset=brighten` on `cctv/sharpest.jpg`: refused: Unknown preset 'brighten'. Available: blue_black_ink, h_dab, h_e, h_e_dab, red_blue_ink
- `preset=brighten` on `cctv/softest.jpg`: refused: Unknown preset 'brighten'. Available: blue_black_ink, h_dab, h_e, h_e_dab, red_blue_ink
- `preset=brighten` on `reference/lena.png`: refused: Unknown preset 'brighten'. Available: blue_black_ink, h_dab, h_e, h_e_dab, red_blue_ink

## Refused parameters

Rejected on purpose, with the message the user would see.

- `preset=brighten` -> ValueError: Unknown preset 'brighten'. Available: blue_black_ink, h_dab, h_e, h_e_dab, red_blue_ink

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 25.0 | [362, 640] uint8 mean 124.71 | ok |
| `cctv/brightest.jpg` | `preset=blue_black_ink` | 22.8 | [362, 640] uint8 mean 244.54 | ok |
| `cctv/brightest.jpg` | `preset=brighten` | 0.0 | - | refused: ValueError: Unknown preset 'brighten'. Available: blue_black_ink, h_dab |
| `cctv/brightest.jpg` | `invert=True` | 23.5 | [362, 640] uint8 mean 130.29 | ok |
| `cctv/darkest.jpg` | `defaults` | 23.6 | [362, 640] uint8 mean 62.64 | ok |
| `cctv/darkest.jpg` | `preset=blue_black_ink` | 24.7 | [362, 640] uint8 mean 242.45 | ok |
| `cctv/darkest.jpg` | `preset=brighten` | 0.0 | - | refused: ValueError: Unknown preset 'brighten'. Available: blue_black_ink, h_dab |
| `cctv/darkest.jpg` | `invert=True` | 24.9 | [362, 640] uint8 mean 192.36 | ok |
| `cctv/event_fall.jpg` | `defaults` | 24.0 | [362, 640] uint8 mean 79.51 | ok |
| `cctv/event_fall.jpg` | `preset=blue_black_ink` | 27.7 | [362, 640] uint8 mean 234.4 | ok |
| `cctv/event_fall.jpg` | `preset=brighten` | 0.0 | - | refused: ValueError: Unknown preset 'brighten'. Available: blue_black_ink, h_dab |
| `cctv/event_fall.jpg` | `invert=True` | 23.5 | [362, 640] uint8 mean 175.49 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 23.3 | [362, 640] uint8 mean 75.93 | ok |
| `cctv/event_optflow.jpg` | `preset=blue_black_ink` | 24.6 | [362, 640] uint8 mean 236.37 | ok |
| `cctv/event_optflow.jpg` | `preset=brighten` | 0.0 | - | refused: ValueError: Unknown preset 'brighten'. Available: blue_black_ink, h_dab |
| `cctv/event_optflow.jpg` | `invert=True` | 23.2 | [362, 640] uint8 mean 179.07 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 23.4 | [362, 640] uint8 mean 120.68 | ok |
| `cctv/event_tamper.jpg` | `preset=blue_black_ink` | 23.7 | [362, 640] uint8 mean 243.36 | ok |
| `cctv/event_tamper.jpg` | `preset=brighten` | 0.0 | - | refused: ValueError: Unknown preset 'brighten'. Available: blue_black_ink, h_dab |
| `cctv/event_tamper.jpg` | `invert=True` | 28.0 | [362, 640] uint8 mean 134.32 | ok |
| `cctv/flattest.jpg` | `defaults` | 22.8 | [362, 640] uint8 mean 71.29 | ok |
| `cctv/flattest.jpg` | `preset=blue_black_ink` | 24.5 | [362, 640] uint8 mean 234.1 | ok |
| `cctv/flattest.jpg` | `preset=brighten` | 0.0 | - | refused: ValueError: Unknown preset 'brighten'. Available: blue_black_ink, h_dab |
| `cctv/flattest.jpg` | `invert=True` | 23.7 | [362, 640] uint8 mean 183.71 | ok |
| `cctv/most_blown.jpg` | `defaults` | 24.0 | [362, 640] uint8 mean 92.87 | ok |
| `cctv/most_blown.jpg` | `preset=blue_black_ink` | 23.5 | [362, 640] uint8 mean 244.59 | ok |
| `cctv/most_blown.jpg` | `preset=brighten` | 0.0 | - | refused: ValueError: Unknown preset 'brighten'. Available: blue_black_ink, h_dab |
| `cctv/most_blown.jpg` | `invert=True` | 23.2 | [362, 640] uint8 mean 162.13 | ok |
| `cctv/sharpest.jpg` | `defaults` | 23.5 | [362, 640] uint8 mean 87.73 | ok |
| `cctv/sharpest.jpg` | `preset=blue_black_ink` | 23.3 | [362, 640] uint8 mean 240.91 | ok |
| `cctv/sharpest.jpg` | `preset=brighten` | 0.0 | - | refused: ValueError: Unknown preset 'brighten'. Available: blue_black_ink, h_dab |
| `cctv/sharpest.jpg` | `invert=True` | 23.8 | [362, 640] uint8 mean 167.27 | ok |
| `cctv/softest.jpg` | `defaults` | 24.2 | [362, 640] uint8 mean 75.85 | ok |
| `cctv/softest.jpg` | `preset=blue_black_ink` | 24.3 | [362, 640] uint8 mean 241.01 | ok |
| `cctv/softest.jpg` | `preset=brighten` | 0.0 | - | refused: ValueError: Unknown preset 'brighten'. Available: blue_black_ink, h_dab |
| `cctv/softest.jpg` | `invert=True` | 23.4 | [362, 640] uint8 mean 179.15 | ok |
| `reference/lena.png` | `defaults` | 26.6 | [512, 512] uint8 mean 117.22 | ok |
| `reference/lena.png` | `preset=blue_black_ink` | 28.7 | [512, 512] uint8 mean 254.31 | ok |
| `reference/lena.png` | `preset=brighten` | 0.0 | - | refused: ValueError: Unknown preset 'brighten'. Available: blue_black_ink, h_dab |
| `reference/lena.png` | `invert=True` | 26.6 | [512, 512] uint8 mean 137.78 | ok |

## Artifacts

Outputs written to `validation/artifacts/stain/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
- `reference_lena.png`
