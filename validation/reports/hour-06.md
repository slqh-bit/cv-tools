# Hour 6 - undistort proved against ground truth, and the ghost's operating window

**2026-08-20** | 73 entries, 0 needing attention | 741 tests | 21 filters with specific checks

Two items carried since hour 4 are closed, and the ghost's usable range is now
measured rather than assumed.

## undistort, end to end, against something known to be straight

Carried twice as "never exercised". The 13 chessboard views in the corpus now
drive the whole pipeline: calibrate, save, reload, correct.

    reprojection error   0.4087 px over 13 views
    distortion           k1=-0.2651  k2=-0.0467
    chessboard located   13/13 views

The measurement that matters uses ground truth rather than a proxy. A
chessboard row is straight *in the world*, so after correction its detected
corners must be collinear:

| | mean row bow | worst |
|---|---|---|
| before | 3.56 px | 5.34 px |
| after | **0.56 px** | 1.08 px |

Improved on **13 of 13 views**, an 84% reduction. The saved calibration
reloads unchanged and `undistort_with_file` - the path a preset replays -
matches the direct library call exactly.

**A note on metrics.** `estimate_straightness`, the proxy the fisheye module
uses, improved on only 7 of those 13 views while the corner geometry improved
on all 13. It is content-dependent and not a reliable measure of whether a
correction worked. The check uses corner collinearity instead.

## The ghost has a narrow operating window, and it is not where I assumed

Both operating points so far were measured on Q55 pasted into Q95. Sweeping
the inner quality over 26 frames, against a Q95 frame:

| inner quality | gap | detected | recovered |
|---|---|---|---|
| 40 | 55 | 3/26 | 60, 65 (wrong) |
| **55** | **40** | **14/26** | 50, 55, 60 |
| 70 | 25 | 1/26 | 60 |
| 80 | 15 | 0/26 | - |
| 88 | 7 | 1/26 | 60 |
| 92 | 3 | 2/26 | 60 |

Detection peaks at a 40-point gap and falls away on **both** sides. A narrow
gap is unsurprising - the dip is shallow. A *wider* gap being worse is not, and
the cause is structural: `DEFAULT_QUALITIES` sweeps 50 to 100, so a region
saved at Q40 has its dip below the bottom of the range and cannot be found
there. Worse, the filter names a wrong quality rather than none.

## Widening the sweep is not free

The obvious fix is to sweep lower. It works for the low end and breaks the
middle:

| inner quality | 50-100 sweep | 30-100 sweep |
|---|---|---|
| 35 | 4/26 | **16/26** |
| 40 | 3/26 | **11/26** |
| 55 | **14/26** | **0/26** |
| 70 | 1/26 | 3/26 |

`ghost_sweep` normalises each block's curve across whatever range it is given.
Adding steps at the bottom, where differences are large, rescales the whole
curve and flattens the dips at the top - Q55 stops being detectable at all.

**The threshold belongs to the sweep.** A caller who changes `qualities`
silently invalidates the calibration. The report now carries
`calibrated_sweep`, and the rendered output raises a flagged line when the
range is not the one the threshold was measured against. Both limits - the
sweep range and the quality gap - are in the module beside the constant, with
the tables above.

No default was changed. Reaching lower would cost more than it buys at this
threshold, and choosing a different trade is a decision with numbers attached
rather than a guess.

## Outstanding

1. The dashboard has no guided point picking - carried from hour 5
2. `samples/jpeg_ghost.png` was built for the old contract and nothing
   exercises it now
3. A sweep-range-invariant statistic would let one threshold cover Q35 to Q70.
   The normalisation is what ties them together; a per-quality normalisation
   against the frame's own distribution might not
4. Every ghost measurement so far pastes *from the same frame*. A paste from a
   different scene is the realistic case and may behave differently, since the
   texture mismatch that produced the false positives would then be genuine
