# laplacian - validation result

**Laplacian edge map**  
`src.filters.edge_detection` | family: Analyze | 2026-08-21T12:45:42

## Verdict

**PASS** - 36 runs, no invariant broken.

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 0.8 | [362, 640] uint8 mean 5.15 | ok |
| `cctv/brightest.jpg` | `normalize=False` | 0.5 | [362, 640] uint8 mean 33.44 | ok |
| `cctv/brightest.jpg` | `blur_sigma=0.0` | 0.6 | [362, 640] uint8 mean 5.15 | ok |
| `cctv/brightest.jpg` | `blur_sigma=10.0` | 3.3 | [362, 640] uint8 mean 33.41 | ok |
| `cctv/darkest.jpg` | `defaults` | 0.7 | [362, 640] uint8 mean 5.71 | ok |
| `cctv/darkest.jpg` | `normalize=False` | 0.5 | [362, 640] uint8 mean 33.81 | ok |
| `cctv/darkest.jpg` | `blur_sigma=0.0` | 0.5 | [362, 640] uint8 mean 5.71 | ok |
| `cctv/darkest.jpg` | `blur_sigma=10.0` | 3.4 | [362, 640] uint8 mean 36.56 | ok |
| `cctv/event_fall.jpg` | `defaults` | 0.6 | [362, 640] uint8 mean 10.36 | ok |
| `cctv/event_fall.jpg` | `normalize=False` | 0.5 | [362, 640] uint8 mean 64.22 | ok |
| `cctv/event_fall.jpg` | `blur_sigma=0.0` | 0.5 | [362, 640] uint8 mean 10.36 | ok |
| `cctv/event_fall.jpg` | `blur_sigma=10.0` | 3.3 | [362, 640] uint8 mean 32.8 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 0.6 | [362, 640] uint8 mean 6.9 | ok |
| `cctv/event_optflow.jpg` | `normalize=False` | 0.5 | [362, 640] uint8 mean 32.25 | ok |
| `cctv/event_optflow.jpg` | `blur_sigma=0.0` | 0.6 | [362, 640] uint8 mean 6.9 | ok |
| `cctv/event_optflow.jpg` | `blur_sigma=10.0` | 2.7 | [362, 640] uint8 mean 44.08 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 0.7 | [362, 640] uint8 mean 5.34 | ok |
| `cctv/event_tamper.jpg` | `normalize=False` | 0.6 | [362, 640] uint8 mean 33.39 | ok |
| `cctv/event_tamper.jpg` | `blur_sigma=0.0` | 0.5 | [362, 640] uint8 mean 5.34 | ok |
| `cctv/event_tamper.jpg` | `blur_sigma=10.0` | 2.9 | [362, 640] uint8 mean 33.57 | ok |
| `cctv/flattest.jpg` | `defaults` | 0.6 | [362, 640] uint8 mean 6.34 | ok |
| `cctv/flattest.jpg` | `normalize=False` | 0.6 | [362, 640] uint8 mean 30.39 | ok |
| `cctv/flattest.jpg` | `blur_sigma=0.0` | 0.8 | [362, 640] uint8 mean 6.34 | ok |
| `cctv/flattest.jpg` | `blur_sigma=10.0` | 2.7 | [362, 640] uint8 mean 43.92 | ok |
| `cctv/most_blown.jpg` | `defaults` | 0.5 | [362, 640] uint8 mean 5.99 | ok |
| `cctv/most_blown.jpg` | `normalize=False` | 0.5 | [362, 640] uint8 mean 34.46 | ok |
| `cctv/most_blown.jpg` | `blur_sigma=0.0` | 0.7 | [362, 640] uint8 mean 5.99 | ok |
| `cctv/most_blown.jpg` | `blur_sigma=10.0` | 2.8 | [362, 640] uint8 mean 32.99 | ok |
| `cctv/sharpest.jpg` | `defaults` | 0.6 | [362, 640] uint8 mean 11.74 | ok |
| `cctv/sharpest.jpg` | `normalize=False` | 0.5 | [362, 640] uint8 mean 68.21 | ok |
| `cctv/sharpest.jpg` | `blur_sigma=0.0` | 0.7 | [362, 640] uint8 mean 11.74 | ok |
| `cctv/sharpest.jpg` | `blur_sigma=10.0` | 2.9 | [362, 640] uint8 mean 30.19 | ok |
| `cctv/softest.jpg` | `defaults` | 0.6 | [362, 640] uint8 mean 5.02 | ok |
| `cctv/softest.jpg` | `normalize=False` | 0.5 | [362, 640] uint8 mean 28.75 | ok |
| `cctv/softest.jpg` | `blur_sigma=0.0` | 0.8 | [362, 640] uint8 mean 5.02 | ok |
| `cctv/softest.jpg` | `blur_sigma=10.0` | 2.6 | [362, 640] uint8 mean 44.62 | ok |

## Artifacts

Outputs written to `validation/artifacts/laplacian/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
