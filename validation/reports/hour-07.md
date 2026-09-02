# Hour 7 - the control that decides whether any of it means anything

**2026-08-20** | 73 entries, 0 needing attention | 741 tests | ghost now carries 7 checks

Hour 6 ended by naming the weakness in every ghost measurement taken so far:
each one pasted a region cut from the *same frame*. A real forgery brings
content from somewhere else, and the texture difference that produced the
false positives would then be genuine. Testing that was this hour.

## The result

Four cases, 8 frame pairs each, region (152, 104, 296, 200):

| case | fired | mean dip | quality named |
|---|---|---|---|
| A same scene, Q55 into Q95 | 2/8 | -0.232 | 55 |
| B **cross scene**, Q55 into Q95 | 4/8 | -0.250 | **55** |
| C **cross scene, Q95 into Q95** | **0/8** | -0.063 | - |
| D untouched | 0/8 | -0.077 | - |

**Case C is the one that matters.** A region cut from an entirely different
scene - different furniture, different lighting, different everything the eye
would use - pasted at the *same* JPEG quality as its host, does not fire. It
differs from its surroundings in every way except compression history, and the
detector stays silent.

That is the claim the statistic needed and had not been given. Hour 5 changed
it from "how far the region sits below the frame" to "how far its best quality
dips below its own average" precisely to stop measuring texture. This says the
change did what it was meant to: with texture varied to the maximum and
compression held constant, the answer is no.

Case B says the realistic forgery is found at about the same rate as the
same-scene one, and names the right quality when it does.

The control is now a permanent check. Without it, a detector that merely
noticed "this part looks different from the rest" would pass every other check
in the file.

## A correction: the sample was not stale

Hour 5 listed `samples/jpeg_ghost.png` as built for the old contract with
nothing exercising it. Wrong on both counts. Given its actual region - the
generator pastes at `[128:256, 176:336]`, which is (176, 128, 160, 128) - it
reports:

    detected=True   quality=95   dip=-0.258

Exactly the quality the region was pasted at. The per-quality trace shows why:

    Q50   Q55   Q60   Q65   Q70   Q75   Q80   Q85   Q90    Q95    Q100
   +0.03 +0.26 +0.33 +0.32 +0.23 +0.30 +0.38 +0.38 +0.32  -0.03  -0.01

The region sits *above* the frame everywhere except at its own quality.

It also covers a direction nothing else here does. Every other measurement in
this campaign puts a **lower**-quality region inside a higher-quality frame;
this one is a Q95 region inside a Q60 frame. A technique that only worked one
way round would have passed everything else. Now checked.

## A check that was asserting more than the filter promises

The first version of the cross-scene check asserted that a specific Q55 donor
pair must be detected. It failed - dip -0.206 against a 0.25 threshold - and
the failure was correct: the measured detection rate is 59%, so that pair is
one of the four in ten the filter is documented to miss.

Rewritten to test the ordering instead: a quality difference has to dip deeper
than texture alone. -0.206 against -0.113 on the same donor, which is the
discriminative claim and is true every time.

Worth noting as a pattern - three checks this campaign have asserted a
behaviour stronger than the filter's measured rate. A check that a filter
passes only 59% of the time is a flaky test, not a validation.

## Outstanding

1. The dashboard has no guided point picking - carried from hour 5
2. A sweep-range-invariant statistic would let one threshold cover Q35 to Q70;
   the per-block normalisation is what ties them together
3. Detection sits at 59% with 3% false positives on grid-aligned pastes with a
   40-point quality gap. Every one of those qualifiers is a real limit and all
   of them are now measured, but none has been improved on
4. `ela`, `noise`, `compression` and `metadata` have no specific checks - they
   are exercised by the sweep but nothing asserts what they promise
