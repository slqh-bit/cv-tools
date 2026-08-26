# invert_channel - validation result

**Invert one colour channel**  
`src.filters.invert` | family: Adjust | 2026-08-21T12:44:42

## Verdict

**PASS** - 9 runs, no invariant broken, 4 specific checks passed.

9 run(s) refused bad parameters with a clear message, which is the wanted behaviour.

## What this filter specifically promises

- PASS - inverting r inverts only r: channel 0 complemented, the other two untouched
- PASS - inverting g inverts only g: channel 1 complemented, the other two untouched
- PASS - inverting b inverts only b: channel 2 complemented, the other two untouched
- PASS - luminance inversion flips brightness and roughly keeps hue: mean brightness -21.4, mean hue shift 6.0 degrees of 180

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `channel=H` on `cctv/brightest.jpg`: refused: Invalid channel: H
- `channel=H` on `cctv/darkest.jpg`: refused: Invalid channel: H
- `channel=H` on `cctv/event_fall.jpg`: refused: Invalid channel: H
- `channel=H` on `cctv/event_optflow.jpg`: refused: Invalid channel: H
- `channel=H` on `cctv/event_tamper.jpg`: refused: Invalid channel: H
- `channel=H` on `cctv/flattest.jpg`: refused: Invalid channel: H
- `channel=H` on `cctv/most_blown.jpg`: refused: Invalid channel: H
- `channel=H` on `cctv/sharpest.jpg`: refused: Invalid channel: H
- `channel=H` on `cctv/softest.jpg`: refused: Invalid channel: H

## Refused parameters

Rejected on purpose, with the message the user would see.

- `channel=H` -> ValueError: Invalid channel: H

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `channel=H` | 0.0 | - | refused: ValueError: Invalid channel: H |
| `cctv/darkest.jpg` | `channel=H` | 0.0 | - | refused: ValueError: Invalid channel: H |
| `cctv/event_fall.jpg` | `channel=H` | 0.0 | - | refused: ValueError: Invalid channel: H |
| `cctv/event_optflow.jpg` | `channel=H` | 0.0 | - | refused: ValueError: Invalid channel: H |
| `cctv/event_tamper.jpg` | `channel=H` | 0.0 | - | refused: ValueError: Invalid channel: H |
| `cctv/flattest.jpg` | `channel=H` | 0.0 | - | refused: ValueError: Invalid channel: H |
| `cctv/most_blown.jpg` | `channel=H` | 0.0 | - | refused: ValueError: Invalid channel: H |
| `cctv/sharpest.jpg` | `channel=H` | 0.0 | - | refused: ValueError: Invalid channel: H |
| `cctv/softest.jpg` | `channel=H` | 0.0 | - | refused: ValueError: Invalid channel: H |
