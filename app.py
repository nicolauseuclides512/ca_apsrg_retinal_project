"""Streamlit demo app for CA-APSRG retinal vessel segmentation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.evaluation.metrics import evaluate_segmentation  # noqa: E402
from src.preprocessing.preprocess import PreprocessConfig, preprocess_fundus  # noqa: E402
from src.segmentation.adaptive_morphology import AdaptiveMorphologyConfig  # noqa: E402
from src.segmentation.apsrg_baseline import APSRGParams, apsrg_segment  # noqa: E402
from src.segmentation.ca_apsrg import CAAPSRGConfig, ca_apsrg_refine  # noqa: E402
from src.segmentation.context_features import ContextFeatureConfig  # noqa: E402
from src.ui.streamlit_helpers import (  # noqa: E402
    file_exists,
    load_yaml_config,
    make_context_dataframe,
    make_metrics_dataframe,
    numeric_mean,
    pil_to_gray_array,
    pil_to_rgb_array,
    safe_read_csv,
    show_image_grid,
    ensure_display_mask,
)
from src.utils.image_io import overlay_mask_on_image, resize_if_needed  # noqa: E402


APP_TITLE = "CA-APSRG Retinal Vessel Segmentation"
DEFAULT_CONFIG_PATH = Path("configs/default.yaml")
BATCH_FILES = {
    "Per-image metrics": Path("outputs/experiments/metrics_per_image.csv"),
    "Metrics summary": Path("outputs/experiments/metrics_summary.csv"),
    "Article table mean/std": Path("outputs/analysis/article_table_mean_std.csv"),
    "Improvement by dataset": Path("outputs/analysis/improvement_by_dataset.csv"),
}
CORE_METRICS = ["precision", "recall", "f1_score", "iou"]
EXPERIMENT_LABELS = {
    "exp1_recall_oriented": "Experiment 1 - Recall-oriented CA-APSRG",
    "exp2_precision_oriented": "Experiment 2 - Precision-oriented CA-APSRG",
    "exp3_balanced_main": "Experiment 3 - Balanced CA-APSRG Main Result",
    "exp4_static_morphology": "Experiment 4 - Static Morphology Ablation",
    "exp5_no_skeleton_guard": "Experiment 5 - No Skeleton Guard Ablation",
    "exp6_no_small_component": "Experiment 6 - No Small Component Removal Ablation",
}
EXPERIMENT_ORDER = list(EXPERIMENT_LABELS.keys())
EXPERIMENT_TABLE_FILES = {
    "Per-image metrics": ("experiments_dir", "metrics_per_image.csv"),
    "Metrics summary": ("experiments_dir", "metrics_summary.csv"),
    "Batch manifest used": ("experiments_dir", "batch_manifest_used.csv"),
    "Article table mean/std": ("analysis_dir", "article_table_mean_std.csv"),
    "Improvement by dataset": ("analysis_dir", "improvement_by_dataset.csv"),
    "Improvement per image": ("analysis_dir", "improvement_per_image.csv"),
    "Long metrics": ("analysis_dir", "long_metrics.csv"),
    "Summary by dataset/method": ("analysis_dir", "summary_by_dataset_method.csv"),
}
IMAGE_ARTIFACT_COLUMNS = [
    ("Original fundus", "image_path"),
    ("Ground truth mask", "mask_path"),
    ("Preprocessed", "preprocessed_path"),
    ("APSRG baseline mask", "baseline_mask_path"),
    ("CA-APSRG mask", "ca_apsrg_mask_path"),
    ("APSRG overlay", "baseline_overlay_path"),
    ("CA-APSRG overlay", "ca_apsrg_overlay_path"),
    ("Side-by-side comparison", "comparison_path"),
]


def resolve_project_path(path: str | Path) -> Path:
    """Resolve a project-relative path without hardcoding local absolute paths."""
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def configure_page() -> None:
    """Configure global Streamlit page settings."""
    st.set_page_config(
        page_title=APP_TITLE,
        layout="wide",
        initial_sidebar_state="expanded",
    )


def sidebar() -> tuple[str, Path]:
    """Render sidebar navigation and return selected page and config path."""
    st.sidebar.title(APP_TITLE)
    page = st.sidebar.radio(
        "Menu",
        [
            "Home",
            "Single Image Demo",
            "Batch Result Viewer",
            "Method Explanation",
            "About Dataset",
        ],
    )

    config_text = st.sidebar.text_input("Config path", value=str(DEFAULT_CONFIG_PATH))
    st.sidebar.info(
        "Demo penelitian segmentasi pembuluh darah retina berbasis "
        "Context-Aware APSRG dan adaptive morphological refinement."
    )
    return page, resolve_project_path(config_text)


def home_page() -> None:
    """Render the app home page."""
    st.title(
        "Context-Aware APSRG with Adaptive Morphological Refinement "
        "for Retinal Blood Vessel Segmentation"
    )
    st.write(
        "CA-APSRG adalah pengembangan dari APSRG untuk mengurangi false positive "
        "pada segmentasi pembuluh darah retina tanpa menghilangkan pembuluh darah tipis."
    )

    st.subheader("Pipeline Flow")
    st.markdown(
        """
        **Input Fundus Image** -> **Preprocessing** -> **APSRG Baseline** ->
        **Context Feature Extraction** -> **Adaptive Morphological Refinement** ->
        **CA-APSRG Output**
        """
    )
    st.info(
        "Aplikasi ini mendukung demo single image melalui upload citra dan viewer "
        "hasil batch experiment dari CSV yang sudah dibuat oleh script eksperimen."
    )


def load_ui_config(config_path: Path) -> dict[str, Any]:
    """Load config for UI use and show a warning when it is missing."""
    config = load_yaml_config(config_path)
    if not config:
        st.warning(f"Config file not found or empty: `{config_path.relative_to(PROJECT_ROOT) if config_path.is_relative_to(PROJECT_ROOT) else config_path}`. Defaults will be used.")
    return config


def build_algorithm_configs(config: dict[str, Any]) -> tuple[
    PreprocessConfig,
    APSRGParams,
    AdaptiveMorphologyConfig,
    CAAPSRGConfig,
    ContextFeatureConfig,
]:
    """Create algorithm config dataclasses from the loaded YAML dictionary."""
    preprocessing = PreprocessConfig.from_dict(config.get("preprocessing", {}))
    apsrg = APSRGParams.from_dict(config.get("apsrg_baseline", {}))
    adaptive = AdaptiveMorphologyConfig.from_dict(
        config.get("adaptive_morphology", {}),
        ca_apsrg_config=config.get("ca_apsrg", {}),
    )
    ca = CAAPSRGConfig.from_dict(config.get("ca_apsrg", {}))
    context = ContextFeatureConfig.from_dict(config.get("context_features", {}))
    return preprocessing, apsrg, adaptive, ca, context


def _resize_optional_mask(mask: np.ndarray | None, reference: np.ndarray) -> np.ndarray | None:
    """Resize an optional mask to match a reference image shape."""
    if mask is None:
        return None
    return resize_if_needed(mask, reference, interpolation="nearest")


def run_single_image_pipeline(
    *,
    image_rgb: np.ndarray,
    gt_mask: np.ndarray | None,
    fov_mask: np.ndarray | None,
    config_path: Path,
) -> dict[str, Any]:
    """Run preprocessing, APSRG baseline, CA-APSRG refinement, and optional metrics."""
    config = load_ui_config(config_path)
    preprocessing_cfg, apsrg_cfg, adaptive_cfg, ca_cfg, context_cfg = build_algorithm_configs(config)

    preprocessed = preprocess_fundus(image_rgb, fov_mask=fov_mask, config=preprocessing_cfg)
    fov_for_segmentation = _resize_optional_mask(fov_mask, preprocessed)

    baseline_mask, apsrg_debug = apsrg_segment(
        preprocessed,
        fov_mask=fov_for_segmentation,
        params=apsrg_cfg,
    )
    refined_mask, ca_debug = ca_apsrg_refine(
        baseline_mask,
        fov_mask=fov_for_segmentation,
        params=adaptive_cfg,
        ca_config=ca_cfg,
        context_config=context_cfg,
    )

    baseline_metrics = None
    ca_metrics = None
    if gt_mask is not None:
        baseline_metrics = evaluate_segmentation(
            baseline_mask,
            gt_mask,
            fov_for_segmentation,
            resize_prediction_to_gt=True,
            resize_fov_to_gt=True,
        )
        ca_metrics = evaluate_segmentation(
            refined_mask,
            gt_mask,
            fov_for_segmentation,
            resize_prediction_to_gt=True,
            resize_fov_to_gt=True,
        )

    return {
        "image_rgb": image_rgb,
        "gt_mask": gt_mask,
        "fov_mask": fov_for_segmentation,
        "preprocessed": preprocessed,
        "baseline_mask": baseline_mask,
        "refined_mask": refined_mask,
        "apsrg_debug": apsrg_debug,
        "ca_debug": ca_debug,
        "baseline_metrics": baseline_metrics,
        "ca_metrics": ca_metrics,
    }


def render_single_image_result(
    result: dict[str, Any],
    *,
    show_processing_steps: bool,
    show_overlays: bool,
    show_debug_features: bool,
) -> None:
    """Render stored single-image result arrays and tables."""
    image_rgb = result["image_rgb"]
    baseline_mask = result["baseline_mask"]
    refined_mask = result["refined_mask"]
    gt_mask = result.get("gt_mask")
    preprocessed = result["preprocessed"]
    apsrg_debug = result.get("apsrg_debug", {})
    ca_debug = result.get("ca_debug", {})

    st.subheader("Segmentation Output")
    output_images = [
        ("Original fundus image", image_rgb),
        ("Preprocessed image", preprocessed),
        ("APSRG baseline mask", ensure_display_mask(baseline_mask)),
        ("CA-APSRG refined mask", ensure_display_mask(refined_mask)),
    ]
    if gt_mask is not None:
        output_images.append(("Ground truth mask", ensure_display_mask(gt_mask)))
    show_image_grid(output_images, columns=3)

    if show_overlays:
        st.subheader("Overlays")
        baseline_overlay = overlay_mask_on_image(
            image_rgb,
            baseline_mask,
            alpha=0.45,
            mask_color=(255, 0, 0),
        )
        ca_overlay = overlay_mask_on_image(
            image_rgb,
            refined_mask,
            alpha=0.45,
            mask_color=(0, 255, 0),
        )
        show_image_grid(
            [
                ("APSRG overlay", baseline_overlay),
                ("CA-APSRG overlay", ca_overlay),
            ],
            columns=2,
        )

    baseline_metrics = result.get("baseline_metrics")
    ca_metrics = result.get("ca_metrics")
    if baseline_metrics is not None and ca_metrics is not None:
        st.subheader("Metrics Comparison")
        metrics_df = make_metrics_dataframe(baseline_metrics, ca_metrics)
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)
    else:
        st.info("Ground truth mask not uploaded; metrics cannot be computed.")

    if show_processing_steps:
        st.subheader("Processing Steps")
        show_image_grid(
            [
                ("Preprocessed image", preprocessed),
                ("Vesselness image", apsrg_debug.get("vesselness")),
                ("Seed map", ensure_display_mask(apsrg_debug.get("seeds"))),
                ("Candidate map", ensure_display_mask(apsrg_debug.get("candidate"))),
                ("APSRG baseline mask", ensure_display_mask(baseline_mask)),
                ("CA-APSRG refined mask", ensure_display_mask(refined_mask)),
            ],
            columns=3,
        )

    if show_debug_features:
        st.subheader("Debug and Context Features")
        context_df = make_context_dataframe(ca_debug)
        st.dataframe(context_df, use_container_width=True, hide_index=True)


def single_image_demo_page(config_path: Path) -> None:
    """Render and run the single-image demo page."""
    st.title("Single Image Demo")
    st.write("Upload citra fundus, lalu jalankan pipeline CA-APSRG pada satu gambar.")

    fundus_file = st.file_uploader(
        "Upload fundus image",
        type=["png", "jpg", "jpeg", "tif", "tiff", "ppm"],
    )
    col_a, col_b = st.columns(2)
    with col_a:
        gt_file = st.file_uploader(
            "Upload ground truth mask (optional)",
            type=["png", "gif", "tif", "tiff"],
        )
    with col_b:
        fov_file = st.file_uploader(
            "Upload FoV mask (optional)",
            type=["png", "gif", "tif", "tiff"],
        )

    show_processing_steps = st.checkbox("Show processing steps", value=True)
    show_overlays = st.checkbox("Show overlays", value=True)
    show_debug_features = st.checkbox("Show debug/context features", value=True)

    if st.button("Run CA-APSRG", type="primary"):
        if fundus_file is None:
            st.warning("Please upload a fundus image first.")
        else:
            try:
                with st.spinner("Running CA-APSRG segmentation..."):
                    image_rgb = pil_to_rgb_array(fundus_file)
                    gt_mask = ensure_display_mask(pil_to_gray_array(gt_file)) if gt_file is not None else None
                    fov_mask = ensure_display_mask(pil_to_gray_array(fov_file)) if fov_file is not None else None
                    st.session_state["single_image_result"] = run_single_image_pipeline(
                        image_rgb=image_rgb,
                        gt_mask=gt_mask,
                        fov_mask=fov_mask,
                        config_path=config_path,
                    )
                st.success("CA-APSRG segmentation completed.")
            except Exception as exc:
                st.error(f"Failed to run segmentation: {exc}")

    result = st.session_state.get("single_image_result")
    if result is not None:
        render_single_image_result(
            result,
            show_processing_steps=show_processing_steps,
            show_overlays=show_overlays,
            show_debug_features=show_debug_features,
        )


def summarize_from_per_image(df: pd.DataFrame) -> pd.DataFrame:
    """Build overall mean and delta summary from metrics_per_image.csv."""
    rows: list[dict[str, Any]] = []
    for metric in CORE_METRICS:
        baseline = numeric_mean(df.get(f"baseline_{metric}", []))
        ca = numeric_mean(df.get(f"ca_apsrg_{metric}", []))
        rows.append(
            {
                "metric": metric,
                "APSRG baseline mean": baseline,
                "CA-APSRG mean": ca,
                "delta (CA - APSRG)": None if baseline is None or ca is None else ca - baseline,
            }
        )
    return pd.DataFrame(rows)


def summarize_from_metrics_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Build overall mean and delta summary from metrics_summary.csv."""
    if "method" not in df.columns:
        return pd.DataFrame()

    rows: list[dict[str, Any]] = []
    method_text = df["method"].astype(str).str.lower()
    baseline_mask = method_text.eq("apsrg") | method_text.str.contains("baseline", na=False)
    ca_mask = method_text.str.contains("ca", na=False)

    for metric in CORE_METRICS:
        mean_col = f"{metric}_mean"
        if mean_col not in df.columns:
            continue

        baseline = numeric_mean(df.loc[baseline_mask, mean_col])
        ca = numeric_mean(df.loc[ca_mask, mean_col])
        rows.append(
            {
                "metric": metric,
                "APSRG baseline mean": baseline,
                "CA-APSRG mean": ca,
                "delta (CA - APSRG)": None if baseline is None or ca is None else ca - baseline,
            }
        )

    return pd.DataFrame(rows)


