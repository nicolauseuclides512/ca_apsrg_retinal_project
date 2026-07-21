"""
Selective hybrid fuzzy-Harris seed polling for APSRG.

The hybrid mechanism follows the conceptual development:

SRG:
    fuzzy similarity and connected-edge information determine
    eligible seed areas.

APSRG:
    Harris Corner polls representative seed points from those
    fuzzy-supported areas.

Unlike a simple union operation, this module does not directly combine all
fuzzy and Harris seed pixels. Harris candidates are first constrained by
fuzzy seed support, candidate vessel map, and optional FoV mask. Candidates
are then ranked using fuzzy, Harris, and vesselness scores.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Optional

import cv2
import numpy as np

from src.segmentation.apsrg_harris import (
    HarrisSeedParams,
    select_harris_seeds,
)
from src.segmentation.srg_features import (
    SRGFeatureParams,
    select_fuzzy_srg_seeds,
)
from src.utils.image_io import ensure_binary_mask, normalize_to_uint8


@dataclass(frozen=True)
class HybridSeedParams:
    """Parameters for selective fuzzy-Harris seed polling."""

    enabled: bool = True

    # Desired number of final seed points.
    target_seed_count: int = 35
    min_seed_count: int = 7
    max_seed_count: int = 77

    # Spatial relation between fuzzy support and Harris candidates.
    fuzzy_support_radius: int = 2
    relaxed_support_radius: int = 5

    # Minimum spatial distance between selected seed points.
    min_seed_distance: int = 3

    # Composite ranking score.
    fuzzy_weight: float = 0.35
    harris_weight: float = 0.40
    vesselness_weight: float = 0.25

    # Constraints.
    use_candidate_constraint: bool = True
    use_fov_constraint: bool = True

    # Fallbacks when strict fuzzy-Harris candidates are insufficient.
    allow_relaxed_harris_fallback: bool = True
    allow_fuzzy_fallback: bool = True

    # Optional seed dilation after point selection.
    seed_dilate_radius: int = 0

    @classmethod
    def from_dict(
        cls,
        config: dict[str, Any] | None,
    ) -> "HybridSeedParams":
        """Create parameters from a YAML-like dictionary."""
        if not config:
            return cls()

        return cls(
            enabled=bool(config.get("enabled", True)),
            target_seed_count=int(config.get("target_seed_count", 35)),
            min_seed_count=int(config.get("min_seed_count", 7)),
            max_seed_count=int(config.get("max_seed_count", 77)),
            fuzzy_support_radius=int(config.get("fuzzy_support_radius", 2)),
            relaxed_support_radius=int(
                config.get("relaxed_support_radius", 5)
            ),
            min_seed_distance=int(config.get("min_seed_distance", 3)),
            fuzzy_weight=float(config.get("fuzzy_weight", 0.35)),
            harris_weight=float(config.get("harris_weight", 0.40)),
            vesselness_weight=float(
                config.get("vesselness_weight", 0.25)
            ),
            use_candidate_constraint=bool(
                config.get("use_candidate_constraint", True)
            ),
            use_fov_constraint=bool(
                config.get("use_fov_constraint", True)
            ),
            allow_relaxed_harris_fallback=bool(
                config.get("allow_relaxed_harris_fallback", True)
            ),
            allow_fuzzy_fallback=bool(
                config.get("allow_fuzzy_fallback", True)
            ),
            seed_dilate_radius=int(config.get("seed_dilate_radius", 0)),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return parameters as dictionary."""
        return asdict(self)


def _prepare_mask(
    mask: Optional[np.ndarray],
    shape: tuple[int, int],
) -> Optional[np.ndarray]:
    """Convert optional mask into a validated boolean mask."""
    if mask is None:
        return None

    result = ensure_binary_mask(
        mask,
        return_uint8=False,
    ).astype(bool)

    if result.shape != shape:
        raise ValueError(
            f"Mask shape {result.shape} does not match image shape {shape}"
        )

    return result


def _normalize_score(
    image: Optional[np.ndarray],
    shape: tuple[int, int],
) -> np.ndarray:
    """Normalize an optional score image into float32 [0, 1]."""
    if image is None:
        return np.zeros(shape, dtype=np.float32)

    arr = np.asarray(image)

    if arr.shape != shape:
        raise ValueError(
            f"Score image shape {arr.shape} does not match {shape}"
        )

    arr_float = arr.astype(np.float32)

    if (
        float(np.nanmin(arr_float)) >= 0.0
        and float(np.nanmax(arr_float)) <= 1.0
    ):
        return np.clip(arr_float, 0.0, 1.0)

    return normalize_to_uint8(arr_float).astype(np.float32) / 255.0


