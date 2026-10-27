# deblur_defocus_grid - validation result

**Contact sheet of defocus deblurs across radius and noise, for finding a radius that cannot be measured**  
`cv_tools.filters.motion_deblur` | family: Analyze | 2026-10-12T19:07:20

## Verdict

**PASS** - 72 runs, no invariant broken, 2 specific checks passed.

## What this filter specifically promises

- PASS - the middle tile is the estimate itself, at full resolution: tile is pixel-identical to the filter run on its own
- PASS - rows step the radius and columns the noise term: tile is pixel-identical to the filter run on its own

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 285.3 | [1140, 1920, 3] uint8 mean 154.09 | ok |
| `cctv/brightest.jpg` | `radius=0.1` | 87.0 | [380, 1920, 3] uint8 mean 155.77 | ok |
| `cctv/brightest.jpg` | `radius=50.0` | 587.8 | [1140, 1920, 3] uint8 mean 149.54 | ok |
| `cctv/brightest.jpg` | `noise_power=0.0001` | 277.0 | [1140, 1920, 3] uint8 mean 137.04 | ok |
| `cctv/brightest.jpg` | `noise_power=0.5` | 272.0 | [1140, 1920, 3] uint8 mean 156.13 | ok |
| `cctv/brightest.jpg` | `solver=richardson_lucy` | 10772.6 | [1140, 1920, 3] uint8 mean 153.83 | ok |
| `cctv/brightest.jpg` | `iterations=5` | 268.8 | [1140, 1920, 3] uint8 mean 154.09 | ok |
| `cctv/brightest.jpg` | `iterations=100` | 268.5 | [1140, 1920, 3] uint8 mean 154.09 | ok |
| `cctv/darkest.jpg` | `defaults` | 268.8 | [1140, 1920, 3] uint8 mean 105.51 | ok |
| `cctv/darkest.jpg` | `radius=0.1` | 86.7 | [380, 1920, 3] uint8 mean 105.84 | ok |
| `cctv/darkest.jpg` | `radius=50.0` | 593.5 | [1140, 1920, 3] uint8 mean 105.65 | ok |
| `cctv/darkest.jpg` | `noise_power=0.0001` | 272.9 | [1140, 1920, 3] uint8 mean 112.03 | ok |
| `cctv/darkest.jpg` | `noise_power=0.5` | 275.6 | [1140, 1920, 3] uint8 mean 106.02 | ok |
| `cctv/darkest.jpg` | `solver=richardson_lucy` | 10330.7 | [1140, 1920, 3] uint8 mean 102.7 | ok |
| `cctv/darkest.jpg` | `iterations=5` | 271.4 | [1140, 1920, 3] uint8 mean 105.51 | ok |
| `cctv/darkest.jpg` | `iterations=100` | 263.9 | [1140, 1920, 3] uint8 mean 105.51 | ok |
| `cctv/event_fall.jpg` | `defaults` | 269.1 | [1140, 1920, 3] uint8 mean 119.68 | ok |
| `cctv/event_fall.jpg` | `radius=0.1` | 84.4 | [380, 1920, 3] uint8 mean 119.86 | ok |
| `cctv/event_fall.jpg` | `radius=50.0` | 584.3 | [1140, 1920, 3] uint8 mean 119.14 | ok |
| `cctv/event_fall.jpg` | `noise_power=0.0001` | 263.2 | [1140, 1920, 3] uint8 mean 120.6 | ok |
| `cctv/event_fall.jpg` | `noise_power=0.5` | 266.4 | [1140, 1920, 3] uint8 mean 119.9 | ok |
| `cctv/event_fall.jpg` | `solver=richardson_lucy` | 9681.4 | [1140, 1920, 3] uint8 mean 110.26 | ok |
| `cctv/event_fall.jpg` | `iterations=5` | 264.6 | [1140, 1920, 3] uint8 mean 119.68 | ok |
| `cctv/event_fall.jpg` | `iterations=100` | 260.1 | [1140, 1920, 3] uint8 mean 119.68 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 267.8 | [1140, 1920, 3] uint8 mean 119.5 | ok |
| `cctv/event_optflow.jpg` | `radius=0.1` | 85.0 | [380, 1920, 3] uint8 mean 119.79 | ok |
| `cctv/event_optflow.jpg` | `radius=50.0` | 568.8 | [1140, 1920, 3] uint8 mean 119.14 | ok |
| `cctv/event_optflow.jpg` | `noise_power=0.0001` | 266.4 | [1140, 1920, 3] uint8 mean 119.49 | ok |
| `cctv/event_optflow.jpg` | `noise_power=0.5` | 266.0 | [1140, 1920, 3] uint8 mean 119.83 | ok |
| `cctv/event_optflow.jpg` | `solver=richardson_lucy` | 9519.4 | [1140, 1920, 3] uint8 mean 116.44 | ok |
| `cctv/event_optflow.jpg` | `iterations=5` | 262.7 | [1140, 1920, 3] uint8 mean 119.5 | ok |
| `cctv/event_optflow.jpg` | `iterations=100` | 268.0 | [1140, 1920, 3] uint8 mean 119.5 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 273.8 | [1140, 1920, 3] uint8 mean 151.52 | ok |
| `cctv/event_tamper.jpg` | `radius=0.1` | 85.5 | [380, 1920, 3] uint8 mean 153.03 | ok |
| `cctv/event_tamper.jpg` | `radius=50.0` | 570.3 | [1140, 1920, 3] uint8 mean 147.51 | ok |
| `cctv/event_tamper.jpg` | `noise_power=0.0001` | 331.6 | [1140, 1920, 3] uint8 mean 135.82 | ok |
| `cctv/event_tamper.jpg` | `noise_power=0.5` | 263.2 | [1140, 1920, 3] uint8 mean 153.36 | ok |
| `cctv/event_tamper.jpg` | `solver=richardson_lucy` | 9574.6 | [1140, 1920, 3] uint8 mean 151.13 | ok |
| `cctv/event_tamper.jpg` | `iterations=5` | 265.9 | [1140, 1920, 3] uint8 mean 151.52 | ok |
| `cctv/event_tamper.jpg` | `iterations=100` | 263.4 | [1140, 1920, 3] uint8 mean 151.52 | ok |
| `cctv/flattest.jpg` | `defaults` | 271.7 | [1140, 1920, 3] uint8 mean 115.89 | ok |
| `cctv/flattest.jpg` | `radius=0.1` | 83.4 | [380, 1920, 3] uint8 mean 116.06 | ok |
| `cctv/flattest.jpg` | `radius=50.0` | 569.7 | [1140, 1920, 3] uint8 mean 116.26 | ok |
| `cctv/flattest.jpg` | `noise_power=0.0001` | 262.5 | [1140, 1920, 3] uint8 mean 117.6 | ok |
| `cctv/flattest.jpg` | `noise_power=0.5` | 259.3 | [1140, 1920, 3] uint8 mean 116.1 | ok |
| `cctv/flattest.jpg` | `solver=richardson_lucy` | 9626.6 | [1140, 1920, 3] uint8 mean 112.87 | ok |
| `cctv/flattest.jpg` | `iterations=5` | 267.3 | [1140, 1920, 3] uint8 mean 115.89 | ok |
| `cctv/flattest.jpg` | `iterations=100` | 266.7 | [1140, 1920, 3] uint8 mean 115.89 | ok |
| `cctv/most_blown.jpg` | `defaults` | 267.5 | [1140, 1920, 3] uint8 mean 130.51 | ok |
| `cctv/most_blown.jpg` | `radius=0.1` | 87.8 | [380, 1920, 3] uint8 mean 131.74 | ok |
| `cctv/most_blown.jpg` | `radius=50.0` | 565.8 | [1140, 1920, 3] uint8 mean 127.18 | ok |
| `cctv/most_blown.jpg` | `noise_power=0.0001` | 261.4 | [1140, 1920, 3] uint8 mean 125.26 | ok |
| `cctv/most_blown.jpg` | `noise_power=0.5` | 264.2 | [1140, 1920, 3] uint8 mean 131.89 | ok |
| `cctv/most_blown.jpg` | `solver=richardson_lucy` | 9559.4 | [1140, 1920, 3] uint8 mean 128.39 | ok |
| `cctv/most_blown.jpg` | `iterations=5` | 274.1 | [1140, 1920, 3] uint8 mean 130.51 | ok |
| `cctv/most_blown.jpg` | `iterations=100` | 270.2 | [1140, 1920, 3] uint8 mean 130.51 | ok |
| `cctv/sharpest.jpg` | `defaults` | 273.2 | [1140, 1920, 3] uint8 mean 125.43 | ok |
| `cctv/sharpest.jpg` | `radius=0.1` | 83.2 | [380, 1920, 3] uint8 mean 126.39 | ok |
| `cctv/sharpest.jpg` | `radius=50.0` | 562.3 | [1140, 1920, 3] uint8 mean 122.31 | ok |
| `cctv/sharpest.jpg` | `noise_power=0.0001` | 265.2 | [1140, 1920, 3] uint8 mean 122.76 | ok |
| `cctv/sharpest.jpg` | `noise_power=0.5` | 264.3 | [1140, 1920, 3] uint8 mean 125.85 | ok |
| `cctv/sharpest.jpg` | `solver=richardson_lucy` | 9538.7 | [1140, 1920, 3] uint8 mean 116.42 | ok |
| `cctv/sharpest.jpg` | `iterations=5` | 269.9 | [1140, 1920, 3] uint8 mean 125.43 | ok |
| `cctv/sharpest.jpg` | `iterations=100` | 264.6 | [1140, 1920, 3] uint8 mean 125.43 | ok |
| `cctv/softest.jpg` | `defaults` | 265.5 | [1140, 1920, 3] uint8 mean 119.94 | ok |
| `cctv/softest.jpg` | `radius=0.1` | 88.6 | [380, 1920, 3] uint8 mean 119.92 | ok |
| `cctv/softest.jpg` | `radius=50.0` | 582.5 | [1140, 1920, 3] uint8 mean 120.63 | ok |
| `cctv/softest.jpg` | `noise_power=0.0001` | 268.7 | [1140, 1920, 3] uint8 mean 120.33 | ok |
| `cctv/softest.jpg` | `noise_power=0.5` | 262.8 | [1140, 1920, 3] uint8 mean 119.8 | ok |
| `cctv/softest.jpg` | `solver=richardson_lucy` | 9571.7 | [1140, 1920, 3] uint8 mean 118.17 | ok |
| `cctv/softest.jpg` | `iterations=5` | 265.6 | [1140, 1920, 3] uint8 mean 119.94 | ok |
| `cctv/softest.jpg` | `iterations=100` | 272.3 | [1140, 1920, 3] uint8 mean 119.94 | ok |

## Artifacts

Outputs written to `validation/artifacts/deblur_defocus_grid/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
