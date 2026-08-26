# Hour 2 - JPEG ghost: diagnosed, rebuilt, and cut back to what it can prove

**2026-08-20** | 733 tests pass | one filter rewritten, one wrong fix discarded

This hour went entirely to the defect hour 1 opened. It took three attempts,
two of which were wrong, and the wrong ones are written up here because the
second nearly shipped.

## The diagnosis

`ghost_map` and `ghost_report` took `np.argmin` over each block's difference
curve across the recompression sweep. A block's curve falls monotonically as
quality rises - recompressing at Q100 barely changes anything - so the global
minimum lands on the top of the sweep for almost every block, whatever the
block's history.

Measured on a block inside a known Q55 paste:

| quality | 50 | 55 | 60 | 65 | 70 | 75 | 80 | 85 | 90 | 95 | 100 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| difference | 77.6 | 60.5 | 51.3 | 42.9 | 37.1 | 29.4 | 22.3 | 15.5 | 8.5 | 3.4 | **0.7** |

Strictly decreasing, no dip at 55, `argmin` returns 100. That is why a clean
frame reported 42% "outlier" blocks: the outlier count was every block whose
argmin differed from the mode, and the mode is an artefact of the slope.

Two hypotheses ruled out along the way:

- **The documented blind spot.** The module docstring says a uniform resave of
  the whole composite hides the ghost, and hour 1's ground truth did resave at
  Q95. So I rebuilt the test as a PNG composite of JPEG sources - the case the
  filter is explicitly *for*. It failed there too: pasted region median Q100,
  same as its surroundings.
- **JPEG grid alignment.** Pasting at x=150 is off the 8x8 grid. Repeating at
  x=152, y=104 (both multiples of 8) changed nothing material: still no dip at
  55, still argmin 100.

## What actually works

The evidence is in the *sweep*, not in a collapse of it. Normalising each
block's curve to 0-1 and comparing a region against the rest of the frame, per
quality:

| | Q50 | **Q55** | Q60 | Q65 | Q70 | Q95 |
|---|---|---|---|---|---|---|
| forged (Q55 paste) | -0.179 | **-0.342** | -0.096 | +0.069 | +0.211 | +0.079 |
| untouched control | -0.001 | -0.012 | +0.001 | -0.006 | -0.022 | +0.001 |

The region goes darkest at exactly the quality it was saved at, with 15x the
separation the control produces anywhere. The information was always there;
`argmin` was throwing it away.

## The wrong fix, and why it was discarded

First attempt: search for the ghost automatically - take the most coherent
dark cluster in each frame, score it against the rest, pick the best. Against
the single ground-truth pair it looked excellent: detected at Q55, region
x112-464/y64-320 against a truth of x152-448/y104-304.

Then I calibrated it across 18 real CCTV frames, and it inverted:

| | mean separation | worst |
|---|---|---|
| untouched frames | **-0.526** | -0.624 |
| same frames, genuine Q55 paste | **-0.439** | -0.401 |

Clean frames separate *more strongly* than forged ones. No threshold exists -
at 0.40 it detects 100% of forgeries and 100% of the clean frames too. The
statistic was measuring texture homogeneity: a flat wall or ceiling forms a
large coherent cluster at some quality in every frame, and that swamps the
compression signal. The single-pair result held only because the region had
been handed to it.

Discarded. A detector that fires on every untouched frame is worse than one
that admits it cannot search.

## What shipped

`ghost_report(image, region=(x, y, w, h))` - the region is named, not searched
for. Validated across 12 real CCTV frames with a Q55 paste:

- **10 of 12** forgeries detected, recovering Q50-55 against a Q55 truth
- **2 of 12** untouched frames called positive

Both numbers are in the filter's caveat, so they travel with every report the
CLI, GUI and dashboard print. Without a region the report says what it cannot
do instead of guessing.

Also added:

- `ghost_sweep()` - the normalised sweep, exposed as the honest primitive.
  This is the form the technique is described in and the form worth looking at
- `ghost_map()` now returns the sweep frame carrying the most structure - dark
  where the pixels match that quality - instead of an argmin collage
- 6 new tests replacing 3 that asserted the broken contract

This fits the desktop viewer's drag-to-select from hour 0: mark the region on
the frame, and the region is what the report interrogates.

## Honest limits

- 17% false positives on this sample. Usable as a pointer, not as a finding -
  which is what the caveat now says
- 12 frames from one camera is a thin calibration. The threshold (0.10) should
  be re-derived against a second camera before anyone leans on it
- Recovered quality lands within one sweep step of truth (50 or 55 for a Q55
  paste), so read it as a neighbourhood, not a number

## Outstanding

1. `docs/filters.md` and its French translation still describe the old
   per-block-quality contract. **Stale as of this commit** - first task of
   hour 3, with the PDFs regenerated
2. The hour-1 backlog is untouched: `undistort`'s raw `TypeError`,
   `auto_perspective`/`clone_detect` returning the input silently, the Nikon
   thumbnail false-positive candidate
3. The 20-minute deep dives have not started. Hour 2 bought one working
   forensic filter instead, which was the right trade
