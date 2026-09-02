# Hour 18 - the dashboard was inverting the wrong channel

**2026-08-21** | 76 entries, 0 needing attention | 753 tests | 301 assertions

Hour 17 closed by noting that nothing verified the product's colour handling
end to end. Writing that test found a live bug in the web dashboard, and it
had been there the whole time.

## Same image, same operation, two different answers

A pure red PNG, and the instruction "invert the red channel":

| | result |
|---|---|
| desktop app | R=0 G=0 B=0 - **red inverted** |
| dashboard | R=255 G=0 B=255 - **blue inverted, red untouched** |

`cv_tools/dashboard.py` converted every upload to BGR on load:

    image = image[:, :, ::-1].copy()  # RGB -> BGR, filters are OpenCV-shaped

The comment is wrong about this codebase. `ImageLoader` converts BGR to RGB on
load and `save_image` converts back, so RGB is the pipeline's colour order
throughout, and the filters expect it.

## What it affected

Nothing that measures luminance. CLAHE, levels, sharpening, denoising, the
edge detectors, every forensic report - all of them convert to greyscale
first, and the weights differ but the operation is the same shape. That is
precisely why it survived: the toolkit's headline filters cannot see it.

What it broke, in the dashboard only:

- `invert_channel`, and the `channel` parameter on `contrast_brightness`,
  `levels` and `curves` - all acting on the opposite channel
- `temperature` - warm and cool exchanged
- `white_balance`, `saturation`, `vibrance`, `color_balance`, `cmyk`,
  `channel_mixer`, `stain`, `component` - every colour-space conversion fed
  reversed input

Three lines removed: the load conversion and the two flips that undid it for
display and export. The desktop app was correct throughout.

## The test that should have existed

`tests/test_colour_pipeline.py`, seven tests pinning the convention at every
boundary a real image crosses:

- the loader returns index 0 as red for a file whose first band is red
- what `save_image` writes is what PIL reads back
- a file round trip preserves every colour exactly
- inverting red turns the red band black **in the saved file**, and adds red
  to the green and blue bands
- a chain and its replayed preset agree pixel for pixel
- the dashboard's load path keeps RGB
- both front ends produce identical pixels from the same file

The fourth of those is the one that fails against the old dashboard. It is
also the one nobody would think to write without having been bitten, which is
the argument for writing it now that we have been.

## Where this sits in the campaign

Hour 16 found the *harness* loading BGR while the product loads RGB, and I
recorded it as an instrument error. It was that - and it was also the thread
that led here. Chasing why a check disagreed with a filter about which index
red lives in took two hours and ended at a real defect in shipped code.

The count over eighteen hours is now roughly eight product defects against
fifteen instrument errors. The instrument errors are not wasted work; two of
them led directly to product defects that nothing else had surfaced.

## Documented

The convention is now stated in both language references, at the top where a
contributor meets it, with the reason it is easy to miss: a luminance
operation cannot tell the difference. PDFs rebuilt.

## Outstanding

1. The dashboard has no guided point picking - carried since hour 5
2. 24 of 67 filters still have no specific checks
3. The GUI's viewer was never checked the way the dashboard just was. Its
   `to_display` assumes RGB and appears correct, and the screenshots through
   this campaign look right, but "appears correct" is what the dashboard
   looked like too
4. Nothing tests a raw file or a video frame for the same property, and both
   take different paths through `ImageLoader`
