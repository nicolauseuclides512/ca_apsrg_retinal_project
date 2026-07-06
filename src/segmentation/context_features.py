from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class ContextFeatures:
    vessel_density: float
    component_count: int
    mean_component_area: float
    median_component_area: float
    small_component_ratio: float


def extract_context_features(mask: np.ndarray, fov_mask: np.ndarray | None = None, small_area_limit: int = 20) -> ContextFeatures:
    valid_area = int(fov_mask.sum()) if fov_mask is not None else mask.size
    valid_area = max(valid_area, 1)

    work = (mask > 0).astype(np.uint8)
    if fov_mask is not None:
        work[~fov_mask] = 0

    vessel_density = float(work.sum() / valid_area)

    n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(work, connectivity=8)
    areas = []
    for label in range(1, n_labels):
        area = int(stats[label, cv2.CC_STAT_AREA])
        areas.append(area)

    if len(areas) == 0:
        return ContextFeatures(
            vessel_density=vessel_density,
            component_count=0,
            mean_component_area=0.0,
            median_component_area=0.0,
            small_component_ratio=0.0,
        )

    arr = np.array(areas, dtype=np.float32)
    small_component_ratio = float((arr < small_area_limit).sum() / len(arr))

    return ContextFeatures(
        vessel_density=vessel_density,
        component_count=len(areas),
        mean_component_area=float(arr.mean()),
        median_component_area=float(np.median(arr)),
        small_component_ratio=small_component_ratio,
    )
