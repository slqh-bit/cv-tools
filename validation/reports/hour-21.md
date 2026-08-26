# Hour 21 - batch mode, and a path that was right the first time

**2026-08-21** | 76 entries, 0 needing attention | 765 tests | 301 assertions

Hour 20 closed on the observation that nothing in twenty hours had tested the
CLI's batch mode, which is the path most likely to meet real evidence: a folder
of frames in whatever formats the camera, the exporter and the recipient
happened to produce.

It works. This is the first path this campaign has examined and found correct
on the first pass, which is worth saying plainly rather than burying under the
tests it now has.

## What was thrown at it

A directory built to look like a real one: six formats, a subdirectory, a text
file, and a deliberately corrupt PNG.

    a.png  b.jpg  c.jpeg  d.bmp  e.tif  f.webp
    day2/g.png
    notes.txt        (not an image)
    broken.png       (PNG header, then garbage)

Result:

    Batch complete: 7/8 succeeded
    exit code 1
    error: Failed to load image: .../broken.png

Every valid frame processed, each written in its own format. `notes.txt` was
never treated as an input. The corrupt file was named on stderr and **did not
abandon the run** - which is the property that matters, because one unreadable
frame in a folder of hundreds must not cost the other hundreds. The exit code
still reports that something went wrong.

`--recursive` mirrors the tree: `day2/g.png` in, `out/day2/g.png` out.

## The two things most likely to be quietly wrong

**Colour through the batch.** Given the last five hours, this was the first
thing to check. Pure red, green and blue bands in, and the dominant channel
per band out: `[0, 1, 2]` on every file. Batch inherits the loader, so it
inherits the fix.

**Reports written per file.** The code writes the report and the preset only on
the first frame, and the reasoning is in a comment - per-file reports would
overwrite each other and leave whichever frame happened to be last. Verified:
one report, one preset, one recorded step.

And a preset replayed across formats gives the same pixels from every
container:

    x.png  red band -> (0, 69, 38)
    y.jpg  red band -> (0, 69, 38)
    z.tif  red band -> (0, 69, 38)

## Now tested

`tests/test_batch.py`, eight cases: every supported format processed, a
non-image ignored, a corrupt file not abandoning the batch, `--recursive`
mirroring the tree, colour surviving, the report and preset written once,
`--batch` on a file refused, and an empty directory reported rather than
silently succeeding.

## A note on what "found nothing" is worth

Twenty hours of this campaign have produced roughly eight product defects and
fifteen instrument errors. An hour that finds nothing reads as a wasted hour
against that, and it is not: batch mode now has eight tests it did not have,
and the next person to change `resolve_batch_output` or the loader's format
list will find out immediately.

The value of a check is not what it found today.

## Outstanding

1. 24 of 67 filters still have no specific checks
2. The raw loader path has no test, for want of a sample file
3. Batch runs each file through a fresh pipeline. Nothing tests what happens
   when a chain is *stateful* across frames - `frame_averaging` and
   `super_resolve` take several images at once and are not reachable from
   `--batch` at all, which may be a gap in the CLI rather than in the tests
4. The corrupt-file test uses a truncated PNG. A file that decodes but is
   nonsense - right header, wrong dimensions, zero bytes of pixel data - is a
   different failure mode and is not covered
