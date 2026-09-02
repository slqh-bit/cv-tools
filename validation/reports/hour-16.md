# Hour 16 - the corpus had been the wrong colour for sixteen hours

**2026-08-21** | 75 entries, 0 needing attention | 746 tests | 261 assertions across 43 groups

A check written to catch a channel-order bug found one. It was mine.

## What happened

Writing exact-formula checks for `invert_channel`, I asserted that
`channel='r'` inverts array index 2, the red channel of a BGR image. Two of the
three failed: `g` passed, `b` and `r` did not - the signature of a channel
swap.

Every filter that takes a `channel` behaved the same way, so it looked
systemic. Then a round trip through a real file settled it:

    wrote a pure RED png
    ImageLoader returns B=255 G=0 R=0   -> the loader gives RGB
    after invert_channel(channel='r'), the file has R=0
      -> red was inverted: correct

`core.ImageLoader` converts BGR to RGB on load, and `save_image` converts back.
The pipeline is RGB end to end, the filters are right, and the file that comes
out is the file the user expects.

**The harness loaded the corpus with `cv2.imread`, which returns BGR.** For
sixteen hours every filter in this campaign has been fed images with red and
blue exchanged.

## What that invalidates, and what it does not

Most measurements are luminance-based - local contrast, noise sigma, Laplacian
variance, blockiness. Swapping red and blue changes the greyscale weights
(0.299 against 0.114) so the absolute numbers shift, but the comparisons were
between images processed identically, and the conclusions hold.

What was actually wrong:

- Every colour-cast measurement in `check_white_balance` named the wrong
  channel
- The colour blocks in the cross-cutting invariants were labelled backwards -
  the assertion was index-based so it still worked, but it read as nonsense
- `check_invert_variants` mapped the channel names in BGR order and reported a
  correct filter as broken

All corrected. `load_corpus` now goes through `ImageLoader`, so the harness
feeds filters exactly what the product feeds them.

**A harness that does not load images the way the product does is not testing
the product.** That sentence is now in the docstring, because the cost of
learning it was sixteen hours of colour-blind measurements.

## Two other checks of mine were wrong, both found by the same sweep

`solarize` was reported as failing to invert values at the threshold. The rule
is *above* the threshold, so at threshold 128 the value 128 passes through -
an off-by-one in my check, not the filter.

`white_patch` was reported as failing to reduce a colour cast. It was being
tested on the frame with the most blown highlights in the corpus, and
white_patch normalises by each channel's brightest pixel: when every channel
already reaches 255, every gain is exactly 1.0 and the method cannot do
anything at all. Moved to a frame where it can work - where it reduces a cast
of 45.0 to 17.9 - with the blown-highlight weakness kept as its own assertion.

I also had to walk back my own first correction there. I asserted white_patch
"does nothing at all" on blown frames; that is true only when *every* channel
saturates, which is the tinted case. On the untinted frame it acts, just far
worse than gray_world. The check says the weaker, true thing.

## The coverage audit that started the hour

`validation/coverage.py` compares what `checks.py` registers against what the
last sweep recorded, and fails if anything registered was never run. It exists
because that failure has happened twice - report checks in hour 10, the
differential group in hour 15 - and both times looked like a clean sweep.

    43 check groups registered
    43 ran in the last sweep, contributing 261 assertions
    33 of 67 filters have no specific checks

## Also this hour

Three more differential comparisons against scikit-image: `nl_means` tracks
`denoise_nl_means` at 0.99838, `unsharp_mask` matches `filters.unsharp_mask` at
0.99991, and both denoisers lower the noise they were given from the same
starting point.

New exact-formula checks for `solarize`, `invert_channel`, `invert_luminance`
and the automatic stretches.

## Outstanding

1. Every number in reports 1-15 was measured on channel-swapped input. The
   conclusions stand, the absolute figures do not
2. The dashboard has no guided point picking - carried since hour 5
3. 33 of 67 filters still have no specific checks
4. Nothing checks that a filter which claims to work "per channel" applies to
   the channel the caller named - only `invert_channel` is now verified that
   way, and `contrast_brightness`, `levels` and `curves` all take the same
   parameter
