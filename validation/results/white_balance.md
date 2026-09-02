# white_balance - validation result

**Automatic colour cast removal**  
`cv_tools.filters.white_balance` | family: Adjust | 2026-09-01T16:34:50

## Verdict

**PASS** - 45 runs, no invariant broken, 5 specific checks passed.

18 run(s) refused bad parameters with a clear message, which is the wanted behaviour.

## What this filter specifically promises

- PASS - gray_world reduces a deliberate red cast: channel spread 45.0 -> 0.5
- PASS - white_patch reduces a deliberate red cast: channel spread 45.0 -> 17.9
- PASS - shades_of_gray reduces a deliberate red cast: channel spread 45.0 -> 9.1
- PASS - white_patch is the one that struggles with blown highlights: 4.9% of this frame is at 250 or above; white_patch leaves a spread of 9.7 against gray_world's 0.8
- PASS - a patch declared neutral comes out neutral, from a cast frame: channel spread inside the patch 14.4 -> 0.5

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `method=fill` on `cctv/brightest.jpg`: refused: Unknown method 'fill'. Available: gray_world, white_patch, shades_of_gray
- `method=noise` on `cctv/brightest.jpg`: refused: Unknown method 'noise'. Available: gray_world, white_patch, shades_of_gray
- `method=fill` on `cctv/darkest.jpg`: refused: Unknown method 'fill'. Available: gray_world, white_patch, shades_of_gray
- `method=noise` on `cctv/darkest.jpg`: refused: Unknown method 'noise'. Available: gray_world, white_patch, shades_of_gray
- `method=fill` on `cctv/event_fall.jpg`: refused: Unknown method 'fill'. Available: gray_world, white_patch, shades_of_gray
- `method=noise` on `cctv/event_fall.jpg`: refused: Unknown method 'noise'. Available: gray_world, white_patch, shades_of_gray
- `method=fill` on `cctv/event_optflow.jpg`: refused: Unknown method 'fill'. Available: gray_world, white_patch, shades_of_gray
- `method=noise` on `cctv/event_optflow.jpg`: refused: Unknown method 'noise'. Available: gray_world, white_patch, shades_of_gray
- `method=fill` on `cctv/event_tamper.jpg`: refused: Unknown method 'fill'. Available: gray_world, white_patch, shades_of_gray
- `method=noise` on `cctv/event_tamper.jpg`: refused: Unknown method 'noise'. Available: gray_world, white_patch, shades_of_gray
- `method=fill` on `cctv/flattest.jpg`: refused: Unknown method 'fill'. Available: gray_world, white_patch, shades_of_gray
- `method=noise` on `cctv/flattest.jpg`: refused: Unknown method 'noise'. Available: gray_world, white_patch, shades_of_gray

## Refused parameters

Rejected on purpose, with the message the user would see.

