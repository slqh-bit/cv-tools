# cv-tools

A modular Python image processing toolkit inspired by Amped FIVE forensic image enhancement.

Filters are applied as an **ordered chain**, every step is recorded, and the chain can be
exported as a JSON preset or a forensic-style processing report.

## Filters

**Sprint 1 — Adjust & Correct**

| Filter | File | Description |
|--------|------|-------------|
| CLAHE | `filters/clahe.py` | Contrast Limited Adaptive Histogram Equalization |
| ROI | `filters/roi.py` | Region of Interest selection, extraction, analysis |
| Contrast & Brightness | `filters/contrast_brightness.py` | Linear adjustment (+ gamma, auto-contrast) |
| Levels | `filters/levels.py` | Histogram black/mid/white point adjustment |
| Histogram Equalization | `filters/histogram_equalization.py` | Global histogram equalization |
| Crop & Resize | `filters/crop_resize.py` | Crop, resize, rotate, flip |

**Sprint 2 — Enhance & Analyze**

| Filter | File | Description |
|--------|------|-------------|
| Sharpen | `filters/sharpen.py` | Unsharp mask and Laplacian sharpening |
| Smoothing | `filters/smoothing.py` | Gaussian blur, median filter, bilateral filter |
| Edge Detection | `filters/edge_detection.py` | Canny, auto-Canny, Sobel, Laplacian |
| Histogram | `filters/histogram.py` | Histogram display, tonal stats, clipping detection |

**Sprint 3 — Forensic & Advanced**

| Filter | File | Description |
|--------|------|-------------|
| ELA | `filters/ela.py` | Error Level Analysis |
| FFT Analysis | `filters/fft_analysis.py` | Spectrum, frequency filtering, periodic noise removal |
| Noise Analysis | `filters/noise_analysis.py` | Noise sigma, SNR, per-block noise map |
| Clone Detection | `filters/clone_detection.py` | Copy-move forgery detection |
| JPEG Ghost | `filters/jpeg_ghost.py` | Per-block prior JPEG quality from pixel evidence |
| Metadata Forensics | `filters/metadata_forensics.py` | EXIF and JPEG segment inconsistencies |
| Motion Deblur | `filters/motion_deblur.py` | Wiener deconvolution, PSF construction |
| Frame Averaging | `filters/frame_averaging.py` | Multi-frame denoise, background reconstruction |

**Remaining catalogue — Adjust, Enhance, Correct, Special**

| Filter | File | Description |
|--------|------|-------------|
| Curves | `filters/curves.py` | Control-point tonal curve with presets |
| White Balance | `filters/white_balance.py` | Auto, from-patch, and manual temperature |
| Saturation | `filters/saturation.py` | Saturation, vibrance, desaturate, selective hue |
| Colour Balance | `filters/color_balance.py` | Per-tonal-range RGB, CMYK, channel mixer |
| Invert | `filters/invert.py` | Full, per-channel, luminance-only, solarize |
| NL Means | `filters/nl_means_denoise.py` | Non-local means, single and multi-frame |
| Super-Resolution | `filters/super_resolution.py` | Multi-frame reconstruction, upscaling |
| Detail Enhancement | `filters/detail_enhancement.py` | Local contrast, multiscale, texture boost |
| Perspective | `filters/perspective_correction.py` | Four-point rectification, corner detection |
| Fisheye | `filters/fisheye_correction.py` | Barrel and equidistant fisheye correction |
| Aspect Ratio | `filters/aspect_ratio.py` | Pixel aspect correction, frame fitting |
| Undistort | `filters/undistort.py` | Chessboard calibration and lens correction |
| Compression | `filters/compression_analysis.py` | Blocking measures, JPEG quality, deblock |
| Colour Deconvolution | `filters/color_deconvolution.py` | Separate overlapping colorants |
| Component Separation | `filters/component_separation.py` | Colour spaces, frequency, bit planes |
| Redaction | `filters/redaction.py` | Irreversible obscuring, with verification |
| Annotate | `filters/annotate.py` | Arrows, shapes, text, and calibrated measurement |
| Measure 3D | `filters/measure_3d.py` | Object height from one view, by single-view metrology |

See [docs/filters.md](docs/filters.md) for the full parameter reference.

