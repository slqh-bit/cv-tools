# nl_means_auto - validation result

**Non-local means with strength from measured noise**  
`cv_tools.filters.nl_means_denoise` | family: Enhance | 2026-10-12T19:03:32

## Verdict

**PASS** - 27 runs, no invariant broken.

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 398.5 | [362, 640, 3] uint8 mean 163.33 | ok |
| `cctv/brightest.jpg` | `aggressiveness=0.1` | 407.6 | [362, 640, 3] uint8 mean 163.33 | ok |
| `cctv/brightest.jpg` | `aggressiveness=3.0` | 400.2 | [362, 640, 3] uint8 mean 163.44 | ok |
| `cctv/darkest.jpg` | `defaults` | 396.5 | [362, 640, 3] uint8 mean 110.62 | ok |
| `cctv/darkest.jpg` | `aggressiveness=0.1` | 408.6 | [362, 640, 3] uint8 mean 110.62 | ok |
| `cctv/darkest.jpg` | `aggressiveness=3.0` | 401.3 | [362, 640, 3] uint8 mean 110.63 | ok |
| `cctv/event_fall.jpg` | `defaults` | 439.7 | [362, 640, 3] uint8 mean 125.14 | ok |
| `cctv/event_fall.jpg` | `aggressiveness=0.1` | 396.6 | [362, 640, 3] uint8 mean 125.19 | ok |
| `cctv/event_fall.jpg` | `aggressiveness=3.0` | 402.4 | [362, 640, 3] uint8 mean 125.04 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 401.1 | [362, 640, 3] uint8 mean 125.12 | ok |
| `cctv/event_optflow.jpg` | `aggressiveness=0.1` | 388.2 | [362, 640, 3] uint8 mean 125.12 | ok |
| `cctv/event_optflow.jpg` | `aggressiveness=3.0` | 394.7 | [362, 640, 3] uint8 mean 125.08 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 425.5 | [362, 640, 3] uint8 mean 160.46 | ok |
| `cctv/event_tamper.jpg` | `aggressiveness=0.1` | 391.8 | [362, 640, 3] uint8 mean 160.46 | ok |
| `cctv/event_tamper.jpg` | `aggressiveness=3.0` | 384.7 | [362, 640, 3] uint8 mean 160.56 | ok |
| `cctv/flattest.jpg` | `defaults` | 400.4 | [362, 640, 3] uint8 mean 121.2 | ok |
| `cctv/flattest.jpg` | `aggressiveness=0.1` | 421.6 | [362, 640, 3] uint8 mean 121.2 | ok |
| `cctv/flattest.jpg` | `aggressiveness=3.0` | 394.6 | [362, 640, 3] uint8 mean 121.17 | ok |
| `cctv/most_blown.jpg` | `defaults` | 411.9 | [362, 640, 3] uint8 mean 137.83 | ok |
| `cctv/most_blown.jpg` | `aggressiveness=0.1` | 407.5 | [362, 640, 3] uint8 mean 137.83 | ok |
| `cctv/most_blown.jpg` | `aggressiveness=3.0` | 383.1 | [362, 640, 3] uint8 mean 137.88 | ok |
| `cctv/sharpest.jpg` | `defaults` | 465.6 | [362, 640, 3] uint8 mean 131.5 | ok |
| `cctv/sharpest.jpg` | `aggressiveness=0.1` | 402.6 | [362, 640, 3] uint8 mean 131.5 | ok |
| `cctv/sharpest.jpg` | `aggressiveness=3.0` | 404.7 | [362, 640, 3] uint8 mean 131.53 | ok |
| `cctv/softest.jpg` | `defaults` | 398.6 | [362, 640, 3] uint8 mean 125.12 | ok |
| `cctv/softest.jpg` | `aggressiveness=0.1` | 384.2 | [362, 640, 3] uint8 mean 125.12 | ok |
| `cctv/softest.jpg` | `aggressiveness=3.0` | 378.6 | [362, 640, 3] uint8 mean 125.15 | ok |

## Artifacts

Outputs written to `validation/artifacts/nl_means_auto/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
