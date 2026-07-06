"""
Experiment pipeline for CA-APSRG retinal vessel segmentation.

This module connects the complete research workflow:

1. Read fundus image, ground-truth vessel mask, and optional FoV mask.
2. Preprocess the fundus image.
3. Run APSRG baseline segmentation.
4. Refine APSRG output using CA-APSRG adaptive morphology.
5. Evaluate APSRG baseline and CA-APSRG against the manual annotation.
6. Save masks, overlays, debug information, and CSV-ready metric rows.

The module is designed to be called by:
- scripts/02_run_single_image.py
- scripts/03_run_batch.py

Conventions:
- RGB fundus images are read in RGB order.
- Masks are represented internally as boolean arrays.
- Saved masks are 0/255 PNG files.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd
import yaml
from tqdm import tqdm

from src.evaluation.metrics import (
    SegmentationMetrics,
    evaluate_segmentation,
    metrics_to_dict,
)
from src.preprocessing.preprocess import PreprocessConfig, preprocess_fundus
from src.segmentation.adaptive_morphology import AdaptiveMorphologyConfig
from src.segmentation.apsrg_baseline import APSRGParams, apsrg_segment
from src.segmentation.ca_apsrg import CAAPSRGConfig, ca_apsrg_refine
from src.segmentation.context_features import ContextFeatureConfig
from src.utils.image_io import (
    create_side_by_side,
    ensure_binary_mask,
    ensure_dir,
    overlay_mask_on_image,
    read_binary_mask,
    read_rgb_image,
    save_binary_mask,
    save_png_uint8,
)


@dataclass(frozen=True)
class PipelineOutputConfig:
    """Configuration for saving pipeline outputs."""

    save_preprocessed: bool = True
    save_apsrg_mask: bool = True
    save_ca_apsrg_mask: bool = True
    save_overlay: bool = True
    save_side_by_side: bool = True
    save_debug_json: bool = True
    overlay_alpha: float = 0.45

    @classmethod
    def from_dict(cls, config: dict[str, Any] | None) -> "PipelineOutputConfig":
        """Create PipelineOutputConfig from config['outputs'] and config['visualization']."""
        config = config or {}
        visualization = config.get("visualization", {}) if isinstance(config.get("visualization", {}), dict) else {}

        return cls(
            save_preprocessed=bool(config.get("save_preprocessed", True)),
            save_apsrg_mask=bool(config.get("save_apsrg_mask", True)),
            save_ca_apsrg_mask=bool(config.get("save_ca_apsrg_mask", True)),
            save_overlay=bool(config.get("save_overlay", True)),
            save_side_by_side=bool(config.get("save_side_by_side", visualization.get("save_side_by_side", True))),
            save_debug_json=bool(config.get("save_debug_json", True)),
            overlay_alpha=float(config.get("overlay_alpha", 0.45)),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return config as a dictionary."""
        return asdict(self)


