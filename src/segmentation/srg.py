"""Public entry point for the project's SRG baseline.

SRG uses fuzzy similarity, fuzzy seed support, connected-edge processing,
and edge-delayed region growing. It excludes Harris polling and CA-APSRG
context-aware morphological refinement.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

import numpy as np

from src.segmentation.apsrg_baseline import APSRGParams, apsrg_segment


def segment_with_srg(
    preprocessed_gray: np.ndarray,
    fov_mask: np.ndarray | None = None,
    *,
    params: APSRGParams | None = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Segment one preprocessed image with the fuzzy SRG baseline."""
    base = params or APSRGParams()
    method_params = replace(
        base,
        seed_selection_method="fuzzy_srg",
        region_growing_mode="edge_delayed",
    )
    mask, debug = apsrg_segment(
        preprocessed_gray, fov_mask=fov_mask, params=method_params
    )
    debug["method"] = "SRG"
    return mask, debug


segment_srg = segment_with_srg
