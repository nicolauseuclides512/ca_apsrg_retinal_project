"""
Run method-level ablation experiments for the improved CA-APSRG pipeline.

This script keeps the previous morphology experiments (1-6) untouched and
creates a separate ablation suite for the methodological evolution:

A01: Legacy percentile-polling seeds + BFS
A02: Harris polling seeds + BFS
A03: Fuzzy SRG seeds + BFS
A04: Selective fuzzy-Harris seeds + BFS
A05: Selective fuzzy-Harris seeds + edge-delayed growing
A06: A05 + APSRG process context recorded, without level override
A07: A05 + APSRG process context allowed to override refinement level

Each experiment uses the same preprocessing, candidate-map thresholds, and
balanced adaptive morphology unless explicitly changed by the ablation.

Run from project root:

    python scripts/06_run_method_ablation.py --clean

Quick smoke test:

    python scripts/06_run_method_ablation.py \
        --dataset DRIVE --max-images 3 --clean

Generated outputs:

    configs/method_ablation/*.yaml
    outputs/method_ablation/experiments_<key>/
    outputs/method_ablation/analysis_<key>/
    outputs/method_ablation/comparison/ablation_summary_long.csv
    outputs/method_ablation/comparison/ablation_article_table.csv
    outputs/method_ablation/comparison/ablation_delta_vs_reference.csv
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_ROOT / "configs" / "default.yaml"
CONFIG_DIR = PROJECT_ROOT / "configs" / "method_ablation"
OUTPUT_ROOT = PROJECT_ROOT / "outputs" / "method_ablation"
COMPARISON_DIR = OUTPUT_ROOT / "comparison"

REFERENCE_EXPERIMENT = "a01_legacy_polling_bfs"

METRICS = [
    "accuracy",
    "precision",
    "recall",
    "specificity",
    "f1_score",
    "iou",
    "balanced_accuracy",
    "dice",
]

EXPERIMENTS: dict[str, dict[str, Any]] = {
    "a01_legacy_polling_bfs": {
        "label": "A01 - Legacy percentile-polling seeds with BFS",
        "description": (
            "Reference implementation using the previous percentile/local "
            "polling seed strategy and conventional BFS region growing."
        ),
        "overrides": {
            "apsrg_baseline": {
                "seed_selection_method": "percentile_polling",
                "region_growing_mode": "bfs",
            },
            "ca_apsrg": {
                "process_context": {
                    "enabled": False,
                    "can_trigger_refinement": False,
                    "can_override_refinement_level": False,
                }
            },
        },
    },
    "a02_harris_bfs": {
        "label": "A02 - Harris polling seeds with BFS",
        "description": (
            "Tests the APSRG Harris automatic seed-polling contribution while "
            "retaining conventional BFS region growing."
        ),
        "overrides": {
            "apsrg_baseline": {
                "seed_selection_method": "harris_polling",
                "region_growing_mode": "bfs",
            },
            "ca_apsrg": {
                "process_context": {
                    "enabled": False,
                    "can_trigger_refinement": False,
                    "can_override_refinement_level": False,
                }
            },
        },
    },
    "a03_fuzzy_srg_bfs": {
        "label": "A03 - Fuzzy SRG seeds with BFS",
        "description": (
            "Tests fuzzy connected-edge and local-similarity seed selection "
            "without Harris polling or edge-delayed growing."
        ),
        "overrides": {
            "apsrg_baseline": {
                "seed_selection_method": "fuzzy_srg",
                "region_growing_mode": "bfs",
            },
            "ca_apsrg": {
                "process_context": {
                    "enabled": False,
                    "can_trigger_refinement": False,
                    "can_override_refinement_level": False,
                }
            },
        },
    },
    "a04_selective_hybrid_bfs": {
        "label": "A04 - Selective fuzzy-Harris seeds with BFS",
        "description": (
            "Tests selective fuzzy-supported Harris polling while keeping "
            "conventional BFS region growing."
        ),
        "overrides": {
            "apsrg_baseline": {
                "seed_selection_method": "selective_fuzzy_harris",
                "region_growing_mode": "bfs",
            },
            "ca_apsrg": {
                "process_context": {
                    "enabled": False,
                    "can_trigger_refinement": False,
                    "can_override_refinement_level": False,
                }
            },
        },
    },
    "a05_selective_hybrid_edge_delayed": {
        "label": "A05 - Selective fuzzy-Harris with edge-delayed growing",
        "description": (
            "Tests the complete improved APSRG core before process-context "
            "influence on adaptive morphology."
        ),
        "overrides": {
            "apsrg_baseline": {
                "seed_selection_method": "selective_fuzzy_harris",
                "region_growing_mode": "edge_delayed",
            },
            "ca_apsrg": {
                "process_context": {
                    "enabled": False,
                    "can_trigger_refinement": False,
                    "can_override_refinement_level": False,
                }
            },
        },
    },
    "a06_process_context_record_only": {
        "label": "A06 - Full APSRG with process context recorded only",
        "description": (
            "Records APSRG process context but does not allow it to override "
            "the mask-based refinement level. This is a sanity-control run."
        ),
        "overrides": {
            "apsrg_baseline": {
                "seed_selection_method": "selective_fuzzy_harris",
                "region_growing_mode": "edge_delayed",
            },
            "ca_apsrg": {
                "process_context": {
                    "enabled": True,
                    "can_trigger_refinement": True,
                    "can_override_refinement_level": False,
                }
            },
        },
    },
    "a07_process_context_override": {
        "label": "A07 - Full CA-APSRG with process-context override",
        "description": (
            "Full proposed pipeline in which APSRG process context may change "
            "the adaptive morphology refinement level."
        ),
        "overrides": {
            "apsrg_baseline": {
                "seed_selection_method": "selective_fuzzy_harris",
                "region_growing_mode": "edge_delayed",
            },
            "ca_apsrg": {
                "process_context": {
                    "enabled": True,
                    "can_trigger_refinement": True,
                    "can_override_refinement_level": True,
                }
            },
        },
    },
}


def load_yaml(path: Path) -> dict[str, Any]:
    """Read a YAML file into a dictionary."""
    if not path.is_file():
        raise FileNotFoundError(f"YAML file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    return data or {}


def save_yaml(path: Path, data: dict[str, Any]) -> None:
    """Write a dictionary as YAML."""
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(
            data,
            file,
            sort_keys=False,
            allow_unicode=True,
        )


def deep_update(base: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge updates into base and return base."""
    for key, value in updates.items():
        if (
            isinstance(value, dict)
            and isinstance(base.get(key), dict)
        ):
            deep_update(base[key], value)
        else:
            base[key] = deepcopy(value)

    return base


