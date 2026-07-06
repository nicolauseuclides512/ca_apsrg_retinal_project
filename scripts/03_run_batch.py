"""
Script No. 15: Run CA-APSRG pipeline on a batch of retinal fundus images.

Typical use after manifest has been created:

    python scripts/03_run_batch.py

or explicitly:

    python scripts/03_run_batch.py \
        --manifest data/manifests/manifest.csv \
        --output-dir outputs/experiments

Run only one dataset:

    python scripts/03_run_batch.py --dataset DRIVE
    python scripts/03_run_batch.py --dataset STARE
    python scripts/03_run_batch.py --dataset CHASEDB1

Run a small debugging subset:

    python scripts/03_run_batch.py --dataset DRIVE --max-images 3

Run conditional refinement instead of always refining:

    python scripts/03_run_batch.py --conditional-refine --precision-threshold 0.95

The script calls src/pipeline/run_pipeline.py and saves:
- metrics_per_image.csv
- metrics_summary.csv
- pipeline_errors.csv, only when errors occur
- batch_manifest_used.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Optional

import pandas as pd
import yaml

# Make sure `src` can be imported when this script is run as:
# python scripts/03_run_batch.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline.run_pipeline import run_batch  # noqa: E402


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


def parse_dataset_filters(values: list[str] | None) -> list[str]:
    """Parse dataset filters passed as repeated arguments or comma-separated values."""
    if not values:
        return []

    datasets: list[str] = []
    for value in values:
        parts = [item.strip() for item in str(value).split(",")]
        datasets.extend([item for item in parts if item])

    return datasets


def filter_manifest(
    manifest_df: pd.DataFrame,
    *,
    datasets: list[str] | None = None,
    image_ids: list[str] | None = None,
    start_index: int = 0,
    max_images: int | None = None,
) -> pd.DataFrame:
    """Filter manifest rows for controlled batch execution."""
    df = manifest_df.copy()

    if datasets:
        dataset_set = {str(dataset).strip().lower() for dataset in datasets}
        df = df[df["dataset"].astype(str).str.lower().isin(dataset_set)]

    if image_ids:
        image_set = {str(image_id).strip().lower() for image_id in image_ids}
        df = df[df["image_id"].astype(str).str.lower().isin(image_set)]

    if start_index > 0:
        df = df.iloc[int(start_index):]

    if max_images is not None:
        df = df.head(int(max_images))

    return df.reset_index(drop=True)


def save_filtered_manifest(df: pd.DataFrame, output_dir: Path) -> Path:
    """Save the manifest actually used for this batch run."""
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_used_path = output_dir / "batch_manifest_used.csv"
    df.to_csv(manifest_used_path, index=False)
    return manifest_used_path


def build_arg_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Run CA-APSRG pipeline for all or selected rows in a manifest CSV.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--config",
        default="configs/default.yaml",
        help="YAML configuration file path.",
    )
    parser.add_argument(
        "--manifest",
        default=None,
        help="Manifest CSV path. If omitted, it is read from config paths.manifest_path or data.manifest_path.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Experiment output directory. If omitted, it is read from config paths.experiments_dir or experiment.output_dir.",
    )

    parser.add_argument(
        "--dataset",
        action="append",
        default=None,
        help="Dataset filter. Can be repeated or comma-separated, e.g. --dataset DRIVE --dataset STARE or --dataset DRIVE,STARE.",
    )
    parser.add_argument(
        "--image-id",
        action="append",
        default=None,
        help="Image ID filter. Can be repeated, useful for debugging selected images.",
    )
    parser.add_argument(
        "--start-index",
        type=int,
        default=0,
        help="Start processing from this zero-based row index after filtering.",
    )
    parser.add_argument(
        "--max-images",
        type=int,
        default=None,
        help="Maximum number of manifest rows to process after filtering.",
    )

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
        help="Apply CA-APSRG only when baseline precision is below the precision threshold.",
    )
    parser.add_argument(
        "--precision-threshold",
        type=float,
        default=None,
        help="Precision threshold used when conditional refinement is enabled.",
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress bar.",
    )

    return parser


def print_manifest_summary(df: pd.DataFrame) -> None:
    """Print compact manifest summary."""
    print("\nManifest rows selected:")
    print(f"- Total rows: {len(df)}")

    if df.empty:
        return

    if "dataset" in df.columns:
        summary = df.groupby("dataset", dropna=False).size().reset_index(name="n_images")
        print(summary.to_string(index=False))


def print_metric_summary(summary_path: Path) -> None:
    """Print compact metric summary from metrics_summary.csv when available."""
    if not summary_path.is_file():
        print(f"\nMetric summary file not found: {summary_path}")
        return

    summary = pd.read_csv(summary_path)
    if summary.empty:
        print("\nMetric summary is empty.")
        return

    preferred_cols = [
        "dataset",
        "method",
        "n_images",
        "precision_mean",
        "recall_mean",
        "f1_score_mean",
        "iou_mean",
        "accuracy_mean",
    ]
    available_cols = [col for col in preferred_cols if col in summary.columns]

    print("\nMetrics summary:")
    print(summary[available_cols].to_string(index=False))


def print_improvement_summary(results: pd.DataFrame) -> None:
    """Print CA-APSRG minus APSRG improvement summary if metrics are available."""
    required = ["dataset", "baseline_precision", "ca_apsrg_precision", "baseline_f1_score", "ca_apsrg_f1_score"]
    if results.empty or not all(col in results.columns for col in required):
        return

    df = results.copy()
    df["delta_precision"] = df["ca_apsrg_precision"] - df["baseline_precision"]
    df["delta_recall"] = df.get("ca_apsrg_recall", 0) - df.get("baseline_recall", 0)
    df["delta_f1_score"] = df["ca_apsrg_f1_score"] - df["baseline_f1_score"]
    df["delta_iou"] = df.get("ca_apsrg_iou", 0) - df.get("baseline_iou", 0)

    summary = (
        df.groupby("dataset", dropna=False)[["delta_precision", "delta_recall", "delta_f1_score", "delta_iou"]]
        .mean()
        .reset_index()
    )

    print("\nAverage improvement, CA-APSRG minus APSRG:")
    print(summary.to_string(index=False))


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    config_path = resolve_project_path(args.config, "configs/default.yaml")
    if config_path is None:
        raise ValueError("Config path could not be resolved.")

    config = load_yaml_config(config_path)

    manifest_from_config = (
        get_nested(config, "paths", "manifest_path")
        or get_nested(config, "data", "manifest_path")
        or "data/manifests/manifest.csv"
    )
    output_dir_from_config = (
        get_nested(config, "paths", "experiments_dir")
        or get_nested(config, "experiment", "output_dir")
        or "outputs/experiments"
    )

    manifest_path = resolve_project_path(args.manifest, manifest_from_config)
    output_dir = resolve_project_path(args.output_dir, output_dir_from_config)

    if manifest_path is None:
        raise ValueError("Manifest path could not be resolved.")
    if output_dir is None:
        raise ValueError("Output directory could not be resolved.")
    if not manifest_path.is_file():
        raise FileNotFoundError(
            f"Manifest file not found: {manifest_path}\n"
            "Run script No. 6 first: python scripts/01_build_manifest.py"
        )

    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_df = pd.read_csv(manifest_path)
    datasets = parse_dataset_filters(args.dataset)
    image_ids = parse_dataset_filters(args.image_id)

    filtered_df = filter_manifest(
        manifest_df,
        datasets=datasets,
        image_ids=image_ids,
        start_index=max(int(args.start_index), 0),
        max_images=args.max_images,
    )

    if filtered_df.empty:
        raise ValueError(
            "No manifest rows selected. Check --dataset, --image-id, --start-index, or --max-images."
        )

    manifest_used_path = save_filtered_manifest(filtered_df, output_dir)

    print("=" * 72)
    print("CA-APSRG Batch Runner")
    print("=" * 72)
    print(f"Project root       : {PROJECT_ROOT}")
    print(f"Config file        : {config_path}")
    print(f"Original manifest  : {manifest_path}")
    print(f"Manifest used      : {manifest_used_path}")
    print(f"Output directory   : {output_dir}")
    print(f"Dataset filter     : {datasets if datasets else 'all'}")
    print(f"Image ID filter    : {image_ids if image_ids else 'all'}")
    print(f"Start index        : {args.start_index}")
    print(f"Max images         : {args.max_images if args.max_images is not None else 'all'}")
    print(f"Always refine      : {args.always_refine if args.always_refine is not None else 'config default'}")
    print(f"Precision threshold: {args.precision_threshold if args.precision_threshold is not None else 'config default'}")
    print("=" * 72)

    print_manifest_summary(filtered_df)

    results = run_batch(
        manifest_path=manifest_used_path,
        output_dir=output_dir,
        config_path=config_path,
        always_refine=args.always_refine,
        precision_threshold=args.precision_threshold,
        show_progress=not args.no_progress,
    )

    per_image_path = output_dir / "metrics_per_image.csv"
    summary_path = output_dir / "metrics_summary.csv"
    error_path = output_dir / "pipeline_errors.csv"

    print("\nFiles saved:")
    print(f"- Manifest used     : {manifest_used_path}")
    print(f"- Per-image metrics : {per_image_path}")
    print(f"- Metrics summary   : {summary_path}")
    if error_path.is_file():
        print(f"- Pipeline errors   : {error_path}")

    print_metric_summary(summary_path)
    print_improvement_summary(results)

    print("\nDone.")


if __name__ == "__main__":
    main()