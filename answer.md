# Interview Answer — Follow-up 1

**Question:** *Name the 2–3 established forensic video/image tools that practitioners actually use for CCTV analysis — for example, the one you said cv-tools is modelled on — and for each, what did you observe about it that shaped a design decision in your toolkit?*

---

## 0. Framing

One product is named throughout this codebase — **Amped FIVE** — and it is named in the docstrings of exactly the design decisions it drove:

| Location | Reference |
|---|---|
| `README.md:3` | "inspired by Amped FIVE forensic image enhancement" |
| `cv_tools/core/pipeline.py:33` | "Mirrors Amped FIVE's chain-based workflow" |
| `cv_tools/core/report.py:51` | "Generate Markdown report (similar to Amped FIVE reports)" |
| `cv_tools/utils/compare.py:2` | "Amped FIVE's original-vs-processed view" |
| `cv_tools/filters/clahe.py:116` | "like Amped FIVE's preview" |
| `cv_tools/filters/motion_deblur.py:298` | "the one Amped FIVE's preview encourages" |

So: **one modelled-on product, a landscape I can name around it, and an explicit statement of what I used as a reference instead of a bench comparison.** No claim of hands-on lab time with a licence I did not have.

---

## 1. Amped FIVE (Amped Software) — the tool cv-tools is modelled on

Four observations, four design decisions:

| Observed in FIVE | Decision in cv-tools |
|---|---|
| The workflow is a **chain**, not a stack of destructive edits — every step is listed, reorderable, and the original is never touched | `Pipeline` keeps `_original` immutable and records each step as a `FilterStep` dataclass (name, module, params, ISO timestamp) with undo/redo and JSON preset export — `cv_tools/core/pipeline.py` |
| The **report is a deliverable**, not an export afterthought — the point of the tool is that another examiner can reproduce your chain | `cv_tools/core/report.py` emits Markdown / JSON / PDF including the source file hash, so the chain is replayable by a third party. PDF renders through matplotlib because it was already a dependency — no extra install between the analyst and a court-presentable document |
| Parameters that **cannot be estimated reliably** get a preview grid, not an "auto" button | `apply_clahe_grid()` and `deblur_sweep()` render labelled parameter grids. The deblur docstring says it outright: blur length and angle cannot be read off the image reliably, so sweep the parameters and judge by eye — `cv_tools/filters/motion_deblur.py:298` |
| Filters are grouped by **function family** (Adjust / Enhance / Correct / Analyze / Special), and there is always an original-vs-processed view | `cv_tools/utils/compare.py` for the split view; commit `6ff67aa` specifically regrouped the dashboard from A–Z into those families |

## 2. Amped Authenticate — the authentication counterpart, and the reason Sprint 3 exists

ELA, JPEG ghost, clone detection, noise analysis, metadata/EXIF inconsistency **is** the Authenticate feature set, and that is the Sprint 3 list in this repo.

The more important thing taken from that category of tool is **epistemic**: these tools surface *indicators*, they do not return verdicts. So no filter in cv-tools returns `manipulated: true`.

The README carries the caveat block explicitly:

- texture raises ELA error levels
- genuine repetition (tiles, windows, text) is real duplication
- a uniform re-save of the whole composite erases any single region's JPEG-ghost history
- metadata is plain text anyone can edit, and most platforms strip it on upload — so a clean header is the normal state of an ordinary file, not evidence of anything
- deconvolution with a guessed PSF invents detail that was never recorded

`metadata_forensics.py` returns flags with prose explaining what each one does *not* prove.

## 3. iNPUT-ACE / Axon Investigate (and DVR Examiner) — the acquisition tier I deliberately did not compete with

Their real moat is proprietary DVR demuxing: hundreds of vendor-specific containers and codecs, frame-accurate timing recovery, correct display-aspect handling on anamorphic footage. Two consequences:

- **Scope decision.** cv-tools starts *after* decode. `ImageLoader` accepts what OpenCV / FFmpeg can already open (plus camera raw via an optional `rawpy` import) and makes no attempt at proprietary DVR formats. Reimplementing that badly is worse than not implementing it.
- **What I did take.** The aspect problem is real even post-decode — D1 CCTV at 704×480 displayed as 4:3 makes every measurement wrong — hence `aspect_ratio.py` for pixel-aspect correction, and the hard rule in `measure_3d.py` that lens distortion must be corrected (`undistort.py`, `fisheye_correction.py`) *before* any metrology, because straight lines that image as curves put the vanishing geometry wrong before the arithmetic starts.

On the open-source side, the workstation equivalents are **VideoCleaner**, **ForeVid**, and **Forensically** for browser-side ELA / clone / noise triage.

---

## 4. The honest clause

> I did not have a FIVE or Authenticate licence. My exposure was their published documentation, tech notes, and the literature behind each filter — so what I modelled was the *workflow*, not benchmarked output. I never ran the same clip through both and diffed the pixels.

### What I used as a performance reference instead

1. **Synthetic ground truth with known answers.** `tests/test_measure_3d.py` builds a synthetic camera, projects objects of known height, and checks the recovered value. That produced a quantified error budget rather than a vibe: against a camera 2.5 m up with a 1.8 m reference, assuming scene verticals image as parallel over-reads by roughly **+16 mm at 5° of pitch and +33 mm at 18°**. `measure_height` also reports a per-pixel sensitivity, because accuracy collapses as the base approaches the horizon.
2. **The papers as the reference implementation.** Single-view metrology follows Criminisi, Reid & Zisserman, *Single View Metrology*, IJCV 40(2), 2000 — the cross-ratio formulation is written out in the module docstring. JPEG ghost and ELA follow the published methods. The paper is the spec; the test asserts against it.
3. **OpenCV as the numerical baseline** for anything that exists in both, plus seeded and deterministic tests (`test_noise_is_reproducible_with_a_seed`) so that a chain replays identically — which matters more than raw output quality for anything that has to be reproducible.

### What that reference base cannot tell me

How these filters behave on **real degraded CCTV** — heavy H.264 blocking, IR-illuminated night footage, 12 fps recorders. That is the gap, and closing it needs a trial licence or a labelled real-world corpus, not more unit tests.

---

## 5. The 90-second version, if cut off

> Amped FIVE is the model — chain-based non-destructive workflow, reports as a first-class deliverable, parameter sweeps instead of fake auto-detect. Amped Authenticate shaped the forensic filter set and, more importantly, the rule that no filter returns a verdict. iNPUT-ACE / Axon Investigate defined what I *didn't* build — proprietary DVR decoding — but taught me the aspect-ratio and lens-distortion traps that break measurement. I had no licence for any of them, so my references were synthetic ground truth with known answers, the source papers, and OpenCV as a numerical baseline.

---

## 6. Detail to keep in your pocket if they probe further

`cv_tools/filters/redaction.py` refuses to treat blur and pixelate as safe:

- **Blur is reversible.** A Gaussian blur is a known, invertible convolution — and *this same toolkit ships the Wiener deconvolution that reverses it* (`motion_deblur.py`).
- **Pixelation is reversible for short known-alphabet text.** Each block is the mean of its pixels; rendering every candidate plate or postcode and matching block means is a documented and cheap attack.

Only `fill` and `noise` discard the original pixels. `fill` is the default and the only method for a document intended for release; `blur` and `pixelate` remain available for previews but warn, and `verify_redaction` tells you whether what you produced is recoverable.

That is the detail that shows the adversary was considered, not just the feature list.
