"""
Colour Deconvolution - Separate overlapping colorants.

When two colorants overlap - ink written over a printed form, a stamp across a
signature, a stain on a document - the observed colour is their combination.
Ordinary channel extraction cannot pull them apart because each colorant
contributes to all three channels.

Colorant absorption is multiplicative in transmitted light but *additive* in
optical density, so the separation is done there: convert to density, solve the
linear system given each colorant's density vector, and each colorant's
contribution comes out as its own image.

The method is Ruifrok and Johnston's stain deconvolution, standard in
histology and directly applicable to questioned documents.

Two constraints worth knowing: the colorants' colour vectors must be known or
measurable, and at most three can be separated - three channels give three
equations. Colorants whose vectors are nearly parallel separate poorly, and no
amount of processing fixes that.
"""

from typing import Dict, List, Optional, Sequence, Tuple

import cv2
import numpy as np

# Stain vectors as (R, G, B) absorbance directions. The document ones describe
# common writing and printing colorants.
STAIN_PRESETS: Dict[str, List[Tuple[float, float, float]]] = {
    # Haematoxylin / Eosin / DAB, the histology standards this method comes from
    'h_e': [(0.650, 0.704, 0.286), (0.072, 0.990, 0.105)],
    'h_dab': [(0.650, 0.704, 0.286), (0.268, 0.570, 0.776)],
    'h_e_dab': [(0.650, 0.704, 0.286), (0.072, 0.990, 0.105), (0.268, 0.570, 0.776)],
    # Document work: blue ballpoint over black toner, and red stamp ink
    'blue_black_ink': [(0.850, 0.520, 0.090), (0.577, 0.577, 0.577)],
    'red_blue_ink': [(0.210, 0.850, 0.480), (0.850, 0.520, 0.090)],
}


