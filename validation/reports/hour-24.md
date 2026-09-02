# Hour 24 - a hypothesis, a measurement, and a fix that stopped the harm

**2026-08-21** | 76 entries, 0 needing attention | 774 tests | 301 assertions

Hour 23 ended with a suspicion rather than a finding: `estimate_shifts`
recovered roughly half the true offset in one synthetic test, and that might
explain why super-resolution peaked at four frames and got worse after. This
hour tested it.

## The estimator is exact everywhere except where it matters

Measured against exactly known translations:

| applied | estimated | error |
|---|---|---|
| 1.00, 2.00, 3.00, 5.00 px | exact | **0.002 px** |
| 0.25 | 0.22 | 0.033 px |
| 0.75 | 0.78 | 0.030 px |
| **0.50** | **0.20** | **0.299 px** |
| **0.50, 0.50** | 0.21, 0.81 | **0.428 px** |

Integer offsets to two thousandths of a pixel. Quarter offsets to three
hundredths. **Half-pixel offsets wrong by a third of a pixel**, consistently,
pushed away from 0.5 towards 0.2 or 0.8.

That is peak-interpolation bias: `cv2.phaseCorrelate` locates the correlation
peak by fitting a curve to its immediate neighbours, which pulls towards whole
pixels and is worst exactly halfway between them.

**And half a pixel is what a 2x reconstruction wants.** The bias landed
precisely where it did the most damage.

## The comparison that decided the fix

scikit-image - already a dependency - refines the peak on an upsampled
correlation surface:

    mean error   ours 0.299 px    skimage 0.038 px
    worst error  ours 0.438 px    skimage 0.150 px

Exact at every half-pixel case where ours was worst.

## What it bought, and what it did not

| frames | before | after |
|---|---|---|
| 2 | +0.24 dB | +0.23 dB |
| 4 | **+0.66 dB** | +0.64 dB |
| 8 | +0.33 dB | **+0.56 dB** |
| 16 | **−0.10 dB** | **+0.55 dB** |

**The peak did not move.** Super-resolution is still worth about 0.6 dB, and
this campaign is not going to claim otherwise.

What changed is that it stopped actively harming. Sixteen frames used to score
below a plain bicubic upscale - a user who gathered more evidence got a worse
result for it, and nothing said so. Now more frames hold the gain instead of
eroding it.

`estimate_shifts` gained an `upsample` parameter, defaulting to 20, and falls
back to the plain peak fit if scikit-image is ever absent rather than failing.

## Two regression tests

Half-pixel offsets read back to within 0.1px, and twelve frames must not
reconstruct far worse than four - the second being the shape of the bug rather
than its symptom.

## What this hour is an example of

The suspicion came from a number I noticed in passing while measuring
something else, wrote down, and did not chase. Chasing it a day later took one
measurement to confirm, one comparison to fix, and produced a correctness
change in a filter that had passed every test it had.

Three of the last four defects this campaign has found came from a note in an
outstanding list rather than from a sweep. The sweeps keep the ground solid;
the noticing is what finds things.

## Outstanding

1. 24 of 67 filters still have no specific checks
2. `nl_means_denoise_frames` remains unmeasured and unreachable from the CLI
3. The 0.25px case still reads 0.10 with the refinement - worse than the old
   0.22. Bilinear interpolation is not an exact shift operator, so the "truth"
   at quarter offsets is itself questionable; establishing it properly needs a
   band-limited synthetic source
4. The raw loader path still has no test
