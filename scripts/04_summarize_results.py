"""
Script No. 16: Summarize and visualize CA-APSRG experiment results.

Typical use after running batch experiment:

    python scripts/04_summarize_results.py

or explicitly:

    python scripts/04_summarize_results.py \
        --results outputs/experiments/metrics_per_image.csv \
        --output-dir outputs/analysis

Run only selected datasets:

    python scripts/04_summarize_results.py --dataset DRIVE
    python scripts/04_summarize_results.py --dataset DRIVE,STARE,CHASEDB1

This script creates CSV tables, a Markdown report, and optional charts for:
- APSRG baseline vs CA-APSRG mean/std metrics,
- CA-APSRG minus APSRG improvement,
- win/loss counts,
- best improvement cases,
- worst segmentation cases.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


METRIC_NAMES = [
    "accuracy",
    "precision",
    "recall",
    "specificity",
    "f1_score",
    "iou",
    "false_positive_rate",
    "false_negative_rate",
    "balanced_accuracy",
    "dice",
]

PREFERRED_REPORT_METRICS = ["precision", "recall", "f1_score", "iou", "accuracy"]

METHOD_PREFIXES = {
    "baseline": "APSRG Baseline",
    "ca_apsrg": "CA-APSRG",
}


def load_yaml_config(config_path: str | Path) -> dict[str, Any]:
    config_path = Path(config_path)
    if not config_path.is_file():
        return {}

    with config_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    return data or {}


def get_nested(config: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = config
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def resolve_project_path(path_value: str | Path | None, default: str | Path | None = None) -> Optional[Path]:
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


def parse_filters(values: list[str] | None) -> list[str]:
    if not values:
        return []

    parsed: list[str] = []
    for value in values:
        parsed.extend([item.strip() for item in str(value).split(",") if item.strip()])
    return parsed


def ensure_dir(path: str | Path) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def available_metrics(df: pd.DataFrame) -> list[str]:
    metrics: list[str] = []
    for metric in METRIC_NAMES:
        if f"baseline_{metric}" in df.columns and f"ca_apsrg_{metric}" in df.columns:
            metrics.append(metric)
    return metrics


def filter_results(df: pd.DataFrame, datasets: list[str] | None = None) -> pd.DataFrame:
    if not datasets:
        return df.reset_index(drop=True)

    dataset_set = {str(dataset).strip().lower() for dataset in datasets}
    filtered = df[df["dataset"].astype(str).str.lower().isin(dataset_set)].copy()
    return filtered.reset_index(drop=True)


def build_long_metrics(df: pd.DataFrame) -> pd.DataFrame:
    metrics = available_metrics(df)
    long_rows: list[dict[str, Any]] = []

    for _, row in df.iterrows():
        for prefix, method_name in METHOD_PREFIXES.items():
            item: dict[str, Any] = {
                "dataset": row.get("dataset", ""),
                "image_id": row.get("image_id", ""),
                "method": method_name,
            }
            for metric in metrics:
                item[metric] = row.get(f"{prefix}_{metric}", np.nan)
            long_rows.append(item)

    return pd.DataFrame(long_rows)


def summarize_by_dataset_method(long_df: pd.DataFrame) -> pd.DataFrame:
    if long_df.empty:
        return pd.DataFrame()

    metrics = [metric for metric in METRIC_NAMES if metric in long_df.columns]
    summary = long_df.groupby(["dataset", "method"], dropna=False)[metrics].agg(["mean", "std", "min", "max"])
    summary.columns = [f"{metric}_{stat}" for metric, stat in summary.columns]
    summary = summary.reset_index()

    count_df = long_df.groupby(["dataset", "method"], dropna=False).size().reset_index(name="n_images")
    return count_df.merge(summary, on=["dataset", "method"], how="left")


def build_improvement_table(df: pd.DataFrame) -> pd.DataFrame:
    metrics = available_metrics(df)
    keep_cols = [col for col in ["dataset", "image_id", "image_path", "mask_path", "fov_path", "comparison_path"] if col in df.columns]
    improvement = df[keep_cols].copy()

    for metric in metrics:
        improvement[f"baseline_{metric}"] = pd.to_numeric(df[f"baseline_{metric}"], errors="coerce")
        improvement[f"ca_apsrg_{metric}"] = pd.to_numeric(df[f"ca_apsrg_{metric}"], errors="coerce")
        improvement[f"delta_{metric}"] = improvement[f"ca_apsrg_{metric}"] - improvement[f"baseline_{metric}"]

    if "ca_apsrg_applied" in df.columns:
        improvement["ca_apsrg_applied"] = df["ca_apsrg_applied"]

    for col in df.columns:
        if col.startswith("context_") or col.startswith("selected_"):
            improvement[col] = df[col]

    return improvement


def summarize_improvements(improvement: pd.DataFrame, epsilon: float = 1e-12) -> pd.DataFrame:
    if improvement.empty:
        return pd.DataFrame()

    delta_cols = [col for col in improvement.columns if col.startswith("delta_")]
    if not delta_cols:
        return pd.DataFrame()

    grouped = improvement.groupby("dataset", dropna=False)
    summary = grouped[delta_cols].agg(["mean", "std", "median", "min", "max"])
    summary.columns = [f"{metric}_{stat}" for metric, stat in summary.columns]
    summary = summary.reset_index()

    count_df = grouped.size().reset_index(name="n_images")
    summary = count_df.merge(summary, on="dataset", how="left")

    for metric in ["precision", "recall", "f1_score", "iou", "accuracy"]:
        delta_col = f"delta_{metric}"
        if delta_col in improvement.columns:
            win_loss = grouped[delta_col].agg(
                n_improved=lambda s: int((s > epsilon).sum()),
                n_equal=lambda s: int((s.abs() <= epsilon).sum()),
                n_decreased=lambda s: int((s < -epsilon).sum()),
            ).reset_index()
            win_loss = win_loss.rename(
                columns={
                    "n_improved": f"{metric}_n_improved",
                    "n_equal": f"{metric}_n_equal",
                    "n_decreased": f"{metric}_n_decreased",
                }
            )
            summary = summary.merge(win_loss, on="dataset", how="left")

    return summary


def build_article_table(summary: pd.DataFrame) -> pd.DataFrame:
    if summary.empty:
        return pd.DataFrame()

    rows: list[dict[str, Any]] = []
    for _, row in summary.iterrows():
        item: dict[str, Any] = {
            "dataset": row.get("dataset", ""),
            "method": row.get("method", ""),
            "n_images": int(row.get("n_images", 0)),
        }
        for metric in PREFERRED_REPORT_METRICS:
            mean_col = f"{metric}_mean"
            std_col = f"{metric}_std"
            if mean_col in summary.columns:
                mean_value = row.get(mean_col, np.nan)
                std_value = row.get(std_col, np.nan)
                if pd.isna(std_value):
                    item[metric] = f"{mean_value:.4f}"
                else:
                    item[metric] = f"{mean_value:.4f} ± {std_value:.4f}"
        rows.append(item)

    return pd.DataFrame(rows)


def select_case_tables(improvement: pd.DataFrame, top_k: int = 10) -> dict[str, pd.DataFrame]:
    tables: dict[str, pd.DataFrame] = {}
    base_cols = [col for col in ["dataset", "image_id", "comparison_path"] if col in improvement.columns]

    if "delta_f1_score" in improvement.columns:
        cols = base_cols + [
            col for col in ["baseline_f1_score", "ca_apsrg_f1_score", "delta_f1_score", "delta_precision", "delta_recall"]
            if col in improvement.columns
        ]
        tables["best_f1_improvements"] = improvement.sort_values("delta_f1_score", ascending=False)[cols].head(top_k)
        tables["worst_f1_drops"] = improvement.sort_values("delta_f1_score", ascending=True)[cols].head(top_k)
        tables["worst_ca_f1_cases"] = improvement.sort_values("ca_apsrg_f1_score", ascending=True)[cols].head(top_k)

    if "delta_precision" in improvement.columns:
        cols = base_cols + [
            col for col in ["baseline_precision", "ca_apsrg_precision", "delta_precision", "delta_recall", "delta_f1_score"]
            if col in improvement.columns
        ]
        tables["best_precision_improvements"] = improvement.sort_values("delta_precision", ascending=False)[cols].head(top_k)
        tables["worst_precision_drops"] = improvement.sort_values("delta_precision", ascending=True)[cols].head(top_k)

    return tables


def _save_bar_chart(df: pd.DataFrame, *, metric: str, output_path: Path) -> None:
    mean_col = f"{metric}_mean"
    if df.empty or mean_col not in df.columns:
        return

    pivot = df.pivot(index="dataset", columns="method", values=mean_col)
    ax = pivot.plot(kind="bar", figsize=(9, 5))
    ax.set_title(f"{metric.replace('_', ' ').title()} by Dataset and Method")
    ax.set_xlabel("Dataset")
    ax.set_ylabel(metric.replace("_", " ").title())
    ax.set_ylim(0, 1)
    ax.legend(title="Method")
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()


def _save_delta_chart(improvement_summary: pd.DataFrame, *, metric: str, output_path: Path) -> None:
    mean_col = f"delta_{metric}_mean"
    if improvement_summary.empty or mean_col not in improvement_summary.columns:
        return

    plot_df = improvement_summary.set_index("dataset")[[mean_col]]
    ax = plot_df.plot(kind="bar", figsize=(8, 5), legend=False)
    ax.axhline(0, linewidth=1)
    ax.set_title(f"Average Δ {metric.replace('_', ' ').title()} (CA-APSRG - APSRG)")
    ax.set_xlabel("Dataset")
    ax.set_ylabel(f"Delta {metric.replace('_', ' ').title()}")
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()


def save_plots(summary: pd.DataFrame, improvement_summary: pd.DataFrame, output_dir: Path) -> list[Path]:
    plot_dir = ensure_dir(output_dir / "plots")
    saved: list[Path] = []

    for metric in ["precision", "recall", "f1_score", "iou", "accuracy"]:
        path = plot_dir / f"{metric}_by_dataset_method.png"
        _save_bar_chart(summary, metric=metric, output_path=path)
        if path.is_file():
            saved.append(path)

    for metric in ["precision", "recall", "f1_score", "iou"]:
        path = plot_dir / f"delta_{metric}_by_dataset.png"
        _save_delta_chart(improvement_summary, metric=metric, output_path=path)
        if path.is_file():
            saved.append(path)

    return saved


def dataframe_to_markdown(df: pd.DataFrame, max_rows: int = 20) -> str:
    if df.empty:
        return "_No data available._"

    display_df = df.head(max_rows).copy()
    try:
        return display_df.to_markdown(index=False)
    except Exception:
        return "```text\n" + display_df.to_string(index=False) + "\n```"


def write_markdown_report(
    *,
    output_path: Path,
    source_results_path: Path,
    summary: pd.DataFrame,
    improvement_summary: pd.DataFrame,
    article_table: pd.DataFrame,
    case_tables: dict[str, pd.DataFrame],
    saved_plots: list[Path],
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# CA-APSRG Experiment Summary")
    lines.append("")
    lines.append(f"Source results file: `{source_results_path}`")
    lines.append("")

    lines.append("## Article-style Summary Table")
    lines.append("")
    lines.append(dataframe_to_markdown(article_table, max_rows=50))
    lines.append("")

    lines.append("## Mean Improvement by Dataset")
    lines.append("")
    improvement_cols = [
        col for col in [
            "dataset",
            "n_images",
            "delta_precision_mean",
            "delta_recall_mean",
            "delta_f1_score_mean",
            "delta_iou_mean",
            "f1_score_n_improved",
            "f1_score_n_equal",
            "f1_score_n_decreased",
        ]
        if col in improvement_summary.columns
    ]
    lines.append(dataframe_to_markdown(improvement_summary[improvement_cols] if improvement_cols else improvement_summary, max_rows=50))
    lines.append("")

    lines.append("## Full Summary by Dataset and Method")
    lines.append("")
    summary_cols = [
        col for col in [
            "dataset",
            "method",
            "n_images",
            "precision_mean",
            "precision_std",
            "recall_mean",
            "recall_std",
            "f1_score_mean",
            "f1_score_std",
            "iou_mean",
            "iou_std",
            "accuracy_mean",
            "accuracy_std",
        ]
        if col in summary.columns
    ]
    lines.append(dataframe_to_markdown(summary[summary_cols] if summary_cols else summary, max_rows=100))
    lines.append("")

    for name, table in case_tables.items():
        lines.append(f"## {name.replace('_', ' ').title()}")
        lines.append("")
        lines.append(dataframe_to_markdown(table, max_rows=20))
        lines.append("")

    if saved_plots:
        lines.append("## Saved Plots")
        lines.append("")
        for path in saved_plots:
            lines.append(f"- `{path}`")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Summarize CA-APSRG batch experiment metrics.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--results", default=None)
    parser.add_argument("--output-dir", default="outputs/analysis")
    parser.add_argument("--dataset", action="append", default=None)
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--no-plots", action="store_true")
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    config_path = resolve_project_path(args.config, "configs/default.yaml")
    if config_path is None:
        raise ValueError("Config path could not be resolved.")

    config = load_yaml_config(config_path)

    results_from_config = (
        get_nested(config, "outputs", "metrics_per_image_csv")
        or str(Path(get_nested(config, "paths", "experiments_dir", default="outputs/experiments")) / "metrics_per_image.csv")
    )

    results_path = resolve_project_path(args.results, results_from_config)
    output_dir = resolve_project_path(args.output_dir, "outputs/analysis")

    if results_path is None:
        raise ValueError("Results path could not be resolved.")
    if output_dir is None:
        raise ValueError("Output directory could not be resolved.")
    if not results_path.is_file():
        raise FileNotFoundError(
            f"Results file not found: {results_path}\n"
            "Run script No. 15 first: python scripts/03_run_batch.py"
        )

    output_dir = ensure_dir(output_dir)

    results = pd.read_csv(results_path)
    datasets = parse_filters(args.dataset)
    results = filter_results(results, datasets=datasets)

    if results.empty:
        raise ValueError("No result rows available after filtering.")

    long_metrics = build_long_metrics(results)
    summary = summarize_by_dataset_method(long_metrics)
    improvement = build_improvement_table(results)
    improvement_summary = summarize_improvements(improvement)
    article_table = build_article_table(summary)
    case_tables = select_case_tables(improvement, top_k=int(args.top_k))

    long_metrics_path = output_dir / "long_metrics.csv"
    summary_path = output_dir / "summary_by_dataset_method.csv"
    improvement_path = output_dir / "improvement_per_image.csv"
    improvement_summary_path = output_dir / "improvement_by_dataset.csv"
    article_table_path = output_dir / "article_table_mean_std.csv"

    long_metrics.to_csv(long_metrics_path, index=False)
    summary.to_csv(summary_path, index=False)
    improvement.to_csv(improvement_path, index=False)
    improvement_summary.to_csv(improvement_summary_path, index=False)
    article_table.to_csv(article_table_path, index=False)

    case_dir = ensure_dir(output_dir / "case_tables")
    case_paths: list[Path] = []
    for name, table in case_tables.items():
        path = case_dir / f"{name}.csv"
        table.to_csv(path, index=False)
        case_paths.append(path)

    saved_plots: list[Path] = []
    if not args.no_plots:
        saved_plots = save_plots(summary, improvement_summary, output_dir)

    report_path = write_markdown_report(
        output_path=output_dir / "results_summary.md",
        source_results_path=results_path,
        summary=summary,
        improvement_summary=improvement_summary,
        article_table=article_table,
        case_tables=case_tables,
        saved_plots=saved_plots,
    )

    print("=" * 72)
    print("CA-APSRG Result Summarizer")
    print("=" * 72)
    print(f"Project root     : {PROJECT_ROOT}")
    print(f"Config file      : {config_path}")
    print(f"Results file     : {results_path}")
    print(f"Output directory : {output_dir}")
    print(f"Dataset filter   : {datasets if datasets else 'all'}")
    print("=" * 72)

    print("\nSaved CSV files:")
    print(f"- Long metrics              : {long_metrics_path}")
    print(f"- Summary by dataset/method : {summary_path}")
    print(f"- Improvement per image     : {improvement_path}")
    print(f"- Improvement by dataset    : {improvement_summary_path}")
    print(f"- Article table             : {article_table_path}")

    if case_paths:
        print("\nSaved case tables:")
        for path in case_paths:
            print(f"- {path}")

    if saved_plots:
        print("\nSaved plots:")
        for path in saved_plots:
            print(f"- {path}")

    print(f"\nMarkdown report: {report_path}")

    print("\nArticle-style table preview:")
    print(article_table.to_string(index=False))

    improvement_cols = [
        col for col in [
            "dataset",
            "n_images",
            "delta_precision_mean",
            "delta_recall_mean",
            "delta_f1_score_mean",
            "delta_iou_mean",
        ]
        if col in improvement_summary.columns
    ]
    if improvement_cols:
        print("\nImprovement preview:")
        print(improvement_summary[improvement_cols].to_string(index=False))

    print("\nDone.")


if __name__ == "__main__":
    main()