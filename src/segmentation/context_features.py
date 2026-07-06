"""
Context feature extraction for CA-APSRG retinal vessel segmentation.

This module analyzes the preliminary APSRG vessel mask and extracts contextual
information used by the CA-APSRG refinement stage.

The proposal states that CA-APSRG should adapt the morphological refinement
parameters based on local/structural characteristics of the preliminary vessel
segmentation, especially:
- vessel density,
- connected component statistics,
- small component ratio,
- structure continuity indicators.

Conventions:
- Input vessel mask: bool or 0/255 uint8, shape (H, W).
- Optional FoV mask: bool or 0/255 uint8, shape (H, W).
- All computations can be restricted to valid pixels inside FoV.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

import cv2
import numpy as np
import pandas as pd
from skimage.morphology import skeletonize

from src.utils.image_io import ensure_binary_mask, read_binary_mask, resize_if_needed


@dataclass(frozen=True)
class ContextFeatureConfig:
    """Configuration for extracting context features from a vessel mask."""

    small_component_area: int = 12
    connectivity: int = 8
    compute_skeleton_features: bool = True
    resize_fov_to_mask: bool = False

    @classmethod
    def from_dict(cls, config: dict[str, Any] | None) -> "ContextFeatureConfig":
        """Create ContextFeatureConfig from config['context_features']."""
        if not config:
            return cls()

        return cls(
            small_component_area=int(config.get("small_component_area", 12)),
            connectivity=int(config.get("connectivity", 8)),
            compute_skeleton_features=bool(config.get("compute_skeleton_features", True)),
            resize_fov_to_mask=bool(config.get("resize_fov_to_mask", False)),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return config as a dictionary."""
        return asdict(self)


@dataclass
class ComponentStatistics:
    """Connected component statistics for the preliminary vessel mask."""

    component_count: int
    total_component_area: int
    small_component_count: int
    small_component_area_total: int
    small_component_ratio: float
    small_component_area_ratio: float
    mean_component_area: float
    median_component_area: float
    std_component_area: float
    min_component_area: int
    max_component_area: int
    largest_component_area: int
    largest_component_area_ratio: float

    def to_dict(self) -> dict[str, Any]:
        """Return statistics as a dictionary."""
        return asdict(self)


@dataclass
class SkeletonStatistics:
    """Simple skeleton-based structure indicators."""

    skeleton_pixel_count: int
    skeleton_to_vessel_ratio: float
    endpoint_count: int
    branchpoint_count: int
    endpoint_density: float
    branchpoint_density: float

    def to_dict(self) -> dict[str, Any]:
        """Return statistics as a dictionary."""
        return asdict(self)


@dataclass
class ContextFeatures:
    """Context descriptor used by CA-APSRG adaptive morphology."""

    vessel_density: float
    vessel_pixel_count: int
    valid_area_pixel_count: int

    component_count: int
    mean_component_area: float
    median_component_area: float
    std_component_area: float
    min_component_area: int
    max_component_area: int

    small_component_count: int
    small_component_ratio: float
    small_component_area_total: int
    small_component_area_ratio: float

    largest_component_area: int
    largest_component_area_ratio: float

    skeleton_pixel_count: int = 0
    skeleton_to_vessel_ratio: float = 0.0
    endpoint_count: int = 0
    branchpoint_count: int = 0
    endpoint_density: float = 0.0
    branchpoint_density: float = 0.0

    density_level: str = "normal"
    noise_level: str = "normal"
    recommended_refinement_level: str = "normal"

    def to_dict(self) -> dict[str, Any]:
        """Return features as a dictionary."""
        return asdict(self)


ContextFeature = ContextFeatures


def _validate_connectivity(connectivity: int) -> int:
    """Validate OpenCV connectivity value."""
    connectivity = int(connectivity)
    if connectivity not in {4, 8}:
        raise ValueError("connectivity must be either 4 or 8")
    return connectivity


def _prepare_mask_and_fov(
    mask: np.ndarray,
    fov_mask: Optional[np.ndarray] = None,
    *,
    resize_fov_to_mask: bool = False,
) -> tuple[np.ndarray, Optional[np.ndarray], np.ndarray]:
    """
    Prepare binary mask, optional FoV, and final valid area mask.

    Returns
    -------
    vessel_mask:
        Boolean vessel mask restricted to FoV when FoV is supplied.
    fov:
        Boolean FoV mask or None.
    valid_area:
        Boolean mask defining pixels included in context computation.
    """
    vessel_mask = ensure_binary_mask(mask, return_uint8=False)

    if fov_mask is not None:
        fov = ensure_binary_mask(fov_mask, return_uint8=False)

        if fov.shape != vessel_mask.shape:
            if resize_fov_to_mask:
                fov = resize_if_needed(fov.astype(np.uint8), vessel_mask, interpolation="nearest") > 0
            else:
                raise ValueError(f"FoV mask shape {fov.shape} does not match vessel mask shape {vessel_mask.shape}")

        valid_area = fov.astype(bool)
        vessel_mask = vessel_mask & valid_area
    else:
        fov = None
        valid_area = np.ones(vessel_mask.shape, dtype=bool)

    return vessel_mask.astype(bool), fov, valid_area.astype(bool)


