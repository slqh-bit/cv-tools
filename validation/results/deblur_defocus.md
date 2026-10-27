# deblur_defocus - validation result

**Deconvolution of defocus blur: Wiener, or Richardson-Lucy for noisy, compressed footage**  
`cv_tools.filters.motion_deblur` | family: Forensic | 2026-10-12T19:10:30

## Verdict

**PASS** - 80 runs, no invariant broken, 5 specific checks passed.

10 run(s) refused bad parameters with a clear message, which is the wanted behaviour.

## What this filter specifically promises

- PASS - wiener: the true PSF moves every blurred frame towards the original: radius 4 px, blurred in linear light by a disc drawn in validation.checks; PSNR gain +1.19 dB at worst (cctv/sharpest.jpg JPEG 60), +1.54 dB on average over 4 frames
- PASS - richardson_lucy: the true PSF moves every blurred frame towards the original: radius 4 px, blurred in linear light by a disc drawn in validation.checks; PSNR gain +1.83 dB at worst (cctv/sharpest.jpg JPEG 60), +2.13 dB on average over 4 frames
- PASS - the true PSF restores better than every wrong one tried: closest wrong PSF, radius 2.5 on cctv/sharpest.jpg JPEG 60, was 1.68 dB behind; 12 comparisons
- PASS - richardson_lucy earns its cost on compressed frames: +0.76 dB over wiener on average, both at default settings
- PASS - really defocused text is changed, not passed through: no ground truth exists for this image; fidelity is judged on the frames above

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `radius=0.1` on `cctv/brightest.jpg`: refused: radius must be at least 0.5, got 0.1
- `radius=0.1` on `cctv/darkest.jpg`: refused: radius must be at least 0.5, got 0.1
- `radius=0.1` on `cctv/event_fall.jpg`: refused: radius must be at least 0.5, got 0.1
- `radius=0.1` on `cctv/event_optflow.jpg`: refused: radius must be at least 0.5, got 0.1
- `radius=0.1` on `cctv/event_tamper.jpg`: refused: radius must be at least 0.5, got 0.1
- `radius=0.1` on `cctv/flattest.jpg`: refused: radius must be at least 0.5, got 0.1
- `radius=0.1` on `cctv/most_blown.jpg`: refused: radius must be at least 0.5, got 0.1
- `radius=0.1` on `cctv/sharpest.jpg`: refused: radius must be at least 0.5, got 0.1
- `radius=0.1` on `cctv/softest.jpg`: refused: radius must be at least 0.5, got 0.1
- `radius=0.1` on `reference/defocus_text.jpg`: refused: radius must be at least 0.5, got 0.1

## Refused parameters

Rejected on purpose, with the message the user would see.

