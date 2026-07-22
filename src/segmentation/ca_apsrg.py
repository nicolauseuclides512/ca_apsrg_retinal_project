"""
CA-APSRG context-aware refinement module.

This module combines the APSRG baseline with context-aware adaptive
morphological refinement. It is the main method proposed in the project:

    APSRG mask
    -> context feature extraction
    -> refinement-level decision
    -> adaptive morphological refinement
    -> CA-APSRG vessel mask

SRG supplies fuzzy/connected-edge growing; the adapted APSRG baseline adds
automatic Harris polling. CA-APSRG is the subsequent conservative context
refinement. The full-pipeline function remains for compatibility, while
``ca_apsrg_refine`` is the boundary of the CA-specific development.

Conventions:
- Input image: preprocessed grayscale uint8, shape (H, W).
- Optional FoV mask: bool or 0/255 uint8, shape (H, W).
- Output masks: boolean arrays, shape (H, W).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any, Optional

import numpy as np

from src.segmentation.adaptive_morphology import (
    AdaptiveMorphologyConfig,
    adaptive_morphological_refinement,
)
from src.segmentation.apsrg_baseline import (
    APSRGBaseline,
    APSRGParams,
    apsrg_segment,
)
from src.segmentation.context_features import (
    ContextFeatureConfig,
    extract_context_features,
)
from src.utils.image_io import (
    ensure_binary_mask,
    read_binary_mask,
    read_gray_image,
    save_binary_mask,
)
from src.segmentation.apsrg_process_context import (
    APSRGProcessContextConfig,
    extract_apsrg_process_context,
)


@dataclass(frozen=True)
class CAAPSRGConfig:
    """Configuration for CA-APSRG segmentation."""

    enabled: bool = True
    always_refine: bool = True

    low_density_threshold: float = 0.025
    high_density_threshold: float = 0.120

    target_preserve_thin_vessels: bool = True

    process_context: APSRGProcessContextConfig = field(
        default_factory=APSRGProcessContextConfig
    )

    @classmethod
    def from_dict(
        cls,
        config: dict[str, Any] | None,
    ) -> "CAAPSRGConfig":
        """Create CAAPSRGConfig from config['ca_apsrg']."""
        if not config:
            return cls()

        process_context_config = (
            config.get("process_context")
            or config.get("apsrg_process_context")
            or {}
        )

        return cls(
            enabled=bool(config.get("enabled", True)),
            always_refine=bool(
                config.get("always_refine", True)
            ),
            low_density_threshold=float(
                config.get("low_density_threshold", 0.025)
            ),
            high_density_threshold=float(
                config.get("high_density_threshold", 0.120)
            ),
            target_preserve_thin_vessels=bool(
                config.get(
                    "target_preserve_thin_vessels",
                    True,
                )
            ),
            process_context=(
                APSRGProcessContextConfig.from_dict(
                    process_context_config
                )
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return config as a dictionary."""
        return asdict(self)


@dataclass
class CAAPSRGResult:
    """Container for CA-APSRG segmentation outputs."""

    baseline_mask: np.ndarray
    refined_mask: np.ndarray
    context_features: dict[str, Any]
    refined_context_features: dict[str, Any]
    apsrg_debug: dict[str, Any]
    refinement_debug: dict[str, Any]
    config: dict[str, Any]

    @property
    def ca_mask(self) -> np.ndarray:
        """Alias for refined_mask."""
        return self.refined_mask

    def to_debug_dict(self) -> dict[str, Any]:
        """Return debug information without duplicating large masks unnecessarily."""
        return {
            "context_features": self.context_features,
            "refined_context_features": self.refined_context_features,
            "apsrg_debug": self.apsrg_debug,
            "refinement_debug": self.refinement_debug,
            "config": self.config,
            "n_baseline_pixels": int(np.asarray(self.baseline_mask).sum()),
            "n_refined_pixels": int(np.asarray(self.refined_mask).sum()),
        }


CAAPSRGParams = CAAPSRGConfig


