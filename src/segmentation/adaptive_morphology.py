"""
Adaptive morphological refinement for CA-APSRG retinal vessel segmentation.

This module is the main refinement stage after APSRG baseline segmentation.
It uses context features extracted from the preliminary APSRG mask to choose
morphological parameters adaptively.

Main goals:
- Reduce false positives from isolated noisy components.
- Preserve thin vessel structures as much as possible.
- Keep the refinement interpretable and configurable.

Conventions:
- Input baseline mask: bool or 0/255 uint8, shape (H, W).
- Optional FoV mask: bool or 0/255 uint8, shape (H, W).
- Output refined mask: boolean array, shape (H, W).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

import cv2
import numpy as np
from skimage.morphology import skeletonize

from src.segmentation.skimage_compat import remove_small_holes_compat
from src.segmentation.context_features import (
    ContextFeatureConfig,
    ContextFeatures,
    extract_context_features,
)
from src.utils.image_io import (
    ensure_binary_mask,
    read_binary_mask,
    save_binary_mask,
    resize_if_needed,
)


@dataclass(frozen=True)
class AdaptiveMorphologyConfig:
    """Configuration for context-aware adaptive morphological refinement."""

    enabled: bool = True

    remove_small_objects: bool = True
    fill_small_holes: bool = True
    closing_enabled: bool = True
    opening_enabled: bool = False
    skeleton_guard_enabled: bool = True

    small_component_area_low_density: int = 8
    small_component_area_normal: int = 14
    small_component_area_high_density: int = 24

    hole_area_low_density: int = 8
    hole_area_normal: int = 16
    hole_area_high_density: int = 32

    closing_kernel_low_density: int = 3
    closing_kernel_normal: int = 3
    closing_kernel_high_density: int = 5

    opening_kernel_low_density: int = 0
    opening_kernel_normal: int = 3
    opening_kernel_high_density: int = 3

    low_density_threshold: float = 0.025
    high_density_threshold: float = 0.120

    skeleton_restore_radius: int = 1
    skeleton_min_component_length: int = 6

    @classmethod
    def from_dict(
        cls,
        config: dict[str, Any] | None,
        *,
        ca_apsrg_config: dict[str, Any] | None = None,
    ) -> "AdaptiveMorphologyConfig":
        """
        Create AdaptiveMorphologyConfig from config['adaptive_morphology'].

        ca_apsrg_config can optionally provide low_density_threshold and
        high_density_threshold when those thresholds are stored under
        config['ca_apsrg'].
        """
        config = config or {}
        ca_apsrg_config = ca_apsrg_config or {}

        return cls(
            enabled=bool(config.get("enabled", True)),
            remove_small_objects=bool(config.get("remove_small_objects", True)),
            fill_small_holes=bool(config.get("fill_small_holes", True)),
            closing_enabled=bool(config.get("closing_enabled", True)),
            opening_enabled=bool(config.get("opening_enabled", False)),
            skeleton_guard_enabled=bool(config.get("skeleton_guard_enabled", True)),
            small_component_area_low_density=int(config.get("small_component_area_low_density", 8)),
            small_component_area_normal=int(config.get("small_component_area_normal", 14)),
            small_component_area_high_density=int(config.get("small_component_area_high_density", 24)),
            hole_area_low_density=int(config.get("hole_area_low_density", 8)),
            hole_area_normal=int(config.get("hole_area_normal", 16)),
            hole_area_high_density=int(config.get("hole_area_high_density", 32)),
            closing_kernel_low_density=int(config.get("closing_kernel_low_density", 3)),
            closing_kernel_normal=int(config.get("closing_kernel_normal", 3)),
            closing_kernel_high_density=int(config.get("closing_kernel_high_density", 5)),
            opening_kernel_low_density=int(config.get("opening_kernel_low_density", 0)),
            opening_kernel_normal=int(config.get("opening_kernel_normal", 3)),
            opening_kernel_high_density=int(config.get("opening_kernel_high_density", 3)),
            low_density_threshold=float(
                config.get(
                    "low_density_threshold",
                    ca_apsrg_config.get("low_density_threshold", 0.025),
                )
            ),
            high_density_threshold=float(
                config.get(
                    "high_density_threshold",
                    ca_apsrg_config.get("high_density_threshold", 0.120),
                )
            ),
            skeleton_restore_radius=int(config.get("skeleton_restore_radius", 1)),
            skeleton_min_component_length=int(config.get("skeleton_min_component_length", 6)),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return config as a dictionary."""
        return asdict(self)


