"""
Run CA-APSRG experiments 1-6, copy Experiment 3 to default Streamlit output folders,
and package all results into one ZIP file.

Run from the project root:

    python scripts/05_run_all_experiments.py --clean

Outputs created:
- configs/experiments/exp1_recall_oriented.yaml
- configs/experiments/exp2_precision_oriented.yaml
- configs/experiments/exp3_balanced_main.yaml
- configs/experiments/exp4_static_morphology.yaml
- configs/experiments/exp5_no_skeleton_guard.yaml
- configs/experiments/exp6_no_small_component.yaml
- outputs/experiments_exp1_recall_oriented/
- outputs/analysis_exp1_recall_oriented/
- ...
- outputs/experiments_exp6_no_small_component/
- outputs/analysis_exp6_no_small_component/
- outputs/experiments/      -> copy of Experiment 3, for Streamlit Cloud
- outputs/analysis/         -> copy of Experiment 3, for Streamlit Cloud
- outputs/ca_apsrg_experiments_1_to_6.zip
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import zipfile
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_ROOT / "configs" / "default.yaml"
EXPERIMENT_CONFIG_DIR = PROJECT_ROOT / "configs" / "experiments"


EXP_ADAPTIVE_CONFIGS: dict[str, dict[str, Any]] = {
    "exp1_recall_oriented": {
        "label": "Experiment 1 - Recall-oriented CA-APSRG",
        "adaptive_morphology": {
            "enabled": True,
            "remove_small_objects": True,
            "fill_small_holes": True,
            "closing_enabled": True,
            "opening_enabled": False,
            "skeleton_guard_enabled": True,
            "small_component_area_low_density": 8,
            "small_component_area_normal": 14,
            "small_component_area_high_density": 24,
            "hole_area_low_density": 8,
            "hole_area_normal": 16,
            "hole_area_high_density": 32,
            "closing_kernel_low_density": 3,
            "closing_kernel_normal": 3,
            "closing_kernel_high_density": 5,
            "opening_kernel_low_density": 0,
            "opening_kernel_normal": 3,
            "opening_kernel_high_density": 3,
            "skeleton_restore_radius": 1,
            "skeleton_min_component_length": 6,
        },
    },
    "exp2_precision_oriented": {
        "label": "Experiment 2 - Precision-oriented CA-APSRG",
        "adaptive_morphology": {
            "enabled": True,
            "remove_small_objects": True,
            "fill_small_holes": False,
            "closing_enabled": False,
            "opening_enabled": True,
            "skeleton_guard_enabled": False,
            "small_component_area_low_density": 12,
            "small_component_area_normal": 24,
            "small_component_area_high_density": 36,
            "hole_area_low_density": 4,
            "hole_area_normal": 8,
            "hole_area_high_density": 12,
            "closing_kernel_low_density": 0,
            "closing_kernel_normal": 0,
            "closing_kernel_high_density": 0,
            "opening_kernel_low_density": 0,
            "opening_kernel_normal": 3,
            "opening_kernel_high_density": 3,
            "skeleton_restore_radius": 1,
            "skeleton_min_component_length": 6,
        },
    },
    "exp3_balanced_main": {
        "label": "Experiment 3 - Balanced CA-APSRG Main Result",
        "adaptive_morphology": {
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
        },
    },
    "exp4_static_morphology": {
        "label": "Experiment 4 - Static Morphology Ablation",
        "adaptive_morphology": {
            "enabled": True,
            "remove_small_objects": True,
            "fill_small_holes": False,
            "closing_enabled": False,
            "opening_enabled": False,
            "skeleton_guard_enabled": True,
            "small_component_area_low_density": 18,
            "small_component_area_normal": 18,
            "small_component_area_high_density": 18,
            "hole_area_low_density": 8,
            "hole_area_normal": 8,
            "hole_area_high_density": 8,
            "closing_kernel_low_density": 0,
            "closing_kernel_normal": 0,
            "closing_kernel_high_density": 0,
            "opening_kernel_low_density": 0,
            "opening_kernel_normal": 0,
            "opening_kernel_high_density": 0,
            "skeleton_restore_radius": 1,
            "skeleton_min_component_length": 6,
        },
    },
    "exp5_no_skeleton_guard": {
        "label": "Experiment 5 - No Skeleton Guard Ablation",
        "adaptive_morphology": {
            "enabled": True,
            "remove_small_objects": True,
            "fill_small_holes": False,
            "closing_enabled": False,
            "opening_enabled": False,
            "skeleton_guard_enabled": False,
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
        },
    },
    "exp6_no_small_component": {
        "label": "Experiment 6 - No Small Component Removal Ablation",
        "adaptive_morphology": {
            "enabled": True,
            "remove_small_objects": False,
            "fill_small_holes": False,
            "closing_enabled": False,
            "opening_enabled": False,
            "skeleton_guard_enabled": False,
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
        },
    },
}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def save_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(data, file, sort_keys=False, allow_unicode=True)


def build_experiment_config(base_config: dict[str, Any], experiment_key: str) -> dict[str, Any]:
    exp = EXP_ADAPTIVE_CONFIGS[experiment_key]
    cfg = deepcopy(base_config)

    cfg.setdefault("project", {})
    cfg["project"]["experiment_name"] = experiment_key
    cfg["project"]["experiment_label"] = exp["label"]

    cfg["adaptive_morphology"] = deepcopy(exp["adaptive_morphology"])
    cfg.setdefault("ca_apsrg", {})["enabled"] = True
    cfg.setdefault("ca_apsrg", {})["always_refine"] = True
    cfg.setdefault("experiment", {})["always_refine"] = True

    return cfg


def run_command(command: list[str]) -> None:
    print("\n$ " + " ".join(command))
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


def copytree_replace(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def should_skip_zip_path(path: Path, metrics_only: bool) -> bool:
    parts = set(path.parts)
    if "__pycache__" in parts or ".pytest_cache" in parts:
        return True
    if not metrics_only:
        return False
    # Keep CSV, Markdown, YAML, and plots; skip masks/overlays/comparison images.
    suffix = path.suffix.lower()
    return suffix not in {".csv", ".md", ".yaml", ".yml", ".png"} or (
        suffix == ".png" and "plots" not in parts
    )


def zip_results(zip_path: Path, metrics_only: bool = False) -> Path:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    if zip_path.exists():
        zip_path.unlink()

    include_roots = [
        PROJECT_ROOT / "configs" / "default.yaml",
        PROJECT_ROOT / "configs" / "experiments",
        PROJECT_ROOT / "outputs" / "experiments",
        PROJECT_ROOT / "outputs" / "analysis",
    ]

    for key in EXP_ADAPTIVE_CONFIGS:
        include_roots.extend(
            [
                PROJECT_ROOT / "outputs" / f"experiments_{key}",
                PROJECT_ROOT / "outputs" / f"analysis_{key}",
            ]
        )

    with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root in include_roots:
            if not root.exists():
                continue
            if root.is_file():
                zf.write(root, root.relative_to(PROJECT_ROOT))
                continue
            for path in root.rglob("*"):
                if path.is_file() and not should_skip_zip_path(path, metrics_only=metrics_only):
                    zf.write(path, path.relative_to(PROJECT_ROOT))

    return zip_path


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run and package CA-APSRG experiments 1-6.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--manifest", default="data/manifests/manifest.csv")
    parser.add_argument("--clean", action="store_true", help="Delete each experiment output folder before rerunning.")
    parser.add_argument("--skip-run", action="store_true", help="Only copy Experiment 3 to default folders and create ZIP from existing outputs.")
    parser.add_argument("--only", nargs="*", default=None, choices=list(EXP_ADAPTIVE_CONFIGS.keys()))
    parser.add_argument("--zip-output", default="outputs/ca_apsrg_experiments_1_to_6.zip")
    parser.add_argument("--metrics-only-zip", action="store_true", help="Exclude masks/overlays/comparison images from ZIP; keep CSV/MD/YAML/plots only.")
    parser.add_argument("--no-copy-exp3", action="store_true", help="Do not copy Experiment 3 to outputs/experiments and outputs/analysis.")
    return parser


def main() -> None:
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
    EXPERIMENT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    selected_keys = args.only if args.only else list(EXP_ADAPTIVE_CONFIGS.keys())
    generated_config_paths: dict[str, Path] = {}

    # Always generate all experiment YAML files, even if only some are run.
    for key in EXP_ADAPTIVE_CONFIGS:
        cfg = build_experiment_config(base_config, key)
        cfg_path = EXPERIMENT_CONFIG_DIR / f"{key}.yaml"
        save_yaml(cfg_path, cfg)
        generated_config_paths[key] = cfg_path

    if not args.skip_run:
        for key in selected_keys:
            print("\n" + "=" * 80)
            print(EXP_ADAPTIVE_CONFIGS[key]["label"])
            print("=" * 80)

            exp_output_dir = PROJECT_ROOT / "outputs" / f"experiments_{key}"
            analysis_output_dir = PROJECT_ROOT / "outputs" / f"analysis_{key}"

            if args.clean:
                clean_dir(exp_output_dir)
                clean_dir(analysis_output_dir)

            run_command(
                [
                    sys.executable,
                    "scripts/03_run_batch.py",
                    "--config",
                    str(generated_config_paths[key].relative_to(PROJECT_ROOT)),
                    "--manifest",
                    args.manifest,
                    "--output-dir",
                    str(exp_output_dir.relative_to(PROJECT_ROOT)),
                ]
            )
            run_command(
                [
                    sys.executable,
                    "scripts/04_summarize_results.py",
                    "--config",
                    str(generated_config_paths[key].relative_to(PROJECT_ROOT)),
                    "--results",
                    str((exp_output_dir / "metrics_per_image.csv").relative_to(PROJECT_ROOT)),
                    "--output-dir",
                    str(analysis_output_dir.relative_to(PROJECT_ROOT)),
                ]
            )

    if not args.no_copy_exp3:
        exp3_exp_dir = PROJECT_ROOT / "outputs" / "experiments_exp3_balanced_main"
        exp3_analysis_dir = PROJECT_ROOT / "outputs" / "analysis_exp3_balanced_main"
        if not exp3_exp_dir.is_dir() or not exp3_analysis_dir.is_dir():
            raise FileNotFoundError(
                "Experiment 3 output folders are missing. Run Experiment 3 first or do not use --skip-run."
            )

        print("\nCopying Experiment 3 to default Streamlit output folders...")
        copytree_replace(exp3_exp_dir, PROJECT_ROOT / "outputs" / "experiments")
        copytree_replace(exp3_analysis_dir, PROJECT_ROOT / "outputs" / "analysis")

        print("Restoring configs/default.yaml to Experiment 3 balanced main configuration...")
        shutil.copy2(generated_config_paths["exp3_balanced_main"], DEFAULT_CONFIG)

    zip_path = zip_results(PROJECT_ROOT / args.zip_output, metrics_only=args.metrics_only_zip)

    print("\nDone.")
    print(f"ZIP saved to: {zip_path}")
    print("Default Streamlit folders now point to Experiment 3 balanced main result:")
    print("- outputs/experiments")
    print("- outputs/analysis")
    print("Default YAML restored to Experiment 3:")
    print("- configs/default.yaml")


if __name__ == "__main__":
    main()
