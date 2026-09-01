# curves - validation result

**Tonal curve from control points or a preset**  
`src.filters.curves` | family: Adjust | 2026-09-01T16:34:50

## Verdict

**PASS** - 9 runs, no invariant broken, 8 specific checks passed.

9 run(s) refused bad parameters with a clear message, which is the wanted behaviour.

## What this filter specifically promises

- PASS - a straight line is an identity: the 0,0 - 255,255 curve changes nothing
- PASS - lift_shadows raises the shadows: mean of pixels under 64: 43.3 -> 75.7
- PASS - a monotonic preset stays monotonic: no tone reversal across the 0-255 ramp
- PASS - curves does not move content: the marker centred at (163.5, 163.5) reads centred at (163.5, 163.5)
- PASS - curves keeps the red block red: channel 0 dominates, expected 0
- PASS - curves keeps the green block green: channel 1 dominates, expected 1
- PASS - curves keeps the blue block blue: channel 2 dominates, expected 2
- PASS - curves reaches both halves of the frame: mean change 33.89 left against 33.83 right

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `` on `cctv/brightest.jpg`: refused: Provide either points or a preset
- `` on `cctv/darkest.jpg`: refused: Provide either points or a preset
- `` on `cctv/event_fall.jpg`: refused: Provide either points or a preset
- `` on `cctv/event_optflow.jpg`: refused: Provide either points or a preset
- `` on `cctv/event_tamper.jpg`: refused: Provide either points or a preset
- `` on `cctv/flattest.jpg`: refused: Provide either points or a preset
- `` on `cctv/most_blown.jpg`: refused: Provide either points or a preset
- `` on `cctv/sharpest.jpg`: refused: Provide either points or a preset
- `` on `cctv/softest.jpg`: refused: Provide either points or a preset

## Refused parameters

Rejected on purpose, with the message the user would see.

- `` -> ValueError: Provide either points or a preset

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 0.0 | - | refused: ValueError: Provide either points or a preset |
| `cctv/darkest.jpg` | `defaults` | 0.0 | - | refused: ValueError: Provide either points or a preset |
| `cctv/event_fall.jpg` | `defaults` | 0.0 | - | refused: ValueError: Provide either points or a preset |
| `cctv/event_optflow.jpg` | `defaults` | 0.0 | - | refused: ValueError: Provide either points or a preset |
| `cctv/event_tamper.jpg` | `defaults` | 0.0 | - | refused: ValueError: Provide either points or a preset |
| `cctv/flattest.jpg` | `defaults` | 0.0 | - | refused: ValueError: Provide either points or a preset |
| `cctv/most_blown.jpg` | `defaults` | 0.0 | - | refused: ValueError: Provide either points or a preset |
| `cctv/sharpest.jpg` | `defaults` | 0.0 | - | refused: ValueError: Provide either points or a preset |
| `cctv/softest.jpg` | `defaults` | 0.0 | - | refused: ValueError: Provide either points or a preset |
