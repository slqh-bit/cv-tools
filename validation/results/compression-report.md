# compression - validation result

**Blocking measures, plus the quality read from the file**  
`src.filters.compression_analysis` | family: Analysis | 2026-09-01T16:37:25

## Verdict

**PASS** - 8 runs, no invariant broken, 6 specific checks passed.

## What this filter specifically promises

- PASS - reads back a quality of 40 from the tables: reported 40 for a file saved at 40
- PASS - reads back a quality of 60 from the tables: reported 60 for a file saved at 60
- PASS - reads back a quality of 75 from the tables: reported 75 for a file saved at 75
- PASS - reads back a quality of 90 from the tables: reported 90 for a file saved at 90
- PASS - reports no tables for a file that has none: a PNG carries no quantisation tables
- PASS - blockiness rises measurably as quality falls: 3.9 -> 4.2 -> 4.4 at quality 90/60/30 (+0.5 end to end)

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 20.2 | None None mean None | ok |
| `cctv/darkest.jpg` | `defaults` | 19.6 | None None mean None | ok |
| `cctv/event_fall.jpg` | `defaults` | 22.3 | None None mean None | ok |
| `cctv/event_optflow.jpg` | `defaults` | 19.3 | None None mean None | ok |
| `cctv/event_tamper.jpg` | `defaults` | 18.6 | None None mean None | ok |
| `cctv/flattest.jpg` | `defaults` | 19.0 | None None mean None | ok |
| `cctv/most_blown.jpg` | `defaults` | 19.0 | None None mean None | ok |
| `cctv/sharpest.jpg` | `defaults` | 19.2 | None None mean None | ok |

## Reports

### `cctv/brightest.jpg`

```
Compression analysis:
  blockiness: 3.7/100 (boundary step 5.75 vs interior 4.32)
  likely JPEG-compressed: yes
  region uniformity: 0.72
  quantisation tables: 2, estimated quality 95
  note: blocking indicates compression strength, not manipulation
```

### `cctv/darkest.jpg`

```
Compression analysis:
  blockiness: 3.0/100 (boundary step 5.90 vs interior 4.66)
  likely JPEG-compressed: yes
  region uniformity: 0.78
  quantisation tables: 2, estimated quality 95
  note: blocking indicates compression strength, not manipulation
```

### `cctv/event_fall.jpg`

```
Compression analysis:
  blockiness: 4.9/100 (boundary step 14.71 vs interior 10.20)
  likely JPEG-compressed: yes
  region uniformity: 0.63
  quantisation tables: 2, estimated quality 95
  note: blocking indicates compression strength, not manipulation
```

### `cctv/event_optflow.jpg`

```
Compression analysis:
  blockiness: 3.4/100 (boundary step 6.00 vs interior 4.59)
  likely JPEG-compressed: yes
  region uniformity: 0.75
  quantisation tables: 2, estimated quality 95
  note: blocking indicates compression strength, not manipulation
```

### `cctv/event_tamper.jpg`

```
Compression analysis:
  blockiness: 3.8/100 (boundary step 5.74 vs interior 4.29)
  likely JPEG-compressed: yes
  region uniformity: 0.71
  quantisation tables: 2, estimated quality 95
  note: blocking indicates compression strength, not manipulation
```

### `cctv/flattest.jpg`

```
Compression analysis:
  blockiness: 3.5/100 (boundary step 5.63 vs interior 4.29)
  likely JPEG-compressed: yes
  region uniformity: 0.76
  quantisation tables: 2, estimated quality 95
  note: blocking indicates compression strength, not manipulation
```

### `cctv/most_blown.jpg`

```
Compression analysis:
  blockiness: 2.5/100 (boundary step 5.98 vs interior 4.89)
  likely JPEG-compressed: yes
  region uniformity: 0.86
  quantisation tables: 2, estimated quality 95
  note: blocking indicates compression strength, not manipulation
```

### `cctv/sharpest.jpg`

```
Compression analysis:
  blockiness: 4.0/100 (boundary step 15.30 vs interior 11.25)
  likely JPEG-compressed: yes
  region uniformity: 0.70
  quantisation tables: 2, estimated quality 95
  note: blocking indicates compression strength, not manipulation
```

