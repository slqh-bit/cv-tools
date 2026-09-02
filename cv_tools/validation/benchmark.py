"""
Measure whether a filter actually improves degraded footage.

``degrade.py`` produces an image whose clean form is known. That makes the
question answerable in numbers: run a filter on the degraded frame, and see
whether the result moved toward the original or away from it.

**Read the metrics for what they are.** PSNR and SSIM measure fidelity to the
reference, which is the right question for denoising and deblurring and the
wrong one for enhancement. CLAHE deliberately changes the tonal distribution:
it will usually *lose* PSNR while making a number plate readable, which is the
entire point of running it. So the report carries a no-reference sharpness
measure alongside, and neither number replaces looking at the image.

What the harness is really for is catching the case nobody looks for - a filter
whose defaults make things quantifiably worse on the material it was written
for, which is invisible in a unit test asserting on array shapes.
"""

from dataclasses import dataclass, asdict, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import cv2
import numpy as np
from skimage.metrics import peak_signal_noise_ratio, structural_similarity


def _luma(image: np.ndarray) -> np.ndarray:
    """Single-channel view, so a filter that greys its output stays comparable."""
    if image.ndim == 2:
        return image
    if image.shape[2] == 1:
        return image[:, :, 0]
    if image.shape[2] == 4:
        image = image[:, :, :3]
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def _match(reference: np.ndarray, candidate: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Crop both to their common area.

    Some degradations lose a row or column - encoders reject odd dimensions, so
    ``codec_generations`` crops. Cropping the reference to match is honest;
    resizing it back up would compare against interpolated pixels that were
    never in the original.
    """
    height = min(reference.shape[0], candidate.shape[0])
    width = min(reference.shape[1], candidate.shape[1])
    return reference[:height, :width], candidate[:height, :width]


def sharpness(image: np.ndarray) -> float:
    """
    Variance of the Laplacian: a no-reference measure of acutance.

    Needs no ground truth, which is what makes it usable on real footage where
    there is none. It rises with genuine detail and equally with amplified
    noise, so it is only meaningful read next to a fidelity metric - a filter
    that raises sharpness while losing SSIM is sharpening the noise.

    Args:
        image: Image, uint8

    Returns:
        Variance of the Laplacian response
    """
    return float(cv2.Laplacian(_luma(image), cv2.CV_64F).var())


def compare(reference: np.ndarray, candidate: np.ndarray) -> Dict[str, float]:
    """
    Fidelity of ``candidate`` to ``reference``.

    Measured on luma, so a filter that returns a single channel - every edge
    detector does - is still comparable rather than erroring on shape.

    Args:
        reference: Ground truth image, uint8
        candidate: Image to score, uint8

    Returns:
        ``psnr`` in dB, ``ssim`` in 0-1, and ``sharpness``
    """
    ref, cand = _match(_luma(reference), _luma(candidate))
    # SSIM's default 7x7 window needs at least 7 pixels on each side.
    window = min(7, ref.shape[0], ref.shape[1])
    window -= (window + 1) % 2                      # nearest odd value
    # An exact match makes the mean squared error zero, which PSNR divides by.
    # The answer is infinity; computing it just to catch a warning is noise.
    identical = ref.shape == cand.shape and np.array_equal(ref, cand)

    return {
        'psnr': float('inf') if identical
                else float(peak_signal_noise_ratio(ref, cand, data_range=255)),
        'ssim': float(structural_similarity(ref, cand, data_range=255,
                                            win_size=max(window, 3))),
        'sharpness': sharpness(cand),
    }


@dataclass
class Result:
    """One filter measured against one degradation."""
    filter_name: str
    degradation: str
    params: Dict[str, Any] = field(default_factory=dict)
    baseline: Dict[str, float] = field(default_factory=dict)
    processed: Dict[str, float] = field(default_factory=dict)
    error: Optional[str] = None

    @property
    def psnr_delta(self) -> float:
        """dB gained over leaving the degraded frame alone. Negative is worse."""
        if self.error:
            return float('nan')
        return self.processed['psnr'] - self.baseline['psnr']

    @property
    def ssim_delta(self) -> float:
        if self.error:
            return float('nan')
        return self.processed['ssim'] - self.baseline['ssim']

    @property
    def sharpness_ratio(self) -> float:
        """Processed acutance over the degraded frame's. Above 1 is sharper."""
        if self.error or not self.baseline.get('sharpness'):
            return float('nan')
        return self.processed['sharpness'] / self.baseline['sharpness']

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data.update(psnr_delta=self.psnr_delta, ssim_delta=self.ssim_delta,
                    sharpness_ratio=self.sharpness_ratio)
        return data


def evaluate(
    clean: np.ndarray,
    degraded: np.ndarray,
    filter_fn: Callable[..., np.ndarray],
    filter_name: str,
    degradation: str,
    params: Optional[Dict[str, Any]] = None,
) -> Result:
    """
    Score one filter on one degraded image against its clean original.

    A filter that raises is recorded as a failed result rather than aborting the
    run: on a sweep across every filter, one that cannot handle a monochrome or
    odd-sized input is itself a finding worth seeing next to the others.

    Args:
        clean: Ground truth image, uint8
        degraded: The same image after degradation, uint8
        filter_fn: Callable taking ``(image, **params)``
        filter_name: Name for the report
        degradation: Degradation name for the report
        params: Parameters passed to the filter

    Returns:
        A ``Result``, carrying ``error`` if the filter raised
    """
    params = dict(params or {})
    baseline = compare(clean, degraded)
    try:
        processed = filter_fn(degraded, **params)
    except Exception as exc:                        # noqa: BLE001 - reported, not raised
        return Result(filter_name, degradation, params, baseline, {}, error=str(exc))

    if not isinstance(processed, np.ndarray) or processed.size == 0:
        return Result(filter_name, degradation, params, baseline, {},
                      error='filter did not return an image')

    return Result(filter_name, degradation, params, baseline,
                  compare(clean, processed))


def run_matrix(
    clean: np.ndarray,
    degradations: Sequence[Tuple[str, np.ndarray]],
    filters: Sequence[Tuple[str, Callable[..., np.ndarray], Dict[str, Any]]],
) -> List[Result]:
    """
    Score every filter against every degradation.

    Args:
        clean: Ground truth image, uint8
        degradations: ``(name, degraded_image)`` pairs
        filters: ``(name, callable, params)`` triples

    Returns:
        One ``Result`` per combination, in the order given
    """
    results: List[Result] = []
    for degradation_name, degraded in degradations:
        for filter_name, filter_fn, params in filters:
            results.append(evaluate(clean, degraded, filter_fn, filter_name,
                                    degradation_name, params))
    return results


def to_markdown(results: Sequence[Result], sort_by: str = 'psnr_delta') -> str:
    """
    Render results as a Markdown table, best first.

    Args:
        results: Results to render
        sort_by: ``psnr_delta``, ``ssim_delta`` or ``sharpness_ratio``

    Returns:
        A Markdown table
    """
    ok = [r for r in results if not r.error]
    failed = [r for r in results if r.error]
    ok.sort(key=lambda r: getattr(r, sort_by), reverse=True)

    lines = [
        '| Filter | Degradation | PSNR dB | ΔPSNR | SSIM | ΔSSIM | Sharpness × |',
        '|---|---|---:|---:|---:|---:|---:|',
    ]
    for r in ok:
        lines.append(
            f'| `{r.filter_name}` | {r.degradation} | {r.processed["psnr"]:.2f} | '
            f'{r.psnr_delta:+.2f} | {r.processed["ssim"]:.3f} | {r.ssim_delta:+.3f} | '
            f'{r.sharpness_ratio:.2f} |')

    if failed:
        lines += ['', '**Filters that raised**', '',
                  '| Filter | Degradation | Error |', '|---|---|---|']
        for r in failed:
            lines.append(f'| `{r.filter_name}` | {r.degradation} | {r.error} |')
    return '\n'.join(lines)
