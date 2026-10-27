# deblur_nonlinear - validation result

**Deconvolution of motion blur along a bent path, traced off the streak of one point**  
`cv_tools.filters.motion_deblur` | family: Forensic | 2026-10-12T19:10:48

## Verdict

**PASS** - 54 runs, no invariant broken.

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]]` | 35.5 | [362, 640, 3] uint8 mean 160.8 | ok |
| `cctv/brightest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], nois...` | 33.6 | [362, 640, 3] uint8 mean 147.13 | ok |
| `cctv/brightest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], nois...` | 33.1 | [362, 640, 3] uint8 mean 162.91 | ok |
| `cctv/brightest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], solv...` | 1808.8 | [362, 640, 3] uint8 mean 156.42 | ok |
| `cctv/brightest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], iter...` | 34.1 | [362, 640, 3] uint8 mean 160.8 | ok |
| `cctv/brightest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], iter...` | 32.5 | [362, 640, 3] uint8 mean 160.8 | ok |
| `cctv/darkest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]]` | 33.1 | [362, 640, 3] uint8 mean 109.54 | ok |
| `cctv/darkest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], nois...` | 32.9 | [362, 640, 3] uint8 mean 114.19 | ok |
| `cctv/darkest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], nois...` | 34.2 | [362, 640, 3] uint8 mean 110.65 | ok |
| `cctv/darkest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], solv...` | 1824.6 | [362, 640, 3] uint8 mean 102.78 | ok |
| `cctv/darkest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], iter...` | 34.6 | [362, 640, 3] uint8 mean 109.54 | ok |
| `cctv/darkest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], iter...` | 33.4 | [362, 640, 3] uint8 mean 109.54 | ok |
| `cctv/event_fall.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]]` | 32.7 | [362, 640, 3] uint8 mean 124.42 | ok |
| `cctv/event_fall.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], nois...` | 33.5 | [362, 640, 3] uint8 mean 124.67 | ok |
| `cctv/event_fall.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], nois...` | 31.9 | [362, 640, 3] uint8 mean 125.19 | ok |
| `cctv/event_fall.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], solv...` | 1829.8 | [362, 640, 3] uint8 mean 108.39 | ok |
| `cctv/event_fall.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], iter...` | 33.2 | [362, 640, 3] uint8 mean 124.42 | ok |
| `cctv/event_fall.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], iter...` | 33.3 | [362, 640, 3] uint8 mean 124.42 | ok |
| `cctv/event_optflow.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]]` | 34.3 | [362, 640, 3] uint8 mean 124.85 | ok |
| `cctv/event_optflow.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], nois...` | 37.3 | [362, 640, 3] uint8 mean 123.46 | ok |
| `cctv/event_optflow.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], nois...` | 33.1 | [362, 640, 3] uint8 mean 125.21 | ok |
| `cctv/event_optflow.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], solv...` | 1820.2 | [362, 640, 3] uint8 mean 117.36 | ok |
| `cctv/event_optflow.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], iter...` | 33.4 | [362, 640, 3] uint8 mean 124.85 | ok |
| `cctv/event_optflow.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], iter...` | 34.7 | [362, 640, 3] uint8 mean 124.85 | ok |
| `cctv/event_tamper.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]]` | 33.1 | [362, 640, 3] uint8 mean 158.1 | ok |
| `cctv/event_tamper.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], nois...` | 34.8 | [362, 640, 3] uint8 mean 145.55 | ok |
| `cctv/event_tamper.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], nois...` | 33.7 | [362, 640, 3] uint8 mean 160.01 | ok |
| `cctv/event_tamper.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], solv...` | 1849.3 | [362, 640, 3] uint8 mean 153.66 | ok |
| `cctv/event_tamper.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], iter...` | 33.5 | [362, 640, 3] uint8 mean 158.1 | ok |
| `cctv/event_tamper.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], iter...` | 32.4 | [362, 640, 3] uint8 mean 158.1 | ok |
| `cctv/flattest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]]` | 33.7 | [362, 640, 3] uint8 mean 121.15 | ok |
| `cctv/flattest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], nois...` | 34.0 | [362, 640, 3] uint8 mean 121.04 | ok |
| `cctv/flattest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], nois...` | 33.5 | [362, 640, 3] uint8 mean 121.29 | ok |
| `cctv/flattest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], solv...` | 1843.7 | [362, 640, 3] uint8 mean 113.84 | ok |
| `cctv/flattest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], iter...` | 34.4 | [362, 640, 3] uint8 mean 121.15 | ok |
| `cctv/flattest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], iter...` | 34.5 | [362, 640, 3] uint8 mean 121.15 | ok |
| `cctv/most_blown.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]]` | 33.2 | [362, 640, 3] uint8 mean 135.87 | ok |
| `cctv/most_blown.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], nois...` | 35.0 | [362, 640, 3] uint8 mean 132.2 | ok |
| `cctv/most_blown.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], nois...` | 33.6 | [362, 640, 3] uint8 mean 137.71 | ok |
| `cctv/most_blown.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], solv...` | 1829.5 | [362, 640, 3] uint8 mean 129.3 | ok |
| `cctv/most_blown.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], iter...` | 33.6 | [362, 640, 3] uint8 mean 135.87 | ok |
| `cctv/most_blown.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], iter...` | 36.8 | [362, 640, 3] uint8 mean 135.87 | ok |
| `cctv/sharpest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]]` | 34.3 | [362, 640, 3] uint8 mean 131.02 | ok |
| `cctv/sharpest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], nois...` | 34.1 | [362, 640, 3] uint8 mean 127.97 | ok |
| `cctv/sharpest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], nois...` | 32.9 | [362, 640, 3] uint8 mean 131.33 | ok |
| `cctv/sharpest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], solv...` | 1830.8 | [362, 640, 3] uint8 mean 114.11 | ok |
| `cctv/sharpest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], iter...` | 32.9 | [362, 640, 3] uint8 mean 131.02 | ok |
| `cctv/sharpest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], iter...` | 32.7 | [362, 640, 3] uint8 mean 131.02 | ok |
| `cctv/softest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]]` | 32.9 | [362, 640, 3] uint8 mean 125.31 | ok |
| `cctv/softest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], nois...` | 32.5 | [362, 640, 3] uint8 mean 126.18 | ok |
| `cctv/softest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], nois...` | 33.4 | [362, 640, 3] uint8 mean 124.91 | ok |
| `cctv/softest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], solv...` | 1850.8 | [362, 640, 3] uint8 mean 120.02 | ok |
| `cctv/softest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], iter...` | 33.1 | [362, 640, 3] uint8 mean 125.31 | ok |
| `cctv/softest.jpg` | `path=[[100, 100], [108, 97], [114, 97], [120, 104]], iter...` | 34.7 | [362, 640, 3] uint8 mean 125.31 | ok |

## Artifacts

Outputs written to `validation/artifacts/deblur_nonlinear/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