def normalize_vectors(vectors: Sequence[Sequence[float]]) -> np.ndarray:
    """
    Normalise colorant vectors to unit length and complete the basis.

    With only two colorants given, a third orthogonal vector is generated so
    the 3x3 system can be inverted; its output channel is the residual, the
    part of the image neither colorant explains.

    Args:
        vectors: One to three (R, G, B) absorbance directions

    Returns:
        (3, 3) array of unit vectors
    """
    array = np.asarray(vectors, dtype=np.float64)
    if array.ndim != 2 or array.shape[1] != 3:
        raise ValueError(f"Expected a list of (R, G, B) vectors, got shape {array.shape}")
    if not 1 <= array.shape[0] <= 3:
        raise ValueError(f"Between 1 and 3 colorants can be separated, got {array.shape[0]}")

    basis = np.zeros((3, 3), dtype=np.float64)
    for index, vector in enumerate(array):
        length = np.linalg.norm(vector)
        if length <= 0:
            raise ValueError(f"Colorant vector {index} has zero length")
        basis[index] = vector / length

    if array.shape[0] == 1:
        # Two arbitrary orthogonal directions complete the basis
        first = basis[0]
        helper = np.array([1.0, 0.0, 0.0]) if abs(first[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
        basis[1] = np.cross(first, helper)
        basis[1] /= np.linalg.norm(basis[1])
        basis[2] = np.cross(first, basis[1])
    elif array.shape[0] == 2:
        third = np.cross(basis[0], basis[1])
        length = np.linalg.norm(third)
        if length < 1e-6:
            raise ValueError(
                "The two colorant vectors are parallel, so they cannot be separated"
            )
        basis[2] = third / length

    if abs(np.linalg.det(basis)) < 1e-9:
        raise ValueError(
            "Colorant vectors are linearly dependent and cannot be separated"
        )

    return basis


def deconvolve_colors(
    image: np.ndarray,
    vectors: Optional[Sequence[Sequence[float]]] = None,
    preset: Optional[str] = None,
) -> List[np.ndarray]:
    """
    Split an image into its colorant contributions.

    Args:
        image: Input image (RGB or RGBA)
        vectors: One to three (R, G, B) absorbance directions
        preset: Name from ``STAIN_PRESETS``, used instead of ``vectors``

    Returns:
        Three single-channel uint8 images, one per basis vector. Dark means a
        strong contribution from that colorant.

    Example:
        >>> ink, toner, residual = deconvolve_colors(document, preset='blue_black_ink')
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")

    if preset is not None:
        if preset not in STAIN_PRESETS:
            available = ', '.join(sorted(STAIN_PRESETS))
            raise ValueError(f"Unknown preset '{preset}'. Available: {available}")
        vectors = STAIN_PRESETS[preset]
    elif vectors is None:
        raise ValueError("Provide either vectors or a preset")

    img = image.astype(np.uint8) if image.dtype != np.uint8 else image
    if img.ndim == 2:
        raise ValueError("Colour deconvolution needs a colour image")
    rgb = img[:, :, :3]

    basis = normalize_vectors(vectors)
    separation = np.linalg.inv(basis)

    # Beer-Lambert: density is the negative log of transmitted intensity. The
    # +1 keeps pure black finite instead of infinite.
    intensity = rgb.astype(np.float64) + 1.0
    density = -np.log10(intensity / 256.0)

    height, width = density.shape[:2]
    concentrations = density.reshape(-1, 3) @ separation
    concentrations = concentrations.reshape(height, width, 3)

    outputs = []
    for index in range(3):
        # Back to intensity, so a strong colorant reads dark as it does in the
        # original image
        channel = np.exp(-concentrations[:, :, index] * np.log(10.0)) * 255.0
        outputs.append(np.clip(channel, 0, 255).astype(np.uint8))

    return outputs


def extract_stain(
    image: np.ndarray,
    index: int = 0,
    preset: str = 'h_e',
    invert: bool = False,
) -> np.ndarray:
    """
    Return a single colorant channel, for use in a filter chain.

    Args:
        image: Input image
        index: Which colorant, 0 to 2
        preset: Name from ``STAIN_PRESETS``
        invert: Return the colorant bright on dark instead of dark on light

    Returns:
        Single-channel uint8 image
    """
    if not 0 <= index <= 2:
        raise ValueError(f"index must be 0, 1, or 2, got {index}")

    channels = deconvolve_colors(image, preset=preset)
    channel = channels[index]
    return 255 - channel if invert else channel


def estimate_stain_vector(
    image: np.ndarray,
    x: int,
    y: int,
    width: int,
    height: int,
) -> Tuple[float, float, float]:
    """
    Measure a colorant's vector from a region containing only that colorant.

    The reliable way to build a separation for an unknown ink: sample a patch
    of the pen stroke on clean paper and use the vector it returns.

    Args:
        image: Input image
        x, y, width, height: Region containing the colorant alone

    Returns:
        The measured (R, G, B) unit absorbance vector

    Example:
        >>> vector = estimate_stain_vector(document, 120, 80, 20, 12)
        >>> channels = deconvolve_colors(document, vectors=[vector])
    """
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")
    if width <= 0 or height <= 0:
        raise ValueError(f"Region must be non-empty, got {width}x{height}")

    img = image.astype(np.uint8) if image.dtype != np.uint8 else image
    if img.ndim == 2:
        raise ValueError("Colour deconvolution needs a colour image")
    rgb = img[:, :, :3]

    frame_h, frame_w = rgb.shape[:2]
    x1, y1 = max(0, x), max(0, y)
    x2, y2 = min(frame_w, x + width), min(frame_h, y + height)
    if x1 >= x2 or y1 >= y2:
        raise ValueError(
            f"Region ({x}, {y}, {width}, {height}) lies outside the image "
            f"({frame_w}x{frame_h})"
        )

    patch = rgb[y1:y2, x1:x2].astype(np.float64) + 1.0
    density = -np.log10(patch / 256.0)

    mean = density.reshape(-1, 3).mean(axis=0)
    length = np.linalg.norm(mean)
    if length < 1e-6:
        raise ValueError(
            "The sampled region has no colour density - it is probably blank paper"
        )

    unit = mean / length
    return (float(unit[0]), float(unit[1]), float(unit[2]))
