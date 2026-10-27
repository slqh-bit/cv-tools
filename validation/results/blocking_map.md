# blocking_map - validation result

**Per-region JPEG blocking map**  
`cv_tools.filters.compression_analysis` | family: Analyze | 2026-10-12T19:04:11

## Verdict

**PASS** - 27 runs, no invariant broken.

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 16.9 | [362, 640] uint8 mean 75.26 | ok |
| `cctv/brightest.jpg` | `normalize=False` | 17.7 | [362, 640] uint8 mean 131.57 | ok |
| `cctv/brightest.jpg` | `upscale=False` | 16.0 | [11, 20] uint8 mean 75.26 | ok |
| `cctv/darkest.jpg` | `defaults` | 15.9 | [362, 640] uint8 mean 11.93 | ok |
| `cctv/darkest.jpg` | `normalize=False` | 16.7 | [362, 640] uint8 mean 121.73 | ok |
| `cctv/darkest.jpg` | `upscale=False` | 15.7 | [11, 20] uint8 mean 11.99 | ok |
| `cctv/event_fall.jpg` | `defaults` | 15.9 | [362, 640] uint8 mean 47.3 | ok |
| `cctv/event_fall.jpg` | `normalize=False` | 15.7 | [362, 640] uint8 mean 148.91 | ok |
| `cctv/event_fall.jpg` | `upscale=False` | 15.8 | [11, 20] uint8 mean 47.3 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 16.1 | [362, 640] uint8 mean 33.42 | ok |
| `cctv/event_optflow.jpg` | `normalize=False` | 18.6 | [362, 640] uint8 mean 133.09 | ok |
| `cctv/event_optflow.jpg` | `upscale=False` | 15.2 | [11, 20] uint8 mean 33.43 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 16.0 | [362, 640] uint8 mean 60.24 | ok |
| `cctv/event_tamper.jpg` | `normalize=False` | 16.8 | [362, 640] uint8 mean 134.75 | ok |
| `cctv/event_tamper.jpg` | `upscale=False` | 25.6 | [11, 20] uint8 mean 60.24 | ok |
| `cctv/flattest.jpg` | `defaults` | 15.7 | [362, 640] uint8 mean 31.22 | ok |
| `cctv/flattest.jpg` | `normalize=False` | 22.5 | [362, 640] uint8 mean 134.13 | ok |
| `cctv/flattest.jpg` | `upscale=False` | 25.1 | [11, 20] uint8 mean 31.22 | ok |
| `cctv/most_blown.jpg` | `defaults` | 16.9 | [362, 640] uint8 mean 2.56 | ok |
| `cctv/most_blown.jpg` | `normalize=False` | 15.3 | [362, 640] uint8 mean 109.0 | ok |
| `cctv/most_blown.jpg` | `upscale=False` | 15.7 | [11, 20] uint8 mean 2.56 | ok |
| `cctv/sharpest.jpg` | `defaults` | 15.7 | [362, 640] uint8 mean 26.51 | ok |
| `cctv/sharpest.jpg` | `normalize=False` | 15.9 | [362, 640] uint8 mean 131.71 | ok |
| `cctv/sharpest.jpg` | `upscale=False` | 15.5 | [11, 20] uint8 mean 26.55 | ok |
| `cctv/softest.jpg` | `defaults` | 15.7 | [362, 640] uint8 mean 53.34 | ok |
| `cctv/softest.jpg` | `normalize=False` | 16.4 | [362, 640] uint8 mean 154.14 | ok |
| `cctv/softest.jpg` | `upscale=False` | 16.5 | [11, 20] uint8 mean 53.34 | ok |

## Artifacts

Outputs written to `validation/artifacts/blocking_map/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
