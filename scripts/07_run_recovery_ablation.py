"""
Run recovery-ablation experiments for the CA-APSRG retinal-vessel pipeline.

This suite follows the recovery analysis after method ablation A01-A07:

R00: Legacy percentile-polling seeds + BFS (reference)
R01: Selective fuzzy-Harris, 35 point seeds, radius 0 + BFS
R02: Selective fuzzy-Harris, 77 seeds, radius 1 + BFS
R03: R02 + edge-delayed growing with region-mean acceptance
R04: R02 + edge-delayed growing with local-or-region acceptance
R05: R04 + hybrid edge priority
R06: R04 + APSRG process-context override

The script:
1. reads configs/default.yaml;
2. writes resolved recovery configs to configs/recovery_ablation/;
3. runs scripts/03_run_batch.py for each selected experiment;
4. runs scripts/04_summarize_results.py;
5. builds cross-experiment comparison tables in outputs/recovery_ablation/comparison/.

Run from the project root.

Full three-dataset run:

    python scripts/07_run_recovery_ablation.py \
        --dataset DRIVE --dataset STARE --dataset CHASEDB1 --clean

Quick DRIVE smoke test:

    python scripts/07_run_recovery_ablation.py \
        --dataset DRIVE --max-images 3 --clean --no-plots
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml
from scipy.stats import wilcoxon

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_ROOT / "configs" / "default.yaml"
CONFIG_DIR = PROJECT_ROOT / "configs" / "recovery_ablation"
OUTPUT_ROOT = PROJECT_ROOT / "outputs" / "recovery_ablation"
COMPARISON_DIR = OUTPUT_ROOT / "comparison"

REFERENCE_EXPERIMENT = "r00_legacy_polling_bfs"
BOOTSTRAP_ITERATIONS = 5000
BOOTSTRAP_CONFIDENCE = 0.95
BOOTSTRAP_RANDOM_SEED = 42
PAIR_EPSILON = 1e-12

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

BALANCED_MORPHOLOGY: dict[str, Any] = {
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

PROCESS_CONTEXT_DISABLED: dict[str, Any] = {
    "enabled": False,
    "can_trigger_refinement": False,
    "can_override_refinement_level": False,
}

PROCESS_CONTEXT_RECORD_ONLY: dict[str, Any] = {
    "enabled": True,
    "can_trigger_refinement": True,
    "can_override_refinement_level": False,
}

PROCESS_CONTEXT_OVERRIDE: dict[str, Any] = {
    "enabled": True,
    "can_trigger_refinement": True,
    "can_override_refinement_level": True,
}


def selective_seed_overrides(
    *,
    target_seed_count: int,
    seed_dilate_radius: int,
) -> dict[str, Any]:
    """Return the controlled selective fuzzy-Harris parameter block."""
    return {
        "enabled": True,
        "target_seed_count": int(target_seed_count),
        "min_seed_count": 7,
        "max_seed_count": 77,
        "fuzzy_support_radius": 2,
        "relaxed_support_radius": 5,
        "min_seed_distance": 3,
        "fuzzy_weight": 0.35,
        "harris_weight": 0.40,
        "vesselness_weight": 0.25,
        "use_candidate_constraint": True,
        "use_fov_constraint": True,
        "allow_relaxed_harris_fallback": True,
        "allow_fuzzy_fallback": True,
        "seed_dilate_radius": int(seed_dilate_radius),
    }


def edge_growing_overrides(
    *,
    priority_mode: str,
    acceptance_mode: str,
) -> dict[str, Any]:
    """Return the controlled edge-delayed region-growing parameter block."""
    return {
        "enabled": True,
        "priority_mode": str(priority_mode),
        "fuzzy_distance_scale": 0.4,
        "connected_edge_wd": 0.4,
        "edge_floor": 0.05,
        "edge_weight": 0.35,
        "acceptance_mode": str(acceptance_mode),
        "region_mean_tolerance_multiplier": 2.0,
        "max_fuzzy_distance": 1.0,
        "recompute_priority": True,
        "priority_tolerance": 0.000001,
        "record_growth_order": True,
    }


EXPERIMENTS: dict[str, dict[str, Any]] = {
    "r00_legacy_polling_bfs": {
        "label": "R00 - Legacy percentile-polling seeds with BFS",
        "description": (
            "Recovery reference using the previous percentile/local-polling "
            "seed strategy and conventional BFS region growing."
        ),
        "overrides": {
            "apsrg_baseline": {
                "seed_selection_method": "percentile_polling",
                "region_growing_mode": "bfs",
            },
            "ca_apsrg": {
                "process_context": PROCESS_CONTEXT_DISABLED,
            },
        },
    },
    "r01_selective35_bfs": {
        "label": "R01 - Selective fuzzy-Harris, 35 seeds, radius 0, BFS",
        "description": (
            "Reproduces the restrictive selective seed setting while using "
            "BFS, isolating the effect of sparse point seeds."
        ),
        "overrides": {
            "apsrg_baseline": {
                "seed_selection_method": "selective_fuzzy_harris",
                "region_growing_mode": "bfs",
                "hybrid_seed": selective_seed_overrides(
                    target_seed_count=35,
                    seed_dilate_radius=0,
                ),
            },
            "ca_apsrg": {
                "process_context": PROCESS_CONTEXT_DISABLED,
            },
        },
    },
    "r02_selective77_radius1_bfs": {
        "label": "R02 - Selective fuzzy-Harris, 77 seeds, radius 1, BFS",
        "description": (
            "Tests recovery of vessel coverage by increasing selected seed "
            "points and dilating each seed before BFS growth."
        ),
        "overrides": {
            "apsrg_baseline": {
                "seed_selection_method": "selective_fuzzy_harris",
                "region_growing_mode": "bfs",
                "hybrid_seed": selective_seed_overrides(
                    target_seed_count=77,
                    seed_dilate_radius=1,
                ),
            },
            "ca_apsrg": {
                "process_context": PROCESS_CONTEXT_DISABLED,
            },
        },
    },
    "r03_edge_region_mean": {
        "label": "R03 - Selective 77/radius 1 with region-mean edge growing",
        "description": (
            "Controls the original restrictive edge-delayed acceptance gate "
            "after seed coverage has been recovered."
        ),
        "overrides": {
            "apsrg_baseline": {
                "seed_selection_method": "selective_fuzzy_harris",
                "region_growing_mode": "edge_delayed",
                "max_intensity_difference": 18,
                "hybrid_seed": selective_seed_overrides(
                    target_seed_count=77,
                    seed_dilate_radius=1,
                ),
                "edge_delayed_region_growing": edge_growing_overrides(
                    priority_mode="kang_product",
                    acceptance_mode="region_mean",
                ),
            },
            "ca_apsrg": {
                "process_context": PROCESS_CONTEXT_DISABLED,
            },
        },
    },
    "r04_local_or_region": {
        "label": "R04 - Selective 77/radius 1 with local-or-region acceptance",
        "description": (
            "Tests gradual local-path consistency while retaining a tolerant "
            "region-mean alternative under Kang-product priority."
        ),
        "overrides": {
            "apsrg_baseline": {
                "seed_selection_method": "selective_fuzzy_harris",
                "region_growing_mode": "edge_delayed",
                "max_intensity_difference": 18,
                "hybrid_seed": selective_seed_overrides(
                    target_seed_count=77,
                    seed_dilate_radius=1,
                ),
                "edge_delayed_region_growing": edge_growing_overrides(
                    priority_mode="kang_product",
                    acceptance_mode="local_or_region",
                ),
            },
            "ca_apsrg": {
                "process_context": PROCESS_CONTEXT_RECORD_ONLY,
            },
        },
    },
    "r05_local_or_region_hybrid_priority": {
        "label": "R05 - R04 with hybrid edge priority",
        "description": (
            "Keeps the recovered seed and acceptance settings from R04 while "
            "testing the hybrid fuzzy-distance/edge priority formulation."
        ),
        "overrides": {
            "apsrg_baseline": {
                "seed_selection_method": "selective_fuzzy_harris",
                "region_growing_mode": "edge_delayed",
                "max_intensity_difference": 18,
                "hybrid_seed": selective_seed_overrides(
                    target_seed_count=77,
                    seed_dilate_radius=1,
                ),
                "edge_delayed_region_growing": edge_growing_overrides(
                    priority_mode="hybrid",
                    acceptance_mode="local_or_region",
                ),
            },
            "ca_apsrg": {
                "process_context": PROCESS_CONTEXT_RECORD_ONLY,
            },
        },
    },
    "r06_local_or_region_process_override": {
        "label": "R06 - R04 with process-context refinement override",
        "description": (
            "Tests the process-context contribution against R04 without "
            "changing seed selection, acceptance, or priority mode."
        ),
        "overrides": {
            "apsrg_baseline": {
                "seed_selection_method": "selective_fuzzy_harris",
                "region_growing_mode": "edge_delayed",
                "max_intensity_difference": 18,
                "hybrid_seed": selective_seed_overrides(
                    target_seed_count=77,
                    seed_dilate_radius=1,
                ),
                "edge_delayed_region_growing": edge_growing_overrides(
                    priority_mode="kang_product",
                    acceptance_mode="local_or_region",
                ),
            },
            "ca_apsrg": {
                "process_context": PROCESS_CONTEXT_OVERRIDE,
            },
        },
    },
}


def load_yaml(path: Path) -> dict[str, Any]:
    """Read one YAML file into a dictionary."""
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
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            deep_update(base[key], value)
        else:
            base[key] = deepcopy(value)

    return base


def build_experiment_config(
    base_config: dict[str, Any],
    experiment_key: str,
) -> dict[str, Any]:
    """Build one complete recovery-experiment YAML dictionary."""
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

    # Fix morphology across the recovery study, so only the intended APSRG
    # and process-context factors vary.
    adaptive = config.setdefault("adaptive_morphology", {})
    adaptive.update(deepcopy(BALANCED_MORPHOLOGY))

    return config


def run_command(command: list[str]) -> None:
    """Run one subprocess from the project root and fail on errors."""
    print("\n$ " + " ".join(command))
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def clean_directory(path: Path) -> None:
    """Delete a directory when it exists."""
    if path.exists():
        shutil.rmtree(path)


def detect_id_columns(frame: pd.DataFrame) -> list[str]:
    """Return stable identifier columns for paired comparisons."""
    candidates = ["dataset", "image_id", "image_path"]
    selected = [column for column in candidates if column in frame.columns]

    if not selected:
        raise ValueError(
            "Could not find dataset/image identifier columns in metrics file."
        )

    return selected


def collect_long_results(experiment_keys: list[str]) -> pd.DataFrame:
    """Collect APSRG and CA-APSRG metrics from completed experiments."""
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

                subset = frame[id_columns + [column]].copy()
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
    """Build descriptive summary by experiment, dataset, method, and metric."""
    if long_results.empty:
        return pd.DataFrame()

    group_columns = [
        "experiment",
        "experiment_label",
        "dataset",
        "output_method",
        "metric",
    ]

    return (
        long_results.groupby(group_columns, dropna=False)["value"]
        .agg(["count", "mean", "std", "median", "min", "max"])
        .reset_index()
        .rename(columns={"count": "n_images"})
    )


def build_article_table(summary: pd.DataFrame) -> pd.DataFrame:
    """Build a compact wide table for manuscript inspection."""
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


def _paired_test_and_interval(
    deltas: pd.Series,
    *,
    confidence: float = BOOTSTRAP_CONFIDENCE,
    n_bootstrap: int = BOOTSTRAP_ITERATIONS,
    random_seed: int = BOOTSTRAP_RANDOM_SEED,
) -> dict[str, Any]:
    """Return paired win/tie/loss, Wilcoxon, and bootstrap mean CI."""
    values = pd.to_numeric(deltas, errors="coerce").dropna().to_numpy(dtype=float)
    n_pairs = int(values.size)

    if n_pairs == 0:
        return {
            "n_pairs": 0,
            "mean_delta": np.nan,
            "median_delta": np.nan,
            "std_delta": np.nan,
            "wins": 0,
            "ties": 0,
            "losses": 0,
            "wilcoxon_statistic": np.nan,
            "wilcoxon_p_value": np.nan,
            "bootstrap_mean_ci_low": np.nan,
            "bootstrap_mean_ci_high": np.nan,
        }

    wins = int(np.sum(values > PAIR_EPSILON))
    ties = int(np.sum(np.abs(values) <= PAIR_EPSILON))
    losses = int(np.sum(values < -PAIR_EPSILON))

    if np.all(np.abs(values) <= PAIR_EPSILON):
        wilcoxon_statistic = 0.0
        wilcoxon_p_value = 1.0
    else:
        try:
            test = wilcoxon(
                values,
                zero_method="wilcox",
                correction=False,
                alternative="two-sided",
                mode="auto",
            )
            wilcoxon_statistic = float(test.statistic)
            wilcoxon_p_value = float(test.pvalue)
        except ValueError:
            wilcoxon_statistic = np.nan
            wilcoxon_p_value = np.nan

    rng = np.random.default_rng(int(random_seed))
    sample_indices = rng.integers(
        0,
        n_pairs,
        size=(max(int(n_bootstrap), 1), n_pairs),
    )
    bootstrap_means = values[sample_indices].mean(axis=1)
    alpha = 1.0 - float(confidence)
    ci_low = float(np.quantile(bootstrap_means, alpha / 2.0))
    ci_high = float(np.quantile(bootstrap_means, 1.0 - alpha / 2.0))

    return {
        "n_pairs": n_pairs,
        "mean_delta": float(np.mean(values)),
        "median_delta": float(np.median(values)),
        "std_delta": float(np.std(values, ddof=1)) if n_pairs > 1 else 0.0,
        "wins": wins,
        "ties": ties,
        "losses": losses,
        "wilcoxon_statistic": wilcoxon_statistic,
        "wilcoxon_p_value": wilcoxon_p_value,
        "bootstrap_mean_ci_low": ci_low,
        "bootstrap_mean_ci_high": ci_high,
    }


def _summarize_paired_deltas(
    frame: pd.DataFrame,
    group_columns: list[str],
) -> pd.DataFrame:
    """Summarize paired deltas for each requested group."""
    if frame.empty:
        return pd.DataFrame()

    records: list[dict[str, Any]] = []
    grouped = frame.groupby(group_columns, dropna=False, sort=False)

    for group_values, group in grouped:
        if not isinstance(group_values, tuple):
            group_values = (group_values,)

        record = dict(zip(group_columns, group_values))
        seed_offset = sum(ord(ch) for ch in "|".join(map(str, group_values)))
        record.update(
            _paired_test_and_interval(
                group["delta"],
                random_seed=BOOTSTRAP_RANDOM_SEED + seed_offset,
            )
        )
        records.append(record)

    return pd.DataFrame.from_records(records)


def build_delta_vs_reference(long_results: pd.DataFrame) -> pd.DataFrame:
    """Build paired deltas and statistics against R00."""
    if long_results.empty:
        return pd.DataFrame()

    reference = long_results[
        long_results["experiment"] == REFERENCE_EXPERIMENT
    ].copy()

    if reference.empty:
        print("Warning: R00 reference unavailable; delta table skipped.")
        return pd.DataFrame()

    id_columns = [
        column
        for column in ["dataset", "image_id", "image_path"]
        if column in long_results.columns
    ]
    merge_keys = id_columns + ["output_method", "metric"]

    reference = reference[merge_keys + ["value"]].rename(
        columns={"value": "reference_value"}
    )

    comparison = long_results[
        long_results["experiment"] != REFERENCE_EXPERIMENT
    ].merge(reference, on=merge_keys, how="inner")

    if comparison.empty:
        return pd.DataFrame()

    comparison["delta"] = comparison["value"] - comparison["reference_value"]

    return _summarize_paired_deltas(
        comparison,
        [
            "experiment",
            "experiment_label",
            "dataset",
            "output_method",
            "metric",
        ],
    )


def build_stage_delta(
    long_results: pd.DataFrame,
    left_experiment: str,
    right_experiment: str,
) -> pd.DataFrame:
    """Build paired statistics for one planned recovery comparison."""
    if long_results.empty:
        return pd.DataFrame()

    id_columns = [
        column
        for column in ["dataset", "image_id", "image_path"]
        if column in long_results.columns
    ]
    merge_keys = id_columns + ["output_method", "metric"]

    left = long_results[
        long_results["experiment"] == left_experiment
    ][merge_keys + ["value"]].rename(columns={"value": "left_value"})

    right = long_results[
        long_results["experiment"] == right_experiment
    ][merge_keys + ["value"]].rename(columns={"value": "right_value"})

    paired = right.merge(left, on=merge_keys, how="inner")
    if paired.empty:
        return pd.DataFrame()

    paired["delta"] = paired["right_value"] - paired["left_value"]
    paired["comparison"] = f"{left_experiment}_to_{right_experiment}"
    paired["left_experiment"] = left_experiment
    paired["right_experiment"] = right_experiment

    return _summarize_paired_deltas(
        paired,
        [
            "comparison",
            "left_experiment",
            "right_experiment",
            "dataset",
            "output_method",
            "metric",
        ],
    )


def build_planned_stage_deltas(long_results: pd.DataFrame) -> pd.DataFrame:
    """Build comparisons that isolate each recovery contribution."""
    comparisons = [
        ("r01_selective35_bfs", "r02_selective77_radius1_bfs"),
        ("r02_selective77_radius1_bfs", "r03_edge_region_mean"),
        ("r03_edge_region_mean", "r04_local_or_region"),
        ("r04_local_or_region", "r05_local_or_region_hybrid_priority"),
        ("r04_local_or_region", "r06_local_or_region_process_override"),
    ]

    frames = [
        build_stage_delta(long_results, left, right)
        for left, right in comparisons
    ]
    frames = [frame for frame in frames if not frame.empty]

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)


def completed_experiment_keys() -> list[str]:
    """Return all recovery experiments with a completed metrics CSV."""
    return [
        experiment_key
        for experiment_key in EXPERIMENTS
        if (
            OUTPUT_ROOT
            / f"experiments_{experiment_key}"
            / "metrics_per_image.csv"
        ).is_file()
    ]


def save_comparison_outputs(experiment_keys: list[str] | None = None) -> None:
    """Create comparison CSV files from every completed experiment."""
    COMPARISON_DIR.mkdir(parents=True, exist_ok=True)

    keys = experiment_keys or completed_experiment_keys()
    if not keys:
        print("No completed recovery experiments found.")
        return

    long_results = collect_long_results(keys)
    if long_results.empty:
        print("No completed metrics found for recovery comparison.")
        return

    summary = build_summary(long_results)
    article_table = build_article_table(summary)
    delta_reference = build_delta_vs_reference(long_results)
    stage_deltas = build_planned_stage_deltas(long_results)

    outputs = {
        "recovery_per_image_long.csv": long_results,
        "recovery_summary_long.csv": summary,
        "recovery_article_table.csv": article_table,
        "recovery_delta_vs_r00.csv": delta_reference,
        "recovery_stage_deltas.csv": stage_deltas,
    }

    for filename, frame in outputs.items():
        frame.to_csv(COMPARISON_DIR / filename, index=False)

    print("\nRecovery comparison saved:")
    print(f"Completed experiments: {', '.join(keys)}")
    for filename in outputs:
        print(f"- {COMPARISON_DIR / filename}")


def build_arg_parser() -> argparse.ArgumentParser:
    """Create command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run CA-APSRG recovery-ablation experiments R00-R06.",
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
        help="Maximum manifest rows per experiment after dataset filtering.",
    )
    parser.add_argument(
        "--only",
        nargs="*",
        choices=list(EXPERIMENTS.keys()),
        default=None,
        help="Run only selected recovery experiment keys.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete selected experiment and analysis folders before running.",
    )
    parser.add_argument(
        "--skip-run",
        action="store_true",
        help="Only generate configs and rebuild comparison tables.",
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
    """Run the selected recovery-ablation suite."""
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

    # Always generate every YAML for transparency and reproducibility.
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

    save_comparison_outputs(completed_experiment_keys())

    print("\nDone.")
    print(f"Generated configs : {CONFIG_DIR}")
    print(f"Experiment outputs: {OUTPUT_ROOT}")
    print(f"Comparison tables : {COMPARISON_DIR}")


if __name__ == "__main__":
    main()