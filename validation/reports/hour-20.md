# Hour 20 - pixels on a screen, and clearing a fifteen-hour backlog item

**2026-08-21** | 76 entries, 0 needing attention | 757 tests | 301 assertions

Two things: the last unverified step of the colour path, and an item that had
been carried since hour 5.

## The colour thread is closed at the glass

Every colour check so far read an array - the one the canvas composes, the one
PIL receives. What Tk actually rasterises was still taken on trust. A real
window, showing a file with pure primaries, screenshotted and sampled:

    canvas grabbed 747x545
      screen pixel in the red band   at x=40 : (255, 0, 0)
      screen pixel in the green band at x=240: (0, 255, 0)
      screen pixel in the blue band  at x=400: (0, 0, 255)

File to loader to filter to canvas to PIL to Tk to screen. Exact primaries at
every step, and the screenshot shows red, green, blue in that order.

That closes a thread that ran from hour 16's harness error, through hour 18's
live dashboard bug, to here.

## The dashboard can pick points now

Carried since hour 5. Fifteen hours of listing something is a signal that it
should either be done or dropped, so it is done.

`measure_3d` and `perspective` are filled by tapping the image, one point at a
time, with the prompt naming what is wanted - *the FOOT of the reference
object*, then *the TOP*, and so on. Two taps become the four numbers a horizon
line takes. Verified end to end through AppTest:

    reference_base   = '300,400'
    reference_top    = '300,250'
    base             = '450,420'
    top              = '450,300'
    horizon          = '0,180,639,180'

**The sequence moved to `filters.registry.POINT_PARAMETERS`**, so both front
ends read one definition. The desktop app previously held its own copy, and two
copies of a prompt list would have drifted the first time either changed - the
same reasoning that put the analysis registry there in hour 1.

## What was actually missing

The dashboard has had tap-to-pick since before this campaign. It collected
coordinates into a list and left the user to work out which was which and type
them into five fields. What was missing was not the tapping; it was knowing
what each tap is *for*.

That is the same gap the desktop app had before hour 5, and the same reason it
matters: single-view metrology gives a confidently wrong height when a
reference top is confused with an object top, and nothing downstream catches
it.

## Standing

    757 tests
    76 entries, 0 needing attention
    50 check groups, 301 assertions, all reached by the sweep
    Colour verified from file to screen on both front ends

## Outstanding

1. 24 of 67 filters still have no specific checks - now mostly ones whose
   promise is genuinely hard to state (`stain`, `multiscale_detail`,
   `fft_spectrum`, `s_curve`)
2. The raw loader path has no test, for want of a sample file. A small DNG in
   the repository would close it
3. The dashboard's picking is verified through AppTest, which drives the
   script rather than a browser. The tap component itself - the part that
   turns a click into coordinates - is exercised by neither front end's tests
4. Nothing in this campaign has tested the CLI's batch mode against a
   directory of mixed formats, which is the path most likely to be used on
   real evidence
