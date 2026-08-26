# Hour 3 - the backlog cleared, and the first deep dives

**2026-08-20** | 73 entries, 0 needing attention | 740 tests pass | 44 specific checks green

Hour 1 ended with 13 flagged entries. All 13 are resolved: 4 were real defects,
9 were the harness misreading correct behaviour.

## Documentation caught up with the code

`docs/filters.md` and `docs/filters.fr.md` still described the ghost contract
that hour 2 removed - per-block best-match quality, `dominant_quality`,
`outlier_count`. Both rewritten in both languages, PDFs regenerated (28 and 29
pages), and both carry a migration note naming the keys that no longer exist,
because a preset or report written before the fix records them.

## undistort: a clear message instead of a raw TypeError

A blank calibration field arrived as `None` and reached `open()`, which raised
`TypeError: expected str, bytes or os.PathLike object, not NoneType` - true,
and useless to anyone trying to work out what to supply.

    ValueError: undistort needs a calibration file. Produce one with
    calibrate_from_chessboard() over photos of a chessboard taken on this
    camera, then save it with save_calibration().

The harness now records those 40 runs as refusals rather than defects, which is
what they are.

## The Nikon thumbnail flag is a true positive

Hour 1 listed this as a suspected false positive: a real Nikon D80 file from
Wikimedia trips `thumbnail_mismatch`, and the file has been downscaled, so the
hash distance could plausibly have been an artefact.

It is not. Extracting the thumbnail and putting it beside the main image shows
the same cat in the same moment - but framed **wider**. The main image is a
tighter crop; the embedded thumbnail still carries the pre-crop framing, which
is exactly the contradiction the check exists to find. Hamming distance 29/64
against a threshold of 12, and `dimension_mismatch` fires independently on the
same file. Two checks agreeing on one conclusion: cropped after capture, and
the thumbnail was never regenerated.

Worth recording as a validated positive from a file nobody here constructed.

## Deep dives: 15 filters, 44 specific checks, all passing

Measured on the CCTV frames rather than asserted:

| filter | what was measured |
|---|---|
| `clahe` | local sigma 8.79 -> 11.34 on the darkest frame; monotonic in clip_limit; shadow noise stays under 3x; all five colour modes usable |
| `levels` | defaults an exact identity; every ramp value at or below the black point maps to 0, at or above white to 255; gamma orders correctly |
| `contrast_brightness` | +40 brightness moves the mean by +37.4, the rest lost to clipping |
| `curves` | a straight line is the identity; `lift_shadows` raises sub-64 pixels; the preset stays monotonic across the ramp |
| `histeq` | widens the 1-99 percentile span; noise rises, which is why CLAHE exists |
| `sharpen` | Laplacian variance up on the softest frame, monotonic in amount, under 15% clipping at amount 2.5 |
| `nl_means` | noise sigma down, edge density retained above 40%, monotonic in h |
| `local_contrast` | local sigma up at 31px, monotonic in strength, no clipping at full strength |
| `upscale` | exact output dimensions at 2x and 3x; a round trip returns within 4/255 |
| `deblur_motion` | high-frequency energy up on a genuinely blurred plate; a wrong PSF still changes the image rather than passing it through |
| `deblur_defocus` | high-frequency energy up on defocused text across radius 3-12 |
| `perspective` | a grid warped from known corners comes back straight |
| `barrel` | the inverse of a known k1 straightens the grid |
| `redact` | fill and noise leave no residual correlation; blur and pixelate correctly reported as not safe; nothing outside the box changes |
| `clone_detect` | finds the exact shift the corpus applied; silent on the untouched control |
| `ghost` | recovers Q55 for a named Q55 paste; quiet on the same region of an untouched frame; claims nothing without a region |

Two of my own checks were wrong and are fixed: `local_contrast` was called with
an `amount` argument it does not take (it takes `radius` and `strength`), and
the `ghost` check still read the pre-rewrite keys.

## Harness: correct behaviour stopped counting as failure

Nine of the 13 flagged entries were filters whose defaults are a documented
identity - `levels`, `contrast_brightness`, `temperature`, `color_balance`,
`cmyk`, `channel_mixer`, `pixel_aspect` - plus `auto_perspective` and
`clone_detect`, which return the input when they find nothing.

The harness now holds that list with a reason for each, and the result file
says so in words rather than leaving an unexplained pass. This is the third
harness correction of the campaign; each one was the harness being wrong about
the code, which is the failure mode worth watching in a tool like this.

## Outstanding

1. `auto_perspective` and `clone_detect` still return the input silently when
   they find nothing. Recorded rather than fixed: in a forensic tool "found
   nothing" and "did nothing" should not look identical, but changing a filter's
   return contract needs its own decision
2. The dashboard has no equivalent of the desktop viewer's guided point
   picking; its tap-to-pick collects loose coordinates
3. Deep dives remain for the geometry and colour families - `fisheye`,
   `undistort`, `white_balance`, `saturation`, `component`, `measure_3d`
4. The ghost threshold is calibrated on one camera. A second camera would tell
   us whether 0.10 travels