- `method=fill` -> ValueError: Unknown method 'fill'. Available: gray_world, white_patch, shades_of_gray
- `method=noise` -> ValueError: Unknown method 'noise'. Available: gray_world, white_patch, shades_of_gray

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 11.2 | [362, 640, 3] uint8 mean 164.82 | ok |
| `cctv/brightest.jpg` | `method=fill` | 0.0 | - | refused: ValueError: Unknown method 'fill'. Available: gray_world, white_patch,  |
| `cctv/brightest.jpg` | `method=noise` | 0.0 | - | refused: ValueError: Unknown method 'noise'. Available: gray_world, white_patch, |
| `cctv/brightest.jpg` | `percentile=50.0` | 11.3 | [362, 640, 3] uint8 mean 164.82 | ok |
| `cctv/brightest.jpg` | `percentile=100.0` | 11.5 | [362, 640, 3] uint8 mean 164.82 | ok |
| `cctv/darkest.jpg` | `defaults` | 11.6 | [362, 640, 3] uint8 mean 111.19 | ok |
| `cctv/darkest.jpg` | `method=fill` | 0.0 | - | refused: ValueError: Unknown method 'fill'. Available: gray_world, white_patch,  |
| `cctv/darkest.jpg` | `method=noise` | 0.0 | - | refused: ValueError: Unknown method 'noise'. Available: gray_world, white_patch, |
| `cctv/darkest.jpg` | `percentile=50.0` | 11.3 | [362, 640, 3] uint8 mean 111.19 | ok |
| `cctv/darkest.jpg` | `percentile=100.0` | 11.3 | [362, 640, 3] uint8 mean 111.19 | ok |
| `cctv/event_fall.jpg` | `defaults` | 11.0 | [362, 640, 3] uint8 mean 125.49 | ok |
| `cctv/event_fall.jpg` | `method=fill` | 0.0 | - | refused: ValueError: Unknown method 'fill'. Available: gray_world, white_patch,  |
| `cctv/event_fall.jpg` | `method=noise` | 0.0 | - | refused: ValueError: Unknown method 'noise'. Available: gray_world, white_patch, |
| `cctv/event_fall.jpg` | `percentile=50.0` | 11.1 | [362, 640, 3] uint8 mean 125.49 | ok |
| `cctv/event_fall.jpg` | `percentile=100.0` | 10.9 | [362, 640, 3] uint8 mean 125.49 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 10.7 | [362, 640, 3] uint8 mean 125.66 | ok |
| `cctv/event_optflow.jpg` | `method=fill` | 0.0 | - | refused: ValueError: Unknown method 'fill'. Available: gray_world, white_patch,  |
| `cctv/event_optflow.jpg` | `method=noise` | 0.0 | - | refused: ValueError: Unknown method 'noise'. Available: gray_world, white_patch, |
| `cctv/event_optflow.jpg` | `percentile=50.0` | 11.7 | [362, 640, 3] uint8 mean 125.66 | ok |
| `cctv/event_optflow.jpg` | `percentile=100.0` | 11.5 | [362, 640, 3] uint8 mean 125.66 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 11.5 | [362, 640, 3] uint8 mean 161.72 | ok |
| `cctv/event_tamper.jpg` | `method=fill` | 0.0 | - | refused: ValueError: Unknown method 'fill'. Available: gray_world, white_patch,  |
| `cctv/event_tamper.jpg` | `method=noise` | 0.0 | - | refused: ValueError: Unknown method 'noise'. Available: gray_world, white_patch, |
| `cctv/event_tamper.jpg` | `percentile=50.0` | 11.7 | [362, 640, 3] uint8 mean 161.72 | ok |
| `cctv/event_tamper.jpg` | `percentile=100.0` | 11.1 | [362, 640, 3] uint8 mean 161.72 | ok |
| `cctv/flattest.jpg` | `defaults` | 11.3 | [362, 640, 3] uint8 mean 121.9 | ok |
| `cctv/flattest.jpg` | `method=fill` | 0.0 | - | refused: ValueError: Unknown method 'fill'. Available: gray_world, white_patch,  |
| `cctv/flattest.jpg` | `method=noise` | 0.0 | - | refused: ValueError: Unknown method 'noise'. Available: gray_world, white_patch, |
| `cctv/flattest.jpg` | `percentile=50.0` | 11.2 | [362, 640, 3] uint8 mean 121.9 | ok |
| `cctv/flattest.jpg` | `percentile=100.0` | 11.3 | [362, 640, 3] uint8 mean 121.9 | ok |
| `cctv/most_blown.jpg` | `defaults` | 11.1 | [362, 640, 3] uint8 mean 138.24 | ok |
| `cctv/most_blown.jpg` | `method=fill` | 0.0 | - | refused: ValueError: Unknown method 'fill'. Available: gray_world, white_patch,  |
| `cctv/most_blown.jpg` | `method=noise` | 0.0 | - | refused: ValueError: Unknown method 'noise'. Available: gray_world, white_patch, |
| `cctv/most_blown.jpg` | `percentile=50.0` | 11.4 | [362, 640, 3] uint8 mean 138.24 | ok |
| `cctv/most_blown.jpg` | `percentile=100.0` | 11.2 | [362, 640, 3] uint8 mean 138.24 | ok |
| `cctv/sharpest.jpg` | `defaults` | 12.0 | [362, 640, 3] uint8 mean 131.46 | ok |
| `cctv/sharpest.jpg` | `method=fill` | 0.0 | - | refused: ValueError: Unknown method 'fill'. Available: gray_world, white_patch,  |
| `cctv/sharpest.jpg` | `method=noise` | 0.0 | - | refused: ValueError: Unknown method 'noise'. Available: gray_world, white_patch, |
| `cctv/sharpest.jpg` | `percentile=50.0` | 13.0 | [362, 640, 3] uint8 mean 131.46 | ok |
| `cctv/sharpest.jpg` | `percentile=100.0` | 11.8 | [362, 640, 3] uint8 mean 131.46 | ok |
| `cctv/softest.jpg` | `defaults` | 11.4 | [362, 640, 3] uint8 mean 125.87 | ok |
| `cctv/softest.jpg` | `method=fill` | 0.0 | - | refused: ValueError: Unknown method 'fill'. Available: gray_world, white_patch,  |
| `cctv/softest.jpg` | `method=noise` | 0.0 | - | refused: ValueError: Unknown method 'noise'. Available: gray_world, white_patch, |
| `cctv/softest.jpg` | `percentile=50.0` | 11.3 | [362, 640, 3] uint8 mean 125.87 | ok |
| `cctv/softest.jpg` | `percentile=100.0` | 12.5 | [362, 640, 3] uint8 mean 125.87 | ok |

## Artifacts

Outputs written to `validation/artifacts/white_balance/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
