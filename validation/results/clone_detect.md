# clone_detect - validation result

**Highlight copy-move duplicated regions**  
`src.filters.clone_detection` | family: Forensic | 2026-09-01T16:36:19

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
| `cctv/brightest.jpg` | `defaults` | 593.9 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/brightest.jpg` | `alpha=0.0` | 622.7 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/brightest.jpg` | `alpha=1.0` | 620.3 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/darkest.jpg` | `defaults` | 580.6 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/darkest.jpg` | `alpha=0.0` | 601.1 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/darkest.jpg` | `alpha=1.0` | 591.9 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/event_fall.jpg` | `defaults` | 822.5 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_fall.jpg` | `alpha=0.0` | 810.9 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_fall.jpg` | `alpha=1.0` | 827.7 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_optflow.jpg` | `defaults` | 710.0 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_optflow.jpg` | `alpha=0.0` | 631.5 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_optflow.jpg` | `alpha=1.0` | 820.0 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_tamper.jpg` | `defaults` | 873.1 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/event_tamper.jpg` | `alpha=0.0` | 803.9 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/event_tamper.jpg` | `alpha=1.0` | 775.1 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/flattest.jpg` | `defaults` | 631.5 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/flattest.jpg` | `alpha=0.0` | 602.2 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/flattest.jpg` | `alpha=1.0` | 628.3 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/most_blown.jpg` | `defaults` | 664.7 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/most_blown.jpg` | `alpha=0.0` | 678.0 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/most_blown.jpg` | `alpha=1.0` | 657.1 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/sharpest.jpg` | `defaults` | 795.5 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/sharpest.jpg` | `alpha=0.0` | 806.4 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/sharpest.jpg` | `alpha=1.0` | 823.8 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/softest.jpg` | `defaults` | 653.8 | [362, 640, 3] uint8 mean 125.38 | output identical to input |
| `cctv/softest.jpg` | `alpha=0.0` | 617.6 | [362, 640, 3] uint8 mean 125.38 | output identical to input |
| `cctv/softest.jpg` | `alpha=1.0` | 574.4 | [362, 640, 3] uint8 mean 125.38 | output identical to input |
| `ground_truth/copy_move.png` | `defaults` | 668.5 | [362, 640, 3] uint8 mean 131.93 | ok |
| `ground_truth/copy_move.png` | `alpha=0.0` | 652.6 | [362, 640, 3] uint8 mean 135.37 | output identical to input |
| `ground_truth/copy_move.png` | `alpha=1.0` | 643.5 | [362, 640, 3] uint8 mean 126.79 | ok |
| `ground_truth/clean_control.jpg` | `defaults` | 636.2 | [362, 640, 3] uint8 mean 131.75 | output identical to input |
| `ground_truth/clean_control.jpg` | `alpha=0.0` | 620.3 | [362, 640, 3] uint8 mean 131.75 | output identical to input |
| `ground_truth/clean_control.jpg` | `alpha=1.0` | 671.8 | [362, 640, 3] uint8 mean 131.75 | output identical to input |

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
