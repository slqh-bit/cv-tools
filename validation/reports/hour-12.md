# Hour 12 - hunting the rest of the sobel class, and eight filters that had no checks

**2026-08-20** | 73 entries, 0 needing attention | 743 tests | 189 specific checks | 35 entries checked

Hour 11 found `sobel` returning different pixels between runs and closed with
the obvious worry: the determinism check runs once per filter on one image and
only fires when a pixel sits exactly on an integer boundary. How many others
were there?

## None. Every filter and every report replays identically.

`validation/determinism.py` runs every registered filter over several images
several times and compares:

    67 filters x 5 images x 3 runs      - identical every time
    6 reports x 4 images x 2 runs       - identical every time

`sobel` was the only one. That is worth knowing rather than assuming, and the
script stays so it can be re-run after any change that touches an OpenCV call.

## Two filters had been invisible to every sweep

The hunt reported `fit_aspect` and `selective_saturation` as *not driveable* -
their required parameters (`target_ratio`, `hue_center`) were missing from the
harness's value table, so `parameter_matrix` returned nothing and both had been
recorded as "1 run, no drivable parameter set" since hour 1.

Eleven hours of green sweeps included two filters that were never actually run.
Both now exercised.

## Eight filters got checks, and three of mine were wrong

`flip`, `invert`, `rotate`, `resize`, `crop`, `fft_filter`, `remove_periodic`
and `deblock` had none. Now 23 checks between them, including ground truth
where it exists - `remove_periodic` measured against the sample built with a
known interference (7 detected peaks before, fewer after), `crop` against the
exact array slice, `invert` against `255 - input` exactly.

Writing them, I got `rotate` wrong twice:

1. Assumed an `expand` parameter. There is none - `TypeError`.
2. Corrected to "a quarter turn keeps the frame size". Wrong the other way:
   640x362 became 362x640.

Reading the implementation settled it. `rotate` computes the rotated bounding
box and grows the canvas, so a quarter turn swaps the dimensions and loses
nothing, and 45 degrees gives 708x708 from 640x362. Four quarter turns return
the original with a mean difference of 0.01/255.

Both wrong versions would have been "passing checks" had the filter happened to
behave as I assumed. Guessing an API and asserting against the guess is how a
check ends up testing the guess.

## Involutions need a partner

`flip(flip(x)) == x` and `invert(invert(x)) == x` are both satisfied by a
filter that does nothing. Each is paired in the same assertion with "and the
single application differs from the input", so the pair discriminates where
neither half would.

The same reasoning applies to the cross-cutting invariants from hour 11: "does
not move content" and "keeps the red block red" are *preservation* claims that
an identity necessarily satisfies. They pair with "reaches both halves of the
frame", which an identity fails. `mutate.py` now classifies preservation
claims by pattern rather than listing each one.

## Where the two mutations stand

    identity     125 of 172 checks notice     nothing else survived
    channels      34 of 189
    shift         30 of 189
    gain          18 of 189
    half          23 of 189

The perturbation numbers rose with the new geometry checks - `crop`, `resize`
and `rotate` assert exact dimensions and exact pixels, so a shifted or
recoloured output fails them.

`gain` went from 8 to 18, entirely from the new checks that compare against an
exact expected array rather than a statistic.

## Outstanding

1. The dashboard has no guided point picking - carried since hour 5
2. 38 of 73 entries still have no specific checks, down from 46
3. `gain` remains the weakest perturbation to detect: most filters are allowed
   to change exposure, so there is no general invariant
4. `determinism.py` uses default parameters only. A filter could be stable at
   its defaults and not at an extreme, which the parameter sweep would not
   catch either since it runs each combination once
