# desaturate - validation result

**Grayscale conversion by a chosen rule**  
`cv_tools.filters.saturation` | family: Adjust | 2026-09-01T16:34:53

## Verdict

**PASS** - 27 runs, no invariant broken.

18 run(s) refused bad parameters with a clear message, which is the wanted behaviour.

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `method=fill` on `cctv/brightest.jpg`: refused: Unknown method 'fill'. Available: luminance, average, lightness, max, min
- `method=noise` on `cctv/brightest.jpg`: refused: Unknown method 'noise'. Available: luminance, average, lightness, max, min
- `method=fill` on `cctv/darkest.jpg`: refused: Unknown method 'fill'. Available: luminance, average, lightness, max, min
- `method=noise` on `cctv/darkest.jpg`: refused: Unknown method 'noise'. Available: luminance, average, lightness, max, min
- `method=fill` on `cctv/event_fall.jpg`: refused: Unknown method 'fill'. Available: luminance, average, lightness, max, min
- `method=noise` on `cctv/event_fall.jpg`: refused: Unknown method 'noise'. Available: luminance, average, lightness, max, min
- `method=fill` on `cctv/event_optflow.jpg`: refused: Unknown method 'fill'. Available: luminance, average, lightness, max, min
- `method=noise` on `cctv/event_optflow.jpg`: refused: Unknown method 'noise'. Available: luminance, average, lightness, max, min
- `method=fill` on `cctv/event_tamper.jpg`: refused: Unknown method 'fill'. Available: luminance, average, lightness, max, min
- `method=noise` on `cctv/event_tamper.jpg`: refused: Unknown method 'noise'. Available: luminance, average, lightness, max, min
- `method=fill` on `cctv/flattest.jpg`: refused: Unknown method 'fill'. Available: luminance, average, lightness, max, min
- `method=noise` on `cctv/flattest.jpg`: refused: Unknown method 'noise'. Available: luminance, average, lightness, max, min

## Refused parameters

Rejected on purpose, with the message the user would see.

- `method=fill` -> ValueError: Unknown method 'fill'. Available: luminance, average, lightness, max, min
- `method=noise` -> ValueError: Unknown method 'noise'. Available: luminance, average, lightness, max, min

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 1.4 | [362, 640] uint8 mean 164.06 | ok |
| `cctv/brightest.jpg` | `method=fill` | 0.0 | - | refused: ValueError: Unknown method 'fill'. Available: luminance, average, light |
| `cctv/brightest.jpg` | `method=noise` | 0.0 | - | refused: ValueError: Unknown method 'noise'. Available: luminance, average, ligh |
| `cctv/darkest.jpg` | `defaults` | 1.4 | [362, 640] uint8 mean 110.91 | ok |
| `cctv/darkest.jpg` | `method=fill` | 0.0 | - | refused: ValueError: Unknown method 'fill'. Available: luminance, average, light |
| `cctv/darkest.jpg` | `method=noise` | 0.0 | - | refused: ValueError: Unknown method 'noise'. Available: luminance, average, ligh |
| `cctv/event_fall.jpg` | `defaults` | 1.4 | [362, 640] uint8 mean 127.35 | ok |
| `cctv/event_fall.jpg` | `method=fill` | 0.0 | - | refused: ValueError: Unknown method 'fill'. Available: luminance, average, light |
| `cctv/event_fall.jpg` | `method=noise` | 0.0 | - | refused: ValueError: Unknown method 'noise'. Available: luminance, average, ligh |
| `cctv/event_optflow.jpg` | `defaults` | 1.7 | [362, 640] uint8 mean 127.62 | ok |
| `cctv/event_optflow.jpg` | `method=fill` | 0.0 | - | refused: ValueError: Unknown method 'fill'. Available: luminance, average, light |
| `cctv/event_optflow.jpg` | `method=noise` | 0.0 | - | refused: ValueError: Unknown method 'noise'. Available: luminance, average, ligh |
| `cctv/event_tamper.jpg` | `defaults` | 1.4 | [362, 640] uint8 mean 160.87 | ok |
| `cctv/event_tamper.jpg` | `method=fill` | 0.0 | - | refused: ValueError: Unknown method 'fill'. Available: luminance, average, light |
| `cctv/event_tamper.jpg` | `method=noise` | 0.0 | - | refused: ValueError: Unknown method 'noise'. Available: luminance, average, ligh |
| `cctv/flattest.jpg` | `defaults` | 1.5 | [362, 640] uint8 mean 123.3 | ok |
| `cctv/flattest.jpg` | `method=fill` | 0.0 | - | refused: ValueError: Unknown method 'fill'. Available: luminance, average, light |
| `cctv/flattest.jpg` | `method=noise` | 0.0 | - | refused: ValueError: Unknown method 'noise'. Available: luminance, average, ligh |
| `cctv/most_blown.jpg` | `defaults` | 1.4 | [362, 640] uint8 mean 137.95 | ok |
| `cctv/most_blown.jpg` | `method=fill` | 0.0 | - | refused: ValueError: Unknown method 'fill'. Available: luminance, average, light |
| `cctv/most_blown.jpg` | `method=noise` | 0.0 | - | refused: ValueError: Unknown method 'noise'. Available: luminance, average, ligh |
| `cctv/sharpest.jpg` | `defaults` | 1.4 | [362, 640] uint8 mean 131.55 | ok |
| `cctv/sharpest.jpg` | `method=fill` | 0.0 | - | refused: ValueError: Unknown method 'fill'. Available: luminance, average, light |
| `cctv/sharpest.jpg` | `method=noise` | 0.0 | - | refused: ValueError: Unknown method 'noise'. Available: luminance, average, ligh |
| `cctv/softest.jpg` | `defaults` | 1.4 | [362, 640] uint8 mean 125.59 | ok |
| `cctv/softest.jpg` | `method=fill` | 0.0 | - | refused: ValueError: Unknown method 'fill'. Available: luminance, average, light |
| `cctv/softest.jpg` | `method=noise` | 0.0 | - | refused: ValueError: Unknown method 'noise'. Available: luminance, average, ligh |

## Artifacts

Outputs written to `validation/artifacts/desaturate/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