@dataclass(frozen=True)
class SelectedMorphologyParams:
    """Morphological parameters selected from context features."""

    refinement_level: str
    density_level: str
    noise_level: str
    min_component_area: int
    hole_area: int
    closing_kernel_size: int
    opening_kernel_size: int
    use_opening: bool
    use_closing: bool
    use_skeleton_guard: bool

    def to_dict(self) -> dict[str, Any]:
        """Return selected parameters as a dictionary."""
        return asdict(self)


AdaptiveMorphologyParams = AdaptiveMorphologyConfig


def _prepare_mask(mask: np.ndarray) -> np.ndarray:
    """Convert input mask to boolean array."""
    return ensure_binary_mask(mask, return_uint8=False)


def _prepare_fov(fov_mask: Optional[np.ndarray], reference_shape: tuple[int, int]) -> Optional[np.ndarray]:
    """Convert optional FoV mask to boolean array matching reference shape."""
    if fov_mask is None:
        return None

    fov = ensure_binary_mask(fov_mask, return_uint8=False)
    if fov.shape != reference_shape:
        fov = resize_if_needed(fov.astype(np.uint8), reference_shape, interpolation="nearest") > 0

    return fov.astype(bool)


def _odd_kernel_size(kernel_size: int) -> int:
    """Return a valid odd morphology kernel size. A value <= 0 disables the operation."""
    kernel_size = int(kernel_size)
    if kernel_size <= 0:
        return 0
    if kernel_size % 2 == 0:
        kernel_size += 1
    return max(kernel_size, 3)


def _ellipse_kernel(kernel_size: int) -> Optional[np.ndarray]:
    """Create an elliptical structuring element or return None when disabled."""
    k = _odd_kernel_size(kernel_size)
    if k <= 0:
        return None
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))


def remove_components_by_area(mask: np.ndarray, min_area: int = 8, *, connectivity: int = 8) -> np.ndarray:
    """Remove connected components whose area is smaller than min_area."""
    mask_bool = _prepare_mask(mask)
    min_area = int(min_area)

    if min_area <= 1:
        return mask_bool

    conn = 8 if int(connectivity) == 8 else 4
    mask_u8 = mask_bool.astype(np.uint8)
    n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask_u8, connectivity=conn)

    cleaned = np.zeros_like(mask_bool, dtype=bool)
    for label in range(1, n_labels):
        area = int(stats[label, cv2.CC_STAT_AREA])
        if area >= min_area:
            cleaned[labels == label] = True

    return cleaned


_remove_components_by_area = remove_components_by_area


def fill_holes_adaptive(mask: np.ndarray, hole_area: int = 16) -> np.ndarray:
    """Fill small holes in vessel regions."""
    mask_bool = _prepare_mask(mask)
    hole_area = int(hole_area)

    if hole_area <= 0:
        return mask_bool

    return remove_small_holes_compat(mask_bool, area_threshold=hole_area)


