# Hour 17 - closing the channel question, and the greyscale that came with it

**2026-08-21** | 76 entries, 0 needing attention | 746 tests | 301 assertions across 50 groups

Hour 16 found the harness feeding filters BGR while the product feeds them RGB,
and left the obvious follow-up open: three filters take a `channel` parameter
and nothing verified any of them acted on the channel named. That is precisely
where a colour-order confusion hides.

## Every per-channel filter acts on the channel named

`contrast_brightness`, `levels`, `curves` and `invert_channel`, each driven
with `channel='r'`, `'g'` and `'b'` against a frame whose three channels are
deliberately far apart:

    12 of 12 - every filter touched exactly the array index the name means,
    in the RGB that ImageLoader produces

Settled by measurement rather than by inference from one filter. It is the
check that would have caught hour 16's problem from either direction, and it
did not exist until now.

## The checks were still converting to greyscale the wrong way

`_gray` used `COLOR_BGR2GRAY` while every `_to_gray` in `cv_tools/filters` uses
`COLOR_RGB2GRAY`. On RGB data that weights the channels 0.114/0.587/0.299
instead of 0.299/0.587/0.114 - a different greyscale, and a different number
out of every luminance measurement in the file. Same for the HSV conversions
behind the saturation checks.

Corrected, and the full sweep came back clean. That is worth noting rather than
glossing: **nothing broke**, because every check compares images processed
identically, so a shared error in the measure cancels. The numbers in earlier
reports were wrong; the comparisons they supported were not.

## Six more filters got checks

`canny` and `auto_canny` - the map is binary, the detected edge sits within two
columns of a step edge placed at a known column, a flat frame yields nothing,
and a higher threshold finds strictly fewer edges (4508 -> 2691 -> 1544).

`roi_crop` - returns the exact slice, and clips an oversized region where
`crop` raises, which is the documented difference between them.

`bit_plane` - all eight planes binary, and plane 7 agrees with a 128 threshold
on 99%+ of pixels, which is what the most significant bit means.

`noise_map` - brighter where noise was planted than where it was not.

`temperature` - warming raises red and lowers blue, cooling does the reverse,
and 0 is an exact identity.

`pixel_aspect` and `fit_aspect` - the arithmetic, checked as arithmetic.

Coverage went from 33 filters without checks to 24.

## One more check that could not fail

Mutation caught `auto_levels widens the tonal span` passing against a filter
that does nothing. Two faults in one line: `after >= before` admits equality,
and the corpus frame already spans 228 of 255, so an automatic stretch has
nothing left to do on it. Both fixed - the frame is now deliberately squeezed
into the middle of the range, and the assertion demands a 50% widening. It goes
79 -> 227.

That is the fourth check in this campaign written with a non-strict comparison
that an unchanged image satisfies. It is a habit worth naming: `>=` in a check
that means "this filter changes something" is almost always wrong.

## Standing

    50 check groups, all reached by the sweep, 301 assertions
    179 of 239 notice a filter that does nothing
    24 of 67 filters still have no specific checks

## Outstanding

1. The dashboard has no guided point picking - carried since hour 5
2. 24 filters without checks, now mostly ones whose promise is genuinely hard
   to state: `stain`, `multiscale_detail`, `fft_spectrum`, `s_curve`
3. Nothing has verified the *product's* own colour handling end to end - that
   a file loaded, filtered and saved comes back with its colours intact. The
   round trip I ran by hand in hour 16 to settle the convention would make a
   good permanent test, and there is none
