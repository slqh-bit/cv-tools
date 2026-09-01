# metadata - validation result

**EXIF tags, JPEG segments and the contradictions between them**  
`src.filters.metadata_forensics` | family: Analysis | 2026-09-01T16:37:27

## Verdict

**PASS** - 8 runs, no invariant broken, 7 specific checks passed.

## What this filter specifically promises

- PASS - reads a real camera header: 52 tags, NIKON CORPORATION NIKON D80
- PASS - flags the cropped-after-capture contradictions: findings: ['dimension_mismatch', 'modified_after_capture', 'thumbnail_mismatch']
- PASS - remarks on this JPEG having no EXIF at all: findings on sharpest.jpg: ['no_exif'] - absence is normal, and said so
- PASS - reads the PNG as itself and stays quiet about EXIF: format .png, has_exif False, findings none - PNG is not an EXIF-bearing format, so silence is correct
- PASS - catches a digitised time before the capture time: findings: ['modified_after_capture', 'timestamp_disorder']
- PASS - separates a consistent set of timestamps from a disordered one: 0 findings on three identical timestamps against 2 on a disordered set
- PASS - names an editor in the Software tag: Photoshop matched, camera firmware not

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 0.7 | None None mean None | ok |
| `cctv/darkest.jpg` | `defaults` | 0.6 | None None mean None | ok |
| `cctv/event_fall.jpg` | `defaults` | 0.5 | None None mean None | ok |
| `cctv/event_optflow.jpg` | `defaults` | 0.5 | None None mean None | ok |
| `cctv/event_tamper.jpg` | `defaults` | 0.5 | None None mean None | ok |
| `cctv/flattest.jpg` | `defaults` | 0.5 | None None mean None | ok |
| `cctv/most_blown.jpg` | `defaults` | 0.5 | None None mean None | ok |
| `cctv/sharpest.jpg` | `defaults` | 0.5 | None None mean None | ok |

## Reports

### `cctv/brightest.jpg`

```
Metadata forensics (brightest.jpg):
  EXIF: none
  segments: APP0
  [info] no_exif: A .jpg file normally carries EXIF; this one has none, so it was stripped, re-encoded, or never written by a camera
  note: metadata is trivially edited or stripped; a clean header proves nothing
```

### `cctv/darkest.jpg`

```
Metadata forensics (darkest.jpg):
  EXIF: none
  segments: APP0
  [info] no_exif: A .jpg file normally carries EXIF; this one has none, so it was stripped, re-encoded, or never written by a camera
  note: metadata is trivially edited or stripped; a clean header proves nothing
```

### `cctv/event_fall.jpg`

```
Metadata forensics (event_fall.jpg):
  EXIF: none
  segments: APP0
  [info] no_exif: A .jpg file normally carries EXIF; this one has none, so it was stripped, re-encoded, or never written by a camera
  note: metadata is trivially edited or stripped; a clean header proves nothing
```

### `cctv/event_optflow.jpg`

```
Metadata forensics (event_optflow.jpg):
  EXIF: none
  segments: APP0
  [info] no_exif: A .jpg file normally carries EXIF; this one has none, so it was stripped, re-encoded, or never written by a camera
  note: metadata is trivially edited or stripped; a clean header proves nothing
```

### `cctv/event_tamper.jpg`

```
Metadata forensics (event_tamper.jpg):
  EXIF: none
  segments: APP0
  [info] no_exif: A .jpg file normally carries EXIF; this one has none, so it was stripped, re-encoded, or never written by a camera
  note: metadata is trivially edited or stripped; a clean header proves nothing
```

### `cctv/flattest.jpg`

```
Metadata forensics (flattest.jpg):
  EXIF: none
  segments: APP0
  [info] no_exif: A .jpg file normally carries EXIF; this one has none, so it was stripped, re-encoded, or never written by a camera
  note: metadata is trivially edited or stripped; a clean header proves nothing
```

### `cctv/most_blown.jpg`

```
Metadata forensics (most_blown.jpg):
  EXIF: none
  segments: APP0
  [info] no_exif: A .jpg file normally carries EXIF; this one has none, so it was stripped, re-encoded, or never written by a camera
  note: metadata is trivially edited or stripped; a clean header proves nothing
```

### `cctv/sharpest.jpg`

```
Metadata forensics (sharpest.jpg):
  EXIF: none
  segments: APP0
  [info] no_exif: A .jpg file normally carries EXIF; this one has none, so it was stripped, re-encoded, or never written by a camera
  note: metadata is trivially edited or stripped; a clean header proves nothing
```