- `radius=0.1` -> ValueError: radius must be at least 0.5, got 0.1

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 28.4 | [362, 640, 3] uint8 mean 161.7 | ok |
| `cctv/brightest.jpg` | `radius=0.1` | 0.0 | - | refused: ValueError: radius must be at least 0.5, got 0.1 |
| `cctv/brightest.jpg` | `radius=50.0` | 62.1 | [362, 640, 3] uint8 mean 156.92 | ok |
| `cctv/brightest.jpg` | `noise_power=0.0001` | 27.7 | [362, 640, 3] uint8 mean 142.76 | ok |
| `cctv/brightest.jpg` | `noise_power=0.5` | 28.3 | [362, 640, 3] uint8 mean 163.52 | ok |
| `cctv/brightest.jpg` | `solver=richardson_lucy` | 863.9 | [362, 640, 3] uint8 mean 160.97 | ok |
| `cctv/brightest.jpg` | `iterations=5` | 28.7 | [362, 640, 3] uint8 mean 161.7 | ok |
| `cctv/brightest.jpg` | `iterations=100` | 30.6 | [362, 640, 3] uint8 mean 161.7 | ok |
| `cctv/darkest.jpg` | `defaults` | 28.1 | [362, 640, 3] uint8 mean 110.27 | ok |
| `cctv/darkest.jpg` | `radius=0.1` | 0.0 | - | refused: ValueError: radius must be at least 0.5, got 0.1 |
| `cctv/darkest.jpg` | `radius=50.0` | 61.6 | [362, 640, 3] uint8 mean 109.72 | ok |
| `cctv/darkest.jpg` | `noise_power=0.0001` | 27.5 | [362, 640, 3] uint8 mean 117.44 | ok |
| `cctv/darkest.jpg` | `noise_power=0.5` | 28.0 | [362, 640, 3] uint8 mean 110.92 | ok |
| `cctv/darkest.jpg` | `solver=richardson_lucy` | 829.9 | [362, 640, 3] uint8 mean 107.2 | ok |
| `cctv/darkest.jpg` | `iterations=5` | 28.3 | [362, 640, 3] uint8 mean 110.27 | ok |
| `cctv/darkest.jpg` | `iterations=100` | 28.0 | [362, 640, 3] uint8 mean 110.27 | ok |
| `cctv/event_fall.jpg` | `defaults` | 28.3 | [362, 640, 3] uint8 mean 125.05 | ok |
| `cctv/event_fall.jpg` | `radius=0.1` | 0.0 | - | refused: ValueError: radius must be at least 0.5, got 0.1 |
| `cctv/event_fall.jpg` | `radius=50.0` | 61.8 | [362, 640, 3] uint8 mean 124.68 | ok |
| `cctv/event_fall.jpg` | `noise_power=0.0001` | 29.5 | [362, 640, 3] uint8 mean 125.95 | ok |
| `cctv/event_fall.jpg` | `noise_power=0.5` | 29.1 | [362, 640, 3] uint8 mean 125.49 | ok |
| `cctv/event_fall.jpg` | `solver=richardson_lucy` | 863.7 | [362, 640, 3] uint8 mean 114.93 | ok |
| `cctv/event_fall.jpg` | `iterations=5` | 29.1 | [362, 640, 3] uint8 mean 125.05 | ok |
| `cctv/event_fall.jpg` | `iterations=100` | 27.8 | [362, 640, 3] uint8 mean 125.05 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 28.7 | [362, 640, 3] uint8 mean 125.05 | ok |
| `cctv/event_optflow.jpg` | `radius=0.1` | 0.0 | - | refused: ValueError: radius must be at least 0.5, got 0.1 |
| `cctv/event_optflow.jpg` | `radius=50.0` | 63.1 | [362, 640, 3] uint8 mean 125.15 | ok |
| `cctv/event_optflow.jpg` | `noise_power=0.0001` | 28.2 | [362, 640, 3] uint8 mean 124.86 | ok |
| `cctv/event_optflow.jpg` | `noise_power=0.5` | 28.6 | [362, 640, 3] uint8 mean 125.41 | ok |
| `cctv/event_optflow.jpg` | `solver=richardson_lucy` | 850.9 | [362, 640, 3] uint8 mean 121.69 | ok |
| `cctv/event_optflow.jpg` | `iterations=5` | 28.1 | [362, 640, 3] uint8 mean 125.05 | ok |
| `cctv/event_optflow.jpg` | `iterations=100` | 27.3 | [362, 640, 3] uint8 mean 125.05 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 27.7 | [362, 640, 3] uint8 mean 158.95 | ok |
| `cctv/event_tamper.jpg` | `radius=0.1` | 0.0 | - | refused: ValueError: radius must be at least 0.5, got 0.1 |
| `cctv/event_tamper.jpg` | `radius=50.0` | 61.1 | [362, 640, 3] uint8 mean 154.77 | ok |
| `cctv/event_tamper.jpg` | `noise_power=0.0001` | 27.3 | [362, 640, 3] uint8 mean 141.47 | ok |
| `cctv/event_tamper.jpg` | `noise_power=0.5` | 27.3 | [362, 640, 3] uint8 mean 160.62 | ok |
| `cctv/event_tamper.jpg` | `solver=richardson_lucy` | 836.1 | [362, 640, 3] uint8 mean 158.14 | ok |
| `cctv/event_tamper.jpg` | `iterations=5` | 29.2 | [362, 640, 3] uint8 mean 158.95 | ok |
| `cctv/event_tamper.jpg` | `iterations=100` | 27.8 | [362, 640, 3] uint8 mean 158.95 | ok |
| `cctv/flattest.jpg` | `defaults` | 30.3 | [362, 640, 3] uint8 mean 121.24 | ok |
| `cctv/flattest.jpg` | `radius=0.1` | 0.0 | - | refused: ValueError: radius must be at least 0.5, got 0.1 |
| `cctv/flattest.jpg` | `radius=50.0` | 63.7 | [362, 640, 3] uint8 mean 122.04 | ok |
| `cctv/flattest.jpg` | `noise_power=0.0001` | 28.1 | [362, 640, 3] uint8 mean 122.93 | ok |
| `cctv/flattest.jpg` | `noise_power=0.5` | 30.3 | [362, 640, 3] uint8 mean 121.49 | ok |
| `cctv/flattest.jpg` | `solver=richardson_lucy` | 844.6 | [362, 640, 3] uint8 mean 117.95 | ok |
| `cctv/flattest.jpg` | `iterations=5` | 29.0 | [362, 640, 3] uint8 mean 121.24 | ok |
| `cctv/flattest.jpg` | `iterations=100` | 27.5 | [362, 640, 3] uint8 mean 121.24 | ok |
| `cctv/most_blown.jpg` | `defaults` | 27.4 | [362, 640, 3] uint8 mean 136.78 | ok |
| `cctv/most_blown.jpg` | `radius=0.1` | 0.0 | - | refused: ValueError: radius must be at least 0.5, got 0.1 |
| `cctv/most_blown.jpg` | `radius=50.0` | 63.8 | [362, 640, 3] uint8 mean 133.11 | ok |
| `cctv/most_blown.jpg` | `noise_power=0.0001` | 28.3 | [362, 640, 3] uint8 mean 130.93 | ok |
| `cctv/most_blown.jpg` | `noise_power=0.5` | 27.9 | [362, 640, 3] uint8 mean 138.07 | ok |
| `cctv/most_blown.jpg` | `solver=richardson_lucy` | 860.3 | [362, 640, 3] uint8 mean 134.19 | ok |
| `cctv/most_blown.jpg` | `iterations=5` | 29.3 | [362, 640, 3] uint8 mean 136.78 | ok |
| `cctv/most_blown.jpg` | `iterations=100` | 27.8 | [362, 640, 3] uint8 mean 136.78 | ok |
| `cctv/sharpest.jpg` | `defaults` | 28.4 | [362, 640, 3] uint8 mean 131.42 | ok |
| `cctv/sharpest.jpg` | `radius=0.1` | 0.0 | - | refused: ValueError: radius must be at least 0.5, got 0.1 |
| `cctv/sharpest.jpg` | `radius=50.0` | 62.5 | [362, 640, 3] uint8 mean 127.51 | ok |
| `cctv/sharpest.jpg` | `noise_power=0.0001` | 27.1 | [362, 640, 3] uint8 mean 128.43 | ok |
| `cctv/sharpest.jpg` | `noise_power=0.5` | 27.3 | [362, 640, 3] uint8 mean 131.74 | ok |
| `cctv/sharpest.jpg` | `solver=richardson_lucy` | 833.7 | [362, 640, 3] uint8 mean 121.27 | ok |
| `cctv/sharpest.jpg` | `iterations=5` | 29.2 | [362, 640, 3] uint8 mean 131.42 | ok |
| `cctv/sharpest.jpg` | `iterations=100` | 27.9 | [362, 640, 3] uint8 mean 131.42 | ok |
| `cctv/softest.jpg` | `defaults` | 27.9 | [362, 640, 3] uint8 mean 125.46 | ok |
| `cctv/softest.jpg` | `radius=0.1` | 0.0 | - | refused: ValueError: radius must be at least 0.5, got 0.1 |
| `cctv/softest.jpg` | `radius=50.0` | 61.5 | [362, 640, 3] uint8 mean 126.14 | ok |
| `cctv/softest.jpg` | `noise_power=0.0001` | 28.0 | [362, 640, 3] uint8 mean 125.95 | ok |
| `cctv/softest.jpg` | `noise_power=0.5` | 28.0 | [362, 640, 3] uint8 mean 125.38 | ok |
| `cctv/softest.jpg` | `solver=richardson_lucy` | 839.6 | [362, 640, 3] uint8 mean 123.54 | ok |
| `cctv/softest.jpg` | `iterations=5` | 29.3 | [362, 640, 3] uint8 mean 125.46 | ok |
| `cctv/softest.jpg` | `iterations=100` | 27.3 | [362, 640, 3] uint8 mean 125.46 | ok |
| `reference/defocus_text.jpg` | `defaults` | 41.7 | [472, 697, 3] uint8 mean 179.34 | ok |
| `reference/defocus_text.jpg` | `radius=0.1` | 0.0 | - | refused: ValueError: radius must be at least 0.5, got 0.1 |
| `reference/defocus_text.jpg` | `radius=50.0` | 80.8 | [472, 697, 3] uint8 mean 179.23 | ok |
| `reference/defocus_text.jpg` | `noise_power=0.0001` | 41.2 | [472, 697, 3] uint8 mean 178.87 | ok |
| `reference/defocus_text.jpg` | `noise_power=0.5` | 42.3 | [472, 697, 3] uint8 mean 179.34 | ok |
| `reference/defocus_text.jpg` | `solver=richardson_lucy` | 2118.5 | [472, 697, 3] uint8 mean 179.25 | ok |
| `reference/defocus_text.jpg` | `iterations=5` | 41.5 | [472, 697, 3] uint8 mean 179.34 | ok |
| `reference/defocus_text.jpg` | `iterations=100` | 42.5 | [472, 697, 3] uint8 mean 179.34 | ok |

## Artifacts

Outputs written to `validation/artifacts/deblur_defocus/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
- `reference_defocus_text.png`