@dataclass(frozen=True)
class EvaluationConfig:
    """Evaluation configuration."""

    binary_threshold: int = 127
    evaluate_inside_fov_only: bool = True
    resize_prediction_to_gt: bool = True
    resize_fov_to_gt: bool = True

    @classmethod
    def from_dict(cls, config: dict[str, Any] | None) -> "EvaluationConfig":
        """Create EvaluationConfig from config['evaluation']."""
        config = config or {}
        return cls(
            binary_threshold=int(config.get("binary_threshold", 127)),
            evaluate_inside_fov_only=bool(config.get("evaluate_inside_fov_only", True)),
            resize_prediction_to_gt=bool(config.get("resize_prediction_to_gt", True)),
            resize_fov_to_gt=bool(config.get("resize_fov_to_gt", True)),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return config as a dictionary."""
        return asdict(self)


@dataclass(frozen=True)
class PipelineConfig:
    """Complete pipeline configuration for one experiment run."""

    preprocessing: PreprocessConfig
    apsrg: APSRGParams
    adaptive_morphology: AdaptiveMorphologyConfig
    ca_apsrg: CAAPSRGConfig
    context_features: ContextFeatureConfig
    evaluation: EvaluationConfig
    outputs: PipelineOutputConfig
    always_refine: bool = True
    precision_threshold: float = 0.95

    @classmethod
    def default(cls) -> "PipelineConfig":
        """Return default pipeline configuration."""
        return cls(
            preprocessing=PreprocessConfig(),
            apsrg=APSRGParams(),
            adaptive_morphology=AdaptiveMorphologyConfig(),
            ca_apsrg=CAAPSRGConfig(),
            context_features=ContextFeatureConfig(),
            evaluation=EvaluationConfig(),
            outputs=PipelineOutputConfig(),
            always_refine=True,
            precision_threshold=0.95,
        )

    @classmethod
    def from_dict(cls, config: dict[str, Any] | None) -> "PipelineConfig":
        """Create PipelineConfig from full YAML-like dictionary."""
        config = config or {}
        experiment_cfg = config.get("experiment", {}) if isinstance(config.get("experiment", {}), dict) else {}

        ca_cfg = dict(config.get("ca_apsrg", {}) or {})
        if "always_refine" not in ca_cfg and "always_refine" in experiment_cfg:
            ca_cfg["always_refine"] = experiment_cfg.get("always_refine")

        return cls(
            preprocessing=PreprocessConfig.from_dict(config.get("preprocessing", {})),
            apsrg=APSRGParams.from_dict(config.get("apsrg_baseline", {})),
            adaptive_morphology=AdaptiveMorphologyConfig.from_dict(
                config.get("adaptive_morphology", {}),
                ca_apsrg_config=config.get("ca_apsrg", {}),
            ),
            ca_apsrg=CAAPSRGConfig.from_dict(ca_cfg),
            context_features=ContextFeatureConfig.from_dict(config.get("context_features", {})),
            evaluation=EvaluationConfig.from_dict(config.get("evaluation", {})),
            outputs=PipelineOutputConfig.from_dict(
                {
                    **(config.get("outputs", {}) or {}),
                    "visualization": config.get("visualization", {}) or {},
                }
            ),
            always_refine=bool(experiment_cfg.get("always_refine", ca_cfg.get("always_refine", True))),
            precision_threshold=float(experiment_cfg.get("false_positive_precision_threshold", 0.95)),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return config as a serializable dictionary."""
        return {
            "preprocessing": self.preprocessing.to_dict(),
            "apsrg_baseline": self.apsrg.to_dict(),
            "adaptive_morphology": self.adaptive_morphology.to_dict(),
            "ca_apsrg": self.ca_apsrg.to_dict(),
            "context_features": self.context_features.to_dict(),
            "evaluation": self.evaluation.to_dict(),
            "outputs": self.outputs.to_dict(),
            "always_refine": self.always_refine,
            "precision_threshold": self.precision_threshold,
        }


@dataclass
class SingleImageResult:
    """Result container for one processed image."""

    row: dict[str, Any]
    baseline_mask: np.ndarray
    ca_apsrg_mask: np.ndarray
    preprocessed: np.ndarray
    debug: dict[str, Any]


def load_yaml_config(config_path: str | Path) -> dict[str, Any]:
    """Load a YAML config file."""
    config_path = Path(config_path)
    if not config_path.is_file():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    return data or {}


def load_pipeline_config(config_path: str | Path | None = None, config: dict[str, Any] | None = None) -> PipelineConfig:
    """Load PipelineConfig from a YAML file, a dictionary, or defaults."""
    if config is not None:
        return PipelineConfig.from_dict(config)
    if config_path is not None:
        return PipelineConfig.from_dict(load_yaml_config(config_path))
    return PipelineConfig.default()


def _is_missing_path(value: Any) -> bool:
    """Return True if a path-like value is empty, None, or NaN."""
    if value is None:
        return True
    if isinstance(value, float) and np.isnan(value):
        return True
    text = str(value).strip()
    return text == "" or text.lower() in {"nan", "none", "null"}


def _optional_path(value: Any) -> Optional[Path]:
    """Convert value to Path or None."""
    if _is_missing_path(value):
        return None
    return Path(str(value))


def _safe_stem(value: str) -> str:
    """Create a safe file/folder stem from dataset or image id."""
    text = str(value).strip() or "unknown"
    for ch in ["/", "\\", ":", "*", "?", '"', "<", ">", "|", " "]:
        text = text.replace(ch, "_")
    return text


def _make_json_safe(value: Any) -> Any:
    """Convert nested objects into JSON-safe values."""
    if isinstance(value, np.ndarray):
        return {
            "type": "ndarray",
            "shape": list(value.shape),
            "dtype": str(value.dtype),
            "min": float(np.min(value)) if value.size else None,
            "max": float(np.max(value)) if value.size else None,
            "sum": float(np.sum(value)) if value.size else 0.0,
        }
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _make_json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_make_json_safe(v) for v in value]
    return value


