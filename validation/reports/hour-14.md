# Hour 14 - the whole slider, and two measures that quit early

**2026-08-21** | 73 entries, 0 needing attention | 746 tests | 212 specific checks

Hour 13 closed on the observation that the checks asserted behaviour at or near
each filter's defaults. The parameter matrix ran the extremes to see whether
they crashed; nothing said what `clahe` at clip_limit 10 should produce. A
slider the interface offers is a promise that every value on it does something
sensible, and that promise was untested.

## Sampling the declared range

Seven filters now have their principal parameter sampled at six points across
the range `SLIDER_RANGES` declares - the same numbers the GUI and dashboard
panels offer - with the measured effect held to a direction:

    clahe            clip_limit  0.1:13.75  2.08:20.71  4.06:24.40
                                 6.04:26.56 8.02:28.14  10:29.31
    saturation       factor      0:0.00     0.6:33.93   1.2:67.18
                                 1.8:99.65  2.4:126.25  3:148.22

Two assertions per filter: the measure moves the right way across the whole
range, and no value on the slider flattens the image. An interface offering a
value the filter cannot survive is offering a trap.

## Both of my first two measures saturated

**`gaussian_blur`** measured by Laplacian variance:

    0.1:887.83  10.08:1.59  20.06:1.61  30.04:1.65  40.02:1.63  50:1.47

Flat from radius 10 to 50, and mildly non-monotonic inside the noise, which the
5% tolerance absorbed. The check would have passed while testing nothing over
four fifths of the slider.

The filter is fine. Radius 50 differs from radius 10 by a mean of 18.79 levels
and a maximum of 105, and global contrast falls the whole way - 42.65 at radius
5 to 21.58 at 50. Once the fine detail is gone it cannot go more gone, so the
*measure* stopped moving while the *filter* kept working. Switched to image
standard deviation, which tracks the blur across the full range.

**`nl_means`** measured by `estimate_noise` had the same shape:

    1:1.70  10.8:0.91  20.6:0.58  30.4:0.44  40.2:0.40  50:0.38

By h=30 there is almost no noise left to remove. The images keep changing - h=50
differs from h=30 by up to 109 levels - so again the measure floored, not the
filter. Switched to global contrast; `check_nl_means` still asserts the noise
claim itself over the range where it means something.

## A guard so this cannot happen quietly again

A saturated measure makes the ordering claim true and meaningless. Each range
check now carries a second assertion: the measure has to still separate values
in the **upper half** of the range, by at least 5% of its total span.

It found `nl_means` immediately - 0.06 of a 1.32 span, 4.5% - which is how the
second saturation came to light rather than sitting there passing.

## Where the mutations stand

    identity     135 of 187 checks notice     nothing else survived
    channels      34 of 212
    shift         30 of 212
    gain          18 of 212
    half          23 of 212

The new "no value flattens the image" checks are negative guards - an identity
does not flatten anything either - and are now classified by phrase rather than
listed one by one, since they are generated per filter.

## What this hour actually establishes

Not that the filters are correct at their extremes. It establishes that the
*direction* of each principal parameter holds across its whole declared range,
and that no offered value produces a dead frame. `clahe` at clip_limit 10 raises
local contrast to 29.31 - that it is the *right* 29.31 is not something this
checks, and I do not have a reference implementation to check it against.

That distinction is worth keeping visible. Every hour of this campaign has
narrowed what "passing" means; it has not yet reached "correct".

## Outstanding

1. The dashboard has no guided point picking - carried since hour 5
2. 38 of 73 entries still have no specific checks
3. Only seven filters have their range swept. The others have parameters with
   no obvious monotone measure - `border_mode`, `method`, `channel` - or none
4. No check compares any filter against an independent implementation. Every
   assertion is internal consistency or ground truth this campaign built
