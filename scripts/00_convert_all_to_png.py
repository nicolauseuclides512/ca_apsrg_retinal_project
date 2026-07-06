"""
Script No. 4: Convert all retinal vessel dataset images to PNG.

Run from the project root, for example:

    python scripts/00_convert_all_to_png.py

or with explicit paths:

    python scripts/00_convert_all_to_png.py \
        --input-root "data/raw/Retinal Vessel" \
        --output-root "data/working_png" \
        --copy-png \
        --binarize-masks

This script uses src/data/png_converter.py as the main conversion engine.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

# Make sure `src` can be imported when this script is run as:
# python scripts/00_convert_all_to_png.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.png_converter import (  # noqa: E402
    PngConversionConfig,
    convert_folder_recursive,
    summarize_conversion_report,
    write_conversion_report,
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


def resolve_project_path(path_value: str | Path | None, default: str) -> Path:
    """
    Resolve a project-relative path.

    Absolute paths are kept as-is. Relative paths are resolved from PROJECT_ROOT.
    """
    raw_path = Path(path_value or default)
    if raw_path.is_absolute():
        return raw_path
    return PROJECT_ROOT / raw_path


def tuple_from_config(value: Any, default: tuple[str, ...]) -> tuple[str, ...]:
    """Convert list/tuple/string config values into tuple[str, ...]."""
    if value is None:
        return default
    if isinstance(value, str):
        return (value,)
    if isinstance(value, (list, tuple)):
        return tuple(str(item) for item in value)
    return default


def bool_from_optional(value: bool | None, fallback: bool) -> bool:
    """Use CLI optional boolean when provided; otherwise use config fallback."""
    return fallback if value is None else bool(value)


def build_conversion_config(config: dict[str, Any], args: argparse.Namespace) -> PngConversionConfig:
    """Build PngConversionConfig from YAML config plus command-line overrides."""
    conversion_cfg = config.get("conversion", {}) if isinstance(config.get("conversion", {}), dict) else {}

    default_cfg = PngConversionConfig()

    convertible_extensions = tuple_from_config(
        conversion_cfg.get("convertible_extensions"),
        default_cfg.convertible_extensions,
    )
    skip_archive_extensions = tuple_from_config(
        conversion_cfg.get("skip_archive_extensions"),
        default_cfg.skip_archive_extensions,
    )
    mask_name_keywords = tuple_from_config(
        conversion_cfg.get("mask_name_keywords"),
        default_cfg.mask_name_keywords,
    )

    return PngConversionConfig(
        convertible_extensions=convertible_extensions,
        copy_existing_png=bool_from_optional(
            args.copy_png,
            bool(conversion_cfg.get("copy_existing_png", default_cfg.copy_existing_png)),
        ),
        skip_archive_extensions=skip_archive_extensions,
        binarize_masks=bool_from_optional(
            args.binarize_masks,
            bool(conversion_cfg.get("binarize_masks", default_cfg.binarize_masks)),
        ),
        binary_threshold=int(conversion_cfg.get("binary_threshold", default_cfg.binary_threshold)),
        png_compress_level=int(conversion_cfg.get("png_compress_level", default_cfg.png_compress_level)),
        preserve_relative_structure=bool(
            conversion_cfg.get("preserve_relative_structure", default_cfg.preserve_relative_structure)
        ),
        overwrite=bool(args.overwrite),
        mask_name_keywords=mask_name_keywords,
        observer_suffixes=default_cfg.observer_suffixes,
    )


def build_arg_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Convert DRIVE, STARE, CHASEDB1, or other retinal vessel datasets recursively to PNG.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--config",
        default="configs/default.yaml",
        help="YAML configuration file path.",
    )
    parser.add_argument(
        "--input-root",
        default=None,
        help="Original dataset root. If omitted, it is read from config paths.raw_root or data.raw_root.",
    )
    parser.add_argument(
        "--output-root",
        default=None,
        help="Output root for standardized PNG dataset. If omitted, it is read from config.",
    )
    parser.add_argument(
        "--report",
        default=None,
        help="CSV conversion report path. If omitted, it is read from config.",
    )

    parser.add_argument(
        "--copy-png",
        dest="copy_png",
        action="store_true",
        default=None,
        help="Copy existing PNG files into output root.",
    )
    parser.add_argument(
        "--no-copy-png",
        dest="copy_png",
        action="store_false",
        help="Do not copy existing PNG files.",
    )
    parser.add_argument(
        "--binarize-masks",
        dest="binarize_masks",
        action="store_true",
        default=None,
        help="Binarize files that look like masks, labels, manual annotations, or FoV masks.",
    )
    parser.add_argument(
        "--no-binarize-masks",
        dest="binarize_masks",
        action="store_false",
        help="Do not binarize mask-like files.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing PNG files in output root.",
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress bar.",
    )

    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    config_path = resolve_project_path(args.config, "configs/default.yaml")
    config = load_yaml_config(config_path)

    raw_root_from_config = (
        get_nested(config, "paths", "raw_root")
        or get_nested(config, "data", "raw_root")
        or "data/raw/Retinal Vessel"
    )
    working_root_from_config = (
        get_nested(config, "paths", "working_png_root")
        or get_nested(config, "data", "working_png_root")
        or "data/working_png"
    )
    report_from_config = (
        get_nested(config, "conversion", "report_csv")
        or get_nested(config, "paths", "reports_dir")
        or "outputs/reports/png_conversion_report.csv"
    )

    if report_from_config and str(report_from_config).endswith("reports"):
        report_from_config = str(Path(report_from_config) / "png_conversion_report.csv")

    input_root = resolve_project_path(args.input_root, str(raw_root_from_config))
    output_root = resolve_project_path(args.output_root, str(working_root_from_config))
    report_path = resolve_project_path(args.report, str(report_from_config))

    conversion_config = build_conversion_config(config, args)

    print("=" * 72)
    print("CA-APSRG Dataset PNG Conversion")
    print("=" * 72)
    print(f"Project root      : {PROJECT_ROOT}")
    print(f"Config file       : {config_path}")
    print(f"Input root        : {input_root}")
    print(f"Output root       : {output_root}")
    print(f"Report path       : {report_path}")
    print(f"Copy existing PNG : {conversion_config.copy_existing_png}")
    print(f"Binarize masks    : {conversion_config.binarize_masks}")
    print(f"Overwrite output  : {conversion_config.overwrite}")
    print("=" * 72)

    report = convert_folder_recursive(
        input_root=input_root,
        output_root=output_root,
        config=conversion_config,
        show_progress=not args.no_progress,
    )

    write_conversion_report(report, report_path)
    summary = summarize_conversion_report(report)

    print("\nConversion summary:")
    if summary:
        for action, count in summary.items():
            print(f"- {action}: {count}")
    else:
        print("- No files processed.")

    print(f"\nTotal records: {len(report)}")
    print(f"Report saved : {report_path}")
    print(f"PNG output   : {output_root}")

    error_count = int((report["action"] == "error").sum()) if not report.empty and "action" in report else 0
    if error_count > 0:
        print(f"\nWarning: {error_count} file(s) failed to convert. Check the CSV report.")


if __name__ == "__main__":
    main()