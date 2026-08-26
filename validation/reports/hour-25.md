# Hour 25 - the automatic denoiser was making images worse

**2026-08-21** | 76 entries, 0 needing attention | 778 tests | 301 assertions

Two things: a loose end from my own change yesterday, and the largest
single-filter defect this campaign has found.

## Yesterday's caveat was itself a measurement error

Hour 24 refined `estimate_shifts` on an upsampled correlation surface, and I
recorded a worry: the quarter-pixel case got *worse*, 0.150 error against the
old 0.033. I noted the ground truth was suspect because `warpAffine`
interpolates.

It was. Bilinear interpolation is not an exact shift operator - it low-pass
filters asymmetrically, so an image it calls "shifted 0.25px" is not. A phase
ramp in the frequency domain is exact. Against that:

    peak fit alone      mean error 0.2324 px, worst 0.326 px
    upsampled by 20     mean error 0.0044 px, worst 0.030 px

Better at **every** offset from 0.1 to 2.5 pixels, by a factor of 53 on
average. The one residual - a true 0.33 reading as 0.30 - is the search grid,
which resolves to 1/20 of a pixel exactly as documented.

The test now uses the Fourier shift. A test built on interpolated ground truth
was measuring the interpolator as much as the estimator.

## nl_means_auto scored below doing nothing

Measuring `nl_means_denoise_frames` led here. `estimate_h` returned three times
the measured noise sigma, and the filter at that strength destroys the image:

| image | measured sigma | h chosen | result |
|---|---|---|---|
| CCTV frame | 10.3 | 30.8 | **−6.89 dB** |
| baboon | 13.0 | 39.0 | **−6.5 dB**, detail 3022 → 11 |
| smooth scene | 7.8 | 23.5 | +2.20 dB (best available: +7.12) |

`nl_means_denoise_auto` is the entry point that exists so a user does not have
to choose. It was returning images measurably worse than the ones handed to it.

The docstring already disagreed with the code: *"aggressiveness: Multiplier on
the measured sigma. Around 1 preserves detail"* - while the line below computed
`sigma * 3.0 * aggressiveness`.

## Choosing the number by measurement

Five images, two noise levels each, scored against the clean original:

| h / sigma | 0.4 | **0.6** | 0.8 | 1.0 | 1.6 | 3.0 |
|---|---|---|---|---|---|---|
| mean gain | +0.94 | **+2.23** | +2.16 | +1.69 | −0.44 | **−3.93** |
| worst case | −0.99 | **−1.85** | −4.26 | −6.59 | −9.41 | **−10.91** |

0.6 has both the best mean and the best worst case among the strengths that
help at all. It is now `H_PER_SIGMA`, with that table beside it.

Afterwards, on the three CCTV frames: **+1.27, +2.83, +3.75 dB** where the same
call previously lost about 6.9.

## What the same measurements say about the filter generally

Denoising is scene-dependent in a way the documentation did not admit. A smooth
wall gains 6 dB. A densely textured subject - fur, foliage, gravel - **loses at
every strength**, because its detail sits at the same scale as the noise. And
on a static sequence, averaging seven frames scores 36.9 dB where denoising one
of them scores 25.0.

All of that is now in the filter reference. A denoiser that helps some images
and harms others is worth having; one that does not say which is not.

## Three regression tests

Automatic denoising beats leaving the noise alone, the suggested strength stays
below 1.5x the measured sigma, and `aggressiveness` scales it linearly.

## Outstanding

1. 24 of 67 filters still have no specific checks
2. `nl_means_denoise_frames` is measured now and it is *worse* than plain
   frame averaging on a static scene - 24.9 dB against 36.9. Whether it earns
   its place at all is a question this hour raised and did not answer
3. `h_color` has the same scaling question and was not examined
4. The raw loader path still has no test
