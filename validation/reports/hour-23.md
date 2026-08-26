# Hour 23 - super-resolution, and a report that contradicted its own filter

**2026-08-21** | 76 entries, 0 needing attention | 772 tests | 301 assertions

Hour 22 left `super_resolve` and `nl_means_denoise_frames` unreachable from the
CLI and asked whether wiring them up was worth doing. Measuring first turned
out to be the right order: one of them has a defect, and the honest numbers
change what exposing it would be promising.

## A report that green-lit what the reconstructor refuses

Given eight real CCTV snapshots, `super_resolve_report` said:

    usable: True
    frames_with_subpixel_motion: 6 of 8
    mean shift 112.58px, max 179.39px

`super_resolve`, handed the same frames, refused:

    Only the reference frame fell within max_shift (8.0px), so the result
    would be a plain upscale rather than a reconstruction.

The report's whole job is to answer "does this sequence carry the sub-pixel
motion reconstruction needs". It answered yes about frames its own
reconstructor rejects.

**The cause.** `usable` counted any frame whose shift had a *fractional part*
above 0.1. A displacement of 179.39px has one. Magnitude was never considered,
so a frame showing a different moment of the scene counted as evidence of finer
sampling.

**The fix.** The report now takes the same `max_shift` the reconstructor uses,
counts only frames within it, and reports `frames_within_max_shift` alongside
the threshold. Report and filter now agree in both directions.

While fixing it I made the threshold too lax - one sub-pixel frame instead of
two - and an existing test caught it immediately: four *identical* frames came
back usable, because the shift estimator returns small non-zero offsets
(0.096, -0.039) even for frames that are the same. One fractional reading is as
likely to be estimator noise as motion. The old threshold of two was right and
is kept.

That is the first time in this campaign an existing test caught a mistake of
mine before I did.

## What super-resolution is actually worth

Against a known original, reconstructing 2x from frames with ideal sub-pixel
offsets:

| frames | gain over bicubic |
|---|---|
| 2 | +0.24 dB |
| 4 | **+0.66 dB** |
| 8 | +0.33 dB |
| 16 | **−0.10 dB** |

It peaks at about four frames and then **gets worse**, because each additional
frame's registration error is smeared into the result. With sensor noise the
shape is the same (+0.76 dB at four).

Half a decibel is a real improvement and it is not what "super-resolution"
suggests to someone who has seen it on television. The numbers are now in the
filter reference, along with the fact that real CCTV snapshots seconds apart
are refused outright - it is a tool for a burst, not for a sequence of events.

## On not wiring it to the CLI

I did not expose `super_resolve` through `--frame-method` this hour. Given
what the measurements say, putting it beside `mean` and `median` would imply a
parity it does not have: those two work on any sequence of a still scene, this
one needs frames already aligned to within eight pixels and repays four of them
with half a decibel.

That is a judgement rather than a finding, and it is reversible - but it should
be made with the numbers visible, and until this hour they were not.

## Outstanding

1. 24 of 67 filters still have no specific checks
2. `nl_means_denoise_frames` remains unmeasured and unreachable. It is the
   more promising of the two for CCTV, since it wants temporal redundancy
   rather than sub-pixel offsets
3. `estimate_shifts` recovers roughly half the true offset in my synthetic
   tests - applied 0.25px in low-res terms, estimated 0.14. Whether that
   limits the reconstruction gain above is untested, and it would explain the
   peak at four frames
4. The raw loader path still has no test