> **On the forensic filters.** ELA, clone detection, noise analysis and JPEG ghost detection
> locate things *worth examining*; none of them establishes that an image was manipulated.
> Texture raises ELA error levels, genuine repetition (tiles, windows, text) is real
> duplication, and any re-save destroys the traces these tools read — a JPEG ghost's blind
> spot is a uniform resave of the whole composite, which erases any single region's earlier
> history. Metadata is plain text anyone can edit, and most platforms strip it on upload, so
> a clean header is the normal state of an ordinary file rather than evidence of anything.
> Deconvolution with a guessed PSF invents detail that was never recorded. Read
> [docs/filters.md](docs/filters.md) before relying on any of them.

## Installation

```bash
pip install -r requirements.txt
```

Camera raw support needs `rawpy`, which is in `requirements.txt` but is a large binary
dependency — everything except raw decoding works without it, and raw files give a clear
install message if it is missing.

Generate the sample test images and video:

```bash
python samples/generate_samples.py
```

This writes a dark CCTV-style plate scene, a low-contrast grey chart, a colour chart, a
forged image containing a copy-pasted region, an image with periodic interference, a JPEG
original for ELA, a composite whose centre region carries a different JPEG quality (for
ghost detection), and a 24-frame video of a static scene with one moving object.

## CLI Usage

Run from the project root. Filters apply **in the order written on the command line**.

```bash
# CLAHE enhancement
python -m src.cli input.jpg --clahe clip=2.0 tile=8x8 -o output.jpg

# ROI crop (x,y,width,height)
python -m src.cli input.jpg --roi 100,100,300,200 -o cropped.jpg

# Brightness + Contrast
python -m src.cli input.jpg --brightness 30 --contrast 1.5 -o adjusted.jpg

# Levels adjustment (black,gamma,white)
python -m src.cli input.jpg --levels 20,1.0,220 -o leveled.jpg

# Histogram equalization
python -m src.cli input.jpg --histeq mode=lab -o equalized.jpg

# Chain filters — order matters
python -m src.cli input.jpg --brightness 20 --clahe clip=3.0 --resize 50% -o out.jpg
```

### Colour adjustment

```bash
# Tonal curve, by preset or explicit control points
python -m src.cli input.jpg --curves preset=lift_shadows -o out.jpg
python -m src.cli input.jpg --curves points=0:0,128:170,255:255 -o out.jpg

# White balance: automatic, or measured from a region known to be neutral
python -m src.cli input.jpg --white-balance method=shades_of_gray -o out.jpg
python -m src.cli input.jpg --wb-patch 300,200,40,30 -o out.jpg

# Saturation, vibrance (protects already-vivid colours), and grayscale
python -m src.cli input.jpg --saturation 1.4 -o out.jpg
python -m src.cli input.jpg --vibrance 1.5 -o out.jpg
python -m src.cli input.jpg --desaturate lightness -o out.jpg

# Colour balance per tonal range, and inversion
python -m src.cli input.jpg --color-balance shadows=-15:0:15 highlights=15:5:-10 -o out.jpg
python -m src.cli negative.jpg --invert -o positive.jpg
```

### Geometric correction

```bash
# Rectify a surface from its four corners, with a known real-world ratio
python -m src.cli plate.jpg --perspective 120,80,500,60,530,300,100,320 \
    --perspective-ratio plate_eu -o flat.jpg

# Lens distortion: by eye, or from a real camera calibration
python -m src.cli wide.jpg --barrel k1=-0.25 zoom=1.15 -o straight.jpg
python -m src.cli dome.jpg --fisheye strength=0.6 zoom=1.2 -o flat.jpg
python -m src.cli frame.jpg --undistort calibration.json -o corrected.jpg

# Square up non-square pixels from SD video
python -m src.cli pal.png --pixel-aspect pal_43 -o square.png
```

### Separation and redaction

```bash
# Isolate a colour component - detail invisible in RGB often shows in LAB
python -m src.cli input.jpg --component lab:a -o redness.png

# Bit planes: structure in the low planes is worth a second look
python -m src.cli input.jpg --bit-plane 0 -o lsb.png

# Separate overlapping inks
python -m src.cli document.jpg --stain preset=blue_black_ink index=0 -o ink.png

# Redact. fill and noise destroy the content; blur and pixelate are recoverable
python -m src.cli input.jpg --redact 120,80,200,40 -o safe.jpg
python -m src.cli input.jpg --redact 120,80,200,40 --redact-method blur -o preview.jpg

# Compression history
python -m src.cli evidence.jpg --compression-stats
```

