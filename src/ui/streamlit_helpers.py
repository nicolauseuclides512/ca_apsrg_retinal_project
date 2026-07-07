"""Helper utilities for the CA-APSRG Streamlit demo."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
import pandas as pd
import streamlit as st
import yaml
from PIL import Image, ImageOps


METRIC_COLUMNS = ["accuracy", "precision", "recall", "specificity", "f1_score", "iou"]
CONTEXT_KEYS = [
    "vessel_density",
    "component_count",
    "small_component_ratio",
    "small_component_area_ratio",
    "density_level",
    "noise_level",
    "recommended_refinement_level",
]


def load_yaml_config(config_path: str | Path) -> dict[str, Any]:
    """Load a YAML configuration file and return an empty dict when missing."""
    path = Path(config_path)
    if not path.is_file():
        return {}

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    return data or {}


def pil_to_rgb_array(uploaded_file: Any) -> np.ndarray:
    """Read a Streamlit uploaded image as RGB uint8."""
    uploaded_file.seek(0)
    with Image.open(uploaded_file) as image:
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")
        return np.asarray(image, dtype=np.uint8)


def pil_to_gray_array(uploaded_file: Any) -> np.ndarray:
    """Read a Streamlit uploaded image as grayscale uint8."""
    uploaded_file.seek(0)
    with Image.open(uploaded_file) as image:
        image = ImageOps.exif_transpose(image)
        image = image.convert("L")
        return np.asarray(image, dtype=np.uint8)


def ensure_display_mask(mask: np.ndarray | None) -> np.ndarray | None:
    """Convert a binary-like mask to visible 0/255 uint8 values."""
    if mask is None:
        return None

    arr = np.asarray(mask)
    if arr.ndim == 3:
        arr = arr[..., 0]

    if arr.dtype == np.bool_:
        return arr.astype(np.uint8) * 255

    if arr.size and float(np.nanmax(arr)) <= 1.0:
        return (arr > 0).astype(np.uint8) * 255

    if np.issubdtype(arr.dtype, np.floating):
        arr = np.nan_to_num(arr, nan=0.0, posinf=255.0, neginf=0.0)
        if arr.size and float(arr.max()) <= 1.0:
            return (arr > 0.5).astype(np.uint8) * 255

    return (arr > 127).astype(np.uint8) * 255


def _to_plain_dict(value: Any) -> dict[str, Any]:
    """Convert metric/debug dataclasses or mappings into a plain dictionary."""
    if value is None:
        return {}
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return dict(value)
    if hasattr(value, "to_dict"):
        return dict(value.to_dict())
    return {}


def make_metrics_dataframe(baseline_metrics: Any, ca_metrics: Any) -> pd.DataFrame:
    """Build a compact APSRG vs CA-APSRG metric comparison table."""
    baseline = _to_plain_dict(baseline_metrics)
    ca = _to_plain_dict(ca_metrics)
    rows: list[dict[str, Any]] = []

    for metric in METRIC_COLUMNS:
        baseline_value = baseline.get(metric)
        ca_value = ca.get(metric)
        delta = None
        if baseline_value is not None and ca_value is not None:
            delta = float(ca_value) - float(baseline_value)

        rows.append(
            {
                "metric": metric,
                "APSRG baseline": baseline_value,
                "CA-APSRG": ca_value,
                "delta (CA - APSRG)": delta,
            }
        )

    return pd.DataFrame(rows)


def _find_selected_parameters(debug: dict[str, Any]) -> dict[str, Any]:
    """Extract selected morphology parameters from known debug layouts."""
    direct = debug.get("selected_parameters")
    if isinstance(direct, dict):
        return direct

    refinement_debug = debug.get("refinement_debug")
    if isinstance(refinement_debug, dict):
        selected = refinement_debug.get("selected_parameters")
        if isinstance(selected, dict):
            return selected

    return {}


def make_context_dataframe(debug: dict[str, Any]) -> pd.DataFrame:
    """Build a context/debug feature table from CA-APSRG debug info."""
    context = debug.get("context_features", {}) if isinstance(debug, dict) else {}
    refined = debug.get("refined_context_features", {}) if isinstance(debug, dict) else {}
    selected = _find_selected_parameters(debug if isinstance(debug, dict) else {})

    rows: list[dict[str, Any]] = []
    for key in CONTEXT_KEYS:
        rows.append(
            {
                "item": key,
                "APSRG baseline": context.get(key) if isinstance(context, dict) else None,
                "CA-APSRG refined": refined.get(key) if isinstance(refined, dict) else None,
                "selected morphology parameter": None,
            }
        )

    for key, value in selected.items():
        rows.append(
            {
                "item": key,
                "APSRG baseline": None,
                "CA-APSRG refined": None,
                "selected morphology parameter": value,
            }
        )

    return pd.DataFrame(rows)


def show_image_grid(title_image_pairs: Sequence[tuple[str, np.ndarray | None]], columns: int = 3) -> None:
    """Display images in a simple Streamlit grid."""
    pairs = [(title, image) for title, image in title_image_pairs if image is not None]
    if not pairs:
        return

    columns = max(int(columns), 1)
    for start in range(0, len(pairs), columns):
        cols = st.columns(columns)
        for col, (title, image) in zip(cols, pairs[start : start + columns]):
            with col:
                st.image(image, caption=title, width="stretch")


def safe_read_csv(path: str | Path) -> pd.DataFrame | None:
    """Read a CSV file if it exists; return None on missing or parse failure."""
    path = Path(path)
    if not path.is_file():
        return None

    try:
        return pd.read_csv(path)
    except Exception:
        return None


def file_exists(path: str | Path) -> bool:
    """Return True when path points to an existing file."""
    return Path(path).is_file()


def numeric_mean(values: Iterable[Any]) -> float | None:
    """Return a numeric mean while ignoring non-numeric values."""
    series = pd.to_numeric(pd.Series(list(values)), errors="coerce").dropna()
    if series.empty:
        return None
    return float(series.mean())