def build_experiment_config(
    base_config: dict[str, Any],
    experiment_key: str,
) -> dict[str, Any]:
    """Build one resolved experiment YAML dictionary."""
    spec = EXPERIMENTS[experiment_key]
    config = deepcopy(base_config)

    deep_update(config, spec["overrides"])

    project = config.setdefault("project", {})
    project["experiment_name"] = experiment_key
    project["experiment_label"] = spec["label"]
    project["experiment_description"] = spec["description"]

    experiment = config.setdefault("experiment", {})
    experiment["always_refine"] = True

    ca_config = config.setdefault("ca_apsrg", {})
    ca_config["enabled"] = True
    ca_config["always_refine"] = True

    # Keep the balanced adaptive morphology fixed across all method ablations.
    adaptive = config.setdefault("adaptive_morphology", {})
    adaptive.update(
        {
            "enabled": True,
            "remove_small_objects": True,
            "fill_small_holes": False,
            "closing_enabled": False,
            "opening_enabled": False,
            "skeleton_guard_enabled": True,
            "small_component_area_low_density": 8,
            "small_component_area_normal": 18,
            "small_component_area_high_density": 28,
            "hole_area_low_density": 4,
            "hole_area_normal": 8,
            "hole_area_high_density": 12,
            "closing_kernel_low_density": 0,
            "closing_kernel_normal": 0,
            "closing_kernel_high_density": 0,
            "opening_kernel_low_density": 0,
            "opening_kernel_normal": 0,
            "opening_kernel_high_density": 0,
            "skeleton_restore_radius": 1,
            "skeleton_min_component_length": 6,
        }
    )

    return config


def run_command(command: list[str]) -> None:
    """Run one subprocess from the project root."""
    print("\n$ " + " ".join(command))
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def clean_directory(path: Path) -> None:
    """Delete a directory when it exists."""
    if path.exists():
        shutil.rmtree(path)


def detect_id_columns(frame: pd.DataFrame) -> list[str]:
    """Return stable columns for paired per-image comparison."""
    candidates = ["dataset", "image_id", "image_path"]
    selected = [column for column in candidates if column in frame.columns]

    if "dataset" not in selected and "dataset" in frame.columns:
        selected.insert(0, "dataset")

    if not selected:
        raise ValueError(
            "Could not find dataset/image identifier columns in metrics file."
        )

    return selected


