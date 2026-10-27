# deblur_motion_grid - validation result

**Contact sheet of motion deblurs around an estimated length and angle, for closing in on the right one**  
`cv_tools.filters.motion_deblur` | family: Analyze | 2026-10-12T19:04:12

## Verdict

**PASS** - 90 runs, no invariant broken, 2 specific checks passed.

## What this filter specifically promises

- PASS - the middle tile is the estimate itself, at full resolution: tile is pixel-identical to the filter run on its own
- PASS - rows step the length and columns the angle: tile is pixel-identical to the filter run on its own

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 291.2 | [1140, 1920, 3] uint8 mean 153.5 | ok |
| `cctv/brightest.jpg` | `length=1.0` | 183.0 | [760, 1920, 3] uint8 mean 155.78 | ok |
| `cctv/brightest.jpg` | `length=200.0` | 1264.3 | [1140, 1920, 3] uint8 mean 132.17 | ok |
| `cctv/brightest.jpg` | `angle=-180.0` | 326.4 | [1140, 1920, 3] uint8 mean 153.56 | ok |
| `cctv/brightest.jpg` | `angle=180.0` | 322.0 | [1140, 1920, 3] uint8 mean 153.55 | ok |
| `cctv/brightest.jpg` | `noise_power=0.0001` | 330.7 | [1140, 1920, 3] uint8 mean 138.31 | ok |
| `cctv/brightest.jpg` | `noise_power=0.5` | 307.4 | [1140, 1920, 3] uint8 mean 156.08 | ok |
| `cctv/brightest.jpg` | `solver=richardson_lucy` | 16751.5 | [1140, 1920, 3] uint8 mean 151.47 | ok |
| `cctv/brightest.jpg` | `iterations=5` | 305.3 | [1140, 1920, 3] uint8 mean 153.5 | ok |
| `cctv/brightest.jpg` | `iterations=100` | 339.5 | [1140, 1920, 3] uint8 mean 153.5 | ok |
| `cctv/darkest.jpg` | `defaults` | 299.1 | [1140, 1920, 3] uint8 mean 104.96 | ok |
| `cctv/darkest.jpg` | `length=1.0` | 198.8 | [760, 1920, 3] uint8 mean 105.8 | ok |
| `cctv/darkest.jpg` | `length=200.0` | 1206.6 | [1140, 1920, 3] uint8 mean 102.68 | ok |
| `cctv/darkest.jpg` | `angle=-180.0` | 332.7 | [1140, 1920, 3] uint8 mean 105.02 | ok |
| `cctv/darkest.jpg` | `angle=180.0` | 313.3 | [1140, 1920, 3] uint8 mean 105.01 | ok |
| `cctv/darkest.jpg` | `noise_power=0.0001` | 324.6 | [1140, 1920, 3] uint8 mean 110.65 | ok |
| `cctv/darkest.jpg` | `noise_power=0.5` | 317.5 | [1140, 1920, 3] uint8 mean 105.98 | ok |
| `cctv/darkest.jpg` | `solver=richardson_lucy` | 16661.0 | [1140, 1920, 3] uint8 mean 100.94 | ok |
| `cctv/darkest.jpg` | `iterations=5` | 301.0 | [1140, 1920, 3] uint8 mean 104.96 | ok |
| `cctv/darkest.jpg` | `iterations=100` | 329.9 | [1140, 1920, 3] uint8 mean 104.96 | ok |
| `cctv/event_fall.jpg` | `defaults` | 320.6 | [1140, 1920, 3] uint8 mean 119.51 | ok |
| `cctv/event_fall.jpg` | `length=1.0` | 187.2 | [760, 1920, 3] uint8 mean 119.8 | ok |
| `cctv/event_fall.jpg` | `length=200.0` | 1176.3 | [1140, 1920, 3] uint8 mean 121.43 | ok |
| `cctv/event_fall.jpg` | `angle=-180.0` | 315.3 | [1140, 1920, 3] uint8 mean 119.57 | ok |
| `cctv/event_fall.jpg` | `angle=180.0` | 311.5 | [1140, 1920, 3] uint8 mean 119.56 | ok |
| `cctv/event_fall.jpg` | `noise_power=0.0001` | 346.6 | [1140, 1920, 3] uint8 mean 119.98 | ok |
| `cctv/event_fall.jpg` | `noise_power=0.5` | 355.1 | [1140, 1920, 3] uint8 mean 119.89 | ok |
| `cctv/event_fall.jpg` | `solver=richardson_lucy` | 16755.2 | [1140, 1920, 3] uint8 mean 105.65 | ok |
| `cctv/event_fall.jpg` | `iterations=5` | 299.0 | [1140, 1920, 3] uint8 mean 119.51 | ok |
| `cctv/event_fall.jpg` | `iterations=100` | 363.9 | [1140, 1920, 3] uint8 mean 119.51 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 311.4 | [1140, 1920, 3] uint8 mean 119.35 | ok |
| `cctv/event_optflow.jpg` | `length=1.0` | 195.3 | [760, 1920, 3] uint8 mean 119.78 | ok |
| `cctv/event_optflow.jpg` | `length=200.0` | 1199.3 | [1140, 1920, 3] uint8 mean 121.46 | ok |
| `cctv/event_optflow.jpg` | `angle=-180.0` | 318.0 | [1140, 1920, 3] uint8 mean 119.41 | ok |
| `cctv/event_optflow.jpg` | `angle=180.0` | 310.2 | [1140, 1920, 3] uint8 mean 119.4 | ok |
| `cctv/event_optflow.jpg` | `noise_power=0.0001` | 315.7 | [1140, 1920, 3] uint8 mean 118.58 | ok |
| `cctv/event_optflow.jpg` | `noise_power=0.5` | 340.1 | [1140, 1920, 3] uint8 mean 119.8 | ok |
| `cctv/event_optflow.jpg` | `solver=richardson_lucy` | 16559.5 | [1140, 1920, 3] uint8 mean 114.38 | ok |
| `cctv/event_optflow.jpg` | `iterations=5` | 314.3 | [1140, 1920, 3] uint8 mean 119.35 | ok |
| `cctv/event_optflow.jpg` | `iterations=100` | 306.6 | [1140, 1920, 3] uint8 mean 119.35 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 310.2 | [1140, 1920, 3] uint8 mean 150.96 | ok |
| `cctv/event_tamper.jpg` | `length=1.0` | 192.1 | [760, 1920, 3] uint8 mean 153.04 | ok |
| `cctv/event_tamper.jpg` | `length=200.0` | 1230.2 | [1140, 1920, 3] uint8 mean 130.66 | ok |
| `cctv/event_tamper.jpg` | `angle=-180.0` | 334.2 | [1140, 1920, 3] uint8 mean 151.02 | ok |
| `cctv/event_tamper.jpg` | `angle=180.0` | 361.4 | [1140, 1920, 3] uint8 mean 151.01 | ok |
| `cctv/event_tamper.jpg` | `noise_power=0.0001` | 334.5 | [1140, 1920, 3] uint8 mean 136.92 | ok |
| `cctv/event_tamper.jpg` | `noise_power=0.5` | 340.4 | [1140, 1920, 3] uint8 mean 153.31 | ok |
| `cctv/event_tamper.jpg` | `solver=richardson_lucy` | 15679.6 | [1140, 1920, 3] uint8 mean 148.83 | ok |
| `cctv/event_tamper.jpg` | `iterations=5` | 286.5 | [1140, 1920, 3] uint8 mean 150.96 | ok |
| `cctv/event_tamper.jpg` | `iterations=100` | 285.9 | [1140, 1920, 3] uint8 mean 150.96 | ok |
| `cctv/flattest.jpg` | `defaults` | 289.5 | [1140, 1920, 3] uint8 mean 115.74 | ok |
| `cctv/flattest.jpg` | `length=1.0` | 174.3 | [760, 1920, 3] uint8 mean 116.05 | ok |
| `cctv/flattest.jpg` | `length=200.0` | 1114.2 | [1140, 1920, 3] uint8 mean 118.89 | ok |
| `cctv/flattest.jpg` | `angle=-180.0` | 288.2 | [1140, 1920, 3] uint8 mean 115.8 | ok |
| `cctv/flattest.jpg` | `angle=180.0` | 293.0 | [1140, 1920, 3] uint8 mean 115.79 | ok |
| `cctv/flattest.jpg` | `noise_power=0.0001` | 283.3 | [1140, 1920, 3] uint8 mean 116.62 | ok |
| `cctv/flattest.jpg` | `noise_power=0.5` | 288.3 | [1140, 1920, 3] uint8 mean 116.06 | ok |
| `cctv/flattest.jpg` | `solver=richardson_lucy` | 15087.5 | [1140, 1920, 3] uint8 mean 110.95 | ok |
| `cctv/flattest.jpg` | `iterations=5` | 288.8 | [1140, 1920, 3] uint8 mean 115.74 | ok |
| `cctv/flattest.jpg` | `iterations=100` | 295.1 | [1140, 1920, 3] uint8 mean 115.74 | ok |
| `cctv/most_blown.jpg` | `defaults` | 292.2 | [1140, 1920, 3] uint8 mean 130.1 | ok |
| `cctv/most_blown.jpg` | `length=1.0` | 175.7 | [760, 1920, 3] uint8 mean 131.66 | ok |
| `cctv/most_blown.jpg` | `length=200.0` | 1117.4 | [1140, 1920, 3] uint8 mean 121.57 | ok |
| `cctv/most_blown.jpg` | `angle=-180.0` | 287.6 | [1140, 1920, 3] uint8 mean 130.16 | ok |
| `cctv/most_blown.jpg` | `angle=180.0` | 289.5 | [1140, 1920, 3] uint8 mean 130.14 | ok |
| `cctv/most_blown.jpg` | `noise_power=0.0001` | 293.0 | [1140, 1920, 3] uint8 mean 125.54 | ok |
| `cctv/most_blown.jpg` | `noise_power=0.5` | 295.8 | [1140, 1920, 3] uint8 mean 131.84 | ok |
| `cctv/most_blown.jpg` | `solver=richardson_lucy` | 15971.4 | [1140, 1920, 3] uint8 mean 126.48 | ok |
| `cctv/most_blown.jpg` | `iterations=5` | 317.5 | [1140, 1920, 3] uint8 mean 130.1 | ok |
| `cctv/most_blown.jpg` | `iterations=100` | 311.1 | [1140, 1920, 3] uint8 mean 130.1 | ok |
| `cctv/sharpest.jpg` | `defaults` | 322.3 | [1140, 1920, 3] uint8 mean 125.4 | ok |
| `cctv/sharpest.jpg` | `length=1.0` | 178.8 | [760, 1920, 3] uint8 mean 125.78 | ok |
| `cctv/sharpest.jpg` | `length=200.0` | 1151.7 | [1140, 1920, 3] uint8 mean 122.68 | ok |
| `cctv/sharpest.jpg` | `angle=-180.0` | 315.4 | [1140, 1920, 3] uint8 mean 125.46 | ok |
| `cctv/sharpest.jpg` | `angle=180.0` | 328.3 | [1140, 1920, 3] uint8 mean 125.45 | ok |
| `cctv/sharpest.jpg` | `noise_power=0.0001` | 347.7 | [1140, 1920, 3] uint8 mean 122.34 | ok |
| `cctv/sharpest.jpg` | `noise_power=0.5` | 323.3 | [1140, 1920, 3] uint8 mean 125.82 | ok |
| `cctv/sharpest.jpg` | `solver=richardson_lucy` | 17002.0 | [1140, 1920, 3] uint8 mean 112.12 | ok |
| `cctv/sharpest.jpg` | `iterations=5` | 282.9 | [1140, 1920, 3] uint8 mean 125.4 | ok |
| `cctv/sharpest.jpg` | `iterations=100` | 289.3 | [1140, 1920, 3] uint8 mean 125.4 | ok |
| `cctv/softest.jpg` | `defaults` | 286.6 | [1140, 1920, 3] uint8 mean 119.6 | ok |
| `cctv/softest.jpg` | `length=1.0` | 176.9 | [760, 1920, 3] uint8 mean 119.82 | ok |
| `cctv/softest.jpg` | `length=200.0` | 1133.8 | [1140, 1920, 3] uint8 mean 110.32 | ok |
| `cctv/softest.jpg` | `angle=-180.0` | 283.5 | [1140, 1920, 3] uint8 mean 119.66 | ok |
| `cctv/softest.jpg` | `angle=180.0` | 284.8 | [1140, 1920, 3] uint8 mean 119.65 | ok |
| `cctv/softest.jpg` | `noise_power=0.0001` | 285.9 | [1140, 1920, 3] uint8 mean 119.57 | ok |
| `cctv/softest.jpg` | `noise_power=0.5` | 287.9 | [1140, 1920, 3] uint8 mean 119.75 | ok |
| `cctv/softest.jpg` | `solver=richardson_lucy` | 15425.6 | [1140, 1920, 3] uint8 mean 116.41 | ok |
| `cctv/softest.jpg` | `iterations=5` | 297.7 | [1140, 1920, 3] uint8 mean 119.6 | ok |
| `cctv/softest.jpg` | `iterations=100` | 319.5 | [1140, 1920, 3] uint8 mean 119.6 | ok |

## Artifacts

Outputs written to `validation/artifacts/deblur_motion_grid/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
