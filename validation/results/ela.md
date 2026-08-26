# ela - validation result

**Error Level Analysis map**  
`src.filters.ela` | family: Forensic | 2026-08-21T12:45:43

## Verdict

**PASS** - 66 runs, no invariant broken.

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 4.8 | [362, 640, 3] uint8 mean 9.12 | ok |
| `cctv/brightest.jpg` | `quality=1` | 4.2 | [362, 640, 3] uint8 mean 15.22 | ok |
| `cctv/brightest.jpg` | `quality=100` | 5.0 | [362, 640, 3] uint8 mean 3.26 | ok |
| `cctv/brightest.jpg` | `scale=0.1` | 4.6 | [362, 640, 3] uint8 mean 0.0 | ok |
| `cctv/brightest.jpg` | `scale=8.0` | 4.7 | [362, 640, 3] uint8 mean 4.05 | ok |
| `cctv/brightest.jpg` | `grayscale=True` | 10.0 | [362, 640] uint8 mean 12.19 | ok |
| `cctv/darkest.jpg` | `defaults` | 4.8 | [362, 640, 3] uint8 mean 9.26 | ok |
| `cctv/darkest.jpg` | `quality=1` | 4.0 | [362, 640, 3] uint8 mean 16.71 | ok |
| `cctv/darkest.jpg` | `quality=100` | 5.5 | [362, 640, 3] uint8 mean 3.4 | ok |
| `cctv/darkest.jpg` | `scale=0.1` | 5.0 | [362, 640, 3] uint8 mean 0.0 | ok |
| `cctv/darkest.jpg` | `scale=8.0` | 6.4 | [362, 640, 3] uint8 mean 4.11 | ok |
| `cctv/darkest.jpg` | `grayscale=True` | 10.6 | [362, 640] uint8 mean 12.42 | ok |
| `cctv/event_fall.jpg` | `defaults` | 5.8 | [362, 640, 3] uint8 mean 15.86 | ok |
| `cctv/event_fall.jpg` | `quality=1` | 4.5 | [362, 640, 3] uint8 mean 19.51 | ok |
| `cctv/event_fall.jpg` | `quality=100` | 6.2 | [362, 640, 3] uint8 mean 6.11 | ok |
| `cctv/event_fall.jpg` | `scale=0.1` | 4.9 | [362, 640, 3] uint8 mean 0.0 | ok |
| `cctv/event_fall.jpg` | `scale=8.0` | 4.8 | [362, 640, 3] uint8 mean 11.19 | ok |
| `cctv/event_fall.jpg` | `grayscale=True` | 10.1 | [362, 640] uint8 mean 22.91 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 4.8 | [362, 640, 3] uint8 mean 8.35 | ok |
| `cctv/event_optflow.jpg` | `quality=1` | 4.2 | [362, 640, 3] uint8 mean 21.91 | ok |
| `cctv/event_optflow.jpg` | `quality=100` | 5.4 | [362, 640, 3] uint8 mean 5.86 | ok |
| `cctv/event_optflow.jpg` | `scale=0.1` | 4.3 | [362, 640, 3] uint8 mean 0.0 | ok |
| `cctv/event_optflow.jpg` | `scale=8.0` | 4.5 | [362, 640, 3] uint8 mean 5.1 | ok |
| `cctv/event_optflow.jpg` | `grayscale=True` | 10.4 | [362, 640] uint8 mean 13.33 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 5.2 | [362, 640, 3] uint8 mean 9.71 | ok |
| `cctv/event_tamper.jpg` | `quality=1` | 4.4 | [362, 640, 3] uint8 mean 16.8 | ok |
| `cctv/event_tamper.jpg` | `quality=100` | 5.4 | [362, 640, 3] uint8 mean 3.81 | ok |
| `cctv/event_tamper.jpg` | `scale=0.1` | 4.5 | [362, 640, 3] uint8 mean 0.0 | ok |
| `cctv/event_tamper.jpg` | `scale=8.0` | 6.1 | [362, 640, 3] uint8 mean 4.04 | ok |
| `cctv/event_tamper.jpg` | `grayscale=True` | 10.1 | [362, 640] uint8 mean 12.94 | ok |
| `cctv/flattest.jpg` | `defaults` | 5.3 | [362, 640, 3] uint8 mean 8.4 | ok |
| `cctv/flattest.jpg` | `quality=1` | 4.2 | [362, 640, 3] uint8 mean 21.15 | ok |
| `cctv/flattest.jpg` | `quality=100` | 5.5 | [362, 640, 3] uint8 mean 5.07 | ok |
| `cctv/flattest.jpg` | `scale=0.1` | 4.6 | [362, 640, 3] uint8 mean 0.0 | ok |
| `cctv/flattest.jpg` | `scale=8.0` | 4.5 | [362, 640, 3] uint8 mean 4.8 | ok |
| `cctv/flattest.jpg` | `grayscale=True` | 9.7 | [362, 640] uint8 mean 13.41 | ok |
| `cctv/most_blown.jpg` | `defaults` | 4.7 | [362, 640, 3] uint8 mean 10.03 | ok |
| `cctv/most_blown.jpg` | `quality=1` | 4.3 | [362, 640, 3] uint8 mean 16.94 | ok |
| `cctv/most_blown.jpg` | `quality=100` | 5.1 | [362, 640, 3] uint8 mean 3.74 | ok |
| `cctv/most_blown.jpg` | `scale=0.1` | 4.5 | [362, 640, 3] uint8 mean 0.0 | ok |
| `cctv/most_blown.jpg` | `scale=8.0` | 4.6 | [362, 640, 3] uint8 mean 4.46 | ok |
| `cctv/most_blown.jpg` | `grayscale=True` | 9.8 | [362, 640] uint8 mean 13.47 | ok |
| `cctv/sharpest.jpg` | `defaults` | 5.0 | [362, 640, 3] uint8 mean 16.11 | ok |
| `cctv/sharpest.jpg` | `quality=1` | 4.4 | [362, 640, 3] uint8 mean 16.37 | ok |
| `cctv/sharpest.jpg` | `quality=100` | 6.0 | [362, 640, 3] uint8 mean 4.75 | ok |
| `cctv/sharpest.jpg` | `scale=0.1` | 4.7 | [362, 640, 3] uint8 mean 0.0 | ok |
| `cctv/sharpest.jpg` | `scale=8.0` | 5.0 | [362, 640, 3] uint8 mean 10.34 | ok |
| `cctv/sharpest.jpg` | `grayscale=True` | 10.4 | [362, 640] uint8 mean 20.54 | ok |
| `cctv/softest.jpg` | `defaults` | 4.9 | [362, 640, 3] uint8 mean 9.4 | ok |
| `cctv/softest.jpg` | `quality=1` | 4.2 | [362, 640, 3] uint8 mean 17.36 | ok |
| `cctv/softest.jpg` | `quality=100` | 5.1 | [362, 640, 3] uint8 mean 2.32 | ok |
| `cctv/softest.jpg` | `scale=0.1` | 4.6 | [362, 640, 3] uint8 mean 0.0 | ok |
| `cctv/softest.jpg` | `scale=8.0` | 4.5 | [362, 640, 3] uint8 mean 3.27 | ok |
| `cctv/softest.jpg` | `grayscale=True` | 9.8 | [362, 640] uint8 mean 12.19 | ok |
| `ground_truth/quality_splice.jpg` | `defaults` | 5.1 | [362, 640, 3] uint8 mean 14.07 | ok |
| `ground_truth/quality_splice.jpg` | `quality=1` | 4.3 | [362, 640, 3] uint8 mean 16.38 | ok |
| `ground_truth/quality_splice.jpg` | `quality=100` | 5.7 | [362, 640, 3] uint8 mean 4.7 | ok |
| `ground_truth/quality_splice.jpg` | `scale=0.1` | 4.8 | [362, 640, 3] uint8 mean 0.0 | ok |
| `ground_truth/quality_splice.jpg` | `scale=8.0` | 4.7 | [362, 640, 3] uint8 mean 9.93 | ok |
| `ground_truth/quality_splice.jpg` | `grayscale=True` | 10.1 | [362, 640] uint8 mean 18.02 | ok |
| `ground_truth/clean_control.jpg` | `defaults` | 5.6 | [362, 640, 3] uint8 mean 14.69 | ok |
| `ground_truth/clean_control.jpg` | `quality=1` | 4.3 | [362, 640, 3] uint8 mean 16.37 | ok |
| `ground_truth/clean_control.jpg` | `quality=100` | 5.7 | [362, 640, 3] uint8 mean 4.01 | ok |
| `ground_truth/clean_control.jpg` | `scale=0.1` | 4.6 | [362, 640, 3] uint8 mean 0.0 | ok |
| `ground_truth/clean_control.jpg` | `scale=8.0` | 4.7 | [362, 640, 3] uint8 mean 10.37 | ok |
| `ground_truth/clean_control.jpg` | `grayscale=True` | 10.2 | [362, 640] uint8 mean 18.62 | ok |

## Artifacts

Outputs written to `validation/artifacts/ela/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
- `ground_truth_clean_control.png`
- `ground_truth_quality_splice.png`
