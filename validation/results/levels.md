# levels - validation result

**Black point / gamma / white point adjustment**  
`cv_tools.filters.levels` | family: Adjust | 2026-09-01T16:34:46

## Verdict

**PASS** - 99 runs, no invariant broken, 10 specific checks passed.

18 run(s) refused bad parameters with a clear message, which is the wanted behaviour.

At default parameters this filter is an identity: black 0, white 255, gamma 1 is the identity mapping. An unchanged image there is correct, not a fault.

## What this filter specifically promises

- PASS - defaults are an exact identity: black 0, white 255, gamma 1 changes nothing
- PASS - a stretch widens the dynamic range: std 47.3 -> 68.2
- PASS - every value at or below the black point maps to 0: ramp values 0-64 map to [0]
- PASS - every value at or above the white point maps to 255: ramp values 192-255 map to [255]
- PASS - gamma below 1 darkens and above 1 brightens: 66 < 121 < 172
- PASS - levels does not move content: the marker centred at (163.5, 163.5) reads centred at (163.5, 163.5)
- PASS - levels keeps the red block red: channel 0 dominates, expected 0
- PASS - levels keeps the green block green: channel 1 dominates, expected 1
- PASS - levels keeps the blue block blue: channel 2 dominates, expected 2
- PASS - levels reaches both halves of the frame: mean change 13.61 left against 13.59 right

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `` on `cctv/brightest.jpg`: output identical to input
- `black_point=0` on `cctv/brightest.jpg`: output identical to input
- `black_point=255` on `cctv/brightest.jpg`: refused: black_point must be less than white_point
- `white_point=0` on `cctv/brightest.jpg`: refused: black_point must be less than white_point
- `white_point=255` on `cctv/brightest.jpg`: output identical to input
- `output_black=0` on `cctv/brightest.jpg`: output identical to input
- `output_black=255` on `cctv/brightest.jpg`: flat output - every pixel is 255
- `output_white=0` on `cctv/brightest.jpg`: flat output - every pixel is 0
- `output_white=255` on `cctv/brightest.jpg`: output identical to input
- `` on `cctv/darkest.jpg`: output identical to input
- `black_point=0` on `cctv/darkest.jpg`: output identical to input
- `black_point=255` on `cctv/darkest.jpg`: refused: black_point must be less than white_point

## Refused parameters

Rejected on purpose, with the message the user would see.