def collect_long_results(
    experiment_keys: list[str],
) -> pd.DataFrame:
    """Collect per-image metrics from all completed experiments."""
    records: list[dict[str, Any]] = []

    for experiment_key in experiment_keys:
        metrics_path = (
            OUTPUT_ROOT
            / f"experiments_{experiment_key}"
            / "metrics_per_image.csv"
        )

        if not metrics_path.is_file():
            print(f"Warning: metrics not found, skipped: {metrics_path}")
            continue

        frame = pd.read_csv(metrics_path)
        id_columns = detect_id_columns(frame)

        for output_method, prefix in [
            ("APSRG", "baseline"),
            ("CA-APSRG", "ca_apsrg"),
        ]:
            for metric in METRICS:
                column = f"{prefix}_{metric}"
                if column not in frame.columns:
                    continue

                subset_columns = id_columns + [column]
                subset = frame[subset_columns].copy()
                subset = subset.rename(columns={column: "value"})
                subset["experiment"] = experiment_key
                subset["experiment_label"] = EXPERIMENTS[experiment_key]["label"]
                subset["output_method"] = output_method
                subset["metric"] = metric

                records.extend(subset.to_dict(orient="records"))

    if not records:
        return pd.DataFrame()

    return pd.DataFrame.from_records(records)


def build_summary(long_results: pd.DataFrame) -> pd.DataFrame:
    """Build mean/std/count summary by experiment, dataset, method, metric."""
    if long_results.empty:
        return pd.DataFrame()

    group_columns = [
        "experiment",
        "experiment_label",
        "dataset",
        "output_method",
        "metric",
    ]

    summary = (
        long_results.groupby(group_columns, dropna=False)["value"]
        .agg(["count", "mean", "std", "median", "min", "max"])
        .reset_index()
        .rename(columns={"count": "n_images"})
    )

    return summary


def build_article_table(summary: pd.DataFrame) -> pd.DataFrame:
    """Build a wide table suitable for manuscript inspection."""
    if summary.empty:
        return pd.DataFrame()

    preferred_metrics = [
        "precision",
        "recall",
        "f1_score",
        "iou",
        "accuracy",
    ]

    filtered = summary[summary["metric"].isin(preferred_metrics)].copy()

    table = filtered.pivot_table(
        index=[
            "experiment",
            "experiment_label",
            "dataset",
            "output_method",
        ],
        columns="metric",
        values="mean",
        aggfunc="first",
    ).reset_index()

    table.columns.name = None
    return table


def build_delta_vs_reference(long_results: pd.DataFrame) -> pd.DataFrame:
    """Build paired mean deltas and win/tie/loss counts vs A01 reference."""
    if long_results.empty:
        return pd.DataFrame()

    reference = long_results[
        long_results["experiment"] == REFERENCE_EXPERIMENT
    ].copy()

    if reference.empty:
        print("Warning: reference experiment is unavailable; delta table skipped.")
        return pd.DataFrame()

    candidate_id_columns = [
        column
        for column in ["dataset", "image_id", "image_path"]
        if column in long_results.columns
    ]

    merge_keys = candidate_id_columns + ["output_method", "metric"]

    reference = reference[merge_keys + ["value"]].rename(
        columns={"value": "reference_value"}
    )

    comparison = long_results[
        long_results["experiment"] != REFERENCE_EXPERIMENT
    ].merge(reference, on=merge_keys, how="inner")

    if comparison.empty:
        return pd.DataFrame()

    comparison["delta"] = comparison["value"] - comparison["reference_value"]
    epsilon = 1e-12
    comparison["win"] = comparison["delta"] > epsilon
    comparison["tie"] = comparison["delta"].abs() <= epsilon
    comparison["loss"] = comparison["delta"] < -epsilon

    delta_summary = (
        comparison.groupby(
            [
                "experiment",
                "experiment_label",
                "dataset",
                "output_method",
                "metric",
            ],
            dropna=False,
        )
        .agg(
            n_pairs=("delta", "count"),
            mean_delta=("delta", "mean"),
            median_delta=("delta", "median"),
            std_delta=("delta", "std"),
            wins=("win", "sum"),
            ties=("tie", "sum"),
            losses=("loss", "sum"),
        )
        .reset_index()
    )

    return delta_summary


def save_comparison_outputs(experiment_keys: list[str]) -> None:
    """Create cross-experiment comparison CSV files."""
    COMPARISON_DIR.mkdir(parents=True, exist_ok=True)

    long_results = collect_long_results(experiment_keys)
    if long_results.empty:
        print("No completed metrics were found for cross-experiment comparison.")
        return

    summary = build_summary(long_results)
    article_table = build_article_table(summary)
    delta_table = build_delta_vs_reference(long_results)

    long_results.to_csv(
        COMPARISON_DIR / "ablation_per_image_long.csv",
        index=False,
    )
    summary.to_csv(
        COMPARISON_DIR / "ablation_summary_long.csv",
        index=False,
    )
    article_table.to_csv(
        COMPARISON_DIR / "ablation_article_table.csv",
        index=False,
    )
    delta_table.to_csv(
        COMPARISON_DIR / "ablation_delta_vs_reference.csv",
        index=False,
    )

    print("\nCross-experiment comparison saved:")
    print(f"- {COMPARISON_DIR / 'ablation_per_image_long.csv'}")
    print(f"- {COMPARISON_DIR / 'ablation_summary_long.csv'}")
    print(f"- {COMPARISON_DIR / 'ablation_article_table.csv'}")
    print(f"- {COMPARISON_DIR / 'ablation_delta_vs_reference.csv'}")


