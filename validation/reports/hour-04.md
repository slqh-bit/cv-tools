# Hour 4 - a second camera, and what actually limits JPEG ghost

**2026-08-20** | 73 entries, 0 needing attention | 740 tests | 20 filters with specific checks

Two things this hour: the ghost threshold tested on cameras it was never
calibrated on, and deep dives across the geometry and colour families. The
first produced a correction to two earlier reports.

## The threshold travels. Grid alignment is what does not.

Hour 3 left this open: the 0.10 threshold was calibrated on one camera. Three
CALME site cameras (1920x1088, different scenes, different hardware) were
available as video in `ai cam/testbench`, so four frames were extracted from
each.

**First result, at a region of (400, 300, 600, 400):**

| | mean separation | detected |
|---|---|---|
| forged (Q55 paste) | -0.090 | 4/12 |
| untouched | -0.055 | - |

That reads as a failure to generalise, and I nearly wrote it up as one. The
clean frames' worst case (-0.109) was stronger than the forged mean.

**It was the paste offset.** `y=300` is not a multiple of 8:

| paste offset | on the 8x8 grid | forged mean | clean mean | detected |
|---|---|---|---|---|
| (400, 300) | no | -0.090 | -0.055 | 4/12 |
| **(400, 304)** | **yes** | **-0.300** | -0.056 | **12/12** |
| (402, 304) | no | -0.095 | -0.056 | 4/12 |
| **(400, 296)** | **yes** | **-0.178** | -0.055 | **12/12** |
| (404, 300) | no | -0.031 | -0.055 | 1/12 |

Aligned: 12 of 12 on cameras the threshold had never seen, at three times the
resolution it was derived at. Off by four pixels: 1 of 12, separating no more
than an untouched frame does.

This is a property of JPEG, not of this implementation. A region quantised on
one 8x8 grid and pasted onto a different one carries no recoverable
signature - the DCT blocks no longer line up with the ones being tested.

**Two earlier statements were wrong and are corrected:**

- Hour 2 concluded that grid alignment "changes nothing material". That was
  measured through the broken `argmin` statistic, where nothing changed
  anything. With a working statistic, alignment is the dominant variable.
- My own first result this hour, that the threshold does not generalise. It
  does. I had picked an off-grid offset.

The caveat now travels with every ghost report the CLI, GUI and dashboard
print, and sits beside the threshold in the module.

## Deep dives: geometry and colour

`component` - 26 checks, all passing: every channel of every colour space the
filter offers returns a usable plane, and bit planes 0 and 7 are genuinely
binary.

`fisheye` - straightens a grid distorted by a known k1; all three border modes
fill the corners.

`measure_3d` - the strongest available check is self-consistency, and it
holds exactly: a reference measured against itself returns **1800.00mm** against
a 1800mm reference. A shorter image height measures shorter (587 vs 1027mm),
and uncertainty grows from 14.7 to 132.0 mm/px as the object approaches the
horizon - the documentation's warning, measured rather than repeated.

`white_balance` - all three estimators reduce a deliberate 31.7-level blue
cast: gray_world to 0.5, shades_of_gray to 8.2, white_patch to 30.9.

`saturation` - factor 1.0 is *not* an exact identity. Measured: at most 2
levels, and a bare BGR->HSV->BGR round trip alone accounts for essentially all
of it (mean 0.277 of 0.289). Colour-space quantisation, not the scaling - but
worth knowing before chaining several saturation steps.

## What the dives found in the filters

**white_patch is unreliable on frames with blown highlights.** It normalises by
the brightest pixel per channel, so a clipped window drives it. On
`event_tamper.jpg`, 4.9% of which sits at 250 or above, it *increases* the
channel spread 3.1 -> 9.7 where gray_world gives 5.7. Recorded in the filter's
checks rather than treated as a fault: it is the known trade-off of the method,
and the frame is the case where it shows.

## Corrections to my own instruments

- The harness returned early for a filter it could not drive from its parameter
  matrix, skipping that filter's specific checks. `measure_3d` reported 0
  checks for that reason and now reports 4
- `horizon` was missing from the harness's required-value table, which is why
  `measure_3d` could not be driven at all
- Two of my new checks were wrong: `desaturate` returns a single-channel image
  and cannot be indexed on three, and `white_balance` was asked to reduce a
  cast on a frame that had almost none (spread 3.1)

That is the fourth hour in which the instruments needed more correction than
the code. Worth stating plainly: of the issues raised across four sweeps, the
ratio is roughly two harness errors to one product defect.

## Outstanding

1. `auto_perspective` and `clone_detect` still return the input silently when
   they find nothing - unchanged from hour 3, still a contract decision
2. The dashboard has no guided point picking
3. `undistort`'s calibration path cannot be exercised end to end: the corpus
   has 13 chessboard views but no calibration has been produced from them
4. Ghost's 2-in-12 false positive rate from hour 2 has not been re-measured
   with grid-aligned pastes. It may be lower than reported
