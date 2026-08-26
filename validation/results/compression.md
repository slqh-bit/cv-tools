# compression - validation result

**Blocking measures, plus the quality read from the file**  
`src.filters.compression_analysis` | family: Analysis | 2026-08-20T00:27:56

## Verdict

**PASS** - 8 runs, no invariant broken.

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 19.3 | None None mean None | ok |
| `cctv/darkest.jpg` | `defaults` | 16.6 | None None mean None | ok |
| `cctv/event_fall.jpg` | `defaults` | 17.5 | None None mean None | ok |
| `cctv/event_optflow.jpg` | `defaults` | 16.5 | None None mean None | ok |
| `cctv/event_tamper.jpg` | `defaults` | 16.6 | None None mean None | ok |
| `cctv/flattest.jpg` | `defaults` | 16.6 | None None mean None | ok |
| `cctv/most_blown.jpg` | `defaults` | 16.5 | None None mean None | ok |
| `cctv/sharpest.jpg` | `defaults` | 16.6 | None None mean None | ok |

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
  blockiness: 3.0/100 (boundary step 5.92 vs interior 4.67)
  likely JPEG-compressed: yes
  region uniformity: 0.78
  quantisation tables: 2, estimated quality 95
  note: blocking indicates compression strength, not manipulation
```

### `cctv/event_fall.jpg`

```
Compression analysis:
  blockiness: 4.9/100 (boundary step 14.70 vs interior 10.19)
  likely JPEG-compressed: yes
  region uniformity: 0.63
  quantisation tables: 2, estimated quality 95
  note: blocking indicates compression strength, not manipulation
```

### `cctv/event_optflow.jpg`

```
Compression analysis:
  blockiness: 3.4/100 (boundary step 6.05 vs interior 4.64)
  likely JPEG-compressed: yes
  region uniformity: 0.76
  quantisation tables: 2, estimated quality 95
  note: blocking indicates compression strength, not manipulation
```

### `cctv/event_tamper.jpg`

```
Compression analysis:
  blockiness: 3.8/100 (boundary step 5.74 vs interior 4.29)
  likely JPEG-compressed: yes
  region uniformity: 0.72
  quantisation tables: 2, estimated quality 95
  note: blocking indicates compression strength, not manipulation
```

### `cctv/flattest.jpg`

```
Compression analysis:
  blockiness: 3.5/100 (boundary step 5.68 vs interior 4.33)
  likely JPEG-compressed: yes
  region uniformity: 0.76
  quantisation tables: 2, estimated quality 95
  note: blocking indicates compression strength, not manipulation
```

### `cctv/most_blown.jpg`

```
Compression analysis:
  blockiness: 2.5/100 (boundary step 5.99 vs interior 4.89)
  likely JPEG-compressed: yes
  region uniformity: 0.86
  quantisation tables: 2, estimated quality 95
  note: blocking indicates compression strength, not manipulation
```

### `cctv/sharpest.jpg`

```
Compression analysis:
  blockiness: 4.0/100 (boundary step 15.31 vs interior 11.25)
  likely JPEG-compressed: yes
  region uniformity: 0.70
  quantisation tables: 2, estimated quality 95
  note: blocking indicates compression strength, not manipulation
```

