# auto_perspective - validation result

**Detect and rectify a rectangular surface**  
`cv_tools.filters.perspective_correction` | family: Correct | 2026-09-01T16:35:51

## Verdict

**PASS** - 10 runs, no invariant broken.

At default parameters this filter is an identity: returns the input when it finds no quadrilateral. An unchanged image there is correct, not a fault.

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
- `` on `reference/perspective_sudoku.png`: output identical to input

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 1.6 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/darkest.jpg` | `defaults` | 2.1 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/event_fall.jpg` | `defaults` | 2.4 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_optflow.jpg` | `defaults` | 2.0 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_tamper.jpg` | `defaults` | 1.6 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/flattest.jpg` | `defaults` | 1.8 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/most_blown.jpg` | `defaults` | 1.9 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/sharpest.jpg` | `defaults` | 2.2 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/softest.jpg` | `defaults` | 1.8 | [362, 640, 3] uint8 mean 125.38 | output identical to input |
| `reference/perspective_sudoku.png` | `defaults` | 2.7 | [563, 558, 3] uint8 mean 101.19 | output identical to input |

## Artifacts

Outputs written to `validation/artifacts/auto_perspective/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
- `reference_perspective_sudoku.png`