def build_arg_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Run method-level CA-APSRG ablation experiments.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--manifest",
        default="data/manifests/manifest.csv",
        help="Manifest CSV path relative to project root.",
    )
    parser.add_argument(
        "--dataset",
        action="append",
        default=None,
        help=(
            "Dataset filter passed to the batch runner. May be repeated or "
            "comma-separated."
        ),
    )
    parser.add_argument(
        "--max-images",
        type=int,
        default=None,
        help="Maximum number of images per experiment after dataset filtering.",
    )
    parser.add_argument(
        "--only",
        nargs="*",
        choices=list(EXPERIMENTS.keys()),
        default=None,
        help="Run only selected ablation experiment keys.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete selected experiment output folders before running.",
    )
    parser.add_argument(
        "--skip-run",
        action="store_true",
        help="Generate configs and rebuild comparison tables from existing results.",
    )
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Pass --no-plots to scripts/04_summarize_results.py.",
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Pass --no-progress to scripts/03_run_batch.py.",
    )

    return parser


def main() -> None:
    """Run the selected method-ablation suite."""
    args = build_arg_parser().parse_args()

    if not DEFAULT_CONFIG.is_file():
        raise FileNotFoundError(f"Default config not found: {DEFAULT_CONFIG}")

    manifest_path = PROJECT_ROOT / args.manifest
    if not manifest_path.is_file():
        raise FileNotFoundError(
            f"Manifest not found: {manifest_path}\n"
            "Run scripts/01_build_manifest.py first."
        )

    base_config = load_yaml(DEFAULT_CONFIG)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    selected_keys = args.only if args.only else list(EXPERIMENTS.keys())
    generated_configs: dict[str, Path] = {}

    # Generate all YAML files for transparency, even when only a subset is run.
    for experiment_key in EXPERIMENTS:
        config = build_experiment_config(base_config, experiment_key)
        config_path = CONFIG_DIR / f"{experiment_key}.yaml"
        save_yaml(config_path, config)
        generated_configs[experiment_key] = config_path

    if not args.skip_run:
        for experiment_key in selected_keys:
            spec = EXPERIMENTS[experiment_key]
            experiment_dir = OUTPUT_ROOT / f"experiments_{experiment_key}"
            analysis_dir = OUTPUT_ROOT / f"analysis_{experiment_key}"

            if args.clean:
                clean_directory(experiment_dir)
                clean_directory(analysis_dir)

            print("\n" + "=" * 88)
            print(spec["label"])
            print(spec["description"])
            print("=" * 88)

            batch_command = [
                sys.executable,
                "scripts/03_run_batch.py",
                "--config",
                str(generated_configs[experiment_key].relative_to(PROJECT_ROOT)),
                "--manifest",
                args.manifest,
                "--output-dir",
                str(experiment_dir.relative_to(PROJECT_ROOT)),
            ]

            for dataset_value in args.dataset or []:
                batch_command.extend(["--dataset", dataset_value])

            if args.max_images is not None:
                batch_command.extend(["--max-images", str(args.max_images)])

            if args.no_progress:
                batch_command.append("--no-progress")

            run_command(batch_command)

            summarize_command = [
                sys.executable,
                "scripts/04_summarize_results.py",
                "--config",
                str(generated_configs[experiment_key].relative_to(PROJECT_ROOT)),
                "--results",
                str((experiment_dir / "metrics_per_image.csv").relative_to(PROJECT_ROOT)),
                "--output-dir",
                str(analysis_dir.relative_to(PROJECT_ROOT)),
            ]

            for dataset_value in args.dataset or []:
                summarize_command.extend(["--dataset", dataset_value])

            if args.no_plots:
                summarize_command.append("--no-plots")

            run_command(summarize_command)

    save_comparison_outputs(selected_keys)

    print("\nDone.")
    print(f"Generated configs : {CONFIG_DIR}")
    print(f"Experiment outputs: {OUTPUT_ROOT}")
    print(f"Comparison tables : {COMPARISON_DIR}")


if __name__ == "__main__":
    main()