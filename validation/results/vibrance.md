# vibrance - validation result

**Saturation weighted towards muted colours**  
`src.filters.saturation` | family: Adjust | 2026-08-21T12:44:40

## Verdict

**PASS** - 27 runs, no invariant broken.

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 3.4 | [362, 640, 3] uint8 mean 163.25 | ok |
| `cctv/brightest.jpg` | `factor=0.0` | 3.2 | [362, 640, 3] uint8 mean 168.74 | ok |
| `cctv/brightest.jpg` | `factor=3.0` | 3.4 | [362, 640, 3] uint8 mean 152.87 | ok |
| `cctv/darkest.jpg` | `defaults` | 4.2 | [362, 640, 3] uint8 mean 110.65 | ok |
| `cctv/darkest.jpg` | `factor=0.0` | 2.6 | [362, 640, 3] uint8 mean 114.54 | ok |
| `cctv/darkest.jpg` | `factor=3.0` | 2.7 | [362, 640, 3] uint8 mean 103.33 | ok |
| `cctv/event_fall.jpg` | `defaults` | 2.5 | [362, 640, 3] uint8 mean 125.22 | ok |
| `cctv/event_fall.jpg` | `factor=0.0` | 2.8 | [362, 640, 3] uint8 mean 133.21 | ok |
| `cctv/event_fall.jpg` | `factor=3.0` | 2.5 | [362, 640, 3] uint8 mean 109.83 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 2.9 | [362, 640, 3] uint8 mean 125.11 | ok |
| `cctv/event_optflow.jpg` | `factor=0.0` | 2.8 | [362, 640, 3] uint8 mean 134.01 | ok |
| `cctv/event_optflow.jpg` | `factor=3.0` | 3.3 | [362, 640, 3] uint8 mean 107.95 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 2.4 | [362, 640, 3] uint8 mean 160.33 | ok |
| `cctv/event_tamper.jpg` | `factor=0.0` | 2.8 | [362, 640, 3] uint8 mean 165.91 | ok |
| `cctv/event_tamper.jpg` | `factor=3.0` | 2.5 | [362, 640, 3] uint8 mean 149.78 | ok |
| `cctv/flattest.jpg` | `defaults` | 3.0 | [362, 640, 3] uint8 mean 121.2 | ok |
| `cctv/flattest.jpg` | `factor=0.0` | 2.7 | [362, 640, 3] uint8 mean 129.85 | ok |
| `cctv/flattest.jpg` | `factor=3.0` | 2.6 | [362, 640, 3] uint8 mean 104.43 | ok |
| `cctv/most_blown.jpg` | `defaults` | 2.4 | [362, 640, 3] uint8 mean 137.81 | ok |
| `cctv/most_blown.jpg` | `factor=0.0` | 2.6 | [362, 640, 3] uint8 mean 141.7 | ok |
| `cctv/most_blown.jpg` | `factor=3.0` | 3.0 | [362, 640, 3] uint8 mean 130.59 | ok |
| `cctv/sharpest.jpg` | `defaults` | 3.2 | [362, 640, 3] uint8 mean 131.48 | ok |
| `cctv/sharpest.jpg` | `factor=0.0` | 3.3 | [362, 640, 3] uint8 mean 135.25 | ok |
| `cctv/sharpest.jpg` | `factor=3.0` | 3.3 | [362, 640, 3] uint8 mean 124.5 | ok |
| `cctv/softest.jpg` | `defaults` | 3.1 | [362, 640, 3] uint8 mean 125.07 | ok |
| `cctv/softest.jpg` | `factor=0.0` | 2.9 | [362, 640, 3] uint8 mean 130.68 | ok |
| `cctv/softest.jpg` | `factor=3.0` | 2.6 | [362, 640, 3] uint8 mean 114.34 | ok |

## Artifacts

Outputs written to `validation/artifacts/vibrance/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
