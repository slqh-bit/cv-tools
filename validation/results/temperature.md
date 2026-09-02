# temperature - validation result

**Manual colour temperature and tint**  
`cv_tools.filters.white_balance` | family: Adjust | 2026-09-01T16:34:51

## Verdict

**PASS** - 45 runs, no invariant broken, 3 specific checks passed.

At default parameters this filter is an identity: temperature 0 and tint 0 change nothing. An unchanged image there is correct, not a fault.

## What this filter specifically promises

- PASS - warming raises red and lowers blue: R 125.9->161.8, B 123.6->87.9
- PASS - cooling does the opposite: R 125.9->90.2, B 123.6->159.4
- PASS - temperature 0 leaves the frame alone: no shift requested

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `` on `cctv/brightest.jpg`: output identical to input
- `` on `cctv/darkest.jpg`: output identical to input
- `` on `cctv/event_fall.jpg`: output identical to input
- `` on `cctv/event_optflow.jpg`: output identical to input
- `` on `cctv/event_tamper.jpg`: output identical to input
- `` on `cctv/flattest.jpg`: output identical to input
- `` on `cctv/most_blown.jpg`: output identical to input
- `` on `cctv/sharpest.jpg`: output identical to input
- `` on `cctv/softest.jpg`: output identical to input

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 2.8 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/brightest.jpg` | `temperature=-100.0` | 2.6 | [362, 640, 3] uint8 mean 159.08 | ok |
| `cctv/brightest.jpg` | `temperature=100.0` | 2.4 | [362, 640, 3] uint8 mean 159.53 | ok |
| `cctv/brightest.jpg` | `tint=-100.0` | 2.6 | [362, 640, 3] uint8 mean 161.14 | ok |
| `cctv/brightest.jpg` | `tint=100.0` | 2.7 | [362, 640, 3] uint8 mean 162.67 | ok |
| `cctv/darkest.jpg` | `defaults` | 2.5 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/darkest.jpg` | `temperature=-100.0` | 2.6 | [362, 640, 3] uint8 mean 110.53 | ok |
| `cctv/darkest.jpg` | `temperature=100.0` | 2.6 | [362, 640, 3] uint8 mean 110.76 | ok |
| `cctv/darkest.jpg` | `tint=-100.0` | 2.4 | [362, 640, 3] uint8 mean 110.27 | ok |
| `cctv/darkest.jpg` | `tint=100.0` | 2.5 | [362, 640, 3] uint8 mean 110.61 | ok |
| `cctv/event_fall.jpg` | `defaults` | 2.4 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_fall.jpg` | `temperature=-100.0` | 2.7 | [362, 640, 3] uint8 mean 125.45 | ok |
| `cctv/event_fall.jpg` | `temperature=100.0` | 2.5 | [362, 640, 3] uint8 mean 125.88 | ok |
| `cctv/event_fall.jpg` | `tint=-100.0` | 2.5 | [362, 640, 3] uint8 mean 125.16 | ok |
| `cctv/event_fall.jpg` | `tint=100.0` | 2.4 | [362, 640, 3] uint8 mean 125.53 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 2.5 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_optflow.jpg` | `temperature=-100.0` | 2.7 | [362, 640, 3] uint8 mean 125.31 | ok |
| `cctv/event_optflow.jpg` | `temperature=100.0` | 2.9 | [362, 640, 3] uint8 mean 125.53 | ok |
| `cctv/event_optflow.jpg` | `tint=-100.0` | 3.1 | [362, 640, 3] uint8 mean 125.08 | ok |
| `cctv/event_optflow.jpg` | `tint=100.0` | 3.6 | [362, 640, 3] uint8 mean 125.25 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 3.4 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/event_tamper.jpg` | `temperature=-100.0` | 2.6 | [362, 640, 3] uint8 mean 156.54 | ok |
| `cctv/event_tamper.jpg` | `temperature=100.0` | 2.5 | [362, 640, 3] uint8 mean 157.29 | ok |
| `cctv/event_tamper.jpg` | `tint=-100.0` | 2.4 | [362, 640, 3] uint8 mean 158.71 | ok |
| `cctv/event_tamper.jpg` | `tint=100.0` | 3.0 | [362, 640, 3] uint8 mean 159.94 | ok |
| `cctv/flattest.jpg` | `defaults` | 3.2 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/flattest.jpg` | `temperature=-100.0` | 2.9 | [362, 640, 3] uint8 mean 121.51 | ok |
| `cctv/flattest.jpg` | `temperature=100.0` | 2.5 | [362, 640, 3] uint8 mean 121.71 | ok |
| `cctv/flattest.jpg` | `tint=-100.0` | 2.9 | [362, 640, 3] uint8 mean 121.18 | ok |
| `cctv/flattest.jpg` | `tint=100.0` | 2.5 | [362, 640, 3] uint8 mean 121.36 | ok |
| `cctv/most_blown.jpg` | `defaults` | 2.7 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/most_blown.jpg` | `temperature=-100.0` | 2.6 | [362, 640, 3] uint8 mean 135.91 | ok |
| `cctv/most_blown.jpg` | `temperature=100.0` | 3.8 | [362, 640, 3] uint8 mean 136.26 | ok |
| `cctv/most_blown.jpg` | `tint=-100.0` | 2.5 | [362, 640, 3] uint8 mean 136.6 | ok |
| `cctv/most_blown.jpg` | `tint=100.0` | 2.6 | [362, 640, 3] uint8 mean 136.89 | ok |
| `cctv/sharpest.jpg` | `defaults` | 2.4 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/sharpest.jpg` | `temperature=-100.0` | 3.0 | [362, 640, 3] uint8 mean 130.86 | ok |
| `cctv/sharpest.jpg` | `temperature=100.0` | 2.7 | [362, 640, 3] uint8 mean 130.88 | ok |
| `cctv/sharpest.jpg` | `tint=-100.0` | 2.6 | [362, 640, 3] uint8 mean 130.77 | ok |
| `cctv/sharpest.jpg` | `tint=100.0` | 3.7 | [362, 640, 3] uint8 mean 131.28 | ok |
| `cctv/softest.jpg` | `defaults` | 2.5 | [362, 640, 3] uint8 mean 125.38 | output identical to input |
| `cctv/softest.jpg` | `temperature=-100.0` | 4.4 | [362, 640, 3] uint8 mean 125.34 | ok |
| `cctv/softest.jpg` | `temperature=100.0` | 2.9 | [362, 640, 3] uint8 mean 125.73 | ok |
| `cctv/softest.jpg` | `tint=-100.0` | 3.0 | [362, 640, 3] uint8 mean 125.37 | ok |
| `cctv/softest.jpg` | `tint=100.0` | 3.2 | [362, 640, 3] uint8 mean 125.54 | ok |

## Artifacts

Outputs written to `validation/artifacts/temperature/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
