"""
Fuzzy SRG feature extraction for retinal vessel segmentation.

This module implements the SRG feature layer inspired by Kang et al.'s
seeded region growing method:
- connected edge map,
- not-connected-edge map,
- fuzzy similarity map,
- adaptive fuzzy threshold,
- fuzzy SRG seed selection.

In the original SRG formulation, seeds are selected from regions that have
high local similarity and are not located on connected edges or detailed
background regions. This implementation adapts that idea for the current
CA-APSRG retinal vessel segmentation pipeline.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Optional

import cv2
import numpy as np

from src.utils.image_io import ensure_binary_mask, normalize_to_uint8, to_uint8


@dataclass(frozen=True)
class SRGFeatureParams:
    """Configuration for fuzzy SRG feature extraction."""

    enabled: bool = True

    # Fuzzy edge and similarity parameters.
    wd: float = 0.4
    ws: float = 0.4

    # Window sizes.
    edge_window_size: int = 3
    similarity_window_size: int = 3
    threshold_mean_window_size: int = 5

    # Fuzzy threshold values from Kang et al.
    t_small: float = 0.75
    t_big: float = 0.95

    # Seed constraints.
    use_candidate_constraint: bool = True
    use_fov_constraint: bool = True

    # Fallback when fuzzy seed criterion is too strict.
    fallback_to_ranked_score: bool = True
    min_seed_pixels: int = 20
    max_seed_pixels: int = 5000

    # Optional seed dilation.
    seed_dilate_radius: int = 0

    @classmethod
    def from_dict(cls, config: dict[str, Any] | None) -> "SRGFeatureParams":
        """Create SRGFeatureParams from a dictionary."""
        if not config:
            return cls()

        return cls(
            enabled=bool(config.get("enabled", True)),
            wd=float(config.get("wd", 0.4)),
            ws=float(config.get("ws", 0.4)),
            edge_window_size=int(config.get("edge_window_size", 3)),
            similarity_window_size=int(config.get("similarity_window_size", 3)),
            threshold_mean_window_size=int(config.get("threshold_mean_window_size", 5)),
            t_small=float(config.get("t_small", 0.75)),
            t_big=float(config.get("t_big", 0.95)),
            use_candidate_constraint=bool(config.get("use_candidate_constraint", True)),
            use_fov_constraint=bool(config.get("use_fov_constraint", True)),
            fallback_to_ranked_score=bool(config.get("fallback_to_ranked_score", True)),
            min_seed_pixels=int(config.get("min_seed_pixels", 20)),
            max_seed_pixels=int(config.get("max_seed_pixels", 5000)),
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


def _prepare_gray_float(image: np.ndarray) -> np.ndarray:
    """Convert image to normalized 2D grayscale float32 in [0, 1]."""
    arr = np.asarray(image)

    if arr.ndim == 3:
        arr = cv2.cvtColor(to_uint8(arr), cv2.COLOR_RGB2GRAY)

    if arr.ndim != 2:
        raise ValueError(f"Expected a 2D grayscale image, got shape {arr.shape}")

    arr_uint8 = to_uint8(arr)
    return arr_uint8.astype(np.float32) / 255.0


def _prepare_optional_mask(mask: Optional[np.ndarray], shape: tuple[int, int]) -> Optional[np.ndarray]:
    """Convert optional mask to boolean and validate its shape."""
    if mask is None:
        return None

    mask_bool = ensure_binary_mask(mask, return_uint8=False).astype(bool)

    if mask_bool.shape != shape:
        raise ValueError(f"Mask shape {mask_bool.shape} does not match image shape {shape}")

    return mask_bool


def _shift_reflect(image: np.ndarray, dy: int, dx: int) -> np.ndarray:
    """
    Shift image by dy, dx using reflect padding.

    dy < 0 means taking values from upper neighbor.
    dx < 0 means taking values from left neighbor.
    """
    padded = np.pad(image, ((1, 1), (1, 1)), mode="reflect")
    y_start = 1 + dy
    x_start = 1 + dx
    h, w = image.shape
    return padded[y_start:y_start + h, x_start:x_start + w]


def _clip01(arr: np.ndarray) -> np.ndarray:
    """Clip array into [0, 1]."""
    return np.clip(arr, 0.0, 1.0).astype(np.float32)


def compute_connected_edge_map(
    image: np.ndarray,
    *,
    wd: float = 0.4,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute connected edge map inspired by fuzzy SRG.

    Returns
    -------
    connected_edge:
        Fuzzy membership degree CE in [0, 1].
    edge_intensity:
        Fuzzy edge intensity E in [0, 1].
    edge_direction:
        Direction map D with values 1..4.
    """
    gray = _prepare_gray_float(image)
    wd = max(float(wd), 1e-8)

    # 3x3 neighborhood:
    # x1 x2 x3
    # x4 x5 x6
    # x7 x8 x9
    x1 = _shift_reflect(gray, -1, -1)
    x2 = _shift_reflect(gray, -1, 0)
    x3 = _shift_reflect(gray, -1, 1)
    x4 = _shift_reflect(gray, 0, -1)
    x5 = gray
    x6 = _shift_reflect(gray, 0, 1)
    x7 = _shift_reflect(gray, 1, -1)
    x8 = _shift_reflect(gray, 1, 0)
    x9 = _shift_reflect(gray, 1, 1)

    # Direction 1:
    # S0 = {x1,x2,x4,x5,x7,x8}, S1 = {x3,x6,x9}
    m0_d1 = (x1 + x2 + x4 + x5 + x7 + x8) / 6.0
    m1_d1 = (x3 + x6 + x9) / 3.0
    d1 = _clip01(np.abs(m0_d1 - m1_d1) / wd)

    # Direction 2:
    # S0 = {x1,x2,x3,x4,x5,x6}, S1 = {x7,x8,x9}
    m0_d2 = (x1 + x2 + x3 + x4 + x5 + x6) / 6.0
    m1_d2 = (x7 + x8 + x9) / 3.0
    d2 = _clip01(np.abs(m0_d2 - m1_d2) / wd)

    # Direction 3:
    # S0 = {x1,x2,x3,x5,x6,x9}, S1 = {x4,x7,x8}
    m0_d3 = (x1 + x2 + x3 + x5 + x6 + x9) / 6.0
    m1_d3 = (x4 + x7 + x8) / 3.0
    d3 = _clip01(np.abs(m0_d3 - m1_d3) / wd)

    # Direction 4:
    # S0 = {x1,x2,x3,x4,x5,x7}, S1 = {x6,x8,x9}
    m0_d4 = (x1 + x2 + x3 + x4 + x5 + x7) / 6.0
    m1_d4 = (x6 + x8 + x9) / 3.0
    d4 = _clip01(np.abs(m0_d4 - m1_d4) / wd)

    stacked = np.stack([d1, d2, d3, d4], axis=0)
    edge_intensity = np.max(stacked, axis=0).astype(np.float32)
    edge_direction = (np.argmax(stacked, axis=0) + 1).astype(np.uint8)

    # Connected edge CE based on the selected direction.
    e_up = _shift_reflect(edge_intensity, -1, 0)
    e_down = _shift_reflect(edge_intensity, 1, 0)
    ce_d1 = (e_up + edge_intensity + e_down) / 3.0

    e_left = _shift_reflect(edge_intensity, 0, -1)
    e_right = _shift_reflect(edge_intensity, 0, 1)
    ce_d2 = (e_left + edge_intensity + e_right) / 3.0

    e_up_left = _shift_reflect(edge_intensity, -1, -1)
    e_down_right = _shift_reflect(edge_intensity, 1, 1)
    ce_d3 = (e_up_left + edge_intensity + e_down_right) / 3.0

    e_down_left = _shift_reflect(edge_intensity, 1, -1)
    e_up_right = _shift_reflect(edge_intensity, -1, 1)
    ce_d4 = (e_down_left + edge_intensity + e_up_right) / 3.0

    connected_edge = np.zeros_like(edge_intensity, dtype=np.float32)
    connected_edge = np.where(edge_direction == 1, ce_d1, connected_edge)
    connected_edge = np.where(edge_direction == 2, ce_d2, connected_edge)
    connected_edge = np.where(edge_direction == 3, ce_d3, connected_edge)
    connected_edge = np.where(edge_direction == 4, ce_d4, connected_edge)

    return _clip01(connected_edge), _clip01(edge_intensity), edge_direction


