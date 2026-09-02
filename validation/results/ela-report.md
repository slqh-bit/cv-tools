# ela - validation result

**Block-level recompression error and its outliers**  
`cv_tools.filters.ela` | family: Analysis | 2026-09-01T16:37:20

## Verdict

**PASS** - 8 runs, no invariant broken, 3 specific checks passed.

## What this filter specifically promises

- PASS - a region with a different history stands out more than an untouched one: inside-outside gap 4.53 on the splice against 0.08 on the same region of an untouched frame
- PASS - reports the block statistics the report renders: mean 1.03, hottest block at (336, 0)
- PASS - the comparison quality changes the error level: 3.09 -> 2.27 -> 0.93 at quality 70/85/95

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 11.6 | None None mean None | ok |
| `cctv/darkest.jpg` | `defaults` | 10.3 | None None mean None | ok |
| `cctv/event_fall.jpg` | `defaults` | 11.0 | None None mean None | ok |
| `cctv/event_optflow.jpg` | `defaults` | 10.5 | None None mean None | ok |
| `cctv/event_tamper.jpg` | `defaults` | 13.7 | None None mean None | ok |
| `cctv/flattest.jpg` | `defaults` | 10.6 | None None mean None | ok |
| `cctv/most_blown.jpg` | `defaults` | 11.3 | None None mean None | ok |
| `cctv/sharpest.jpg` | `defaults` | 10.6 | None None mean None | ok |

## Reports

### `cctv/brightest.jpg`

```
Error Level Analysis (JPEG quality 90, 16px blocks):
  mean error: 0.68, max: 14.00
  block mean: 0.68, std: 0.57
  hottest block: (336, 208): mean=4.24, z-score=6.20
  note: only meaningful on JPEG originals; texture raises error levels too
```

### `cctv/darkest.jpg`

```
Error Level Analysis (JPEG quality 90, 16px blocks):
  mean error: 0.69, max: 14.00
  block mean: 0.70, std: 0.69
  hottest block: (112, 112): mean=4.43, z-score=5.37
  note: only meaningful on JPEG originals; texture raises error levels too
```

### `cctv/event_fall.jpg`

```
Error Level Analysis (JPEG quality 90, 16px blocks):
  mean error: 2.01, max: 22.00
  block mean: 2.01, std: 1.18
  hottest block: (624, 176): mean=6.30, z-score=3.63
  note: only meaningful on JPEG originals; texture raises error levels too
```

### `cctv/event_optflow.jpg`

```
Error Level Analysis (JPEG quality 90, 16px blocks):
  mean error: 1.01, max: 19.00
  block mean: 1.02, std: 0.89
  hottest block: (496, 32): mean=4.91, z-score=4.39
  note: only meaningful on JPEG originals; texture raises error levels too
```

### `cctv/event_tamper.jpg`

```
Error Level Analysis (JPEG quality 90, 16px blocks):
  mean error: 0.67, max: 13.00
  block mean: 0.67, std: 0.58
  hottest block: (336, 208): mean=3.65, z-score=5.18
  note: only meaningful on JPEG originals; texture raises error levels too
```

### `cctv/flattest.jpg`

```
Error Level Analysis (JPEG quality 90, 16px blocks):
  mean error: 0.96, max: 18.00
  block mean: 0.96, std: 0.86
  hottest block: (496, 16): mean=4.79, z-score=4.45
  note: only meaningful on JPEG originals; texture raises error levels too
```

### `cctv/most_blown.jpg`

```
Error Level Analysis (JPEG quality 90, 16px blocks):
  mean error: 0.75, max: 14.00
  block mean: 0.76, std: 0.71
  hottest block: (112, 32): mean=3.59, z-score=4.01
  note: only meaningful on JPEG originals; texture raises error levels too
```

### `cctv/sharpest.jpg`

```
Error Level Analysis (JPEG quality 90, 16px blocks):
  mean error: 1.64, max: 20.00
  block mean: 1.65, std: 0.95
  hottest block: (352, 0): mean=5.55, z-score=4.09
  note: only meaningful on JPEG originals; texture raises error levels too
```


## Artifacts

Outputs written to `validation/artifacts/ela/`:

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
