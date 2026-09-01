# bit_plane - validation result

**Extract one bit plane of the intensity**  
`src.filters.component_separation` | family: Special | 2026-09-01T16:37:18

## Verdict

**PASS** - 9 runs, no invariant broken, 9 specific checks passed.

## What this filter specifically promises

- PASS - plane 0 is binary: values [0, 255]
- PASS - plane 1 is binary: values [0, 255]
- PASS - plane 2 is binary: values [0, 255]
- PASS - plane 3 is binary: values [0, 255]
- PASS - plane 4 is binary: values [0, 255]
- PASS - plane 5 is binary: values [0, 255]
- PASS - plane 6 is binary: values [0, 255]
- PASS - plane 7 is binary: values [0, 255]
- PASS - plane 7 marks the pixels at or above 128: 100.00% of pixels agree with a 128 threshold

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 4.5 | [362, 640] uint8 mean 125.65 | ok |
| `cctv/darkest.jpg` | `defaults` | 4.0 | [362, 640] uint8 mean 126.36 | ok |
| `cctv/event_fall.jpg` | `defaults` | 3.2 | [362, 640] uint8 mean 128.78 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 4.4 | [362, 640] uint8 mean 127.64 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 2.9 | [362, 640] uint8 mean 129.42 | ok |
| `cctv/flattest.jpg` | `defaults` | 3.1 | [362, 640] uint8 mean 128.84 | ok |
| `cctv/most_blown.jpg` | `defaults` | 2.9 | [362, 640] uint8 mean 125.36 | ok |
| `cctv/sharpest.jpg` | `defaults` | 3.2 | [362, 640] uint8 mean 126.97 | ok |
| `cctv/softest.jpg` | `defaults` | 2.8 | [362, 640] uint8 mean 126.43 | ok |

## Artifacts

Outputs written to `validation/artifacts/bit_plane/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
