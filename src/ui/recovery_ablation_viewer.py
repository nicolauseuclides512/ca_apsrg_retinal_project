"""Streamlit viewer for CA-APSRG recovery ablation experiments R00-R06."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st


CORE_METRICS = ["precision", "recall", "f1_score", "iou", "accuracy"]
RECOVERY_ORDER = [
    "r00_legacy_polling_bfs",
    "r01_selective35_bfs",
    "r02_selective77_radius1_bfs",
    "r03_edge_region_mean",
    "r04_local_or_region",
    "r05_local_or_region_hybrid_priority",
    "r06_local_or_region_process_override",
]
RECOVERY_LABELS = {
    "r00_legacy_polling_bfs": "R00 - Legacy percentile-polling + BFS",
    "r01_selective35_bfs": "R01 - Selective fuzzy-Harris, 35 seeds + BFS",
    "r02_selective77_radius1_bfs": "R02 - Selective fuzzy-Harris, 77 seeds, radius 1 + BFS",
    "r03_edge_region_mean": "R03 - Edge-delayed + region-mean acceptance",
    "r04_local_or_region": "R04 - Edge-delayed + local-or-region acceptance",
    "r05_local_or_region_hybrid_priority": "R05 - R04 + hybrid edge priority",
    "r06_local_or_region_process_override": "R06 - R04 + process-context override",
}
STAGE_LABELS = {
    "r01_selective35_bfs_to_r02_selective77_radius1_bfs": "R01 → R02: seed coverage recovery",
    "r02_selective77_radius1_bfs_to_r03_edge_region_mean": "R02 → R03: region-mean edge growing",
    "r03_edge_region_mean_to_r04_local_or_region": "R03 → R04: local-or-region acceptance",
    "r04_local_or_region_to_r05_local_or_region_hybrid_priority": "R04 → R05: hybrid priority",
    "r04_local_or_region_to_r06_local_or_region_process_override": "R04 → R06: process-context override",
}
RECOVERY_FILES = {
    "Article table": "recovery_article_table.csv",
    "Delta vs R00": "recovery_delta_vs_r00.csv",
    "Stage deltas": "recovery_stage_deltas.csv",
    "Per-image long": "recovery_per_image_long.csv",
    "Summary long": "recovery_summary_long.csv",
}
PROCESS_CONTEXT_FILES = {
    "Process-context per image": "process_context_per_image.csv",
    "Process-context summary": "process_context_summary.csv",
    "Process-context level counts": "process_context_level_counts.csv",
}
IMAGE_ARTIFACT_COLUMNS = [
    ("Original fundus", "image_path"),
    ("Ground truth", "mask_path"),
    ("Preprocessed", "preprocessed_path"),
    ("APSRG mask", "baseline_mask_path"),
    ("CA-APSRG mask", "ca_apsrg_mask_path"),
    ("APSRG overlay", "baseline_overlay_path"),
    ("CA-APSRG overlay", "ca_apsrg_overlay_path"),
    ("Comparison", "comparison_path"),
]


def _safe_read_csv(path: Path) -> pd.DataFrame | None:
    """Read a CSV file safely."""
    if not path.is_file():
        return None
    try:
        return pd.read_csv(path)
    except Exception:
        return None


def _format_value(value: Any, digits: int = 4) -> str:
    """Format a numeric value for Streamlit cards."""
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value):.{digits}f}"


def _ordered_experiments(values: list[str]) -> list[str]:
    """Return experiments in the intended R00-R06 order."""
    value_set = set(values)
    ordered = [key for key in RECOVERY_ORDER if key in value_set]
    ordered.extend(sorted(value_set.difference(ordered)))
    return ordered


def _experiment_label(experiment: str) -> str:
    """Return a compact experiment label."""
    return RECOVERY_LABELS.get(experiment, experiment.replace("_", " ").title())


def _comparison_label(comparison: str) -> str:
    """Return a compact stage-comparison label."""
    return STAGE_LABELS.get(comparison, comparison.replace("_to_", " → ").replace("_", " "))


def _significance_label(p_value: Any, ci_low: Any, ci_high: Any) -> str:
    """Classify statistical evidence from p-value and bootstrap CI."""
    try:
        p = float(p_value)
        low = float(ci_low)
        high = float(ci_high)
    except (TypeError, ValueError):
        return "Not available"

    ci_excludes_zero = low > 0.0 or high < 0.0
    if p < 0.05 and ci_excludes_zero:
        return "Significant"
    if p < 0.05:
        return "Wilcoxon significant; CI crosses zero"
    return "Not significant"


def _analysis_sentence(row: pd.Series, subject: str) -> str:
    """Build one concise interpretation sentence from a delta row."""
    delta = float(row.get("mean_delta", 0.0))
    metric = str(row.get("metric", "metric")).replace("_", " ")
    dataset = str(row.get("dataset", "all datasets"))
    method = str(row.get("output_method", ""))
    direction = "increased" if delta > 0 else "decreased" if delta < 0 else "did not change"
    evidence = _significance_label(
        row.get("wilcoxon_p_value"),
        row.get("bootstrap_mean_ci_low"),
        row.get("bootstrap_mean_ci_high"),
    )
    return (
        f"{subject} {direction} mean {metric} by {abs(delta):.4f} "
        f"for {method} on {dataset}. Statistical status: {evidence}."
    )


def _load_recovery_tables(root: Path) -> dict[str, pd.DataFrame]:
    """Load recovery comparison and process-context tables."""
    tables: dict[str, pd.DataFrame] = {}
    comparison_dir = root / "comparison"
    for title, filename in RECOVERY_FILES.items():
        df = _safe_read_csv(comparison_dir / filename)
        if df is not None:
            tables[title] = df

    diagnostics_dir = root / "process_context_diagnostics"
    for title, filename in PROCESS_CONTEXT_FILES.items():
        df = _safe_read_csv(diagnostics_dir / filename)
        if df is not None:
            tables[title] = df
    return tables


def _macro_summary(article_df: pd.DataFrame, output_method: str) -> pd.DataFrame:
    """Build one macro-average row per experiment."""
    if article_df.empty:
        return pd.DataFrame()

    work = article_df[article_df["output_method"].astype(str) == output_method].copy()
    if work.empty:
        return pd.DataFrame()

    rows: list[dict[str, Any]] = []
    for experiment, group in work.groupby("experiment", sort=False):
        row: dict[str, Any] = {
            "experiment": experiment,
            "experiment_label": _experiment_label(str(experiment)),
        }
        for metric in CORE_METRICS:
            if metric in group.columns:
                row[metric] = pd.to_numeric(group[metric], errors="coerce").mean()
        rows.append(row)

    result = pd.DataFrame(rows)
    if result.empty:
        return result
    order_map = {key: index for index, key in enumerate(RECOVERY_ORDER)}
    result["_order"] = result["experiment"].map(order_map).fillna(len(order_map))
    return result.sort_values("_order").drop(columns="_order")


def _render_overview(article_df: pd.DataFrame) -> None:
    """Render high-level R00-R06 overview and ranking."""
    st.subheader("Recovery Ablation Overview")
    st.caption(
        "R00-R06 compare legacy APSRG, selective fuzzy-Harris seed recovery, "
        "edge-delayed region growing, local-or-region acceptance, priority mode, "
        "and process-context override."
    )

    if article_df.empty:
        st.warning("recovery_article_table.csv was not found.")
        return

    col_a, col_b, col_c = st.columns([1, 1, 1])
    output_method = col_a.selectbox("Output method", ["CA-APSRG", "APSRG"], key="recovery_overview_method")
    ranking_metric = col_b.selectbox("Ranking metric", CORE_METRICS, index=2, key="recovery_overview_metric")
    dataset_options = ["All datasets"] + sorted(article_df["dataset"].dropna().astype(str).unique().tolist())
    dataset = col_c.selectbox("Dataset", dataset_options, key="recovery_overview_dataset")

    filtered = article_df[article_df["output_method"].astype(str) == output_method].copy()
    if dataset != "All datasets":
        filtered = filtered[filtered["dataset"].astype(str) == dataset]
        summary = filtered[["experiment", "experiment_label", *CORE_METRICS]].copy()
    else:
        summary = _macro_summary(article_df, output_method)

    if summary.empty:
        st.warning("No matching recovery rows were found.")
        return

    summary["display_experiment"] = summary["experiment"].map(_experiment_label)
    summary = summary.sort_values(ranking_metric, ascending=False)

    best = summary.iloc[0]
    r00 = summary[summary["experiment"] == "r00_legacy_polling_bfs"]
    r04 = summary[summary["experiment"] == "r04_local_or_region"]
    r04_delta = None
    if not r00.empty and not r04.empty:
        r04_delta = float(r04.iloc[0][ranking_metric]) - float(r00.iloc[0][ranking_metric])

    cards = st.columns(4)
    cards[0].metric("Best configuration", _experiment_label(str(best["experiment"])).split(" - ")[0])
    cards[1].metric(f"Best {ranking_metric}", _format_value(best[ranking_metric]))
    cards[2].metric("R04 vs R00", _format_value(r04_delta) if r04_delta is not None else "-")
    cards[3].metric("Configurations", int(summary["experiment"].nunique()))

    display_cols = ["display_experiment", *[m for m in CORE_METRICS if m in summary.columns]]
    st.dataframe(
        summary[display_cols].rename(columns={"display_experiment": "experiment"}),
        width="stretch",
        hide_index=True,
    )

    chart = summary.set_index("display_experiment")[[ranking_metric]]
    st.bar_chart(chart)

    st.info(
        "R04 is highlighted as the stable recovery candidate because it uses 77 selective "
        "fuzzy-Harris seeds, radius-1 seed dilation, Kang-product priority, and "
        "local-or-region acceptance. R05 tests priority mode; R06 tests process-context override."
    )


def _render_apsrg_vs_ca(article_df: pd.DataFrame) -> None:
    """Render APSRG versus CA-APSRG comparison for a selected experiment."""
    st.subheader("APSRG vs CA-APSRG")
    if article_df.empty:
        st.warning("Recovery article table is unavailable.")
        return

    experiments = _ordered_experiments(article_df["experiment"].dropna().astype(str).unique().tolist())
    datasets = sorted(article_df["dataset"].dropna().astype(str).unique().tolist())
    col_a, col_b = st.columns(2)
    experiment = col_a.selectbox(
        "Recovery experiment",
        experiments,
        index=experiments.index("r04_local_or_region") if "r04_local_or_region" in experiments else 0,
        format_func=_experiment_label,
        key="recovery_compare_experiment",
    )
    dataset = col_b.selectbox("Dataset", datasets, key="recovery_compare_dataset")

    work = article_df[
        (article_df["experiment"].astype(str) == experiment)
        & (article_df["dataset"].astype(str) == dataset)
    ].copy()
    if work.empty:
        st.warning("No matching APSRG/CA-APSRG rows were found.")
        return

    pivot = work.set_index("output_method")[[m for m in CORE_METRICS if m in work.columns]].T
    if "APSRG" in pivot.columns and "CA-APSRG" in pivot.columns:
        pivot["delta (CA - APSRG)"] = pivot["CA-APSRG"] - pivot["APSRG"]
    pivot.index.name = "metric"
    st.dataframe(pivot.reset_index(), width="stretch", hide_index=True)

    cards = st.columns(4)
    for card, metric in zip(cards, ["f1_score", "iou", "precision", "recall"]):
        baseline_value = None
        ca_value = None
        if metric in pivot.index:
            baseline_value = pivot.loc[metric].get("APSRG")
            ca_value = pivot.loc[metric].get("CA-APSRG")
        delta = None if baseline_value is None or ca_value is None else float(ca_value) - float(baseline_value)
        card.metric(metric.replace("_", " ").title(), _format_value(ca_value), _format_value(delta))

    chart = work.set_index("output_method")[["f1_score", "iou", "precision", "recall"]].T
    st.bar_chart(chart)


def _render_stage_analysis(stage_df: pd.DataFrame) -> None:
    """Render controlled stage-to-stage ablation analysis."""
    st.subheader("Stage-by-Stage Recovery Analysis")
    if stage_df.empty:
        st.warning("recovery_stage_deltas.csv was not found.")
        return

    datasets = sorted(stage_df["dataset"].dropna().astype(str).unique().tolist())
    comparisons = stage_df["comparison"].dropna().astype(str).unique().tolist()
    comparisons = sorted(comparisons, key=lambda x: list(STAGE_LABELS).index(x) if x in STAGE_LABELS else 999)

    col_a, col_b, col_c, col_d = st.columns(4)
    output_method = col_a.selectbox("Output method", ["CA-APSRG", "APSRG"], key="stage_method")
    metric = col_b.selectbox("Metric", CORE_METRICS, index=2, key="stage_metric")
    dataset = col_c.selectbox("Dataset", ["All datasets", *datasets], key="stage_dataset")
    comparison = col_d.selectbox("Stage", ["All stages", *comparisons], format_func=lambda x: x if x == "All stages" else _comparison_label(x), key="stage_comparison")

    work = stage_df[
        (stage_df["output_method"].astype(str) == output_method)
        & (stage_df["metric"].astype(str) == metric)
    ].copy()
    if dataset != "All datasets":
        work = work[work["dataset"].astype(str) == dataset]
    if comparison != "All stages":
        work = work[work["comparison"].astype(str) == comparison]

    if work.empty:
        st.warning("No stage-analysis rows match the selected filters.")
        return

    work["stage"] = work["comparison"].astype(str).map(_comparison_label)
    work["significance"] = work.apply(
        lambda row: _significance_label(
            row.get("wilcoxon_p_value"),
            row.get("bootstrap_mean_ci_low"),
            row.get("bootstrap_mean_ci_high"),
        ),
        axis=1,
    )
    preferred = [
        "stage",
        "dataset",
        "output_method",
        "metric",
        "mean_delta",
        "median_delta",
        "wins",
        "ties",
        "losses",
        "wilcoxon_p_value",
        "bootstrap_mean_ci_low",
        "bootstrap_mean_ci_high",
        "significance",
    ]
    st.dataframe(work[[col for col in preferred if col in work.columns]], width="stretch", hide_index=True)

    chart = work.groupby("stage", dropna=False)["mean_delta"].mean().to_frame("mean delta")
    st.bar_chart(chart)

    st.markdown("**Automatic interpretation**")
    for _, row in work.sort_values(["comparison", "dataset"]).iterrows():
        st.write("- " + _analysis_sentence(row, _comparison_label(str(row["comparison"]))))


def _render_delta_vs_r00(delta_df: pd.DataFrame) -> None:
    """Render each recovery configuration against R00."""
    st.subheader("Comparison Against R00")
    if delta_df.empty:
        st.warning("recovery_delta_vs_r00.csv was not found.")
        return

    experiments = _ordered_experiments(delta_df["experiment"].dropna().astype(str).unique().tolist())
    datasets = sorted(delta_df["dataset"].dropna().astype(str).unique().tolist())
    col_a, col_b, col_c = st.columns(3)
    output_method = col_a.selectbox("Output method", ["CA-APSRG", "APSRG"], key="r00_method")
    metric = col_b.selectbox("Metric", CORE_METRICS, index=2, key="r00_metric")
    dataset = col_c.selectbox("Dataset", ["All datasets", *datasets], key="r00_dataset")

    work = delta_df[
        (delta_df["output_method"].astype(str) == output_method)
        & (delta_df["metric"].astype(str) == metric)
    ].copy()
    if dataset != "All datasets":
        work = work[work["dataset"].astype(str) == dataset]
    if work.empty:
        st.warning("No delta-vs-R00 rows match the selected filters.")
        return

    work["experiment_display"] = work["experiment"].astype(str).map(_experiment_label)
    work["significance"] = work.apply(
        lambda row: _significance_label(
            row.get("wilcoxon_p_value"),
            row.get("bootstrap_mean_ci_low"),
            row.get("bootstrap_mean_ci_high"),
        ),
        axis=1,
    )
    order_map = {key: index for index, key in enumerate(experiments)}
    work["_order"] = work["experiment"].map(order_map).fillna(999)
    work = work.sort_values(["_order", "dataset"]).drop(columns="_order")

    preferred = [
        "experiment_display",
        "dataset",
        "mean_delta",
        "median_delta",
        "wins",
        "ties",
        "losses",
        "wilcoxon_p_value",
        "bootstrap_mean_ci_low",
        "bootstrap_mean_ci_high",
        "significance",
    ]
    st.dataframe(
        work[[col for col in preferred if col in work.columns]].rename(columns={"experiment_display": "experiment"}),
        width="stretch",
        hide_index=True,
    )

    chart = work.groupby("experiment_display", dropna=False)["mean_delta"].mean().to_frame("mean delta vs R00")
    st.bar_chart(chart)

    r04 = work[work["experiment"].astype(str) == "r04_local_or_region"]
    if not r04.empty:
        st.markdown("**R04 interpretation**")
        for _, row in r04.iterrows():
            st.write("- " + _analysis_sentence(row, "R04 versus R00"))


def _is_missing(value: Any) -> bool:
    """Return True for absent path-like values."""
    if value is None:
        return True
    if isinstance(value, float) and np.isnan(value):
        return True
    return str(value).strip().lower() in {"", "nan", "none", "null"}


def _resolve_artifact_path(value: Any, project_root: Path, experiment_dir: Path) -> Path | None:
    """Resolve paths stored on another machine into current repository paths."""
    if _is_missing(value):
        return None

    raw = str(value).strip()
    normalized = raw.replace("\\", "/")
    parts = [part for part in normalized.split("/") if part and not part.endswith(":")]
    candidates = [Path(raw), Path(normalized), project_root / raw, project_root / normalized]

    if "outputs" in parts:
        candidates.append(project_root / Path(*parts[parts.index("outputs") :]))
    if "data" in parts:
        candidates.append(project_root / Path(*parts[parts.index("data") :]))
    if experiment_dir.name in parts:
        suffix = Path(*parts[parts.index(experiment_dir.name) + 1 :])
        candidates.append(experiment_dir / suffix)

    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)
        if candidate.is_file():
            return candidate
    return None


def _image_metric_table(row: pd.Series) -> pd.DataFrame:
    """Build APSRG versus CA-APSRG metrics for one selected image."""
    rows: list[dict[str, Any]] = []
    for metric in ["precision", "recall", "f1_score", "iou", "accuracy", "specificity"]:
        apsrg = row.get(f"baseline_{metric}")
        ca = row.get(f"ca_apsrg_{metric}")
        delta = None
        if not _is_missing(apsrg) and not _is_missing(ca):
            delta = float(ca) - float(apsrg)
        rows.append({"metric": metric, "APSRG": apsrg, "CA-APSRG": ca, "delta": delta})
    return pd.DataFrame(rows)


def _show_image_grid(images: list[tuple[str, Path]], columns: int = 2) -> None:
    """Display local artifact images in a grid."""
    if not images:
        return
    for start in range(0, len(images), columns):
        cols = st.columns(columns)
        for col, (title, path) in zip(cols, images[start : start + columns]):
            with col:
                st.image(str(path), caption=title, width="stretch")


def _render_image_browser(root: Path, project_root: Path) -> None:
    """Render artifacts and per-image metrics for any R00-R06 experiment."""
    st.subheader("Recovery Image Browser")
    available = [
        key
        for key in RECOVERY_ORDER
        if (root / f"experiments_{key}" / "metrics_per_image.csv").is_file()
    ]
    if not available:
        st.warning("No recovery experiment metrics_per_image.csv files were found.")
        return

    col_a, col_b, col_c = st.columns(3)
    experiment = col_a.selectbox(
        "Experiment",
        available,
        index=available.index("r04_local_or_region") if "r04_local_or_region" in available else 0,
        format_func=_experiment_label,
        key="recovery_image_experiment",
    )
    experiment_dir = root / f"experiments_{experiment}"
    metrics_df = _safe_read_csv(experiment_dir / "metrics_per_image.csv")
    if metrics_df is None or metrics_df.empty:
        st.warning("Per-image metrics could not be loaded.")
        return

    datasets = sorted(metrics_df["dataset"].dropna().astype(str).unique().tolist())
    dataset = col_b.selectbox("Dataset", datasets, key="recovery_image_dataset")
    filtered = metrics_df[metrics_df["dataset"].astype(str) == dataset].copy()

    sort_mode = col_c.selectbox(
        "Sort",
        ["Image ID", "Best CA F1", "Worst CA F1", "Best CA-APSRG delta", "Worst CA-APSRG delta"],
        key="recovery_image_sort",
    )
    filtered["delta_f1"] = pd.to_numeric(filtered.get("ca_apsrg_f1_score"), errors="coerce") - pd.to_numeric(
        filtered.get("baseline_f1_score"), errors="coerce"
    )
    if sort_mode == "Best CA F1":
        filtered = filtered.sort_values("ca_apsrg_f1_score", ascending=False)
    elif sort_mode == "Worst CA F1":
        filtered = filtered.sort_values("ca_apsrg_f1_score", ascending=True)
    elif sort_mode == "Best CA-APSRG delta":
        filtered = filtered.sort_values("delta_f1", ascending=False)
    elif sort_mode == "Worst CA-APSRG delta":
        filtered = filtered.sort_values("delta_f1", ascending=True)
    else:
        filtered = filtered.sort_values("image_id")

    image_ids = filtered["image_id"].astype(str).tolist()
    image_id = st.selectbox("Image ID", image_ids, key="recovery_image_id")
    row = filtered[filtered["image_id"].astype(str) == image_id].iloc[0]

    st.dataframe(_image_metric_table(row), width="stretch", hide_index=True)

    images: list[tuple[str, Path]] = []
    missing: list[str] = []
    for title, column in IMAGE_ARTIFACT_COLUMNS:
        path = _resolve_artifact_path(row.get(column), project_root, experiment_dir)
        if path is not None:
            images.append((title, path))
        elif column in row.index and not _is_missing(row.get(column)):
            missing.append(title)
    _show_image_grid(images, columns=2)
    if missing:
        st.caption("Artifacts not found locally: " + ", ".join(missing))

    context_cols = [
        "context_vessel_density",
        "context_component_count",
        "context_small_component_ratio",
        "context_density_level",
        "context_noise_level",
        "context_recommended_refinement_level",
        "selected_refinement_level",
        "selected_min_component_area",
        "n_baseline_pixels",
        "n_ca_apsrg_pixels",
    ]
    available_context = [col for col in context_cols if col in row.index]
    if available_context:
        with st.expander("Context and selected refinement parameters"):
            st.dataframe(
                pd.DataFrame({"item": available_context, "value": [row.get(col) for col in available_context]}),
                width="stretch",
                hide_index=True,
            )

    debug_path = _resolve_artifact_path(row.get("debug_json_path"), project_root, experiment_dir)
    if debug_path is not None:
        with st.expander("Debug JSON"):
            st.code(str(debug_path.relative_to(project_root) if debug_path.is_relative_to(project_root) else debug_path))


def _render_process_context(tables: dict[str, pd.DataFrame]) -> None:
    """Render process-context diagnostic tables and distributions."""
    st.subheader("Process-Context Diagnostics")
    per_image = tables.get("Process-context per image", pd.DataFrame())
    summary = tables.get("Process-context summary", pd.DataFrame())
    levels = tables.get("Process-context level counts", pd.DataFrame())

    if summary.empty and levels.empty and per_image.empty:
        st.info(
            "Process-context diagnostics were not found. Run "
            "scripts/08_export_process_context_diagnostics.py first."
        )
        return

    if not levels.empty:
        st.markdown("**Refinement and risk-level counts**")
        st.dataframe(levels, width="stretch", hide_index=True)

    if not summary.empty:
        st.markdown("**Process-context summary**")
        st.dataframe(summary, width="stretch", hide_index=True)

    if not per_image.empty:
        datasets = sorted(per_image["dataset"].dropna().astype(str).unique().tolist()) if "dataset" in per_image.columns else []
        selected_dataset = st.selectbox("Diagnostic dataset", ["All datasets", *datasets], key="process_context_dataset")
        work = per_image.copy()
        if selected_dataset != "All datasets" and "dataset" in work.columns:
            work = work[work["dataset"].astype(str) == selected_dataset]

        preferred = [
            "dataset",
            "image_id",
            "selected_seed_point_count",
            "candidate_density",
            "growth_ratio",
            "connected_edge_density",
            "process_risk_score",
            "process_risk_level",
            "process_refinement_level",
            "combined_refinement_level",
            "n_pixels_removed",
            "n_pixels_added",
        ]
        cols = [col for col in preferred if col in work.columns]
        st.dataframe(work[cols] if cols else work, width="stretch", hide_index=True)

        chart_cols = [col for col in ["candidate_density", "growth_ratio", "connected_edge_density"] if col in work.columns]
        if chart_cols:
            chart = work.groupby("dataset", dropna=False)[chart_cols].mean() if "dataset" in work.columns else work[chart_cols].mean().to_frame().T
            st.bar_chart(chart)

    st.warning(
        "Interpret R06 carefully: if process risk and combined refinement remain normal, "
        "R06 can be identical to R04 even though process-context extraction is enabled."
    )


def _render_csv_tables(tables: dict[str, pd.DataFrame]) -> None:
    """Render and download any recovery-analysis CSV table."""
    st.subheader("Recovery CSV Tables")
    if not tables:
        st.warning("No recovery CSV tables were found.")
        return
    name = st.selectbox("Table", list(tables.keys()), key="recovery_csv_table")
    df = tables[name]
    st.dataframe(df, width="stretch")
    st.download_button(
        "Download selected CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=name.lower().replace(" ", "_").replace("-", "_") + ".csv",
        mime="text/csv",
    )


def _render_representative_cases(project_root: Path) -> None:
    """Render the nine article-facing best, typical, and worst cases."""
    root = project_root / "results" / "representative_cases"
    metadata_path = root / "representative_cases.csv"
    if not metadata_path.is_file():
        st.warning("Representative-case metadata was not found in results/.")
        return
    metadata = pd.read_csv(metadata_path)
    dataset = st.selectbox("Representative dataset", sorted(metadata["dataset"].unique()))
    category = st.selectbox("Category", ["best", "typical", "worst"])
    row = metadata[(metadata["dataset"] == dataset) & (metadata["category"] == category)].iloc[0]
    st.dataframe(row.to_frame("value"), width="stretch")
    case_dir = root / str(dataset) / str(category)
    images = sorted(case_dir.glob("*.png"))
    if images:
        st.image([str(path) for path in images], caption=[path.stem for path in images], width=260)


def recovery_ablation_page(project_root: Path) -> None:
    """Render the complete R00-R06 recovery ablation dashboard."""
    st.title("Recovery Ablation R00-R06")
    st.write(
        "Dashboard ini menampilkan hasil APSRG dan CA-APSRG, perbandingan R00-R06, "
        "uji statistik, analisis antar-tahap, artefak per citra, dan diagnostik process context."
    )

    recovery_root = project_root / "outputs" / "recovery_ablation"
    tables = _load_recovery_tables(recovery_root)
    article_df = tables.get("Article table", pd.DataFrame())
    delta_df = tables.get("Delta vs R00", pd.DataFrame())
    stage_df = tables.get("Stage deltas", pd.DataFrame())

    if not recovery_root.is_dir():
        st.warning(
            "outputs/recovery_ablation was not found. Run scripts/07_run_recovery_ablation.py first."
        )
        return

    tabs = st.tabs(
        [
            "Overview R00-R06",
            "APSRG vs CA-APSRG",
            "Stage Analysis",
            "Delta vs R00",
            "Image Browser",
            "Representative Cases",
            "Process Context",
            "CSV Tables",
        ]
    )
    with tabs[0]:
        _render_overview(article_df)
    with tabs[1]:
        _render_apsrg_vs_ca(article_df)
    with tabs[2]:
        _render_stage_analysis(stage_df)
    with tabs[3]:
        _render_delta_vs_r00(delta_df)
    with tabs[4]:
        _render_image_browser(recovery_root, project_root)
    with tabs[5]:
        _render_representative_cases(project_root)
    with tabs[6]:
        _render_process_context(tables)
    with tabs[7]:
        _render_csv_tables(tables)
