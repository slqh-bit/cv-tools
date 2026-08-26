# remove_periodic - validation result

**Notch out periodic pattern noise**  
`src.filters.fft_analysis` | family: Forensic | 2026-08-21T12:45:48

## Verdict

**PASS** - 45 runs, no invariant broken, 2 specific checks passed.

## What this filter specifically promises

- PASS - removes the periodic peaks it detects: 2 peaks before, 0 after
- PASS - and changes the image doing so: the output differs from the input

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 294.0 | [362, 640] uint8 mean 144.72 | ok |
| `cctv/brightest.jpg` | `notch_radius=1.0` | 307.4 | [362, 640] uint8 mean 163.98 | ok |
| `cctv/brightest.jpg` | `notch_radius=20.0` | 211.1 | [362, 640] uint8 mean 4.19 | ok |
| `cctv/brightest.jpg` | `threshold=0.0` | 300.4 | [362, 640] uint8 mean 144.72 | ok |
| `cctv/brightest.jpg` | `threshold=255.0` | 27.9 | [362, 640] uint8 mean 164.57 | ok |
| `cctv/darkest.jpg` | `defaults` | 257.9 | [362, 640] uint8 mean 110.89 | ok |
| `cctv/darkest.jpg` | `notch_radius=1.0` | 273.1 | [362, 640] uint8 mean 110.89 | ok |
| `cctv/darkest.jpg` | `notch_radius=20.0` | 188.9 | [362, 640] uint8 mean 110.89 | ok |
| `cctv/darkest.jpg` | `threshold=0.0` | 300.4 | [362, 640] uint8 mean 110.89 | ok |
| `cctv/darkest.jpg` | `threshold=255.0` | 28.0 | [362, 640] uint8 mean 111.39 | ok |
| `cctv/event_fall.jpg` | `defaults` | 86.9 | [362, 640] uint8 mean 127.35 | ok |
| `cctv/event_fall.jpg` | `notch_radius=1.0` | 86.5 | [362, 640] uint8 mean 127.35 | ok |
| `cctv/event_fall.jpg` | `notch_radius=20.0` | 77.7 | [362, 640] uint8 mean 127.36 | ok |
| `cctv/event_fall.jpg` | `threshold=0.0` | 299.8 | [362, 640] uint8 mean 127.36 | ok |
| `cctv/event_fall.jpg` | `threshold=255.0` | 27.7 | [362, 640] uint8 mean 127.85 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 292.6 | [362, 640] uint8 mean 127.61 | ok |
| `cctv/event_optflow.jpg` | `notch_radius=1.0` | 307.2 | [362, 640] uint8 mean 127.62 | ok |
| `cctv/event_optflow.jpg` | `notch_radius=20.0` | 211.6 | [362, 640] uint8 mean 127.61 | ok |
| `cctv/event_optflow.jpg` | `threshold=0.0` | 301.6 | [362, 640] uint8 mean 127.61 | ok |
| `cctv/event_optflow.jpg` | `threshold=255.0` | 28.2 | [362, 640] uint8 mean 128.11 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 291.3 | [362, 640] uint8 mean 160.83 | ok |
| `cctv/event_tamper.jpg` | `notch_radius=1.0` | 309.5 | [362, 640] uint8 mean 160.82 | ok |
| `cctv/event_tamper.jpg` | `notch_radius=20.0` | 212.1 | [362, 640] uint8 mean 160.81 | ok |
| `cctv/event_tamper.jpg` | `threshold=0.0` | 328.2 | [362, 640] uint8 mean 160.83 | ok |
| `cctv/event_tamper.jpg` | `threshold=255.0` | 30.2 | [362, 640] uint8 mean 161.33 | ok |
| `cctv/flattest.jpg` | `defaults` | 292.4 | [362, 640] uint8 mean 123.3 | ok |
| `cctv/flattest.jpg` | `notch_radius=1.0` | 306.0 | [362, 640] uint8 mean 123.3 | ok |
| `cctv/flattest.jpg` | `notch_radius=20.0` | 212.5 | [362, 640] uint8 mean 123.3 | ok |
| `cctv/flattest.jpg` | `threshold=0.0` | 300.9 | [362, 640] uint8 mean 123.3 | ok |
| `cctv/flattest.jpg` | `threshold=255.0` | 28.0 | [362, 640] uint8 mean 123.8 | ok |
| `cctv/most_blown.jpg` | `defaults` | 292.8 | [362, 640] uint8 mean 137.95 | ok |
| `cctv/most_blown.jpg` | `notch_radius=1.0` | 305.4 | [362, 640] uint8 mean 137.95 | ok |
| `cctv/most_blown.jpg` | `notch_radius=20.0` | 212.1 | [362, 640] uint8 mean 137.94 | ok |
| `cctv/most_blown.jpg` | `threshold=0.0` | 302.0 | [362, 640] uint8 mean 137.95 | ok |
| `cctv/most_blown.jpg` | `threshold=255.0` | 28.1 | [362, 640] uint8 mean 138.45 | ok |
| `cctv/sharpest.jpg` | `defaults` | 236.4 | [362, 640] uint8 mean 131.52 | ok |
| `cctv/sharpest.jpg` | `notch_radius=1.0` | 247.3 | [362, 640] uint8 mean 131.51 | ok |
| `cctv/sharpest.jpg` | `notch_radius=20.0` | 174.3 | [362, 640] uint8 mean 131.53 | ok |
| `cctv/sharpest.jpg` | `threshold=0.0` | 301.1 | [362, 640] uint8 mean 131.52 | ok |
| `cctv/sharpest.jpg` | `threshold=255.0` | 27.8 | [362, 640] uint8 mean 132.02 | ok |
| `cctv/softest.jpg` | `defaults` | 294.2 | [362, 640] uint8 mean 103.51 | ok |
| `cctv/softest.jpg` | `notch_radius=1.0` | 308.9 | [362, 640] uint8 mean 125.56 | ok |
| `cctv/softest.jpg` | `notch_radius=20.0` | 209.7 | [362, 640] uint8 mean 2.32 | ok |
| `cctv/softest.jpg` | `threshold=0.0` | 303.5 | [362, 640] uint8 mean 103.51 | ok |
| `cctv/softest.jpg` | `threshold=255.0` | 27.8 | [362, 640] uint8 mean 126.06 | ok |

## Artifacts

Outputs written to `validation/artifacts/remove_periodic/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
