# deblur_blind - validation result

**Blind deconvolution: estimates the blur from the frame. For defocus and haze, not straight motion; harms a sharp frame**  
`cv_tools.filters.motion_deblur` | family: Forensic | 2026-10-12T19:11:26

## Verdict

**PASS** - 27 runs, no invariant broken.

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `noise_power=0.0001` on `cctv/event_fall.jpg`: output identical to input
- `noise_power=0.0001` on `cctv/sharpest.jpg`: output identical to input

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 5936.4 | [362, 640, 3] uint8 mean 159.33 | ok |
| `cctv/brightest.jpg` | `noise_power=0.0001` | 5855.1 | [362, 640, 3] uint8 mean 157.99 | ok |
| `cctv/brightest.jpg` | `noise_power=0.5` | 5920.0 | [362, 640, 3] uint8 mean 160.09 | ok |
| `cctv/darkest.jpg` | `defaults` | 5796.7 | [362, 640, 3] uint8 mean 110.08 | ok |
| `cctv/darkest.jpg` | `noise_power=0.0001` | 5848.1 | [362, 640, 3] uint8 mean 109.98 | ok |
| `cctv/darkest.jpg` | `noise_power=0.5` | 5796.9 | [362, 640, 3] uint8 mean 111.83 | ok |
| `cctv/event_fall.jpg` | `defaults` | 5913.1 | [362, 640, 3] uint8 mean 125.46 | ok |
| `cctv/event_fall.jpg` | `noise_power=0.0001` | 5871.0 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_fall.jpg` | `noise_power=0.5` | 5806.4 | [362, 640, 3] uint8 mean 130.34 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 5793.0 | [362, 640, 3] uint8 mean 124.49 | ok |
| `cctv/event_optflow.jpg` | `noise_power=0.0001` | 5833.3 | [362, 640, 3] uint8 mean 124.36 | ok |
| `cctv/event_optflow.jpg` | `noise_power=0.5` | 5834.5 | [362, 640, 3] uint8 mean 126.42 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 5821.7 | [362, 640, 3] uint8 mean 156.57 | ok |
| `cctv/event_tamper.jpg` | `noise_power=0.0001` | 5792.4 | [362, 640, 3] uint8 mean 155.24 | ok |
| `cctv/event_tamper.jpg` | `noise_power=0.5` | 5828.9 | [362, 640, 3] uint8 mean 157.66 | ok |
| `cctv/flattest.jpg` | `defaults` | 5798.8 | [362, 640, 3] uint8 mean 120.61 | ok |
| `cctv/flattest.jpg` | `noise_power=0.0001` | 5827.9 | [362, 640, 3] uint8 mean 120.46 | ok |
| `cctv/flattest.jpg` | `noise_power=0.5` | 5868.8 | [362, 640, 3] uint8 mean 122.4 | ok |
| `cctv/most_blown.jpg` | `defaults` | 5806.0 | [362, 640, 3] uint8 mean 135.99 | ok |
| `cctv/most_blown.jpg` | `noise_power=0.0001` | 5831.2 | [362, 640, 3] uint8 mean 135.47 | ok |
| `cctv/most_blown.jpg` | `noise_power=0.5` | 5850.7 | [362, 640, 3] uint8 mean 137.11 | ok |
| `cctv/sharpest.jpg` | `defaults` | 5809.5 | [362, 640, 3] uint8 mean 131.69 | ok |
| `cctv/sharpest.jpg` | `noise_power=0.0001` | 5824.1 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/sharpest.jpg` | `noise_power=0.5` | 5830.2 | [362, 640, 3] uint8 mean 135.06 | ok |
| `cctv/softest.jpg` | `defaults` | 5818.6 | [362, 640, 3] uint8 mean 123.07 | ok |
| `cctv/softest.jpg` | `noise_power=0.0001` | 5797.2 | [362, 640, 3] uint8 mean 122.27 | ok |
| `cctv/softest.jpg` | `noise_power=0.5` | 5799.5 | [362, 640, 3] uint8 mean 125.63 | ok |

## Artifacts

Outputs written to `validation/artifacts/deblur_blind/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
