# clone_detect - validation result

**Highlight copy-move duplicated regions**  
`src.filters.clone_detection` | family: Forensic | 2026-08-21T12:46:00

## Verdict

**PASS** - 33 runs, no invariant broken, 2 specific checks passed.

At default parameters this filter is an identity: returns the input when it finds no duplicated region. An unchanged image there is correct, not a fault.

## What this filter specifically promises

- PASS - finds the shift that was actually applied: expected dx=+260 dy=+140, top shifts: [(260, 140)]
- PASS - does not report a forgery on the untouched control: detected=False, 0 matching pairs

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `` on `cctv/brightest.jpg`: output identical to input
- `alpha=0.0` on `cctv/brightest.jpg`: output identical to input
- `alpha=1.0` on `cctv/brightest.jpg`: output identical to input
- `` on `cctv/darkest.jpg`: output identical to input
- `alpha=0.0` on `cctv/darkest.jpg`: output identical to input
- `alpha=1.0` on `cctv/darkest.jpg`: output identical to input
- `` on `cctv/event_fall.jpg`: output identical to input
- `alpha=0.0` on `cctv/event_fall.jpg`: output identical to input
- `alpha=1.0` on `cctv/event_fall.jpg`: output identical to input
- `` on `cctv/event_optflow.jpg`: output identical to input
- `alpha=0.0` on `cctv/event_optflow.jpg`: output identical to input
- `alpha=1.0` on `cctv/event_optflow.jpg`: output identical to input

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 524.9 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/brightest.jpg` | `alpha=0.0` | 523.6 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/brightest.jpg` | `alpha=1.0` | 525.6 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/darkest.jpg` | `defaults` | 462.2 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/darkest.jpg` | `alpha=0.0` | 463.5 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/darkest.jpg` | `alpha=1.0` | 461.2 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/event_fall.jpg` | `defaults` | 622.6 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_fall.jpg` | `alpha=0.0` | 618.7 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_fall.jpg` | `alpha=1.0` | 624.3 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_optflow.jpg` | `defaults` | 473.5 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_optflow.jpg` | `alpha=0.0` | 472.6 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_optflow.jpg` | `alpha=1.0` | 473.6 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_tamper.jpg` | `defaults` | 522.4 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/event_tamper.jpg` | `alpha=0.0` | 528.4 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/event_tamper.jpg` | `alpha=1.0` | 523.0 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/flattest.jpg` | `defaults` | 457.4 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/flattest.jpg` | `alpha=0.0` | 456.5 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/flattest.jpg` | `alpha=1.0` | 457.1 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/most_blown.jpg` | `defaults` | 474.5 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/most_blown.jpg` | `alpha=0.0` | 476.4 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/most_blown.jpg` | `alpha=1.0` | 500.4 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/sharpest.jpg` | `defaults` | 594.9 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/sharpest.jpg` | `alpha=0.0` | 594.4 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/sharpest.jpg` | `alpha=1.0` | 597.0 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/softest.jpg` | `defaults` | 463.5 | [362, 640, 3] uint8 mean 125.38 | output identical to input |
| `cctv/softest.jpg` | `alpha=0.0` | 465.3 | [362, 640, 3] uint8 mean 125.38 | output identical to input |
| `cctv/softest.jpg` | `alpha=1.0` | 463.0 | [362, 640, 3] uint8 mean 125.38 | output identical to input |
| `ground_truth/copy_move.png` | `defaults` | 609.3 | [362, 640, 3] uint8 mean 131.93 | ok |
| `ground_truth/copy_move.png` | `alpha=0.0` | 609.8 | [362, 640, 3] uint8 mean 135.37 | output identical to input |
| `ground_truth/copy_move.png` | `alpha=1.0` | 614.9 | [362, 640, 3] uint8 mean 126.79 | ok |
| `ground_truth/clean_control.jpg` | `defaults` | 594.1 | [362, 640, 3] uint8 mean 131.75 | output identical to input |
| `ground_truth/clean_control.jpg` | `alpha=0.0` | 593.8 | [362, 640, 3] uint8 mean 131.75 | output identical to input |
| `ground_truth/clean_control.jpg` | `alpha=1.0` | 591.0 | [362, 640, 3] uint8 mean 131.75 | output identical to input |

## Artifacts

Outputs written to `validation/artifacts/clone_detect/`:

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
- `ground_truth_copy_move.png`
