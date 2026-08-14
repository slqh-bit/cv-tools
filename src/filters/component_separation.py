"""
Component Separation - Split an image into its constituent parts.

Detail invisible in a colour composite is often plainly visible in one
component of it. A bloodstain on dark fabric can vanish in RGB but stand out in
the LAB a-channel; a bruise shows better in the blue channel; faint writing
under an overwrite separates in HSV saturation.

Three kinds of separation are offered:

    - **Colour space** - split into R/G/B, H/S/V, L/a/b, Y/Cr/Cb. Cheap, and
      the first thing to try.
    - **Frequency** - split into a smooth base layer and the detail on top of
      it, which isolates texture from shading.
    - **Bit plane** - split into the eight binary planes of the intensity.
      The low planes are usually noise, but they are where LSB steganography
      and some tampering traces live.
"""

from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

# Colour spaces and the channel names they yield, in order
COLOR_SPACES: Dict[str, Tuple[int, Tuple[str, str, str]]] = {
    'rgb': (-1, ('R', 'G', 'B')),
    'hsv': (cv2.COLOR_RGB2HSV, ('H', 'S', 'V')),
    'hls': (cv2.COLOR_RGB2HLS, ('H', 'L', 'S')),
    'lab': (cv2.COLOR_RGB2LAB, ('L', 'a', 'b')),
    'luv': (cv2.COLOR_RGB2LUV, ('L', 'u', 'v')),
    'ycrcb': (cv2.COLOR_RGB2YCrCb, ('Y', 'Cr', 'Cb')),
    'yuv': (cv2.COLOR_RGB2YUV, ('Y', 'U', 'V')),
    'xyz': (cv2.COLOR_RGB2XYZ, ('X', 'Y', 'Z')),
}


def separate_channels(
    image: np.ndarray,
    space: str = 'rgb',
) -> Dict[str, np.ndarray]:
    """
    Split a colour image into the channels of a colour space.

    Args:
        image: Input image (RGB or RGBA)
        space: One of ``COLOR_SPACES``

    Returns:
        Dict mapping channel name to a single-channel uint8 image

    Example:
        >>> channels = separate_channels(frame, 'lab')
        >>> redness = channels['a']
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if space not in COLOR_SPACES:
        available = ', '.join(sorted(COLOR_SPACES))
        raise ValueError(f"Unknown colour space '{space}'. Available: {available}")

    img = image.astype(np.uint8) if image.dtype != np.uint8 else image
    if img.ndim == 2:
        raise ValueError("Channel separation needs a colour image")

    rgb = img[:, :, :3]
    code, names = COLOR_SPACES[space]
    converted = rgb if code == -1 else cv2.cvtColor(rgb, code)

    return {name: converted[:, :, index].copy() for index, name in enumerate(names)}


def extract_component(
    image: np.ndarray,
    space: str = 'lab',
    channel: str = 'L',
    normalize: bool = False,
) -> np.ndarray:
    """
    Return one colour component, for use in a filter chain.

    Args:
        image: Input image
        space: One of ``COLOR_SPACES``
        channel: Channel name within that space, e.g. 'a' in 'lab'
        normalize: Stretch the result to fill 0-255, which makes a narrow
                   channel like LAB's a-channel readable

    Returns:
        Single-channel uint8 image

    Example:
        >>> redness = extract_component(frame, 'lab', 'a', normalize=True)
    """
    channels = separate_channels(image, space)

    if channel not in channels:
        available = ', '.join(channels)
        raise ValueError(
            f"Colour space '{space}' has no channel '{channel}'. Available: {available}"
        )

    result = channels[channel]

    if normalize:
        low, high = float(result.min()), float(result.max())
        if high > low:
            stretched = (result.astype(np.float32) - low) * (255.0 / (high - low))
            result = np.clip(stretched, 0, 255).astype(np.uint8)

    return result


def separate_frequency(
    image: np.ndarray,
    radius: float = 8.0,
    amplify: float = 1.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Split an image into a smooth base layer and its detail layer.

    The base holds shading and broad tone; the detail holds texture and edges.
    Separating them lets each be examined without the other - detail on a
    steeply shaded surface is far easier to read once the shading is removed.

    Args:
        image: Input image
        radius: Blur radius dividing the two layers. Larger puts more into
                the detail layer.
        amplify: Multiplier on the detail layer before it is centred on
                 mid-gray, to make faint texture visible

    Returns:
        ``(base, detail)``. The detail layer is centred on 128, so flat regions
        appear mid-gray rather than black.

    Example:
        >>> base, detail = separate_frequency(surface, radius=12, amplify=3)
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if radius <= 0:
        raise ValueError(f"radius must be positive, got {radius}")
    if amplify <= 0:
        raise ValueError(f"amplify must be positive, got {amplify}")

    img = image.astype(np.uint8) if image.dtype != np.uint8 else image
    rgb = img[:, :, :3] if img.ndim == 3 and img.shape[2] == 4 else img

    base = cv2.GaussianBlur(rgb, (0, 0), sigmaX=radius, sigmaY=radius)
    detail = rgb.astype(np.float32) - base.astype(np.float32)
    detail = np.clip(detail * amplify + 128.0, 0, 255).astype(np.uint8)

    return base, detail


def separate_bit_planes(image: np.ndarray) -> List[np.ndarray]:
    """
    Split the intensity into its eight binary bit planes.

    Plane 7 is the most significant and looks like the image; plane 0 is the
    least and is usually noise. Structure appearing in the low planes is
    notable - natural sensor noise has none, so a pattern there suggests data
    hidden in the least significant bits or a region pasted from elsewhere.

    Args:
        image: Input image; colour is reduced to luminance first

    Returns:
        Eight single-channel uint8 images, index 0 to 7, each 0 or 255

    Example:
        >>> planes = separate_bit_planes(photo)
        >>> planes[0].std() > 100   # structure in the lowest bit
        True
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")

    img = image.astype(np.uint8) if image.dtype != np.uint8 else image
    if img.ndim == 3:
        gray = cv2.cvtColor(img[:, :, :3], cv2.COLOR_RGB2GRAY)
    else:
        gray = img

    return [((gray >> bit) & 1).astype(np.uint8) * 255 for bit in range(8)]


