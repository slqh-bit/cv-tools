# nl_means_auto - validation result

**Non-local means with strength from measured noise**  
`src.filters.nl_means_denoise` | family: Enhance | 2026-08-21T12:45:07

## Verdict

**PASS** - 27 runs, no invariant broken.

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 403.5 | [362, 640, 3] uint8 mean 163.33 | ok |
| `cctv/brightest.jpg` | `aggressiveness=0.1` | 369.5 | [362, 640, 3] uint8 mean 163.33 | ok |
| `cctv/brightest.jpg` | `aggressiveness=3.0` | 372.0 | [362, 640, 3] uint8 mean 163.44 | ok |
| `cctv/darkest.jpg` | `defaults` | 377.0 | [362, 640, 3] uint8 mean 110.62 | ok |
| `cctv/darkest.jpg` | `aggressiveness=0.1` | 391.5 | [362, 640, 3] uint8 mean 110.62 | ok |
| `cctv/darkest.jpg` | `aggressiveness=3.0` | 381.7 | [362, 640, 3] uint8 mean 110.63 | ok |
| `cctv/event_fall.jpg` | `defaults` | 371.1 | [362, 640, 3] uint8 mean 125.14 | ok |
| `cctv/event_fall.jpg` | `aggressiveness=0.1` | 375.9 | [362, 640, 3] uint8 mean 125.19 | ok |
| `cctv/event_fall.jpg` | `aggressiveness=3.0` | 370.8 | [362, 640, 3] uint8 mean 125.04 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 372.5 | [362, 640, 3] uint8 mean 125.12 | ok |
| `cctv/event_optflow.jpg` | `aggressiveness=0.1` | 376.3 | [362, 640, 3] uint8 mean 125.12 | ok |
| `cctv/event_optflow.jpg` | `aggressiveness=3.0` | 384.7 | [362, 640, 3] uint8 mean 125.08 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 365.7 | [362, 640, 3] uint8 mean 160.46 | ok |
| `cctv/event_tamper.jpg` | `aggressiveness=0.1` | 376.8 | [362, 640, 3] uint8 mean 160.46 | ok |
| `cctv/event_tamper.jpg` | `aggressiveness=3.0` | 381.7 | [362, 640, 3] uint8 mean 160.56 | ok |
| `cctv/flattest.jpg` | `defaults` | 397.0 | [362, 640, 3] uint8 mean 121.2 | ok |
| `cctv/flattest.jpg` | `aggressiveness=0.1` | 382.6 | [362, 640, 3] uint8 mean 121.2 | ok |
| `cctv/flattest.jpg` | `aggressiveness=3.0` | 371.3 | [362, 640, 3] uint8 mean 121.17 | ok |
| `cctv/most_blown.jpg` | `defaults` | 381.8 | [362, 640, 3] uint8 mean 137.83 | ok |
| `cctv/most_blown.jpg` | `aggressiveness=0.1` | 371.8 | [362, 640, 3] uint8 mean 137.83 | ok |
| `cctv/most_blown.jpg` | `aggressiveness=3.0` | 378.1 | [362, 640, 3] uint8 mean 137.88 | ok |
| `cctv/sharpest.jpg` | `defaults` | 383.7 | [362, 640, 3] uint8 mean 131.5 | ok |
| `cctv/sharpest.jpg` | `aggressiveness=0.1` | 377.4 | [362, 640, 3] uint8 mean 131.5 | ok |
| `cctv/sharpest.jpg` | `aggressiveness=3.0` | 372.3 | [362, 640, 3] uint8 mean 131.53 | ok |
| `cctv/softest.jpg` | `defaults` | 407.0 | [362, 640, 3] uint8 mean 125.12 | ok |
| `cctv/softest.jpg` | `aggressiveness=0.1` | 379.7 | [362, 640, 3] uint8 mean 125.12 | ok |
| `cctv/softest.jpg` | `aggressiveness=3.0` | 369.0 | [362, 640, 3] uint8 mean 125.15 | ok |

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
