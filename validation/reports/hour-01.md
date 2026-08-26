# Hour 1 - corpus, harness, first full sweep

**2026-08-20** | 73 filters and reports | 3,081 runs | 2 real defects found, 1 fixed

## What was built

**Corpus** (`validation/corpus/`, described in `manifest.json`). Three sources,
because no one of them proves what the others do:

| Source | What it is | Why |
|---|---|---|
| `cctv/` | 9 frames chosen by measurement from the 200 in `ai cam/snapshots` | The job. Real sensor noise, real JPEG history, real lighting |
| `reference/` | Motion-blurred plate, defocused text, sudoku, 13 chessboard views, a Nikon D80 JPEG | Properties that must be known rather than assumed |
| `ground_truth/` | Copy-move paste, a region re-encoded at a lower quality, a clean control, a known barrel distortion, a known perspective warp | A forensic filter that reports something can only be checked against an image whose history was chosen |

The CCTV frames are picked by measurement, not at random - every snapshot is
the same room, so a random nine would test one exposure nine times. They are
the darkest, the brightest, the most blown, the flattest, the softest and
sharpest by Laplacian variance, plus one of each event type the camera raises.

**Harness** (`validation/harness.py`). Runs each filter over its images and a
parameter matrix, and separates three outcomes that a naive runner conflates:

- **defect** - broke a promise the toolkit makes
- **refused** - rejected bad input on purpose, with a message. This is the
  filter working
- **note** - a parameter at the end of its range doing exactly what it says

That distinction was itself a fix: the first version called `levels` at
defaults a failure for returning the image unchanged, which is precisely what
black 0 / white 255 / gamma 1 should do.

**Checks** (`validation/checks.py`). What each filter specifically promises,
measured with a number: CLAHE raises local sigma, `nl_means` lowers measured
noise without collapsing edge density, `redact` fill/noise leave no residual
correlation, `perspective` returns a known warp to straight.

## Defect 1 - the UIs offered 39 values the filters reject (FIXED)

`apply_clahe` implements `color_mode='luminance'` and not `'grayscale'`;
`histogram_equalization` the reverse. Both were offered the union. `method` was
worse: four filters use that name for four unrelated vocabularies, so
`white_balance` offered `pixelate` and `desaturate` offered `gray_world`.

Six filter/parameter pairs, 39 values. In the Tkinter combobox a bad suggestion
can be typed over; the dashboard's selectbox offers only what it lists, so
there it was a dead end with no way past.

**Fix.** Each module now names its own vocabulary next to the code that
validates it (`clahe.COLOR_MODES`, `white_balance.METHODS`,
`saturation.DESATURATE_METHODS`, `super_resolution.METHODS`,
`aspect_ratio.INTERPOLATIONS`, `fisheye_correction.BORDER_MODES`), and one
`choices_for(spec)` in `src/gui/widgets.py` narrows per filter for both front
ends - replacing the dashboard's private copy.

**Regression test.** `test_every_offered_choice_is_one_the_filter_accepts`
walks every filter against every value the panel offers it. I had found one
pair by hand; the test found all six.

## Defect 2 - JPEG ghost does not detect JPEG ghosts (OPEN)

| Image | Outlier blocks |
|---|---|
| Ground-truth splice (Q55 region in a Q95 frame) | 43.0% |
| Untouched control (same frame, Q95) | 42.4% |
| Extreme splice (Q25 region, 300x200, in a Q95 frame) | 41.1% |

No discrimination. On the extreme splice exactly **one** block matched Q<=60,
at (32, 144) - nowhere near the splice at x150-450, y100-300.

**Cause.** The per-block difference curve falls monotonically as recompression
quality rises, so a global `argmin` over it lands on Q95 or Q100 for nearly
every block. A ghost is a *local dip* at the region's prior quality; the global
minimum of a decreasing curve cannot see it. Hence the bimodal 95/100 histogram
and a 40%+ outlier rate on a clean image - that is the noise floor, not
evidence.

**Fix needed.** Detect the dip rather than the global minimum. Real
algorithmic work, scheduled for hour 2.

## Lower severity

- `undistort` raises a raw `TypeError` from `os.PathLike` instead of a clear
  message when the calibration path is missing
- `auto_perspective` and `clone_detect` return the input unchanged when they
  find nothing, which in a forensic tool reads the same as having done nothing
- The Nikon reference file trips `thumbnail_mismatch`. Worth confirming against
  a downscaled original before trusting it - a candidate false positive in a
  check added two commits ago

## Harness bugs fixed this hour

- Correct behaviour counted as failure (identity at defaults, clean refusals)
- `ela` and `ghost` are each both a chain filter and a report, and the report
  overwrote the filter's result file. Reports are now `<name>-report.md`

## Next

1. Fix the ghost algorithm, validate against `ground_truth/quality_splice.jpg`
2. Begin the 20-minute deep dives: CLAHE, levels, denoise, sharpen, deblur,
   super-resolution
