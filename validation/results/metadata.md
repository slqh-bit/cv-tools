# metadata - validation result

**EXIF tags, JPEG segments and the contradictions between them**  
`cv_tools.filters.metadata_forensics` | family: Analysis | 2026-08-20T00:27:57

## Verdict

**PASS** - 8 runs, no invariant broken.

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 0.7 | None None mean None | ok |
| `cctv/darkest.jpg` | `defaults` | 0.5 | None None mean None | ok |
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

