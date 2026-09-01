# noise_map - validation result

**Per-block noise level map**  
`src.filters.noise_analysis` | family: Forensic | 2026-09-01T16:36:19

## Verdict

**PASS** - 27 runs, no invariant broken, 2 specific checks passed.

## What this filter specifically promises

- PASS - the map is brighter where the noise was planted: mean 219.0 inside the noisy patch against 17.1 outside
- PASS - and it covers the frame: 384x256 for a 384x256 frame

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 1.2 | [362, 640] uint8 mean 49.17 | ok |
| `cctv/brightest.jpg` | `normalize=False` | 0.8 | [362, 640] uint8 mean 0.97 | ok |
| `cctv/brightest.jpg` | `upscale=False` | 0.7 | [11, 20] uint8 mean 49.2 | ok |
| `cctv/darkest.jpg` | `defaults` | 0.7 | [362, 640] uint8 mean 47.74 | ok |
| `cctv/darkest.jpg` | `normalize=False` | 0.9 | [362, 640] uint8 mean 1.24 | ok |
| `cctv/darkest.jpg` | `upscale=False` | 0.9 | [11, 20] uint8 mean 47.7 | ok |
| `cctv/event_fall.jpg` | `defaults` | 0.7 | [362, 640] uint8 mean 43.67 | ok |
| `cctv/event_fall.jpg` | `normalize=False` | 0.9 | [362, 640] uint8 mean 3.65 | ok |
| `cctv/event_fall.jpg` | `upscale=False` | 1.1 | [11, 20] uint8 mean 43.69 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 0.7 | [362, 640] uint8 mean 35.89 | ok |
| `cctv/event_optflow.jpg` | `normalize=False` | 0.9 | [362, 640] uint8 mean 1.29 | ok |
| `cctv/event_optflow.jpg` | `upscale=False` | 0.7 | [11, 20] uint8 mean 35.9 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 1.4 | [362, 640] uint8 mean 49.28 | ok |
| `cctv/event_tamper.jpg` | `normalize=False` | 1.0 | [362, 640] uint8 mean 0.96 | ok |
| `cctv/event_tamper.jpg` | `upscale=False` | 0.7 | [11, 20] uint8 mean 49.31 | ok |
| `cctv/flattest.jpg` | `defaults` | 0.7 | [362, 640] uint8 mean 35.8 | ok |
| `cctv/flattest.jpg` | `normalize=False` | 1.0 | [362, 640] uint8 mean 1.17 | ok |
| `cctv/flattest.jpg` | `upscale=False` | 0.8 | [11, 20] uint8 mean 35.81 | ok |
| `cctv/most_blown.jpg` | `defaults` | 0.7 | [362, 640] uint8 mean 47.53 | ok |
| `cctv/most_blown.jpg` | `normalize=False` | 0.9 | [362, 640] uint8 mean 1.4 | ok |
| `cctv/most_blown.jpg` | `upscale=False` | 0.8 | [11, 20] uint8 mean 47.49 | ok |
| `cctv/sharpest.jpg` | `defaults` | 0.7 | [362, 640] uint8 mean 56.38 | ok |
| `cctv/sharpest.jpg` | `normalize=False` | 1.1 | [362, 640] uint8 mean 4.18 | ok |
| `cctv/sharpest.jpg` | `upscale=False` | 0.8 | [11, 20] uint8 mean 56.33 | ok |
| `cctv/softest.jpg` | `defaults` | 0.7 | [362, 640] uint8 mean 44.56 | ok |
| `cctv/softest.jpg` | `normalize=False` | 1.0 | [362, 640] uint8 mean 0.7 | ok |
| `cctv/softest.jpg` | `upscale=False` | 0.6 | [11, 20] uint8 mean 44.59 | ok |

## Artifacts

Outputs written to `validation/artifacts/noise_map/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
