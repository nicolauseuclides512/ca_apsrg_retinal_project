"""
APSRG process-context extraction for CA-APSRG.

This module converts APSRG debug information into compact contextual
features that can be used by the CA-APSRG refinement stage.

The process context complements mask-based context features:

Mask context:
- vessel density,
- connected components,
- small component ratio,
- skeleton structure.

APSRG process context:
- seed count and seed density,
- candidate vessel density,
- region-growing expansion ratio,
- Harris and fuzzy seed statistics,
- connected-edge density,
- maximum-iteration status,
- process-level refinement recommendation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Optional

import numpy as np

from src.utils.image_io import ensure_binary_mask


@dataclass(frozen=True)
class APSRGProcessContextConfig:
    """Configuration for interpreting APSRG processing behaviour."""

    enabled: bool = True

    # Whether process context can influence CA-APSRG.
    can_trigger_refinement: bool = True
    can_override_refinement_level: bool = False

    # Seed-count limits inspired by APSRG polling experiments.
    low_seed_count: int = 7
    high_seed_count: int = 77

    # Process-risk thresholds.
    high_candidate_density: float = 0.25
    high_connected_edge_density: float = 0.20
    connected_edge_threshold: float = 0.50
    high_growth_ratio: float = 600.0

    # If region growing reaches the iteration limit, treat it as high risk.
    max_iterations_is_high_risk: bool = True

    @classmethod
    def from_dict(
        cls,
        config: dict[str, Any] | None,
    ) -> "APSRGProcessContextConfig":
        """Create configuration from a YAML-like dictionary."""
        if not config:
            return cls()

        return cls(
            enabled=bool(config.get("enabled", True)),
            can_trigger_refinement=bool(
                config.get("can_trigger_refinement", True)
            ),
            can_override_refinement_level=bool(
                config.get("can_override_refinement_level", False)
            ),
            low_seed_count=int(config.get("low_seed_count", 7)),
            high_seed_count=int(config.get("high_seed_count", 77)),
            high_candidate_density=float(
                config.get("high_candidate_density", 0.25)
            ),
            high_connected_edge_density=float(
                config.get("high_connected_edge_density", 0.20)
            ),
            connected_edge_threshold=float(
                config.get("connected_edge_threshold", 0.50)
            ),
            high_growth_ratio=float(
                config.get("high_growth_ratio", 600.0)
            ),
            max_iterations_is_high_risk=bool(
                config.get("max_iterations_is_high_risk", True)
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return configuration as dictionary."""
        return asdict(self)


@dataclass(frozen=True)
class APSRGProcessContext:
    """Compact descriptor of APSRG seed and region-growing behaviour."""

    seed_selection_method: str
    region_growing_mode: str

    valid_area_pixel_count: int
    seed_pixel_count: int
    selected_seed_point_count: int
    candidate_pixel_count: int
    output_pixel_count: int

    seed_density: float
    candidate_density: float
    output_density: float
    growth_ratio: float

    fuzzy_seed_pixel_count: int
    harris_candidate_count: int
    strict_hybrid_candidate_count: int
    initial_seed_component_count: int
    accepted_growth_pixel_count: int

    connected_edge_mean: float
    connected_edge_density: float

    max_iterations_reached: bool

    process_risk_score: int
    process_risk_level: str
    recommended_refinement_level: str

    def to_dict(self) -> dict[str, Any]:
        """Return context as dictionary."""
        return asdict(self)


def _find_nested_value(
    data: Any,
    candidate_keys: Iterable[str],
    default: Any = None,
) -> Any:
    """Recursively find the first matching key in nested dictionaries."""
    keys = set(candidate_keys)

    if isinstance(data, dict):
        for key in keys:
            if key in data:
                return data[key]

        for value in data.values():
            if isinstance(value, dict):
                found = _find_nested_value(
                    value,
                    keys,
                    default=None,
                )
                if found is not None:
                    return found

    return default


def _find_nested_array(
    data: Any,
    candidate_keys: Iterable[str],
) -> Optional[np.ndarray]:
    """Recursively find a NumPy array stored under one of the keys."""
    value = _find_nested_value(
        data,
        candidate_keys,
        default=None,
    )

    if isinstance(value, np.ndarray):
        return value

    return None


