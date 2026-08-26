# upscale - validation result

**Single-frame interpolated enlargement**  
`src.filters.super_resolution` | family: Enhance | 2026-08-21T12:45:21

## Verdict

**PASS** - 50 runs, no invariant broken, 3 specific checks passed.

20 run(s) refused bad parameters with a clear message, which is the wanted behaviour.

## What this filter specifically promises

- PASS - 2x gives exactly the expected size: 1280x724, expected 1280x724
- PASS - 3x gives exactly the expected size: 1920x1086, expected 1920x1086
- PASS - a round trip returns close to the original: mean absolute difference 1.63/255 after up and down

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `method=fill` on `cctv/brightest.jpg`: refused: Unknown method 'fill'. Available: bicubic, bilinear, lanczos, nearest
- `method=noise` on `cctv/brightest.jpg`: refused: Unknown method 'noise'. Available: bicubic, bilinear, lanczos, nearest
- `method=fill` on `cctv/darkest.jpg`: refused: Unknown method 'fill'. Available: bicubic, bilinear, lanczos, nearest
- `method=noise` on `cctv/darkest.jpg`: refused: Unknown method 'noise'. Available: bicubic, bilinear, lanczos, nearest
- `method=fill` on `cctv/event_fall.jpg`: refused: Unknown method 'fill'. Available: bicubic, bilinear, lanczos, nearest
- `method=noise` on `cctv/event_fall.jpg`: refused: Unknown method 'noise'. Available: bicubic, bilinear, lanczos, nearest
- `method=fill` on `cctv/event_optflow.jpg`: refused: Unknown method 'fill'. Available: bicubic, bilinear, lanczos, nearest
- `method=noise` on `cctv/event_optflow.jpg`: refused: Unknown method 'noise'. Available: bicubic, bilinear, lanczos, nearest
- `method=fill` on `cctv/event_tamper.jpg`: refused: Unknown method 'fill'. Available: bicubic, bilinear, lanczos, nearest
- `method=noise` on `cctv/event_tamper.jpg`: refused: Unknown method 'noise'. Available: bicubic, bilinear, lanczos, nearest
- `method=fill` on `cctv/flattest.jpg`: refused: Unknown method 'fill'. Available: bicubic, bilinear, lanczos, nearest
- `method=noise` on `cctv/flattest.jpg`: refused: Unknown method 'noise'. Available: bicubic, bilinear, lanczos, nearest

## Refused parameters

Rejected on purpose, with the message the user would see.

