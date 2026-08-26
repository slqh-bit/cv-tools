# pixel_aspect - validation result

**Rescale non-square pixels to square**  
`src.filters.aspect_ratio` | family: Correct | 2026-08-21T12:45:40

## Verdict

**PASS** - 54 runs, no invariant broken, 5 specific checks passed.

9 run(s) refused bad parameters with a clear message, which is the wanted behaviour.

At default parameters this filter is an identity: a pixel aspect of 1.0 is already square. An unchanged image there is correct, not a fault.

## What this filter specifically promises

- PASS - pixel aspect 0.5 rescales the frame: 640x362 became 320x362
- PASS - pixel aspect 2 rescales the frame: 640x362 became 1280x362
- PASS - a pixel aspect of 1.0 is already square: nothing to correct
- PASS - fitting to 1.78 gives that ratio: 644x362 is 1.779
- PASS - fitting to 1.33 gives that ratio: 640x480 is 1.333

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `` on `cctv/brightest.jpg`: output identical to input
- `interpolation=auto` on `cctv/brightest.jpg`: refused: Unknown interpolation 'auto'. Available: area, bicubic, bilinear, lanczos, nearest
- `interpolation=nearest` on `cctv/brightest.jpg`: output identical to input
- `scale_axis=height` on `cctv/brightest.jpg`: output identical to input
- `` on `cctv/darkest.jpg`: output identical to input
- `interpolation=auto` on `cctv/darkest.jpg`: refused: Unknown interpolation 'auto'. Available: area, bicubic, bilinear, lanczos, nearest
- `interpolation=nearest` on `cctv/darkest.jpg`: output identical to input
- `scale_axis=height` on `cctv/darkest.jpg`: output identical to input
- `` on `cctv/event_fall.jpg`: output identical to input
- `interpolation=auto` on `cctv/event_fall.jpg`: refused: Unknown interpolation 'auto'. Available: area, bicubic, bilinear, lanczos, nearest
- `interpolation=nearest` on `cctv/event_fall.jpg`: output identical to input
- `scale_axis=height` on `cctv/event_fall.jpg`: output identical to input

## Refused parameters

Rejected on purpose, with the message the user would see.

