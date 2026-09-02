# Validation against degraded footage

The unit tests prove each filter computes what it says. They cannot say whether
a filter's **defaults help** on the material this toolkit exists for, because a
clean synthetic chart is not a night-time DVR frame.

This is the harness that answers that, and the results it currently produces.
The table at the bottom is generated; the narrative around it is not, so
regenerate into a scratch file and fold the numbers in rather than overwriting
this page.

```bash
python scripts/validate_filters.py
python scripts/validate_filters.py --presets night_ir --filters clahe,nl_means
python scripts/validate_filters.py --output results.md --save-degraded gallery/degraded/
```

## What this establishes, and what it does not

The degradation is **simulated**, so read the results accordingly.

`cv_tools/validation/degrade.py` reproduces the *mechanisms* of real CCTV
degradation, with the physics written into each function: Poisson shot noise
that scales with the signal, so shadows are proportionally noisier than
highlights; light lost at the lens *before* the sensor reads it, so night noise
is generated against the few photons that arrived; 8×8 transform quantisation
using JPEG's Annex K table, so coarseness grows toward high frequencies as it
does in a real codec; IR illumination that falls off from the centre because
the camera lights the scene itself.

A filter that fails here would certainly fail on real footage. But **agreement
here does not establish that a filter's defaults are right on any particular
recorder**, whose encoder, denoiser and sharpener are proprietary and applied
before anything reaches a file. Real footage remains the only thing that
settles that. The harness is built so a labelled corpus drops straight in: any
clean/degraded pair works, and nothing in `benchmark.py` knows the degradation
was simulated.

Two known gaps in the model:

- **No motion compensation.** A P-frame that referenced a badly coded
  neighbour smears in a way `block_compression` has no equivalent for.
- **No H.264.** `codec_generations` encodes through OpenCV's own writers, and
  headless builds usually lack an H.264 encoder, so it falls back to MPEG-4
  Part 2 or MJPEG. Less of a compromise than it sounds — a large part of the
  installed DVR base records exactly those — but it is not H.264.

## Reading the metrics

PSNR and SSIM measure **fidelity to the reference**. That is the right question
for a denoiser and the wrong one for enhancement: CLAHE changes the tonal
distribution deliberately, so it will usually *lose* PSNR while making a plate
readable. A no-reference sharpness measure (variance of the Laplacian) sits
alongside for exactly that reason, and it rises with genuine detail and with
amplified noise equally.

So the numbers below are a screen, not a verdict. What the harness is really
for is catching the case nobody looks for — a filter whose defaults make things
**quantifiably worse** on the material it was written for.

## Findings

### 1. Measuring a dark frame measures its exposure, not its noise

On the three dark presets, every denoiser scored about **+0.01 dB** — which
reads as "denoising does nothing". It does not. On a frame 15 dB from its
reference because it is underexposed, the exposure error dominates the metric
and hides everything else.

Correct the exposure first and the *same denoiser on the same frame* shows its
real effect:

| Preset | Denoiser | Denoise only | Exposure corrected first |
|---|---|---:|---:|
| `low_light_colour` | `gaussian_blur` | +0.01 dB | **+1.34 dB** |
| `low_light_colour` | `nl_means` | −0.06 dB | **+1.22 dB** |
| `night_ir` | `gaussian_blur` | +0.01 dB | **+1.02 dB** |
| `night_ir` | `bilateral_filter` | +0.01 dB | **+0.75 dB** |
| `motion_night` | `nl_means` | −0.04 dB | **+0.44 dB** |

A hundred-fold difference in apparent effect, from ordering alone. Any
benchmark of denoisers on dark footage that skips this step is measuring the
wrong thing.

### 2. Enhancement filters help bad footage and harm decent footage

The sign of the effect flips with how degraded the input is:

