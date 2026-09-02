# saturation - validation result

**Uniform saturation scaling**  
`cv_tools.filters.saturation` | family: Adjust | 2026-09-01T16:34:52

## Verdict

**PASS** - 27 runs, no invariant broken, 16 specific checks passed.

## What this filter specifically promises

- PASS - factor 1.0 returns the image within colour-space rounding: largest difference 2/255, from the HSV round trip rather than the scaling
- PASS - above 1 raises saturation, below 1 lowers it: 13.9 < 25.4 < 36.9 mean S
- PASS - zero saturation leaves no colour at all: mean S 0.00
- PASS - desaturate luminance produces a neutral image: single channel (362, 640), no chroma to hold
- PASS - desaturate average produces a neutral image: single channel (362, 640), no chroma to hold
- PASS - desaturate lightness produces a neutral image: single channel (362, 640), no chroma to hold
- PASS - desaturate max produces a neutral image: single channel (362, 640), no chroma to hold
- PASS - desaturate min produces a neutral image: single channel (362, 640), no chroma to hold
- PASS - saturation does not move content: the marker centred at (163.5, 163.5) reads centred at (163.5, 163.5)
- PASS - saturation keeps the red block red: channel 0 dominates, expected 0
- PASS - saturation keeps the green block green: channel 1 dominates, expected 1
- PASS - saturation keeps the blue block blue: channel 2 dominates, expected 2
- PASS - saturation reaches both halves of the frame: mean change 8.53 left against 8.52 right
- PASS - saturation: factor moves the result up across its whole range: 0:0.00, 0.6:33.93, 1.2:67.18, 1.8:99.65, 2.4:126.25, 3:148.22
- PASS - saturation: the measure still separates values in the upper half of the factor range: the top half moves 48.57 of a total 148.22
- PASS - saturation: no factor on the slider flattens the image: all 6 sampled values keep image structure

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 2.6 | [362, 640, 3] uint8 mean 163.25 | ok |
| `cctv/brightest.jpg` | `factor=0.0` | 2.8 | [362, 640, 3] uint8 mean 169.8 | ok |
| `cctv/brightest.jpg` | `factor=3.0` | 2.6 | [362, 640, 3] uint8 mean 151.1 | ok |
| `cctv/darkest.jpg` | `defaults` | 2.4 | [362, 640, 3] uint8 mean 110.65 | ok |
| `cctv/darkest.jpg` | `factor=0.0` | 2.0 | [362, 640, 3] uint8 mean 115.44 | ok |
| `cctv/darkest.jpg` | `factor=3.0` | 2.1 | [362, 640, 3] uint8 mean 102.24 | ok |
| `cctv/event_fall.jpg` | `defaults` | 1.9 | [362, 640, 3] uint8 mean 125.22 | ok |
| `cctv/event_fall.jpg` | `factor=0.0` | 3.0 | [362, 640, 3] uint8 mean 137.11 | ok |
| `cctv/event_fall.jpg` | `factor=3.0` | 1.8 | [362, 640, 3] uint8 mean 106.47 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 2.1 | [362, 640, 3] uint8 mean 125.11 | ok |
| `cctv/event_optflow.jpg` | `factor=0.0` | 2.5 | [362, 640, 3] uint8 mean 138.24 | ok |
| `cctv/event_optflow.jpg` | `factor=3.0` | 2.1 | [362, 640, 3] uint8 mean 103.85 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 2.3 | [362, 640, 3] uint8 mean 160.33 | ok |
| `cctv/event_tamper.jpg` | `factor=0.0` | 2.1 | [362, 640, 3] uint8 mean 166.97 | ok |
| `cctv/event_tamper.jpg` | `factor=3.0` | 2.0 | [362, 640, 3] uint8 mean 147.98 | ok |
| `cctv/flattest.jpg` | `defaults` | 2.1 | [362, 640, 3] uint8 mean 121.2 | ok |
| `cctv/flattest.jpg` | `factor=0.0` | 2.1 | [362, 640, 3] uint8 mean 133.77 | ok |
| `cctv/flattest.jpg` | `factor=3.0` | 2.1 | [362, 640, 3] uint8 mean 100.36 | ok |
| `cctv/most_blown.jpg` | `defaults` | 2.8 | [362, 640, 3] uint8 mean 137.81 | ok |
| `cctv/most_blown.jpg` | `factor=0.0` | 2.6 | [362, 640, 3] uint8 mean 142.47 | ok |
| `cctv/most_blown.jpg` | `factor=3.0` | 2.2 | [362, 640, 3] uint8 mean 129.68 | ok |
| `cctv/sharpest.jpg` | `defaults` | 2.5 | [362, 640, 3] uint8 mean 131.48 | ok |
| `cctv/sharpest.jpg` | `factor=0.0` | 2.1 | [362, 640, 3] uint8 mean 136.13 | ok |
| `cctv/sharpest.jpg` | `factor=3.0` | 1.9 | [362, 640, 3] uint8 mean 123.49 | ok |
| `cctv/softest.jpg` | `defaults` | 1.9 | [362, 640, 3] uint8 mean 125.07 | ok |
| `cctv/softest.jpg` | `factor=0.0` | 2.0 | [362, 640, 3] uint8 mean 132.02 | ok |
| `cctv/softest.jpg` | `factor=3.0` | 2.0 | [362, 640, 3] uint8 mean 112.46 | ok |

## Artifacts

Outputs written to `validation/artifacts/saturation/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