def compute_not_connected_edge_map(connected_edge: np.ndarray) -> np.ndarray:
    """Compute NCE = 1 - CE."""
    return _clip01(1.0 - np.asarray(connected_edge, dtype=np.float32))


def compute_fuzzy_similarity_map(
    image: np.ndarray,
    *,
    ws: float = 0.4,
    window_size: int = 3,
) -> np.ndarray:
    """
    Compute fuzzy similarity map S in [0, 1].

    S is high when the local window is homogeneous and low when the local
    neighborhood has strong detail, noise, or edge variation.
    """
    gray = _prepare_gray_float(image)
    ws = max(float(ws), 1e-8)
    window_size = _ensure_odd(window_size, minimum=3)
    radius = window_size // 2

    local_mean = cv2.blur(
        gray,
        (window_size, window_size),
        borderType=cv2.BORDER_REFLECT,
    )

    distance_sum = np.zeros_like(gray, dtype=np.float32)
    count = 0

    padded = np.pad(gray, ((radius, radius), (radius, radius)), mode="reflect")
    h, w = gray.shape

    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            y_start = radius + dy
            x_start = radius + dx
            shifted = padded[y_start:y_start + h, x_start:x_start + w]
            distance_sum += np.minimum(np.abs(shifted - local_mean) / ws, 1.0)
            count += 1

    similarity = 1.0 - (distance_sum / float(count))
    return _clip01(similarity)


