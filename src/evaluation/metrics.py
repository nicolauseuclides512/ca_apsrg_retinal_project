"""
Evaluation metrics for retinal blood vessel segmentation.

This module evaluates binary vessel masks produced by APSRG baseline and
CA-APSRG against manual vessel annotations.

Conventions:
- Ground truth foreground vessel pixels are True or > threshold.
- Prediction foreground vessel pixels are True or > threshold.
- Optional FoV mask restricts the evaluation to the valid retinal area.
- Metrics are computed at pixel level.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Optional

import numpy as np
import pandas as pd

from src.utils.image_io import ensure_binary_mask, read_binary_mask, resize_if_needed


@dataclass(frozen=True)
class BinaryConfusionMatrix:
    """Pixel-level confusion matrix for binary segmentation."""

    tp: int
    fp: int
    tn: int
    fn: int

    @property
    def total(self) -> int:
        """Total number of evaluated pixels."""
        return int(self.tp + self.fp + self.tn + self.fn)

    @property
    def predicted_positive(self) -> int:
        """Number of predicted vessel pixels."""
        return int(self.tp + self.fp)

    @property
    def predicted_negative(self) -> int:
        """Number of predicted background pixels."""
        return int(self.tn + self.fn)

    @property
    def actual_positive(self) -> int:
        """Number of manual vessel pixels."""
        return int(self.tp + self.fn)

    @property
    def actual_negative(self) -> int:
        """Number of manual background pixels."""
        return int(self.tn + self.fp)


@dataclass
class SegmentationMetrics:
    """Main evaluation metrics for binary vessel segmentation."""

    accuracy: float
    precision: float
    recall: float
    specificity: float
    f1_score: float
    iou: float
    tp: int
    fp: int
    tn: int
    fn: int
    false_positive_rate: float = 0.0
    false_negative_rate: float = 0.0
    balanced_accuracy: float = 0.0
    dice: float = 0.0
    evaluated_pixels: int = 0
    predicted_vessel_pixels: int = 0
    gt_vessel_pixels: int = 0


def safe_divide(numerator: float, denominator: float, zero_division: float = 0.0) -> float:
    """Safely divide two numbers and return zero_division when denominator is zero."""
    if denominator == 0:
        return float(zero_division)
    return float(numerator / denominator)


def _validate_same_shape(
    pred_mask: np.ndarray,
    gt_mask: np.ndarray,
    fov_mask: Optional[np.ndarray] = None,
) -> None:
    """Raise ValueError when prediction, ground truth, or FoV mask shapes are inconsistent."""
    if pred_mask.shape != gt_mask.shape:
        raise ValueError(f"Prediction and ground truth must have same shape, got {pred_mask.shape} and {gt_mask.shape}")
    if fov_mask is not None and fov_mask.shape != gt_mask.shape:
        raise ValueError(f"FoV mask and ground truth must have same shape, got {fov_mask.shape} and {gt_mask.shape}")


def prepare_binary_arrays(
    pred_mask: np.ndarray,
    gt_mask: np.ndarray,
    fov_mask: Optional[np.ndarray] = None,
    *,
    threshold: int = 127,
    resize_prediction_to_gt: bool = False,
    resize_fov_to_gt: bool = False,
) -> tuple[np.ndarray, np.ndarray, Optional[np.ndarray]]:
    """
    Convert prediction, ground truth, and optional FoV into boolean arrays.
    """
    pred_arr = np.asarray(pred_mask)
    gt_arr = np.asarray(gt_mask)

    if resize_prediction_to_gt and pred_arr.shape[:2] != gt_arr.shape[:2]:
        pred_arr = resize_if_needed(pred_arr, gt_arr, interpolation="nearest")

    if fov_mask is not None:
        fov_arr = np.asarray(fov_mask)
        if resize_fov_to_gt and fov_arr.shape[:2] != gt_arr.shape[:2]:
            fov_arr = resize_if_needed(fov_arr, gt_arr, interpolation="nearest")
    else:
        fov_arr = None

    pred = ensure_binary_mask(pred_arr, threshold=threshold, return_uint8=False)
    gt = ensure_binary_mask(gt_arr, threshold=threshold, return_uint8=False)
    fov = ensure_binary_mask(fov_arr, threshold=threshold, return_uint8=False) if fov_arr is not None else None

    _validate_same_shape(pred, gt, fov)
    return pred, gt, fov


def flatten_inside_fov(
    pred: np.ndarray,
    gt: np.ndarray,
    fov: Optional[np.ndarray] = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Flatten prediction and ground truth, optionally restricted to FoV pixels."""
    if fov is not None:
        valid = np.asarray(fov).astype(bool)
        return pred[valid].reshape(-1), gt[valid].reshape(-1)

    return pred.reshape(-1), gt.reshape(-1)


