from __future__ import annotations

import argparse
from pathlib import Path

from src.data.png_converter import convert_tree_to_png


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert retinal vessel datasets recursively to PNG.")
    parser.add_argument("--input-root", required=True, help="Original dataset root folder.")
    parser.add_argument("--output-root", required=True, help="Working PNG output folder.")
    parser.add_argument("--copy-png", action="store_true", help="Copy existing PNG files into output root.")
    parser.add_argument("--binarize-masks", action="store_true", help="Binarize files that look like masks/labels.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output PNG files.")
    parser.add_argument(
        "--report",
        default="outputs/reports/png_conversion_report.csv",
        help="CSV report path.",
    )
    args = parser.parse_args()

    report = convert_tree_to_png(
        input_root=args.input_root,
        output_root=args.output_root,
        copy_png=args.copy_png,
        binarize_masks=args.binarize_masks,
        overwrite=args.overwrite,
    )

    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(report_path, index=False)

    print(f"Done. Converted/copied/skipped files: {len(report)}")
    print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    main()
