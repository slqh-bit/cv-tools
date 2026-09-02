"""
Validation harness: degrade an image with a known original, then measure
whether a filter moves it back.

The filter tests prove the arithmetic. This answers the separate question of
whether a filter's defaults help on the degraded material the toolkit exists
for - see ``docs/validation.md`` for the measured results and, more
importantly, for what simulated degradation does and does not establish.
"""

# Note that ``degrade`` below is the *function*, and it shadows the submodule
# of the same name: ``from cv_tools.validation import degrade`` gives the
# callable, which is the intended API. Reach the module as
# ``cv_tools.validation.degrade`` only via ``import`` or ``sys.modules``.
from .degrade import (
    DEGRADATIONS,
    PRESETS,
    anamorphic,
    block_compression,
    codec_generations,
    degrade,
    degrade_preset,
    interlace,
    ir_night,
    low_light,
    motion_blur,
    resolution_loss,
    sensor_noise,
)
from .benchmark import (
    Result,
    compare,
    evaluate,
    run_matrix,
    sharpness,
    to_markdown,
)

__all__ = [
    'DEGRADATIONS', 'PRESETS', 'degrade', 'degrade_preset',
    'sensor_noise', 'low_light', 'ir_night', 'block_compression',
    'codec_generations', 'motion_blur', 'resolution_loss', 'anamorphic',
    'interlace',
    'Result', 'compare', 'evaluate', 'run_matrix', 'sharpness', 'to_markdown',
]