def confusion_matrix_binary(
    pred_mask: np.ndarray,
    gt_mask: np.ndarray,
    fov_mask: Optional[np.ndarray] = None,
    *,
    threshold: int = 127,
    resize_prediction_to_gt: bool = False,
    resize_fov_to_gt: bool = False,
) -> BinaryConfusionMatrix:
    """Compute pixel-level TP, FP, TN, and FN for a binary segmentation mask."""
    pred, gt, fov = prepare_binary_arrays(
        pred_mask,
        gt_mask,
        fov_mask,
        threshold=threshold,
        resize_prediction_to_gt=resize_prediction_to_gt,
        resize_fov_to_gt=resize_fov_to_gt,
    )
    pred_flat, gt_flat = flatten_inside_fov(pred, gt, fov)

    tp = int(np.logical_and(pred_flat, gt_flat).sum())
    fp = int(np.logical_and(pred_flat, np.logical_not(gt_flat)).sum())
    tn = int(np.logical_and(np.logical_not(pred_flat), np.logical_not(gt_flat)).sum())
    fn = int(np.logical_and(np.logical_not(pred_flat), gt_flat).sum())

    return BinaryConfusionMatrix(tp=tp, fp=fp, tn=tn, fn=fn)


def accuracy(cm: BinaryConfusionMatrix) -> float:
    """Accuracy = (TP + TN) / (TP + FP + TN + FN)."""
    return safe_divide(cm.tp + cm.tn, cm.total)


def precision(cm: BinaryConfusionMatrix) -> float:
    """Precision = TP / (TP + FP)."""
    return safe_divide(cm.tp, cm.tp + cm.fp)


def recall(cm: BinaryConfusionMatrix) -> float:
    """Recall/Sensitivity = TP / (TP + FN)."""
    return safe_divide(cm.tp, cm.tp + cm.fn)


def sensitivity(cm: BinaryConfusionMatrix) -> float:
    """Alias for recall."""
    return recall(cm)


def specificity(cm: BinaryConfusionMatrix) -> float:
    """Specificity = TN / (TN + FP)."""
    return safe_divide(cm.tn, cm.tn + cm.fp)


def false_positive_rate(cm: BinaryConfusionMatrix) -> float:
    """False positive rate = FP / (FP + TN)."""
    return safe_divide(cm.fp, cm.fp + cm.tn)


def false_negative_rate(cm: BinaryConfusionMatrix) -> float:
    """False negative rate = FN / (FN + TP)."""
    return safe_divide(cm.fn, cm.fn + cm.tp)


def f1_score(cm: BinaryConfusionMatrix) -> float:
    """F1-score/Dice coefficient = 2TP / (2TP + FP + FN)."""
    return safe_divide(2 * cm.tp, 2 * cm.tp + cm.fp + cm.fn)


def dice_coefficient(cm: BinaryConfusionMatrix) -> float:
    """Alias for F1-score in binary segmentation."""
    return f1_score(cm)


def iou(cm: BinaryConfusionMatrix) -> float:
    """Intersection over Union/Jaccard index = TP / (TP + FP + FN)."""
    return safe_divide(cm.tp, cm.tp + cm.fp + cm.fn)


def balanced_accuracy(cm: BinaryConfusionMatrix) -> float:
    """Balanced accuracy = (recall + specificity) / 2."""
    return 0.5 * (recall(cm) + specificity(cm))


