"""
Export CA-APSRG process-context diagnostics from saved debug JSON files.

Default input:
    outputs/recovery_ablation/experiments_r06_local_or_region_process_override

Outputs:
    process_context_per_image.csv
    process_context_summary.csv
    process_context_level_counts.csv

Run from project root:

    python scripts/08_export_process_context_diagnostics.py

Custom input/output:

    python scripts/08_export_process_context_diagnostics.py \
        --input-dir outputs/recovery_ablation/experiments_r06_local_or_region_process_override \
        --output-dir outputs/recovery_ablation/process_context_diagnostics
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "recovery_ablation"
    / "experiments_r06_local_or_region_process_override"
)
DEFAULT_OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "recovery_ablation"
    / "process_context_diagnostics"
)


def _nested_get(data: Any, path: Iterable[str], default: Any = None) -> Any:
    """Read a nested dictionary path safely."""
    current = data
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def _first_value(data: Any, paths: list[tuple[str, ...]], default: Any = None) -> Any:
    """Return the first available value among nested paths."""
    for path in paths:
        value = _nested_get(data, path, default=None)
        if value is not None:
            return value
    return default


def _scalar(value: Any, default: Any = None) -> Any:
    """Keep JSON-compatible scalar values only."""
    if value is None:
        return default
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, (str, int, float, bool)):
        return value
    return default


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _to_float(value: Any, default: float = np.nan) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def find_debug_files(input_dir: Path) -> list[Path]:
    """Find all saved per-image debug JSON files recursively."""
    if not input_dir.is_dir():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    files = sorted(input_dir.glob("**/debug/*_debug.json"))
    if not files:
        files = sorted(input_dir.glob("**/*_debug.json"))

    if not files:
        raise FileNotFoundError(
            f"No *_debug.json files found under: {input_dir}"
        )

    return files


def load_json(path: Path) -> dict[str, Any]:
    """Load one debug JSON file."""
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    if not isinstance(payload, dict):
        raise ValueError(f"Debug JSON must contain an object: {path}")

    return payload


def extract_record(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    """Extract one flat process-context diagnostic record."""
    apsrg_debug = payload.get("apsrg_debug", {}) or {}
    ca_debug = payload.get("ca_apsrg_debug", {}) or {}
    process = ca_debug.get("apsrg_process_context", {}) or {}
    refinement = ca_debug.get("refinement_debug", {}) or {}

    selected_parameters = _first_value(
        ca_debug,
        [
            ("refinement_debug", "selected_parameters"),
            ("selected_parameters",),
        ],
        default={},
    )
    if not isinstance(selected_parameters, dict):
        selected_parameters = {}

    seed_debug = apsrg_debug.get("seed_selection_debug", {}) or {}
    growing_debug = apsrg_debug.get("region_growing_debug", {}) or {}

    record: dict[str, Any] = {
        "dataset": str(payload.get("dataset", "")),
        "image_id": str(payload.get("image_id", path.stem.replace("_debug", ""))),
        "debug_json_path": str(path),
        "seed_selection_method": _scalar(
            process.get(
                "seed_selection_method",
                _nested_get(apsrg_debug, ("params", "seed_selection_method"), "unknown"),
            ),
            "unknown",
        ),
        "region_growing_mode": _scalar(
            process.get(
                "region_growing_mode",
                _nested_get(apsrg_debug, ("params", "region_growing_mode"), "unknown"),
            ),
            "unknown",
        ),
        "mask_refinement_level": _scalar(
            ca_debug.get("mask_refinement_level", "normal"),
            "normal",
        ),
        "process_refinement_level": _scalar(
            ca_debug.get("process_refinement_level", "normal"),
            "normal",
        ),
        "combined_refinement_level": _scalar(
            ca_debug.get("combined_refinement_level", "normal"),
            "normal",
        ),
        "process_risk_score": _to_int(process.get("process_risk_score", 0)),
        "process_risk_level": _scalar(
            process.get("process_risk_level", "low"),
            "low",
        ),
        "recommended_refinement_level": _scalar(
            process.get("recommended_refinement_level", "normal"),
            "normal",
        ),
        "selected_seed_point_count": _to_int(
            process.get(
                "selected_seed_point_count",
                seed_debug.get("n_selected_seed_points", 0),
            )
        ),
        "seed_pixel_count": _to_int(
            process.get(
                "seed_pixel_count",
                apsrg_debug.get("n_seed_pixels", 0),
            )
        ),
        "candidate_pixel_count": _to_int(
            process.get(
                "candidate_pixel_count",
                apsrg_debug.get("n_candidate_pixels", 0),
            )
        ),
        "output_pixel_count": _to_int(
            process.get(
                "output_pixel_count",
                apsrg_debug.get("n_output_pixels", 0),
            )
        ),
        "seed_density": _to_float(process.get("seed_density", np.nan)),
        "candidate_density": _to_float(process.get("candidate_density", np.nan)),
        "output_density": _to_float(process.get("output_density", np.nan)),
        "growth_ratio": _to_float(process.get("growth_ratio", np.nan)),
        "connected_edge_mean": _to_float(
            process.get("connected_edge_mean", np.nan)
        ),
        "connected_edge_density": _to_float(
            process.get("connected_edge_density", np.nan)
        ),
        "fuzzy_seed_pixel_count": _to_int(
            process.get(
                "fuzzy_seed_pixel_count",
                seed_debug.get("n_fuzzy_seed_pixels", 0),
            )
        ),
        "harris_candidate_count": _to_int(
            process.get(
                "harris_candidate_count",
                seed_debug.get("n_harris_candidates", 0),
            )
        ),
        "strict_hybrid_candidate_count": _to_int(
            process.get(
                "strict_hybrid_candidate_count",
                seed_debug.get("n_strict_hybrid_candidates", 0),
            )
        ),
        "initial_seed_component_count": _to_int(
            process.get(
                "initial_seed_component_count",
                growing_debug.get("n_initial_seed_components", 0),
            )
        ),
        "accepted_growth_pixel_count": _to_int(
            process.get(
                "accepted_growth_pixel_count",
                growing_debug.get("n_accepted_growth_pixels", 0),
            )
        ),
        "max_iterations_reached": bool(
            process.get(
                "max_iterations_reached",
                growing_debug.get("max_iterations_reached", False),
            )
        ),
        "n_baseline_pixels": _to_int(
            ca_debug.get(
                "n_baseline_pixels",
                apsrg_debug.get("n_output_pixels", 0),
            )
        ),
        "n_refined_pixels": _to_int(
            ca_debug.get("n_refined_pixels", 0)
        ),
        "n_pixels_removed": _to_int(
            ca_debug.get("n_pixels_removed", 0)
        ),
        "n_pixels_added": _to_int(
            ca_debug.get("n_pixels_added", 0)
        ),
        "selected_min_component_area": _to_int(
            selected_parameters.get("min_component_area", 0)
        ),
        "selected_hole_area": _to_int(
            selected_parameters.get("hole_area", 0)
        ),
        "selected_closing_kernel": _to_int(
            selected_parameters.get("closing_kernel", 0)
        ),
        "selected_opening_kernel": _to_int(
            selected_parameters.get("opening_kernel", 0)
        ),
        "refinement_enabled": bool(ca_debug.get("enabled", False)),
        "refinement_changed_mask": bool(
            _to_int(ca_debug.get("n_pixels_removed", 0)) > 0
            or _to_int(ca_debug.get("n_pixels_added", 0)) > 0
        ),
    }

    return record


def build_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """Create numeric summary by dataset and combined refinement level."""
    if frame.empty:
        return pd.DataFrame()

    numeric_columns = [
        "process_risk_score",
        "selected_seed_point_count",
        "seed_pixel_count",
        "candidate_pixel_count",
        "output_pixel_count",
        "seed_density",
        "candidate_density",
        "output_density",
        "growth_ratio",
        "connected_edge_mean",
        "connected_edge_density",
        "n_baseline_pixels",
        "n_refined_pixels",
        "n_pixels_removed",
        "n_pixels_added",
        "selected_min_component_area",
    ]
    existing = [column for column in numeric_columns if column in frame.columns]

    summary = (
        frame.groupby(
            ["dataset", "combined_refinement_level"],
            dropna=False,
        )[existing]
        .agg(["count", "mean", "std", "median", "min", "max"])
        .reset_index()
    )
    summary.columns = [
        "_".join(str(part) for part in column if str(part))
        if isinstance(column, tuple)
        else str(column)
        for column in summary.columns
    ]
    return summary


def build_level_counts(frame: pd.DataFrame) -> pd.DataFrame:
    """Count refinement and risk-level combinations per dataset."""
    if frame.empty:
        return pd.DataFrame()

    group_columns = [
        "dataset",
        "mask_refinement_level",
        "process_refinement_level",
        "combined_refinement_level",
        "process_risk_level",
        "refinement_changed_mask",
    ]

    return (
        frame.groupby(group_columns, dropna=False)
        .size()
        .reset_index(name="n_images")
        .sort_values(group_columns)
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export CA-APSRG process-context diagnostics.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input-dir",
        default=str(DEFAULT_INPUT_DIR.relative_to(PROJECT_ROOT)),
        help="Experiment output directory containing debug JSON files.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR.relative_to(PROJECT_ROOT)),
        help="Destination directory for diagnostic CSV files.",
    )
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()

    input_dir = Path(args.input_dir)
    if not input_dir.is_absolute():
        input_dir = PROJECT_ROOT / input_dir

    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = PROJECT_ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, Any]] = []
    for path in find_debug_files(input_dir):
        try:
            records.append(extract_record(path, load_json(path)))
        except (OSError, ValueError, json.JSONDecodeError) as error:
            print(f"Warning: skipped {path}: {error}")

    if not records:
        raise RuntimeError("No valid process-context debug records were extracted.")

    per_image = pd.DataFrame.from_records(records).sort_values(
        ["dataset", "image_id"],
        kind="stable",
    )
    summary = build_summary(per_image)
    level_counts = build_level_counts(per_image)

    outputs = {
        "process_context_per_image.csv": per_image,
        "process_context_summary.csv": summary,
        "process_context_level_counts.csv": level_counts,
    }

    for filename, frame in outputs.items():
        path = output_dir / filename
        frame.to_csv(path, index=False)
        print(path)


if __name__ == "__main__":
    main()