def _safe_int(value: Any, default: int = 0) -> int:
    """Convert value into integer safely."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _safe_float(value: Any, default: float = 0.0) -> float:
    """Convert value into float safely."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _safe_ratio(
    numerator: float,
    denominator: float,
    default: float = 0.0,
) -> float:
    """Compute a division while protecting against zero denominator."""
    if float(denominator) <= 0.0:
        return float(default)

    return float(numerator) / float(denominator)


def _prepare_valid_area(
    apsrg_debug: dict[str, Any],
    fov_mask: Optional[np.ndarray],
) -> tuple[np.ndarray, int]:
    """Build the valid image area used for process density computation."""
    candidate = _find_nested_array(
        apsrg_debug,
        ["candidate"],
    )

    connected_edge = _find_nested_array(
        apsrg_debug,
        ["connected_edge"],
    )

    reference_shape: tuple[int, int] | None = None

    if candidate is not None and candidate.ndim == 2:
        reference_shape = candidate.shape
    elif connected_edge is not None and connected_edge.ndim == 2:
        reference_shape = connected_edge.shape

    if fov_mask is not None:
        fov = ensure_binary_mask(
            fov_mask,
            return_uint8=False,
        ).astype(bool)

        if reference_shape is not None and fov.shape != reference_shape:
            raise ValueError(
                f"FoV shape {fov.shape} does not match APSRG debug "
                f"shape {reference_shape}"
            )

        return fov, int(fov.sum())

    if reference_shape is not None:
        valid = np.ones(reference_shape, dtype=bool)
        return valid, int(valid.sum())

    return np.ones((1, 1), dtype=bool), 1


def _compute_connected_edge_statistics(
    apsrg_debug: dict[str, Any],
    valid_area: np.ndarray,
    *,
    threshold: float,
) -> tuple[float, float]:
    """Compute mean CE membership and strong-connected-edge density."""
    connected_edge = _find_nested_array(
        apsrg_debug,
        ["connected_edge"],
    )

    if connected_edge is None:
        return 0.0, 0.0

    edge = np.asarray(
        connected_edge,
        dtype=np.float32,
    )

    if edge.shape != valid_area.shape:
        return 0.0, 0.0

    values = edge[valid_area]

    if values.size == 0:
        return 0.0, 0.0

    mean_value = float(np.mean(values))
    density = float(
        np.mean(values >= float(threshold))
    )

    return mean_value, density


def _classify_process_context(
    *,
    seed_count: int,
    candidate_density: float,
    connected_edge_density: float,
    growth_ratio: float,
    max_iterations_reached: bool,
    config: APSRGProcessContextConfig,
) -> tuple[int, str, str]:
    """
    Determine process risk and refinement recommendation.

    Conservative:
        APSRG provides very few seeds and refinement should avoid removing
        additional thin-vessel structures.

    Aggressive:
        APSRG produces a broad candidate region, strong edge response,
        unusually large growth, or reaches the iteration limit.

    Normal:
        APSRG processing remains between these conditions.
    """
    risk_score = 0

    if candidate_density >= config.high_candidate_density:
        risk_score += 1

    if connected_edge_density >= config.high_connected_edge_density:
        risk_score += 1

    if growth_ratio >= config.high_growth_ratio:
        risk_score += 1

    if seed_count > config.high_seed_count:
        risk_score += 1

    if (
        max_iterations_reached
        and config.max_iterations_is_high_risk
    ):
        risk_score += 2

    if risk_score >= 2:
        return risk_score, "high", "aggressive"

    if seed_count <= config.low_seed_count:
        return risk_score, "low", "conservative"

    if risk_score == 1:
        return risk_score, "medium", "normal"

    return risk_score, "low", "normal"