### Enhance and denoise

```bash
# Unsharp mask — threshold protects flat areas from noise amplification
python -m src.cli input.jpg --sharpen amount=1.5 radius=1.0 threshold=4 -o sharp.jpg

# Denoise: gaussian (general), median (salt-and-pepper), bilateral (edge-preserving)
python -m src.cli input.jpg --gaussian 1.5 -o soft.jpg
python -m src.cli input.jpg --median 3 -o despeckled.jpg
python -m src.cli input.jpg --bilateral d=9 color=75 space=75 -o denoised.jpg

# Non-local means: slower than bilateral, but keeps repeating texture
python -m src.cli input.jpg --nl-means h=12 -o denoised.jpg
python -m src.cli input.jpg --nl-means-auto -o denoised.jpg

# Local contrast ("clarity") and texture enhancement
python -m src.cli input.jpg --local-contrast radius=25 strength=0.6 -o clearer.jpg
python -m src.cli input.jpg --detail-enhance sigma_s=10 sigma_r=0.15 -o detailed.jpg

# Typical forensic order: denoise, enhance contrast, then sharpen
python -m src.cli plate.jpg --roi 240,280,180,80 --resize 300% \
    --bilateral d=7 color=40 --clahe clip=3.0 tile=4x4 \
    --sharpen amount=1.4 radius=1.5 threshold=6 -o plate_enhanced.jpg
```

### Measurement

Measuring needs a scale, and a scale is valid only for the plane it was measured in.
Correct perspective first — a calibration taken on the ground says nothing about a sign
further from the camera.

```python
from src.filters import Scale, scale_from_reference, measure_distance, draw_measurement

# Calibrate from something of known size in the rectified plane
scale = scale_from_reference((100, 200), (340, 200), 520, 'mm')   # EU plate width

measure_distance((100, 200), (220, 260), scale)['distance']
marked = draw_measurement(flat, (100, 200), (220, 260), scale)
```

### Measuring height (3D)

A scale calibrated on the ground cannot give you the height of someone standing on it —
height runs out of the plane the scale lives in. `measure_3d` recovers it from the ground
plane's horizon, the vanishing point of scene verticals, and one object of known height
standing on that same ground.

```bash
# Horizon as a single row works for a level camera; give the vertical vanishing
# point as well for a tilted one, which most CCTV is
python -m src.cli scene.jpg --measure-3d \
    base=352,408 top=352,264 reference_base=160,374 reference_top=160,250 \
    horizon=144 reference_height=1800 -o measured.jpg
```

```python
from src.filters import measure_height, vanishing_point, horizon_from_vanishing_points

# Recover the geometry from lines already in the scene
horizon = horizon_from_vanishing_points(
    vanishing_point([(80, 300, 400, 250), (90, 420, 430, 330)]),   # one ground direction
    vanishing_point([(120, 250, 150, 430), (300, 240, 360, 420)]), # another
)
vertical = vanishing_point([(160, 250, 160, 374), (352, 264, 352, 408)])

result = measure_height(
    base=(352, 408), top=(352, 264),
    reference_base=(160, 374), reference_top=(160, 250),
    reference_height=1800, horizon=horizon, vertical_point=vertical,
)
result['height'], result['uncertainty_per_pixel']
```

> **Read the uncertainty.** Both objects must stand on the *same* ground plane, lens
> distortion must be corrected first, and accuracy collapses as the base approaches the
> horizon. `uncertainty_per_pixel` reports how far the answer moves for a one-pixel error
> in the clicked points — a floor on the error, not the whole of it. See
> [docs/filters.md](docs/filters.md).

### Edge detection

Edge detectors return a single-channel map, so they turn a color image grayscale mid-chain.

```bash
python -m src.cli input.jpg --canny 50,150 -o edges.jpg

# Thresholds derived from the image median — useful across varied exposures
python -m src.cli input.jpg --auto-canny --blur-first 1.5 -o edges.jpg

python -m src.cli input.jpg --sobel dx=1 dy=1 kernel=3 -o gradients.jpg
python -m src.cli input.jpg --laplacian kernel=3 blur=1.0 -o laplacian.jpg
```

### Forensic analysis

