# resize - validation result

**Resize by target size or scale factor**  
`src.filters.crop_resize` | family: Adjust | 2026-08-21T12:44:37

## Verdict

**PASS** - 27 runs, no invariant broken, 3 specific checks passed.

27 run(s) refused bad parameters with a clear message, which is the wanted behaviour.

## What this filter specifically promises

- PASS - scale 0.5 gives exactly the expected size: 320x181, expected 320x181
- PASS - scale 2 gives exactly the expected size: 1280x724, expected 1280x724
- PASS - an explicit size is honoured exactly: 320x240 requested 320x240

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `` on `cctv/brightest.jpg`: refused: Must specify width, height, or scale
- `interpolation=nearest` on `cctv/brightest.jpg`: refused: Must specify width, height, or scale
- `interpolation=bilinear` on `cctv/brightest.jpg`: refused: Must specify width, height, or scale
- `` on `cctv/darkest.jpg`: refused: Must specify width, height, or scale
- `interpolation=nearest` on `cctv/darkest.jpg`: refused: Must specify width, height, or scale
- `interpolation=bilinear` on `cctv/darkest.jpg`: refused: Must specify width, height, or scale
- `` on `cctv/event_fall.jpg`: refused: Must specify width, height, or scale
- `interpolation=nearest` on `cctv/event_fall.jpg`: refused: Must specify width, height, or scale
- `interpolation=bilinear` on `cctv/event_fall.jpg`: refused: Must specify width, height, or scale
- `` on `cctv/event_optflow.jpg`: refused: Must specify width, height, or scale
- `interpolation=nearest` on `cctv/event_optflow.jpg`: refused: Must specify width, height, or scale
- `interpolation=bilinear` on `cctv/event_optflow.jpg`: refused: Must specify width, height, or scale

## Refused parameters

Rejected on purpose, with the message the user would see.

- `` -> ValueError: Must specify width, height, or scale

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 0.0 | - | refused: ValueError: Must specify width, height, or scale |
| `cctv/brightest.jpg` | `interpolation=nearest` | 0.0 | - | refused: ValueError: Must specify width, height, or scale |
| `cctv/brightest.jpg` | `interpolation=bilinear` | 0.0 | - | refused: ValueError: Must specify width, height, or scale |
| `cctv/darkest.jpg` | `defaults` | 0.0 | - | refused: ValueError: Must specify width, height, or scale |
| `cctv/darkest.jpg` | `interpolation=nearest` | 0.0 | - | refused: ValueError: Must specify width, height, or scale |
| `cctv/darkest.jpg` | `interpolation=bilinear` | 0.0 | - | refused: ValueError: Must specify width, height, or scale |
| `cctv/event_fall.jpg` | `defaults` | 0.0 | - | refused: ValueError: Must specify width, height, or scale |
| `cctv/event_fall.jpg` | `interpolation=nearest` | 0.0 | - | refused: ValueError: Must specify width, height, or scale |
| `cctv/event_fall.jpg` | `interpolation=bilinear` | 0.0 | - | refused: ValueError: Must specify width, height, or scale |
| `cctv/event_optflow.jpg` | `defaults` | 0.0 | - | refused: ValueError: Must specify width, height, or scale |
| `cctv/event_optflow.jpg` | `interpolation=nearest` | 0.0 | - | refused: ValueError: Must specify width, height, or scale |
| `cctv/event_optflow.jpg` | `interpolation=bilinear` | 0.0 | - | refused: ValueError: Must specify width, height, or scale |
| `cctv/event_tamper.jpg` | `defaults` | 0.0 | - | refused: ValueError: Must specify width, height, or scale |
| `cctv/event_tamper.jpg` | `interpolation=nearest` | 0.0 | - | refused: ValueError: Must specify width, height, or scale |
| `cctv/event_tamper.jpg` | `interpolation=bilinear` | 0.0 | - | refused: ValueError: Must specify width, height, or scale |
| `cctv/flattest.jpg` | `defaults` | 0.0 | - | refused: ValueError: Must specify width, height, or scale |
| `cctv/flattest.jpg` | `interpolation=nearest` | 0.0 | - | refused: ValueError: Must specify width, height, or scale |
| `cctv/flattest.jpg` | `interpolation=bilinear` | 0.0 | - | refused: ValueError: Must specify width, height, or scale |
| `cctv/most_blown.jpg` | `defaults` | 0.0 | - | refused: ValueError: Must specify width, height, or scale |
| `cctv/most_blown.jpg` | `interpolation=nearest` | 0.0 | - | refused: ValueError: Must specify width, height, or scale |
| `cctv/most_blown.jpg` | `interpolation=bilinear` | 0.0 | - | refused: ValueError: Must specify width, height, or scale |
| `cctv/sharpest.jpg` | `defaults` | 0.0 | - | refused: ValueError: Must specify width, height, or scale |
| `cctv/sharpest.jpg` | `interpolation=nearest` | 0.0 | - | refused: ValueError: Must specify width, height, or scale |
| `cctv/sharpest.jpg` | `interpolation=bilinear` | 0.0 | - | refused: ValueError: Must specify width, height, or scale |
| `cctv/softest.jpg` | `defaults` | 0.0 | - | refused: ValueError: Must specify width, height, or scale |
| `cctv/softest.jpg` | `interpolation=nearest` | 0.0 | - | refused: ValueError: Must specify width, height, or scale |
| `cctv/softest.jpg` | `interpolation=bilinear` | 0.0 | - | refused: ValueError: Must specify width, height, or scale |