def extract_apsrg_process_context(
    apsrg_debug: dict[str, Any] | None,
    *,
    fov_mask: Optional[np.ndarray] = None,
    config: APSRGProcessContextConfig | None = None,
) -> APSRGProcessContext:
    """Extract APSRG process-level context from the debug dictionary."""
    cfg = config or APSRGProcessContextConfig()
    debug = apsrg_debug or {}

    valid_area, valid_area_count = _prepare_valid_area(
        debug,
        fov_mask,
    )

    params = debug.get("params", {}) or {}

    seed_selection_method = str(
        params.get(
            "seed_selection_method",
            _find_nested_value(
                debug,
                ["method"],
                default="unknown",
            ),
        )
    )

    region_growing_mode = str(
        params.get(
            "region_growing_mode",
            _find_nested_value(
                debug,
                ["mode"],
                default="unknown",
            ),
        )
    )

    seed_count = _safe_int(
        debug.get(
            "n_seed_pixels",
            _find_nested_value(
                debug,
                ["n_hybrid_seed_pixels", "n_initial_seed_pixels"],
                default=0,
            ),
        )
    )

    selected_seed_points = _safe_int(
        _find_nested_value(
            debug,
            ["n_selected_seed_points", "selected_seed_count"],
            default=seed_count,
        )
    )

    candidate_count = _safe_int(
        debug.get(
            "n_candidate_pixels",
            _find_nested_value(
                debug,
                ["n_candidate_pixels"],
                default=0,
            ),
        )
    )

    output_count = _safe_int(
        debug.get(
            "n_output_pixels",
            _find_nested_value(
                debug,
                ["n_output_pixels"],
                default=0,
            ),
        )
    )

    fuzzy_seed_count = _safe_int(
        _find_nested_value(
            debug,
            [
                "n_fuzzy_seed_pixels",
                "n_fuzzy_srg_seed_pixels",
            ],
            default=0,
        )
    )

    harris_candidate_count = _safe_int(
        _find_nested_value(
            debug,
            ["n_harris_candidates"],
            default=0,
        )
    )

    strict_hybrid_candidate_count = _safe_int(
        _find_nested_value(
            debug,
            ["n_strict_hybrid_candidates"],
            default=0,
        )
    )

    initial_seed_components = _safe_int(
        _find_nested_value(
            debug,
            ["n_initial_seed_components"],
            default=0,
        )
    )

    accepted_growth_pixels = _safe_int(
        _find_nested_value(
            debug,
            ["n_accepted_growth_pixels"],
            default=0,
        )
    )

    max_iterations_reached = bool(
        _find_nested_value(
            debug,
            ["max_iterations_reached"],
            default=False,
        )
    )

    seed_density = _safe_ratio(
        seed_count,
        valid_area_count,
    )

    candidate_density = _safe_ratio(
        candidate_count,
        valid_area_count,
    )

    output_density = _safe_ratio(
        output_count,
        valid_area_count,
    )

    growth_ratio = _safe_ratio(
        output_count,
        max(seed_count, 1),
    )

    (
        connected_edge_mean,
        connected_edge_density,
    ) = _compute_connected_edge_statistics(
        debug,
        valid_area,
        threshold=cfg.connected_edge_threshold,
    )

    (
        risk_score,
        risk_level,
        recommended_level,
    ) = _classify_process_context(
        seed_count=selected_seed_points,
        candidate_density=candidate_density,
        connected_edge_density=connected_edge_density,
        growth_ratio=growth_ratio,
        max_iterations_reached=max_iterations_reached,
        config=cfg,
    )

    return APSRGProcessContext(
        seed_selection_method=seed_selection_method,
        region_growing_mode=region_growing_mode,
        valid_area_pixel_count=int(valid_area_count),
        seed_pixel_count=int(seed_count),
        selected_seed_point_count=int(selected_seed_points),
        candidate_pixel_count=int(candidate_count),
        output_pixel_count=int(output_count),
        seed_density=float(seed_density),
        candidate_density=float(candidate_density),
        output_density=float(output_density),
        growth_ratio=float(growth_ratio),
        fuzzy_seed_pixel_count=int(fuzzy_seed_count),
        harris_candidate_count=int(harris_candidate_count),
        strict_hybrid_candidate_count=int(
            strict_hybrid_candidate_count
        ),
        initial_seed_component_count=int(
            initial_seed_components
        ),
        accepted_growth_pixel_count=int(
            accepted_growth_pixels
        ),
        connected_edge_mean=float(connected_edge_mean),
        connected_edge_density=float(
            connected_edge_density
        ),
        max_iterations_reached=bool(
            max_iterations_reached
        ),
        process_risk_score=int(risk_score),
        process_risk_level=str(risk_level),
        recommended_refinement_level=str(
            recommended_level
        ),
    )