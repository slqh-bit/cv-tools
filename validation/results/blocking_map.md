# blocking_map - validation result

**Per-region JPEG blocking map**  
`src.filters.compression_analysis` | family: Analyze | 2026-09-01T16:35:58

## Verdict

**PASS** - 27 runs, no invariant broken.

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 19.6 | [362, 640] uint8 mean 75.26 | ok |
| `cctv/brightest.jpg` | `normalize=False` | 16.9 | [362, 640] uint8 mean 131.57 | ok |
| `cctv/brightest.jpg` | `upscale=False` | 15.8 | [11, 20] uint8 mean 75.26 | ok |
| `cctv/darkest.jpg` | `defaults` | 21.0 | [362, 640] uint8 mean 11.93 | ok |
| `cctv/darkest.jpg` | `normalize=False` | 16.2 | [362, 640] uint8 mean 121.73 | ok |
| `cctv/darkest.jpg` | `upscale=False` | 20.3 | [11, 20] uint8 mean 11.99 | ok |
| `cctv/event_fall.jpg` | `defaults` | 16.2 | [362, 640] uint8 mean 47.3 | ok |
| `cctv/event_fall.jpg` | `normalize=False` | 15.5 | [362, 640] uint8 mean 148.91 | ok |
| `cctv/event_fall.jpg` | `upscale=False` | 15.1 | [11, 20] uint8 mean 47.3 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 15.1 | [362, 640] uint8 mean 33.42 | ok |
| `cctv/event_optflow.jpg` | `normalize=False` | 15.3 | [362, 640] uint8 mean 133.09 | ok |
| `cctv/event_optflow.jpg` | `upscale=False` | 14.9 | [11, 20] uint8 mean 33.43 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 15.6 | [362, 640] uint8 mean 60.24 | ok |
| `cctv/event_tamper.jpg` | `normalize=False` | 18.7 | [362, 640] uint8 mean 134.75 | ok |
| `cctv/event_tamper.jpg` | `upscale=False` | 15.3 | [11, 20] uint8 mean 60.24 | ok |
| `cctv/flattest.jpg` | `defaults` | 15.1 | [362, 640] uint8 mean 31.22 | ok |
| `cctv/flattest.jpg` | `normalize=False` | 15.2 | [362, 640] uint8 mean 134.13 | ok |
| `cctv/flattest.jpg` | `upscale=False` | 15.0 | [11, 20] uint8 mean 31.22 | ok |
| `cctv/most_blown.jpg` | `defaults` | 14.9 | [362, 640] uint8 mean 2.56 | ok |
| `cctv/most_blown.jpg` | `normalize=False` | 16.0 | [362, 640] uint8 mean 109.0 | ok |
| `cctv/most_blown.jpg` | `upscale=False` | 16.2 | [11, 20] uint8 mean 2.56 | ok |
| `cctv/sharpest.jpg` | `defaults` | 15.6 | [362, 640] uint8 mean 26.51 | ok |
| `cctv/sharpest.jpg` | `normalize=False` | 21.1 | [362, 640] uint8 mean 131.71 | ok |
| `cctv/sharpest.jpg` | `upscale=False` | 15.4 | [11, 20] uint8 mean 26.55 | ok |
| `cctv/softest.jpg` | `defaults` | 15.3 | [362, 640] uint8 mean 53.34 | ok |
| `cctv/softest.jpg` | `normalize=False` | 15.7 | [362, 640] uint8 mean 154.14 | ok |
| `cctv/softest.jpg` | `upscale=False` | 15.2 | [11, 20] uint8 mean 53.34 | ok |

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