```bash
# Error Level Analysis — meaningful only on JPEG originals
python -m src.cli photo.jpg --ela quality=90 -o ela.png
python -m src.cli photo.jpg --ela-stats

# Copy-move forgery detection (highlights both the source and the paste)
python -m src.cli photo.jpg --clone-stats
python -m src.cli photo.jpg --clone-detect -o clones.png

# Noise level, SNR, and per-block uniformity
python -m src.cli photo.jpg --noise-stats
python -m src.cli photo.jpg --noise-map 32 -o noise.png

# JPEG ghost detection — per-block prior compression quality from pixels alone
python -m src.cli photo.jpg --ghost-stats
python -m src.cli photo.jpg --ghost block=16 min=50 max=100 step=5 -o ghost.png

# EXIF and JPEG segment inconsistencies — reads the file header, not the pixels
python -m src.cli photo.jpg --metadata-stats

# Frequency domain: spectrum, filtering, and periodic pattern removal
python -m src.cli scan.png --fft -o spectrum.png
python -m src.cli scan.png --remove-periodic -o cleaned.png
python -m src.cli scan.png --fft-filter type=lowpass cutoff=30 -o smoothed.png

# Wiener deblurring — you must supply the correct PSF
python -m src.cli blurred.jpg --deblur length=15 angle=30 noise=0.01 -o sharp.jpg
python -m src.cli blurred.jpg --deblur-defocus radius=5 noise=0.01 -o sharp.jpg
```

### Multi-frame video processing

`--frames N` builds the source image from N video frames instead of one.

```bash
# Average 24 frames to suppress sensor noise
python -m src.cli clip.avi --frames 24 -o clean.png

# Median composite: removes anything that moved, leaving the background
python -m src.cli clip.avi --frames 24 --frame-method median -o background.png

# Brighten very dark footage by accumulating light
python -m src.cli clip.avi --frames 30 --frame-method integrate -o brightened.png

# Average only the best-focused half of the frames
python -m src.cli clip.avi --frames 20 --frame-method sharpest -o sharpest.png

# Spread the sample over a longer span to clear a slow-moving object
python -m src.cli clip.avi --frames 12 --frame-step 5 --frame-method median -o bg.png
```

### Analysis and reporting

```bash
# Source metadata: dimensions, EXIF, SHA-256
python -m src.cli input.jpg --info

# Per-channel statistics for a region of the processed image
python -m src.cli input.jpg --clahe --analyze-roi 270,300,110,36

# Histogram chart of the processed image
python -m src.cli input.jpg --clahe --histogram hist.png -o out.jpg

# Tonal stats: dynamic range used, plus shadow/highlight clipping
python -m src.cli input.jpg --hist-stats

# Side-by-side original vs processed
python -m src.cli input.jpg --clahe clip=3.0 --compare compare.png -o out.jpg

# Processing report — .md, .json or .pdf chosen by extension
python -m src.cli input.jpg --clahe --levels 10,1.1,200 --report report.md -o out.jpg
python -m src.cli input.jpg --clahe --report report.pdf -o out.jpg
```

### Presets and batch processing

```bash
# Save the applied chain as a reusable preset
python -m src.cli input.jpg --brightness 30 --clahe clip=2.5 \
    --save-preset plate.json -o out.jpg

# Replay it on another image
python -m src.cli other.jpg --load-preset plate.json -o other_out.jpg

# Apply to every image in a directory
python -m src.cli frames/ --load-preset plate.json --batch -o enhanced/

# Include subdirectories; the output mirrors the input tree
python -m src.cli frames/ --load-preset plate.json --batch --recursive -o enhanced/

# List every registered filter, or every analysis report
python -m src.cli --list-filters
python -m src.cli --list-analyses
```

The `--*-stats` flags are generated from the analysis registry, so a report added there is
reachable from the command line, the GUI and the dashboard without any of the three being
edited.

Video input is supported for still extraction — use `--frame N` to pick the frame.

Supported inputs: PNG, JPEG (including `.jfif`), BMP, TIFF, WebP, NetPBM; camera raw
(CR2/CR3, NEF, ARW, ORF, RW2, RAF, PEF, DNG and others) via `rawpy`; and MP4, AVI, MKV,
MOV, WMV, FLV, MPEG video.

