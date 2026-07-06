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


def batch_result_viewer_page() -> None:
    """Render batch CSV result viewer."""
    st.title("Batch Result Viewer")
    st.info("Viewer ini membaca CSV hasil batch experiment. Tidak ada batch experiment yang dijalankan dari Streamlit.")

    loaded_tables: dict[str, pd.DataFrame] = {}
    missing_paths: list[Path] = []
    for title, relative_path in BATCH_FILES.items():
        path = resolve_project_path(relative_path)
        if file_exists(path):
            df = safe_read_csv(path)
            if df is not None:
                loaded_tables[title] = df
        else:
            missing_paths.append(relative_path)

    if not loaded_tables:
        st.warning("Batch result file not found. Run scripts/03_run_batch.py and scripts/04_summarize_results.py first.")
        return

    if missing_paths:
        st.warning("Batch result file not found. Run scripts/03_run_batch.py and scripts/04_summarize_results.py first.")
        st.caption("Missing files: " + ", ".join(f"`{path}`" for path in missing_paths))

    tabs = st.tabs(list(loaded_tables.keys()))
    for tab, (title, df) in zip(tabs, loaded_tables.items()):
        with tab:
            st.subheader(title)
            st.dataframe(df, use_container_width=True)

    per_image_df = loaded_tables.get("Per-image metrics")
    metrics_summary_df = loaded_tables.get("Metrics summary")
    if per_image_df is not None:
        summary_df = summarize_from_per_image(per_image_df)
        chart_source = per_image_df
        chart_builder = chart_data_from_per_image
    elif metrics_summary_df is not None:
        summary_df = summarize_from_metrics_summary(metrics_summary_df)
        chart_source = metrics_summary_df
        chart_builder = chart_data_from_metrics_summary
    else:
        summary_df = pd.DataFrame()
        chart_source = pd.DataFrame()
        chart_builder = chart_data_from_per_image

    if not summary_df.empty:
        st.subheader("Mean Metrics and Delta")
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

    st.subheader("Metric Comparison Charts")
    for metric in CORE_METRICS:
        chart_df = chart_builder(chart_source, metric)
        if chart_df.empty:
            continue
        st.markdown(f"**{metric.replace('_', '-').title()} comparison**")
        st.bar_chart(chart_df)


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
