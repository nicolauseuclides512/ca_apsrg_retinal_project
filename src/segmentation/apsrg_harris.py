"""
Harris Corner seed polling for APSRG retinal vessel segmentation.

This module implements the first APSRG enhancement step inspired by the
APSRG fundus vessel paper: Harris Corner is used as an automatic polling
mechanism for seed selection before region growing.

The implementation is adapted for the current CA-APSRG project:
- Harris response is computed on a vessel-enhanced image, usually the
  black-hat vesselness map from apsrg_baseline.py.
- Seed candidates are constrained by the candidate vessel map and optional
  FoV mask.
- The number of selected seed points is configurable, with a default target
  of 35 inspired by the APSRG paper's seed polling experiment.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Optional

import cv2
import numpy as np

from src.utils.image_io import ensure_binary_mask, normalize_to_uint8, to_uint8


@dataclass(frozen=True)
class HarrisSeedParams:
    """Configuration for Harris Corner seed polling."""

    enabled: bool = True

    # Harris detector parameters.
    block_size: int = 2
    ksize: int = 3
    k: float = 0.04

    # Candidate selection.
    response_threshold_ratio: float = 0.01
    nms_window_size: int = 3

    # Seed count control.
    target_seed_count: int = 35
    min_seed_count: int = 7
    max_seed_count: int = 77

    # Scoring and constraints.
    prefer_vesselness_weight: float = 0.65
    use_candidate_constraint: bool = True
    fallback_to_top_vesselness: bool = True

    # Optional dilation for seed points.
    seed_dilate_radius: int = 0

    @classmethod
    def from_dict(cls, config: dict[str, Any] | None) -> "HarrisSeedParams":
        """Create HarrisSeedParams from a dictionary."""
        if not config:
            return cls()

        return cls(
            enabled=bool(config.get("enabled", True)),
            block_size=int(config.get("block_size", 2)),
            ksize=int(config.get("ksize", 3)),
            k=float(config.get("k", 0.04)),
            response_threshold_ratio=float(config.get("response_threshold_ratio", 0.01)),
            nms_window_size=int(config.get("nms_window_size", 3)),
            target_seed_count=int(config.get("target_seed_count", 35)),
            min_seed_count=int(config.get("min_seed_count", 7)),
            max_seed_count=int(config.get("max_seed_count", 77)),
            prefer_vesselness_weight=float(config.get("prefer_vesselness_weight", 0.65)),
            use_candidate_constraint=bool(config.get("use_candidate_constraint", True)),
            fallback_to_top_vesselness=bool(config.get("fallback_to_top_vesselness", True)),
            seed_dilate_radius=int(config.get("seed_dilate_radius", 0)),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return parameter values as dictionary."""
        return asdict(self)


def _ensure_odd(value: int, minimum: int = 3) -> int:
    """Return an odd integer not smaller than minimum."""
    value = max(int(value), int(minimum))
    if value % 2 == 0:
        value += 1
    return value


def _prepare_gray(image: np.ndarray) -> np.ndarray:
    """Convert input image to 2D uint8 grayscale."""
    arr = np.asarray(image)
    if arr.ndim == 3:
        arr = cv2.cvtColor(to_uint8(arr), cv2.COLOR_RGB2GRAY)
    if arr.ndim != 2:
        raise ValueError(f"Expected grayscale image, got shape {arr.shape}")
    return to_uint8(arr)


def _prepare_optional_mask(mask: Optional[np.ndarray], shape: tuple[int, int]) -> Optional[np.ndarray]:
    """Convert optional mask to boolean and validate shape."""
    if mask is None:
        return None
    mask_bool = ensure_binary_mask(mask, return_uint8=False)
    if mask_bool.shape != shape:
        raise ValueError(f"Mask shape {mask_bool.shape} does not match image shape {shape}")
    return mask_bool.astype(bool)


def compute_harris_response(
    image: np.ndarray,
    *,
    params: HarrisSeedParams | None = None,
) -> np.ndarray:
    """
    Compute normalized Harris Corner response.

    Returns a float32 image in [0, 1].
    """
    params = params or HarrisSeedParams()
    gray = _prepare_gray(image)

    block_size = max(int(params.block_size), 2)
    ksize = _ensure_odd(params.ksize, minimum=3)

    gray_float = np.float32(gray) / 255.0

    # OpenCV cornerHarris expects:
    # cv2.cornerHarris(src, blockSize, ksize, k)
    # Use positional arguments for compatibility across OpenCV versions.
    response = cv2.cornerHarris(
        gray_float,
        block_size,
        ksize,
        float(params.k),
    )

    # Harris response can contain negative values.
    # We keep only positive corner responses.
    response = np.maximum(response, 0.0).astype(np.float32)

    if float(response.max()) <= 0.0:
        return np.zeros_like(response, dtype=np.float32)

    response = response / float(response.max())
    return response.astype(np.float32)


