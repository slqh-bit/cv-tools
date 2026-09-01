# invert - validation result

**Invert all colour channels**  
`src.filters.invert` | family: Adjust | 2026-09-01T16:34:54

## Verdict

**PASS** - 9 runs, no invariant broken, 2 specific checks passed.

## What this filter specifically promises

- PASS - inverting twice returns the original, and once does not: an involution that actually inverts
- PASS - every value becomes its complement: output equals 255 minus input, exactly

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 0.3 | [362, 640, 3] uint8 mean 91.47 | ok |
| `cctv/darkest.jpg` | `defaults` | 0.3 | [362, 640, 3] uint8 mean 144.07 | ok |
| `cctv/event_fall.jpg` | `defaults` | 0.3 | [362, 640, 3] uint8 mean 129.49 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 0.3 | [362, 640, 3] uint8 mean 129.58 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 0.3 | [362, 640, 3] uint8 mean 94.38 | ok |
| `cctv/flattest.jpg` | `defaults` | 0.3 | [362, 640, 3] uint8 mean 133.5 | ok |
| `cctv/most_blown.jpg` | `defaults` | 0.3 | [362, 640, 3] uint8 mean 116.92 | ok |
| `cctv/sharpest.jpg` | `defaults` | 0.3 | [362, 640, 3] uint8 mean 123.24 | ok |
| `cctv/softest.jpg` | `defaults` | 0.3 | [362, 640, 3] uint8 mean 129.62 | ok |

## Artifacts

Outputs written to `validation/artifacts/invert/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
