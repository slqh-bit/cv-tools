# Hour 9 - testing the tests, and finding a quarter of them worthless

**2026-08-20** | 73 entries, 0 needing attention | 741 tests | 144 specific checks

Hour 8 ended on a claim that needed acting on rather than repeating: *a check
that passes is not evidence until you know what it would take to fail it.*
This hour made that measurable.

## The method

`validation/mutate.py` replaces every filter the checks can reach with an
identity - it returns its input untouched - and runs each filter's checks
against the broken version. A check that still passes is not testing the
filter.

Not every pass is a fault. `levels` promises that its *defaults* are an
identity, and an identity honours that. Those are listed apart.

## The result: 29 of 77 checks proved nothing

    42 of 77 checks failed against a filter that does nothing

Which means 35 passed, of which only 6 legitimately. **Twenty-nine checks - 38%
of everything written across eight hours - would have passed against a filter
that did nothing at all.**

### component: 24 checks that only proved the input existed

    result.dtype == np.uint8 and result.size > 0

That is what "extracts a usable plane" meant. An identity satisfies it for
every one of the 24 space/channel pairs. The check counted 26 green ticks and
tested nothing.

Now: the result has to be a **single** plane at the frame's own dimensions -
which the three-channel input is not - and two channels of the same space have
to differ from one another. 34 checks, all failing under mutation.

### local_contrast: non-decreasing is not increasing

    all(b >= a - 0.01 for a, b in zip(scores, scores[1:]))

Three identical numbers satisfy that. A filter ignoring `strength` passed.
Now requires the end to exceed the start by 5%, and reports the ratio.

### white_balance: an assertion hardcoded to True

    out.append(('white_patch is unreliable on a frame with blown highlights',
                True,
                ...))

I wrote that in hour 4 as a way of recording an observation. It is a comment
with a tick beside it, and it sat in the results file for five hours looking
like a passing check. Now asserted properly: white_patch has to leave a
*wider* spread than gray_world on this frame, which is the thing actually
observed.

### white_balance: a check that depended on the frame already being right

"a patch declared neutral comes out near neutral" measured the patch on the
*untouched* frame, where it is already near neutral. Now measured on the
tinted frame, and it has to improve on where it started.

## After

    77 of 85 checks failed against a filter that does nothing

Eight pass: six legitimate identities, and two negative guards.

**The guards are worth naming as a category.** "Does not clip the frame at full
strength" and "heavy sharpening does not clip most of the frame" assert a
filter does not do something harmful - which doing nothing also satisfies.
That is inherent, not a defect, and both sit beside a positive check on the
same filter. `mutate.py` now classifies them rather than reporting them as
suspect forever.

## What this says about the campaign

The instrument-error rate stands at roughly two harness or check errors per
product defect across nine hours. This hour is the sharpest instance: 38% of
the checks were decorative, and every one of them had been reported in an
hourly summary as a passing measurement.

The green ticks in hours 3, 4 and 6 for `component`, `local_contrast` and
`white_balance` were not evidence. The numbers beside them were real
measurements, but the pass/fail verdicts were unearned.

`mutate.py` is now part of the campaign, not a one-off. Any check added from
here has to fail against a filter that does nothing, or be classified as an
identity promise or a guard, deliberately.

## Outstanding

1. Mutation testing only covers image-returning filters. The four report
   checks from hour 8 are not exercised by it - an identity makes no sense for
   a function returning a dict, so they need a different mutation (returning
   an empty report, or one with plausible but wrong numbers)
2. The dashboard has no guided point picking - carried since hour 5
3. 46 of 73 entries still have no specific checks
4. Blockiness sensitivity, raised in hour 8 and not looked at
