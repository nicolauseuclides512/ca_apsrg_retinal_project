"""
Script No. 14: Run CA-APSRG pipeline on a single fundus image.

Typical use after manifest has been created:

    python scripts/02_run_single_image.py --manifest data/manifests/manifest.csv --row-index 0

Run by dataset and image id:

    python scripts/02_run_single_image.py \
        --manifest data/manifests/manifest.csv \
        --dataset DRIVE \
        --image-id 21

Run with explicit file paths:

    python scripts/02_run_single_image.py \
        --image-path "data/working_png/DRIVE/DRIVE/training/images/21_training.png" \
        --mask-path "data/working_png/DRIVE/DRIVE/training/1st_manual/21_manual1.png" \
        --fov-path "data/working_png/DRIVE/DRIVE/training/mask/21_training_mask.png" \
        --dataset DRIVE \
        --image-id 21

Outputs are saved under outputs/single_test by default.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Optional

import pandas as pd
import yaml

# Make sure `src` can be imported when this script is run as:
# python scripts/02_run_single_image.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline.run_pipeline import run_single_image  # noqa: E402


def load_yaml_config(config_path: str | Path) -> dict[str, Any]:
    """Load YAML config file. Return empty dict when the file is missing."""
    config_path = Path(config_path)
    if not config_path.is_file():
        return {}

    with config_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    return data or {}


def get_nested(config: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Safely read nested values from a dictionary."""
    current: Any = config
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def resolve_project_path(path_value: str | Path | None, default: str | Path | None = None) -> Optional[Path]:
    """
    Resolve a project-relative path.

    Absolute paths are kept as-is. Empty values return None.
    """
    raw_value = path_value if path_value is not None else default
    if raw_value is None:
        return None

    text = str(raw_value).strip()
    if text == "" or text.lower() in {"nan", "none", "null"}:
        return None

    path = Path(text)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def is_missing(value: Any) -> bool:
    """Return True when a manifest path value is empty or NaN-like."""
    if value is None:
        return True
    if isinstance(value, float) and pd.isna(value):
        return True
    text = str(value).strip()
    return text == "" or text.lower() in {"nan", "none", "null"}


def choose_manifest_row(
    manifest_path: str | Path,
    *,
    row_index: int | None = None,
    dataset: str | None = None,
    image_id: str | None = None,
) -> pd.Series:
    """
    Select one row from manifest by row index or by dataset/image_id.

    Priority:
    1. row_index when provided,
    2. dataset + image_id,
    3. first row in manifest.
    """
    manifest_path = Path(manifest_path)
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Manifest file not found: {manifest_path}")

    df = pd.read_csv(manifest_path)
    if df.empty:
        raise ValueError(f"Manifest is empty: {manifest_path}")

    if row_index is not None:
        idx = int(row_index)
        if idx < 0 or idx >= len(df):
            raise IndexError(f"row_index {idx} is outside manifest range 0..{len(df) - 1}")
        return df.iloc[idx]

    if dataset and image_id:
        dataset_text = str(dataset).strip().lower()
        image_id_text = str(image_id).strip().lower()

        filtered = df[
            (df["dataset"].astype(str).str.lower() == dataset_text)
            & (df["image_id"].astype(str).str.lower() == image_id_text)
        ]

        if filtered.empty:
            available = df[["dataset", "image_id"]].head(20).to_string(index=False)
            raise ValueError(
                f"No manifest row found for dataset={dataset!r}, image_id={image_id!r}.\n"
                f"First available rows:\n{available}"
            )

        return filtered.iloc[0]

    return df.iloc[0]


def build_arg_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Run CA-APSRG on one retinal fundus image.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--config",
        default="configs/default.yaml",
        help="YAML configuration file path.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory. If omitted, it is read from config paths.single_test_dir or experiment.single_test_dir.",
    )

    # Option A: read one item from manifest.
    parser.add_argument(
        "--manifest",
        default=None,
        help="Manifest CSV path. If omitted, config data.manifest_path is used when explicit image path is not provided.",
    )
    parser.add_argument(
        "--row-index",
        type=int,
        default=None,
        help="Row index in manifest to process. Uses zero-based indexing.",
    )
    parser.add_argument(
        "--dataset",
        default=None,
        help="Dataset name to select from manifest or to store in output metadata.",
    )
    parser.add_argument(
        "--image-id",
        default=None,
        help="Image id to select from manifest or to store in output metadata.",
    )

    # Option B: explicit paths.
    parser.add_argument(
        "--image-path",
        default=None,
        help="Explicit fundus image path. When provided, manifest selection is skipped.",
    )
    parser.add_argument(
        "--mask-path",
        default=None,
        help="Explicit ground-truth vessel mask path.",
    )
    parser.add_argument(
        "--fov-path",
        default=None,
        help="Explicit FoV mask path.",
    )

    # Experiment switches.
    parser.add_argument(
        "--always-refine",
        dest="always_refine",
        action="store_true",
        default=None,
        help="Always apply CA-APSRG refinement.",
    )
    parser.add_argument(
        "--conditional-refine",
        dest="always_refine",
        action="store_false",
        help="Apply CA-APSRG only when the precision threshold rule says it is needed.",
    )
    parser.add_argument(
        "--precision-threshold",
        type=float,
        default=None,
        help="Precision threshold used when conditional refinement is enabled.",
    )

    return parser


