# Hour 13 - the parameter sweep finds what the defaults hid

**2026-08-21** | 73 entries, 0 needing attention | 746 tests | 191 specific checks

Hour 12 closed on a stated limit: `determinism.py` used default parameters
only, so a filter reproducible at its defaults and not at an extreme would
pass. Extended to the whole parameter matrix, it found one on the first run.

## redact with method='noise' does not replay

    UNSTABLE  redact  on cctv/brightest.jpg with method='noise':
              83667 pixel(s) differ by up to 255

Every other filter, across every parameter variant the sweep drives, returns
identical pixels. This one is different in kind: the output is random **by
design**, and it should be. Noise redaction that produced the same noise every
time would be worse, not better.

But the preset system rests on a chain replaying identically, and this breaks
it silently. Export a preset with a noise redaction in it, replay it, and you
get a different image - equally redacted, not the same file. A report whose
result cannot be reproduced is not evidence.

## The capability existed and was not reachable

`redact()` has had a `seed` parameter all along. `redact_region()` - the
wrapper the registry, the chain, presets, the CLI, the GUI and the dashboard
all use - did not pass it through. So the one entry point anybody actually
uses could not produce a reproducible redaction.

Now exposed, with the reasoning in the docstring:

    same seed reproduces exactly : True
    no seed differs each run     : True
    seeded noise still destroys  : True (residual correlation 0.0008)

Seeding does not weaken the redaction. The original pixels are discarded
either way, so knowing the noise recovers nothing - which is the question
worth asking before adding a seed to anything forensic.

The default stays unseeded. A fixed default would make every redaction
produced by this toolkit identical, which is a worse property than
irreproducibility.

Documented in both languages, PDFs rebuilt, three regression tests added: the
seed reproduces, the default still varies, and a seeded redaction still passes
`verify_redaction`.

## The tool now separates random-by-design from broken

`determinism.py` carries a short list of filters whose output is random on
purpose, with the way to pin each one. `redact` reports as:

    by design redact  method='noise' draws fresh noise each run;
                      pass seed= to make a chain replay identically

Flagging it as UNSTABLE every run would train whoever reads this to skim the
line, which is how a real one gets missed.

## What the extension cost and found

    67 filters x 14 parameter variants x 2 images x 2 runs = 36s

Cheap. It found in one run what twelve hours of default-only checking had not,
and the reason is worth stating: `method='noise'` is not the default, so no
prior sweep had ever exercised it twice on the same input.

The same gap logic applies to the checks. Most assert something about a filter
at or near its defaults; the extremes are exercised for crashes by the
parameter matrix but not for correctness.

## Outstanding

1. The dashboard has no guided point picking - carried since hour 5
2. 38 of 73 entries still have no specific checks
3. Checks test near-default behaviour almost exclusively. `levels` at
   `gamma=3.0` gets run, but nothing asserts what it should produce
4. `--params all` walks 14 variants per filter, one parameter moved at a time.
   Combinations are untested and there are too many to enumerate, so a defect
   needing two extremes at once would still hide
