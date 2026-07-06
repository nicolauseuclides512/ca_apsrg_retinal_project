from __future__ import annotations

import argparse

from src.pipeline.run_pipeline import run_batch


def main() -> None:
    parser = argparse.ArgumentParser(description="Run CA-APSRG pipeline for all rows in manifest.")
    parser.add_argument("--manifest", required=True, help="Manifest CSV path.")
    parser.add_argument("--output-dir", default="outputs/experiments", help="Output directory.")
    parser.add_argument("--no-always-refine", action="store_true", help="Only refine if false-positive indication exists.")
    args = parser.parse_args()

    df = run_batch(
        manifest_path=args.manifest,
        output_dir=args.output_dir,
        always_refine=not args.no_always_refine,
    )

    print(f"Done. Results saved to: {args.output_dir}/metrics_summary.csv")
    print(df.head())
    if "dataset" in df.columns:
        metric_cols = [c for c in df.columns if c.startswith("baseline_") or c.startswith("ca_apsrg_")]
        print(df.groupby("dataset")[metric_cols].mean(numeric_only=True))


if __name__ == "__main__":
    main()