def _prepare_fov_mask(fov_mask: Optional[np.ndarray], reference_shape: tuple[int, int]) -> Optional[np.ndarray]:
    """Prepare optional FoV mask as boolean array."""
    if fov_mask is None:
        return None

    fov = ensure_binary_mask(fov_mask, return_uint8=False)
    if fov.shape != reference_shape:
        raise ValueError(f"FoV mask shape {fov.shape} does not match image shape {reference_shape}")
    return fov.astype(bool)

def combine_refinement_levels(
    mask_level: str,
    process_level: str,
    *,
    allow_process_override: bool,
) -> str:
    """
    Combine mask-based and APSRG-process refinement recommendations.

    When process override is disabled, the original mask-based level is used.

    When enabled:
    - identical levels are preserved;
    - a normal level accepts the non-normal recommendation;
    - conflicting conservative/aggressive recommendations become normal.
    """
    valid_levels = {
        "conservative",
        "normal",
        "aggressive",
    }

    mask_value = str(mask_level).lower()
    process_value = str(process_level).lower()

    if mask_value not in valid_levels:
        mask_value = "normal"

    if process_value not in valid_levels:
        process_value = "normal"

    if not allow_process_override:
        return mask_value

    if mask_value == process_value:
        return mask_value

    if process_value == "normal":
        return mask_value

    if mask_value == "normal":
        return process_value

    # Conservative and aggressive conflict.
    return "normal"

def should_apply_refinement(
    ca_config: CAAPSRGConfig,
    context_features: dict[str, Any],
    process_context: dict[str, Any] | None = None,
) -> bool:
    """Decide whether adaptive refinement should be applied."""
    if not ca_config.enabled:
        return False

    if ca_config.always_refine:
        return True

    density_level = str(
        context_features.get(
            "density_level",
            "normal",
        )
    ).lower()

    noise_level = str(
        context_features.get(
            "noise_level",
            "normal",
        )
    ).lower()

    refinement_level = str(
        context_features.get(
            "recommended_refinement_level",
            "normal",
        )
    ).lower()

    mask_rule = (
        noise_level in {"medium", "high"}
        or density_level == "high"
        or refinement_level
        in {"aggressive", "conservative"}
    )

    process_rule = False

    if (
        process_context
        and ca_config.process_context.enabled
        and ca_config.process_context.can_trigger_refinement
    ):
        process_risk = str(
            process_context.get(
                "process_risk_level",
                "low",
            )
        ).lower()

        process_level = str(
            process_context.get(
                "recommended_refinement_level",
                "normal",
            )
        ).lower()

        process_rule = (
            process_risk in {"medium", "high"}
            or process_level
            in {"conservative", "aggressive"}
        )

    return bool(mask_rule or process_rule)


