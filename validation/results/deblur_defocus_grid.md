# deblur_defocus_grid - validation result

**Contact sheet of defocus deblurs across radius and noise, for finding a radius that cannot be measured**  
`cv_tools.filters.motion_deblur` | family: Analyze | 2026-10-10T14:15:53

## Verdict

**PASS** - 72 runs, no invariant broken, 2 specific checks passed.

## What this filter specifically promises

- PASS - the middle tile is the estimate itself, at full resolution: tile is pixel-identical to the filter run on its own
- PASS - rows step the radius and columns the noise term: tile is pixel-identical to the filter run on its own

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 250.3 | [1140, 1920, 3] uint8 mean 154.09 | ok |
| `cctv/brightest.jpg` | `radius=0.1` | 80.6 | [380, 1920, 3] uint8 mean 155.77 | ok |
| `cctv/brightest.jpg` | `radius=50.0` | 547.0 | [1140, 1920, 3] uint8 mean 149.54 | ok |
| `cctv/brightest.jpg` | `noise_power=0.0001` | 281.9 | [1140, 1920, 3] uint8 mean 137.04 | ok |
| `cctv/brightest.jpg` | `noise_power=0.5` | 252.0 | [1140, 1920, 3] uint8 mean 156.13 | ok |
| `cctv/brightest.jpg` | `solver=richardson_lucy` | 9848.6 | [1140, 1920, 3] uint8 mean 153.83 | ok |
| `cctv/brightest.jpg` | `iterations=5` | 251.5 | [1140, 1920, 3] uint8 mean 154.09 | ok |
| `cctv/brightest.jpg` | `iterations=100` | 258.7 | [1140, 1920, 3] uint8 mean 154.09 | ok |
| `cctv/darkest.jpg` | `defaults` | 256.0 | [1140, 1920, 3] uint8 mean 105.51 | ok |
| `cctv/darkest.jpg` | `radius=0.1` | 81.0 | [380, 1920, 3] uint8 mean 105.84 | ok |
| `cctv/darkest.jpg` | `radius=50.0` | 540.3 | [1140, 1920, 3] uint8 mean 105.65 | ok |
| `cctv/darkest.jpg` | `noise_power=0.0001` | 262.2 | [1140, 1920, 3] uint8 mean 112.03 | ok |
| `cctv/darkest.jpg` | `noise_power=0.5` | 275.1 | [1140, 1920, 3] uint8 mean 106.02 | ok |
| `cctv/darkest.jpg` | `solver=richardson_lucy` | 9620.8 | [1140, 1920, 3] uint8 mean 102.7 | ok |
| `cctv/darkest.jpg` | `iterations=5` | 257.9 | [1140, 1920, 3] uint8 mean 105.51 | ok |
| `cctv/darkest.jpg` | `iterations=100` | 250.2 | [1140, 1920, 3] uint8 mean 105.51 | ok |
| `cctv/event_fall.jpg` | `defaults` | 254.1 | [1140, 1920, 3] uint8 mean 119.68 | ok |
| `cctv/event_fall.jpg` | `radius=0.1` | 80.6 | [380, 1920, 3] uint8 mean 119.86 | ok |
| `cctv/event_fall.jpg` | `radius=50.0` | 552.7 | [1140, 1920, 3] uint8 mean 119.14 | ok |
| `cctv/event_fall.jpg` | `noise_power=0.0001` | 257.6 | [1140, 1920, 3] uint8 mean 120.6 | ok |
| `cctv/event_fall.jpg` | `noise_power=0.5` | 247.9 | [1140, 1920, 3] uint8 mean 119.9 | ok |
| `cctv/event_fall.jpg` | `solver=richardson_lucy` | 10336.4 | [1140, 1920, 3] uint8 mean 110.26 | ok |
| `cctv/event_fall.jpg` | `iterations=5` | 273.1 | [1140, 1920, 3] uint8 mean 119.68 | ok |
| `cctv/event_fall.jpg` | `iterations=100` | 291.3 | [1140, 1920, 3] uint8 mean 119.68 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 335.6 | [1140, 1920, 3] uint8 mean 119.5 | ok |
| `cctv/event_optflow.jpg` | `radius=0.1` | 93.4 | [380, 1920, 3] uint8 mean 119.79 | ok |
| `cctv/event_optflow.jpg` | `radius=50.0` | 556.8 | [1140, 1920, 3] uint8 mean 119.14 | ok |
| `cctv/event_optflow.jpg` | `noise_power=0.0001` | 249.0 | [1140, 1920, 3] uint8 mean 119.49 | ok |
| `cctv/event_optflow.jpg` | `noise_power=0.5` | 249.9 | [1140, 1920, 3] uint8 mean 119.83 | ok |
| `cctv/event_optflow.jpg` | `solver=richardson_lucy` | 9538.0 | [1140, 1920, 3] uint8 mean 116.44 | ok |
| `cctv/event_optflow.jpg` | `iterations=5` | 249.0 | [1140, 1920, 3] uint8 mean 119.5 | ok |
| `cctv/event_optflow.jpg` | `iterations=100` | 248.2 | [1140, 1920, 3] uint8 mean 119.5 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 258.2 | [1140, 1920, 3] uint8 mean 151.52 | ok |
| `cctv/event_tamper.jpg` | `radius=0.1` | 79.1 | [380, 1920, 3] uint8 mean 153.03 | ok |
| `cctv/event_tamper.jpg` | `radius=50.0` | 545.7 | [1140, 1920, 3] uint8 mean 147.51 | ok |
| `cctv/event_tamper.jpg` | `noise_power=0.0001` | 261.8 | [1140, 1920, 3] uint8 mean 135.82 | ok |
| `cctv/event_tamper.jpg` | `noise_power=0.5` | 249.3 | [1140, 1920, 3] uint8 mean 153.36 | ok |
| `cctv/event_tamper.jpg` | `solver=richardson_lucy` | 9231.8 | [1140, 1920, 3] uint8 mean 151.13 | ok |
| `cctv/event_tamper.jpg` | `iterations=5` | 249.1 | [1140, 1920, 3] uint8 mean 151.52 | ok |
| `cctv/event_tamper.jpg` | `iterations=100` | 245.9 | [1140, 1920, 3] uint8 mean 151.52 | ok |
| `cctv/flattest.jpg` | `defaults` | 254.2 | [1140, 1920, 3] uint8 mean 115.89 | ok |
| `cctv/flattest.jpg` | `radius=0.1` | 95.1 | [380, 1920, 3] uint8 mean 116.06 | ok |
| `cctv/flattest.jpg` | `radius=50.0` | 572.8 | [1140, 1920, 3] uint8 mean 116.26 | ok |
| `cctv/flattest.jpg` | `noise_power=0.0001` | 249.9 | [1140, 1920, 3] uint8 mean 117.6 | ok |
| `cctv/flattest.jpg` | `noise_power=0.5` | 251.0 | [1140, 1920, 3] uint8 mean 116.1 | ok |
| `cctv/flattest.jpg` | `solver=richardson_lucy` | 9080.3 | [1140, 1920, 3] uint8 mean 112.87 | ok |
| `cctv/flattest.jpg` | `iterations=5` | 247.9 | [1140, 1920, 3] uint8 mean 115.89 | ok |
| `cctv/flattest.jpg` | `iterations=100` | 247.9 | [1140, 1920, 3] uint8 mean 115.89 | ok |
| `cctv/most_blown.jpg` | `defaults` | 250.8 | [1140, 1920, 3] uint8 mean 130.51 | ok |
| `cctv/most_blown.jpg` | `radius=0.1` | 79.0 | [380, 1920, 3] uint8 mean 131.74 | ok |
| `cctv/most_blown.jpg` | `radius=50.0` | 555.6 | [1140, 1920, 3] uint8 mean 127.18 | ok |
| `cctv/most_blown.jpg` | `noise_power=0.0001` | 251.6 | [1140, 1920, 3] uint8 mean 125.26 | ok |
| `cctv/most_blown.jpg` | `noise_power=0.5` | 249.0 | [1140, 1920, 3] uint8 mean 131.89 | ok |
| `cctv/most_blown.jpg` | `solver=richardson_lucy` | 9047.0 | [1140, 1920, 3] uint8 mean 128.39 | ok |
| `cctv/most_blown.jpg` | `iterations=5` | 247.2 | [1140, 1920, 3] uint8 mean 130.51 | ok |
| `cctv/most_blown.jpg` | `iterations=100` | 250.0 | [1140, 1920, 3] uint8 mean 130.51 | ok |
| `cctv/sharpest.jpg` | `defaults` | 248.5 | [1140, 1920, 3] uint8 mean 125.43 | ok |
| `cctv/sharpest.jpg` | `radius=0.1` | 79.2 | [380, 1920, 3] uint8 mean 126.39 | ok |
| `cctv/sharpest.jpg` | `radius=50.0` | 546.8 | [1140, 1920, 3] uint8 mean 122.31 | ok |
| `cctv/sharpest.jpg` | `noise_power=0.0001` | 258.6 | [1140, 1920, 3] uint8 mean 122.76 | ok |
| `cctv/sharpest.jpg` | `noise_power=0.5` | 267.2 | [1140, 1920, 3] uint8 mean 125.85 | ok |
| `cctv/sharpest.jpg` | `solver=richardson_lucy` | 9451.5 | [1140, 1920, 3] uint8 mean 116.42 | ok |
| `cctv/sharpest.jpg` | `iterations=5` | 248.7 | [1140, 1920, 3] uint8 mean 125.43 | ok |
| `cctv/sharpest.jpg` | `iterations=100` | 249.8 | [1140, 1920, 3] uint8 mean 125.43 | ok |
| `cctv/softest.jpg` | `defaults` | 248.2 | [1140, 1920, 3] uint8 mean 119.94 | ok |
| `cctv/softest.jpg` | `radius=0.1` | 78.5 | [380, 1920, 3] uint8 mean 119.92 | ok |
| `cctv/softest.jpg` | `radius=50.0` | 535.8 | [1140, 1920, 3] uint8 mean 120.63 | ok |
| `cctv/softest.jpg` | `noise_power=0.0001` | 250.7 | [1140, 1920, 3] uint8 mean 120.33 | ok |
| `cctv/softest.jpg` | `noise_power=0.5` | 256.3 | [1140, 1920, 3] uint8 mean 119.8 | ok |
| `cctv/softest.jpg` | `solver=richardson_lucy` | 9119.2 | [1140, 1920, 3] uint8 mean 118.17 | ok |
| `cctv/softest.jpg` | `iterations=5` | 247.5 | [1140, 1920, 3] uint8 mean 119.94 | ok |
| `cctv/softest.jpg` | `iterations=100` | 252.3 | [1140, 1920, 3] uint8 mean 119.94 | ok |

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
