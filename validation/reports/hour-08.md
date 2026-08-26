# Hour 8 - the four reports get checks, and one of them nearly hid a bug that was mine

**2026-08-20** | 73 entries, 0 needing attention | 741 tests | 136 specific checks across 27 entries

`ela`, `noise`, `compression` and `metadata` ran in every sweep but nothing
asserted what they promise. All four now have checks driven by ground truth
rather than by whether they return a dict.

## A harness gap that would have made this hour pointless

`run_analysis_spec` never called `run_checks`. Checks written for a report
would have been collected, keyed, and silently never executed - and the run
would have printed `0/0 checks` next to a green tick.

Found before writing the checks rather than after, which was luck. Reports now
run their checks, keyed `<name>:report` where a filter shares the name, so
`ela`'s report checks stay off `ela`'s filter result.

## compression: the one measurement with an exact answer

A JPEG carries the quantisation tables it was written with, so the quality read
back can be checked against the quality it was saved at - no proxy, no
threshold, no tolerance worth arguing about:

| saved at | reported |
|---|---|
| 40 | **40** |
| 60 | **60** |
| 75 | **75** |
| 90 | **90** |

Exact on all four. A PNG correctly reports no tables at all rather than
guessing.

**One thing worth flagging.** Blockiness runs 3.9 -> 4.2 -> 4.4 across quality
90 -> 60 -> 30. The ordering is right, but that is a very narrow range for a
measure the report renders as `X/100` and describes as "uncompressed images sit
near 1, heavy compression well above it". A three-fold change in compression
moves it by 13%. It is ordered, so the check passes; whether it is *useful* at
that sensitivity is a separate question, and one this campaign has not asked.

## metadata: seven checks, including the negatives

The positives were already known. What was missing were the cases where it must
stay quiet:

- a PNG with no EXIF draws no remark, because PNG is not an EXIF-bearing format
- three identical timestamps produce zero findings
- camera firmware in the Software tag is not read as an editor, where
  Photoshop is

And the Nikon file still flags exactly the three contradictions hour 3
established as true positives.

## noise: my ground truth was wrong, and the tolerance hid it

The first version measured sigma recovery on a three-channel image:

    sigma 2  -> 1.37      sigma 5  -> 3.35      sigma 10 -> 6.70

All three passed a 35% tolerance. All three are the same ratio - 0.685, 0.670,
0.670 - and a systematic factor is never noise.

I went looking for a normalisation error in the estimator and found none: the
Immerkaer kernel's divisor of 6 is exactly sqrt(sum of squares) = sqrt(36), so
the formula is right. The error was mine. I added **independent** noise to
three channels and compared against the per-channel sigma, but `_to_gray`
weights the channels 0.114 / 0.587 / 0.299, so luminance noise is
sqrt(0.114^2 + 0.587^2 + 0.299^2) = **0.669** of it. The number I called an
error was the correct answer to a question I had asked wrong.

Rewritten against single-channel ground truth, where the answer is exact:

| sigma | measured | error |
|---|---|---|
| 2 | 2.03 | 1.6% |
| 5 | 5.00 | 0.1% |
| 10 | 10.01 | 0.1% |
| 20 | 20.03 | 0.1% |

Tolerance tightened from 35% to 5%, and the luminance weighting is now a check
of its own rather than an unexamined assumption.

**The tolerance was the real fault.** A 35% band is wide enough to pass a
consistent 33% bias, which is exactly the kind of error worth catching. A
check that cannot fail is not a check, and a loose tolerance is the quiet way
to write one.

## ela

A region re-encoded at Q55 inside a Q95 frame reads 16.35 mean error against
12.12 outside it, so the region does stand out. The comparison quality moves
the answer as it should (3.11 -> 2.31 -> 0.98 at quality 70/85/95).

## Outstanding

1. The dashboard has no guided point picking - carried since hour 5
2. Blockiness sensitivity, raised above: ordered but possibly too flat to act
   on
3. 46 of 73 entries still have no specific checks. They are the ones where a
   promise is hard to state - `fft_filter`, `remove_periodic`, `stain`,
   `texture_boost` - which is exactly where an unstated promise can hide
4. Every tolerance written before this hour deserves the same look the noise
   one just got. A check that passes is not evidence until you know what it
   would take to fail it