- `black_point=255` -> ValueError: black_point must be less than white_point

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 5.6 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/brightest.jpg` | `black_point=0` | 5.7 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/brightest.jpg` | `black_point=255` | 0.0 | - | refused: ValueError: black_point must be less than white_point |
| `cctv/brightest.jpg` | `gamma=0.1` | 16.1 | [362, 640, 3] uint8 mean 44.96 | ok |
| `cctv/brightest.jpg` | `gamma=3.0` | 14.9 | [362, 640, 3] uint8 mean 214.8 | ok |
| `cctv/brightest.jpg` | `white_point=0` | 0.0 | - | refused: ValueError: black_point must be less than white_point |
| `cctv/brightest.jpg` | `white_point=255` | 6.8 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/brightest.jpg` | `output_black=0` | 5.6 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/brightest.jpg` | `output_black=255` | 5.6 | [362, 640, 3] uint8 mean 255.0 | flat output - every pixel is 255 |
| `cctv/brightest.jpg` | `output_white=0` | 6.0 | [362, 640, 3] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/brightest.jpg` | `output_white=255` | 6.4 | [362, 640, 3] uint8 mean 163.53 | output identical to input |
| `cctv/darkest.jpg` | `defaults` | 5.9 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/darkest.jpg` | `black_point=0` | 7.1 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/darkest.jpg` | `black_point=255` | 0.0 | - | refused: ValueError: black_point must be less than white_point |
| `cctv/darkest.jpg` | `gamma=0.1` | 14.2 | [362, 640, 3] uint8 mean 12.83 | ok |
| `cctv/darkest.jpg` | `gamma=3.0` | 15.2 | [362, 640, 3] uint8 mean 188.23 | ok |
| `cctv/darkest.jpg` | `white_point=0` | 0.0 | - | refused: ValueError: black_point must be less than white_point |
| `cctv/darkest.jpg` | `white_point=255` | 6.8 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/darkest.jpg` | `output_black=0` | 6.9 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/darkest.jpg` | `output_black=255` | 6.6 | [362, 640, 3] uint8 mean 255.0 | flat output - every pixel is 255 |
| `cctv/darkest.jpg` | `output_white=0` | 5.9 | [362, 640, 3] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/darkest.jpg` | `output_white=255` | 10.8 | [362, 640, 3] uint8 mean 110.93 | output identical to input |
| `cctv/event_fall.jpg` | `defaults` | 5.9 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_fall.jpg` | `black_point=0` | 5.8 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_fall.jpg` | `black_point=255` | 0.0 | - | refused: ValueError: black_point must be less than white_point |
| `cctv/event_fall.jpg` | `gamma=0.1` | 13.7 | [362, 640, 3] uint8 mean 14.93 | ok |
| `cctv/event_fall.jpg` | `gamma=3.0` | 13.9 | [362, 640, 3] uint8 mean 193.43 | ok |
| `cctv/event_fall.jpg` | `white_point=0` | 0.0 | - | refused: ValueError: black_point must be less than white_point |
| `cctv/event_fall.jpg` | `white_point=255` | 5.9 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_fall.jpg` | `output_black=0` | 5.5 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_fall.jpg` | `output_black=255` | 5.8 | [362, 640, 3] uint8 mean 255.0 | flat output - every pixel is 255 |
| `cctv/event_fall.jpg` | `output_white=0` | 6.8 | [362, 640, 3] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/event_fall.jpg` | `output_white=255` | 5.9 | [362, 640, 3] uint8 mean 125.51 | output identical to input |
| `cctv/event_optflow.jpg` | `defaults` | 6.0 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_optflow.jpg` | `black_point=0` | 5.9 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_optflow.jpg` | `black_point=255` | 0.0 | - | refused: ValueError: black_point must be less than white_point |
| `cctv/event_optflow.jpg` | `gamma=0.1` | 14.1 | [362, 640, 3] uint8 mean 8.98 | ok |
| `cctv/event_optflow.jpg` | `gamma=3.0` | 14.2 | [362, 640, 3] uint8 mean 196.69 | ok |
| `cctv/event_optflow.jpg` | `white_point=0` | 0.0 | - | refused: ValueError: black_point must be less than white_point |
| `cctv/event_optflow.jpg` | `white_point=255` | 8.4 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_optflow.jpg` | `output_black=0` | 5.5 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_optflow.jpg` | `output_black=255` | 5.7 | [362, 640, 3] uint8 mean 255.0 | flat output - every pixel is 255 |
| `cctv/event_optflow.jpg` | `output_white=0` | 6.8 | [362, 640, 3] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/event_optflow.jpg` | `output_white=255` | 5.5 | [362, 640, 3] uint8 mean 125.42 | output identical to input |
| `cctv/event_tamper.jpg` | `defaults` | 5.7 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/event_tamper.jpg` | `black_point=0` | 5.8 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/event_tamper.jpg` | `black_point=255` | 0.0 | - | refused: ValueError: black_point must be less than white_point |
| `cctv/event_tamper.jpg` | `gamma=0.1` | 16.4 | [362, 640, 3] uint8 mean 39.09 | ok |
| `cctv/event_tamper.jpg` | `gamma=3.0` | 16.1 | [362, 640, 3] uint8 mean 213.48 | ok |
| `cctv/event_tamper.jpg` | `white_point=0` | 0.0 | - | refused: ValueError: black_point must be less than white_point |
| `cctv/event_tamper.jpg` | `white_point=255` | 7.4 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/event_tamper.jpg` | `output_black=0` | 9.5 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/event_tamper.jpg` | `output_black=255` | 7.3 | [362, 640, 3] uint8 mean 255.0 | flat output - every pixel is 255 |
| `cctv/event_tamper.jpg` | `output_white=0` | 8.5 | [362, 640, 3] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/event_tamper.jpg` | `output_white=255` | 8.9 | [362, 640, 3] uint8 mean 160.62 | output identical to input |
| `cctv/flattest.jpg` | `defaults` | 9.3 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/flattest.jpg` | `black_point=0` | 7.6 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/flattest.jpg` | `black_point=255` | 0.0 | - | refused: ValueError: black_point must be less than white_point |
| `cctv/flattest.jpg` | `gamma=0.1` | 17.7 | [362, 640, 3] uint8 mean 7.84 | ok |
| `cctv/flattest.jpg` | `gamma=3.0` | 17.0 | [362, 640, 3] uint8 mean 194.71 | ok |
| `cctv/flattest.jpg` | `white_point=0` | 0.0 | - | refused: ValueError: black_point must be less than white_point |
| `cctv/flattest.jpg` | `white_point=255` | 7.0 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/flattest.jpg` | `output_black=0` | 6.6 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/flattest.jpg` | `output_black=255` | 6.4 | [362, 640, 3] uint8 mean 255.0 | flat output - every pixel is 255 |
| `cctv/flattest.jpg` | `output_white=0` | 9.5 | [362, 640, 3] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/flattest.jpg` | `output_white=255` | 6.5 | [362, 640, 3] uint8 mean 121.5 | output identical to input |
| `cctv/most_blown.jpg` | `defaults` | 6.5 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/most_blown.jpg` | `black_point=0` | 5.9 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/most_blown.jpg` | `black_point=255` | 0.0 | - | refused: ValueError: black_point must be less than white_point |
| `cctv/most_blown.jpg` | `gamma=0.1` | 17.4 | [362, 640, 3] uint8 mean 29.18 | ok |
| `cctv/most_blown.jpg` | `gamma=3.0` | 14.9 | [362, 640, 3] uint8 mean 202.74 | ok |
| `cctv/most_blown.jpg` | `white_point=0` | 0.0 | - | refused: ValueError: black_point must be less than white_point |
| `cctv/most_blown.jpg` | `white_point=255` | 7.4 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/most_blown.jpg` | `output_black=0` | 6.8 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/most_blown.jpg` | `output_black=255` | 5.6 | [362, 640, 3] uint8 mean 255.0 | flat output - every pixel is 255 |
| `cctv/most_blown.jpg` | `output_white=0` | 5.6 | [362, 640, 3] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/most_blown.jpg` | `output_white=255` | 6.4 | [362, 640, 3] uint8 mean 138.08 | output identical to input |
| `cctv/sharpest.jpg` | `defaults` | 6.6 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/sharpest.jpg` | `black_point=0` | 8.0 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/sharpest.jpg` | `black_point=255` | 0.0 | - | refused: ValueError: black_point must be less than white_point |
| `cctv/sharpest.jpg` | `gamma=0.1` | 13.6 | [362, 640, 3] uint8 mean 24.49 | ok |
| `cctv/sharpest.jpg` | `gamma=3.0` | 14.6 | [362, 640, 3] uint8 mean 196.94 | ok |
| `cctv/sharpest.jpg` | `white_point=0` | 0.0 | - | refused: ValueError: black_point must be less than white_point |
| `cctv/sharpest.jpg` | `white_point=255` | 6.0 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/sharpest.jpg` | `output_black=0` | 6.8 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/sharpest.jpg` | `output_black=255` | 6.6 | [362, 640, 3] uint8 mean 255.0 | flat output - every pixel is 255 |
| `cctv/sharpest.jpg` | `output_white=0` | 5.6 | [362, 640, 3] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/sharpest.jpg` | `output_white=255` | 10.8 | [362, 640, 3] uint8 mean 131.76 | output identical to input |
| `cctv/softest.jpg` | `defaults` | 5.6 | [362, 640, 3] uint8 mean 125.38 | output identical to input |
| `cctv/softest.jpg` | `black_point=0` | 6.1 | [362, 640, 3] uint8 mean 125.38 | output identical to input |
| `cctv/softest.jpg` | `black_point=255` | 0.0 | - | refused: ValueError: black_point must be less than white_point |
| `cctv/softest.jpg` | `gamma=0.1` | 13.5 | [362, 640, 3] uint8 mean 4.01 | ok |
| `cctv/softest.jpg` | `gamma=3.0` | 13.9 | [362, 640, 3] uint8 mean 196.76 | ok |
| `cctv/softest.jpg` | `white_point=0` | 0.0 | - | refused: ValueError: black_point must be less than white_point |
| `cctv/softest.jpg` | `white_point=255` | 6.9 | [362, 640, 3] uint8 mean 125.38 | output identical to input |
| `cctv/softest.jpg` | `output_black=0` | 5.8 | [362, 640, 3] uint8 mean 125.38 | output identical to input |
| `cctv/softest.jpg` | `output_black=255` | 5.9 | [362, 640, 3] uint8 mean 255.0 | flat output - every pixel is 255 |
| `cctv/softest.jpg` | `output_white=0` | 6.4 | [362, 640, 3] uint8 mean 0.0 | flat output - every pixel is 0 |
| `cctv/softest.jpg` | `output_white=255` | 6.4 | [362, 640, 3] uint8 mean 125.38 | output identical to input |

## Artifacts

Outputs written to `validation/artifacts/levels/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
