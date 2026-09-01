# component - validation result

**Extract one colour-space channel**  
`src.filters.component_separation` | family: Special | 2026-09-01T16:37:18

## Verdict

**PASS** - 54 runs, no invariant broken, 34 specific checks passed.

27 run(s) refused bad parameters with a clear message, which is the wanted behaviour.

## What this filter specifically promises

- PASS - rgb:R is a single plane, not the image: (362, 640), std 60.6
- PASS - rgb:G is a single plane, not the image: (362, 640), std 61.7
- PASS - rgb:B is a single plane, not the image: (362, 640), std 61.3
- PASS - rgb channels differ from one another: R and G differ
- PASS - hsv:H is a single plane, not the image: (362, 640), std 46.8
- PASS - hsv:S is a single plane, not the image: (362, 640), std 37.7
- PASS - hsv:V is a single plane, not the image: (362, 640), std 60.5
- PASS - hsv channels differ from one another: H and S differ
- PASS - hls:H is a single plane, not the image: (362, 640), std 46.8
- PASS - hls:L is a single plane, not the image: (362, 640), std 60.7
- PASS - hls:S is a single plane, not the image: (362, 640), std 55.0
- PASS - hls channels differ from one another: H and L differ
- PASS - lab:L is a single plane, not the image: (362, 640), std 61.6
- PASS - lab:a is a single plane, not the image: (362, 640), std 3.1
- PASS - lab:b is a single plane, not the image: (362, 640), std 4.8
- PASS - lab channels differ from one another: L and a differ
- PASS - luv:L is a single plane, not the image: (362, 640), std 61.6
- PASS - luv:u is a single plane, not the image: (362, 640), std 3.3
- PASS - luv:v is a single plane, not the image: (362, 640), std 6.1
- PASS - luv channels differ from one another: L and u differ
- PASS - ycrcb:Y is a single plane, not the image: (362, 640), std 61.2
- PASS - ycrcb:Cr is a single plane, not the image: (362, 640), std 4.1
- PASS - ycrcb:Cb is a single plane, not the image: (362, 640), std 4.6
- PASS - ycrcb channels differ from one another: Y and Cr differ
- PASS - yuv:Y is a single plane, not the image: (362, 640), std 61.2
- PASS - yuv:U is a single plane, not the image: (362, 640), std 3.9
- PASS - yuv:V is a single plane, not the image: (362, 640), std 5.1
- PASS - yuv channels differ from one another: Y and U differ
- PASS - xyz:X is a single plane, not the image: (362, 640), std 57.9
- PASS - xyz:Y is a single plane, not the image: (362, 640), std 61.3
- PASS - xyz:Z is a single plane, not the image: (362, 640), std 63.3
- PASS - xyz channels differ from one another: X and Y differ
- PASS - bit plane 0 is binary: distinct values [0, 255]
- PASS - bit plane 7 is binary: distinct values [0, 255]

## Observations

Not defects: a parameter at the end of its range doing exactly what it says.

- `space=hsv` on `cctv/brightest.jpg`: refused: Colour space 'hsv' has no channel 'L'. Available: H, S, V
- `channel=r` on `cctv/brightest.jpg`: refused: Colour space 'lab' has no channel 'r'. Available: L, a, b
- `channel=g` on `cctv/brightest.jpg`: refused: Colour space 'lab' has no channel 'g'. Available: L, a, b
- `space=hsv` on `cctv/darkest.jpg`: refused: Colour space 'hsv' has no channel 'L'. Available: H, S, V
- `channel=r` on `cctv/darkest.jpg`: refused: Colour space 'lab' has no channel 'r'. Available: L, a, b
- `channel=g` on `cctv/darkest.jpg`: refused: Colour space 'lab' has no channel 'g'. Available: L, a, b
- `space=hsv` on `cctv/event_fall.jpg`: refused: Colour space 'hsv' has no channel 'L'. Available: H, S, V
- `channel=r` on `cctv/event_fall.jpg`: refused: Colour space 'lab' has no channel 'r'. Available: L, a, b
- `channel=g` on `cctv/event_fall.jpg`: refused: Colour space 'lab' has no channel 'g'. Available: L, a, b
- `space=hsv` on `cctv/event_optflow.jpg`: refused: Colour space 'hsv' has no channel 'L'. Available: H, S, V
- `channel=r` on `cctv/event_optflow.jpg`: refused: Colour space 'lab' has no channel 'r'. Available: L, a, b
- `channel=g` on `cctv/event_optflow.jpg`: refused: Colour space 'lab' has no channel 'g'. Available: L, a, b

