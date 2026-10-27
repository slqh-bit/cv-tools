# remove_periodic - validation result

**Notch out periodic pattern noise**  
`cv_tools.filters.fft_analysis` | family: Forensic | 2026-10-12T19:09:19

## Verdict

**PASS** - 45 runs, no invariant broken, 2 specific checks passed.

## What this filter specifically promises

- PASS - removes the periodic peaks it detects: 2 peaks before, 0 after
- PASS - and changes the image doing so: the output differs from the input

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 294.4 | [362, 640] uint8 mean 144.72 | ok |
| `cctv/brightest.jpg` | `notch_radius=1.0` | 310.8 | [362, 640] uint8 mean 163.98 | ok |
| `cctv/brightest.jpg` | `notch_radius=20.0` | 213.4 | [362, 640] uint8 mean 4.19 | ok |
| `cctv/brightest.jpg` | `threshold=0.0` | 302.8 | [362, 640] uint8 mean 144.72 | ok |
| `cctv/brightest.jpg` | `threshold=255.0` | 28.5 | [362, 640] uint8 mean 164.57 | ok |
| `cctv/darkest.jpg` | `defaults` | 262.6 | [362, 640] uint8 mean 110.89 | ok |
| `cctv/darkest.jpg` | `notch_radius=1.0` | 275.7 | [362, 640] uint8 mean 110.89 | ok |
| `cctv/darkest.jpg` | `notch_radius=20.0` | 197.6 | [362, 640] uint8 mean 110.89 | ok |
| `cctv/darkest.jpg` | `threshold=0.0` | 312.8 | [362, 640] uint8 mean 110.89 | ok |
| `cctv/darkest.jpg` | `threshold=255.0` | 28.6 | [362, 640] uint8 mean 111.39 | ok |
| `cctv/event_fall.jpg` | `defaults` | 89.0 | [362, 640] uint8 mean 127.35 | ok |
| `cctv/event_fall.jpg` | `notch_radius=1.0` | 87.8 | [362, 640] uint8 mean 127.35 | ok |
| `cctv/event_fall.jpg` | `notch_radius=20.0` | 77.7 | [362, 640] uint8 mean 127.36 | ok |
| `cctv/event_fall.jpg` | `threshold=0.0` | 307.9 | [362, 640] uint8 mean 127.36 | ok |
| `cctv/event_fall.jpg` | `threshold=255.0` | 30.0 | [362, 640] uint8 mean 127.85 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 298.5 | [362, 640] uint8 mean 127.61 | ok |
| `cctv/event_optflow.jpg` | `notch_radius=1.0` | 307.1 | [362, 640] uint8 mean 127.62 | ok |
| `cctv/event_optflow.jpg` | `notch_radius=20.0` | 214.2 | [362, 640] uint8 mean 127.61 | ok |
| `cctv/event_optflow.jpg` | `threshold=0.0` | 311.7 | [362, 640] uint8 mean 127.61 | ok |
| `cctv/event_optflow.jpg` | `threshold=255.0` | 28.1 | [362, 640] uint8 mean 128.11 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 299.3 | [362, 640] uint8 mean 160.83 | ok |
| `cctv/event_tamper.jpg` | `notch_radius=1.0` | 317.8 | [362, 640] uint8 mean 160.82 | ok |
| `cctv/event_tamper.jpg` | `notch_radius=20.0` | 223.4 | [362, 640] uint8 mean 160.81 | ok |
| `cctv/event_tamper.jpg` | `threshold=0.0` | 313.4 | [362, 640] uint8 mean 160.83 | ok |
| `cctv/event_tamper.jpg` | `threshold=255.0` | 28.5 | [362, 640] uint8 mean 161.33 | ok |
| `cctv/flattest.jpg` | `defaults` | 300.2 | [362, 640] uint8 mean 123.3 | ok |
| `cctv/flattest.jpg` | `notch_radius=1.0` | 310.4 | [362, 640] uint8 mean 123.3 | ok |
| `cctv/flattest.jpg` | `notch_radius=20.0` | 220.5 | [362, 640] uint8 mean 123.3 | ok |
| `cctv/flattest.jpg` | `threshold=0.0` | 305.6 | [362, 640] uint8 mean 123.3 | ok |
| `cctv/flattest.jpg` | `threshold=255.0` | 28.0 | [362, 640] uint8 mean 123.8 | ok |
| `cctv/most_blown.jpg` | `defaults` | 316.8 | [362, 640] uint8 mean 137.95 | ok |
| `cctv/most_blown.jpg` | `notch_radius=1.0` | 314.9 | [362, 640] uint8 mean 137.95 | ok |
| `cctv/most_blown.jpg` | `notch_radius=20.0` | 218.4 | [362, 640] uint8 mean 137.94 | ok |
| `cctv/most_blown.jpg` | `threshold=0.0` | 300.7 | [362, 640] uint8 mean 137.95 | ok |
| `cctv/most_blown.jpg` | `threshold=255.0` | 27.2 | [362, 640] uint8 mean 138.45 | ok |
| `cctv/sharpest.jpg` | `defaults` | 237.8 | [362, 640] uint8 mean 131.52 | ok |
| `cctv/sharpest.jpg` | `notch_radius=1.0` | 256.1 | [362, 640] uint8 mean 131.51 | ok |
| `cctv/sharpest.jpg` | `notch_radius=20.0` | 179.5 | [362, 640] uint8 mean 131.53 | ok |
| `cctv/sharpest.jpg` | `threshold=0.0` | 303.2 | [362, 640] uint8 mean 131.52 | ok |
| `cctv/sharpest.jpg` | `threshold=255.0` | 27.8 | [362, 640] uint8 mean 132.02 | ok |
| `cctv/softest.jpg` | `defaults` | 303.1 | [362, 640] uint8 mean 103.51 | ok |
| `cctv/softest.jpg` | `notch_radius=1.0` | 313.6 | [362, 640] uint8 mean 125.56 | ok |
| `cctv/softest.jpg` | `notch_radius=20.0` | 223.6 | [362, 640] uint8 mean 2.32 | ok |
| `cctv/softest.jpg` | `threshold=0.0` | 306.1 | [362, 640] uint8 mean 103.51 | ok |
| `cctv/softest.jpg` | `threshold=255.0` | 28.5 | [362, 640] uint8 mean 126.06 | ok |

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
