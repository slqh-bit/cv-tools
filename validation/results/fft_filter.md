# fft_filter - validation result

**Frequency domain low/high/bandpass filter**  
`cv_tools.filters.fft_analysis` | family: Forensic | 2026-10-10T14:17:45

## Verdict

**PASS** - 72 runs, no invariant broken, 3 specific checks passed.

9 run(s) refused bad parameters with a clear message, which is the wanted behaviour.

## What this filter specifically promises

- PASS - a lowpass removes high-frequency energy: Laplacian variance 4538 -> 10
- PASS - a highpass keeps the detail and drops the rest: mean 131.8 -> 131.2
- PASS - a wider lowpass keeps more detail: 2 -> 10 -> 84 at cutoff 10/30/60

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `filter_type=bandpass` on `cctv/brightest.jpg`: refused: cutoff_high (0.0) must exceed cutoff (30.0) for a bandpass
- `filter_type=bandpass` on `cctv/darkest.jpg`: refused: cutoff_high (0.0) must exceed cutoff (30.0) for a bandpass
- `filter_type=bandpass` on `cctv/event_fall.jpg`: refused: cutoff_high (0.0) must exceed cutoff (30.0) for a bandpass
- `filter_type=bandpass` on `cctv/event_optflow.jpg`: refused: cutoff_high (0.0) must exceed cutoff (30.0) for a bandpass
- `filter_type=bandpass` on `cctv/event_tamper.jpg`: refused: cutoff_high (0.0) must exceed cutoff (30.0) for a bandpass
- `filter_type=bandpass` on `cctv/flattest.jpg`: refused: cutoff_high (0.0) must exceed cutoff (30.0) for a bandpass
- `filter_type=bandpass` on `cctv/most_blown.jpg`: refused: cutoff_high (0.0) must exceed cutoff (30.0) for a bandpass
- `filter_type=bandpass` on `cctv/sharpest.jpg`: refused: cutoff_high (0.0) must exceed cutoff (30.0) for a bandpass
- `filter_type=bandpass` on `cctv/softest.jpg`: refused: cutoff_high (0.0) must exceed cutoff (30.0) for a bandpass

## Refused parameters

Rejected on purpose, with the message the user would see.

