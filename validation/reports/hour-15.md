# Hour 15 - evidence from outside the building

**2026-08-21** | 74 entries, 0 needing attention | 746 tests | 222 specific checks

Every assertion this campaign had written was internal: a filter against its
own documented behaviour, or against ground truth built here. Both can be
self-consistent and wrong together. This hour added the missing kind - the same
operations, computed by code nobody here wrote.

## Ten comparisons against scipy and scikit-image

Both are already dependencies of the toolkit, and both implement several of
these operations by different routes.

| | agreement |
|---|---|
| `gaussian_blur` radius 2 / 5 vs `scipy.ndimage.gaussian_filter` | 0.99986 / 0.99968 |
| `median_filter` vs `scipy.ndimage.median_filter` | 0.99998, 90% of interior pixels bit-identical |
| `levels` gamma 0.5 / 2.0 vs `skimage.exposure.adjust_gamma` | 0.99996 / 0.99979 |
| `histeq` vs `skimage.exposure.equalize_hist` | 0.99897 |
| `sobel` vs `scipy.ndimage.sobel` | 0.99978 |
| `estimate_noise` vs `skimage.restoration.estimate_sigma` | 3.01 vs 3.01, 7.97 vs 7.93 |

The noise comparison is the strongest of them. Immerkaer's kernel here, a
wavelet estimator there - genuinely different mathematics for the same
quantity, agreeing to two decimal places against a known truth.

## The two that failed were both the frame border

`median_filter` came out at 0.988 against scipy, and `sobel` at 0.965. For an
operation as unambiguous as a median that is a real gap, so it was worth
chasing rather than loosening the bar.

Trimming two pixels of border:

| | full frame | interior |
|---|---|---|
| `median_filter` | 0.98801 | **0.99998** |
| `sobel` | 0.96488 | **0.99977** |

Entirely convention: OpenCV replicates the edge pixel, scipy reflects it. The
arithmetic agrees; the edge does not, and never will.

Rather than trim it away silently, that difference is now its own assertion -
the agreement *has* to be worse including the border, and the check says why.
It matters practically: a frame processed here and the same frame processed in
another tool differ in their outermost pixels, which is exactly the sort of
discrepancy that looks alarming when two analysts compare outputs.

## Two holes in the harness, again

`estimate_sigma` needs PyWavelets, which the toolkit does not depend on. The
check first raised an ImportError; it now degrades to a *failing* check saying
the reference is unavailable, rather than passing quietly. PyWavelets is
recorded in `validation/requirements-validation.txt` as a validation-only
dependency, so nothing about the product's own dependencies changed.

More seriously: the differential group did not run at all in the first sweep.
The harness iterates the filter and analysis registries, and `differential`
matches neither - so the checks were written, collected, and never executed,
and `RESULTS.md` said nothing was wrong. The harness now picks up check groups
that belong to no single filter and reports them as their own entry, which is
why the count went from 73 to 74.

That is the second time a check has been silently uncollected - hour 10 found
the same for report checks. Both times the symptom was identical: a clean
sweep that had quietly tested less than it claimed.

## What this changes about the campaign's claims

Six filters now have evidence that does not originate here. That is a
different quality of statement from the previous fourteen hours: not "the
filter behaves as its docstring says", but "the filter computes the same thing
two other libraries compute".

It covers six of sixty-seven. The rest still rest on internal consistency,
including everything forensic - `ela`, `ghost`, `clone_detect` have no
independent implementation available to compare against, which is precisely
why their ground truth had to be constructed by hand.

## Outstanding

1. The dashboard has no guided point picking - carried since hour 5
2. 38 of 74 entries still have no specific checks
3. `nl_means` could be compared against `skimage.restoration.denoise_nl_means`
   and `unsharp_mask` against `skimage.filters.unsharp_mask` - both available
   and not yet used
4. Nothing verifies that a check group is actually reachable by the harness.
   Twice now that has failed silently; a count of collected-versus-run checks
   would catch the third
