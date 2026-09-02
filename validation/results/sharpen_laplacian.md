# sharpen_laplacian - validation result

**Laplacian sharpening**  
`cv_tools.filters.sharpen` | family: Enhance | 2026-09-01T16:34:58

## Verdict

**PASS** - 27 runs, no invariant broken.

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `strength=0.0` on `cctv/brightest.jpg`: output identical to input
- `strength=0.0` on `cctv/darkest.jpg`: output identical to input
- `strength=0.0` on `cctv/event_fall.jpg`: output identical to input
- `strength=0.0` on `cctv/event_optflow.jpg`: output identical to input
- `strength=0.0` on `cctv/event_tamper.jpg`: output identical to input
- `strength=0.0` on `cctv/flattest.jpg`: output identical to input
- `strength=0.0` on `cctv/most_blown.jpg`: output identical to input
- `strength=0.0` on `cctv/sharpest.jpg`: output identical to input
- `strength=0.0` on `cctv/softest.jpg`: output identical to input

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 5.9 | [362, 640, 3] uint8 mean 161.6 | ok |
| `cctv/brightest.jpg` | `strength=0.0` | 5.8 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/brightest.jpg` | `strength=2.0` | 5.5 | [362, 640, 3] uint8 mean 158.49 | ok |
| `cctv/darkest.jpg` | `defaults` | 5.7 | [362, 640, 3] uint8 mean 112.11 | ok |
| `cctv/darkest.jpg` | `strength=0.0` | 5.7 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/darkest.jpg` | `strength=2.0` | 5.6 | [362, 640, 3] uint8 mean 113.89 | ok |
| `cctv/event_fall.jpg` | `defaults` | 5.6 | [362, 640, 3] uint8 mean 127.26 | ok |
| `cctv/event_fall.jpg` | `strength=0.0` | 5.9 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_fall.jpg` | `strength=2.0` | 5.4 | [362, 640, 3] uint8 mean 128.1 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 5.5 | [362, 640, 3] uint8 mean 126.19 | ok |
| `cctv/event_optflow.jpg` | `strength=0.0` | 5.8 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_optflow.jpg` | `strength=2.0` | 9.5 | [362, 640, 3] uint8 mean 126.78 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 6.7 | [362, 640, 3] uint8 mean 158.84 | ok |
| `cctv/event_tamper.jpg` | `strength=0.0` | 6.7 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/event_tamper.jpg` | `strength=2.0` | 6.0 | [362, 640, 3] uint8 mean 155.86 | ok |
| `cctv/flattest.jpg` | `defaults` | 5.9 | [362, 640, 3] uint8 mean 122.35 | ok |
| `cctv/flattest.jpg` | `strength=0.0` | 5.8 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/flattest.jpg` | `strength=2.0` | 5.9 | [362, 640, 3] uint8 mean 123.14 | ok |
| `cctv/most_blown.jpg` | `defaults` | 5.8 | [362, 640, 3] uint8 mean 138.81 | ok |
| `cctv/most_blown.jpg` | `strength=0.0` | 5.9 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/most_blown.jpg` | `strength=2.0` | 5.9 | [362, 640, 3] uint8 mean 139.49 | ok |
| `cctv/sharpest.jpg` | `defaults` | 5.9 | [362, 640, 3] uint8 mean 133.8 | ok |
| `cctv/sharpest.jpg` | `strength=0.0` | 5.6 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/sharpest.jpg` | `strength=2.0` | 5.6 | [362, 640, 3] uint8 mean 134.42 | ok |
| `cctv/softest.jpg` | `defaults` | 5.8 | [362, 640, 3] uint8 mean 126.54 | ok |
| `cctv/softest.jpg` | `strength=0.0` | 5.8 | [362, 640, 3] uint8 mean 125.38 | output identical to input |
| `cctv/softest.jpg` | `strength=2.0` | 6.5 | [362, 640, 3] uint8 mean 126.53 | ok |

## Artifacts

Outputs written to `validation/artifacts/sharpen_laplacian/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