def nonmax_suppression_2d(
    response: np.ndarray,
    *,
    window_size: int = 3,
    threshold: float = 0.01,
    valid_mask: Optional[np.ndarray] = None,
) -> np.ndarray:
    """
    Non-maximum suppression for 2D corner response.

    A pixel is kept when:
    - it is equal to the local maximum in its neighborhood,
    - response value is above threshold,
    - it is inside valid_mask when valid_mask is provided.
    """
    resp = np.asarray(response, dtype=np.float32)
    if resp.ndim != 2:
        raise ValueError("response must be a 2D array")

    kernel_size = _ensure_odd(window_size, minimum=3)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    local_max = cv2.dilate(resp, kernel)

    maxima = (resp >= local_max - 1e-12) & (resp >= float(threshold))

    if valid_mask is not None:
        valid = np.asarray(valid_mask).astype(bool)
        if valid.shape != resp.shape:
            raise ValueError("valid_mask shape must match response shape")
        maxima &= valid

    return maxima.astype(bool)


def _build_valid_seed_area(
    shape: tuple[int, int],
    *,
    candidate_map: Optional[np.ndarray] = None,
    fov_mask: Optional[np.ndarray] = None,
    use_candidate_constraint: bool = True,
) -> np.ndarray:
    """Build boolean valid area for Harris seed selection."""
    valid = np.ones(shape, dtype=bool)

    if candidate_map is not None and use_candidate_constraint:
        candidate = _prepare_optional_mask(candidate_map, shape)
        if candidate is not None:
            valid &= candidate

    if fov_mask is not None:
        fov = _prepare_optional_mask(fov_mask, shape)
        if fov is not None:
            valid &= fov

    return valid


def _normalize_score(image: Optional[np.ndarray], shape: tuple[int, int]) -> np.ndarray:
    """Normalize optional score image to [0, 1]."""
    if image is None:
        return np.zeros(shape, dtype=np.float32)
    arr = normalize_to_uint8(image).astype(np.float32) / 255.0
    if arr.shape != shape:
        raise ValueError(f"Score image shape {arr.shape} does not match {shape}")
    return arr


