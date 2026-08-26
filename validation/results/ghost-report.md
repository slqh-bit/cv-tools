# ghost - validation result

**Per-block prior JPEG quality, and blocks that disagree**  
`src.filters.jpeg_ghost` | family: Analysis | 2026-08-21T12:46:56

## Verdict

**PASS** - 8 runs, no invariant broken, 7 specific checks passed.

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
| `cctv/brightest.jpg` | `defaults` | 76.9 | None None mean None | ok |
| `cctv/darkest.jpg` | `defaults` | 77.0 | None None mean None | ok |
| `cctv/event_fall.jpg` | `defaults` | 78.9 | None None mean None | ok |
| `cctv/event_optflow.jpg` | `defaults` | 76.9 | None None mean None | ok |
| `cctv/event_tamper.jpg` | `defaults` | 75.0 | None None mean None | ok |
| `cctv/flattest.jpg` | `defaults` | 81.1 | None None mean None | ok |
| `cctv/most_blown.jpg` | `defaults` | 77.2 | None None mean None | ok |
| `cctv/sharpest.jpg` | `defaults` | 76.3 | None None mean None | ok |

## Reports

### `cctv/brightest.jpg`

```
JPEG ghost (qualities 50-100, 16px blocks):
  region: none given
  This measures the JPEG quality of a region you name; it does not search for one. Mark a region and run it again - the desktop viewer fills the box from a drag.
  note: only meaningful on a single-JPEG composite; any re-save erases it, and a paste that does not land on the JPEG 8x8 grid leaves nothing to find. Measured on 32 frames from two cameras with grid-aligned pastes: 59% found, 3% of untouched regions called positive. A pointer to inspect, never a finding
```

### `cctv/darkest.jpg`

```
JPEG ghost (qualities 50-100, 16px blocks):
  region: none given
  This measures the JPEG quality of a region you name; it does not search for one. Mark a region and run it again - the desktop viewer fills the box from a drag.
  note: only meaningful on a single-JPEG composite; any re-save erases it, and a paste that does not land on the JPEG 8x8 grid leaves nothing to find. Measured on 32 frames from two cameras with grid-aligned pastes: 59% found, 3% of untouched regions called positive. A pointer to inspect, never a finding
```

### `cctv/event_fall.jpg`

```
JPEG ghost (qualities 50-100, 16px blocks):
  region: none given
  This measures the JPEG quality of a region you name; it does not search for one. Mark a region and run it again - the desktop viewer fills the box from a drag.
  note: only meaningful on a single-JPEG composite; any re-save erases it, and a paste that does not land on the JPEG 8x8 grid leaves nothing to find. Measured on 32 frames from two cameras with grid-aligned pastes: 59% found, 3% of untouched regions called positive. A pointer to inspect, never a finding
```

### `cctv/event_optflow.jpg`

```
JPEG ghost (qualities 50-100, 16px blocks):
  region: none given
  This measures the JPEG quality of a region you name; it does not search for one. Mark a region and run it again - the desktop viewer fills the box from a drag.
  note: only meaningful on a single-JPEG composite; any re-save erases it, and a paste that does not land on the JPEG 8x8 grid leaves nothing to find. Measured on 32 frames from two cameras with grid-aligned pastes: 59% found, 3% of untouched regions called positive. A pointer to inspect, never a finding
```

### `cctv/event_tamper.jpg`

```
JPEG ghost (qualities 50-100, 16px blocks):
  region: none given
  This measures the JPEG quality of a region you name; it does not search for one. Mark a region and run it again - the desktop viewer fills the box from a drag.
  note: only meaningful on a single-JPEG composite; any re-save erases it, and a paste that does not land on the JPEG 8x8 grid leaves nothing to find. Measured on 32 frames from two cameras with grid-aligned pastes: 59% found, 3% of untouched regions called positive. A pointer to inspect, never a finding
```

### `cctv/flattest.jpg`

```
JPEG ghost (qualities 50-100, 16px blocks):
  region: none given
  This measures the JPEG quality of a region you name; it does not search for one. Mark a region and run it again - the desktop viewer fills the box from a drag.
  note: only meaningful on a single-JPEG composite; any re-save erases it, and a paste that does not land on the JPEG 8x8 grid leaves nothing to find. Measured on 32 frames from two cameras with grid-aligned pastes: 59% found, 3% of untouched regions called positive. A pointer to inspect, never a finding
```

### `cctv/most_blown.jpg`

```
JPEG ghost (qualities 50-100, 16px blocks):
  region: none given
  This measures the JPEG quality of a region you name; it does not search for one. Mark a region and run it again - the desktop viewer fills the box from a drag.
  note: only meaningful on a single-JPEG composite; any re-save erases it, and a paste that does not land on the JPEG 8x8 grid leaves nothing to find. Measured on 32 frames from two cameras with grid-aligned pastes: 59% found, 3% of untouched regions called positive. A pointer to inspect, never a finding
```

### `cctv/sharpest.jpg`

```
JPEG ghost (qualities 50-100, 16px blocks):
  region: none given
  This measures the JPEG quality of a region you name; it does not search for one. Mark a region and run it again - the desktop viewer fills the box from a drag.
  note: only meaningful on a single-JPEG composite; any re-save erases it, and a paste that does not land on the JPEG 8x8 grid leaves nothing to find. Measured on 32 frames from two cameras with grid-aligned pastes: 59% found, 3% of untouched regions called positive. A pointer to inspect, never a finding
```


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
