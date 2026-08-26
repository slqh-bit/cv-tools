# sobel - validation result

**Sobel gradient magnitude**  
`src.filters.edge_detection` | family: Analyze | 2026-08-21T12:45:41

## Verdict

**PASS** - 18 runs, no invariant broken.

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 4.4 | [362, 640] uint8 mean 9.36 | ok |
| `cctv/brightest.jpg` | `normalize=False` | 3.5 | [362, 640] uint8 mean 34.49 | ok |
| `cctv/darkest.jpg` | `defaults` | 4.1 | [362, 640] uint8 mean 9.79 | ok |
| `cctv/darkest.jpg` | `normalize=False` | 3.5 | [362, 640] uint8 mean 35.8 | ok |
| `cctv/event_fall.jpg` | `defaults` | 4.1 | [362, 640] uint8 mean 20.02 | ok |
| `cctv/event_fall.jpg` | `normalize=False` | 3.5 | [362, 640] uint8 mean 71.13 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 4.4 | [362, 640] uint8 mean 10.13 | ok |
| `cctv/event_optflow.jpg` | `normalize=False` | 3.7 | [362, 640] uint8 mean 36.77 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 4.0 | [362, 640] uint8 mean 9.64 | ok |
| `cctv/event_tamper.jpg` | `normalize=False` | 3.8 | [362, 640] uint8 mean 34.31 | ok |
| `cctv/flattest.jpg` | `defaults` | 4.1 | [362, 640] uint8 mean 9.55 | ok |
| `cctv/flattest.jpg` | `normalize=False` | 3.5 | [362, 640] uint8 mean 34.86 | ok |
| `cctv/most_blown.jpg` | `defaults` | 4.0 | [362, 640] uint8 mean 10.3 | ok |
| `cctv/most_blown.jpg` | `normalize=False` | 3.6 | [362, 640] uint8 mean 37.26 | ok |
| `cctv/sharpest.jpg` | `defaults` | 4.3 | [362, 640] uint8 mean 20.57 | ok |
| `cctv/sharpest.jpg` | `normalize=False` | 3.5 | [362, 640] uint8 mean 71.71 | ok |
| `cctv/softest.jpg` | `defaults` | 4.3 | [362, 640] uint8 mean 9.77 | ok |
| `cctv/softest.jpg` | `normalize=False` | 3.7 | [362, 640] uint8 mean 29.66 | ok |

## Artifacts

Outputs written to `validation/artifacts/sobel/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