def rank_harris_seed_candidates(
    harris_response: np.ndarray,
    *,
    vesselness: Optional[np.ndarray] = None,
    candidate_mask: Optional[np.ndarray] = None,
    params: HarrisSeedParams | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Rank Harris seed candidates.

    The ranking score combines Harris response and vesselness response:
        score = (1 - w) * Harris + w * Vesselness

    Returns:
    - candidate coordinates as array of shape (N, 2), with columns y, x
    - score values as array of shape (N,)
    """
    params = params or HarrisSeedParams()
    response = np.asarray(harris_response, dtype=np.float32)

    if response.ndim != 2:
        raise ValueError("harris_response must be 2D")

    shape = response.shape
    vesselness_score = _normalize_score(vesselness, shape)

    valid = np.ones(shape, dtype=bool)
    if candidate_mask is not None:
        valid &= np.asarray(candidate_mask).astype(bool)

    coords = np.argwhere(valid)
    if coords.size == 0:
        return np.empty((0, 2), dtype=int), np.empty((0,), dtype=np.float32)

    w = float(np.clip(params.prefer_vesselness_weight, 0.0, 1.0))
    score_image = ((1.0 - w) * response) + (w * vesselness_score)

    scores = score_image[coords[:, 0], coords[:, 1]]
    order = np.argsort(scores)[::-1]

    return coords[order], scores[order]


def _make_seed_mask_from_coords(
    coords: np.ndarray,
    shape: tuple[int, int],
    *,
    limit: int,
    valid_mask: Optional[np.ndarray] = None,
    dilate_radius: int = 0,
) -> np.ndarray:
    """Create seed mask from selected coordinate array."""
    seed_mask = np.zeros(shape, dtype=bool)

    if coords.size == 0 or limit <= 0:
        return seed_mask

    selected = coords[: int(limit)]
    seed_mask[selected[:, 0], selected[:, 1]] = True

    if int(dilate_radius) > 0:
        radius = int(dilate_radius)
        kernel_size = 2 * radius + 1
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        seed_mask = cv2.dilate(seed_mask.astype(np.uint8), kernel).astype(bool)

    if valid_mask is not None:
        seed_mask &= valid_mask.astype(bool)

    return seed_mask.astype(bool)


def select_harris_seeds(
    image: np.ndarray,
    *,
    vesselness: Optional[np.ndarray] = None,
    candidate_map: Optional[np.ndarray] = None,
    fov_mask: Optional[np.ndarray] = None,
    params: HarrisSeedParams | None = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    """
    Select Harris-based seed points for APSRG.

    Parameters
    ----------
    image:
        Image used to compute Harris response. In the current CA-APSRG project,
        this is usually the vesselness image.
    vesselness:
        Optional vesselness score used to rank Harris candidates.
    candidate_map:
        Optional binary candidate vessel map. When use_candidate_constraint=True,
        seed points are restricted to this map.
    fov_mask:
        Optional field-of-view mask.
    params:
        HarrisSeedParams.

    Returns
    -------
    seeds:
        Boolean seed mask.
    debug:
        Dictionary containing Harris response, candidate map, selected seed map,
        and seed count.
    """
    params = params or HarrisSeedParams()
    gray = _prepare_gray(image)
    shape = gray.shape

    valid_area = _build_valid_seed_area(
        shape,
        candidate_map=candidate_map,
        fov_mask=fov_mask,
        use_candidate_constraint=params.use_candidate_constraint,
    )

    if not params.enabled:
        empty = np.zeros(shape, dtype=bool)
        return empty, {
            "enabled": False,
            "harris_response": np.zeros(shape, dtype=np.float32),
            "harris_candidates": empty,
            "harris_selected_seeds": empty,
            "n_harris_seed_pixels": 0,
            "params": params.to_dict(),
        }

    response = compute_harris_response(gray, params=params)
    threshold = float(params.response_threshold_ratio)

    harris_candidates = nonmax_suppression_2d(
        response,
        window_size=params.nms_window_size,
        threshold=threshold,
        valid_mask=valid_area,
    )

    coords, scores = rank_harris_seed_candidates(
        response,
        vesselness=vesselness,
        candidate_mask=harris_candidates,
        params=params,
    )

    target_count = int(params.target_seed_count)
    max_count = int(params.max_seed_count)
    min_count = int(params.min_seed_count)

    if max_count > 0:
        target_count = min(target_count, max_count)

    # If Harris candidates are too few, optionally fall back to top vesselness/corner scores
    # inside the valid seed area.
    if coords.shape[0] < min_count and params.fallback_to_top_vesselness:
        fallback_coords, fallback_scores = rank_harris_seed_candidates(
            response,
            vesselness=vesselness,
            candidate_mask=valid_area,
            params=params,
        )

        if fallback_coords.shape[0] > coords.shape[0]:
            coords = fallback_coords
            scores = fallback_scores

    selected_count = min(target_count, coords.shape[0])

    seeds = _make_seed_mask_from_coords(
        coords,
        shape,
        limit=selected_count,
        valid_mask=valid_area,
        dilate_radius=params.seed_dilate_radius,
    )

    debug: dict[str, Any] = {
        "enabled": True,
        "harris_response": response,
        "harris_candidates": harris_candidates,
        "harris_selected_seeds": seeds,
        "harris_seed_scores_top": scores[: min(len(scores), 20)].tolist(),
        "n_harris_candidates": int(harris_candidates.sum()),
        "n_harris_seed_pixels": int(seeds.sum()),
        "selected_seed_count": int(selected_count),
        "valid_seed_area_pixels": int(valid_area.sum()),
        "params": params.to_dict(),
    }

    return seeds.astype(bool), debug


def overlay_harris_points(
    image_rgb_or_gray: np.ndarray,
    seeds: np.ndarray,
    *,
    point_radius: int = 2,
    color: tuple[int, int, int] = (255, 0, 0),
) -> np.ndarray:
    """
    Create an RGB image with Harris seed points overlaid.

    This helper is optional but useful for Streamlit/debug visualization.
    """
    img = np.asarray(image_rgb_or_gray)

    if img.ndim == 2:
        base = cv2.cvtColor(to_uint8(img), cv2.COLOR_GRAY2RGB)
    elif img.ndim == 3 and img.shape[2] == 3:
        base = to_uint8(img).copy()
    else:
        raise ValueError(f"Unsupported image shape: {img.shape}")

    seed_mask = ensure_binary_mask(seeds, return_uint8=False)
    ys, xs = np.where(seed_mask)

    for y, x in zip(ys, xs):
        cv2.circle(base, (int(x), int(y)), int(point_radius), color, thickness=-1)

    return base