def compute_vessel_density(mask: np.ndarray, valid_area: Optional[np.ndarray] = None) -> tuple[float, int, int]:
    """
    Compute vessel density inside valid area.

    Vessel density = number of vessel pixels / number of valid pixels.
    """
    vessel = ensure_binary_mask(mask, return_uint8=False)

    if valid_area is None:
        valid = np.ones(vessel.shape, dtype=bool)
    else:
        valid = ensure_binary_mask(valid_area, return_uint8=False)
        if valid.shape != vessel.shape:
            raise ValueError(f"valid_area shape {valid.shape} does not match mask shape {vessel.shape}")

    valid_area_pixel_count = int(valid.sum())
    if valid_area_pixel_count <= 0:
        return 0.0, 0, 0

    vessel_pixel_count = int((vessel & valid).sum())
    vessel_density = float(vessel_pixel_count / valid_area_pixel_count)

    return vessel_density, vessel_pixel_count, valid_area_pixel_count


def connected_component_areas(mask: np.ndarray, *, connectivity: int = 8) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute connected component labels, stats, and component areas.

    Returns
    -------
    labels:
        Label image from cv2.connectedComponentsWithStats.
    stats:
        Component stats. Row 0 is background.
    areas:
        Foreground component areas only, excluding background.
    """
    conn = _validate_connectivity(connectivity)
    mask_u8 = ensure_binary_mask(mask, return_uint8=False).astype(np.uint8)

    n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask_u8, connectivity=conn)

    if n_labels <= 1:
        areas = np.array([], dtype=np.int64)
    else:
        areas = stats[1:, cv2.CC_STAT_AREA].astype(np.int64)

    return labels, stats, areas


def compute_component_statistics(
    mask: np.ndarray,
    *,
    small_component_area: int = 12,
    connectivity: int = 8,
) -> ComponentStatistics:
    """Compute connected component statistics for a binary vessel mask."""
    _, _, areas = connected_component_areas(mask, connectivity=connectivity)

    component_count = int(len(areas))
    total_component_area = int(areas.sum()) if component_count > 0 else 0

    if component_count == 0:
        return ComponentStatistics(
            component_count=0,
            total_component_area=0,
            small_component_count=0,
            small_component_area_total=0,
            small_component_ratio=0.0,
            small_component_area_ratio=0.0,
            mean_component_area=0.0,
            median_component_area=0.0,
            std_component_area=0.0,
            min_component_area=0,
            max_component_area=0,
            largest_component_area=0,
            largest_component_area_ratio=0.0,
        )

    small_area = int(small_component_area)
    small_mask = areas < small_area
    small_component_count = int(small_mask.sum())
    small_component_area_total = int(areas[small_mask].sum()) if small_component_count > 0 else 0

    largest_component_area = int(areas.max())

    return ComponentStatistics(
        component_count=component_count,
        total_component_area=total_component_area,
        small_component_count=small_component_count,
        small_component_area_total=small_component_area_total,
        small_component_ratio=float(small_component_count / component_count),
        small_component_area_ratio=float(small_component_area_total / total_component_area) if total_component_area > 0 else 0.0,
        mean_component_area=float(np.mean(areas)),
        median_component_area=float(np.median(areas)),
        std_component_area=float(np.std(areas)),
        min_component_area=int(areas.min()),
        max_component_area=int(areas.max()),
        largest_component_area=largest_component_area,
        largest_component_area_ratio=float(largest_component_area / total_component_area) if total_component_area > 0 else 0.0,
    )


def _count_skeleton_neighbors(skeleton: np.ndarray) -> np.ndarray:
    """Count 8-neighbors for each skeleton pixel."""
    skel_u8 = skeleton.astype(np.uint8)
    kernel = np.array(
        [
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1],
        ],
        dtype=np.uint8,
    )
    return cv2.filter2D(skel_u8, ddepth=cv2.CV_16S, kernel=kernel, borderType=cv2.BORDER_CONSTANT)


def compute_skeleton_statistics(mask: np.ndarray) -> SkeletonStatistics:
    """
    Compute simple skeleton statistics.

    These indicators are not the main evaluation metrics. They are used only as
    additional context for adaptive refinement, especially to avoid removing
    thin structures too aggressively.
    """
    vessel = ensure_binary_mask(mask, return_uint8=False)
    vessel_pixel_count = int(vessel.sum())

    if vessel_pixel_count == 0:
        return SkeletonStatistics(
            skeleton_pixel_count=0,
            skeleton_to_vessel_ratio=0.0,
            endpoint_count=0,
            branchpoint_count=0,
            endpoint_density=0.0,
            branchpoint_density=0.0,
        )

    skeleton = skeletonize(vessel).astype(bool)
    skeleton_pixel_count = int(skeleton.sum())

    if skeleton_pixel_count == 0:
        return SkeletonStatistics(
            skeleton_pixel_count=0,
            skeleton_to_vessel_ratio=0.0,
            endpoint_count=0,
            branchpoint_count=0,
            endpoint_density=0.0,
            branchpoint_density=0.0,
        )

    neighbor_count = _count_skeleton_neighbors(skeleton)
    endpoint_count = int(((neighbor_count == 1) & skeleton).sum())
    branchpoint_count = int(((neighbor_count >= 3) & skeleton).sum())

    return SkeletonStatistics(
        skeleton_pixel_count=skeleton_pixel_count,
        skeleton_to_vessel_ratio=float(skeleton_pixel_count / vessel_pixel_count),
        endpoint_count=endpoint_count,
        branchpoint_count=branchpoint_count,
        endpoint_density=float(endpoint_count / skeleton_pixel_count),
        branchpoint_density=float(branchpoint_count / skeleton_pixel_count),
    )


def classify_vessel_density(
    vessel_density: float,
    *,
    low_density_threshold: float = 0.025,
    high_density_threshold: float = 0.120,
) -> str:
    """Classify vessel density into low, normal, or high."""
    if vessel_density < float(low_density_threshold):
        return "low"
    if vessel_density > float(high_density_threshold):
        return "high"
    return "normal"


def classify_noise_level(
    small_component_ratio: float,
    small_component_area_ratio: float,
    *,
    ratio_threshold: float = 0.35,
    area_ratio_threshold: float = 0.10,
) -> str:
    """
    Estimate whether the preliminary mask contains many isolated small objects.

    This is a proxy for possible false positive noise when ground truth is not
    available.
    """
    if small_component_ratio >= ratio_threshold or small_component_area_ratio >= area_ratio_threshold:
        return "high"
    if small_component_ratio >= ratio_threshold * 0.5 or small_component_area_ratio >= area_ratio_threshold * 0.5:
        return "medium"
    return "low"


def recommend_refinement_level(density_level: str, noise_level: str) -> str:
    """
    Recommend an adaptive morphology refinement level.

    The rule is intentionally interpretable:
    - low-density masks should be refined conservatively to preserve thin vessels,
    - high-noise masks can be refined more aggressively,
    - otherwise use normal refinement.
    """
    density_level = str(density_level).lower()
    noise_level = str(noise_level).lower()

    if density_level == "low" and noise_level in {"low", "medium"}:
        return "conservative"

    if noise_level == "high" and density_level != "low":
        return "aggressive"

    if density_level == "high" and noise_level in {"medium", "high"}:
        return "aggressive"

    return "normal"


def extract_context_features(
    mask: np.ndarray,
    fov_mask: np.ndarray | None = None,
    small_area_limit: int | None = None,
    *,
    config: ContextFeatureConfig | None = None,
    low_density_threshold: float = 0.025,
    high_density_threshold: float = 0.120,
) -> ContextFeatures:
    """
    Extract context features from a preliminary APSRG vessel mask.

    Parameters
    ----------
    mask:
        Preliminary vessel mask from APSRG baseline.
    fov_mask:
        Optional field-of-view mask. If supplied, all feature computations are
        restricted to valid FoV pixels.
    small_area_limit:
        Backward-compatible override for small component area threshold.
    config:
        ContextFeatureConfig object.
    low_density_threshold, high_density_threshold:
        Thresholds used to categorize density level.
    """
    cfg = config or ContextFeatureConfig()

    if small_area_limit is not None:
        cfg = ContextFeatureConfig(
            small_component_area=int(small_area_limit),
            connectivity=cfg.connectivity,
            compute_skeleton_features=cfg.compute_skeleton_features,
            resize_fov_to_mask=cfg.resize_fov_to_mask,
        )

    vessel_mask, _, valid_area = _prepare_mask_and_fov(
        mask,
        fov_mask=fov_mask,
        resize_fov_to_mask=cfg.resize_fov_to_mask,
    )

    vessel_density, vessel_pixel_count, valid_area_pixel_count = compute_vessel_density(vessel_mask, valid_area)

    component_stats = compute_component_statistics(
        vessel_mask,
        small_component_area=cfg.small_component_area,
        connectivity=cfg.connectivity,
    )

    if cfg.compute_skeleton_features:
        skeleton_stats = compute_skeleton_statistics(vessel_mask)
    else:
        skeleton_stats = SkeletonStatistics(
            skeleton_pixel_count=0,
            skeleton_to_vessel_ratio=0.0,
            endpoint_count=0,
            branchpoint_count=0,
            endpoint_density=0.0,
            branchpoint_density=0.0,
        )

    density_level = classify_vessel_density(
        vessel_density,
        low_density_threshold=low_density_threshold,
        high_density_threshold=high_density_threshold,
    )
    noise_level = classify_noise_level(
        component_stats.small_component_ratio,
        component_stats.small_component_area_ratio,
    )
    refinement_level = recommend_refinement_level(density_level, noise_level)

    return ContextFeatures(
        vessel_density=float(vessel_density),
        vessel_pixel_count=int(vessel_pixel_count),
        valid_area_pixel_count=int(valid_area_pixel_count),
        component_count=int(component_stats.component_count),
        mean_component_area=float(component_stats.mean_component_area),
        median_component_area=float(component_stats.median_component_area),
        std_component_area=float(component_stats.std_component_area),
        min_component_area=int(component_stats.min_component_area),
        max_component_area=int(component_stats.max_component_area),
        small_component_count=int(component_stats.small_component_count),
        small_component_ratio=float(component_stats.small_component_ratio),
        small_component_area_total=int(component_stats.small_component_area_total),
        small_component_area_ratio=float(component_stats.small_component_area_ratio),
        largest_component_area=int(component_stats.largest_component_area),
        largest_component_area_ratio=float(component_stats.largest_component_area_ratio),
        skeleton_pixel_count=int(skeleton_stats.skeleton_pixel_count),
        skeleton_to_vessel_ratio=float(skeleton_stats.skeleton_to_vessel_ratio),
        endpoint_count=int(skeleton_stats.endpoint_count),
        branchpoint_count=int(skeleton_stats.branchpoint_count),
        endpoint_density=float(skeleton_stats.endpoint_density),
        branchpoint_density=float(skeleton_stats.branchpoint_density),
        density_level=density_level,
        noise_level=noise_level,
        recommended_refinement_level=refinement_level,
    )


def extract_context_features_from_files(
    mask_path: str | Path,
    fov_path: str | Path | None = None,
    *,
    config: ContextFeatureConfig | None = None,
    low_density_threshold: float = 0.025,
    high_density_threshold: float = 0.120,
) -> ContextFeatures:
    """Read mask and optional FoV mask from disk, then extract context features."""
    mask = read_binary_mask(mask_path)
    fov = read_binary_mask(fov_path) if fov_path else None

    return extract_context_features(
        mask,
        fov_mask=fov,
        config=config,
        low_density_threshold=low_density_threshold,
        high_density_threshold=high_density_threshold,
    )


def context_features_to_dict(features: ContextFeatures) -> dict[str, Any]:
    """Convert ContextFeatures object to dictionary."""
    return features.to_dict()


def build_context_feature_row(
    features: ContextFeatures,
    *,
    dataset: str = "",
    image_id: str = "",
    method: str = "APSRG",
    mask_path: str = "",
    fov_path: str = "",
) -> dict[str, Any]:
    """Return context feature row with metadata for CSV export."""
    row: dict[str, Any] = {
        "dataset": dataset,
        "image_id": image_id,
        "method": method,
        "mask_path": mask_path,
        "fov_path": fov_path,
    }
    row.update(features.to_dict())
    return row


def summarize_context_feature_rows(rows: list[dict[str, Any]], group_by: str | list[str] = "dataset") -> pd.DataFrame:
    """Summarize context features by dataset or method."""
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame()

    group_cols = [group_by] if isinstance(group_by, str) else list(group_by)
    numeric_cols = [
        "vessel_density",
        "vessel_pixel_count",
        "component_count",
        "mean_component_area",
        "median_component_area",
        "small_component_ratio",
        "small_component_area_ratio",
        "largest_component_area_ratio",
        "skeleton_to_vessel_ratio",
        "endpoint_density",
        "branchpoint_density",
    ]
    available_numeric_cols = [col for col in numeric_cols if col in df.columns]

    summary = df.groupby(group_cols, dropna=False)[available_numeric_cols].agg(["mean", "std", "min", "max"])
    summary.columns = [f"{metric}_{stat}" for metric, stat in summary.columns]
    summary = summary.reset_index()

    count_df = df.groupby(group_cols, dropna=False).size().reset_index(name="n_images")
    return count_df.merge(summary, on=group_cols, how="left")


compute_context_features = extract_context_features
extract_features = extract_context_features