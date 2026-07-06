from __future__ import annotations

import numpy as np

from src.segmentation.adaptive_morphology import (
    AdaptiveMorphologyParams,
    adaptive_morphological_refinement,
)


def ca_apsrg_refine(
    baseline_mask: np.ndarray,
    fov_mask: np.ndarray | None = None,
    params: AdaptiveMorphologyParams | None = None,
) -> tuple[np.ndarray, dict]:
    """
    Main CA-APSRG refinement wrapper.

    In this initial project skeleton, CA-APSRG is represented by
    adaptive morphological refinement after APSRG baseline.

    Later additions can include:
    - context-aware seed validation,
    - local patch vessel density,
    - adaptive region growing threshold,
    - false-positive candidate scoring.
    """
    return adaptive_morphological_refinement(baseline_mask, fov_mask=fov_mask, params=params)
