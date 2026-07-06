from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class APSRGParams:
    vesselness_kernel_sizes: tuple[int, ...] = (7, 11, 15)
    seed_percentile: float = 92
    candidate_percentile: float = 78
    min_component_area: int = 8


def enhance_dark_vessels(gray: np.ndarray, kernel_sizes: tuple[int, ...] = (7, 11, 15)) -> np.ndarray:
    """
    Multi-scale black-hat enhancement for dark vessels.

    This is an initial approximation. Replace/refine according to the APSRG paper:
    - multi-scale vessel enhancement,
    - automatic polling seed selection,
    - region growing criterion.
    """
    enhanced_list = []
    for k in kernel_sizes:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
        blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
        enhanced_list.append(blackhat)
    enhanced = np.max(np.stack(enhanced_list, axis=0), axis=0)
    return cv2.normalize(enhanced, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)


def _region_growing_from_seeds(candidate: np.ndarray, seeds: np.ndarray) -> np.ndarray:
    """
    Region growing on binary candidate map from seed pixels.

    candidate: bool map where growing is allowed.
    seeds: bool map as starting points.
    """
    h, w = candidate.shape
    visited = np.zeros((h, w), dtype=bool)
    result = np.zeros((h, w), dtype=bool)

    q = deque()
    ys, xs = np.where(seeds & candidate)
    for y, x in zip(ys, xs):
        visited[y, x] = True
        result[y, x] = True
        q.append((y, x))

    neighbors = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    while q:
        y, x = q.popleft()
        for dy, dx in neighbors:
            yy, xx = y + dy, x + dx
            if yy < 0 or yy >= h or xx < 0 or xx >= w:
                continue
            if visited[yy, xx] or not candidate[yy, xx]:
                continue
            visited[yy, xx] = True
            result[yy, xx] = True
            q.append((yy, xx))

    return result


def remove_small_components(mask: np.ndarray, min_area: int = 8) -> np.ndarray:
    mask_u8 = (mask > 0).astype(np.uint8)
    n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask_u8, connectivity=8)
    clean = np.zeros_like(mask_u8, dtype=np.uint8)

    for label in range(1, n_labels):
        area = stats[label, cv2.CC_STAT_AREA]
        if area >= min_area:
            clean[labels == label] = 1

    return clean.astype(bool)


def apsrg_segment(
    preprocessed_gray: np.ndarray,
    fov_mask: np.ndarray | None = None,
    params: APSRGParams | None = None,
) -> tuple[np.ndarray, dict]:
    """
    Initial runnable APSRG baseline.

    Output:
    - baseline_mask: bool vessel mask
    - debug_info: dictionary containing intermediate maps and thresholds
    """
    if params is None:
        params = APSRGParams()

    vesselness = enhance_dark_vessels(preprocessed_gray, params.vesselness_kernel_sizes)

    valid_pixels = vesselness[fov_mask] if fov_mask is not None else vesselness.reshape(-1)
    valid_pixels = valid_pixels[valid_pixels > 0]

    if valid_pixels.size == 0:
        empty = np.zeros_like(preprocessed_gray, dtype=bool)
        return empty, {"vesselness": vesselness, "seed_thr": None, "candidate_thr": None}

    seed_thr = np.percentile(valid_pixels, params.seed_percentile)
    candidate_thr = np.percentile(valid_pixels, params.candidate_percentile)

    seeds = vesselness >= seed_thr
    candidate = vesselness >= candidate_thr

    if fov_mask is not None:
        seeds &= fov_mask
        candidate &= fov_mask

    grown = _region_growing_from_seeds(candidate, seeds)
    grown = remove_small_components(grown, min_area=params.min_component_area)

    debug_info = {
        "vesselness": vesselness,
        "seeds": seeds,
        "candidate": candidate,
        "seed_thr": float(seed_thr),
        "candidate_thr": float(candidate_thr),
    }
    return grown, debug_info
