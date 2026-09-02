# clahe_grid - validation result

**Contact sheet of CLAHE settings, for choosing one you can justify**  
`cv_tools.filters.clahe` | family: Analyze | 2026-09-01T16:35:58

## Verdict

**PASS** - 27 runs, no invariant broken.

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 7.9 | [362, 640, 3] uint8 mean 152.32 | ok |
| `cctv/brightest.jpg` | `color_mode=hsv` | 5.3 | [362, 640, 3] uint8 mean 152.93 | ok |
| `cctv/brightest.jpg` | `color_mode=yuv` | 5.0 | [362, 640, 3] uint8 mean 154.03 | ok |
| `cctv/darkest.jpg` | `defaults` | 12.2 | [362, 640, 3] uint8 mean 120.43 | ok |
| `cctv/darkest.jpg` | `color_mode=hsv` | 7.6 | [362, 640, 3] uint8 mean 120.26 | ok |
| `cctv/darkest.jpg` | `color_mode=yuv` | 5.6 | [362, 640, 3] uint8 mean 122.54 | ok |
| `cctv/event_fall.jpg` | `defaults` | 16.9 | [362, 640, 3] uint8 mean 126.47 | ok |
| `cctv/event_fall.jpg` | `color_mode=hsv` | 9.0 | [362, 640, 3] uint8 mean 125.85 | ok |
| `cctv/event_fall.jpg` | `color_mode=yuv` | 5.8 | [362, 640, 3] uint8 mean 130.38 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 12.3 | [362, 640, 3] uint8 mean 126.91 | ok |
| `cctv/event_optflow.jpg` | `color_mode=hsv` | 6.4 | [362, 640, 3] uint8 mean 124.98 | ok |
| `cctv/event_optflow.jpg` | `color_mode=yuv` | 6.1 | [362, 640, 3] uint8 mean 129.54 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 11.4 | [362, 640, 3] uint8 mean 149.64 | ok |
| `cctv/event_tamper.jpg` | `color_mode=hsv` | 6.8 | [362, 640, 3] uint8 mean 150.09 | ok |
| `cctv/event_tamper.jpg` | `color_mode=yuv` | 6.9 | [362, 640, 3] uint8 mean 151.53 | ok |
| `cctv/flattest.jpg` | `defaults` | 11.0 | [362, 640, 3] uint8 mean 125.02 | ok |
| `cctv/flattest.jpg` | `color_mode=hsv` | 6.0 | [362, 640, 3] uint8 mean 122.92 | ok |
| `cctv/flattest.jpg` | `color_mode=yuv` | 5.8 | [362, 640, 3] uint8 mean 127.58 | ok |
| `cctv/most_blown.jpg` | `defaults` | 9.9 | [362, 640, 3] uint8 mean 139.89 | ok |
| `cctv/most_blown.jpg` | `color_mode=hsv` | 6.5 | [362, 640, 3] uint8 mean 140.56 | ok |
| `cctv/most_blown.jpg` | `color_mode=yuv` | 5.8 | [362, 640, 3] uint8 mean 141.96 | ok |
| `cctv/sharpest.jpg` | `defaults` | 9.0 | [362, 640, 3] uint8 mean 134.86 | ok |
| `cctv/sharpest.jpg` | `color_mode=hsv` | 7.2 | [362, 640, 3] uint8 mean 135.57 | ok |
| `cctv/sharpest.jpg` | `color_mode=yuv` | 5.5 | [362, 640, 3] uint8 mean 137.96 | ok |
| `cctv/softest.jpg` | `defaults` | 8.6 | [362, 640, 3] uint8 mean 129.26 | ok |
| `cctv/softest.jpg` | `color_mode=hsv` | 6.5 | [362, 640, 3] uint8 mean 127.66 | ok |
| `cctv/softest.jpg` | `color_mode=yuv` | 7.1 | [362, 640, 3] uint8 mean 131.73 | ok |

## Artifacts

Outputs written to `validation/artifacts/clahe_grid/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
