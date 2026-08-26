# invert_luminance - validation result

**Invert brightness, keeping hue**  
`src.filters.invert` | family: Adjust | 2026-08-21T12:44:42

## Verdict

**PASS** - 9 runs, no invariant broken.

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 1.4 | [362, 640, 3] uint8 mean 79.82 | ok |
| `cctv/darkest.jpg` | `defaults` | 1.4 | [362, 640, 3] uint8 mean 129.06 | ok |
| `cctv/event_fall.jpg` | `defaults` | 1.3 | [362, 640, 3] uint8 mean 110.88 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 1.5 | [362, 640, 3] uint8 mean 108.62 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 1.1 | [362, 640, 3] uint8 mean 83.0 | ok |
| `cctv/flattest.jpg` | `defaults` | 1.3 | [362, 640, 3] uint8 mean 113.12 | ok |
| `cctv/most_blown.jpg` | `defaults` | 1.1 | [362, 640, 3] uint8 mean 103.48 | ok |
| `cctv/sharpest.jpg` | `defaults` | 1.1 | [362, 640, 3] uint8 mean 110.39 | ok |
| `cctv/softest.jpg` | `defaults` | 1.1 | [362, 640, 3] uint8 mean 113.94 | ok |

## Artifacts

Outputs written to `validation/artifacts/invert_luminance/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
