# noise - validation result

**Global and per-block noise level, and how evenly it is spread**  
`src.filters.noise_analysis` | family: Analysis | 2026-08-20T00:27:52

## Verdict

**PASS** - 8 runs, no invariant broken.

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
| `cctv/brightest.jpg` | `defaults` | 2.8 | None None mean None | ok |
| `cctv/darkest.jpg` | `defaults` | 2.0 | None None mean None | ok |
| `cctv/event_fall.jpg` | `defaults` | 1.9 | None None mean None | ok |
| `cctv/event_optflow.jpg` | `defaults` | 1.9 | None None mean None | ok |
| `cctv/event_tamper.jpg` | `defaults` | 1.9 | None None mean None | ok |
| `cctv/flattest.jpg` | `defaults` | 1.9 | None None mean None | ok |
| `cctv/most_blown.jpg` | `defaults` | 1.9 | None None mean None | ok |
| `cctv/sharpest.jpg` | `defaults` | 1.9 | None None mean None | ok |

## Reports

### `cctv/brightest.jpg`

```
Noise analysis:
  global sigma: 1.46
  SNR: 32.9 dB
  blocks: 11x20 of 32px, mean=0.96 std=1.34
  uniformity: 1.39 (uneven - inspect)
  noisiest block: (64, 0): sigma=7.00
  quietest block: (192, 0): sigma=0.00
  note: uneven noise can also come from content: flat sky against detailed foreground reads as non-uniform
```

### `cctv/darkest.jpg`

```
Noise analysis:
  global sigma: 1.69
  SNR: 29.6 dB
  blocks: 11x20 of 32px, mean=1.26 std=1.71
  uniformity: 1.35 (uneven - inspect)
  noisiest block: (384, 224): sigma=9.00
  quietest block: (384, 0): sigma=0.00
  note: uneven noise can also come from content: flat sky against detailed foreground reads as non-uniform
```

### `cctv/event_fall.jpg`

```
Noise analysis:
  global sigma: 4.21
  SNR: 22.8 dB
  blocks: 11x20 of 32px, mean=3.66 std=4.84
  uniformity: 1.32 (uneven - inspect)
  noisiest block: (480, 160): sigma=23.00
  quietest block: (192, 0): sigma=0.00
  note: uneven noise can also come from content: flat sky against detailed foreground reads as non-uniform
```

### `cctv/event_optflow.jpg`

```
Noise analysis:
  global sigma: 1.76
  SNR: 28.5 dB
  blocks: 11x20 of 32px, mean=1.30 std=2.22
  uniformity: 1.70 (uneven - inspect)
  noisiest block: (480, 320): sigma=12.00
  quietest block: (192, 0): sigma=0.00
  note: uneven noise can also come from content: flat sky against detailed foreground reads as non-uniform
```

### `cctv/event_tamper.jpg`

```
Noise analysis:
  global sigma: 1.45
  SNR: 32.8 dB
  blocks: 11x20 of 32px, mean=0.96 std=1.36
  uniformity: 1.42 (uneven - inspect)
  noisiest block: (64, 0): sigma=7.00
  quietest block: (192, 0): sigma=0.00
  note: uneven noise can also come from content: flat sky against detailed foreground reads as non-uniform
```

### `cctv/flattest.jpg`

```
Noise analysis:
  global sigma: 1.62
  SNR: 29.0 dB
  blocks: 11x20 of 32px, mean=1.19 std=2.09
  uniformity: 1.76 (uneven - inspect)
  noisiest block: (480, 320): sigma=11.00
  quietest block: (192, 0): sigma=0.00
  note: uneven noise can also come from content: flat sky against detailed foreground reads as non-uniform
```

### `cctv/most_blown.jpg`

```
Noise analysis:
  global sigma: 1.84
  SNR: 30.2 dB
  blocks: 11x20 of 32px, mean=1.41 std=1.73
  uniformity: 1.23 (uneven - inspect)
  noisiest block: (384, 224): sigma=9.00
  quietest block: (384, 0): sigma=0.00
  note: uneven noise can also come from content: flat sky against detailed foreground reads as non-uniform
```

### `cctv/sharpest.jpg`

```
Noise analysis:
  global sigma: 4.64
  SNR: 22.4 dB
  blocks: 11x20 of 32px, mean=4.20 std=4.34
  uniformity: 1.03 (uneven - inspect)
  noisiest block: (384, 224): sigma=20.00
  quietest block: (480, 0): sigma=0.00
  note: uneven noise can also come from content: flat sky against detailed foreground reads as non-uniform
```