Raw files are decoded with the camera's own white balance and **no automatic brightness
stretch**, so the exposure you see is the exposure that was recorded. Override with
`ImageLoader(path, raw_options={...})`, which passes through to rawpy's `postprocess`.

## GUI

```bash
python -m src.gui
```

Optionally with a file to open at startup:

```bash
python -m src.gui samples/cctv_dark.png
```

| Panel | What it does |
|---|---|
| Left | The filter chain, with reorder, duplicate and remove; below it the filter picker, grouped by family and searchable |
| Centre | Image viewer — processed, original, **split**, or side-by-side, with fit/100%/200%/400% and Ctrl+wheel zoom |
| Right | Parameters for the selected filter — or for the selected chain step, to correct it in place |
| Bottom | **Statistics**: live histogram, source metadata with SHA-256, per-channel clipping. **Analysis**: the forensic reports |

The split view puts the original left of a draggable divider and the processed image right
of it — the eye compares far better across an edge than across a gap. Magnified views use
nearest-neighbour so you see the actual pixels rather than a smoothed guess.

The parameter forms are built by introspecting each filter's signature, so every registered
filter has a working panel and a filter added later needs no GUI work.

Selecting a step in the chain loads its own parameters into the panel; **Update selected
step** re-applies it and re-processes everything after it, so an early value can be
corrected without rebuilding the chain by hand.

The window is dark by default — a bright surround biases the eye when judging shadow
detail, which is most of what a CCTV frame is. *View → Theme* switches to light.

Everything runs through the same `Pipeline` and registry the CLI uses, so undo/redo,
reordering, presets and reports behave identically — **a preset saved in the GUI replays in
the CLI and vice versa**.

### Analysis reports

The bottom **Analysis** tab runs the measurements that describe an image without changing
it — the same six the CLI prints, from the same registry:

| Report | Reads | What it measures |
|---|---|---|
| `noise` | pixels | Noise sigma, SNR, and how evenly noise is spread across the frame |
| `ela` | pixels | Block-level recompression error and its outliers |
| `clone` | pixels | Duplicated regions and the shifts relating them |
| `compression` | pixels + file | Blocking measures, plus the quality read from the JPEG's own tables |
| `ghost` | pixels | Per-block prior JPEG quality, and the blocks that disagree |
| `metadata` | file | EXIF tags, JPEG segments, and the contradictions between them |

Findings worth investigating are coloured; every report ends with a note saying what it
cannot tell you. `compression` and `metadata` read the container rather than the pixels, so
they describe the file that was opened, not the chain's output.

Adding an entry to `filters.analysis.ANALYSIS_REGISTRY` makes it appear in the CLI, the GUI
and the dashboard at once — none of the three front ends names the reports individually.

## Dashboard

The same tool in a browser, for a phone or a machine without a display:

```bash
pip install -r requirements.txt -r requirements-dashboard.txt
streamlit run src/dashboard.py
```

| Tab | What it does |
|---|---|
| Viewer | Processed / original / side-by-side, coordinate grid or tap-to-pick, histogram and stat tiles |
| Analysis | The reports above, run on demand |
| Export | Processed PNG, preset JSON, and the processing report as Markdown or JSON |

The sidebar holds the source, the chain (reorder, remove, undo/redo) and the filter picker,
grouped by family exactly as the desktop GUI groups it.

A browser hands over bytes rather than a file, so the dashboard writes the upload to a
temporary copy under its own name — `metadata` and `compression` need the container, and a
report headed `tmp8f3a1.jpg` is no use as a record of what was examined.

Since a browser cannot report the pixel under the cursor the way the desktop viewer does,
the coordinate grid draws the numbers into the displayed image, and tap-to-pick reads them
off a tap. Both are display-only; the download stays clean.

Set `CVTOOLS_PASSWORD` to put a password gate in front of the app before publishing it over
a tunnel.

## Library Usage

```python
from src.core import ImageLoader, Pipeline, ReportGenerator, save_image
from src.filters import apply_clahe, adjust_levels

with ImageLoader('input.jpg') as loader:
    image = loader.load()
    metadata = loader.metadata

pipeline = Pipeline(image)
pipeline.apply(apply_clahe, 'clahe', 'src.filters.clahe', {'clip_limit': 3.0})
pipeline.apply(adjust_levels, 'levels', 'src.filters.levels', {'black_point': 10})

pipeline.undo()                     # step back through the chain
result = pipeline.redo()

save_image(result, 'output.jpg')
ReportGenerator(pipeline.generate_report(), metadata).save('report.md')
```

