# Validation campaign - index

Run 2026-09-01T16:37:29 | Python 3.12.10 | OpenCV 4.14.0  
84 filters and reports, 2539 runs, 308 specific checks.

Corpus: 9 CCTV frames chosen by measurement from the 200 on this desk, published reference images with a known property, and forgeries built here from the CCTV frames so the answer is known. See `corpus/manifest.json`.

## Needs attention

| filter | runs | defects | checks | seconds | result |
|---|---|---|---|---|---|

## Clean

| filter | runs | checks | seconds | result |
|---|---|---|---|---|
| arrow | 9 | 0/0 | 0.2 | [result](results/arrow.md) |
| auto_canny | 45 | 0/0 | 0.2 | [result](results/auto_canny.md) |
| auto_contrast | 27 | 0/0 | 0.3 | [result](results/auto_contrast.md) |
| auto_levels | 18 | 3/3 | 0.3 | [result](results/auto_levels.md) |
| auto_perspective | 10 | 0/0 | 0.2 | [result](results/auto_perspective.md) |
| barrel | 90 | 1/1 | 2.5 | [result](results/barrel.md) |
| bilateral_filter | 45 | 5/5 | 0.8 | [result](results/bilateral_filter.md) |
| bit_plane | 9 | 9/9 | 0.2 | [result](results/bit_plane.md) |
| blocking_map | 27 | 0/0 | 0.7 | [result](results/blocking_map.md) |
| canny | 72 | 7/7 | 0.2 | [result](results/canny.md) |
| channel_mixer | 9 | 0/0 | 0.2 | [result](results/channel_mixer.md) |
| clahe | 45 | 16/16 | 0.7 | [result](results/clahe.md) |
| clahe_grid | 27 | 0/0 | 0.7 | [result](results/clahe_grid.md) |
| clone (report) | 8 | 0/0 | 4.4 | [result](results/clone-report.md) |
| clone_detect | 33 | 2/2 | 31.9 | [result](results/clone_detect.md) |
| cmyk | 9 | 0/0 | 0.2 | [result](results/cmyk.md) |
| color_balance | 18 | 0/0 | 0.6 | [result](results/color_balance.md) |
| component | 54 | 34/34 | 0.3 | [result](results/component.md) |
| compression (report) | 8 | 6/6 | 0.2 | [result](results/compression-report.md) |
| contrast_brightness | 63 | 8/8 | 1.2 | [result](results/contrast_brightness.md) |
| crop | 9 | 3/3 | 0.0 | [result](results/crop.md) |
| curves | 9 | 8/8 | 0.2 | [result](results/curves.md) |
| deblock | 27 | 1/1 | 0.5 | [result](results/deblock.md) |
| deblur_defocus | 50 | 1/1 | 10.5 | [result](results/deblur_defocus.md) |
| deblur_motion | 70 | 2/2 | 11.8 | [result](results/deblur_motion.md) |
| desaturate | 27 | 0/0 | 0.1 | [result](results/desaturate.md) |
| detail_enhance | 45 | 5/5 | 2.8 | [result](results/detail_enhance.md) |
| differential | 0 | 10/10 | 0.6 | [result](results/differential.md) |
| differential_denoise | 0 | 3/3 | 1.3 | [result](results/differential_denoise.md) |
| ela | 66 | 0/0 | 1.0 | [result](results/ela.md) |
| ela (report) | 8 | 3/3 | 0.2 | [result](results/ela-report.md) |
| fft_filter | 72 | 3/3 | 3.8 | [result](results/fft_filter.md) |
| fft_spectrum | 27 | 0/0 | 1.0 | [result](results/fft_spectrum.md) |
| fisheye | 70 | 4/4 | 1.8 | [result](results/fisheye.md) |
| fit_aspect | 45 | 0/0 | 0.4 | [result](results/fit_aspect.md) |
| flip | 27 | 4/4 | 0.3 | [result](results/flip.md) |
| gaussian_blur | 27 | 8/8 | 3.0 | [result](results/gaussian_blur.md) |
| ghost | 22 | 7/7 | 3.2 | [result](results/ghost.md) |
| ghost (report) | 8 | 7/7 | 1.3 | [result](results/ghost-report.md) |
| histeq | 27 | 7/7 | 0.5 | [result](results/histeq.md) |
| invert | 9 | 2/2 | 0.2 | [result](results/invert.md) |
| invert_channel | 9 | 4/4 | 0.0 | [result](results/invert_channel.md) |
| invert_luminance | 9 | 0/0 | 0.2 | [result](results/invert_luminance.md) |
| laplacian | 36 | 0/0 | 0.2 | [result](results/laplacian.md) |
| levels | 99 | 10/10 | 1.6 | [result](results/levels.md) |
| local_contrast | 45 | 11/11 | 4.3 | [result](results/local_contrast.md) |
| measure | 9 | 0/0 | 0.2 | [result](results/measure.md) |
| measure_3d | 27 | 4/4 | 0.3 | [result](results/measure_3d.md) |
| measure_area | 18 | 0/0 | 0.2 | [result](results/measure_area.md) |
| median_filter | 9 | 0/0 | 0.2 | [result](results/median_filter.md) |
| metadata (report) | 8 | 7/7 | 0.1 | [result](results/metadata-report.md) |
| multiscale_detail | 9 | 0/0 | 1.2 | [result](results/multiscale_detail.md) |
| nl_means | 27 | 6/6 | 17.9 | [result](results/nl_means.md) |
| nl_means_auto | 27 | 0/0 | 14.3 | [result](results/nl_means_auto.md) |
| noise (report) | 8 | 7/7 | 0.1 | [result](results/noise-report.md) |
| noise_map | 27 | 2/2 | 0.1 | [result](results/noise_map.md) |
| per_channel | 0 | 12/12 | 0.0 | [result](results/per_channel.md) |
| perspective | 33 | 2/2 | 0.4 | [result](results/perspective.md) |
| pixel_aspect | 54 | 5/5 | 0.6 | [result](results/pixel_aspect.md) |
| redact | 45 | 7/7 | 0.5 | [result](results/redact.md) |
| remove_periodic | 45 | 2/2 | 13.6 | [result](results/remove_periodic.md) |
| resize | 27 | 3/3 | 0.0 | [result](results/resize.md) |
| roi_crop | 9 | 2/2 | 0.0 | [result](results/roi_crop.md) |
| roi_draw | 36 | 0/0 | 0.3 | [result](results/roi_draw.md) |
| roi_filter | 9 | 0/0 | 0.2 | [result](results/roi_filter.md) |
| rotate | 45 | 5/5 | 0.7 | [result](results/rotate.md) |
| s_curve | 27 | 0/0 | 0.3 | [result](results/s_curve.md) |
| saturation | 27 | 16/16 | 0.5 | [result](results/saturation.md) |
| scale_bar | 45 | 0/0 | 0.4 | [result](results/scale_bar.md) |
| selective_saturation | 45 | 0/0 | 0.6 | [result](results/selective_saturation.md) |
| shape | 9 | 0/0 | 0.2 | [result](results/shape.md) |
| sharpen | 63 | 11/11 | 3.3 | [result](results/sharpen.md) |
| sharpen_laplacian | 27 | 0/0 | 0.5 | [result](results/sharpen_laplacian.md) |
| sobel | 18 | 0/0 | 0.2 | [result](results/sobel.md) |
| solarize | 27 | 3/3 | 0.3 | [result](results/solarize.md) |
| stain | 40 | 0/0 | 1.1 | [result](results/stain.md) |
| temperature | 45 | 3/3 | 0.6 | [result](results/temperature.md) |
| text | 18 | 0/0 | 0.2 | [result](results/text.md) |
| texture_boost | 36 | 3/3 | 1.0 | [result](results/texture_boost.md) |
| undistort | 40 | 6/6 | 0.4 | [result](results/undistort.md) |
| upscale | 50 | 3/3 | 6.5 | [result](results/upscale.md) |
| vibrance | 27 | 0/0 | 0.4 | [result](results/vibrance.md) |
| white_balance | 45 | 5/5 | 0.8 | [result](results/white_balance.md) |
| white_balance_patch | 9 | 0/0 | 0.2 | [result](results/white_balance_patch.md) |