def apply_morphological_closing(mask: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """Apply morphological closing to reconnect nearby vessel fragments."""
    mask_bool = _prepare_mask(mask)
    kernel = _ellipse_kernel(kernel_size)

    if kernel is None:
        return mask_bool

    closed = cv2.morphologyEx(mask_bool.astype(np.uint8), cv2.MORPH_CLOSE, kernel)
    return closed.astype(bool)


def apply_morphological_opening(mask: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """Apply morphological opening to suppress small isolated false positives."""
    mask_bool = _prepare_mask(mask)
    kernel = _ellipse_kernel(kernel_size)

    if kernel is None:
        return mask_bool

    opened = cv2.morphologyEx(mask_bool.astype(np.uint8), cv2.MORPH_OPEN, kernel)
    return opened.astype(bool)


def _remove_short_skeleton_components(
    skeleton: np.ndarray,
    *,
    min_length: int = 6,
    connectivity: int = 8,
) -> np.ndarray:
    """Remove very short skeleton fragments before restoration."""
    min_length = int(min_length)
    if min_length <= 1:
        return _prepare_mask(skeleton)

    return remove_components_by_area(skeleton, min_area=min_length, connectivity=connectivity)


def skeleton_guard_restore(
    refined_mask: np.ndarray,
    baseline_mask: np.ndarray,
    *,
    radius: int = 1,
    min_skeleton_component_length: int = 6,
    fov_mask: Optional[np.ndarray] = None,
) -> np.ndarray:
    """
    Restore likely thin vessel centerlines removed during refinement.

    This guard does not simply OR the full baseline skeleton back into the
    result, because that can reintroduce isolated false positives. Instead, it
    restores skeleton pixels that are close to the refined result and belong to
    skeleton fragments of sufficient length.
    """
    refined = _prepare_mask(refined_mask)
    baseline = _prepare_mask(baseline_mask)

    if baseline.sum() == 0:
        return refined

    skeleton = skeletonize(baseline).astype(bool)
    skeleton = _remove_short_skeleton_components(
        skeleton,
        min_length=min_skeleton_component_length,
        connectivity=8,
    )

    if radius <= 0:
        near_refined = refined
    else:
        kernel_size = 2 * int(radius) + 1
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        near_refined = cv2.dilate(refined.astype(np.uint8), kernel).astype(bool)

    restored = refined | (skeleton & near_refined)

    if fov_mask is not None:
        fov = _prepare_fov(fov_mask, restored.shape)
        restored &= fov

    return restored.astype(bool)


def select_adaptive_parameters(
    features: ContextFeatures,
    config: AdaptiveMorphologyConfig | None = None,
) -> SelectedMorphologyParams:
    """
    Select morphological parameters based on context features.

    Rules:
    - low vessel density: conservative filtering,
    - high noise or high vessel density: stronger filtering,
    - otherwise: normal refinement.
    """
    cfg = config or AdaptiveMorphologyConfig()

    density_level = str(features.density_level).lower()
    noise_level = str(features.noise_level).lower()
    refinement_level = str(features.recommended_refinement_level).lower()

    if refinement_level not in {"conservative", "normal", "aggressive"}:
        if density_level == "low":
            refinement_level = "conservative"
        elif density_level == "high" or noise_level == "high":
            refinement_level = "aggressive"
        else:
            refinement_level = "normal"

    if refinement_level == "conservative":
        min_component_area = cfg.small_component_area_low_density
        hole_area = cfg.hole_area_low_density
        closing_kernel_size = cfg.closing_kernel_low_density
        opening_kernel_size = cfg.opening_kernel_low_density
    elif refinement_level == "aggressive":
        min_component_area = cfg.small_component_area_high_density
        hole_area = cfg.hole_area_high_density
        closing_kernel_size = cfg.closing_kernel_high_density
        opening_kernel_size = cfg.opening_kernel_high_density
    else:
        min_component_area = cfg.small_component_area_normal
        hole_area = cfg.hole_area_normal
        closing_kernel_size = cfg.closing_kernel_normal
        opening_kernel_size = cfg.opening_kernel_normal

    use_opening = bool(cfg.opening_enabled and opening_kernel_size > 0)
    use_closing = bool(cfg.closing_enabled and closing_kernel_size > 0)
    use_skeleton_guard = bool(cfg.skeleton_guard_enabled)

    if density_level == "low":
        use_opening = False

    return SelectedMorphologyParams(
        refinement_level=refinement_level,
        density_level=density_level,
        noise_level=noise_level,
        min_component_area=int(min_component_area),
        hole_area=int(hole_area),
        closing_kernel_size=int(closing_kernel_size),
        opening_kernel_size=int(opening_kernel_size),
        use_opening=use_opening,
        use_closing=use_closing,
        use_skeleton_guard=use_skeleton_guard,
    )


_select_adaptive_parameters = select_adaptive_parameters


def adaptive_morphological_refinement(
    baseline_mask: np.ndarray,
    fov_mask: np.ndarray | None = None,
    params: AdaptiveMorphologyConfig | None = None,
    *,
    context_config: ContextFeatureConfig | None = None,
    precomputed_features: ContextFeatures | None = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    """
    Refine APSRG baseline mask using context-aware adaptive morphology.

    Returns
    -------
    refined_mask:
        Boolean refined vessel mask.
    debug_info:
        Dictionary containing context features, selected parameters, and
        intermediate masks useful for debugging/visualization.
    """
    cfg = params or AdaptiveMorphologyConfig()

    baseline = _prepare_mask(baseline_mask)
    fov = _prepare_fov(fov_mask, baseline.shape)

    if fov is not None:
        baseline = baseline & fov

    if precomputed_features is not None:
        if not isinstance(precomputed_features, ContextFeatures):
            raise TypeError(
                "precomputed_features must be a ContextFeatures instance"
            )

        features = precomputed_features

    else:
        features = extract_context_features(
            baseline,
            fov_mask=fov,
            config=context_config,
            low_density_threshold=cfg.low_density_threshold,
            high_density_threshold=cfg.high_density_threshold,
        )
    selected = select_adaptive_parameters(features, cfg)

    if not cfg.enabled:
        debug_disabled = {
            "enabled": False,
            "context_features": features.to_dict(),
            "selected_parameters": selected.to_dict(),
            "notes": "adaptive morphology disabled; returning baseline mask",
        }
        return baseline.astype(bool), debug_disabled

    current = baseline.copy()
    debug_intermediate: dict[str, np.ndarray] = {"baseline": baseline.copy()}

    if cfg.remove_small_objects:
        current = remove_components_by_area(current, min_area=selected.min_component_area, connectivity=8)
        debug_intermediate["after_remove_small_objects"] = current.copy()

    if cfg.fill_small_holes:
        current = fill_holes_adaptive(current, hole_area=selected.hole_area)
        debug_intermediate["after_fill_small_holes"] = current.copy()

    if selected.use_closing:
        current = apply_morphological_closing(current, kernel_size=selected.closing_kernel_size)
        debug_intermediate["after_closing"] = current.copy()

    if selected.use_opening:
        current = apply_morphological_opening(current, kernel_size=selected.opening_kernel_size)
        debug_intermediate["after_opening"] = current.copy()

    if selected.use_skeleton_guard:
        current = skeleton_guard_restore(
            current,
            baseline,
            radius=cfg.skeleton_restore_radius,
            min_skeleton_component_length=cfg.skeleton_min_component_length,
            fov_mask=fov,
        )
        debug_intermediate["after_skeleton_guard"] = current.copy()

    if fov is not None:
        current &= fov

    current = current.astype(bool)

    refined_features = extract_context_features(
        current,
        fov_mask=fov,
        config=context_config,
        low_density_threshold=cfg.low_density_threshold,
        high_density_threshold=cfg.high_density_threshold,
    )

    debug: dict[str, Any] = {
        "enabled": True,
        "context_features": features.to_dict(),
        "refined_context_features": refined_features.to_dict(),
        "selected_parameters": selected.to_dict(),
        "config": cfg.to_dict(),
        "intermediate_masks": debug_intermediate,
        "n_pixels_before": int(baseline.sum()),
        "n_pixels_after": int(current.sum()),
        "n_pixels_removed": int(max(int(baseline.sum()) - int(current.sum()), 0)),
        "n_pixels_added": int(max(int(current.sum()) - int(baseline.sum()), 0)),
    }

    return current, debug


def refine_mask(
    baseline_mask: np.ndarray,
    fov_mask: np.ndarray | None = None,
    config: AdaptiveMorphologyConfig | None = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Alias for adaptive_morphological_refinement()."""
    return adaptive_morphological_refinement(baseline_mask, fov_mask=fov_mask, params=config)


def apply_adaptive_morphology(
    baseline_mask: np.ndarray,
    fov_mask: np.ndarray | None = None,
    config: AdaptiveMorphologyConfig | None = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Alias for adaptive_morphological_refinement()."""
    return adaptive_morphological_refinement(baseline_mask, fov_mask=fov_mask, params=config)


def adaptive_morphology_from_files(
    baseline_mask_path: str | Path,
    output_mask_path: str | Path,
    fov_path: str | Path | None = None,
    *,
    config: AdaptiveMorphologyConfig | None = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Read baseline mask, refine it, save the result, and return mask/debug info."""
    baseline = read_binary_mask(baseline_mask_path)
    fov = read_binary_mask(fov_path) if fov_path else None

    refined, debug = adaptive_morphological_refinement(baseline, fov_mask=fov, params=config)
    save_binary_mask(output_mask_path, refined)

    return refined, debug
