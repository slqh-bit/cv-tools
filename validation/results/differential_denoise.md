# differential_denoise - validation result

**Checks spanning several filters**  
`validation.checks` | family: Cross-cutting | 2026-08-21T12:46:59

## Verdict

No runs - the filter could not be driven from the harness.

## What this filter specifically promises

- PASS - nl_means tracks skimage denoise_nl_means: correlation 0.99825, mean difference 1.39/255 against skimage.restoration
- PASS - both denoisers lower the noise they were given: sigma 1.68 -> 0.94 here, 0.90 in skimage
- PASS - unsharp_mask matches skimage unsharp_mask: correlation 0.99991, mean difference 0.21/255 against skimage.filters

## Runs

| image | parameters | ms | output | note |
|---|---|---|---|---|
