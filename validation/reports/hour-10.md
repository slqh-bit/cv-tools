# Hour 10 - mutation reaches the reports, and the tool's own blind spot

**2026-08-20** | 73 entries, 0 needing attention | 741 tests | 144 checks, none unearned

Hour 9 ended by naming the gap in its own method: mutation covered only
image-returning filters, so the four report checks written in hour 8 still
carried unearned ticks. Closed.

## Freezing, not emptying

There is no "do nothing" version of `noise_report` - it has to return a dict
either way. The equivalent mutation is to make a measurement **stop responding
to its input**: answer one real call, then return that same answer forever. A
check that verifies the number changes with the image fails; a check that only
verifies the keys exist passes, and is thereby shown to be structural.

First run: **10 report checks survived.**

## The tool was wrong before the checks were

Five of those ten were an artefact of my own method. Freezing caches the first
call, so whichever assertion runs first receives the correct answer to its own
question and passes for free - `compression`'s "reads back a quality of 40"
was simply the first iteration of its loop.

I tried running each check twice to prime the cache. That does nothing: the
cache fills from the same first call both times.

The fix is to prime each measurement from an input the checks never ask about
- a flat grey frame, an unrelated Q10 file, an empty tag set - so every answer
the check receives afterwards is foreign to it.

That removed all five artefacts, and in doing so uncovered **two genuinely weak
checks that had been hiding behind them**:

- *"remarks on a JPEG with no EXIF at all"* asserted only that the finding was
  present. `no_exif` appears in the report of any stripped JPEG, including the
  decoy. It never checked the report was about the file in question. Now tied
  to the filename.
- *"says nothing about a consistent set of timestamps"* asserted an empty
  result, which a function returning nothing at all also satisfies. Now paired
  with the disordered case in one assertion: consistent timestamps produce
  nothing **and** disordered ones produce something.

Both had passed every previous sweep.

## Where it stands

    Nothing else survived.

144 checks. Eight pass under mutation and all eight are classified
deliberately: six identity promises, and three guards - two negative
assertions and one structural contract, `ela`'s "reports the block statistics
the report renders", which verifies the keys the renderer expects and is
satisfied by a frozen report correctly.

## The pattern this campaign keeps producing

Nine hours of checks, then two hours of testing the checks, and the second
activity found more than the first. The count so far:

| | found |
|---|---|
| product defects | ~6 |
| harness or check errors | ~13 |

Every instrument error was invisible until something tested the instrument.
The colour-mode defect in hour 1 was found by a contract test, not by reading
code. The 38% of decorative checks in hour 9 were found by mutation, not by
review. This hour's two weak checks were found only after fixing the mutation
tool's own blind spot - three levels deep.

There is no reason to think the current tools have no blind spot. The known
one: mutation replaces a whole function, so it cannot catch a check that is
right about a filter which is subtly wrong in a way an identity is not - a
sharpen that sharpens the wrong channel would pass everything here.

## Outstanding

1. The dashboard has no guided point picking - carried since hour 5
2. 46 of 73 entries still have no specific checks
3. Blockiness sensitivity, raised in hour 8, still unexamined
4. A mutation that perturbs rather than replaces - scaling a return value,
   shifting a coordinate - would reach the class of defect described above