def _dilate_mask(
    mask: np.ndarray,
    radius: int,
) -> np.ndarray:
    """Dilate a boolean mask using an elliptical kernel."""
    mask_bool = np.asarray(mask).astype(bool)

    if int(radius) <= 0:
        return mask_bool

    radius = int(radius)
    kernel_size = (2 * radius) + 1

    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (kernel_size, kernel_size),
    )

    return cv2.dilate(
        mask_bool.astype(np.uint8),
        kernel,
    ).astype(bool)


def _build_valid_area(
    shape: tuple[int, int],
    *,
    candidate_map: Optional[np.ndarray],
    fov_mask: Optional[np.ndarray],
    params: HybridSeedParams,
) -> np.ndarray:
    """Build valid area for final hybrid seed points."""
    valid = np.ones(shape, dtype=bool)

    if candidate_map is not None and params.use_candidate_constraint:
        candidate = _prepare_mask(candidate_map, shape)
        if candidate is not None:
            valid &= candidate

    if fov_mask is not None and params.use_fov_constraint:
        fov = _prepare_mask(fov_mask, shape)
        if fov is not None:
            valid &= fov

    return valid


def _normalize_weights(
    fuzzy_weight: float,
    harris_weight: float,
    vesselness_weight: float,
) -> tuple[float, float, float]:
    """Normalize the three score weights so their sum equals one."""
    weights = np.asarray(
        [
            max(float(fuzzy_weight), 0.0),
            max(float(harris_weight), 0.0),
            max(float(vesselness_weight), 0.0),
        ],
        dtype=np.float32,
    )

    total = float(weights.sum())

    if total <= 0.0:
        return 1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0

    weights /= total

    return (
        float(weights[0]),
        float(weights[1]),
        float(weights[2]),
    )


def compute_hybrid_seed_score(
    fuzzy_score: np.ndarray,
    harris_response: np.ndarray,
    vesselness: np.ndarray,
    *,
    params: HybridSeedParams,
) -> np.ndarray:
    """
    Compute the composite fuzzy-Harris-vesselness seed score.

    score =
        fuzzy_weight * fuzzy_score
        + harris_weight * harris_response
        + vesselness_weight * vesselness
    """
    shape = np.asarray(fuzzy_score).shape

    fuzzy = _normalize_score(fuzzy_score, shape)
    harris = _normalize_score(harris_response, shape)
    vessel = _normalize_score(vesselness, shape)

    fuzzy_weight, harris_weight, vesselness_weight = _normalize_weights(
        params.fuzzy_weight,
        params.harris_weight,
        params.vesselness_weight,
    )

    score = (
        fuzzy_weight * fuzzy
        + harris_weight * harris
        + vesselness_weight * vessel
    )

    return np.clip(score, 0.0, 1.0).astype(np.float32)


def _local_maxima(
    score: np.ndarray,
    valid_mask: np.ndarray,
    *,
    radius: int = 2,
) -> np.ndarray:
    """Find local maxima inside a valid area."""
    radius = max(int(radius), 1)
    kernel_size = (2 * radius) + 1

    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (kernel_size, kernel_size),
    )

    local_max = cv2.dilate(
        score.astype(np.float32),
        kernel,
    )

    maxima = score >= (local_max - 1e-12)
    maxima &= valid_mask.astype(bool)

    return maxima


