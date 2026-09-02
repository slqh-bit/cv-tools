# auto_levels - validation result

**Automatic levels stretch**  
`cv_tools.filters.levels` | family: Adjust | 2026-09-01T16:34:47

## Verdict

**PASS** - 18 runs, no invariant broken, 3 specific checks passed.

## What this filter specifically promises

- PASS - auto_levels widens the tonal span of a compressed frame: 1-99 percentile span 79 -> 227
- PASS - auto_contrast widens the tonal span of a compressed frame: 1-99 percentile span 79 -> 227
- PASS - a second auto_levels barely changes the first: mean change on the second pass 0.00/255

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `per_channel=True` on `cctv/brightest.jpg`: output identical to input
- `per_channel=True` on `cctv/darkest.jpg`: output identical to input
- `per_channel=True` on `cctv/event_fall.jpg`: output identical to input
- `per_channel=True` on `cctv/event_optflow.jpg`: output identical to input
- `per_channel=True` on `cctv/event_tamper.jpg`: output identical to input
- `per_channel=True` on `cctv/flattest.jpg`: output identical to input
- `per_channel=True` on `cctv/most_blown.jpg`: output identical to input
- `per_channel=True` on `cctv/sharpest.jpg`: output identical to input
- `per_channel=True` on `cctv/softest.jpg`: output identical to input

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 1.6 | [362, 640, 3] uint8 mean 162.56 | ok |
| `cctv/brightest.jpg` | `per_channel=True` | 3.6 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/darkest.jpg` | `defaults` | 1.3 | [362, 640, 3] uint8 mean 110.95 | ok |
| `cctv/darkest.jpg` | `per_channel=True` | 4.9 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/event_fall.jpg` | `defaults` | 1.5 | [362, 640, 3] uint8 mean 125.49 | ok |
| `cctv/event_fall.jpg` | `per_channel=True` | 3.9 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_optflow.jpg` | `defaults` | 1.3 | [362, 640, 3] uint8 mean 124.4 | ok |
| `cctv/event_optflow.jpg` | `per_channel=True` | 4.0 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_tamper.jpg` | `defaults` | 1.4 | [362, 640, 3] uint8 mean 160.61 | ok |
| `cctv/event_tamper.jpg` | `per_channel=True` | 4.4 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/flattest.jpg` | `defaults` | 1.2 | [362, 640, 3] uint8 mean 121.45 | ok |
| `cctv/flattest.jpg` | `per_channel=True` | 4.9 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/most_blown.jpg` | `defaults` | 1.4 | [362, 640, 3] uint8 mean 138.09 | ok |
| `cctv/most_blown.jpg` | `per_channel=True` | 5.1 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/sharpest.jpg` | `defaults` | 1.4 | [362, 640, 3] uint8 mean 131.76 | ok |
| `cctv/sharpest.jpg` | `per_channel=True` | 3.9 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/softest.jpg` | `defaults` | 1.4 | [362, 640, 3] uint8 mean 125.39 | ok |
| `cctv/softest.jpg` | `per_channel=True` | 4.5 | [362, 640, 3] uint8 mean 125.38 | output identical to input |

## Artifacts

Outputs written to `validation/artifacts/auto_levels/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
