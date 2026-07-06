from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
from skimage.morphology import skeletonize

from src.segmentation.context_features import ContextFeatures, extract_context_features


@dataclass
class AdaptiveMorphologyParams:
    low_density_threshold: float = 0.025
    high_density_threshold: float = 0.120
    small_component_area_low_density: int = 8
    small_component_area_normal: int = 14
    small_component_area_high_density: int = 24
    closing_kernel_low_density: int = 3
    closing_kernel_normal: int = 3
    closing_kernel_high_density: int = 5
    preserve_skeleton: bool = True


def _remove_components_by_area(mask: np.ndarray, min_area: int) -> np.ndarray:
    mask_u8 = (mask > 0).astype(np.uint8)
    n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask_u8, connectivity=8)
    clean = np.zeros_like(mask_u8, dtype=np.uint8)

    for label in range(1, n_labels):
        area = int(stats[label, cv2.CC_STAT_AREA])
        if area >= min_area:
            clean[labels == label] = 1

    return clean.astype(bool)


def _select_adaptive_parameters(features: ContextFeatures, params: AdaptiveMorphologyParams) -> dict:
    """
    Select morphological parameters based on local/global context.

    This is the first implementation of context-aware decision rules.
    Later, this part can be improved into:
    - local patch-based context,
    - learning-based parameter selection,
    - dataset-specific calibration.
    """
    if features.vessel_density < params.low_density_threshold:
        return {
            "min_area": params.small_component_area_low_density,
            "closing_kernel": params.closing_kernel_low_density,
            "context": "low_density",
        }

    if features.vessel_density > params.high_density_threshold:
        return {
            "min_area": params.small_component_area_high_density,
            "closing_kernel": params.closing_kernel_high_density,
            "context": "high_density",
        }

    return {
        "min_area": params.small_component_area_normal,
        "closing_kernel": params.closing_kernel_normal,
        "context": "normal_density",
    }


def adaptive_morphological_refinement(
    baseline_mask: np.ndarray,
    fov_mask: np.ndarray | None = None,
    params: AdaptiveMorphologyParams | None = None,
) -> tuple[np.ndarray, dict]:
    """
    CA-APSRG post-processing stage:
    - extract context from baseline result,
    - adapt min component area and morphology kernel,
    - remove likely false positives,
    - preserve thin vessel skeleton.
    """
    if params is None:
        params = AdaptiveMorphologyParams()

    baseline = baseline_mask > 0
    if fov_mask is not None:
        baseline = baseline & fov_mask

    features = extract_context_features(baseline, fov_mask)
    selected = _select_adaptive_parameters(features, params)

    cleaned = _remove_components_by_area(baseline, min_area=selected["min_area"])

    kernel_size = int(selected["closing_kernel"])
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    closed = cv2.morphologyEx(cleaned.astype(np.uint8), cv2.MORPH_CLOSE, kernel).astype(bool)

    if params.preserve_skeleton:
        # Preserve central thin structures from the baseline result.
        skeleton = skeletonize(baseline)
        refined = closed | skeleton
        refined = _remove_components_by_area(refined, min_area=max(2, selected["min_area"] // 2))
    else:
        refined = closed

    if fov_mask is not None:
        refined &= fov_mask

    debug = {
        "context_features": features.__dict__,
        "selected_parameters": selected,
    }
    return refined, debug
