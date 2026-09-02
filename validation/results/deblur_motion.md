# deblur_motion - validation result

**Wiener deconvolution of linear motion blur**  
`cv_tools.filters.motion_deblur` | family: Forensic | 2026-09-01T16:36:51

## Verdict

**PASS** - 70 runs, no invariant broken, 2 specific checks passed.

## What this filter specifically promises

- PASS - some PSF raises high-frequency energy on a truly blurred plate: Laplacian variance 11 -> 176 at the best of 6 PSF guesses
- PASS - a wrong PSF still changes the image rather than passing it through: output differs from input at 45 degrees

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 117.1 | [362, 640, 3] uint8 mean 159.17 | ok |
| `cctv/brightest.jpg` | `length=1.0` | 128.1 | [362, 640, 3] uint8 mean 161.34 | ok |
| `cctv/brightest.jpg` | `length=64.0` | 191.5 | [362, 640, 3] uint8 mean 157.75 | ok |
| `cctv/brightest.jpg` | `angle=-180.0` | 122.0 | [362, 640, 3] uint8 mean 159.17 | ok |
| `cctv/brightest.jpg` | `angle=180.0` | 114.0 | [362, 640, 3] uint8 mean 159.17 | ok |
| `cctv/brightest.jpg` | `noise_power=0.0001` | 120.1 | [362, 640, 3] uint8 mean 145.32 | ok |
| `cctv/brightest.jpg` | `noise_power=0.5` | 136.6 | [362, 640, 3] uint8 mean 108.62 | ok |
| `cctv/darkest.jpg` | `defaults` | 122.6 | [362, 640, 3] uint8 mean 108.57 | ok |
| `cctv/darkest.jpg` | `length=1.0` | 127.4 | [362, 640, 3] uint8 mean 109.29 | ok |
| `cctv/darkest.jpg` | `length=64.0` | 154.0 | [362, 640, 3] uint8 mean 106.72 | ok |
| `cctv/darkest.jpg` | `angle=-180.0` | 116.8 | [362, 640, 3] uint8 mean 108.57 | ok |
| `cctv/darkest.jpg` | `angle=180.0` | 115.7 | [362, 640, 3] uint8 mean 108.57 | ok |
| `cctv/darkest.jpg` | `noise_power=0.0001` | 119.3 | [362, 640, 3] uint8 mean 117.16 | ok |
| `cctv/darkest.jpg` | `noise_power=0.5` | 118.4 | [362, 640, 3] uint8 mean 73.51 | ok |
| `cctv/event_fall.jpg` | `defaults` | 120.4 | [362, 640, 3] uint8 mean 123.98 | ok |
| `cctv/event_fall.jpg` | `length=1.0` | 130.5 | [362, 640, 3] uint8 mean 123.74 | ok |
| `cctv/event_fall.jpg` | `length=64.0` | 152.6 | [362, 640, 3] uint8 mean 124.23 | ok |
| `cctv/event_fall.jpg` | `angle=-180.0` | 117.9 | [362, 640, 3] uint8 mean 123.98 | ok |
| `cctv/event_fall.jpg` | `angle=180.0` | 121.6 | [362, 640, 3] uint8 mean 123.98 | ok |
| `cctv/event_fall.jpg` | `noise_power=0.0001` | 114.1 | [362, 640, 3] uint8 mean 125.54 | ok |
| `cctv/event_fall.jpg` | `noise_power=0.5` | 131.8 | [362, 640, 3] uint8 mean 83.26 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 116.2 | [362, 640, 3] uint8 mean 123.5 | ok |
| `cctv/event_optflow.jpg` | `length=1.0` | 120.3 | [362, 640, 3] uint8 mean 123.66 | ok |
| `cctv/event_optflow.jpg` | `length=64.0` | 144.2 | [362, 640, 3] uint8 mean 124.41 | ok |
| `cctv/event_optflow.jpg` | `angle=-180.0` | 116.4 | [362, 640, 3] uint8 mean 123.5 | ok |
| `cctv/event_optflow.jpg` | `angle=180.0` | 118.9 | [362, 640, 3] uint8 mean 123.5 | ok |
| `cctv/event_optflow.jpg` | `noise_power=0.0001` | 116.3 | [362, 640, 3] uint8 mean 125.25 | ok |
| `cctv/event_optflow.jpg` | `noise_power=0.5` | 136.9 | [362, 640, 3] uint8 mean 83.17 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 123.0 | [362, 640, 3] uint8 mean 156.49 | ok |
| `cctv/event_tamper.jpg` | `length=1.0` | 129.0 | [362, 640, 3] uint8 mean 158.46 | ok |
| `cctv/event_tamper.jpg` | `length=64.0` | 152.5 | [362, 640, 3] uint8 mean 155.38 | ok |
| `cctv/event_tamper.jpg` | `angle=-180.0` | 129.7 | [362, 640, 3] uint8 mean 156.49 | ok |
| `cctv/event_tamper.jpg` | `angle=180.0` | 124.6 | [362, 640, 3] uint8 mean 156.49 | ok |
| `cctv/event_tamper.jpg` | `noise_power=0.0001` | 127.3 | [362, 640, 3] uint8 mean 144.0 | ok |
| `cctv/event_tamper.jpg` | `noise_power=0.5` | 118.5 | [362, 640, 3] uint8 mean 106.67 | ok |
| `cctv/flattest.jpg` | `defaults` | 125.2 | [362, 640, 3] uint8 mean 119.73 | ok |
| `cctv/flattest.jpg` | `length=1.0` | 132.0 | [362, 640, 3] uint8 mean 119.76 | ok |
| `cctv/flattest.jpg` | `length=64.0` | 151.4 | [362, 640, 3] uint8 mean 120.81 | ok |
| `cctv/flattest.jpg` | `angle=-180.0` | 125.6 | [362, 640, 3] uint8 mean 119.73 | ok |
| `cctv/flattest.jpg` | `angle=180.0` | 130.6 | [362, 640, 3] uint8 mean 119.73 | ok |
| `cctv/flattest.jpg` | `noise_power=0.0001` | 120.1 | [362, 640, 3] uint8 mean 123.54 | ok |
| `cctv/flattest.jpg` | `noise_power=0.5` | 124.5 | [362, 640, 3] uint8 mean 80.55 | ok |
| `cctv/most_blown.jpg` | `defaults` | 135.9 | [362, 640, 3] uint8 mean 134.79 | ok |
| `cctv/most_blown.jpg` | `length=1.0` | 179.2 | [362, 640, 3] uint8 mean 136.18 | ok |
| `cctv/most_blown.jpg` | `length=64.0` | 152.0 | [362, 640, 3] uint8 mean 131.35 | ok |
| `cctv/most_blown.jpg` | `angle=-180.0` | 123.6 | [362, 640, 3] uint8 mean 134.79 | ok |
| `cctv/most_blown.jpg` | `angle=180.0` | 116.0 | [362, 640, 3] uint8 mean 134.79 | ok |
| `cctv/most_blown.jpg` | `noise_power=0.0001` | 116.1 | [362, 640, 3] uint8 mean 132.71 | ok |
| `cctv/most_blown.jpg` | `noise_power=0.5` | 115.4 | [362, 640, 3] uint8 mean 91.63 | ok |
| `cctv/sharpest.jpg` | `defaults` | 115.8 | [362, 640, 3] uint8 mean 129.86 | ok |
| `cctv/sharpest.jpg` | `length=1.0` | 130.5 | [362, 640, 3] uint8 mean 129.89 | ok |
| `cctv/sharpest.jpg` | `length=64.0` | 143.0 | [362, 640, 3] uint8 mean 125.36 | ok |
| `cctv/sharpest.jpg` | `angle=-180.0` | 120.7 | [362, 640, 3] uint8 mean 129.86 | ok |
| `cctv/sharpest.jpg` | `angle=180.0` | 124.2 | [362, 640, 3] uint8 mean 129.86 | ok |
| `cctv/sharpest.jpg` | `noise_power=0.0001` | 121.0 | [362, 640, 3] uint8 mean 128.19 | ok |
| `cctv/sharpest.jpg` | `noise_power=0.5` | 114.9 | [362, 640, 3] uint8 mean 87.41 | ok |
| `cctv/softest.jpg` | `defaults` | 115.3 | [362, 640, 3] uint8 mean 123.52 | ok |
| `cctv/softest.jpg` | `length=1.0` | 137.4 | [362, 640, 3] uint8 mean 123.72 | ok |
| `cctv/softest.jpg` | `length=64.0` | 144.3 | [362, 640, 3] uint8 mean 124.4 | ok |
| `cctv/softest.jpg` | `angle=-180.0` | 116.9 | [362, 640, 3] uint8 mean 123.52 | ok |
| `cctv/softest.jpg` | `angle=180.0` | 113.6 | [362, 640, 3] uint8 mean 123.52 | ok |
| `cctv/softest.jpg` | `noise_power=0.0001` | 118.8 | [362, 640, 3] uint8 mean 125.52 | ok |
| `cctv/softest.jpg` | `noise_power=0.5` | 115.9 | [362, 640, 3] uint8 mean 83.16 | ok |
| `reference/motion_blur_plate.jpg` | `defaults` | 93.5 | [482, 600, 3] uint8 mean 123.11 | ok |
| `reference/motion_blur_plate.jpg` | `length=1.0` | 121.3 | [482, 600, 3] uint8 mean 123.05 | ok |
| `reference/motion_blur_plate.jpg` | `length=64.0` | 225.2 | [482, 600, 3] uint8 mean 123.71 | ok |
| `reference/motion_blur_plate.jpg` | `angle=-180.0` | 86.9 | [482, 600, 3] uint8 mean 123.11 | ok |
| `reference/motion_blur_plate.jpg` | `angle=180.0` | 86.4 | [482, 600, 3] uint8 mean 123.11 | ok |
| `reference/motion_blur_plate.jpg` | `noise_power=0.0001` | 90.4 | [482, 600, 3] uint8 mean 123.49 | ok |
| `reference/motion_blur_plate.jpg` | `noise_power=0.5` | 86.3 | [482, 600, 3] uint8 mean 82.73 | ok |

## Artifacts

Outputs written to `validation/artifacts/deblur_motion/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
- `reference_motion_blur_plate.png`
