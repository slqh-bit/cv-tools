# deblur_motion - validation result

**Deconvolution of linear motion blur: Wiener, or Richardson-Lucy for noisy, compressed footage**  
`cv_tools.filters.motion_deblur` | family: Forensic | 2026-10-10T14:18:24

## Verdict

**PASS** - 100 runs, no invariant broken, 6 specific checks passed.

## What this filter specifically promises

- PASS - wiener: the true PSF moves every blurred frame towards the original: 15 px at 20 degrees, blurred in linear light by validation.degrade; PSNR gain +1.52 dB at worst (cctv/sharpest.jpg JPEG 60), +1.91 dB on average over 4 frames
- PASS - richardson_lucy: the true PSF moves every blurred frame towards the original: 15 px at 20 degrees, blurred in linear light by validation.degrade; PSNR gain +2.15 dB at worst (cctv/sharpest.jpg JPEG 60), +2.46 dB on average over 4 frames
- PASS - the true PSF restores better than every wrong one tried: closest wrong PSF, angle 35 on cctv/event_fall.jpg JPEG 60, was 1.75 dB behind; 20 comparisons
- PASS - richardson_lucy earns its cost on compressed frames: +0.76 dB over wiener on average, both at default settings
- PASS - a heavy noise term does not darken the frame: mean moved 0.04/255 at noise_power 0.5
- PASS - a really blurred plate is changed, not passed through: no ground truth exists for this image; fidelity is judged on the frames above

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 29.7 | [362, 640, 3] uint8 mean 160.71 | ok |
| `cctv/brightest.jpg` | `length=1.0` | 29.0 | [362, 640, 3] uint8 mean 163.47 | ok |
| `cctv/brightest.jpg` | `length=200.0` | 119.9 | [362, 640, 3] uint8 mean 138.39 | ok |
| `cctv/brightest.jpg` | `angle=-180.0` | 29.9 | [362, 640, 3] uint8 mean 160.71 | ok |
| `cctv/brightest.jpg` | `angle=180.0` | 29.3 | [362, 640, 3] uint8 mean 160.71 | ok |
| `cctv/brightest.jpg` | `noise_power=0.0001` | 28.6 | [362, 640, 3] uint8 mean 146.82 | ok |
| `cctv/brightest.jpg` | `noise_power=0.5` | 28.7 | [362, 640, 3] uint8 mean 163.46 | ok |
| `cctv/brightest.jpg` | `solver=richardson_lucy` | 1519.0 | [362, 640, 3] uint8 mean 158.58 | ok |
| `cctv/brightest.jpg` | `iterations=5` | 30.1 | [362, 640, 3] uint8 mean 160.71 | ok |
| `cctv/brightest.jpg` | `iterations=100` | 29.6 | [362, 640, 3] uint8 mean 160.71 | ok |
| `cctv/darkest.jpg` | `defaults` | 29.8 | [362, 640, 3] uint8 mean 109.74 | ok |
| `cctv/darkest.jpg` | `length=1.0` | 27.2 | [362, 640, 3] uint8 mean 110.95 | ok |
| `cctv/darkest.jpg` | `length=200.0` | 120.7 | [362, 640, 3] uint8 mean 107.4 | ok |
| `cctv/darkest.jpg` | `angle=-180.0` | 34.7 | [362, 640, 3] uint8 mean 109.74 | ok |
| `cctv/darkest.jpg` | `angle=180.0` | 39.3 | [362, 640, 3] uint8 mean 109.74 | ok |
| `cctv/darkest.jpg` | `noise_power=0.0001` | 42.1 | [362, 640, 3] uint8 mean 115.1 | ok |
| `cctv/darkest.jpg` | `noise_power=0.5` | 34.0 | [362, 640, 3] uint8 mean 110.88 | ok |
| `cctv/darkest.jpg` | `solver=richardson_lucy` | 1549.7 | [362, 640, 3] uint8 mean 105.62 | ok |
| `cctv/darkest.jpg` | `iterations=5` | 29.1 | [362, 640, 3] uint8 mean 109.74 | ok |
| `cctv/darkest.jpg` | `iterations=100` | 28.4 | [362, 640, 3] uint8 mean 109.74 | ok |
| `cctv/event_fall.jpg` | `defaults` | 29.9 | [362, 640, 3] uint8 mean 125.16 | ok |
| `cctv/event_fall.jpg` | `length=1.0` | 25.5 | [362, 640, 3] uint8 mean 125.53 | ok |
| `cctv/event_fall.jpg` | `length=200.0` | 120.7 | [362, 640, 3] uint8 mean 127.49 | ok |
| `cctv/event_fall.jpg` | `angle=-180.0` | 29.4 | [362, 640, 3] uint8 mean 125.16 | ok |
| `cctv/event_fall.jpg` | `angle=180.0` | 28.9 | [362, 640, 3] uint8 mean 125.16 | ok |
| `cctv/event_fall.jpg` | `noise_power=0.0001` | 28.9 | [362, 640, 3] uint8 mean 125.07 | ok |
| `cctv/event_fall.jpg` | `noise_power=0.5` | 30.8 | [362, 640, 3] uint8 mean 125.47 | ok |
| `cctv/event_fall.jpg` | `solver=richardson_lucy` | 1508.7 | [362, 640, 3] uint8 mean 110.18 | ok |
| `cctv/event_fall.jpg` | `iterations=5` | 28.6 | [362, 640, 3] uint8 mean 125.16 | ok |
| `cctv/event_fall.jpg` | `iterations=100` | 29.2 | [362, 640, 3] uint8 mean 125.16 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 29.1 | [362, 640, 3] uint8 mean 124.91 | ok |
| `cctv/event_optflow.jpg` | `length=1.0` | 25.6 | [362, 640, 3] uint8 mean 125.43 | ok |
| `cctv/event_optflow.jpg` | `length=200.0` | 121.5 | [362, 640, 3] uint8 mean 127.44 | ok |
| `cctv/event_optflow.jpg` | `angle=-180.0` | 29.7 | [362, 640, 3] uint8 mean 124.91 | ok |
| `cctv/event_optflow.jpg` | `angle=180.0` | 29.4 | [362, 640, 3] uint8 mean 124.91 | ok |
| `cctv/event_optflow.jpg` | `noise_power=0.0001` | 29.9 | [362, 640, 3] uint8 mean 124.11 | ok |
| `cctv/event_optflow.jpg` | `noise_power=0.5` | 30.0 | [362, 640, 3] uint8 mean 125.38 | ok |
| `cctv/event_optflow.jpg` | `solver=richardson_lucy` | 1517.8 | [362, 640, 3] uint8 mean 119.66 | ok |
| `cctv/event_optflow.jpg` | `iterations=5` | 28.8 | [362, 640, 3] uint8 mean 124.91 | ok |
| `cctv/event_optflow.jpg` | `iterations=100` | 29.1 | [362, 640, 3] uint8 mean 124.91 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 29.8 | [362, 640, 3] uint8 mean 158.05 | ok |
| `cctv/event_tamper.jpg` | `length=1.0` | 28.3 | [362, 640, 3] uint8 mean 160.57 | ok |
| `cctv/event_tamper.jpg` | `length=200.0` | 123.1 | [362, 640, 3] uint8 mean 136.83 | ok |
| `cctv/event_tamper.jpg` | `angle=-180.0` | 29.1 | [362, 640, 3] uint8 mean 158.05 | ok |
| `cctv/event_tamper.jpg` | `angle=180.0` | 33.7 | [362, 640, 3] uint8 mean 158.05 | ok |
| `cctv/event_tamper.jpg` | `noise_power=0.0001` | 30.5 | [362, 640, 3] uint8 mean 145.19 | ok |
| `cctv/event_tamper.jpg` | `noise_power=0.5` | 29.2 | [362, 640, 3] uint8 mean 160.55 | ok |
| `cctv/event_tamper.jpg` | `solver=richardson_lucy` | 1506.9 | [362, 640, 3] uint8 mean 155.82 | ok |
| `cctv/event_tamper.jpg` | `iterations=5` | 28.9 | [362, 640, 3] uint8 mean 158.05 | ok |
| `cctv/event_tamper.jpg` | `iterations=100` | 29.4 | [362, 640, 3] uint8 mean 158.05 | ok |
| `cctv/flattest.jpg` | `defaults` | 30.8 | [362, 640, 3] uint8 mean 121.11 | ok |
| `cctv/flattest.jpg` | `length=1.0` | 25.7 | [362, 640, 3] uint8 mean 121.51 | ok |
| `cctv/flattest.jpg` | `length=200.0` | 121.5 | [362, 640, 3] uint8 mean 124.78 | ok |
| `cctv/flattest.jpg` | `angle=-180.0` | 28.7 | [362, 640, 3] uint8 mean 121.11 | ok |
| `cctv/flattest.jpg` | `angle=180.0` | 28.8 | [362, 640, 3] uint8 mean 121.11 | ok |
| `cctv/flattest.jpg` | `noise_power=0.0001` | 30.0 | [362, 640, 3] uint8 mean 122.0 | ok |
| `cctv/flattest.jpg` | `noise_power=0.5` | 29.2 | [362, 640, 3] uint8 mean 121.46 | ok |
| `cctv/flattest.jpg` | `solver=richardson_lucy` | 1522.6 | [362, 640, 3] uint8 mean 116.06 | ok |
| `cctv/flattest.jpg` | `iterations=5` | 28.5 | [362, 640, 3] uint8 mean 121.11 | ok |
| `cctv/flattest.jpg` | `iterations=100` | 28.7 | [362, 640, 3] uint8 mean 121.11 | ok |
| `cctv/most_blown.jpg` | `defaults` | 29.7 | [362, 640, 3] uint8 mean 136.04 | ok |
| `cctv/most_blown.jpg` | `length=1.0` | 28.7 | [362, 640, 3] uint8 mean 138.08 | ok |
| `cctv/most_blown.jpg` | `length=200.0` | 122.4 | [362, 640, 3] uint8 mean 127.31 | ok |
| `cctv/most_blown.jpg` | `angle=-180.0` | 29.1 | [362, 640, 3] uint8 mean 136.04 | ok |
| `cctv/most_blown.jpg` | `angle=180.0` | 29.3 | [362, 640, 3] uint8 mean 136.04 | ok |
| `cctv/most_blown.jpg` | `noise_power=0.0001` | 35.6 | [362, 640, 3] uint8 mean 132.29 | ok |
| `cctv/most_blown.jpg` | `noise_power=0.5` | 38.4 | [362, 640, 3] uint8 mean 138.02 | ok |
| `cctv/most_blown.jpg` | `solver=richardson_lucy` | 1574.9 | [362, 640, 3] uint8 mean 132.41 | ok |
| `cctv/most_blown.jpg` | `iterations=5` | 28.7 | [362, 640, 3] uint8 mean 136.04 | ok |
| `cctv/most_blown.jpg` | `iterations=100` | 28.6 | [362, 640, 3] uint8 mean 136.04 | ok |
| `cctv/sharpest.jpg` | `defaults` | 28.9 | [362, 640, 3] uint8 mean 130.85 | ok |
| `cctv/sharpest.jpg` | `length=1.0` | 25.9 | [362, 640, 3] uint8 mean 131.77 | ok |
| `cctv/sharpest.jpg` | `length=200.0` | 119.2 | [362, 640, 3] uint8 mean 128.62 | ok |
| `cctv/sharpest.jpg` | `angle=-180.0` | 28.8 | [362, 640, 3] uint8 mean 130.85 | ok |
| `cctv/sharpest.jpg` | `angle=180.0` | 28.6 | [362, 640, 3] uint8 mean 130.85 | ok |
| `cctv/sharpest.jpg` | `noise_power=0.0001` | 28.9 | [362, 640, 3] uint8 mean 127.76 | ok |
| `cctv/sharpest.jpg` | `noise_power=0.5` | 28.8 | [362, 640, 3] uint8 mean 131.7 | ok |
| `cctv/sharpest.jpg` | `solver=richardson_lucy` | 1521.7 | [362, 640, 3] uint8 mean 117.04 | ok |
| `cctv/sharpest.jpg` | `iterations=5` | 28.5 | [362, 640, 3] uint8 mean 130.85 | ok |
| `cctv/sharpest.jpg` | `iterations=100` | 28.8 | [362, 640, 3] uint8 mean 130.85 | ok |
| `cctv/softest.jpg` | `defaults` | 29.6 | [362, 640, 3] uint8 mean 125.12 | ok |
| `cctv/softest.jpg` | `length=1.0` | 26.2 | [362, 640, 3] uint8 mean 125.43 | ok |
| `cctv/softest.jpg` | `length=200.0` | 120.1 | [362, 640, 3] uint8 mean 115.53 | ok |
| `cctv/softest.jpg` | `angle=-180.0` | 28.8 | [362, 640, 3] uint8 mean 125.12 | ok |
| `cctv/softest.jpg` | `angle=180.0` | 28.6 | [362, 640, 3] uint8 mean 125.12 | ok |
| `cctv/softest.jpg` | `noise_power=0.0001` | 28.9 | [362, 640, 3] uint8 mean 125.26 | ok |
| `cctv/softest.jpg` | `noise_power=0.5` | 28.6 | [362, 640, 3] uint8 mean 125.33 | ok |
| `cctv/softest.jpg` | `solver=richardson_lucy` | 1537.8 | [362, 640, 3] uint8 mean 121.76 | ok |
| `cctv/softest.jpg` | `iterations=5` | 28.9 | [362, 640, 3] uint8 mean 125.12 | ok |
| `cctv/softest.jpg` | `iterations=100` | 28.5 | [362, 640, 3] uint8 mean 125.12 | ok |
| `reference/motion_blur_plate.jpg` | `defaults` | 34.4 | [482, 600, 3] uint8 mean 124.79 | ok |
| `reference/motion_blur_plate.jpg` | `length=1.0` | 35.7 | [482, 600, 3] uint8 mean 124.85 | ok |
| `reference/motion_blur_plate.jpg` | `length=200.0` | 142.4 | [482, 600, 3] uint8 mean 124.31 | ok |
| `reference/motion_blur_plate.jpg` | `angle=-180.0` | 34.7 | [482, 600, 3] uint8 mean 124.79 | ok |
| `reference/motion_blur_plate.jpg` | `angle=180.0` | 34.6 | [482, 600, 3] uint8 mean 124.79 | ok |
| `reference/motion_blur_plate.jpg` | `noise_power=0.0001` | 34.8 | [482, 600, 3] uint8 mean 123.72 | ok |
| `reference/motion_blur_plate.jpg` | `noise_power=0.5` | 34.6 | [482, 600, 3] uint8 mean 124.84 | ok |
| `reference/motion_blur_plate.jpg` | `solver=richardson_lucy` | 1765.6 | [482, 600, 3] uint8 mean 123.38 | ok |
| `reference/motion_blur_plate.jpg` | `iterations=5` | 35.1 | [482, 600, 3] uint8 mean 124.79 | ok |
| `reference/motion_blur_plate.jpg` | `iterations=100` | 34.2 | [482, 600, 3] uint8 mean 124.79 | ok |

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
