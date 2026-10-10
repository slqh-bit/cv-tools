# multiscale_detail - validation result

**Per-frequency-band detail boost**  
`cv_tools.filters.detail_enhancement` | family: Enhance | 2026-10-10T14:12:51

## Verdict

**PASS** - 9 runs, no invariant broken.

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 53.1 | [362, 640, 3] uint8 mean 162.6 | ok |
| `cctv/darkest.jpg` | `defaults` | 56.7 | [362, 640, 3] uint8 mean 109.5 | ok |
| `cctv/event_fall.jpg` | `defaults` | 58.4 | [362, 640, 3] uint8 mean 124.68 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 59.7 | [362, 640, 3] uint8 mean 124.29 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 53.6 | [362, 640, 3] uint8 mean 159.72 | ok |
| `cctv/flattest.jpg` | `defaults` | 55.0 | [362, 640, 3] uint8 mean 120.38 | ok |
| `cctv/most_blown.jpg` | `defaults` | 53.0 | [362, 640, 3] uint8 mean 136.8 | ok |
| `cctv/sharpest.jpg` | `defaults` | 52.7 | [362, 640, 3] uint8 mean 131.17 | ok |
| `cctv/softest.jpg` | `defaults` | 61.0 | [362, 640, 3] uint8 mean 124.9 | ok |

## Artifacts

Outputs written to `validation/artifacts/multiscale_detail/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
