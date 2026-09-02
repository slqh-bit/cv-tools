# differential - validation result

**Checks spanning several filters**  
`validation.checks` | family: Cross-cutting | 2026-09-01T16:37:27

## Verdict

No runs - the filter could not be driven from the harness.

## What this filter specifically promises

- PASS - gaussian_blur at radius 2 matches scipy: correlation 0.99986, mean difference 0.58/255 against scipy.ndimage
- PASS - gaussian_blur at radius 5 matches scipy: correlation 0.99968, mean difference 0.71/255 against scipy.ndimage
- PASS - median_filter matches scipy: correlation 0.99998, mean difference 0.11/255, and 90.0% of interior pixels identical to scipy.ndimage
- PASS - the two libraries differ only at the frame border: including the border the agreement falls to 0.98801 from 0.99998 - OpenCV replicates the edge pixel, scipy reflects it
- PASS - levels gamma 0.5 matches skimage adjust_gamma: correlation 0.99996, mean difference 0.39/255 against skimage.exposure
- PASS - levels gamma 2 matches skimage adjust_gamma: correlation 0.99979, mean difference 0.63/255 against skimage.exposure
- PASS - histeq matches skimage equalize_hist: correlation 0.99999, mean difference 0.20/255 against skimage.exposure
- PASS - estimate_noise agrees with skimage at sigma 3: 3.01 here, 3.01 from skimage.restoration, truth 3
- PASS - estimate_noise agrees with skimage at sigma 8: 7.97 here, 7.93 from skimage.restoration, truth 8
- PASS - sobel matches scipy in shape, if not in scale: correlation 1.00000, mean difference 0.00/255 against scipy.ndimage

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
