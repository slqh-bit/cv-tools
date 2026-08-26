# selective_saturation - validation result

**Saturate only colours near a target hue**  
`src.filters.saturation` | family: Adjust | 2026-08-21T12:44:41

## Verdict

**PASS** - 45 runs, no invariant broken.

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `hue_center=30.0` | 3.3 | [362, 640, 3] uint8 mean 162.22 | ok |
| `cctv/brightest.jpg` | `hue_center=30.0, hue_range=1.0` | 3.5 | [362, 640, 3] uint8 mean 163.18 | ok |
| `cctv/brightest.jpg` | `hue_center=30.0, hue_range=180.0` | 3.2 | [362, 640, 3] uint8 mean 161.45 | ok |
| `cctv/brightest.jpg` | `hue_center=30.0, factor=0.0` | 3.0 | [362, 640, 3] uint8 mean 165.45 | ok |
| `cctv/brightest.jpg` | `hue_center=30.0, factor=3.0` | 3.3 | [362, 640, 3] uint8 mean 159.04 | ok |
| `cctv/darkest.jpg` | `hue_center=30.0` | 2.8 | [362, 640, 3] uint8 mean 110.27 | ok |
| `cctv/darkest.jpg` | `hue_center=30.0, hue_range=1.0` | 3.1 | [362, 640, 3] uint8 mean 110.64 | ok |
| `cctv/darkest.jpg` | `hue_center=30.0, hue_range=180.0` | 2.9 | [362, 640, 3] uint8 mean 109.6 | ok |
| `cctv/darkest.jpg` | `hue_center=30.0, factor=0.0` | 3.1 | [362, 640, 3] uint8 mean 111.46 | ok |
| `cctv/darkest.jpg` | `hue_center=30.0, factor=3.0` | 3.0 | [362, 640, 3] uint8 mean 109.14 | ok |
| `cctv/event_fall.jpg` | `hue_center=30.0` | 3.2 | [362, 640, 3] uint8 mean 123.65 | ok |
| `cctv/event_fall.jpg` | `hue_center=30.0, hue_range=1.0` | 3.6 | [362, 640, 3] uint8 mean 125.17 | ok |
| `cctv/event_fall.jpg` | `hue_center=30.0, hue_range=180.0` | 2.8 | [362, 640, 3] uint8 mean 121.76 | ok |
| `cctv/event_fall.jpg` | `hue_center=30.0, factor=0.0` | 2.9 | [362, 640, 3] uint8 mean 128.54 | ok |
| `cctv/event_fall.jpg` | `hue_center=30.0, factor=3.0` | 2.7 | [362, 640, 3] uint8 mean 119.58 | ok |
| `cctv/event_optflow.jpg` | `hue_center=30.0` | 2.8 | [362, 640, 3] uint8 mean 123.26 | ok |
| `cctv/event_optflow.jpg` | `hue_center=30.0, hue_range=1.0` | 3.2 | [362, 640, 3] uint8 mean 125.05 | ok |
| `cctv/event_optflow.jpg` | `hue_center=30.0, hue_range=180.0` | 3.1 | [362, 640, 3] uint8 mean 121.09 | ok |
| `cctv/event_optflow.jpg` | `hue_center=30.0, factor=0.0` | 4.4 | [362, 640, 3] uint8 mean 128.98 | ok |
| `cctv/event_optflow.jpg` | `hue_center=30.0, factor=3.0` | 3.1 | [362, 640, 3] uint8 mean 118.39 | ok |
| `cctv/event_tamper.jpg` | `hue_center=30.0` | 3.3 | [362, 640, 3] uint8 mean 159.29 | ok |
| `cctv/event_tamper.jpg` | `hue_center=30.0, hue_range=1.0` | 3.2 | [362, 640, 3] uint8 mean 160.23 | ok |
| `cctv/event_tamper.jpg` | `hue_center=30.0, hue_range=180.0` | 3.1 | [362, 640, 3] uint8 mean 158.64 | ok |
| `cctv/event_tamper.jpg` | `hue_center=30.0, factor=0.0` | 3.1 | [362, 640, 3] uint8 mean 162.55 | ok |
| `cctv/event_tamper.jpg` | `hue_center=30.0, factor=3.0` | 3.2 | [362, 640, 3] uint8 mean 156.1 | ok |
| `cctv/flattest.jpg` | `hue_center=30.0` | 3.4 | [362, 640, 3] uint8 mean 119.57 | ok |
| `cctv/flattest.jpg` | `hue_center=30.0, hue_range=1.0` | 2.8 | [362, 640, 3] uint8 mean 121.15 | ok |
| `cctv/flattest.jpg` | `hue_center=30.0, hue_range=180.0` | 2.9 | [362, 640, 3] uint8 mean 117.55 | ok |
| `cctv/flattest.jpg` | `hue_center=30.0, factor=0.0` | 2.8 | [362, 640, 3] uint8 mean 124.6 | ok |
| `cctv/flattest.jpg` | `hue_center=30.0, factor=3.0` | 3.4 | [362, 640, 3] uint8 mean 115.27 | ok |
| `cctv/most_blown.jpg` | `hue_center=30.0` | 3.2 | [362, 640, 3] uint8 mean 137.47 | ok |
| `cctv/most_blown.jpg` | `hue_center=30.0, hue_range=1.0` | 3.4 | [362, 640, 3] uint8 mean 137.8 | ok |
| `cctv/most_blown.jpg` | `hue_center=30.0, hue_range=180.0` | 3.6 | [362, 640, 3] uint8 mean 136.81 | ok |
| `cctv/most_blown.jpg` | `hue_center=30.0, factor=0.0` | 3.7 | [362, 640, 3] uint8 mean 138.54 | ok |
| `cctv/most_blown.jpg` | `hue_center=30.0, factor=3.0` | 3.6 | [362, 640, 3] uint8 mean 136.45 | ok |
| `cctv/sharpest.jpg` | `hue_center=30.0` | 3.8 | [362, 640, 3] uint8 mean 131.07 | ok |
| `cctv/sharpest.jpg` | `hue_center=30.0, hue_range=1.0` | 3.2 | [362, 640, 3] uint8 mean 131.43 | ok |
| `cctv/sharpest.jpg` | `hue_center=30.0, hue_range=180.0` | 3.4 | [362, 640, 3] uint8 mean 130.47 | ok |
| `cctv/sharpest.jpg` | `hue_center=30.0, factor=0.0` | 3.0 | [362, 640, 3] uint8 mean 132.37 | ok |
| `cctv/sharpest.jpg` | `hue_center=30.0, factor=3.0` | 3.5 | [362, 640, 3] uint8 mean 129.8 | ok |
| `cctv/softest.jpg` | `hue_center=30.0` | 2.9 | [362, 640, 3] uint8 mean 124.07 | ok |
| `cctv/softest.jpg` | `hue_center=30.0, hue_range=1.0` | 3.7 | [362, 640, 3] uint8 mean 125.04 | ok |
| `cctv/softest.jpg` | `hue_center=30.0, hue_range=180.0` | 2.8 | [362, 640, 3] uint8 mean 123.36 | ok |
| `cctv/softest.jpg` | `hue_center=30.0, factor=0.0` | 2.9 | [362, 640, 3] uint8 mean 127.2 | ok |
| `cctv/softest.jpg` | `hue_center=30.0, factor=3.0` | 2.8 | [362, 640, 3] uint8 mean 121.15 | ok |

## Artifacts

Outputs written to `validation/artifacts/selective_saturation/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
