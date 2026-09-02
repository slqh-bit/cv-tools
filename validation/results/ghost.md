# ghost - validation result

**JPEG ghost: the recompression sweep frame with the most structure, dark where the pixels match that quality**  
`cv_tools.filters.jpeg_ghost` | family: Forensic | 2026-09-01T16:37:13

## Verdict

**PASS** - 22 runs, no invariant broken, 7 specific checks passed.

## What this filter specifically promises

- PASS - recovers the quality a named region was saved at: reported 55 for a Q55 paste, separation -0.328
- PASS - the same region of an untouched frame does not fire: separation -0.015 against a -0.25 threshold
- PASS - claims nothing when no region is given: searching for the region does not work and is not offered
- PASS - the sweep is exposed for inspection: 11 normalised frames of 22x40 blocks
- PASS - a different scene at the same quality does not fire: dip -0.094 against a -0.25 threshold - texture alone is not read as compression history
- PASS - a quality difference dips deeper than texture alone: same donor at Q55 dips -0.278 against -0.094 at Q95 - the compression difference is what moves it
- PASS - finds a higher-quality region inside a lower-quality frame: reported 95 for a Q95 region pasted into a Q60 frame, dip -0.331

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 81.6 | [352, 640] uint8 mean 187.37 | ok |
| `cctv/brightest.jpg` | `upscale=False` | 82.4 | [22, 40] uint8 mean 187.37 | ok |
| `cctv/darkest.jpg` | `defaults` | 87.0 | [352, 640] uint8 mean 187.06 | ok |
| `cctv/darkest.jpg` | `upscale=False` | 76.4 | [22, 40] uint8 mean 187.06 | ok |
| `cctv/event_fall.jpg` | `defaults` | 84.5 | [352, 640] uint8 mean 111.09 | ok |
| `cctv/event_fall.jpg` | `upscale=False` | 79.2 | [22, 40] uint8 mean 111.09 | ok |
| `cctv/event_optflow.jpg` | `defaults` | 82.2 | [352, 640] uint8 mean 100.51 | ok |
| `cctv/event_optflow.jpg` | `upscale=False` | 77.4 | [22, 40] uint8 mean 100.51 | ok |
| `cctv/event_tamper.jpg` | `defaults` | 81.9 | [352, 640] uint8 mean 68.97 | ok |
| `cctv/event_tamper.jpg` | `upscale=False` | 80.6 | [22, 40] uint8 mean 68.97 | ok |
| `cctv/flattest.jpg` | `defaults` | 84.5 | [352, 640] uint8 mean 102.21 | ok |
| `cctv/flattest.jpg` | `upscale=False` | 76.1 | [22, 40] uint8 mean 102.21 | ok |
| `cctv/most_blown.jpg` | `defaults` | 79.6 | [352, 640] uint8 mean 207.03 | ok |
| `cctv/most_blown.jpg` | `upscale=False` | 79.0 | [22, 40] uint8 mean 207.03 | ok |
| `cctv/sharpest.jpg` | `defaults` | 83.8 | [352, 640] uint8 mean 237.36 | ok |
| `cctv/sharpest.jpg` | `upscale=False` | 78.4 | [22, 40] uint8 mean 237.36 | ok |
| `cctv/softest.jpg` | `defaults` | 80.7 | [352, 640] uint8 mean 140.26 | ok |
| `cctv/softest.jpg` | `upscale=False` | 76.0 | [22, 40] uint8 mean 140.26 | ok |
| `ground_truth/quality_splice.jpg` | `defaults` | 85.1 | [352, 640] uint8 mean 233.84 | ok |
| `ground_truth/quality_splice.jpg` | `upscale=False` | 85.1 | [22, 40] uint8 mean 233.84 | ok |
| `ground_truth/clean_control.jpg` | `defaults` | 83.5 | [352, 640] uint8 mean 237.94 | ok |
| `ground_truth/clean_control.jpg` | `upscale=False` | 80.0 | [22, 40] uint8 mean 237.94 | ok |

## Artifacts

Outputs written to `validation/artifacts/ghost/`:

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
- `ground_truth_quality_splice.png`
