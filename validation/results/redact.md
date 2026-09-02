# redact - validation result

**Obscure a region (fill/noise destroy, blur/pixelate do not)**  
`cv_tools.filters.redaction` | family: Special | 2026-09-01T16:37:18

## Verdict

**PASS** - 45 runs, no invariant broken, 7 specific checks passed.

## What this filter specifically promises

- PASS - fill destroys the region beyond recovery: is_reversible=False, safe=True, residual correlation with the original 0.0000
- PASS - noise destroys the region beyond recovery: is_reversible=False, safe=True, residual correlation with the original 0.0016
- PASS - blur is correctly reported as not safe: residual correlation 0.8702 - recoverable, which is why it is not offered as redaction
- PASS - pixelate is correctly reported as not safe: residual correlation 0.9090 - recoverable, which is why it is not offered as redaction
- PASS - a seed makes noise redaction replay identically: the same seed reproduces the frame exactly; without one the noise differs every run
- PASS - seeding does not weaken the redaction: residual correlation 0.0012 with a known seed - the original pixels are discarded either way
- PASS - nothing outside the region changes: 203680 pixels outside the box compared

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `x=120, y=80, width=200, height=140` | 0.3 | [362, 640, 3] uint8 mean 143.98 | ok |
| `cctv/brightest.jpg` | `x=120, y=80, width=200, height=140, method=noise` | 0.4 | [362, 640, 3] uint8 mean 159.37 | ok |
| `cctv/brightest.jpg` | `x=120, y=80, width=200, height=140, method=blur` | 7.5 | [362, 640, 3] uint8 mean 163.54 | ok |
| `cctv/brightest.jpg` | `x=120, y=80, width=200, height=140, blur_radius=0.1` | 0.3 | [362, 640, 3] uint8 mean 143.98 | ok |
| `cctv/brightest.jpg` | `x=120, y=80, width=200, height=140, blur_radius=50.0` | 0.3 | [362, 640, 3] uint8 mean 143.98 | ok |
| `cctv/darkest.jpg` | `x=120, y=80, width=200, height=140` | 0.3 | [362, 640, 3] uint8 mean 94.17 | ok |
| `cctv/darkest.jpg` | `x=120, y=80, width=200, height=140, method=noise` | 0.3 | [362, 640, 3] uint8 mean 109.56 | ok |
| `cctv/darkest.jpg` | `x=120, y=80, width=200, height=140, method=blur` | 7.7 | [362, 640, 3] uint8 mean 110.94 | ok |
| `cctv/darkest.jpg` | `x=120, y=80, width=200, height=140, blur_radius=0.1` | 0.3 | [362, 640, 3] uint8 mean 94.17 | ok |
| `cctv/darkest.jpg` | `x=120, y=80, width=200, height=140, blur_radius=50.0` | 0.2 | [362, 640, 3] uint8 mean 94.17 | ok |
| `cctv/event_fall.jpg` | `x=120, y=80, width=200, height=140` | 0.3 | [362, 640, 3] uint8 mean 111.13 | ok |
| `cctv/event_fall.jpg` | `x=120, y=80, width=200, height=140, method=noise` | 0.4 | [362, 640, 3] uint8 mean 126.57 | ok |
| `cctv/event_fall.jpg` | `x=120, y=80, width=200, height=140, method=blur` | 8.5 | [362, 640, 3] uint8 mean 125.5 | ok |
| `cctv/event_fall.jpg` | `x=120, y=80, width=200, height=140, blur_radius=0.1` | 0.3 | [362, 640, 3] uint8 mean 111.13 | ok |
| `cctv/event_fall.jpg` | `x=120, y=80, width=200, height=140, blur_radius=50.0` | 0.3 | [362, 640, 3] uint8 mean 111.13 | ok |
| `cctv/event_optflow.jpg` | `x=120, y=80, width=200, height=140` | 0.3 | [362, 640, 3] uint8 mean 110.08 | ok |
| `cctv/event_optflow.jpg` | `x=120, y=80, width=200, height=140, method=noise` | 0.4 | [362, 640, 3] uint8 mean 125.48 | ok |
| `cctv/event_optflow.jpg` | `x=120, y=80, width=200, height=140, method=blur` | 8.0 | [362, 640, 3] uint8 mean 125.41 | ok |
| `cctv/event_optflow.jpg` | `x=120, y=80, width=200, height=140, blur_radius=0.1` | 0.3 | [362, 640, 3] uint8 mean 110.08 | ok |
| `cctv/event_optflow.jpg` | `x=120, y=80, width=200, height=140, blur_radius=50.0` | 0.4 | [362, 640, 3] uint8 mean 110.08 | ok |
| `cctv/event_tamper.jpg` | `x=120, y=80, width=200, height=140` | 0.3 | [362, 640, 3] uint8 mean 141.42 | ok |
| `cctv/event_tamper.jpg` | `x=120, y=80, width=200, height=140, method=noise` | 0.3 | [362, 640, 3] uint8 mean 156.79 | ok |
| `cctv/event_tamper.jpg` | `x=120, y=80, width=200, height=140, method=blur` | 8.1 | [362, 640, 3] uint8 mean 160.63 | ok |
| `cctv/event_tamper.jpg` | `x=120, y=80, width=200, height=140, blur_radius=0.1` | 0.3 | [362, 640, 3] uint8 mean 141.42 | ok |
| `cctv/event_tamper.jpg` | `x=120, y=80, width=200, height=140, blur_radius=50.0` | 0.3 | [362, 640, 3] uint8 mean 141.42 | ok |
| `cctv/flattest.jpg` | `x=120, y=80, width=200, height=140` | 0.3 | [362, 640, 3] uint8 mean 106.55 | ok |
| `cctv/flattest.jpg` | `x=120, y=80, width=200, height=140, method=noise` | 0.3 | [362, 640, 3] uint8 mean 121.99 | ok |
| `cctv/flattest.jpg` | `x=120, y=80, width=200, height=140, method=blur` | 7.7 | [362, 640, 3] uint8 mean 121.49 | ok |
| `cctv/flattest.jpg` | `x=120, y=80, width=200, height=140, blur_radius=0.1` | 0.4 | [362, 640, 3] uint8 mean 106.55 | ok |
| `cctv/flattest.jpg` | `x=120, y=80, width=200, height=140, blur_radius=50.0` | 0.3 | [362, 640, 3] uint8 mean 106.55 | ok |
| `cctv/most_blown.jpg` | `x=120, y=80, width=200, height=140` | 0.3 | [362, 640, 3] uint8 mean 118.13 | ok |
| `cctv/most_blown.jpg` | `x=120, y=80, width=200, height=140, method=noise` | 0.3 | [362, 640, 3] uint8 mean 133.52 | ok |
| `cctv/most_blown.jpg` | `x=120, y=80, width=200, height=140, method=blur` | 7.6 | [362, 640, 3] uint8 mean 138.08 | ok |
| `cctv/most_blown.jpg` | `x=120, y=80, width=200, height=140, blur_radius=0.1` | 0.3 | [362, 640, 3] uint8 mean 118.13 | ok |
| `cctv/most_blown.jpg` | `x=120, y=80, width=200, height=140, blur_radius=50.0` | 0.2 | [362, 640, 3] uint8 mean 118.13 | ok |
| `cctv/sharpest.jpg` | `x=120, y=80, width=200, height=140` | 0.4 | [362, 640, 3] uint8 mean 113.6 | ok |
| `cctv/sharpest.jpg` | `x=120, y=80, width=200, height=140, method=noise` | 0.4 | [362, 640, 3] uint8 mean 129.05 | ok |
| `cctv/sharpest.jpg` | `x=120, y=80, width=200, height=140, method=blur` | 7.6 | [362, 640, 3] uint8 mean 131.75 | ok |
| `cctv/sharpest.jpg` | `x=120, y=80, width=200, height=140, blur_radius=0.1` | 0.3 | [362, 640, 3] uint8 mean 113.6 | ok |
| `cctv/sharpest.jpg` | `x=120, y=80, width=200, height=140, blur_radius=50.0` | 0.3 | [362, 640, 3] uint8 mean 113.6 | ok |
| `cctv/softest.jpg` | `x=120, y=80, width=200, height=140` | 0.3 | [362, 640, 3] uint8 mean 110.46 | ok |
| `cctv/softest.jpg` | `x=120, y=80, width=200, height=140, method=noise` | 0.3 | [362, 640, 3] uint8 mean 125.83 | ok |
| `cctv/softest.jpg` | `x=120, y=80, width=200, height=140, method=blur` | 7.5 | [362, 640, 3] uint8 mean 125.39 | ok |
| `cctv/softest.jpg` | `x=120, y=80, width=200, height=140, blur_radius=0.1` | 0.3 | [362, 640, 3] uint8 mean 110.46 | ok |
| `cctv/softest.jpg` | `x=120, y=80, width=200, height=140, blur_radius=50.0` | 0.2 | [362, 640, 3] uint8 mean 110.46 | ok |

## Artifacts

Outputs written to `validation/artifacts/redact/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