| Filter | On `night_ir` (bad) | On `daytime_dvr` (decent) |
|---|---:|---:|
| `auto_contrast` | **+8.79 dB** | **−9.82 dB** |
| `clahe` | +1.42 dB | −9.93 dB |
| `histeq` | −10.37 dB | −24.66 dB |

`auto_contrast` is the single best first move on underexposed footage
(+9.08 dB on `low_light_colour`) and among the most destructive things you can
do to footage that was already exposed correctly. There is no globally good
default here, which is an argument for the toolkit's chain-and-preview design
rather than an auto button.

`histeq` loses PSNR under every condition tested while raising the sharpness
measure up to **48×** — the clearest illustration in the table of why acutance
alone must never be read as improvement.

### 3. Filter order depends on the degradation, and the metrics disagree

Denoise-then-contrast versus contrast-then-denoise, best of each pair:

| Preset | PSNR prefers | SSIM prefers |
|---|---|---|
| `low_light_colour` | contrast first (+4.21 dB) | contrast first |
| `night_ir` | contrast first (+4.32 dB) | contrast first |
| `daytime_dvr` | contrast first (+3.01 dB) | contrast first |
| `motion_night` | **denoise first** (+2.00 dB) | **contrast first** |

The README's "denoise, enhance contrast, then sharpen" is sound general advice
and is not a rule: on three of four presets the opposite order measured better,
and on the fourth the two metrics contradict each other. Sweep it rather than
assume it.

### 4. `auto_contrast` and `auto_levels` coincide at their defaults

They scored identically on every degradation. Not a duplicate registry entry —
different functions in different modules with different signatures — but at
their defaults (`cutoff=0.0`, `per_channel=False`) both perform a full-range
luma stretch, agreeing to within one 8-bit level. They diverge as soon as
either parameter is set. Worth knowing before reaching for both.

## Degradation presets

| Preset | Chain | PSNR | SSIM |
|---|---|---:|---:|
| `daytime_dvr` | resolution loss → sensor noise → blocking | 33.74 | 0.743 |
| `interlaced_sd` | resolution loss → interlace → blocking | 33.91 | 0.773 |
| `exported_evidence` | resolution loss → sensor noise → 3 codec generations | 27.43 | 0.501 |
| `motion_night` | low light → motion blur → blocking | 16.25 | 0.524 |
| `night_ir` | IR night → resolution loss → blocking | 16.19 | 0.485 |
| `low_light_colour` | low light → resolution loss → blocking | 15.12 | 0.427 |

Stages are applied in physical order: light is lost at the lens, noise is added
at the sensor, blur happens during the exposure, and only then does the
recorder scale and encode.

## Full results

17 repair filters × 6 degradation presets = 102 measurements, ground truth
`samples/cctv_dark.png`, seed 7. Analysis filters (ELA, FFT, edge maps) are
excluded: they return a diagnostic rather than an improved image, so fidelity
to the original is meaningless for them. Geometric filters are excluded because
they need coordinates a sweep cannot invent.