- `method=fill` -> ValueError: Unknown method 'fill'. Available: bicubic, bilinear, lanczos, nearest
- `method=noise` -> ValueError: Unknown method 'noise'. Available: bicubic, bilinear, lanczos, nearest

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 3.8 | [724, 1280, 3] uint8 mean 163.52 | ok |
| `cctv/brightest.jpg` | `scale=0.1` | 0.5 | [36, 64, 3] uint8 mean 164.14 | ok |
| `cctv/brightest.jpg` | `scale=8.0` | 40.8 | [2896, 5120, 3] uint8 mean 163.52 | ok |
| `cctv/brightest.jpg` | `method=fill` | 0.0 | - | refused: ValueError: Unknown method 'fill'. Available: bicubic, bilinear, lanczo |
| `cctv/brightest.jpg` | `method=noise` | 0.0 | - | refused: ValueError: Unknown method 'noise'. Available: bicubic, bilinear, lancz |
| `cctv/darkest.jpg` | `defaults` | 5.5 | [724, 1280, 3] uint8 mean 110.91 | ok |
| `cctv/darkest.jpg` | `scale=0.1` | 0.5 | [36, 64, 3] uint8 mean 111.15 | ok |
| `cctv/darkest.jpg` | `scale=8.0` | 40.9 | [2896, 5120, 3] uint8 mean 110.92 | ok |
| `cctv/darkest.jpg` | `method=fill` | 0.0 | - | refused: ValueError: Unknown method 'fill'. Available: bicubic, bilinear, lanczo |
| `cctv/darkest.jpg` | `method=noise` | 0.0 | - | refused: ValueError: Unknown method 'noise'. Available: bicubic, bilinear, lancz |
| `cctv/event_fall.jpg` | `defaults` | 6.2 | [724, 1280, 3] uint8 mean 125.53 | ok |
| `cctv/event_fall.jpg` | `scale=0.1` | 0.5 | [36, 64, 3] uint8 mean 127.04 | ok |
| `cctv/event_fall.jpg` | `scale=8.0` | 42.9 | [2896, 5120, 3] uint8 mean 125.53 | ok |
| `cctv/event_fall.jpg` | `method=fill` | 0.0 | - | refused: ValueError: Unknown method 'fill'. Available: bicubic, bilinear, lanczo |
| `cctv/event_fall.jpg` | `method=noise` | 0.0 | - | refused: ValueError: Unknown method 'noise'. Available: bicubic, bilinear, lancz |
| `cctv/event_optflow.jpg` | `defaults` | 6.0 | [724, 1280, 3] uint8 mean 125.42 | ok |
| `cctv/event_optflow.jpg` | `scale=0.1` | 0.6 | [36, 64, 3] uint8 mean 126.24 | ok |
| `cctv/event_optflow.jpg` | `scale=8.0` | 40.3 | [2896, 5120, 3] uint8 mean 125.42 | ok |
| `cctv/event_optflow.jpg` | `method=fill` | 0.0 | - | refused: ValueError: Unknown method 'fill'. Available: bicubic, bilinear, lanczo |
| `cctv/event_optflow.jpg` | `method=noise` | 0.0 | - | refused: ValueError: Unknown method 'noise'. Available: bicubic, bilinear, lancz |
| `cctv/event_tamper.jpg` | `defaults` | 5.5 | [724, 1280, 3] uint8 mean 160.61 | ok |
| `cctv/event_tamper.jpg` | `scale=0.1` | 0.5 | [36, 64, 3] uint8 mean 161.12 | ok |
| `cctv/event_tamper.jpg` | `scale=8.0` | 40.2 | [2896, 5120, 3] uint8 mean 160.61 | ok |
| `cctv/event_tamper.jpg` | `method=fill` | 0.0 | - | refused: ValueError: Unknown method 'fill'. Available: bicubic, bilinear, lanczo |
| `cctv/event_tamper.jpg` | `method=noise` | 0.0 | - | refused: ValueError: Unknown method 'noise'. Available: bicubic, bilinear, lancz |
| `cctv/flattest.jpg` | `defaults` | 5.1 | [724, 1280, 3] uint8 mean 121.49 | ok |
| `cctv/flattest.jpg` | `scale=0.1` | 0.5 | [36, 64, 3] uint8 mean 122.14 | ok |
| `cctv/flattest.jpg` | `scale=8.0` | 40.1 | [2896, 5120, 3] uint8 mean 121.5 | ok |
| `cctv/flattest.jpg` | `method=fill` | 0.0 | - | refused: ValueError: Unknown method 'fill'. Available: bicubic, bilinear, lanczo |
| `cctv/flattest.jpg` | `method=noise` | 0.0 | - | refused: ValueError: Unknown method 'noise'. Available: bicubic, bilinear, lancz |
| `cctv/most_blown.jpg` | `defaults` | 5.7 | [724, 1280, 3] uint8 mean 138.07 | ok |
| `cctv/most_blown.jpg` | `scale=0.1` | 0.5 | [36, 64, 3] uint8 mean 138.04 | ok |
| `cctv/most_blown.jpg` | `scale=8.0` | 41.6 | [2896, 5120, 3] uint8 mean 138.07 | ok |
| `cctv/most_blown.jpg` | `method=fill` | 0.0 | - | refused: ValueError: Unknown method 'fill'. Available: bicubic, bilinear, lanczo |
| `cctv/most_blown.jpg` | `method=noise` | 0.0 | - | refused: ValueError: Unknown method 'noise'. Available: bicubic, bilinear, lancz |
| `cctv/sharpest.jpg` | `defaults` | 5.4 | [724, 1280, 3] uint8 mean 131.78 | ok |
| `cctv/sharpest.jpg` | `scale=0.1` | 0.8 | [36, 64, 3] uint8 mean 132.3 | ok |
| `cctv/sharpest.jpg` | `scale=8.0` | 41.7 | [2896, 5120, 3] uint8 mean 131.78 | ok |
| `cctv/sharpest.jpg` | `method=fill` | 0.0 | - | refused: ValueError: Unknown method 'fill'. Available: bicubic, bilinear, lanczo |
| `cctv/sharpest.jpg` | `method=noise` | 0.0 | - | refused: ValueError: Unknown method 'noise'. Available: bicubic, bilinear, lancz |
| `cctv/softest.jpg` | `defaults` | 5.8 | [724, 1280, 3] uint8 mean 125.39 | ok |
| `cctv/softest.jpg` | `scale=0.1` | 0.6 | [36, 64, 3] uint8 mean 125.97 | ok |
| `cctv/softest.jpg` | `scale=8.0` | 39.8 | [2896, 5120, 3] uint8 mean 125.39 | ok |
| `cctv/softest.jpg` | `method=fill` | 0.0 | - | refused: ValueError: Unknown method 'fill'. Available: bicubic, bilinear, lanczo |
| `cctv/softest.jpg` | `method=noise` | 0.0 | - | refused: ValueError: Unknown method 'noise'. Available: bicubic, bilinear, lancz |
| `reference/baboon.png` | `defaults` | 6.2 | [1024, 1024, 3] uint8 mean 126.37 | ok |
| `reference/baboon.png` | `scale=0.1` | 0.6 | [51, 51, 3] uint8 mean 126.82 | ok |
| `reference/baboon.png` | `scale=8.0` | 42.6 | [4096, 4096, 3] uint8 mean 126.37 | ok |
| `reference/baboon.png` | `method=fill` | 0.0 | - | refused: ValueError: Unknown method 'fill'. Available: bicubic, bilinear, lanczo |
| `reference/baboon.png` | `method=noise` | 0.0 | - | refused: ValueError: Unknown method 'noise'. Available: bicubic, bilinear, lancz |

## Artifacts

Outputs written to `validation/artifacts/upscale/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
- `reference_baboon.png`
