"""Public entry point for the adapted APSRG baseline.

The preprocessing is adapted to retinal-vessel segmentation and is not an
exact IUWT reproduction. APSRG adds Harris-based automatic seed polling to
seeded region growing. Context-aware refinement belongs to CA-APSRG.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

import numpy as np

from src.segmentation.apsrg_baseline import APSRGParams, apsrg_segment


def segment_with_apsrg(
    preprocessed_gray: np.ndarray,
    fov_mask: np.ndarray | None = None,
    *,
    params: APSRGParams | None = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Segment one image with the project's adapted Harris APSRG baseline."""
    base = params or APSRGParams()
    method_params = replace(
        base,
        seed_selection_method="harris_polling",
        region_growing_mode="bfs",
    )
    mask, debug = apsrg_segment(
        preprocessed_gray, fov_mask=fov_mask, params=method_params
    )
    debug["method"] = "adapted APSRG baseline"
    return mask, debug


segment_apsrg_adapted = segment_with_apsrg