def chart_data_from_per_image(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """Create chart data for one metric from per-image results."""
    baseline_col = f"baseline_{metric}"
    ca_col = f"ca_apsrg_{metric}"
    if baseline_col not in df.columns or ca_col not in df.columns:
        return pd.DataFrame()

    plot_df = df.copy()
    plot_df[baseline_col] = pd.to_numeric(plot_df[baseline_col], errors="coerce")
    plot_df[ca_col] = pd.to_numeric(plot_df[ca_col], errors="coerce")

    if "dataset" in plot_df.columns:
        chart = plot_df.groupby("dataset", dropna=False)[[baseline_col, ca_col]].mean()
    else:
        chart = pd.DataFrame(
            {
                baseline_col: [plot_df[baseline_col].mean()],
                ca_col: [plot_df[ca_col].mean()],
            },
            index=["All"],
        )

    return chart.rename(columns={baseline_col: "APSRG", ca_col: "CA-APSRG"})


def chart_data_from_metrics_summary(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """Create chart data for one metric from metrics_summary.csv."""
    mean_col = f"{metric}_mean"
    if "method" not in df.columns or mean_col not in df.columns:
        return pd.DataFrame()

    work = df.copy()
    method_text = work["method"].astype(str).str.lower()
    work["_method_group"] = np.where(
        method_text.str.contains("ca", na=False),
        "CA-APSRG",
        np.where(method_text.eq("apsrg") | method_text.str.contains("baseline", na=False), "APSRG", "Other"),
    )
    work[mean_col] = pd.to_numeric(work[mean_col], errors="coerce")
    work = work[work["_method_group"].isin(["APSRG", "CA-APSRG"])]
    if work.empty:
        return pd.DataFrame()

    if "dataset" in work.columns:
        chart = work.pivot_table(index="dataset", columns="_method_group", values=mean_col, aggfunc="mean")
    else:
        chart = work.pivot_table(columns="_method_group", values=mean_col, aggfunc="mean")
        chart.index = ["All"]

    return chart[[col for col in ["APSRG", "CA-APSRG"] if col in chart.columns]]


def project_relative(path: Path) -> str:
    """Return a compact project-relative path when possible."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def is_missing_value(value: Any) -> bool:
    """Return True for empty, NaN, or placeholder path values."""
    if value is None:
        return True
    if isinstance(value, float) and np.isnan(value):
        return True
    text = str(value).strip()
    return text == "" or text.lower() in {"nan", "none", "null"}


def discover_experiment_result_sets() -> list[dict[str, Any]]:
    """Discover default and numbered experiment output folders."""
    outputs_dir = PROJECT_ROOT / "outputs"
    result_sets: list[dict[str, Any]] = []

    default_analysis = outputs_dir / "analysis"
    default_experiments = outputs_dir / "experiments"
    if default_analysis.exists() or default_experiments.exists():
        result_sets.append(
            {
                "key": "default",
                "label": "Default Streamlit Result - Experiment 3 Copy",
                "analysis_dir": default_analysis,
                "experiments_dir": default_experiments,
            }
        )

    discovered_keys: set[str] = set()
    for key in EXPERIMENT_ORDER:
        analysis_dir = outputs_dir / f"analysis_{key}"
        experiments_dir = outputs_dir / f"experiments_{key}"
        if analysis_dir.exists() or experiments_dir.exists():
            discovered_keys.add(key)
            result_sets.append(
                {
                    "key": key,
                    "label": EXPERIMENT_LABELS[key],
                    "analysis_dir": analysis_dir,
                    "experiments_dir": experiments_dir,
                }
            )

    for analysis_dir in sorted(outputs_dir.glob("analysis_exp*")):
        key = analysis_dir.name.removeprefix("analysis_")
        if key in discovered_keys:
            continue
        result_sets.append(
            {
                "key": key,
                "label": key.replace("_", " ").title(),
                "analysis_dir": analysis_dir,
                "experiments_dir": outputs_dir / f"experiments_{key}",
            }
        )

    return result_sets


def load_experiment_tables(result_set: dict[str, Any]) -> dict[str, pd.DataFrame]:
    """Load all known CSV tables for one experiment result set."""
    tables: dict[str, pd.DataFrame] = {}
    for title, (root_key, filename) in EXPERIMENT_TABLE_FILES.items():
        path = Path(result_set[root_key]) / filename
        df = safe_read_csv(path)
        if df is not None:
            tables[title] = df

    case_dir = Path(result_set["analysis_dir"]) / "case_tables"
    if case_dir.is_dir():
        for path in sorted(case_dir.glob("*.csv")):
            df = safe_read_csv(path)
            if df is not None:
                tables[f"Case: {path.stem.replace('_', ' ').title()}"] = df

    return tables


def resolve_artifact_path(value: Any, result_set: dict[str, Any]) -> Path | None:
    """Resolve local, copied, or Windows-style paths recorded inside experiment CSV files."""
    if is_missing_value(value):
        return None

    raw_text = str(value).strip()
    normalized = raw_text.replace("\\", "/")
    candidates = [Path(raw_text), Path(normalized), PROJECT_ROOT / raw_text, PROJECT_ROOT / normalized]

    parts = [part for part in normalized.split("/") if part and not part.endswith(":")]
    for marker in [PROJECT_ROOT.name, "outputs", "data"]:
        if marker in parts:
            rel = Path(*parts[parts.index(marker) + 1 :])
            candidates.append(PROJECT_ROOT / rel)

    for experiment_dir_name in [Path(result_set["experiments_dir"]).name, "experiments"]:
        if experiment_dir_name in parts:
            suffix = Path(*parts[parts.index(experiment_dir_name) + 1 :])
            candidates.append(Path(result_set["experiments_dir"]) / suffix)

    for part in parts:
        if part.startswith("experiments_exp") and part in parts:
            suffix = Path(*parts[parts.index(part) + 1 :])
            candidates.append(Path(result_set["experiments_dir"]) / suffix)

    seen: set[str] = set()
    for candidate in candidates:
        text = str(candidate)
        if text in seen:
            continue
        seen.add(text)
        if candidate.is_file():
            return candidate

    return None


def format_metric_value(value: Any) -> str:
    """Format metric values compactly for Streamlit metric cards."""
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value):.4f}"


def weighted_mean(df: pd.DataFrame, column: str) -> float | None:
    """Compute weighted mean by n_images when available."""
    if df.empty or column not in df.columns:
        return None
    values = pd.to_numeric(df[column], errors="coerce")
    if "n_images" not in df.columns:
        return numeric_mean(values)
    weights = pd.to_numeric(df["n_images"], errors="coerce").fillna(0)
    valid = values.notna() & (weights > 0)
    if not valid.any():
        return numeric_mean(values)
    return float((values[valid] * weights[valid]).sum() / weights[valid].sum())


def method_metric_mean(summary_df: pd.DataFrame, method_pattern: str, metric: str) -> float | None:
    """Read mean metric for a method from summary table."""
    mean_col = f"{metric}_mean"
    if summary_df.empty or "method" not in summary_df.columns or mean_col not in summary_df.columns:
        return None
    method_text = summary_df["method"].astype(str).str.lower()
    if method_pattern == "ca":
        mask = method_text.str.contains("ca", na=False)
    elif method_pattern == "baseline":
        mask = (
            method_text.eq("apsrg")
            | method_text.str.contains("baseline", na=False)
            | (method_text.str.contains("apsrg", na=False) & ~method_text.str.contains("ca", na=False))
        )
    else:
        mask = method_text.str.contains(method_pattern, na=False)
    return weighted_mean(summary_df.loc[mask], mean_col)


def render_experiment_overview(result_set: dict[str, Any], tables: dict[str, pd.DataFrame]) -> None:
    """Render high-level selected experiment summary."""
    st.caption(
        f"Analysis: `{project_relative(Path(result_set['analysis_dir']))}` | "
        f"Experiments: `{project_relative(Path(result_set['experiments_dir']))}`"
    )

    summary_df = tables.get("Metrics summary", tables.get("Summary by dataset/method", pd.DataFrame()))
    improvement_df = tables.get("Improvement by dataset", pd.DataFrame())

    if not summary_df.empty:
        ca_f1 = method_metric_mean(summary_df, "ca", "f1_score")
        baseline_f1 = method_metric_mean(summary_df, "baseline", "f1_score")
        ca_iou = method_metric_mean(summary_df, "ca", "iou")
        ca_precision = method_metric_mean(summary_df, "ca", "precision")
        delta_f1 = None if ca_f1 is None or baseline_f1 is None else ca_f1 - baseline_f1
        delta_iou = weighted_mean(improvement_df, "delta_iou_mean") if not improvement_df.empty else None

        cols = st.columns(4)
        cols[0].metric("CA-APSRG F1-score", format_metric_value(ca_f1), format_metric_value(delta_f1))
        cols[1].metric("CA-APSRG IoU", format_metric_value(ca_iou), format_metric_value(delta_iou))
        cols[2].metric("CA-APSRG Precision", format_metric_value(ca_precision))
        cols[3].metric("Images", int(summary_df["n_images"].max()) if "n_images" in summary_df.columns else len(summary_df))

    article_df = tables.get("Article table mean/std", pd.DataFrame())
    if not article_df.empty:
        st.subheader("Article-style Summary")
        st.dataframe(article_df, use_container_width=True, hide_index=True)

    if not improvement_df.empty:
        st.subheader("Improvement by Dataset")
        preferred_cols = [
            "dataset",
            "n_images",
            "delta_precision_mean",
            "delta_recall_mean",
            "delta_f1_score_mean",
            "delta_iou_mean",
            "f1_score_n_improved",
            "f1_score_n_decreased",
        ]
        cols = [col for col in preferred_cols if col in improvement_df.columns]
        st.dataframe(improvement_df[cols] if cols else improvement_df, use_container_width=True, hide_index=True)


def render_metric_charts(tables: dict[str, pd.DataFrame]) -> None:
    """Render native metric charts and saved matplotlib plots."""
    metrics_summary_df = tables.get("Metrics summary", tables.get("Summary by dataset/method", pd.DataFrame()))
    per_image_df = tables.get("Per-image metrics", pd.DataFrame())

    st.subheader("Native Metric Charts")
    chart_source = metrics_summary_df if not metrics_summary_df.empty else per_image_df
    chart_builder = chart_data_from_metrics_summary if not metrics_summary_df.empty else chart_data_from_per_image
    for metric in CORE_METRICS:
        chart_df = chart_builder(chart_source, metric)
        if chart_df.empty:
            continue
        st.markdown(f"**{metric.replace('_', '-').title()} comparison**")
        st.bar_chart(chart_df)


def render_saved_plots(result_set: dict[str, Any]) -> None:
    """Render saved plot PNG files from analysis/plots."""
    plot_dir = Path(result_set["analysis_dir"]) / "plots"
    plot_paths = sorted(plot_dir.glob("*.png")) if plot_dir.is_dir() else []
    if not plot_paths:
        st.info("No saved plot images found for this experiment.")
        return

    st.subheader("Saved Analysis Plots")
    for start in range(0, len(plot_paths), 2):
        cols = st.columns(2)
        for col, path in zip(cols, plot_paths[start : start + 2]):
            with col:
                st.image(str(path), caption=path.stem.replace("_", " ").title(), use_container_width=True)


def selected_image_metrics(row: pd.Series) -> pd.DataFrame:
    """Build a compact metric table for one image row."""
    rows: list[dict[str, Any]] = []
    for metric in ["accuracy", *CORE_METRICS, "specificity"]:
        baseline = row.get(f"baseline_{metric}")
        ca = row.get(f"ca_apsrg_{metric}")
        delta = row.get(f"delta_{metric}")
        if is_missing_value(delta) and not is_missing_value(baseline) and not is_missing_value(ca):
            delta = float(ca) - float(baseline)
        rows.append({"metric": metric, "APSRG": baseline, "CA-APSRG": ca, "delta": delta})
    return pd.DataFrame(rows)


def render_image_browser(result_set: dict[str, Any], tables: dict[str, pd.DataFrame]) -> None:
    """Render per-image metrics and visual artifacts."""
    per_image_df = tables.get("Per-image metrics", pd.DataFrame())
    if per_image_df.empty:
        per_image_df = tables.get("Improvement per image", pd.DataFrame())
    if per_image_df.empty:
        st.warning("No per-image metrics table found for image browsing.")
        return

    work = per_image_df.copy()
    if "dataset" not in work.columns or "image_id" not in work.columns:
        st.warning("Per-image table must contain dataset and image_id columns.")
        return

    datasets = sorted(work["dataset"].dropna().astype(str).unique())
    col_a, col_b, col_c = st.columns([1, 1, 1])
    selected_dataset = col_a.selectbox("Dataset", datasets)
    sort_mode = col_b.selectbox(
        "Sort images",
        ["Image ID", "Best delta F1", "Worst delta F1", "Best CA F1", "Worst CA F1"],
    )
    filtered = work[work["dataset"].astype(str) == selected_dataset].copy()

    sort_map = {
        "Best delta F1": ("delta_f1_score", False),
        "Worst delta F1": ("delta_f1_score", True),
        "Best CA F1": ("ca_apsrg_f1_score", False),
        "Worst CA F1": ("ca_apsrg_f1_score", True),
    }
    if sort_mode in sort_map:
        sort_col, ascending = sort_map[sort_mode]
        if sort_col in filtered.columns:
            filtered[sort_col] = pd.to_numeric(filtered[sort_col], errors="coerce")
            filtered = filtered.sort_values(sort_col, ascending=ascending, na_position="last")
    else:
        filtered = filtered.sort_values("image_id")

    image_ids = filtered["image_id"].astype(str).tolist()
    selected_image_id = col_c.selectbox("Image ID", image_ids)
    row = filtered[filtered["image_id"].astype(str) == selected_image_id].iloc[0]

    st.subheader(f"{selected_dataset} / {selected_image_id}")
    st.dataframe(selected_image_metrics(row), use_container_width=True, hide_index=True)

    images: list[tuple[str, Any]] = []
    missing: list[str] = []
    for title, column in IMAGE_ARTIFACT_COLUMNS:
        path = resolve_artifact_path(row.get(column), result_set)
        if path is None:
            if column in row.index and not is_missing_value(row.get(column)):
                missing.append(title)
            continue
        images.append((title, str(path)))

    if images:
        show_image_grid(images, columns=2)
    if missing:
        st.caption("Artifacts not found locally: " + ", ".join(missing))

    debug_path = resolve_artifact_path(row.get("debug_json_path"), result_set)
    if debug_path is not None:
        with st.expander("Debug JSON path"):
            st.code(project_relative(debug_path))


def render_tables(tables: dict[str, pd.DataFrame]) -> None:
    """Render arbitrary CSV tables with download buttons."""
    if not tables:
        st.warning("No CSV tables found for this experiment.")
        return
    table_name = st.selectbox("Table", list(tables.keys()))
    df = tables[table_name]
    st.dataframe(df, use_container_width=True)
    st.download_button(
        "Download selected table as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=f"{table_name.lower().replace(' ', '_').replace(':', '')}.csv",
        mime="text/csv",
    )


def render_case_tables_and_report(result_set: dict[str, Any], tables: dict[str, pd.DataFrame]) -> None:
    """Render case tables and Markdown report."""
    report_path = Path(result_set["analysis_dir"]) / "results_summary.md"
    if report_path.is_file():
        with st.expander("Markdown results summary", expanded=False):
            st.markdown(report_path.read_text(encoding="utf-8"))

    case_tables = {name: df for name, df in tables.items() if name.startswith("Case: ")}
    if not case_tables:
        st.info("No case tables found.")
        return
    table_name = st.selectbox("Case table", list(case_tables.keys()))
    st.dataframe(case_tables[table_name], use_container_width=True, hide_index=True)


def collect_all_experiment_comparison(result_sets: list[dict[str, Any]]) -> pd.DataFrame:
    """Create one comparison row per numbered experiment."""
    rows: list[dict[str, Any]] = []
    candidates = [item for item in result_sets if item["key"] != "default"] or result_sets

    for result_set in candidates:
        improvement = safe_read_csv(Path(result_set["analysis_dir"]) / "improvement_by_dataset.csv")
        summary = safe_read_csv(Path(result_set["experiments_dir"]) / "metrics_summary.csv")
        if improvement is None and summary is None:
            continue

        row: dict[str, Any] = {"experiment": result_set["label"]}
        if improvement is not None:
            row["n_images"] = int(pd.to_numeric(improvement.get("n_images", []), errors="coerce").sum())
            for metric in ["precision", "recall", "f1_score", "iou", "accuracy"]:
                row[f"delta_{metric}"] = weighted_mean(improvement, f"delta_{metric}_mean")

        if summary is not None:
            for metric in ["precision", "recall", "f1_score", "iou", "accuracy"]:
                row[f"ca_{metric}"] = method_metric_mean(summary, "ca", metric)
                row[f"baseline_{metric}"] = method_metric_mean(summary, "baseline", metric)
        rows.append(row)

    return pd.DataFrame(rows)


def render_all_experiment_comparison(result_sets: list[dict[str, Any]]) -> None:
    """Render experiment 1-6 comparison table and charts."""
    comparison_df = collect_all_experiment_comparison(result_sets)
    if comparison_df.empty:
        st.warning("No multi-experiment summary found.")
        return

    st.subheader("Experiment 1-6 Comparison")
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    for metric in ["delta_precision", "delta_recall", "delta_f1_score", "delta_iou"]:
        if metric not in comparison_df.columns:
            continue
        chart_df = comparison_df[["experiment", metric]].set_index("experiment")
        st.markdown(f"**{metric.replace('_', ' ').title()}**")
        st.bar_chart(chart_df)


def batch_result_viewer_page() -> None:
    """Render full experiment result viewer."""
    st.title("Experiment Result Viewer")
    st.info("Viewer ini membaca output eksperimen yang sudah ada. Tidak ada batch experiment yang dijalankan dari Streamlit.")

    result_sets = discover_experiment_result_sets()
    if not result_sets:
        st.warning("Batch result file not found. Run scripts/03_run_batch.py and scripts/04_summarize_results.py first.")
        return

    selected = st.selectbox(
        "Experiment result set",
        result_sets,
        format_func=lambda item: item["label"],
    )
    tables = load_experiment_tables(selected)
    if not tables:
        st.warning("Batch result file not found. Run scripts/03_run_batch.py and scripts/04_summarize_results.py first.")

    tabs = st.tabs(
        [
            "Overview",
            "Metric Charts",
            "Saved Plots",
            "Image Browser",
            "CSV Tables",
            "Case Tables & Report",
            "All Experiments",
        ]
    )
    with tabs[0]:
        render_experiment_overview(selected, tables)
    with tabs[1]:
        render_metric_charts(tables)
    with tabs[2]:
        render_saved_plots(selected)
    with tabs[3]:
        render_image_browser(selected, tables)
    with tabs[4]:
        render_tables(tables)
    with tabs[5]:
        render_case_tables_and_report(selected, tables)
    with tabs[6]:
        render_all_experiment_comparison(result_sets)


def method_explanation_page() -> None:
    """Render method explanation page."""
    st.title("Method Explanation")
    st.markdown(
        """
        ### 1. Preprocessing
        - Green channel extraction
        - Normalization
        - CLAHE
        - Optional denoising
        - Optional FoV masking

        ### 2. APSRG Baseline
        - Vessel enhancement
        - Automatic seed selection
        - Candidate vessel map
        - Region growing
        - Light post-processing

        ### 3. Context Feature Extraction
        - Vessel density
        - Connected component statistics
        - Small component ratio
        - Skeleton indicators

        ### 4. Adaptive Morphological Refinement
        - Remove small objects
        - Fill small holes
        - Morphological closing
        - Optional opening
        - Skeleton guard

        ### 5. CA-APSRG Output
        - Refined vessel segmentation mask
        - Expected goal: reduce false positive while preserving thin vessels
        """
    )


def about_dataset_page() -> None:
    """Render dataset information page."""
    st.title("About Dataset")
    st.markdown(
        """
        Project ini mendukung dataset **DRIVE**, **STARE**, dan **CHASEDB1**.

        - **DRIVE** digunakan sebagai baseline benchmark.
        - **STARE** digunakan untuk citra retina yang lebih menantang.
        - **CHASEDB1** digunakan untuk uji robustness pada struktur pembuluh yang lebih kompleks.
        """
    )
    st.info(
        "Dataset penuh tidak perlu dimasukkan ke Streamlit Cloud. Untuk Streamlit Cloud, "
        "gunakan beberapa sample image saja. Batch experiment sebaiknya dijalankan lokal, "
        "lalu hasil CSV diunggah ke repository untuk ditampilkan."
    )


def main() -> None:
    """Run the Streamlit application."""
    configure_page()
    page, config_path = sidebar()

    try:
        if page == "Home":
            home_page()
        elif page == "Single Image Demo":
            single_image_demo_page(config_path)
        elif page == "Batch Result Viewer":
            batch_result_viewer_page()
        elif page == "Method Explanation":
            method_explanation_page()
        elif page == "About Dataset":
            about_dataset_page()
    except Exception as exc:
        st.error(f"Application error: {exc}")


if __name__ == "__main__":
    main()