- `filter_type=bandpass` -> ValueError: cutoff_high (0.0) must exceed cutoff (30.0) for a bandpass

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 44.4 | [362, 640] uint8 mean 164.07 | ok |
| `cctv/brightest.jpg` | `filter_type=highpass` | 45.3 | [362, 640] uint8 mean 154.03 | ok |
| `cctv/brightest.jpg` | `filter_type=bandpass` | 0.0 | - | refused: ValueError: cutoff_high (0.0) must exceed cutoff (30.0) for a bandpass |
| `cctv/brightest.jpg` | `cutoff=1.0` | 48.9 | [362, 640] uint8 mean 164.07 | ok |
| `cctv/brightest.jpg` | `cutoff=200.0` | 41.6 | [362, 640] uint8 mean 164.07 | ok |
| `cctv/brightest.jpg` | `cutoff_high=1.0` | 41.1 | [362, 640] uint8 mean 164.07 | ok |
| `cctv/brightest.jpg` | `cutoff_high=200.0` | 40.3 | [362, 640] uint8 mean 164.07 | ok |
| `cctv/brightest.jpg` | `soft=False` | 35.7 | [362, 640] uint8 mean 164.03 | ok |
| `cctv/darkest.jpg` | `defaults` | 40.5 | [362, 640] uint8 mean 110.89 | ok |
| `cctv/darkest.jpg` | `filter_type=highpass` | 42.1 | [362, 640] uint8 mean 140.85 | ok |
| `cctv/darkest.jpg` | `filter_type=bandpass` | 0.0 | - | refused: ValueError: cutoff_high (0.0) must exceed cutoff (30.0) for a bandpass |
| `cctv/darkest.jpg` | `cutoff=1.0` | 47.4 | [362, 640] uint8 mean 110.9 | ok |
| `cctv/darkest.jpg` | `cutoff=200.0` | 40.5 | [362, 640] uint8 mean 110.89 | ok |
| `cctv/darkest.jpg` | `cutoff_high=1.0` | 40.5 | [362, 640] uint8 mean 110.89 | ok |
| `cctv/darkest.jpg` | `cutoff_high=200.0` | 44.8 | [362, 640] uint8 mean 110.89 | ok |
| `cctv/darkest.jpg` | `soft=False` | 37.5 | [362, 640] uint8 mean 110.83 | ok |
| `cctv/event_fall.jpg` | `defaults` | 41.9 | [362, 640] uint8 mean 127.35 | ok |
| `cctv/event_fall.jpg` | `filter_type=highpass` | 42.6 | [362, 640] uint8 mean 135.08 | ok |
| `cctv/event_fall.jpg` | `filter_type=bandpass` | 0.0 | - | refused: ValueError: cutoff_high (0.0) must exceed cutoff (30.0) for a bandpass |
| `cctv/event_fall.jpg` | `cutoff=1.0` | 47.6 | [362, 640] uint8 mean 127.36 | ok |
| `cctv/event_fall.jpg` | `cutoff=200.0` | 40.5 | [362, 640] uint8 mean 127.35 | ok |
| `cctv/event_fall.jpg` | `cutoff_high=1.0` | 40.5 | [362, 640] uint8 mean 127.35 | ok |
| `cctv/event_fall.jpg` | `cutoff_high=200.0` | 40.3 | [362, 640] uint8 mean 127.35 | ok |
| `cctv/event_fall.jpg` | `soft=False` | 34.8 | [362, 640] uint8 mean 127.32 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 40.2 | [362, 640] uint8 mean 127.61 | ok |
| `cctv/event_optflow.jpg` | `filter_type=highpass` | 42.3 | [362, 640] uint8 mean 124.01 | ok |
| `cctv/event_optflow.jpg` | `filter_type=bandpass` | 0.0 | - | refused: ValueError: cutoff_high (0.0) must exceed cutoff (30.0) for a bandpass |
| `cctv/event_optflow.jpg` | `cutoff=1.0` | 48.2 | [362, 640] uint8 mean 127.61 | ok |
| `cctv/event_optflow.jpg` | `cutoff=200.0` | 41.5 | [362, 640] uint8 mean 127.61 | ok |
| `cctv/event_optflow.jpg` | `cutoff_high=1.0` | 40.3 | [362, 640] uint8 mean 127.61 | ok |
| `cctv/event_optflow.jpg` | `cutoff_high=200.0` | 40.9 | [362, 640] uint8 mean 127.61 | ok |
| `cctv/event_optflow.jpg` | `soft=False` | 35.3 | [362, 640] uint8 mean 127.59 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 41.7 | [362, 640] uint8 mean 160.83 | ok |
| `cctv/event_tamper.jpg` | `filter_type=highpass` | 55.3 | [362, 640] uint8 mean 155.69 | ok |
| `cctv/event_tamper.jpg` | `filter_type=bandpass` | 0.0 | - | refused: ValueError: cutoff_high (0.0) must exceed cutoff (30.0) for a bandpass |
| `cctv/event_tamper.jpg` | `cutoff=1.0` | 61.3 | [362, 640] uint8 mean 160.83 | ok |
| `cctv/event_tamper.jpg` | `cutoff=200.0` | 44.0 | [362, 640] uint8 mean 160.83 | ok |
| `cctv/event_tamper.jpg` | `cutoff_high=1.0` | 42.2 | [362, 640] uint8 mean 160.83 | ok |
| `cctv/event_tamper.jpg` | `cutoff_high=200.0` | 40.3 | [362, 640] uint8 mean 160.83 | ok |
| `cctv/event_tamper.jpg` | `soft=False` | 35.6 | [362, 640] uint8 mean 160.8 | ok |
| `cctv/flattest.jpg` | `defaults` | 41.1 | [362, 640] uint8 mean 123.3 | ok |
| `cctv/flattest.jpg` | `filter_type=highpass` | 42.7 | [362, 640] uint8 mean 120.11 | ok |
| `cctv/flattest.jpg` | `filter_type=bandpass` | 0.0 | - | refused: ValueError: cutoff_high (0.0) must exceed cutoff (30.0) for a bandpass |
| `cctv/flattest.jpg` | `cutoff=1.0` | 50.6 | [362, 640] uint8 mean 123.31 | ok |
| `cctv/flattest.jpg` | `cutoff=200.0` | 46.0 | [362, 640] uint8 mean 123.3 | ok |
| `cctv/flattest.jpg` | `cutoff_high=1.0` | 42.8 | [362, 640] uint8 mean 123.3 | ok |
| `cctv/flattest.jpg` | `cutoff_high=200.0` | 41.7 | [362, 640] uint8 mean 123.3 | ok |
| `cctv/flattest.jpg` | `soft=False` | 36.6 | [362, 640] uint8 mean 123.28 | ok |
| `cctv/most_blown.jpg` | `defaults` | 42.1 | [362, 640] uint8 mean 137.95 | ok |
| `cctv/most_blown.jpg` | `filter_type=highpass` | 43.4 | [362, 640] uint8 mean 144.93 | ok |
| `cctv/most_blown.jpg` | `filter_type=bandpass` | 0.0 | - | refused: ValueError: cutoff_high (0.0) must exceed cutoff (30.0) for a bandpass |
| `cctv/most_blown.jpg` | `cutoff=1.0` | 47.8 | [362, 640] uint8 mean 137.95 | ok |
| `cctv/most_blown.jpg` | `cutoff=200.0` | 41.2 | [362, 640] uint8 mean 137.95 | ok |
| `cctv/most_blown.jpg` | `cutoff_high=1.0` | 48.3 | [362, 640] uint8 mean 137.95 | ok |
| `cctv/most_blown.jpg` | `cutoff_high=200.0` | 43.1 | [362, 640] uint8 mean 137.95 | ok |
| `cctv/most_blown.jpg` | `soft=False` | 36.6 | [362, 640] uint8 mean 137.83 | ok |
| `cctv/sharpest.jpg` | `defaults` | 41.8 | [362, 640] uint8 mean 131.52 | ok |
| `cctv/sharpest.jpg` | `filter_type=highpass` | 42.6 | [362, 640] uint8 mean 131.18 | ok |
| `cctv/sharpest.jpg` | `filter_type=bandpass` | 0.0 | - | refused: ValueError: cutoff_high (0.0) must exceed cutoff (30.0) for a bandpass |
| `cctv/sharpest.jpg` | `cutoff=1.0` | 49.1 | [362, 640] uint8 mean 131.52 | ok |
| `cctv/sharpest.jpg` | `cutoff=200.0` | 44.5 | [362, 640] uint8 mean 131.52 | ok |
| `cctv/sharpest.jpg` | `cutoff_high=1.0` | 44.0 | [362, 640] uint8 mean 131.52 | ok |
| `cctv/sharpest.jpg` | `cutoff_high=200.0` | 43.3 | [362, 640] uint8 mean 131.52 | ok |
| `cctv/sharpest.jpg` | `soft=False` | 36.4 | [362, 640] uint8 mean 131.41 | ok |
| `cctv/softest.jpg` | `defaults` | 42.1 | [362, 640] uint8 mean 125.56 | ok |
| `cctv/softest.jpg` | `filter_type=highpass` | 42.4 | [362, 640] uint8 mean 135.9 | ok |
| `cctv/softest.jpg` | `filter_type=bandpass` | 0.0 | - | refused: ValueError: cutoff_high (0.0) must exceed cutoff (30.0) for a bandpass |
| `cctv/softest.jpg` | `cutoff=1.0` | 48.5 | [362, 640] uint8 mean 125.56 | ok |
| `cctv/softest.jpg` | `cutoff=200.0` | 40.7 | [362, 640] uint8 mean 125.56 | ok |
| `cctv/softest.jpg` | `cutoff_high=1.0` | 41.0 | [362, 640] uint8 mean 125.56 | ok |
| `cctv/softest.jpg` | `cutoff_high=200.0` | 40.6 | [362, 640] uint8 mean 125.56 | ok |
| `cctv/softest.jpg` | `soft=False` | 35.7 | [362, 640] uint8 mean 125.56 | ok |

## Artifacts

Outputs written to `validation/artifacts/fft_filter/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
