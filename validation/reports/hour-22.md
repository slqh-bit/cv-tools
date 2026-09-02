# Hour 22 - frame integration, and the case it could not reach

**2026-08-21** | 76 entries, 0 needing attention | 770 tests | 301 assertions

Hour 21 noticed that the multi-frame filters were unreachable from batch mode
and left the question of whether that was a gap in the tests or in the CLI. It
was in the CLI, and it mattered for exactly the data sitting on this machine.

## The filters themselves are exact

`average_frames` against noise that is genuinely independent, which is what the
sqrt(N) law requires:

| N | measured | predicted | ratio | sqrt(N) |
|---|---|---|---|---|
| 2 | 5.65 | 5.61 | 1.40 | 1.41 |
| 4 | 4.00 | 3.97 | 1.98 | 2.00 |
| 9 | 2.68 | 2.64 | 2.95 | 3.00 |
| 16 | 2.03 | 1.98 | **3.90** | 4.00 |

The implementation is right. Everything below is about whether real data meets
its premise.

## Three sources, three different answers

| source | 16 frames | ratio |
|---|---|---|
| synthetic independent noise | 7.93 → 2.03 | **3.90×** |
| a static scene on video | 10.94 → 3.39 | 3.22× |
| motion-event snapshots seconds apart | 1.73 → 1.59 | **1.08×** |

The middle row falls short because scene texture and the codec's own
quantisation are correlated between frames and do not average away. The last
row barely moves because the scene itself changed - and that is not a case for
`mean` at all. `median` is the method for it, which removes what moved rather
than smearing it.

All three are now in the filter reference, because "averaging N frames divides
noise by sqrt(N)" is true only of the first, and a user who reads it as a
promise will be disappointed by their own footage.

## The gap: --frames took video only

    --frames requires a video file, got: 2026-07-27_15-00-32_cam1_motion.jpg

Frame integration existed, was documented, and could not be pointed at a folder
of stills - which is how exported CCTV evidence usually arrives, and precisely
what the 200 snapshots on this desk are. The one format most likely to be
handed over was the one format it could not read.

Now it can:

    cv-tools snapshots/ --frames 16 --frame-method mean -o averaged.png
    Combined 16 stills with 'mean'

Frames must share a size - a folder holding two cameras' output is a mistake
worth reporting rather than resizing away - and fewer than two images is
refused with a message that says so. The metadata records what was combined,
so the report names the frames rather than a directory.

`run_one` was split while doing this: loading is now `_load_one` or
`_combine_stills`, and everything after it is `_process_source`. The function
had grown to hold the whole of both paths.

## Five tests

Averaging stills reduces noise by more than 3x on independent noise, a
directory of one image is refused, frames of different sizes are refused, the
metadata records what was combined, and a still *file* still refuses `--frames`
with the message naming both things that would work.

## Outstanding

1. 24 of 67 filters still have no specific checks
2. `--frames` on a directory ignores `--batch`; combining several *groups* of
   stills in one run is not expressible. Whether that is worth having is a
   question about how people actually work, not one this campaign can answer
3. `super_resolve` and `nl_means_denoise_frames` take multiple frames and are
   still unreachable from the CLI by any route - only the four
   `frame_averaging` methods are wired to `--frame-method`
4. The raw loader path still has no test, for want of a sample file
