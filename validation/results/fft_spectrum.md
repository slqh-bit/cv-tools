# fft_spectrum - validation result

**FFT magnitude spectrum**  
`src.filters.fft_analysis` | family: Forensic | 2026-09-01T16:36:01

## Verdict

**PASS** - 27 runs, no invariant broken.

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 23.3 | [362, 640] uint8 mean 113.1 | ok |
| `cctv/brightest.jpg` | `log_scale=False` | 21.1 | [362, 640] uint8 mean 0.0 | ok |
| `cctv/brightest.jpg` | `normalize=False` | 26.7 | [362, 640] uint8 mean 7.28 | ok |
| `cctv/darkest.jpg` | `defaults` | 29.2 | [362, 640] uint8 mean 118.38 | ok |
| `cctv/darkest.jpg` | `log_scale=False` | 22.2 | [362, 640] uint8 mean 0.01 | ok |
| `cctv/darkest.jpg` | `normalize=False` | 22.3 | [362, 640] uint8 mean 7.46 | ok |
| `cctv/event_fall.jpg` | `defaults` | 23.1 | [362, 640] uint8 mean 127.92 | ok |
| `cctv/event_fall.jpg` | `log_scale=False` | 23.2 | [362, 640] uint8 mean 0.01 | ok |
| `cctv/event_fall.jpg` | `normalize=False` | 21.7 | [362, 640] uint8 mean 8.16 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 23.7 | [362, 640] uint8 mean 116.78 | ok |
| `cctv/event_optflow.jpg` | `log_scale=False` | 22.6 | [362, 640] uint8 mean 0.01 | ok |
| `cctv/event_optflow.jpg` | `normalize=False` | 24.7 | [362, 640] uint8 mean 7.41 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 23.5 | [362, 640] uint8 mean 113.09 | ok |
| `cctv/event_tamper.jpg` | `log_scale=False` | 27.2 | [362, 640] uint8 mean 0.0 | ok |
| `cctv/event_tamper.jpg` | `normalize=False` | 27.4 | [362, 640] uint8 mean 7.27 | ok |
| `cctv/flattest.jpg` | `defaults` | 24.3 | [362, 640] uint8 mean 116.21 | ok |
| `cctv/flattest.jpg` | `log_scale=False` | 20.7 | [362, 640] uint8 mean 0.01 | ok |
| `cctv/flattest.jpg` | `normalize=False` | 22.8 | [362, 640] uint8 mean 7.36 | ok |
| `cctv/most_blown.jpg` | `defaults` | 25.5 | [362, 640] uint8 mean 117.7 | ok |
| `cctv/most_blown.jpg` | `log_scale=False` | 21.6 | [362, 640] uint8 mean 0.0 | ok |
| `cctv/most_blown.jpg` | `normalize=False` | 21.7 | [362, 640] uint8 mean 7.51 | ok |
| `cctv/sharpest.jpg` | `defaults` | 23.5 | [362, 640] uint8 mean 129.77 | ok |
| `cctv/sharpest.jpg` | `log_scale=False` | 21.0 | [362, 640] uint8 mean 0.01 | ok |
| `cctv/sharpest.jpg` | `normalize=False` | 21.5 | [362, 640] uint8 mean 8.31 | ok |
| `cctv/softest.jpg` | `defaults` | 24.2 | [362, 640] uint8 mean 112.42 | ok |
| `cctv/softest.jpg` | `log_scale=False` | 22.1 | [362, 640] uint8 mean 0.0 | ok |
| `cctv/softest.jpg` | `normalize=False` | 25.8 | [362, 640] uint8 mean 7.11 | ok |

## Artifacts

Outputs written to `validation/artifacts/fft_spectrum/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
