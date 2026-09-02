# Hour 19 - the other boundaries, and one that stays unmeasured

**2026-08-21** | 76 entries, 0 needing attention | 755 tests | 301 assertions

Hour 18 fixed a colour bug in the dashboard and left two boundaries unchecked:
the desktop viewer, and the loader's video and raw paths. Both were named
because "appears correct" is what the dashboard looked like too.

## The desktop viewer is correct, measured rather than eyeballed

Driving the real `ImageCanvas` against a file whose bands are pure red, green
and blue:

    to_display red band      : (255, 0, 0)
    canvas composite red band: (255, 0, 0)
    as PIL receives it       : (255, 0, 0)
    after inverting red      : (0, 0, 0)

Every step from file to the array PIL hands Tk. The viewer was right all along
- but it is now right *demonstrably*, which is the difference the dashboard
made the case for.

## My expectation was wrong again, in a way worth recording

The split-view check failed: the right edge read (255, 0, 255) where I had
written (0, 0, 255). The processed frame has red inverted **everywhere**,
including the blue band, so (0, 0, 255) becomes (255, 0, 255). The viewer was
correct and I had forgotten that the operation applies to the whole frame, not
only to the band I was thinking about.

That is the fifth time in this campaign a failure has turned out to be my
expectation rather than the code. The ratio holds: instruments are wrong more
often than the thing they measure.

## Video frames come back RGB

A video written through OpenCV - which takes BGR - and loaded back:

    a red video frame loads as R,G,B = [255, 0, 0]

`_load_video_frame` converts, like the still path. Now a test, using MJPEG and
asserting the channel ordering rather than exact values, since the codec is
lossy.

## Raw is the one path that stays unmeasured

`_load_raw` returns `rawpy.postprocess()` directly, with no conversion, because
rawpy outputs RGB. rawpy is installed here; there is no raw file in the
repository or on this machine to decode.

So that path rests on rawpy's documented behaviour rather than on a
measurement. Rather than leave the assumption silent, it is now stated in the
function's own docstring, pointing at the tests that do measure the other two.

An assumption written down is not the same as a tested one, and the docstring
says which this is.

## Now permanent

`tests/test_colour_pipeline.py` covers nine cases: the loader's colour order,
what `save_image` writes, a file round trip, inverting red reaching the saved
file, a preset replaying to identical pixels, the dashboard's load path, both
front ends agreeing, a video frame, and the desktop viewer's composition.

Two of those nine would have failed against the code as it stood twenty-four
hours ago.

## Standing

    755 tests
    76 entries, 0 needing attention
    50 check groups, 301 assertions, all reached

## Outstanding

1. The dashboard has no guided point picking - carried since hour 5
2. 24 of 67 filters still have no specific checks
3. The raw path, above - untestable without a sample file. A small DNG
   committed to the repository would close it
4. The GUI viewer test drives `_compose`, which is the array the canvas
   draws. What Tk actually rasterises after that is still unverified, and a
   screenshot comparison would be the only way to close it