def compute_fuzzy_seed_threshold(
    similarity: np.ndarray,
    not_connected_edge: np.ndarray,
    *,
    t_small: float = 0.75,
    t_big: float = 0.95,
    mean_window_size: int = 5,
) -> np.ndarray:
    """
    Compute adaptive fuzzy threshold Ti,j.

    Rule base:
    - If local similarity is BIG and not-connected-edge is BIG, threshold is SMALL.
    - Otherwise threshold is BIG.

    Because Sbar and NCEbar are already membership degrees in [0,1],
    w1 = Sbar * NCEbar and threshold becomes:
        T = w1 * Tsmall + (1 - w1) * Tbig
    """
    sim = _clip01(similarity)
    nce = _clip01(not_connected_edge)

    mean_window_size = _ensure_odd(mean_window_size, minimum=3)

    sim_mean = cv2.blur(sim, (mean_window_size, mean_window_size), borderType=cv2.BORDER_REFLECT)
    nce_mean = cv2.blur(nce, (mean_window_size, mean_window_size), borderType=cv2.BORDER_REFLECT)

    w1 = _clip01(sim_mean * nce_mean)
    threshold = (w1 * float(t_small)) + ((1.0 - w1) * float(t_big))

    return _clip01(threshold)


def compute_fuzzy_seed_score(
    similarity: np.ndarray,
    not_connected_edge: np.ndarray,
) -> np.ndarray:
    """
    Compute fuzzy seed score.

    The seed criterion in SRG uses min(NCE, S), so the same value is useful
    as a ranking score when fallback is needed.
    """
    return np.minimum(_clip01(similarity), _clip01(not_connected_edge)).astype(np.float32)


def _build_valid_area(
    shape: tuple[int, int],
    *,
    candidate_map: Optional[np.ndarray] = None,
    fov_mask: Optional[np.ndarray] = None,
    params: SRGFeatureParams,
) -> np.ndarray:
    """Build valid area for fuzzy SRG seed selection."""
    valid = np.ones(shape, dtype=bool)

    if candidate_map is not None and params.use_candidate_constraint:
        candidate = _prepare_optional_mask(candidate_map, shape)
        if candidate is not None:
            valid &= candidate

    if fov_mask is not None and params.use_fov_constraint:
        fov = _prepare_optional_mask(fov_mask, shape)
        if fov is not None:
            valid &= fov

    return valid


def _select_top_score_pixels(
    score: np.ndarray,
    valid_area: np.ndarray,
    *,
    max_pixels: int,
) -> np.ndarray:
    """Select top pixels by score inside valid area."""
    mask = np.zeros_like(valid_area, dtype=bool)

    coords = np.argwhere(valid_area)
    if coords.size == 0 or max_pixels <= 0:
        return mask

    scores = score[coords[:, 0], coords[:, 1]]
    order = np.argsort(scores)[::-1]
    selected = coords[order[: int(max_pixels)]]

    mask[selected[:, 0], selected[:, 1]] = True
    return mask


def _dilate_seed_mask(seed_mask: np.ndarray, radius: int, valid_area: np.ndarray) -> np.ndarray:
    """Dilate seed mask with optional radius."""
    if int(radius) <= 0:
        return seed_mask.astype(bool)

    kernel_size = 2 * int(radius) + 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    dilated = cv2.dilate(seed_mask.astype(np.uint8), kernel).astype(bool)
    return dilated & valid_area