| Filter | Degradation | PSNR dB | ΔPSNR | SSIM | ΔSSIM | Sharpness × |
|---|---|---:|---:|---:|---:|---:|
| `auto_contrast` | low_light_colour | 24.21 | +9.08 | 0.568 | +0.141 | 38.35 |
| `auto_levels` | low_light_colour | 24.21 | +9.08 | 0.568 | +0.141 | 38.35 |
| `auto_contrast` | night_ir | 24.98 | +8.79 | 0.628 | +0.143 | 8.79 |
| `auto_levels` | night_ir | 24.98 | +8.79 | 0.628 | +0.143 | 8.79 |
| `auto_contrast` | motion_night | 20.12 | +3.88 | 0.638 | +0.115 | 29.36 |
| `auto_levels` | motion_night | 20.12 | +3.88 | 0.638 | +0.115 | 29.36 |
| `bilateral_filter` | exported_evidence | 29.86 | +2.42 | 0.772 | +0.271 | 0.02 |
| `gaussian_blur` | exported_evidence | 29.66 | +2.22 | 0.771 | +0.270 | 0.00 |
| `median_filter` | exported_evidence | 29.43 | +1.99 | 0.729 | +0.228 | 0.04 |
| `nl_means` | exported_evidence | 29.30 | +1.86 | 0.775 | +0.274 | 0.01 |
| `nl_means_auto` | exported_evidence | 29.10 | +1.67 | 0.769 | +0.268 | 0.00 |
| `clahe` | low_light_colour | 16.71 | +1.59 | 0.526 | +0.099 | 3.78 |
| `clahe` | motion_night | 17.67 | +1.42 | 0.591 | +0.068 | 3.13 |
| `clahe` | night_ir | 17.60 | +1.42 | 0.554 | +0.068 | 2.01 |
| `bilateral_filter` | daytime_dvr | 34.53 | +0.79 | 0.778 | +0.035 | 0.17 |
| `nl_means` | daytime_dvr | 34.38 | +0.64 | 0.780 | +0.037 | 0.08 |
| `median_filter` | daytime_dvr | 34.12 | +0.38 | 0.762 | +0.019 | 0.46 |
| `gaussian_blur` | daytime_dvr | 33.99 | +0.26 | 0.775 | +0.032 | 0.08 |
| `deblock` | exported_evidence | 27.66 | +0.23 | 0.547 | +0.046 | 0.76 |
| `deblock` | daytime_dvr | 33.88 | +0.14 | 0.754 | +0.011 | 0.63 |
| `bilateral_filter` | interlaced_sd | 34.02 | +0.11 | 0.777 | +0.004 | 0.34 |
| `nl_means` | interlaced_sd | 33.99 | +0.08 | 0.777 | +0.004 | 0.21 |
| `sharpen_laplacian` | low_light_colour | 15.20 | +0.07 | 0.343 | -0.084 | 89.27 |
| `median_filter` | interlaced_sd | 33.96 | +0.05 | 0.774 | +0.001 | 0.66 |
| `local_contrast` | motion_night | 16.27 | +0.02 | 0.516 | -0.007 | 2.21 |
| `gaussian_blur` | motion_night | 16.26 | +0.01 | 0.528 | +0.004 | 0.20 |
| `bilateral_filter` | motion_night | 16.26 | +0.01 | 0.528 | +0.004 | 0.22 |
| `gaussian_blur` | low_light_colour | 15.13 | +0.01 | 0.433 | +0.006 | 0.21 |
| `bilateral_filter` | low_light_colour | 15.13 | +0.01 | 0.433 | +0.006 | 0.21 |
| `sharpen_laplacian` | motion_night | 16.26 | +0.01 | 0.451 | -0.073 | 107.82 |
| `deblock` | interlaced_sd | 33.92 | +0.01 | 0.774 | +0.000 | 1.01 |
| `bilateral_filter` | night_ir | 16.19 | +0.01 | 0.501 | +0.016 | 0.06 |
| `gaussian_blur` | night_ir | 16.19 | +0.01 | 0.501 | +0.015 | 0.05 |
| `median_filter` | night_ir | 16.19 | +0.00 | 0.488 | +0.002 | 0.92 |
| `sharpen` | motion_night | 16.25 | +0.00 | 0.520 | -0.004 | 3.29 |
| `local_contrast` | low_light_colour | 15.13 | +0.00 | 0.415 | -0.011 | 2.13 |
| `sharpen` | low_light_colour | 15.13 | +0.00 | 0.422 | -0.005 | 3.26 |
| `median_filter` | motion_night | 16.25 | +0.00 | 0.524 | +0.000 | 0.98 |
| `white_balance` | night_ir | 16.19 | +0.00 | 0.485 | +0.000 | 1.00 |
| `median_filter` | low_light_colour | 15.12 | -0.00 | 0.428 | +0.001 | 0.94 |
| `nl_means_auto` | night_ir | 16.18 | -0.00 | 0.485 | +0.000 | 1.01 |
| `deblock` | motion_night | 16.24 | -0.01 | 0.524 | +0.000 | 0.78 |
| `white_balance` | low_light_colour | 15.12 | -0.01 | 0.426 | -0.000 | 0.98 |
| `nl_means` | night_ir | 16.18 | -0.01 | 0.502 | +0.017 | 0.06 |
| `white_balance` | motion_night | 16.24 | -0.01 | 0.523 | -0.000 | 0.99 |
| `sharpen` | night_ir | 16.18 | -0.01 | 0.470 | -0.015 | 3.34 |
| `deblock` | low_light_colour | 15.11 | -0.01 | 0.427 | +0.000 | 0.70 |
| `nl_means_auto` | motion_night | 16.23 | -0.01 | 0.523 | -0.001 | 0.97 |
| `deblock` | night_ir | 16.17 | -0.02 | 0.487 | +0.001 | 0.69 |
| `detail_enhance` | motion_night | 16.22 | -0.03 | 0.488 | -0.036 | 10.15 |
| `nl_means_auto` | low_light_colour | 15.09 | -0.03 | 0.424 | -0.003 | 0.94 |
| `local_contrast` | night_ir | 16.15 | -0.03 | 0.460 | -0.025 | 2.25 |
| `multiscale_detail` | motion_night | 16.21 | -0.04 | 0.511 | -0.013 | 2.20 |
| `nl_means` | motion_night | 16.21 | -0.04 | 0.526 | +0.002 | 0.23 |
| `multiscale_detail` | low_light_colour | 15.06 | -0.06 | 0.409 | -0.018 | 2.15 |
| `texture_boost` | low_light_colour | 15.06 | -0.06 | 0.414 | -0.013 | 2.10 |
| `nl_means` | low_light_colour | 15.06 | -0.06 | 0.427 | -0.000 | 0.20 |
| `white_balance` | interlaced_sd | 33.85 | -0.06 | 0.773 | -0.000 | 0.98 |
| `nl_means_auto` | daytime_dvr | 33.66 | -0.08 | 0.745 | +0.002 | 1.00 |
| `nl_means_auto` | interlaced_sd | 33.83 | -0.08 | 0.774 | +0.000 | 0.99 |
| `multiscale_detail` | night_ir | 16.10 | -0.08 | 0.457 | -0.029 | 2.26 |
| `texture_boost` | motion_night | 16.15 | -0.09 | 0.512 | -0.012 | 2.18 |
| `white_balance` | exported_evidence | 27.34 | -0.10 | 0.500 | -0.001 | 1.01 |
| `detail_enhance` | low_light_colour | 15.03 | -0.10 | 0.373 | -0.054 | 9.89 |
| `texture_boost` | night_ir | 16.07 | -0.12 | 0.459 | -0.026 | 2.10 |
| `gaussian_blur` | interlaced_sd | 33.79 | -0.12 | 0.775 | +0.002 | 0.10 |
| `sharpen_laplacian` | night_ir | 16.06 | -0.13 | 0.381 | -0.104 | 89.73 |
| `detail_enhance` | night_ir | 15.97 | -0.22 | 0.412 | -0.073 | 9.11 |
| `sharpen` | interlaced_sd | 33.68 | -0.23 | 0.767 | -0.006 | 3.44 |
| `white_balance` | daytime_dvr | 33.49 | -0.25 | 0.743 | +0.000 | 0.99 |
| `texture_boost` | interlaced_sd | 33.56 | -0.35 | 0.766 | -0.008 | 2.11 |
| `sharpen` | daytime_dvr | 32.74 | -1.00 | 0.695 | -0.048 | 3.25 |
| `texture_boost` | daytime_dvr | 32.56 | -1.18 | 0.695 | -0.047 | 2.12 |
| `multiscale_detail` | interlaced_sd | 32.36 | -1.55 | 0.765 | -0.009 | 2.28 |
| `texture_boost` | exported_evidence | 25.73 | -1.71 | 0.380 | -0.122 | 1.92 |
| `local_contrast` | interlaced_sd | 31.98 | -1.93 | 0.763 | -0.010 | 2.31 |
| `multiscale_detail` | daytime_dvr | 31.57 | -2.16 | 0.695 | -0.048 | 2.21 |
| `multiscale_detail` | exported_evidence | 25.10 | -2.33 | 0.352 | -0.149 | 2.25 |
| `local_contrast` | exported_evidence | 25.10 | -2.34 | 0.352 | -0.150 | 2.25 |
| `local_contrast` | daytime_dvr | 31.27 | -2.47 | 0.692 | -0.051 | 2.22 |
| `sharpen` | exported_evidence | 24.10 | -3.33 | 0.275 | -0.227 | 3.86 |
| `detail_enhance` | interlaced_sd | 30.31 | -3.60 | 0.728 | -0.045 | 6.85 |
| `auto_contrast` | exported_evidence | 22.78 | -4.65 | 0.359 | -0.143 | 2.15 |
| `auto_levels` | exported_evidence | 22.78 | -4.65 | 0.359 | -0.143 | 2.15 |
| `clahe` | interlaced_sd | 28.74 | -5.17 | 0.753 | -0.020 | 2.50 |
| `sharpen_laplacian` | interlaced_sd | 28.06 | -5.85 | 0.636 | -0.138 | 109.16 |
| `detail_enhance` | daytime_dvr | 27.69 | -6.05 | 0.522 | -0.221 | 9.10 |
| `detail_enhance` | exported_evidence | 20.45 | -6.98 | 0.148 | -0.353 | 9.00 |
| `histeq` | low_light_colour | 7.60 | -7.52 | 0.277 | -0.150 | 356.34 |
| `clahe` | exported_evidence | 19.49 | -7.94 | 0.172 | -0.329 | 6.92 |
| `histeq` | motion_night | 7.38 | -8.86 | 0.387 | -0.136 | 348.67 |
| `auto_contrast` | daytime_dvr | 23.92 | -9.82 | 0.653 | -0.090 | 3.01 |
| `auto_levels` | daytime_dvr | 23.92 | -9.82 | 0.653 | -0.090 | 3.01 |
| `clahe` | daytime_dvr | 23.80 | -9.93 | 0.534 | -0.209 | 6.94 |
| `histeq` | night_ir | 5.82 | -10.37 | 0.380 | -0.106 | 139.24 |
| `sharpen_laplacian` | daytime_dvr | 23.34 | -10.40 | 0.289 | -0.454 | 93.57 |
| `auto_contrast` | interlaced_sd | 23.30 | -10.61 | 0.725 | -0.048 | 3.39 |
| `auto_levels` | interlaced_sd | 23.30 | -10.61 | 0.725 | -0.048 | 3.39 |
| `sharpen_laplacian` | exported_evidence | 12.80 | -14.64 | 0.036 | -0.465 | 51.95 |
| `histeq` | exported_evidence | 9.08 | -18.36 | 0.098 | -0.404 | 25.46 |
| `histeq` | daytime_dvr | 9.07 | -24.66 | 0.284 | -0.459 | 48.01 |
| `histeq` | interlaced_sd | 8.63 | -25.28 | 0.521 | -0.252 | 29.51 |

## What would close the gap

A labelled corpus of real footage with a known clean reference — which in
practice means footage of a scene recorded simultaneously by a good camera and
a bad one, or a recorder whose raw and encoded outputs are both available.
Failing that, real footage without a reference still supports no-reference
measures and expert ranking, which is weaker but not nothing.

Until then the honest claim is: the arithmetic is verified, the defaults are
screened against a physically-motivated model of degradation, and no filter in
the repair set fails outright on degraded or monochrome input.