def evaluate_from_confusion_matrix(cm: BinaryConfusionMatrix) -> SegmentationMetrics:
    """Convert a binary confusion matrix into a complete metric object."""
    return SegmentationMetrics(
        accuracy=float(accuracy(cm)),
        precision=float(precision(cm)),
        recall=float(recall(cm)),
        specificity=float(specificity(cm)),
        f1_score=float(f1_score(cm)),
        iou=float(iou(cm)),
        tp=int(cm.tp),
        fp=int(cm.fp),
        tn=int(cm.tn),
        fn=int(cm.fn),
        false_positive_rate=float(false_positive_rate(cm)),
        false_negative_rate=float(false_negative_rate(cm)),
        balanced_accuracy=float(balanced_accuracy(cm)),
        dice=float(dice_coefficient(cm)),
        evaluated_pixels=int(cm.total),
        predicted_vessel_pixels=int(cm.predicted_positive),
        gt_vessel_pixels=int(cm.actual_positive),
    )


def evaluate_segmentation(
    pred_mask: np.ndarray,
    gt_mask: np.ndarray,
    fov_mask: Optional[np.ndarray] = None,
    *,
    threshold: int = 127,
    resize_prediction_to_gt: bool = False,
    resize_fov_to_gt: bool = False,
) -> SegmentationMetrics:
    """Evaluate one predicted vessel mask against a manual ground-truth mask."""
    cm = confusion_matrix_binary(
        pred_mask,
        gt_mask,
        fov_mask,
        threshold=threshold,
        resize_prediction_to_gt=resize_prediction_to_gt,
        resize_fov_to_gt=resize_fov_to_gt,
    )
    return evaluate_from_confusion_matrix(cm)


def compute_metrics(
    pred_mask: np.ndarray,
    gt_mask: np.ndarray,
    fov_mask: Optional[np.ndarray] = None,
    *,
    threshold: int = 127,
) -> SegmentationMetrics:
    """Backward-compatible alias for evaluate_segmentation()."""
    return evaluate_segmentation(pred_mask, gt_mask, fov_mask, threshold=threshold)


def metrics_to_dict(metrics: SegmentationMetrics) -> dict[str, Any]:
    """Convert SegmentationMetrics into a serializable dictionary."""
    return asdict(metrics)


def confusion_matrix_to_dict(cm: BinaryConfusionMatrix) -> dict[str, int]:
    """Convert BinaryConfusionMatrix into a serializable dictionary."""
    return asdict(cm)


def evaluate_segmentation_files(
    pred_path: str | Path,
    gt_path: str | Path,
    fov_path: str | Path | None = None,
    *,
    threshold: int = 127,
) -> SegmentationMetrics:
    """Read prediction, ground truth, and optional FoV files, then evaluate them."""
    pred = read_binary_mask(pred_path, threshold=threshold)
    gt = read_binary_mask(gt_path, threshold=threshold)
    fov = read_binary_mask(fov_path, threshold=threshold) if fov_path else None
    return evaluate_segmentation(pred, gt, fov, threshold=threshold)


def add_metadata_to_metrics(
    metrics: SegmentationMetrics,
    *,
    dataset: str = "",
    image_id: str = "",
    method: str = "",
    image_path: str = "",
    mask_path: str = "",
    fov_path: str = "",
) -> dict[str, Any]:
    """Return metrics dictionary plus useful experiment metadata."""
    row = {
        "dataset": dataset,
        "image_id": image_id,
        "method": method,
        "image_path": image_path,
        "mask_path": mask_path,
        "fov_path": fov_path,
    }
    row.update(metrics_to_dict(metrics))
    return row


def summarize_metric_rows(rows: Iterable[dict[str, Any]], group_by: str | list[str] = "method") -> pd.DataFrame:
    """Summarize metric rows by method, dataset, or both."""
    df = pd.DataFrame(list(rows))
    if df.empty:
        return pd.DataFrame()

    group_cols = [group_by] if isinstance(group_by, str) else list(group_by)
    metric_cols = [
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
    available_metrics = [col for col in metric_cols if col in df.columns]

    summary = df.groupby(group_cols, dropna=False)[available_metrics].agg(["mean", "std", "min", "max"])
    summary.columns = [f"{metric}_{stat}" for metric, stat in summary.columns]
    summary = summary.reset_index()

    count_df = df.groupby(group_cols, dropna=False).size().reset_index(name="n_images")
    summary = count_df.merge(summary, on=group_cols, how="left")
    return summary