def extract_bit_plane(image: np.ndarray, bit: int = 0) -> np.ndarray:
    """
    Return a single bit plane, for use in a filter chain.

    Args:
        image: Input image
        bit: Which plane, 0 (least significant) to 7 (most)

    Returns:
        Single-channel uint8 image containing only 0 and 255
    """
    if not 0 <= bit <= 7:
        raise ValueError(f"bit must be between 0 and 7, got {bit}")
    return separate_bit_planes(image)[bit]


def channel_grid(
    image: np.ndarray,
    space: str = 'rgb',
    normalize: bool = True,
) -> np.ndarray:
    """
    Render a space's three channels side by side, each labelled.

    Args:
        image: Input image
        space: One of ``COLOR_SPACES``
        normalize: Stretch each channel to fill 0-255 independently

    Returns:
        RGB composite of the three channels

    Example:
        >>> grid = channel_grid(frame, 'lab')
    """
    channels = separate_channels(image, space)

    panels = []
    for name, channel in channels.items():
        panel = channel
        if normalize:
            low, high = float(panel.min()), float(panel.max())
            if high > low:
                panel = np.clip(
                    (panel.astype(np.float32) - low) * (255.0 / (high - low)), 0, 255
                ).astype(np.uint8)

        panel = cv2.cvtColor(panel, cv2.COLOR_GRAY2RGB)

        scale = max(0.4, min(1.0, panel.shape[1] / 500.0))
        thickness = max(1, int(scale * 2))
        (text_w, text_h), _ = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX,
                                              scale, thickness)
        cv2.rectangle(panel, (5, 5), (15 + text_w, 15 + text_h), (0, 0, 0), -1)
        cv2.putText(panel, name, (10, 10 + text_h), cv2.FONT_HERSHEY_SIMPLEX,
                    scale, (255, 255, 255), thickness, cv2.LINE_AA)
        panels.append(panel)

    return np.hstack(panels)