def print_metric_block(row: dict[str, Any], prefix: str, title: str) -> None:
    """Print a compact metric block if metrics are available."""
    precision_key = f"{prefix}_precision"
    if precision_key not in row:
        print(f"\n{title}: no ground truth metric available.")
        return

    metric_names = ["accuracy", "precision", "recall", "specificity", "f1_score", "iou"]
    print(f"\n{title}:")
    for metric in metric_names:
        key = f"{prefix}_{metric}"
        if key in row:
            value = row[key]
            try:
                print(f"- {metric:12s}: {float(value):.6f}")
            except (TypeError, ValueError):
                print(f"- {metric:12s}: {value}")


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    config_path = resolve_project_path(args.config, "configs/default.yaml")
    if config_path is None:
        raise ValueError("Config path could not be resolved.")

    config = load_yaml_config(config_path)

    output_dir_from_config = (
        get_nested(config, "paths", "single_test_dir")
        or get_nested(config, "experiment", "single_test_dir")
        or "outputs/single_test"
    )
    manifest_from_config = (
        get_nested(config, "paths", "manifest_path")
        or get_nested(config, "data", "manifest_path")
        or "data/manifests/manifest.csv"
    )

    output_dir = resolve_project_path(args.output_dir, output_dir_from_config)
    if output_dir is None:
        raise ValueError("Output directory could not be resolved.")

    if args.image_path:
        image_path = resolve_project_path(args.image_path)
        mask_path = resolve_project_path(args.mask_path) if args.mask_path else None
        fov_path = resolve_project_path(args.fov_path) if args.fov_path else None
        dataset = args.dataset or "single"
        image_id = args.image_id or (image_path.stem if image_path else "unknown")
    else:
        manifest_path = resolve_project_path(args.manifest, manifest_from_config)
        if manifest_path is None:
            raise ValueError("Manifest path could not be resolved.")

        selected = choose_manifest_row(
            manifest_path,
            row_index=args.row_index,
            dataset=args.dataset,
            image_id=args.image_id,
        )

        image_path = resolve_project_path(selected.get("image_path"))
        mask_path = None if is_missing(selected.get("mask_path")) else resolve_project_path(selected.get("mask_path"))
        fov_path = None if is_missing(selected.get("fov_path")) else resolve_project_path(selected.get("fov_path"))
        dataset = str(selected.get("dataset", args.dataset or "dataset"))
        image_id = str(selected.get("image_id", args.image_id or (image_path.stem if image_path else "unknown")))

    if image_path is None:
        raise ValueError("Image path could not be resolved.")

    print("=" * 72)
    print("CA-APSRG Single Image Runner")
    print("=" * 72)
    print(f"Project root       : {PROJECT_ROOT}")
    print(f"Config file        : {config_path}")
    print(f"Image path         : {image_path}")
    print(f"Mask path          : {mask_path if mask_path else ''}")
    print(f"FoV path           : {fov_path if fov_path else ''}")
    print(f"Dataset            : {dataset}")
    print(f"Image ID           : {image_id}")
    print(f"Output directory   : {output_dir}")
    print(f"Always refine      : {args.always_refine if args.always_refine is not None else 'config default'}")
    print("=" * 72)

    result = run_single_image(
        image_path=image_path,
        mask_path=mask_path,
        fov_path=fov_path,
        output_dir=output_dir,
        dataset=dataset,
        image_id=image_id,
        config_path=config_path,
        always_refine=args.always_refine,
        precision_threshold=args.precision_threshold,
        return_arrays=False,
    )

    assert isinstance(result, dict)

    print_metric_block(result, "baseline", "APSRG baseline metrics")
    print_metric_block(result, "ca_apsrg", "CA-APSRG metrics")

    print("\nContext:")
    for key in [
        "context_vessel_density",
        "context_density_level",
        "context_noise_level",
        "context_recommended_refinement_level",
        "selected_refinement_level",
        "selected_min_component_area",
        "selected_closing_kernel_size",
    ]:
        if key in result:
            print(f"- {key}: {result[key]}")

    print("\nSaved outputs:")
    saved_keys = [
        "preprocessed_path",
        "baseline_mask_path",
        "ca_apsrg_mask_path",
        "baseline_overlay_path",
        "ca_apsrg_overlay_path",
        "comparison_path",
        "debug_json_path",
    ]
    for key in saved_keys:
        if key in result:
            print(f"- {key}: {result[key]}")

    print("\nDone.")


if __name__ == "__main__":
    main()