def _write_json(path: str | Path, payload: dict[str, Any]) -> Path:
    """Write a JSON file with numpy-safe conversion."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(_make_json_safe(payload), file, indent=2, ensure_ascii=False)
    return path


def _evaluate_optional(
    pred_mask: np.ndarray,
    gt_mask: Optional[np.ndarray],
    fov_mask: Optional[np.ndarray],
    *,
    evaluation_config: EvaluationConfig,
) -> Optional[SegmentationMetrics]:
    """Evaluate prediction only when ground truth is available."""
    if gt_mask is None:
        return None

    active_fov = fov_mask if evaluation_config.evaluate_inside_fov_only else None
    return evaluate_segmentation(
        pred_mask,
        gt_mask,
        active_fov,
        threshold=evaluation_config.binary_threshold,
        resize_prediction_to_gt=evaluation_config.resize_prediction_to_gt,
        resize_fov_to_gt=evaluation_config.resize_fov_to_gt,
    )


def should_apply_ca_apsrg(
    baseline_precision: Optional[float],
    *,
    always_refine: bool = True,
    precision_threshold: float = 0.95,
) -> bool:
    """
    Decide whether CA-APSRG refinement should be applied.

    For the proposed method, always_refine=True is recommended. The conditional
    mode is kept for ablation experiments.
    """
    if always_refine:
        return True
    if baseline_precision is None:
        return True
    return float(baseline_precision) < float(precision_threshold)


def _save_visual_outputs(
    *,
    image_rgb: np.ndarray,
    preprocessed: np.ndarray,
    gt_mask: Optional[np.ndarray],
    baseline_mask: np.ndarray,
    ca_mask: np.ndarray,
    output_dir: Path,
    dataset: str,
    image_id: str,
    config: PipelineOutputConfig,
) -> dict[str, str]:
    """Save images, masks, overlays, and side-by-side visualization."""
    dataset_dir = output_dir / _safe_stem(dataset or "dataset")
    image_stem = _safe_stem(image_id)
    saved: dict[str, str] = {}

    if config.save_preprocessed:
        path = dataset_dir / "preprocessed" / f"{image_stem}_preprocessed.png"
        save_png_uint8(path, preprocessed)
        saved["preprocessed_path"] = str(path)

    if config.save_apsrg_mask:
        path = dataset_dir / "baseline_masks" / f"{image_stem}_apsrg_baseline.png"
        save_binary_mask(path, baseline_mask)
        saved["baseline_mask_path"] = str(path)

    if config.save_ca_apsrg_mask:
        path = dataset_dir / "ca_apsrg_masks" / f"{image_stem}_ca_apsrg.png"
        save_binary_mask(path, ca_mask)
        saved["ca_apsrg_mask_path"] = str(path)

    baseline_overlay = None
    ca_overlay = None

    if config.save_overlay:
        baseline_overlay = overlay_mask_on_image(
            image_rgb,
            baseline_mask,
            alpha=config.overlay_alpha,
            mask_color=(255, 0, 0),
        )
        ca_overlay = overlay_mask_on_image(
            image_rgb,
            ca_mask,
            alpha=config.overlay_alpha,
            mask_color=(0, 255, 0),
        )

        baseline_path = dataset_dir / "overlays" / f"{image_stem}_baseline_overlay.png"
        ca_path = dataset_dir / "overlays" / f"{image_stem}_ca_apsrg_overlay.png"
        save_png_uint8(baseline_path, baseline_overlay)
        save_png_uint8(ca_path, ca_overlay)
        saved["baseline_overlay_path"] = str(baseline_path)
        saved["ca_apsrg_overlay_path"] = str(ca_path)

    if config.save_side_by_side:
        gt_vis = ensure_binary_mask(gt_mask, return_uint8=True) if gt_mask is not None else np.zeros_like(preprocessed)
        baseline_vis = ensure_binary_mask(baseline_mask, return_uint8=True)
        ca_vis = ensure_binary_mask(ca_mask, return_uint8=True)

        images = [
            image_rgb,
            preprocessed,
            gt_vis,
            baseline_vis,
            ca_vis,
        ]

        if baseline_overlay is not None and ca_overlay is not None:
            images.extend([baseline_overlay, ca_overlay])

        side_by_side = create_side_by_side(images)
        side_path = dataset_dir / "comparison" / f"{image_stem}_comparison.png"
        save_png_uint8(side_path, side_by_side)
        saved["comparison_path"] = str(side_path)

    return saved


def _prefix_metrics(prefix: str, metrics: Optional[SegmentationMetrics]) -> dict[str, Any]:
    """Return metrics dictionary with prefixed column names."""
    if metrics is None:
        return {}
    return {f"{prefix}_{key}": value for key, value in metrics_to_dict(metrics).items()}


def _extract_selected_parameters(ca_debug: dict[str, Any]) -> dict[str, Any]:
    """Extract selected adaptive morphology parameters from nested debug payload."""
    if "selected_parameters" in ca_debug:
        return ca_debug.get("selected_parameters", {}) or {}

    refinement_debug = ca_debug.get("refinement_debug", {})
    if isinstance(refinement_debug, dict):
        return refinement_debug.get("selected_parameters", {}) or {}

    return {}


def run_single_image(
    image_path: str | Path,
    output_dir: str | Path,
    *,
    mask_path: str | Path | None = None,
    fov_path: str | Path | None = None,
    image_id: str | None = None,
    dataset: str = "",
    config_path: str | Path | None = None,
    config: dict[str, Any] | PipelineConfig | None = None,
    always_refine: bool | None = None,
    precision_threshold: float | None = None,
    return_arrays: bool = False,
) -> dict[str, Any] | SingleImageResult:
    """
    Run the complete pipeline for one fundus image.

    Parameters are intentionally compatible with the earlier skeleton version.
    When return_arrays=False, only a CSV-ready row dictionary is returned.
    """
    image_path = Path(image_path)
    mask_path_obj = _optional_path(mask_path)
    fov_path_obj = _optional_path(fov_path)
    output_dir = ensure_dir(output_dir)

    if isinstance(config, PipelineConfig):
        pipe_cfg = config
    else:
        pipe_cfg = load_pipeline_config(config_path=config_path, config=config)

    if always_refine is not None:
        pipe_cfg = PipelineConfig(
            preprocessing=pipe_cfg.preprocessing,
            apsrg=pipe_cfg.apsrg,
            adaptive_morphology=pipe_cfg.adaptive_morphology,
            ca_apsrg=CAAPSRGConfig(
                enabled=pipe_cfg.ca_apsrg.enabled,
                always_refine=bool(always_refine),
                low_density_threshold=pipe_cfg.ca_apsrg.low_density_threshold,
                high_density_threshold=pipe_cfg.ca_apsrg.high_density_threshold,
                target_preserve_thin_vessels=pipe_cfg.ca_apsrg.target_preserve_thin_vessels,
            ),
            context_features=pipe_cfg.context_features,
            evaluation=pipe_cfg.evaluation,
            outputs=pipe_cfg.outputs,
            always_refine=bool(always_refine),
            precision_threshold=pipe_cfg.precision_threshold,
        )

    if precision_threshold is not None:
        pipe_cfg = PipelineConfig(
            preprocessing=pipe_cfg.preprocessing,
            apsrg=pipe_cfg.apsrg,
            adaptive_morphology=pipe_cfg.adaptive_morphology,
            ca_apsrg=pipe_cfg.ca_apsrg,
            context_features=pipe_cfg.context_features,
            evaluation=pipe_cfg.evaluation,
            outputs=pipe_cfg.outputs,
            always_refine=pipe_cfg.always_refine,
            precision_threshold=float(precision_threshold),
        )

    if not image_path.is_file():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    if mask_path_obj is not None and not mask_path_obj.is_file():
        raise FileNotFoundError(f"Mask file not found: {mask_path_obj}")
    if fov_path_obj is not None and not fov_path_obj.is_file():
        raise FileNotFoundError(f"FoV file not found: {fov_path_obj}")

    image_id = image_id or image_path.stem
    dataset = dataset or "dataset"

    image_rgb = read_rgb_image(image_path)
    gt_mask = read_binary_mask(mask_path_obj, threshold=pipe_cfg.evaluation.binary_threshold) if mask_path_obj else None
    fov_mask = read_binary_mask(fov_path_obj, threshold=pipe_cfg.evaluation.binary_threshold) if fov_path_obj else None

    preprocessed = preprocess_fundus(image_rgb, fov_mask=fov_mask, config=pipe_cfg.preprocessing)

    baseline_mask, apsrg_debug = apsrg_segment(
        preprocessed,
        fov_mask=fov_mask,
        params=pipe_cfg.apsrg,
    )

    baseline_metrics = _evaluate_optional(
        baseline_mask,
        gt_mask,
        fov_mask,
        evaluation_config=pipe_cfg.evaluation,
    )
    baseline_precision = baseline_metrics.precision if baseline_metrics is not None else None

    use_refinement = should_apply_ca_apsrg(
        baseline_precision,
        always_refine=pipe_cfg.always_refine,
        precision_threshold=pipe_cfg.precision_threshold,
    )

    if use_refinement:
        ca_mask, ca_debug = ca_apsrg_refine(
            baseline_mask,
            fov_mask=fov_mask,
            params=pipe_cfg.adaptive_morphology,
            ca_config=pipe_cfg.ca_apsrg,
            context_config=pipe_cfg.context_features,
        )
    else:
        ca_mask = baseline_mask.copy()
        ca_debug = {
            "enabled": False,
            "reason": "Refinement skipped by precision threshold rule",
            "baseline_precision": baseline_precision,
            "precision_threshold": pipe_cfg.precision_threshold,
        }

    ca_metrics = _evaluate_optional(
        ca_mask,
        gt_mask,
        fov_mask,
        evaluation_config=pipe_cfg.evaluation,
    )

    saved_paths = _save_visual_outputs(
        image_rgb=image_rgb,
        preprocessed=preprocessed,
        gt_mask=gt_mask,
        baseline_mask=baseline_mask,
        ca_mask=ca_mask,
        output_dir=output_dir,
        dataset=dataset,
        image_id=image_id,
        config=pipe_cfg.outputs,
    )

    debug_payload = {
        "dataset": dataset,
        "image_id": image_id,
        "image_path": str(image_path),
        "mask_path": str(mask_path_obj) if mask_path_obj else "",
        "fov_path": str(fov_path_obj) if fov_path_obj else "",
        "pipeline_config": pipe_cfg.to_dict(),
        "apsrg_debug": apsrg_debug,
        "ca_apsrg_debug": ca_debug,
        "saved_paths": saved_paths,
    }

    if pipe_cfg.outputs.save_debug_json:
        debug_path = output_dir / _safe_stem(dataset) / "debug" / f"{_safe_stem(image_id)}_debug.json"
        _write_json(debug_path, debug_payload)
        saved_paths["debug_json_path"] = str(debug_path)

    row: dict[str, Any] = {
        "dataset": dataset,
        "image_id": image_id,
        "image_path": str(image_path),
        "mask_path": str(mask_path_obj) if mask_path_obj else "",
        "fov_path": str(fov_path_obj) if fov_path_obj else "",
        "ca_apsrg_applied": bool(use_refinement),
        "baseline_precision_for_decision": baseline_precision,
        "n_baseline_pixels": int(np.asarray(baseline_mask).sum()),
        "n_ca_apsrg_pixels": int(np.asarray(ca_mask).sum()),
    }
    row.update(saved_paths)
    row.update(_prefix_metrics("baseline", baseline_metrics))
    row.update(_prefix_metrics("ca_apsrg", ca_metrics))

    context_features = ca_debug.get("context_features", {}) if isinstance(ca_debug, dict) else {}
    refined_context_features = ca_debug.get("refined_context_features", {}) if isinstance(ca_debug, dict) else {}
    selected_parameters = _extract_selected_parameters(ca_debug) if isinstance(ca_debug, dict) else {}

    for key, value in context_features.items():
        if not isinstance(value, (dict, list, tuple, np.ndarray)):
            row[f"context_{key}"] = value

    for key, value in refined_context_features.items():
        if not isinstance(value, (dict, list, tuple, np.ndarray)):
            row[f"refined_context_{key}"] = value

    for key, value in selected_parameters.items():
        if not isinstance(value, (dict, list, tuple, np.ndarray)):
            row[f"selected_{key}"] = value

    if not return_arrays:
        return row

    return SingleImageResult(
        row=row,
        baseline_mask=baseline_mask,
        ca_apsrg_mask=ca_mask,
        preprocessed=preprocessed,
        debug=debug_payload,
    )


def _summary_by_dataset_and_method(results: pd.DataFrame) -> pd.DataFrame:
    """Build a compact summary table comparing APSRG baseline and CA-APSRG."""
    if results.empty:
        return pd.DataFrame()

    metric_names = [
        "accuracy",
        "precision",
        "recall",
        "specificity",
        "f1_score",
        "iou",
        "false_positive_rate",
        "false_negative_rate",
        "balanced_accuracy",
        "dice",
    ]

    long_rows: list[dict[str, Any]] = []
    for _, row in results.iterrows():
        for method_prefix, method_name in [("baseline", "APSRG"), ("ca_apsrg", "CA-APSRG")]:
            item = {
                "dataset": row.get("dataset", ""),
                "image_id": row.get("image_id", ""),
                "method": method_name,
            }
            has_metric = False
            for metric in metric_names:
                col = f"{method_prefix}_{metric}"
                if col in results.columns:
                    item[metric] = row.get(col)
                    has_metric = True
            if has_metric:
                long_rows.append(item)

    long_df = pd.DataFrame(long_rows)
    if long_df.empty:
        return pd.DataFrame()

    available_metrics = [metric for metric in metric_names if metric in long_df.columns]
    summary = long_df.groupby(["dataset", "method"], dropna=False)[available_metrics].agg(["mean", "std", "min", "max"])
    summary.columns = [f"{metric}_{stat}" for metric, stat in summary.columns]
    summary = summary.reset_index()
    count_df = long_df.groupby(["dataset", "method"], dropna=False).size().reset_index(name="n_images")
    return count_df.merge(summary, on=["dataset", "method"], how="left")


def run_batch(
    manifest_path: str | Path,
    output_dir: str | Path,
    *,
    config_path: str | Path | None = None,
    config: dict[str, Any] | PipelineConfig | None = None,
    always_refine: bool | None = None,
    precision_threshold: float | None = None,
    show_progress: bool = True,
) -> pd.DataFrame:
    """
    Run the complete pipeline for all rows in a manifest CSV.

    Returns a per-image DataFrame and saves:
    - metrics_per_image.csv
    - metrics_summary.csv
    """
    manifest_path = Path(manifest_path)
    output_dir = ensure_dir(output_dir)

    if not manifest_path.is_file():
        raise FileNotFoundError(f"Manifest file not found: {manifest_path}")

    if isinstance(config, PipelineConfig):
        pipe_cfg = config
    else:
        pipe_cfg = load_pipeline_config(config_path=config_path, config=config)

    df = pd.read_csv(manifest_path)
    if df.empty:
        raise ValueError(f"Manifest is empty: {manifest_path}")

    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    iterator = df.iterrows()
    if show_progress:
        iterator = tqdm(list(iterator), desc="Running CA-APSRG pipeline")

    for _, item in iterator:
        image_path = item.get("image_path", "")
        mask_path = item.get("mask_path", "")
        fov_path = item.get("fov_path", "")
        dataset = str(item.get("dataset", ""))
        image_id = str(item.get("image_id", ""))

        try:
            row = run_single_image(
                image_path=image_path,
                mask_path=None if _is_missing_path(mask_path) else mask_path,
                fov_path=None if _is_missing_path(fov_path) else fov_path,
                output_dir=output_dir,
                dataset=dataset,
                image_id=image_id,
                config=pipe_cfg,
                always_refine=always_refine,
                precision_threshold=precision_threshold,
                return_arrays=False,
            )
            rows.append(row)  # type: ignore[arg-type]
        except Exception as exc:
            errors.append(
                {
                    "dataset": dataset,
                    "image_id": image_id,
                    "image_path": image_path,
                    "mask_path": mask_path,
                    "fov_path": fov_path,
                    "error": str(exc),
                }
            )

    results = pd.DataFrame(rows)
    per_image_path = output_dir / "metrics_per_image.csv"
    results.to_csv(per_image_path, index=False)

    summary = _summary_by_dataset_and_method(results)
    summary_path = output_dir / "metrics_summary.csv"
    summary.to_csv(summary_path, index=False)

    if errors:
        error_df = pd.DataFrame(errors)
        error_df.to_csv(output_dir / "pipeline_errors.csv", index=False)

    return results


run_experiment = run_batch