## Refused parameters

Rejected on purpose, with the message the user would see.

- `space=hsv` -> ValueError: Colour space 'hsv' has no channel 'L'. Available: H, S, V
- `channel=r` -> ValueError: Colour space 'lab' has no channel 'r'. Available: L, a, b
- `channel=g` -> ValueError: Colour space 'lab' has no channel 'g'. Available: L, a, b

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 0.7 | [362, 640] uint8 mean 170.41 | ok |
| `cctv/brightest.jpg` | `space=hls` | 0.9 | [362, 640] uint8 mean 162.97 | ok |
| `cctv/brightest.jpg` | `space=hsv` | 0.0 | - | refused: ValueError: Colour space 'hsv' has no channel 'L'. Available: H, S, V |
| `cctv/brightest.jpg` | `channel=r` | 0.0 | - | refused: ValueError: Colour space 'lab' has no channel 'r'. Available: L, a, b |
| `cctv/brightest.jpg` | `channel=g` | 0.0 | - | refused: ValueError: Colour space 'lab' has no channel 'g'. Available: L, a, b |
| `cctv/brightest.jpg` | `normalize=True` | 1.8 | [362, 640] uint8 mean 170.41 | ok |
| `cctv/darkest.jpg` | `defaults` | 0.9 | [362, 640] uint8 mean 118.26 | ok |
| `cctv/darkest.jpg` | `space=hls` | 0.7 | [362, 640] uint8 mean 110.66 | ok |
| `cctv/darkest.jpg` | `space=hsv` | 0.0 | - | refused: ValueError: Colour space 'hsv' has no channel 'L'. Available: H, S, V |
| `cctv/darkest.jpg` | `channel=r` | 0.0 | - | refused: ValueError: Colour space 'lab' has no channel 'r'. Available: L, a, b |
| `cctv/darkest.jpg` | `channel=g` | 0.0 | - | refused: ValueError: Colour space 'lab' has no channel 'g'. Available: L, a, b |
| `cctv/darkest.jpg` | `normalize=True` | 1.3 | [362, 640] uint8 mean 118.26 | ok |
| `cctv/event_fall.jpg` | `defaults` | 0.7 | [362, 640] uint8 mean 134.99 | ok |
| `cctv/event_fall.jpg` | `space=hls` | 0.5 | [362, 640] uint8 mean 123.91 | ok |
| `cctv/event_fall.jpg` | `space=hsv` | 0.0 | - | refused: ValueError: Colour space 'hsv' has no channel 'L'. Available: H, S, V |
| `cctv/event_fall.jpg` | `channel=r` | 0.0 | - | refused: ValueError: Colour space 'lab' has no channel 'r'. Available: L, a, b |
| `cctv/event_fall.jpg` | `channel=g` | 0.0 | - | refused: ValueError: Colour space 'lab' has no channel 'g'. Available: L, a, b |
| `cctv/event_fall.jpg` | `normalize=True` | 1.1 | [362, 640] uint8 mean 134.99 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 0.9 | [362, 640] uint8 mean 136.03 | ok |
| `cctv/event_optflow.jpg` | `space=hls` | 0.5 | [362, 640] uint8 mean 123.66 | ok |
| `cctv/event_optflow.jpg` | `space=hsv` | 0.0 | - | refused: ValueError: Colour space 'hsv' has no channel 'L'. Available: H, S, V |
| `cctv/event_optflow.jpg` | `channel=r` | 0.0 | - | refused: ValueError: Colour space 'lab' has no channel 'r'. Available: L, a, b |
| `cctv/event_optflow.jpg` | `channel=g` | 0.0 | - | refused: ValueError: Colour space 'lab' has no channel 'g'. Available: L, a, b |
| `cctv/event_optflow.jpg` | `normalize=True` | 1.1 | [362, 640] uint8 mean 136.03 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 0.7 | [362, 640] uint8 mean 167.28 | ok |
| `cctv/event_tamper.jpg` | `space=hls` | 0.5 | [362, 640] uint8 mean 160.23 | ok |
| `cctv/event_tamper.jpg` | `space=hsv` | 0.0 | - | refused: ValueError: Colour space 'hsv' has no channel 'L'. Available: H, S, V |
| `cctv/event_tamper.jpg` | `channel=r` | 0.0 | - | refused: ValueError: Colour space 'lab' has no channel 'r'. Available: L, a, b |
| `cctv/event_tamper.jpg` | `channel=g` | 0.0 | - | refused: ValueError: Colour space 'lab' has no channel 'g'. Available: L, a, b |
| `cctv/event_tamper.jpg` | `normalize=True` | 1.1 | [362, 640] uint8 mean 167.28 | ok |
| `cctv/flattest.jpg` | `defaults` | 0.7 | [362, 640] uint8 mean 131.74 | ok |
| `cctv/flattest.jpg` | `space=hls` | 0.6 | [362, 640] uint8 mean 119.9 | ok |
| `cctv/flattest.jpg` | `space=hsv` | 0.0 | - | refused: ValueError: Colour space 'hsv' has no channel 'L'. Available: H, S, V |
| `cctv/flattest.jpg` | `channel=r` | 0.0 | - | refused: ValueError: Colour space 'lab' has no channel 'r'. Available: L, a, b |
| `cctv/flattest.jpg` | `channel=g` | 0.0 | - | refused: ValueError: Colour space 'lab' has no channel 'g'. Available: L, a, b |
| `cctv/flattest.jpg` | `normalize=True` | 1.5 | [362, 640] uint8 mean 131.74 | ok |
| `cctv/most_blown.jpg` | `defaults` | 1.0 | [362, 640] uint8 mean 145.08 | ok |
| `cctv/most_blown.jpg` | `space=hls` | 0.7 | [362, 640] uint8 mean 137.92 | ok |
| `cctv/most_blown.jpg` | `space=hsv` | 0.0 | - | refused: ValueError: Colour space 'hsv' has no channel 'L'. Available: H, S, V |
| `cctv/most_blown.jpg` | `channel=r` | 0.0 | - | refused: ValueError: Colour space 'lab' has no channel 'r'. Available: L, a, b |
| `cctv/most_blown.jpg` | `channel=g` | 0.0 | - | refused: ValueError: Colour space 'lab' has no channel 'g'. Available: L, a, b |
| `cctv/most_blown.jpg` | `normalize=True` | 1.3 | [362, 640] uint8 mean 145.08 | ok |
| `cctv/sharpest.jpg` | `defaults` | 1.1 | [362, 640] uint8 mean 138.34 | ok |
| `cctv/sharpest.jpg` | `space=hls` | 0.5 | [362, 640] uint8 mean 131.71 | ok |
| `cctv/sharpest.jpg` | `space=hsv` | 0.0 | - | refused: ValueError: Colour space 'hsv' has no channel 'L'. Available: H, S, V |
| `cctv/sharpest.jpg` | `channel=r` | 0.0 | - | refused: ValueError: Colour space 'lab' has no channel 'r'. Available: L, a, b |
| `cctv/sharpest.jpg` | `channel=g` | 0.0 | - | refused: ValueError: Colour space 'lab' has no channel 'g'. Available: L, a, b |
| `cctv/sharpest.jpg` | `normalize=True` | 1.2 | [362, 640] uint8 mean 138.34 | ok |
| `cctv/softest.jpg` | `defaults` | 0.7 | [362, 640] uint8 mean 133.38 | ok |
| `cctv/softest.jpg` | `space=hls` | 1.6 | [362, 640] uint8 mean 125.01 | ok |
| `cctv/softest.jpg` | `space=hsv` | 0.0 | - | refused: ValueError: Colour space 'hsv' has no channel 'L'. Available: H, S, V |
| `cctv/softest.jpg` | `channel=r` | 0.0 | - | refused: ValueError: Colour space 'lab' has no channel 'r'. Available: L, a, b |
| `cctv/softest.jpg` | `channel=g` | 0.0 | - | refused: ValueError: Colour space 'lab' has no channel 'g'. Available: L, a, b |
| `cctv/softest.jpg` | `normalize=True` | 1.7 | [362, 640] uint8 mean 133.38 | ok |

## Artifacts

Outputs written to `validation/artifacts/component/`:

- `cctv_brightest.png`
- `cctv_darkest.png`
- `cctv_event_fall.png`
- `cctv_event_optflow.png`
- `cctv_event_tamper.png`
- `cctv_flattest.png`
- `cctv_most_blown.png`
- `cctv_sharpest.png`
- `cctv_softest.png`
