# flip - validation result

**Flip horizontally, vertically or both**  
`src.filters.crop_resize` | family: Adjust | 2026-09-01T16:34:49

## Verdict

**PASS** - 27 runs, no invariant broken, 4 specific checks passed.

## What this filter specifically promises

- PASS - horizontal flip is its own inverse and does something: flipping twice returns the original; once does not
- PASS - horizontal flip matches the array operation: matches numpy flip on axis 1
- PASS - vertical flip is its own inverse and does something: flipping twice returns the original; once does not
- PASS - vertical flip matches the array operation: matches numpy flip on axis 0

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 0.2 | [362, 640, 3] uint8 mean 163.53 | ok |
| `cctv/brightest.jpg` | `direction=vertical` | 0.1 | [362, 640, 3] uint8 mean 163.53 | ok |
| `cctv/brightest.jpg` | `direction=both` | 0.1 | [362, 640, 3] uint8 mean 163.53 | ok |
| `cctv/darkest.jpg` | `defaults` | 0.1 | [362, 640, 3] uint8 mean 110.93 | ok |
| `cctv/darkest.jpg` | `direction=vertical` | 0.1 | [362, 640, 3] uint8 mean 110.93 | ok |
| `cctv/darkest.jpg` | `direction=both` | 0.1 | [362, 640, 3] uint8 mean 110.93 | ok |
| `cctv/event_fall.jpg` | `defaults` | 0.1 | [362, 640, 3] uint8 mean 125.51 | ok |
| `cctv/event_fall.jpg` | `direction=vertical` | 0.1 | [362, 640, 3] uint8 mean 125.51 | ok |
| `cctv/event_fall.jpg` | `direction=both` | 0.1 | [362, 640, 3] uint8 mean 125.51 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 0.2 | [362, 640, 3] uint8 mean 125.42 | ok |
| `cctv/event_optflow.jpg` | `direction=vertical` | 0.1 | [362, 640, 3] uint8 mean 125.42 | ok |
| `cctv/event_optflow.jpg` | `direction=both` | 0.1 | [362, 640, 3] uint8 mean 125.42 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 0.1 | [362, 640, 3] uint8 mean 160.62 | ok |
| `cctv/event_tamper.jpg` | `direction=vertical` | 0.1 | [362, 640, 3] uint8 mean 160.62 | ok |
| `cctv/event_tamper.jpg` | `direction=both` | 0.1 | [362, 640, 3] uint8 mean 160.62 | ok |
| `cctv/flattest.jpg` | `defaults` | 0.2 | [362, 640, 3] uint8 mean 121.5 | ok |
| `cctv/flattest.jpg` | `direction=vertical` | 0.1 | [362, 640, 3] uint8 mean 121.5 | ok |
| `cctv/flattest.jpg` | `direction=both` | 0.1 | [362, 640, 3] uint8 mean 121.5 | ok |
| `cctv/most_blown.jpg` | `defaults` | 0.1 | [362, 640, 3] uint8 mean 138.08 | ok |
| `cctv/most_blown.jpg` | `direction=vertical` | 0.1 | [362, 640, 3] uint8 mean 138.08 | ok |
| `cctv/most_blown.jpg` | `direction=both` | 0.1 | [362, 640, 3] uint8 mean 138.08 | ok |
| `cctv/sharpest.jpg` | `defaults` | 0.1 | [362, 640, 3] uint8 mean 131.76 | ok |
| `cctv/sharpest.jpg` | `direction=vertical` | 0.1 | [362, 640, 3] uint8 mean 131.76 | ok |
| `cctv/sharpest.jpg` | `direction=both` | 0.1 | [362, 640, 3] uint8 mean 131.76 | ok |
| `cctv/softest.jpg` | `defaults` | 0.1 | [362, 640, 3] uint8 mean 125.38 | ok |
| `cctv/softest.jpg` | `direction=vertical` | 0.1 | [362, 640, 3] uint8 mean 125.38 | ok |
| `cctv/softest.jpg` | `direction=both` | 0.1 | [362, 640, 3] uint8 mean 125.38 | ok |

## Artifacts

Outputs written to `validation/artifacts/flip/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