def ca_apsrg_refine(
    baseline_mask: np.ndarray,
    fov_mask: np.ndarray | None = None,
    params: AdaptiveMorphologyConfig | None = None,
    *,
    ca_config: CAAPSRGConfig | None = None,
    context_config: ContextFeatureConfig | None = None,
    apsrg_debug: dict[str, Any] | None = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    """
    Refine an APSRG baseline mask using mask context and optional
    APSRG process context.
    """
    ca_cfg = ca_config or CAAPSRGConfig()

    baseline = ensure_binary_mask(
        baseline_mask,
        return_uint8=False,
    )

    fov = _prepare_fov_mask(
        fov_mask,
        baseline.shape,
    )

    if fov is not None:
        baseline = baseline & fov

    baseline_features = extract_context_features(
        baseline,
        fov_mask=fov,
        config=context_config,
        low_density_threshold=ca_cfg.low_density_threshold,
        high_density_threshold=ca_cfg.high_density_threshold,
    )

    if (
        ca_cfg.process_context.enabled
        and apsrg_debug is not None
    ):
        process_features = extract_apsrg_process_context(
            apsrg_debug,
            fov_mask=fov,
            config=ca_cfg.process_context,
        )
        process_context_dict = process_features.to_dict()
    else:
        process_context_dict = {}

    mask_refinement_level = str(
        baseline_features.recommended_refinement_level
    )

    process_refinement_level = str(
        process_context_dict.get(
            "recommended_refinement_level",
            "normal",
        )
    )

    combined_refinement_level = combine_refinement_levels(
        mask_refinement_level,
        process_refinement_level,
        allow_process_override=(
            ca_cfg.process_context.can_override_refinement_level
        ),
    )

    effective_features = baseline_features

    if (
        ca_cfg.process_context.enabled
        and ca_cfg.process_context.can_override_refinement_level
        and combined_refinement_level
        != baseline_features.recommended_refinement_level
    ):
        effective_features = replace(
            baseline_features,
            recommended_refinement_level=(
                combined_refinement_level
            ),
        )

    if not should_apply_refinement(
        ca_cfg,
        baseline_features.to_dict(),
        process_context=process_context_dict,
    ):
        debug = {
            "enabled": False,
            "reason": (
                "CA-APSRG refinement disabled or not "
                "required by context rule"
            ),
            "context_features": baseline_features.to_dict(),
            "apsrg_process_context": process_context_dict,
            "mask_refinement_level": mask_refinement_level,
            "process_refinement_level": (
                process_refinement_level
            ),
            "combined_refinement_level": (
                combined_refinement_level
            ),
            "refined_context_features": (
                baseline_features.to_dict()
            ),
            "ca_apsrg_config": ca_cfg.to_dict(),
        }

        return baseline.astype(bool), debug

    refined, refinement_debug = (
        adaptive_morphological_refinement(
            baseline,
            fov_mask=fov,
            params=params,
            context_config=context_config,
            precomputed_features=effective_features,
        )
    )

    refined_features = extract_context_features(
        refined,
        fov_mask=fov,
        config=context_config,
        low_density_threshold=ca_cfg.low_density_threshold,
        high_density_threshold=ca_cfg.high_density_threshold,
    )

    debug = {
        "enabled": True,
        "context_features": baseline_features.to_dict(),
        "effective_context_features": (
            effective_features.to_dict()
        ),
        "apsrg_process_context": process_context_dict,
        "mask_refinement_level": mask_refinement_level,
        "process_refinement_level": (
            process_refinement_level
        ),
        "combined_refinement_level": (
            combined_refinement_level
        ),
        "refined_context_features": (
            refined_features.to_dict()
        ),
        "refinement_debug": refinement_debug,
        "ca_apsrg_config": ca_cfg.to_dict(),
        "n_baseline_pixels": int(baseline.sum()),
        "n_refined_pixels": int(refined.sum()),
        "n_pixels_removed": int(
            max(
                int(baseline.sum())
                - int(refined.sum()),
                0,
            )
        ),
        "n_pixels_added": int(
            max(
                int(refined.sum())
                - int(baseline.sum()),
                0,
            )
        ),
    }

    return refined.astype(bool), debug


def ca_apsrg_segment(
    preprocessed_gray: np.ndarray,
    fov_mask: np.ndarray | None = None,
    *,
    apsrg_params: APSRGParams | None = None,
    adaptive_params: AdaptiveMorphologyConfig | None = None,
    ca_config: CAAPSRGConfig | None = None,
    context_config: ContextFeatureConfig | None = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    """
    Run the complete CA-APSRG method on one preprocessed image.

    Returns
    -------
    refined_mask:
        Boolean CA-APSRG vessel mask.
    debug_info:
        Dictionary containing APSRG baseline output, context features,
        adaptive morphology details, and parameter values.
    """
    ca_cfg = ca_config or CAAPSRGConfig()

    baseline_mask, apsrg_debug = apsrg_segment(
        preprocessed_gray,
        fov_mask=fov_mask,
        params=apsrg_params,
    )

    refined_mask, refine_debug = ca_apsrg_refine(
        baseline_mask,
        fov_mask=fov_mask,
        params=adaptive_params,
        ca_config=ca_cfg,
        context_config=context_config,
        apsrg_debug=apsrg_debug,
    )

    debug_info: dict[str, Any] = {
        "baseline_mask": baseline_mask,
        "refined_mask": refined_mask,
        "apsrg_debug": apsrg_debug,
        "refinement_debug": refine_debug,
        "context_features": refine_debug.get("context_features", {}),
        "refined_context_features": refine_debug.get("refined_context_features", {}),
        "ca_apsrg_config": ca_cfg.to_dict(),
        "apsrg_params": apsrg_params.to_dict() if apsrg_params else APSRGParams().to_dict(),
        "adaptive_params": adaptive_params.to_dict() if adaptive_params else AdaptiveMorphologyConfig().to_dict(),
        "context_config": context_config.to_dict() if context_config else ContextFeatureConfig().to_dict(),
        "apsrg_process_context": refine_debug.get(
            "apsrg_process_context",
            {},
        ),
        "combined_refinement_level": refine_debug.get(
            "combined_refinement_level",
            "normal",
        ),
    }

    return refined_mask.astype(bool), debug_info


segment_ca_apsrg = ca_apsrg_segment
run_ca_apsrg = ca_apsrg_segment


class CAAPSRGSegmenter:
    """Class wrapper for the complete CA-APSRG segmentation method."""

    def __init__(
        self,
        apsrg_params: APSRGParams | None = None,
        adaptive_params: AdaptiveMorphologyConfig | None = None,
        ca_config: CAAPSRGConfig | None = None,
        context_config: ContextFeatureConfig | None = None,
    ):
        self.apsrg_params = apsrg_params or APSRGParams()
        self.adaptive_params = adaptive_params or AdaptiveMorphologyConfig()
        self.ca_config = ca_config or CAAPSRGConfig()
        self.context_config = context_config or ContextFeatureConfig()
        self.apsrg_baseline = APSRGBaseline(self.apsrg_params)

    @classmethod
    def from_dict(cls, config: dict[str, Any] | None) -> "CAAPSRGSegmenter":
        """Create CAAPSRGSegmenter from a full YAML-like configuration dictionary."""
        config = config or {}
        return cls(
            apsrg_params=APSRGParams.from_dict(config.get("apsrg_baseline", {})),
            adaptive_params=AdaptiveMorphologyConfig.from_dict(
                config.get("adaptive_morphology", {}),
                ca_apsrg_config=config.get("ca_apsrg", {}),
            ),
            ca_config=CAAPSRGConfig.from_dict(config.get("ca_apsrg", {})),
            context_config=ContextFeatureConfig.from_dict(config.get("context_features", {})),
        )

    def segment(
        self,
        preprocessed_gray: np.ndarray,
        fov_mask: Optional[np.ndarray] = None,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        """Run CA-APSRG on one preprocessed image."""
        return ca_apsrg_segment(
            preprocessed_gray,
            fov_mask=fov_mask,
            apsrg_params=self.apsrg_params,
            adaptive_params=self.adaptive_params,
            ca_config=self.ca_config,
            context_config=self.context_config,
        )

    def refine(
        self,
        baseline_mask: np.ndarray,
        fov_mask: Optional[np.ndarray] = None,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        """Refine an existing APSRG baseline mask."""
        return ca_apsrg_refine(
            baseline_mask,
            fov_mask=fov_mask,
            params=self.adaptive_params,
            ca_config=self.ca_config,
            context_config=self.context_config,
        )


CAAPSRG = CAAPSRGSegmenter


def run_ca_apsrg_on_files(
    preprocessed_path: str | Path,
    output_mask_path: str | Path,
    fov_path: str | Path | None = None,
    *,
    apsrg_params: APSRGParams | None = None,
    adaptive_params: AdaptiveMorphologyConfig | None = None,
    ca_config: CAAPSRGConfig | None = None,
    context_config: ContextFeatureConfig | None = None,
    save_baseline_path: str | Path | None = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    """
    Read a preprocessed image from disk, run CA-APSRG, save result, and return it.

    Parameters
    ----------
    preprocessed_path:
        Path to preprocessed grayscale image.
    output_mask_path:
        Destination path for the CA-APSRG refined mask.
    fov_path:
        Optional FoV mask path.
    save_baseline_path:
        Optional destination path for the APSRG baseline mask.
    """
    gray = read_gray_image(preprocessed_path)
    fov = read_binary_mask(fov_path) if fov_path else None

    refined, debug = ca_apsrg_segment(
        gray,
        fov_mask=fov,
        apsrg_params=apsrg_params,
        adaptive_params=adaptive_params,
        ca_config=ca_config,
        context_config=context_config,
    )

    save_binary_mask(output_mask_path, refined)

    if save_baseline_path is not None and "baseline_mask" in debug:
        save_binary_mask(save_baseline_path, debug["baseline_mask"])

    return refined, debug