- `interpolation=auto` -> ValueError: Unknown interpolation 'auto'. Available: area, bicubic, bilinear, lanczos, nearest

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 0.2 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/brightest.jpg` | `pixel_aspect=0.25` | 1.2 | [362, 160, 3] uint8 mean 163.79 | ok |
| `cctv/brightest.jpg` | `pixel_aspect=4.0` | 5.2 | [362, 2560, 3] uint8 mean 163.52 | ok |
| `cctv/brightest.jpg` | `interpolation=auto` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: area, bicubic, bil |
| `cctv/brightest.jpg` | `interpolation=nearest` | 0.4 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/brightest.jpg` | `scale_axis=height` | 0.0 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/darkest.jpg` | `defaults` | 0.1 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/darkest.jpg` | `pixel_aspect=0.25` | 1.2 | [362, 160, 3] uint8 mean 111.13 | ok |
| `cctv/darkest.jpg` | `pixel_aspect=4.0` | 4.5 | [362, 2560, 3] uint8 mean 110.92 | ok |
| `cctv/darkest.jpg` | `interpolation=auto` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: area, bicubic, bil |
| `cctv/darkest.jpg` | `interpolation=nearest` | 0.4 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/darkest.jpg` | `scale_axis=height` | 0.0 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/event_fall.jpg` | `defaults` | 0.1 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_fall.jpg` | `pixel_aspect=0.25` | 1.2 | [362, 160, 3] uint8 mean 125.81 | ok |
| `cctv/event_fall.jpg` | `pixel_aspect=4.0` | 4.7 | [362, 2560, 3] uint8 mean 125.51 | ok |
| `cctv/event_fall.jpg` | `interpolation=auto` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: area, bicubic, bil |
| `cctv/event_fall.jpg` | `interpolation=nearest` | 0.4 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_fall.jpg` | `scale_axis=height` | 0.0 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_optflow.jpg` | `defaults` | 0.1 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_optflow.jpg` | `pixel_aspect=0.25` | 1.2 | [362, 160, 3] uint8 mean 125.57 | ok |
| `cctv/event_optflow.jpg` | `pixel_aspect=4.0` | 4.7 | [362, 2560, 3] uint8 mean 125.42 | ok |
| `cctv/event_optflow.jpg` | `interpolation=auto` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: area, bicubic, bil |
| `cctv/event_optflow.jpg` | `interpolation=nearest` | 0.4 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_optflow.jpg` | `scale_axis=height` | 0.0 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_tamper.jpg` | `defaults` | 0.1 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/event_tamper.jpg` | `pixel_aspect=0.25` | 1.1 | [362, 160, 3] uint8 mean 160.87 | ok |
| `cctv/event_tamper.jpg` | `pixel_aspect=4.0` | 5.1 | [362, 2560, 3] uint8 mean 160.61 | ok |
| `cctv/event_tamper.jpg` | `interpolation=auto` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: area, bicubic, bil |
| `cctv/event_tamper.jpg` | `interpolation=nearest` | 0.4 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/event_tamper.jpg` | `scale_axis=height` | 0.0 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/flattest.jpg` | `defaults` | 0.1 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/flattest.jpg` | `pixel_aspect=0.25` | 1.2 | [362, 160, 3] uint8 mean 121.68 | ok |
| `cctv/flattest.jpg` | `pixel_aspect=4.0` | 4.6 | [362, 2560, 3] uint8 mean 121.49 | ok |
| `cctv/flattest.jpg` | `interpolation=auto` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: area, bicubic, bil |
| `cctv/flattest.jpg` | `interpolation=nearest` | 0.4 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/flattest.jpg` | `scale_axis=height` | 0.0 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/most_blown.jpg` | `defaults` | 0.1 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/most_blown.jpg` | `pixel_aspect=0.25` | 1.2 | [362, 160, 3] uint8 mean 138.37 | ok |
| `cctv/most_blown.jpg` | `pixel_aspect=4.0` | 4.9 | [362, 2560, 3] uint8 mean 138.07 | ok |
| `cctv/most_blown.jpg` | `interpolation=auto` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: area, bicubic, bil |
| `cctv/most_blown.jpg` | `interpolation=nearest` | 0.4 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/most_blown.jpg` | `scale_axis=height` | 0.0 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/sharpest.jpg` | `defaults` | 0.1 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/sharpest.jpg` | `pixel_aspect=0.25` | 1.2 | [362, 160, 3] uint8 mean 131.98 | ok |
| `cctv/sharpest.jpg` | `pixel_aspect=4.0` | 5.8 | [362, 2560, 3] uint8 mean 131.76 | ok |
| `cctv/sharpest.jpg` | `interpolation=auto` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: area, bicubic, bil |
| `cctv/sharpest.jpg` | `interpolation=nearest` | 0.4 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/sharpest.jpg` | `scale_axis=height` | 0.0 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/softest.jpg` | `defaults` | 0.1 | [362, 640, 3] uint8 mean 125.38 | output identical to input |
| `cctv/softest.jpg` | `pixel_aspect=0.25` | 1.2 | [362, 160, 3] uint8 mean 125.66 | ok |
| `cctv/softest.jpg` | `pixel_aspect=4.0` | 5.6 | [362, 2560, 3] uint8 mean 125.39 | ok |
| `cctv/softest.jpg` | `interpolation=auto` | 0.0 | - | refused: ValueError: Unknown interpolation 'auto'. Available: area, bicubic, bil |
| `cctv/softest.jpg` | `interpolation=nearest` | 0.4 | [362, 640, 3] uint8 mean 125.38 | output identical to input |
| `cctv/softest.jpg` | `scale_axis=height` | 0.0 | [362, 640, 3] uint8 mean 125.38 | output identical to input |

## Artifacts

Outputs written to `validation/artifacts/pixel_aspect/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