def select_fuzzy_srg_seeds(
    image: np.ndarray,
    *,
    candidate_map: Optional[np.ndarray] = None,
    fov_mask: Optional[np.ndarray] = None,
    params: SRGFeatureParams | None = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    """
    Select fuzzy SRG seeds.

    Seed criterion:
        min(NCE_i,j, S_i,j) >= T_i,j

    For retinal vessel segmentation, seed candidates can optionally be
    constrained by candidate vessel map and FoV mask.
    """
    params = params or SRGFeatureParams()
    gray = _prepare_gray_float(image)
    shape = gray.shape

    if not params.enabled:
        empty = np.zeros(shape, dtype=bool)
        return empty, {
            "enabled": False,
            "connected_edge": np.zeros(shape, dtype=np.float32),
            "not_connected_edge": np.zeros(shape, dtype=np.float32),
            "fuzzy_similarity": np.zeros(shape, dtype=np.float32),
            "fuzzy_threshold": np.zeros(shape, dtype=np.float32),
            "fuzzy_seed_score": np.zeros(shape, dtype=np.float32),
            "fuzzy_srg_seeds": empty,
            "n_fuzzy_srg_seed_pixels": 0,
            "params": params.to_dict(),
        }

    connected_edge, edge_intensity, edge_direction = compute_connected_edge_map(
        gray,
        wd=params.wd,
    )
    not_connected_edge = compute_not_connected_edge_map(connected_edge)

    fuzzy_similarity = compute_fuzzy_similarity_map(
        gray,
        ws=params.ws,
        window_size=params.similarity_window_size,
    )

    fuzzy_threshold = compute_fuzzy_seed_threshold(
        fuzzy_similarity,
        not_connected_edge,
        t_small=params.t_small,
        t_big=params.t_big,
        mean_window_size=params.threshold_mean_window_size,
    )

    seed_score = compute_fuzzy_seed_score(fuzzy_similarity, not_connected_edge)

    valid_area = _build_valid_area(
        shape,
        candidate_map=candidate_map,
        fov_mask=fov_mask,
        params=params,
    )

    seeds = (seed_score >= fuzzy_threshold) & valid_area

    if int(params.max_seed_pixels) > 0 and int(seeds.sum()) > int(params.max_seed_pixels):
        seeds = _select_top_score_pixels(
            seed_score,
            valid_area & seeds,
            max_pixels=int(params.max_seed_pixels),
        )

    if int(seeds.sum()) < int(params.min_seed_pixels) and params.fallback_to_ranked_score:
        fallback_pixels = max(int(params.min_seed_pixels), min(int(params.max_seed_pixels), int(valid_area.sum())))
        seeds = _select_top_score_pixels(
            seed_score,
            valid_area,
            max_pixels=fallback_pixels,
        )

    seeds = _dilate_seed_mask(
        seeds.astype(bool),
        radius=params.seed_dilate_radius,
        valid_area=valid_area,
    )

    debug: dict[str, Any] = {
        "enabled": True,
        "connected_edge": connected_edge,
        "edge_intensity": edge_intensity,
        "edge_direction": edge_direction,
        "not_connected_edge": not_connected_edge,
        "fuzzy_similarity": fuzzy_similarity,
        "fuzzy_threshold": fuzzy_threshold,
        "fuzzy_seed_score": seed_score,
        "fuzzy_srg_seeds": seeds,
        "valid_seed_area": valid_area,
        "n_fuzzy_srg_seed_pixels": int(seeds.sum()),
        "n_valid_seed_area_pixels": int(valid_area.sum()),
        "params": params.to_dict(),
    }

    return seeds.astype(bool), debug


def extract_srg_feature_maps(
    image: np.ndarray,
    *,
    candidate_map: Optional[np.ndarray] = None,
    fov_mask: Optional[np.ndarray] = None,
    params: SRGFeatureParams | None = None,
) -> dict[str, Any]:
    """Compute SRG feature maps without necessarily using the seeds."""
    params = params or SRGFeatureParams()
    seeds, debug = select_fuzzy_srg_seeds(
        image,
        candidate_map=candidate_map,
        fov_mask=fov_mask,
        params=params,
    )
    debug["seeds"] = seeds
    return debug


def srg_debug_maps_to_uint8(debug: dict[str, Any]) -> dict[str, np.ndarray]:
    """
    Convert selected SRG debug maps to uint8 for saving/display.

    This helper is optional but useful for Streamlit and debug output.
    """
    keys = [
        "connected_edge",
        "edge_intensity",
        "not_connected_edge",
        "fuzzy_similarity",
        "fuzzy_threshold",
        "fuzzy_seed_score",
        "fuzzy_srg_seeds",
        "valid_seed_area",
    ]

    output: dict[str, np.ndarray] = {}
    for key in keys:
        if key not in debug:
            continue

        arr = debug[key]
        if isinstance(arr, np.ndarray):
            if arr.dtype == bool:
                output[key] = arr.astype(np.uint8) * 255
            else:
                output[key] = normalize_to_uint8(arr)

    return output