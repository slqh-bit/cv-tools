# noise - validation result

**Global and per-block noise level, and how evenly it is spread**  
`src.filters.noise_analysis` | family: Analysis | 2026-08-21T12:46:51

## Verdict

**PASS** - 8 runs, no invariant broken, 7 specific checks passed.

## What this filter specifically promises

- PASS - recovers a known sigma of 2 to within 5%: measured 2.03 against 2 added
- PASS - recovers a known sigma of 5 to within 5%: measured 5.00 against 5 added
- PASS - recovers a known sigma of 10 to within 5%: measured 10.01 against 10 added
- PASS - recovers a known sigma of 20 to within 5%: measured 20.03 against 20 added
- PASS - per-channel noise reads through the luminance weighting: 6.69 measured, 6.69 expected from sigma 10 on three independent channels
- PASS - reads a frame with two noise levels as less uniform: uniformity 0.00 even vs 0.75 split
- PASS - points at the block where the noise actually is: noisiest block reported at (288, 192), sigma 12.00; the noise was planted in x 288-384, y 192-288

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 2.7 | None None mean None | ok |
| `cctv/darkest.jpg` | `defaults` | 2.3 | None None mean None | ok |
| `cctv/event_fall.jpg` | `defaults` | 2.0 | None None mean None | ok |
| `cctv/event_optflow.jpg` | `defaults` | 1.9 | None None mean None | ok |
| `cctv/event_tamper.jpg` | `defaults` | 2.0 | None None mean None | ok |
| `cctv/flattest.jpg` | `defaults` | 2.0 | None None mean None | ok |
| `cctv/most_blown.jpg` | `defaults` | 2.0 | None None mean None | ok |
| `cctv/sharpest.jpg` | `defaults` | 1.9 | None None mean None | ok |

## Reports

### `cctv/brightest.jpg`

```
Noise analysis:
  global sigma: 1.46
  SNR: 32.8 dB
  blocks: 11x20 of 32px, mean=0.97 std=1.34
  uniformity: 1.38 (uneven - inspect)
  noisiest block: (64, 0): sigma=7.00
  quietest block: (192, 0): sigma=0.00
  note: uneven noise can also come from content: flat sky against detailed foreground reads as non-uniform
```

### `cctv/darkest.jpg`

```
Noise analysis:
  global sigma: 1.68
  SNR: 29.5 dB
  blocks: 11x20 of 32px, mean=1.24 std=1.70
  uniformity: 1.37 (uneven - inspect)
  noisiest block: (96, 128): sigma=8.00
  quietest block: (384, 0): sigma=0.00
  note: uneven noise can also come from content: flat sky against detailed foreground reads as non-uniform
```

### `cctv/event_fall.jpg`

```
Noise analysis:
  global sigma: 4.19
  SNR: 22.7 dB
  blocks: 11x20 of 32px, mean=3.65 std=4.86
  uniformity: 1.33 (uneven - inspect)
  noisiest block: (480, 320): sigma=24.00
  quietest block: (192, 0): sigma=0.00
  note: uneven noise can also come from content: flat sky against detailed foreground reads as non-uniform
```

### `cctv/event_optflow.jpg`

```
Noise analysis:
  global sigma: 1.73
  SNR: 28.6 dB
  blocks: 11x20 of 32px, mean=1.29 std=2.20
  uniformity: 1.71 (uneven - inspect)
  noisiest block: (480, 320): sigma=12.00
  quietest block: (192, 0): sigma=0.00
  note: uneven noise can also come from content: flat sky against detailed foreground reads as non-uniform
```

### `cctv/event_tamper.jpg`

```
Noise analysis:
  global sigma: 1.45
  SNR: 32.7 dB
  blocks: 11x20 of 32px, mean=0.96 std=1.36
  uniformity: 1.41 (uneven - inspect)
  noisiest block: (64, 0): sigma=7.00
  quietest block: (192, 0): sigma=0.00
  note: uneven noise can also come from content: flat sky against detailed foreground reads as non-uniform
```

### `cctv/flattest.jpg`

```
Noise analysis:
  global sigma: 1.59
  SNR: 29.1 dB
  blocks: 11x20 of 32px, mean=1.17 std=2.09
  uniformity: 1.78 (uneven - inspect)
  noisiest block: (480, 320): sigma=11.00
  quietest block: (192, 0): sigma=0.00
  note: uneven noise can also come from content: flat sky against detailed foreground reads as non-uniform
```

### `cctv/most_blown.jpg`

```
Noise analysis:
  global sigma: 1.83
  SNR: 30.1 dB
  blocks: 11x20 of 32px, mean=1.40 std=1.74
  uniformity: 1.25 (uneven - inspect)
  noisiest block: (384, 224): sigma=9.00
  quietest block: (384, 0): sigma=0.00
  note: uneven noise can also come from content: flat sky against detailed foreground reads as non-uniform
```

### `cctv/sharpest.jpg`

```
Noise analysis:
  global sigma: 4.63
  SNR: 22.4 dB
  blocks: 11x20 of 32px, mean=4.18 std=4.34
  uniformity: 1.04 (uneven - inspect)
  noisiest block: (384, 224): sigma=20.00
  quietest block: (480, 0): sigma=0.00
  note: uneven noise can also come from content: flat sky against detailed foreground reads as non-uniform
```

