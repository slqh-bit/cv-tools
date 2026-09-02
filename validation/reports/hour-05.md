# Hour 5 - the ghost's real accuracy, and a statistic that earns it

**2026-08-20** | 73 entries, 0 needing attention | 740 tests | threshold re-derived from 32 frames

Hour 4 left the ghost false-positive rate unmeasured on grid-aligned pastes.
Measuring it properly turned the hour into a rewrite of the detection
statistic, because the honest numbers were much worse than the per-camera
figures suggested.

## The per-camera numbers were flattering

Re-measuring with everything grid-aligned, 24 Hikview frames: **96% detected**,
up from 83%. Good. But false positives stayed at **17%**, and the worst
untouched region scored -0.150 - above the 0.10 threshold in force.

Pooling both camera families, 32 frames, is where it fell apart:

| | mean | worst |
|---|---|---|
| forged (Q55 paste) | -0.284 | -0.075 |
| untouched | -0.119 | **-0.364** |

The worst untouched region separated *more strongly than the average genuine
paste*. No threshold reached zero false positives; the rate plateaued at 25%
and stayed there however far the threshold was pushed.

Reporting 10-of-12 and 12-of-12 from single cameras, as hours 2 and 4 did, was
measuring too few frames to see this.

## Why, and the fix

A region that differs from the frame only in **texture** - a flat wall against
a busy desk - sits below the rest of the frame at *every* quality, by roughly
the same amount. A region with a different compression history dips at **one**
quality. The old statistic took the minimum separation and could not tell a
constant offset from a dip.

Subtracting the region's own average across the sweep cancels the offset and
leaves the dip. On the same 32 frames:

| threshold | detects | false positives |
|---|---|---|
| 0.20 | 84.4% | 9.4% |
| **0.25** | **59.4%** | **3.1%** |
| 0.27 | 46.9% | 0.0% |

Against the old statistic's best achievable operating point - 28% detection at
zero false positives - every one of these is better.

**0.25 is in force.** A false "this region has a different history" invites a
wrong conclusion; a miss only leaves the question open. All 19 frames that
fired at 0.25 named a quality within one sweep step of the truth. The constant
is one line if a different trade is wanted, and the table above is in the
module beside it.

Verified end to end after the change: 19/32 detected, 1/32 false positive,
recovered qualities 50-60 against a truth of 55.

## The report now shows the number the verdict rests on

`ghost_report` gained a `dip` field, and the rendered report shows both: the
dip that decided it, and the raw separation from the rest of the frame as an
informational line. An analyst can see a region that is merely flatter than its
surroundings for what it is.

## Filters that find nothing

Deferred in hours 3 and 4 as "a contract decision". Resolved, by deciding it
rather than changing it: `clone_detect` and `auto_perspective` returning the
input unchanged is the *right* contract for a chain step - an image in, an
image out, and a preset that replays identically. The ambiguity is real but
belongs to the viewer, not the filter, and the matching report already
distinguishes the cases explicitly.

Documented in both languages with a pointer to `--clone-stats`, PDFs rebuilt.
Closed.

## Harness

`harness.py ghost` was resolving to the report rather than the filter, so the
filter's deep dive silently kept a stale result file - which is how I nearly
read a threshold of -0.10 out of a run made after it changed to 0.25. A bare
name now means the filter when one exists; `ghost:report` asks for the other.

## Outstanding

1. The dashboard has no guided point picking
2. `undistort` still has no end-to-end exercise: 13 chessboard views are in
   the corpus and no calibration has been produced from them. Carried from
   hour 4
3. Both ghost operating points are measured on Q55 pastes into Q95 frames
   only. A quality gap that narrow is the easy case; Q80-into-Q95 would say
   how it degrades
4. The 2 fixtures in `samples/` built for the old ghost contract
   (`jpeg_ghost.png`) are no longer exercised by anything
