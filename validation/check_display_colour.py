"""
Does the desktop viewer show the colours the file contains?

The dashboard looked correct for eighteen hours while inverting the wrong
channel. The desktop app takes a different path - ImageCanvas composes a
frame, `to_display` normalises it, and PIL's `fromarray` hands it to Tk - and
that path has never been checked against a file whose colours are known.

This drives the real widget and reads back what it would have drawn.
"""

import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core import ImageLoader                                # noqa: E402
from src.filters import invert_channel                          # noqa: E402


def primaries() -> np.ndarray:
    frame = np.zeros((24, 96, 3), np.uint8)
    frame[:, :32] = (255, 0, 0)
    frame[:, 32:64] = (0, 255, 0)
    frame[:, 64:] = (0, 0, 255)
    return frame


def main() -> int:
    import tkinter as tk
    from src.gui.widgets import ImageCanvas, to_display

    root = tk.Tk()
    root.withdraw()

    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'primaries.png'
        Image.fromarray(primaries()).save(path)
        with ImageLoader(path) as loader:
            image = loader.load()

    failures = []

    # 1. to_display must not reorder anything
    shown = to_display(image)
    if tuple(shown[0, 0]) != (255, 0, 0):
        failures.append(f'to_display turned the red band into {tuple(shown[0, 0])}')
    print(f'to_display red band      : {tuple(shown[0, 0])}  expected (255, 0, 0)')

    # 2. The composed frame the canvas draws
    canvas = ImageCanvas(root)
    canvas.set_images(image, image)
    composite = canvas._compose()
    print(f'canvas composite red band: {tuple(composite[0, 0])}  expected (255, 0, 0)')
    if tuple(composite[0, 0]) != (255, 0, 0):
        failures.append(f'the canvas composed the red band as {tuple(composite[0, 0])}')

    # 3. What PIL would hand to Tk - the last step before pixels reach a screen
    handed = np.array(Image.fromarray(composite))
    print(f'as PIL receives it       : {tuple(handed[0, 0])}  expected (255, 0, 0)')
    if tuple(handed[0, 0]) != (255, 0, 0):
        failures.append('PIL received a different colour than the canvas composed')

    # 4. A colour operation has to reach the channel named, on screen
    processed = invert_channel(image, channel='r')
    canvas.set_images(image, processed)
    composite = canvas._compose()
    print(f'after inverting red      : {tuple(composite[0, 0])}  expected (0, 0, 0)')
    if tuple(composite[0, 0]) != (0, 0, 0):
        failures.append(f'inverting red showed {tuple(composite[0, 0])} in the viewer')

    # 5. Split view takes its left side from the original and right from the
    #    processed - a swap there would show the wrong image, not the wrong colour
    canvas.set_mode('split')
    split = canvas._compose()
    left = tuple(split[0, 2])
    right = tuple(split[0, split.shape[1] - 3])
    print(f'split view left/right    : {left} / {right}  '
          f'expected (255, 0, 0) / (255, 0, 255)')
    if left != (255, 0, 0):
        failures.append(f'split view left edge is {left}, not the original red')
    # The processed frame has red inverted *everywhere*, so its blue band
    # (0, 0, 255) becomes (255, 0, 255). Expecting plain blue here was my
    # error, not the viewer's.
    if right != (255, 0, 255):
        failures.append(f'split view right edge is {right}, not the processed '
                        f'blue band with red inverted')

    canvas.destroy()
    root.destroy()

    print()
    if failures:
        print(f'{len(failures)} problem(s):')
        for item in failures:
            print(f'  {item}')
        return 1
    print('The desktop viewer shows the colours the file contains.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
