"""
Script No. 6: Build experiment manifest for CA-APSRG.

Run from the project root, for example:

    python scripts/01_build_manifest.py

or with explicit paths:

    python scripts/01_build_manifest.py \
        --working-root "data/working_png" \
        --output "data/manifests/manifest.csv" \
        --stare-observer ah \
        --chasedb1-observer 1stHO

This script uses src/data/manifest_builder.py to pair fundus images with
vessel ground-truth masks from DRIVE, STARE, and CHASEDB1.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

# Make sure `src` can be imported when this script is run as:
# python scripts/01_build_manifest.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.manifest_builder import (  # noqa: E402
    ManifestConfig,
    build_all_manifest,
    save_manifest,
    summarize_manifest,
    validate_manifest,
)


def load_yaml_config(config_path: str | Path) -> dict[str, Any]:
    """Load YAML config file. Return empty dict if the file is not found."""
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


def resolve_project_path(path_value: str | Path | None, default: str | Path) -> Path:
    """
    Resolve a project-relative path.

    Absolute paths are kept as-is. Relative paths are resolved from PROJECT_ROOT.
    """
    raw_path = Path(path_value or default)
    if raw_path.is_absolute():
        return raw_path
    return PROJECT_ROOT / raw_path


def bool_from_optional(value: bool | None, fallback: bool) -> bool:
    """Use CLI optional boolean when provided; otherwise use config fallback."""
    return fallback if value is None else bool(value)


def build_arg_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Build a manifest CSV for retinal vessel segmentation experiments.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--config",
        default="configs/default.yaml",
        help="YAML configuration file path.",
    )
    parser.add_argument(
        "--working-root",
        default=None,
        help="Working PNG dataset root. If omitted, it is read from config data.working_png_root.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output manifest CSV path. If omitted, it is read from config data.manifest_path.",
    )
    parser.add_argument(
        "--validation-report",
        default=None,
        help="Optional CSV path for validation report. If omitted, outputs/reports/manifest_validation.csv is used.",
    )
    parser.add_argument(
        "--summary-report",
        default=None,
        help="Optional CSV path for manifest summary. If omitted, outputs/reports/manifest_summary.csv is used.",
    )
    parser.add_argument(
        "--stare-observer",
        default=None,
        choices=["ah", "vk"],
        help="Preferred STARE observer annotation.",
    )
    parser.add_argument(
        "--chasedb1-observer",
        default=None,
        choices=["1stHO", "2ndHO"],
        help="Preferred CHASEDB1 observer annotation.",
    )

    parser.add_argument(
        "--require-ground-truth",
        dest="require_ground_truth",
        action="store_true",
        default=None,
        help="Only include images with ground-truth masks.",
    )
    parser.add_argument(
        "--allow-missing-ground-truth",
        dest="require_ground_truth",
        action="store_false",
        help="Allow rows without ground-truth masks.",
    )
    parser.add_argument(
        "--include-fov-mask",
        dest="include_fov_mask",
        action="store_true",
        default=None,
        help="Include FoV mask path when available.",
    )
    parser.add_argument(
        "--no-fov-mask",
        dest="include_fov_mask",
        action="store_false",
        help="Do not include FoV mask paths.",
    )
    parser.add_argument(
        "--absolute-paths",
        action="store_true",
        help="Save absolute paths in the manifest instead of project-relative paths.",
    )

    return parser


def save_dataframe(df: pd.DataFrame, output_csv: Path) -> Path:
    """Save a DataFrame to CSV, creating the parent directory if needed."""
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)
    return output_csv


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    config_path = resolve_project_path(args.config, "configs/default.yaml")
    config = load_yaml_config(config_path)

    working_root_from_config = (
        get_nested(config, "paths", "working_png_root")
        or get_nested(config, "data", "working_png_root")
        or "data/working_png"
    )
    manifest_path_from_config = (
        get_nested(config, "paths", "manifest_path")
        or get_nested(config, "data", "manifest_path")
        or "data/manifests/manifest.csv"
    )
    reports_dir_from_config = (
        get_nested(config, "paths", "reports_dir")
        or get_nested(config, "experiment", "reports_dir")
        or "outputs/reports"
    )

    manifest_cfg = config.get("manifest", {}) if isinstance(config.get("manifest", {}), dict) else {}

    working_root = resolve_project_path(args.working_root, working_root_from_config)
    output_csv = resolve_project_path(args.output, manifest_path_from_config)
    reports_dir = resolve_project_path(None, reports_dir_from_config)
    validation_report = resolve_project_path(args.validation_report, reports_dir / "manifest_validation.csv")
    summary_report = resolve_project_path(args.summary_report, reports_dir / "manifest_summary.csv")

    stare_observer = args.stare_observer or str(manifest_cfg.get("stare_observer", "ah"))
    chasedb1_observer = args.chasedb1_observer or str(manifest_cfg.get("chasedb1_observer", "1stHO"))
    require_ground_truth = bool_from_optional(
        args.require_ground_truth,
        bool(manifest_cfg.get("require_ground_truth", True)),
    )
    include_fov_mask = bool_from_optional(
        args.include_fov_mask,
        bool(manifest_cfg.get("include_fov_mask_if_available", True)),
    )

    if not working_root.exists():
        raise FileNotFoundError(
            f"Working PNG root not found: {working_root}\n"
            "Run script No. 4 first: python scripts/00_convert_all_to_png.py"
        )

    manifest_config = ManifestConfig(
        require_ground_truth=require_ground_truth,
        include_fov_mask_if_available=include_fov_mask,
        stare_observer=stare_observer,
        chasedb1_observer=chasedb1_observer,
        use_absolute_paths=bool(args.absolute_paths),
    )

    print("=" * 72)
    print("CA-APSRG Manifest Builder")
    print("=" * 72)
    print(f"Project root          : {PROJECT_ROOT}")
    print(f"Config file           : {config_path}")
    print(f"Working PNG root      : {working_root}")
    print(f"Output manifest       : {output_csv}")
    print(f"Validation report     : {validation_report}")
    print(f"Summary report        : {summary_report}")
    print(f"STARE observer        : {stare_observer}")
    print(f"CHASEDB1 observer     : {chasedb1_observer}")
    print(f"Require ground truth  : {require_ground_truth}")
    print(f"Include FoV mask      : {include_fov_mask}")
    print(f"Use absolute paths    : {args.absolute_paths}")
    print("=" * 72)

    manifest_df = build_all_manifest(working_root, config=manifest_config)
    save_manifest(manifest_df, output_csv)

    validation_df = validate_manifest(manifest_df)
    summary_df = summarize_manifest(manifest_df)

    save_dataframe(validation_df, validation_report)
    save_dataframe(summary_df, summary_report)

    print("\nManifest summary:")
    if summary_df.empty:
        print("- No image-mask pairs found.")
    else:
        print(summary_df.to_string(index=False))

    total_rows = len(manifest_df)
    ready_rows = int(validation_df["is_ready"].sum()) if not validation_df.empty and "is_ready" in validation_df else 0
    missing_images = int((~validation_df["image_exists"]).sum()) if not validation_df.empty and "image_exists" in validation_df else 0
    missing_masks = int((~validation_df["mask_exists"]).sum()) if not validation_df.empty and "mask_exists" in validation_df else 0

    print("\nValidation:")
    print(f"- Total rows      : {total_rows}")
    print(f"- Ready rows      : {ready_rows}")
    print(f"- Missing images  : {missing_images}")
    print(f"- Missing masks   : {missing_masks}")

    print("\nFiles saved:")
    print(f"- Manifest         : {output_csv}")
    print(f"- Validation report: {validation_report}")
    print(f"- Summary report   : {summary_report}")

    if total_rows == 0:
        print(
            "\nWarning: Manifest is empty. Check whether script No. 4 produced PNG files "
            "under data/working_png with DRIVE, STARE, and CHASEDB1 folders."
        )
    elif ready_rows < total_rows:
        print(
            "\nWarning: Some manifest rows are not ready. "
            "Open the validation report to inspect missing image or mask paths."
        )


if __name__ == "__main__":
    main()