def _select_spatially_separated_points(
    score: np.ndarray,
    candidate_mask: np.ndarray,
    *,
    target_count: int,
    min_distance: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Select highest-scoring candidates with minimum spatial distance.

    Returns:
        seed_mask,
        selected coordinates (y, x),
        selected score values.
    """
    candidate_bool = np.asarray(candidate_mask).astype(bool)
    shape = candidate_bool.shape

    seed_mask = np.zeros(shape, dtype=bool)

    coords = np.argwhere(candidate_bool)

    if coords.size == 0 or int(target_count) <= 0:
        return (
            seed_mask,
            np.empty((0, 2), dtype=np.int32),
            np.empty((0,), dtype=np.float32),
        )

    scores = score[coords[:, 0], coords[:, 1]]
    order = np.argsort(scores)[::-1]

    min_distance = max(int(min_distance), 0)
    min_distance_squared = float(min_distance * min_distance)

    selected_coords: list[tuple[int, int]] = []
    selected_scores: list[float] = []

    for index in order:
        y = int(coords[index, 0])
        x = int(coords[index, 1])

        accepted = True

        if min_distance > 0:
            for selected_y, selected_x in selected_coords:
                distance_squared = (
                    (y - selected_y) ** 2
                    + (x - selected_x) ** 2
                )

                if distance_squared < min_distance_squared:
                    accepted = False
                    break

        if not accepted:
            continue

        selected_coords.append((y, x))
        selected_scores.append(float(scores[index]))

        if len(selected_coords) >= int(target_count):
            break

    if selected_coords:
        selected_array = np.asarray(
            selected_coords,
            dtype=np.int32,
        )

        seed_mask[
            selected_array[:, 0],
            selected_array[:, 1],
        ] = True

        score_array = np.asarray(
            selected_scores,
            dtype=np.float32,
        )
    else:
        selected_array = np.empty((0, 2), dtype=np.int32)
        score_array = np.empty((0,), dtype=np.float32)

    return seed_mask, selected_array, score_array


def _apply_seed_dilation(
    seeds: np.ndarray,
    *,
    radius: int,
    valid_area: np.ndarray,
) -> np.ndarray:
    """Optionally dilate final seed points."""
    if int(radius) <= 0:
        return np.asarray(seeds).astype(bool) & valid_area

    dilated = _dilate_mask(
        seeds,
        int(radius),
    )

    return dilated & valid_area


def select_hybrid_fuzzy_harris_seeds(
    image: np.ndarray,
    *,
    vesselness: Optional[np.ndarray] = None,
    candidate_map: Optional[np.ndarray] = None,
    fov_mask: Optional[np.ndarray] = None,
    srg_params: Optional[SRGFeatureParams] = None,
    harris_params: Optional[HarrisSeedParams] = None,
    hybrid_params: Optional[HybridSeedParams] = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    """
    Select seeds using selective fuzzy-Harris polling.

    Processing steps:
    1. Generate fuzzy SRG seed support.
    2. Generate Harris Corner candidates.
    3. Keep Harris candidates inside or near fuzzy-supported areas.
    4. Rank candidates using fuzzy, Harris, and vesselness responses.
    5. Select spatially separated seed points.
    6. Use controlled fallback only when too few seeds are available.
    """
    hybrid_params = hybrid_params or HybridSeedParams()
    srg_params = srg_params or SRGFeatureParams()
    harris_params = harris_params or HarrisSeedParams()

    image_array = np.asarray(image)

    if image_array.ndim != 2:
        raise ValueError(
            "Hybrid fuzzy-Harris seed selection expects a 2D image"
        )

    shape = image_array.shape

    if vesselness is None:
        vesselness = image_array

    valid_area = _build_valid_area(
        shape,
        candidate_map=candidate_map,
        fov_mask=fov_mask,
        params=hybrid_params,
    )

    empty = np.zeros(shape, dtype=bool)

    if not hybrid_params.enabled:
        return empty, {
            "enabled": False,
            "hybrid_selected_seeds": empty,
            "n_hybrid_seed_pixels": 0,
            "params": hybrid_params.to_dict(),
        }

    # Stage 1: fuzzy SRG support.
    fuzzy_seeds, fuzzy_debug = select_fuzzy_srg_seeds(
        image_array,
        candidate_map=candidate_map,
        fov_mask=fov_mask,
        params=srg_params,
    )

    fuzzy_score = fuzzy_debug.get(
        "fuzzy_seed_score",
        fuzzy_seeds.astype(np.float32),
    )

    strict_fuzzy_support = _dilate_mask(
        fuzzy_seeds,
        hybrid_params.fuzzy_support_radius,
    )
    strict_fuzzy_support &= valid_area

    # Stage 2: Harris candidates.
    harris_seeds, harris_debug = select_harris_seeds(
        image_array,
        vesselness=vesselness,
        candidate_map=candidate_map,
        fov_mask=fov_mask,
        params=harris_params,
    )

    harris_response = harris_debug.get(
        "harris_response",
        np.zeros(shape, dtype=np.float32),
    )

    harris_candidates = harris_debug.get(
        "harris_candidates",
        harris_seeds,
    )
    harris_candidates = np.asarray(harris_candidates).astype(bool)

    # Strict APSRG interpretation:
    # Harris polls seed points that are supported by fuzzy SRG.
    strict_candidates = (
        harris_candidates
        & strict_fuzzy_support
        & valid_area
    )

    hybrid_score = compute_hybrid_seed_score(
        fuzzy_score,
        harris_response,
        np.asarray(vesselness),
        params=hybrid_params,
    )

    target_count = max(int(hybrid_params.target_seed_count), 1)

    if int(hybrid_params.max_seed_count) > 0:
        target_count = min(
            target_count,
            int(hybrid_params.max_seed_count),
        )

    final_candidate_pool = strict_candidates.copy()
    fallback_stage = "strict_fuzzy_harris"

    # Jumlah kandidat yang dibutuhkan untuk mencapai target seed.
    required_pool_size = max(
        int(hybrid_params.min_seed_count),
        int(target_count),
    )

    # Fallback 1:
    # Perluas area dukungan fuzzy ketika kandidat strict belum cukup
    # untuk memenuhi target.
    if (
            int(final_candidate_pool.sum()) < required_pool_size
            and hybrid_params.allow_relaxed_harris_fallback
    ):
        relaxed_support = _dilate_mask(
            fuzzy_seeds,
            hybrid_params.relaxed_support_radius,
        )
        relaxed_support &= valid_area

        relaxed_candidates = (
                harris_candidates
                & relaxed_support
                & valid_area
        )

        final_candidate_pool |= relaxed_candidates
        fallback_stage = "relaxed_fuzzy_harris_to_target"

    else:
        relaxed_support = strict_fuzzy_support.copy()
        relaxed_candidates = strict_candidates.copy()

    # Fallback 2:
    # Tambahkan local maxima pada dukungan fuzzy apabila kandidat
    # Harris masih belum mencukupi target.
    if (
            int(final_candidate_pool.sum()) < required_pool_size
            and hybrid_params.allow_fuzzy_fallback
    ):
        fuzzy_local_maxima = _local_maxima(
            hybrid_score,
            relaxed_support & valid_area,
            radius=hybrid_params.min_seed_distance,
        )

        final_candidate_pool |= fuzzy_local_maxima
        fallback_stage = "fuzzy_local_maxima_to_target"

    else:
        fuzzy_local_maxima = np.zeros(
            shape,
            dtype=bool,
        )

    # PENTING:
    # Blok ini harus berada di luar kedua kondisi fallback.
    # Artinya, seed selalu dipilih apa pun fallback yang aktif.
    seeds, selected_coords, selected_scores = (
        _select_spatially_separated_points(
            hybrid_score,
            final_candidate_pool,
            target_count=target_count,
            min_distance=hybrid_params.min_seed_distance,
        )
    )

    # Dilasi baru dilakukan setelah variabel seeds dibuat.
    seeds = _apply_seed_dilation(
        seeds,
        radius=hybrid_params.seed_dilate_radius,
        valid_area=valid_area,
    )

    debug: dict[str, Any] = {
        "enabled": True,
        "fuzzy_debug": fuzzy_debug,
        "harris_debug": harris_debug,

        "fuzzy_seed_support": fuzzy_seeds,
        "strict_fuzzy_support": strict_fuzzy_support,
        "relaxed_fuzzy_support": relaxed_support,

        "harris_candidates": harris_candidates,
        "strict_hybrid_candidates": strict_candidates,
        "relaxed_hybrid_candidates": relaxed_candidates,
        "fuzzy_local_maxima_fallback": fuzzy_local_maxima,
        "final_hybrid_candidate_pool": final_candidate_pool,

        "hybrid_score": hybrid_score,
        "hybrid_selected_seeds": seeds,

        "selected_coordinates": selected_coords.tolist(),
        "selected_scores": selected_scores.tolist(),

        "fallback_stage": fallback_stage,

        "requested_target_seed_count": int(target_count),
        "required_candidate_pool_size": int(required_pool_size),

        "target_seed_count_reached": bool(
            selected_coords.shape[0] >= target_count
        ),

        "n_fuzzy_seed_pixels": int(
            fuzzy_seeds.sum()
        ),

        "n_harris_candidates": int(
            harris_candidates.sum()
        ),

        "n_strict_hybrid_candidates": int(
            strict_candidates.sum()
        ),

        "n_final_hybrid_candidates": int(
            final_candidate_pool.sum()
        ),

        "n_selected_seed_points": int(
            selected_coords.shape[0]
        ),

        "n_hybrid_seed_pixels": int(
            seeds.sum()
        ),

        "params": hybrid_params.to_dict(),
    }

    return seeds.astype(bool), debug