### Loading directories and navigating video

```python
from src.core import ImageLoader

# Every loadable still in a directory, lazily so large sets need not fit in memory
for path, image in ImageLoader.load_directory('frames/', recursive=True):
    print(path.name, image.shape)

paths = ImageLoader.find_images('frames/')     # just the paths

# Frame navigation
with ImageLoader('clip.mp4') as loader:
    frame = loader.goto_frame(120)
    nxt = loader.next_frame()                  # None at the end of the video
    prev = loader.previous_frame()             # None at the start
    print(loader.current_frame_index)
```

### Editing the chain

`replace_chain` rebuilds the whole chain from the original image, which is how you reorder
or drop steps. It takes a resolver mapping each step's name to its function —
`filter_function` covers every registered filter.

```python
from src.core import FilterStep
from src.filters import filter_function

# Reorder: CLAHE before the brightness lift instead of after
pipeline.replace_chain(list(reversed(pipeline.chain)), filter_function)

# Drop a step
pipeline.replace_chain(
    [step for step in pipeline.chain if step.name != 'contrast_brightness'],
    filter_function,
)

# Rebuild from a saved preset
preset = pipeline.load_preset('plate.json')
pipeline.replace_chain(
    [FilterStep.from_dict(step) for step in preset['filters']], filter_function
)
```

If any step fails to resolve or apply, the pipeline is left exactly as it was — a chain that
cannot be rebuilt never replaces one that works.

To append a preset on top of the current chain instead of replacing it, use
`filters.apply_preset(pipeline, preset)`.

## Tests

```bash
python -m unittest discover -s tests -t .
```

716 tests. Run one file or one case:

```bash
python -m unittest tests.test_forensic
python -m unittest tests.test_filters.TestClahe.test_increases_contrast -v
```

The GUI tests skip automatically where Tkinter has no display, and the dashboard tests
where Streamlit is not installed.

## Trying every filter

The tests prove the filters are correct; this shows what they look like. It runs all 67
with their default parameters, writes one PNG each, and tiles them into a labelled contact
sheet.

```bash
python scripts/filter_gallery.py
python scripts/filter_gallery.py samples/cloned_region.png -o gallery/
python scripts/filter_gallery.py --only clahe,sharpen,curves
```

Exit status is non-zero if any filter fails, so it doubles as a smoke test.

A filter that reads a property the default sample lacks renders from its own source
instead, listed in the script's `SOURCES` table — `ghost` needs an image with real JPEG
history, and comes out uniformly white on a never-compressed PNG.

## Project Structure

```
cv-tools/
├── src/
│   ├── core/         # Pipeline engine, loader, report
│   ├── filters/      # Image processing filters + filter and analysis registries
│   ├── gui/          # Optional Tkinter interface
│   ├── utils/        # Argument parsing, comparison rendering
│   ├── cli.py        # Command-line interface
│   └── dashboard.py  # Optional Streamlit web interface
├── .streamlit/       # Dashboard theme
├── tests/            # Unit tests
├── samples/          # Sample image and video generator
└── docs/             # Filter parameter reference
```

## Roadmap

- **Sprint 1 (done)** — CLAHE, ROI, contrast/brightness, levels, histogram equalization,
  crop/resize, pipeline with undo/redo, presets, reports, CLI, batch mode
- **Sprint 2 (done)** — sharpen/unsharp mask, gaussian/median/bilateral smoothing,
  edge detection, histogram display and tonal analysis
- **Sprint 3 (done)** — ELA, FFT analysis and periodic noise removal, noise analysis,
  clone detection, Wiener deblurring, multi-frame video integration
- **Remaining catalogue (done)** — curves, white balance, saturation, colour balance,
  invert; non-local means, super-resolution, detail enhancement; perspective, fisheye,
  aspect ratio, calibration-based undistort; compression analysis; colour deconvolution,
  component separation, redaction, annotation and measurement

- **GUI (done)** — the Phase 5 Tkinter interface, and the Streamlit dashboard beside it

**The plan is complete**: all 40 catalogue filters across 66 registered chain filters, the
core engine, CLI, preset and report systems, batch and multi-frame processing, and the
optional GUI.
