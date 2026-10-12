# deblur_motion_grid - validation result

**Contact sheet of motion deblurs around an estimated length and angle, for closing in on the right one**  
`cv_tools.filters.motion_deblur` | family: Analyze | 2026-10-10T14:13:01

## Verdict

**PASS** - 90 runs, no invariant broken, 2 specific checks passed.

## What this filter specifically promises

- PASS - the middle tile is the estimate itself, at full resolution: tile is pixel-identical to the filter run on its own
- PASS - rows step the length and columns the angle: tile is pixel-identical to the filter run on its own

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 270.3 | [1140, 1920, 3] uint8 mean 153.5 | ok |
| `cctv/brightest.jpg` | `length=1.0` | 164.8 | [760, 1920, 3] uint8 mean 155.78 | ok |
| `cctv/brightest.jpg` | `length=200.0` | 1045.5 | [1140, 1920, 3] uint8 mean 132.17 | ok |
| `cctv/brightest.jpg` | `angle=-180.0` | 266.0 | [1140, 1920, 3] uint8 mean 153.56 | ok |
| `cctv/brightest.jpg` | `angle=180.0` | 283.2 | [1140, 1920, 3] uint8 mean 153.55 | ok |
| `cctv/brightest.jpg` | `noise_power=0.0001` | 273.6 | [1140, 1920, 3] uint8 mean 138.31 | ok |
| `cctv/brightest.jpg` | `noise_power=0.5` | 301.6 | [1140, 1920, 3] uint8 mean 156.08 | ok |
| `cctv/brightest.jpg` | `solver=richardson_lucy` | 14723.1 | [1140, 1920, 3] uint8 mean 151.47 | ok |
| `cctv/brightest.jpg` | `iterations=5` | 274.6 | [1140, 1920, 3] uint8 mean 153.5 | ok |
| `cctv/brightest.jpg` | `iterations=100` | 264.8 | [1140, 1920, 3] uint8 mean 153.5 | ok |
| `cctv/darkest.jpg` | `defaults` | 266.2 | [1140, 1920, 3] uint8 mean 104.96 | ok |
| `cctv/darkest.jpg` | `length=1.0` | 162.0 | [760, 1920, 3] uint8 mean 105.8 | ok |
| `cctv/darkest.jpg` | `length=200.0` | 1057.5 | [1140, 1920, 3] uint8 mean 102.68 | ok |
| `cctv/darkest.jpg` | `angle=-180.0` | 278.8 | [1140, 1920, 3] uint8 mean 105.02 | ok |
| `cctv/darkest.jpg` | `angle=180.0` | 335.3 | [1140, 1920, 3] uint8 mean 105.01 | ok |
| `cctv/darkest.jpg` | `noise_power=0.0001` | 277.1 | [1140, 1920, 3] uint8 mean 110.65 | ok |
| `cctv/darkest.jpg` | `noise_power=0.5` | 289.3 | [1140, 1920, 3] uint8 mean 105.98 | ok |
| `cctv/darkest.jpg` | `solver=richardson_lucy` | 15174.7 | [1140, 1920, 3] uint8 mean 100.94 | ok |
| `cctv/darkest.jpg` | `iterations=5` | 266.4 | [1140, 1920, 3] uint8 mean 104.96 | ok |
| `cctv/darkest.jpg` | `iterations=100` | 282.3 | [1140, 1920, 3] uint8 mean 104.96 | ok |
| `cctv/event_fall.jpg` | `defaults` | 305.2 | [1140, 1920, 3] uint8 mean 119.51 | ok |
| `cctv/event_fall.jpg` | `length=1.0` | 164.8 | [760, 1920, 3] uint8 mean 119.8 | ok |
| `cctv/event_fall.jpg` | `length=200.0` | 1049.4 | [1140, 1920, 3] uint8 mean 121.43 | ok |
| `cctv/event_fall.jpg` | `angle=-180.0` | 266.3 | [1140, 1920, 3] uint8 mean 119.57 | ok |
| `cctv/event_fall.jpg` | `angle=180.0` | 265.6 | [1140, 1920, 3] uint8 mean 119.56 | ok |
| `cctv/event_fall.jpg` | `noise_power=0.0001` | 287.6 | [1140, 1920, 3] uint8 mean 119.98 | ok |
| `cctv/event_fall.jpg` | `noise_power=0.5` | 288.7 | [1140, 1920, 3] uint8 mean 119.89 | ok |
| `cctv/event_fall.jpg` | `solver=richardson_lucy` | 15006.3 | [1140, 1920, 3] uint8 mean 105.65 | ok |
| `cctv/event_fall.jpg` | `iterations=5` | 281.7 | [1140, 1920, 3] uint8 mean 119.51 | ok |
| `cctv/event_fall.jpg` | `iterations=100` | 287.5 | [1140, 1920, 3] uint8 mean 119.51 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 299.9 | [1140, 1920, 3] uint8 mean 119.35 | ok |
| `cctv/event_optflow.jpg` | `length=1.0` | 173.7 | [760, 1920, 3] uint8 mean 119.78 | ok |
| `cctv/event_optflow.jpg` | `length=200.0` | 1098.0 | [1140, 1920, 3] uint8 mean 121.46 | ok |
| `cctv/event_optflow.jpg` | `angle=-180.0` | 266.6 | [1140, 1920, 3] uint8 mean 119.41 | ok |
| `cctv/event_optflow.jpg` | `angle=180.0` | 267.5 | [1140, 1920, 3] uint8 mean 119.4 | ok |
| `cctv/event_optflow.jpg` | `noise_power=0.0001` | 268.3 | [1140, 1920, 3] uint8 mean 118.58 | ok |
| `cctv/event_optflow.jpg` | `noise_power=0.5` | 266.4 | [1140, 1920, 3] uint8 mean 119.8 | ok |
| `cctv/event_optflow.jpg` | `solver=richardson_lucy` | 15678.8 | [1140, 1920, 3] uint8 mean 114.38 | ok |
| `cctv/event_optflow.jpg` | `iterations=5` | 270.2 | [1140, 1920, 3] uint8 mean 119.35 | ok |
| `cctv/event_optflow.jpg` | `iterations=100` | 279.8 | [1140, 1920, 3] uint8 mean 119.35 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 267.4 | [1140, 1920, 3] uint8 mean 150.96 | ok |
| `cctv/event_tamper.jpg` | `length=1.0` | 162.1 | [760, 1920, 3] uint8 mean 153.04 | ok |
| `cctv/event_tamper.jpg` | `length=200.0` | 1054.8 | [1140, 1920, 3] uint8 mean 130.66 | ok |
| `cctv/event_tamper.jpg` | `angle=-180.0` | 315.0 | [1140, 1920, 3] uint8 mean 151.02 | ok |
| `cctv/event_tamper.jpg` | `angle=180.0` | 282.3 | [1140, 1920, 3] uint8 mean 151.01 | ok |
| `cctv/event_tamper.jpg` | `noise_power=0.0001` | 283.5 | [1140, 1920, 3] uint8 mean 136.92 | ok |
| `cctv/event_tamper.jpg` | `noise_power=0.5` | 289.0 | [1140, 1920, 3] uint8 mean 153.31 | ok |
| `cctv/event_tamper.jpg` | `solver=richardson_lucy` | 14727.9 | [1140, 1920, 3] uint8 mean 148.83 | ok |
| `cctv/event_tamper.jpg` | `iterations=5` | 271.6 | [1140, 1920, 3] uint8 mean 150.96 | ok |
| `cctv/event_tamper.jpg` | `iterations=100` | 272.1 | [1140, 1920, 3] uint8 mean 150.96 | ok |
| `cctv/flattest.jpg` | `defaults` | 264.2 | [1140, 1920, 3] uint8 mean 115.74 | ok |
| `cctv/flattest.jpg` | `length=1.0` | 177.0 | [760, 1920, 3] uint8 mean 116.05 | ok |
| `cctv/flattest.jpg` | `length=200.0` | 1045.5 | [1140, 1920, 3] uint8 mean 118.89 | ok |
| `cctv/flattest.jpg` | `angle=-180.0` | 280.7 | [1140, 1920, 3] uint8 mean 115.8 | ok |
| `cctv/flattest.jpg` | `angle=180.0` | 273.6 | [1140, 1920, 3] uint8 mean 115.79 | ok |
| `cctv/flattest.jpg` | `noise_power=0.0001` | 281.1 | [1140, 1920, 3] uint8 mean 116.62 | ok |
| `cctv/flattest.jpg` | `noise_power=0.5` | 318.4 | [1140, 1920, 3] uint8 mean 116.06 | ok |
| `cctv/flattest.jpg` | `solver=richardson_lucy` | 14511.8 | [1140, 1920, 3] uint8 mean 110.95 | ok |
| `cctv/flattest.jpg` | `iterations=5` | 265.9 | [1140, 1920, 3] uint8 mean 115.74 | ok |
| `cctv/flattest.jpg` | `iterations=100` | 266.7 | [1140, 1920, 3] uint8 mean 115.74 | ok |
| `cctv/most_blown.jpg` | `defaults` | 323.7 | [1140, 1920, 3] uint8 mean 130.1 | ok |
| `cctv/most_blown.jpg` | `length=1.0` | 161.2 | [760, 1920, 3] uint8 mean 131.66 | ok |
| `cctv/most_blown.jpg` | `length=200.0` | 1049.3 | [1140, 1920, 3] uint8 mean 121.57 | ok |
| `cctv/most_blown.jpg` | `angle=-180.0` | 327.7 | [1140, 1920, 3] uint8 mean 130.16 | ok |
| `cctv/most_blown.jpg` | `angle=180.0` | 305.9 | [1140, 1920, 3] uint8 mean 130.14 | ok |
| `cctv/most_blown.jpg` | `noise_power=0.0001` | 284.5 | [1140, 1920, 3] uint8 mean 125.54 | ok |
| `cctv/most_blown.jpg` | `noise_power=0.5` | 289.2 | [1140, 1920, 3] uint8 mean 131.84 | ok |
| `cctv/most_blown.jpg` | `solver=richardson_lucy` | 15109.1 | [1140, 1920, 3] uint8 mean 126.48 | ok |
| `cctv/most_blown.jpg` | `iterations=5` | 265.0 | [1140, 1920, 3] uint8 mean 130.1 | ok |
| `cctv/most_blown.jpg` | `iterations=100` | 268.1 | [1140, 1920, 3] uint8 mean 130.1 | ok |
| `cctv/sharpest.jpg` | `defaults` | 267.8 | [1140, 1920, 3] uint8 mean 125.4 | ok |
| `cctv/sharpest.jpg` | `length=1.0` | 169.4 | [760, 1920, 3] uint8 mean 125.78 | ok |
| `cctv/sharpest.jpg` | `length=200.0` | 1146.1 | [1140, 1920, 3] uint8 mean 122.68 | ok |
| `cctv/sharpest.jpg` | `angle=-180.0` | 296.8 | [1140, 1920, 3] uint8 mean 125.46 | ok |
| `cctv/sharpest.jpg` | `angle=180.0` | 293.9 | [1140, 1920, 3] uint8 mean 125.45 | ok |
| `cctv/sharpest.jpg` | `noise_power=0.0001` | 280.6 | [1140, 1920, 3] uint8 mean 122.34 | ok |
| `cctv/sharpest.jpg` | `noise_power=0.5` | 268.7 | [1140, 1920, 3] uint8 mean 125.82 | ok |
| `cctv/sharpest.jpg` | `solver=richardson_lucy` | 14225.0 | [1140, 1920, 3] uint8 mean 112.12 | ok |
| `cctv/sharpest.jpg` | `iterations=5` | 266.3 | [1140, 1920, 3] uint8 mean 125.4 | ok |
| `cctv/sharpest.jpg` | `iterations=100` | 277.0 | [1140, 1920, 3] uint8 mean 125.4 | ok |
| `cctv/softest.jpg` | `defaults` | 272.1 | [1140, 1920, 3] uint8 mean 119.6 | ok |
| `cctv/softest.jpg` | `length=1.0` | 165.9 | [760, 1920, 3] uint8 mean 119.82 | ok |
| `cctv/softest.jpg` | `length=200.0` | 1060.8 | [1140, 1920, 3] uint8 mean 110.32 | ok |
| `cctv/softest.jpg` | `angle=-180.0` | 319.6 | [1140, 1920, 3] uint8 mean 119.66 | ok |
| `cctv/softest.jpg` | `angle=180.0` | 267.8 | [1140, 1920, 3] uint8 mean 119.65 | ok |
| `cctv/softest.jpg` | `noise_power=0.0001` | 274.3 | [1140, 1920, 3] uint8 mean 119.57 | ok |
| `cctv/softest.jpg` | `noise_power=0.5` | 328.8 | [1140, 1920, 3] uint8 mean 119.75 | ok |
| `cctv/softest.jpg` | `solver=richardson_lucy` | 14761.5 | [1140, 1920, 3] uint8 mean 116.41 | ok |
| `cctv/softest.jpg` | `iterations=5` | 266.1 | [1140, 1920, 3] uint8 mean 119.6 | ok |
| `cctv/softest.jpg` | `iterations=100` | 273.6 | [1140, 1920, 3] uint8 mean 119.6 | ok |

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
