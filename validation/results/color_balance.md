# color_balance - validation result

**Per-tonal-range RGB shifts**  
`src.filters.color_balance` | family: Adjust | 2026-08-21T12:44:41

## Verdict

**PASS** - 18 runs, no invariant broken.

At default parameters this filter is an identity: no shift requested on any tonal range. An unchanged image there is correct, not a fault.

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `` on `cctv/brightest.jpg`: output identical to input
- `preserve_luminosity=False` on `cctv/brightest.jpg`: output identical to input
- `` on `cctv/darkest.jpg`: output identical to input
- `preserve_luminosity=False` on `cctv/darkest.jpg`: output identical to input
- `` on `cctv/event_fall.jpg`: output identical to input
- `preserve_luminosity=False` on `cctv/event_fall.jpg`: output identical to input
- `` on `cctv/event_optflow.jpg`: output identical to input
- `preserve_luminosity=False` on `cctv/event_optflow.jpg`: output identical to input
- `` on `cctv/event_tamper.jpg`: output identical to input
- `preserve_luminosity=False` on `cctv/event_tamper.jpg`: output identical to input
- `` on `cctv/flattest.jpg`: output identical to input
- `preserve_luminosity=False` on `cctv/flattest.jpg`: output identical to input

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 11.8 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/brightest.jpg` | `preserve_luminosity=False` | 7.3 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/darkest.jpg` | `defaults` | 11.7 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/darkest.jpg` | `preserve_luminosity=False` | 9.2 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/event_fall.jpg` | `defaults` | 14.9 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_fall.jpg` | `preserve_luminosity=False` | 9.0 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_optflow.jpg` | `defaults` | 13.2 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_optflow.jpg` | `preserve_luminosity=False` | 7.0 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_tamper.jpg` | `defaults` | 13.9 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/event_tamper.jpg` | `preserve_luminosity=False` | 7.3 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/flattest.jpg` | `defaults` | 11.6 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/flattest.jpg` | `preserve_luminosity=False` | 7.2 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/most_blown.jpg` | `defaults` | 12.7 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/most_blown.jpg` | `preserve_luminosity=False` | 7.3 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/sharpest.jpg` | `defaults` | 11.7 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/sharpest.jpg` | `preserve_luminosity=False` | 7.1 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/softest.jpg` | `defaults` | 13.0 | [362, 640, 3] uint8 mean 125.38 | output identical to input |
| `cctv/softest.jpg` | `preserve_luminosity=False` | 7.0 | [362, 640, 3] uint8 mean 125.38 | output identical to input |

## Artifacts

Outputs written to `validation/artifacts/color_balance/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
