# deblur_turbulence - validation result

**Deconvolution of air turbulence blur: heat haze over a long sight line**  
`cv_tools.filters.motion_deblur` | family: Forensic | 2026-10-12T19:11:07

## Verdict

**PASS** - 72 runs, no invariant broken.

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 32.2 | [362, 640, 3] uint8 mean 163.11 | ok |
| `cctv/brightest.jpg` | `size=0.5` | 27.5 | [362, 640, 3] uint8 mean 163.51 | ok |
| `cctv/brightest.jpg` | `size=20.0` | 94.1 | [362, 640, 3] uint8 mean 162.49 | ok |
| `cctv/brightest.jpg` | `noise_power=0.0001` | 30.9 | [362, 640, 3] uint8 mean 153.85 | ok |
| `cctv/brightest.jpg` | `noise_power=0.5` | 31.2 | [362, 640, 3] uint8 mean 163.58 | ok |
| `cctv/brightest.jpg` | `solver=richardson_lucy` | 1733.5 | [362, 640, 3] uint8 mean 161.3 | ok |
| `cctv/brightest.jpg` | `iterations=5` | 32.4 | [362, 640, 3] uint8 mean 163.11 | ok |
| `cctv/brightest.jpg` | `iterations=100` | 33.0 | [362, 640, 3] uint8 mean 163.11 | ok |
| `cctv/darkest.jpg` | `defaults` | 32.1 | [362, 640, 3] uint8 mean 110.82 | ok |
| `cctv/darkest.jpg` | `size=0.5` | 28.2 | [362, 640, 3] uint8 mean 110.92 | ok |
| `cctv/darkest.jpg` | `size=20.0` | 94.5 | [362, 640, 3] uint8 mean 110.97 | ok |
| `cctv/darkest.jpg` | `noise_power=0.0001` | 32.3 | [362, 640, 3] uint8 mean 113.18 | ok |
| `cctv/darkest.jpg` | `noise_power=0.5` | 32.8 | [362, 640, 3] uint8 mean 110.96 | ok |
| `cctv/darkest.jpg` | `solver=richardson_lucy` | 1723.1 | [362, 640, 3] uint8 mean 107.76 | ok |
| `cctv/darkest.jpg` | `iterations=5` | 32.9 | [362, 640, 3] uint8 mean 110.82 | ok |
| `cctv/darkest.jpg` | `iterations=100` | 32.6 | [362, 640, 3] uint8 mean 110.82 | ok |
| `cctv/event_fall.jpg` | `defaults` | 32.3 | [362, 640, 3] uint8 mean 126.12 | ok |
| `cctv/event_fall.jpg` | `size=0.5` | 28.0 | [362, 640, 3] uint8 mean 125.55 | ok |
| `cctv/event_fall.jpg` | `size=20.0` | 93.2 | [362, 640, 3] uint8 mean 128.17 | ok |
| `cctv/event_fall.jpg` | `noise_power=0.0001` | 31.9 | [362, 640, 3] uint8 mean 126.38 | ok |
| `cctv/event_fall.jpg` | `noise_power=0.5` | 32.2 | [362, 640, 3] uint8 mean 125.57 | ok |
| `cctv/event_fall.jpg` | `solver=richardson_lucy` | 1746.3 | [362, 640, 3] uint8 mean 116.99 | ok |
| `cctv/event_fall.jpg` | `iterations=5` | 31.3 | [362, 640, 3] uint8 mean 126.12 | ok |
| `cctv/event_fall.jpg` | `iterations=100` | 31.9 | [362, 640, 3] uint8 mean 126.12 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 31.2 | [362, 640, 3] uint8 mean 125.61 | ok |
| `cctv/event_optflow.jpg` | `size=0.5` | 27.6 | [362, 640, 3] uint8 mean 125.41 | ok |
| `cctv/event_optflow.jpg` | `size=20.0` | 93.4 | [362, 640, 3] uint8 mean 127.32 | ok |
| `cctv/event_optflow.jpg` | `noise_power=0.0001` | 32.3 | [362, 640, 3] uint8 mean 125.12 | ok |
| `cctv/event_optflow.jpg` | `noise_power=0.5` | 32.3 | [362, 640, 3] uint8 mean 125.46 | ok |
| `cctv/event_optflow.jpg` | `solver=richardson_lucy` | 1753.5 | [362, 640, 3] uint8 mean 122.3 | ok |
| `cctv/event_optflow.jpg` | `iterations=5` | 32.2 | [362, 640, 3] uint8 mean 125.61 | ok |
| `cctv/event_optflow.jpg` | `iterations=100` | 32.1 | [362, 640, 3] uint8 mean 125.61 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 32.3 | [362, 640, 3] uint8 mean 160.23 | ok |
| `cctv/event_tamper.jpg` | `size=0.5` | 27.6 | [362, 640, 3] uint8 mean 160.61 | ok |
| `cctv/event_tamper.jpg` | `size=20.0` | 92.6 | [362, 640, 3] uint8 mean 159.72 | ok |
| `cctv/event_tamper.jpg` | `noise_power=0.0001` | 32.5 | [362, 640, 3] uint8 mean 151.49 | ok |
| `cctv/event_tamper.jpg` | `noise_power=0.5` | 32.9 | [362, 640, 3] uint8 mean 160.67 | ok |
| `cctv/event_tamper.jpg` | `solver=richardson_lucy` | 1750.9 | [362, 640, 3] uint8 mean 158.43 | ok |
| `cctv/event_tamper.jpg` | `iterations=5` | 31.5 | [362, 640, 3] uint8 mean 160.23 | ok |
| `cctv/event_tamper.jpg` | `iterations=100` | 32.7 | [362, 640, 3] uint8 mean 160.23 | ok |
| `cctv/flattest.jpg` | `defaults` | 31.9 | [362, 640, 3] uint8 mean 121.68 | ok |
| `cctv/flattest.jpg` | `size=0.5` | 31.2 | [362, 640, 3] uint8 mean 121.49 | ok |
| `cctv/flattest.jpg` | `size=20.0` | 94.5 | [362, 640, 3] uint8 mean 123.43 | ok |
| `cctv/flattest.jpg` | `noise_power=0.0001` | 32.7 | [362, 640, 3] uint8 mean 121.78 | ok |
| `cctv/flattest.jpg` | `noise_power=0.5` | 32.8 | [362, 640, 3] uint8 mean 121.54 | ok |
| `cctv/flattest.jpg` | `solver=richardson_lucy` | 1741.0 | [362, 640, 3] uint8 mean 118.51 | ok |
| `cctv/flattest.jpg` | `iterations=5` | 33.1 | [362, 640, 3] uint8 mean 121.68 | ok |
| `cctv/flattest.jpg` | `iterations=100` | 34.8 | [362, 640, 3] uint8 mean 121.68 | ok |
| `cctv/most_blown.jpg` | `defaults` | 31.4 | [362, 640, 3] uint8 mean 137.96 | ok |
| `cctv/most_blown.jpg` | `size=0.5` | 27.7 | [362, 640, 3] uint8 mean 138.07 | ok |
| `cctv/most_blown.jpg` | `size=20.0` | 91.5 | [362, 640, 3] uint8 mean 137.73 | ok |
| `cctv/most_blown.jpg` | `noise_power=0.0001` | 31.8 | [362, 640, 3] uint8 mean 137.23 | ok |
| `cctv/most_blown.jpg` | `noise_power=0.5` | 32.5 | [362, 640, 3] uint8 mean 138.12 | ok |
| `cctv/most_blown.jpg` | `solver=richardson_lucy` | 1749.7 | [362, 640, 3] uint8 mean 134.76 | ok |
| `cctv/most_blown.jpg` | `iterations=5` | 33.4 | [362, 640, 3] uint8 mean 137.96 | ok |
| `cctv/most_blown.jpg` | `iterations=100` | 32.7 | [362, 640, 3] uint8 mean 137.96 | ok |
| `cctv/sharpest.jpg` | `defaults` | 32.7 | [362, 640, 3] uint8 mean 133.09 | ok |
| `cctv/sharpest.jpg` | `size=0.5` | 28.5 | [362, 640, 3] uint8 mean 131.84 | ok |
| `cctv/sharpest.jpg` | `size=20.0` | 93.4 | [362, 640, 3] uint8 mean 133.3 | ok |
| `cctv/sharpest.jpg` | `noise_power=0.0001` | 31.4 | [362, 640, 3] uint8 mean 132.69 | ok |
| `cctv/sharpest.jpg` | `noise_power=0.5` | 32.5 | [362, 640, 3] uint8 mean 131.8 | ok |
| `cctv/sharpest.jpg` | `solver=richardson_lucy` | 1740.8 | [362, 640, 3] uint8 mean 123.24 | ok |
| `cctv/sharpest.jpg` | `iterations=5` | 32.8 | [362, 640, 3] uint8 mean 133.09 | ok |
| `cctv/sharpest.jpg` | `iterations=100` | 33.5 | [362, 640, 3] uint8 mean 133.09 | ok |
| `cctv/softest.jpg` | `defaults` | 31.9 | [362, 640, 3] uint8 mean 125.76 | ok |
| `cctv/softest.jpg` | `size=0.5` | 28.3 | [362, 640, 3] uint8 mean 125.4 | ok |
| `cctv/softest.jpg` | `size=20.0` | 93.2 | [362, 640, 3] uint8 mean 126.7 | ok |
| `cctv/softest.jpg` | `noise_power=0.0001` | 33.2 | [362, 640, 3] uint8 mean 125.16 | ok |
| `cctv/softest.jpg` | `noise_power=0.5` | 32.5 | [362, 640, 3] uint8 mean 125.42 | ok |
| `cctv/softest.jpg` | `solver=richardson_lucy` | 1769.8 | [362, 640, 3] uint8 mean 123.61 | ok |
| `cctv/softest.jpg` | `iterations=5` | 35.9 | [362, 640, 3] uint8 mean 125.76 | ok |
| `cctv/softest.jpg` | `iterations=100` | 39.5 | [362, 640, 3] uint8 mean 125.76 | ok |

## Artifacts

Outputs written to `validation/artifacts/deblur_turbulence/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
