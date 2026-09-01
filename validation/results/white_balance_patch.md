# white_balance_patch - validation result

**White balance from a known neutral region**  
`src.filters.white_balance` | family: Adjust | 2026-09-01T16:34:51

## Verdict

**PASS** - 9 runs, no invariant broken.

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `x=120, y=80, width=200, height=140` | 4.0 | [362, 640, 3] uint8 mean 162.7 | ok |
| `cctv/darkest.jpg` | `x=120, y=80, width=200, height=140` | 3.8 | [362, 640, 3] uint8 mean 111.45 | ok |
| `cctv/event_fall.jpg` | `x=120, y=80, width=200, height=140` | 3.7 | [362, 640, 3] uint8 mean 134.84 | ok |
| `cctv/event_optflow.jpg` | `x=120, y=80, width=200, height=140` | 3.7 | [362, 640, 3] uint8 mean 135.96 | ok |
| `cctv/event_tamper.jpg` | `x=120, y=80, width=200, height=140` | 3.7 | [362, 640, 3] uint8 mean 159.45 | ok |
| `cctv/flattest.jpg` | `x=120, y=80, width=200, height=140` | 3.7 | [362, 640, 3] uint8 mean 131.36 | ok |
| `cctv/most_blown.jpg` | `x=120, y=80, width=200, height=140` | 3.6 | [362, 640, 3] uint8 mean 138.24 | ok |
| `cctv/sharpest.jpg` | `x=120, y=80, width=200, height=140` | 3.9 | [362, 640, 3] uint8 mean 132.09 | ok |
| `cctv/softest.jpg` | `x=120, y=80, width=200, height=140` | 3.8 | [362, 640, 3] uint8 mean 124.27 | ok |

## Artifacts

Outputs written to `validation/artifacts/white_balance_patch/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
