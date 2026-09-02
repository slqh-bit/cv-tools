# Hour 11 - perturbing mutation, and a real defect it flushed out

**2026-08-20** | 73 entries, 0 needing attention | 743 tests | 166 specific checks

Hour 10 named the blind spot: mutation replaced a whole function, so a filter
that was subtly wrong in a way an identity is not would pass everything. This
hour built the perturbing version - and in the course of it the harness caught
a genuine nondeterminism in `sobel`.

## The perturbations

`validation/perturb.py` runs the real filter and then damages its output the
way a real defect would:

| | what it imitates |
|---|---|
| `channels` | red and blue swapped - the BGR/RGB confusion every OpenCV codebase produces once |
| `shift` | the result rolled four pixels - an off-by-N in a coordinate |
| `gain` | every value scaled by 1.1 - a normalisation error |
| `half` | the filter applied to the left half only - a region bug |

First run, before any fixes:

    channels     7/111 checks noticed
    shift       11/111
    gain         8/111
    half         8/111

Roughly 93% blind. That is not 111 bad checks - a mean local sigma *should* be
invariant to translation - but it left three properties that nothing in the
suite verified at all.

## Three invariants, asserted directly

Rather than hardening every check, eleven tone and detail filters now get three
cross-cutting assertions against a frame carrying a bright marker and three
colour blocks: the filter must not move content, must not permute channels, and
must reach both halves of the frame.

    channels     7 -> 29 checks noticed
    shift       11 -> 22
    half         8 -> 19
    gain         8 -> 8

`gain` is deliberately unchanged. A 10% exposure shift is not universally wrong
- CLAHE and levels are *supposed* to move the histogram - so there is no
invariant to assert. It stays visible as a known blind spot rather than being
papered over.

## The tools had the same hole twice

The invariants at first noticed nothing, because they call
`resolve_filter(name).fn` and both mutation tools only patched the names the
checks module had imported. The registry served the real function throughout.
Both tools now patch `FILTER_REGISTRY` as well.

Then `shift` still read 11. My own invariant was too loose: the marker rolled
four pixels still landed inside the tolerance, and `np.argmax` returns the
*first* maximum, so a shifted block reports a coordinate inside the original
one. Measuring the centroid of the bright region instead took it to 22.

Two instrument errors inside the hour that built the instrument.

## And a real defect: sobel was not deterministic

The full sweep flagged `sobel` for returning different results across two runs
of the same input. Verified directly: six runs, differing intermittently by one
level in exactly one pixel.

The cause is `cv2.magnitude`, which dispatches to different SIMD paths between
calls:

    553.759887695   against   553.759826660

for the same input. `cv2.Sobel` is deterministic; `np.sqrt(gx**2 + gy**2)` is
deterministic; `cv2.magnitude` is not. One pixel of that frame sat on an
integer boundary, so the last-bit difference flipped the uint8.

One pixel by one level sounds like nothing. It is not: the whole preset system
rests on a chain replaying identically, and a report that cannot be reproduced
is not evidence. Replaced with the numpy computation, verified over twelve
runs, and two regression tests added - one for `sobel` specifically and one
asserting every edge filter replays identically.

It was found by the determinism check written in hour 1 and never triggered
until now, because it only fires when a pixel sits exactly on a boundary.

## Outstanding

1. `gain` remains unnoticed by every check, by design - no filter-independent
   invariant exists for it
2. The dashboard has no guided point picking - carried since hour 5
3. 46 of 73 entries still have no specific checks
4. `cv2.magnitude` is used nowhere else, but the class of bug - an OpenCV
   routine that is not bit-reproducible - could sit in any filter whose
   determinism check has never happened to land on a boundary pixel. The
   check runs once per filter on one image; running it on several would
   raise the odds of catching the rest
