from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np


@dataclass
class SegmentationMetrics:
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


def compute_metrics(pred_mask: np.ndarray, gt_mask: np.ndarray, fov_mask: np.ndarray | None = None) -> SegmentationMetrics:
    pred = pred_mask > 0
    gt = gt_mask > 0

    if fov_mask is not None:
        valid = fov_mask > 0
        pred = pred[valid]
        gt = gt[valid]
    else:
        pred = pred.reshape(-1)
        gt = gt.reshape(-1)

    tp = int(np.logical_and(pred, gt).sum())
    fp = int(np.logical_and(pred, ~gt).sum())
    tn = int(np.logical_and(~pred, ~gt).sum())
    fn = int(np.logical_and(~pred, gt).sum())

    eps = 1e-12
    accuracy = (tp + tn) / max(tp + fp + tn + fn, 1)
    precision = tp / (tp + fp + eps)
    recall = tp / (tp + fn + eps)
    specificity = tn / (tn + fp + eps)
    f1 = 2 * precision * recall / (precision + recall + eps)
    iou = tp / (tp + fp + fn + eps)

    return SegmentationMetrics(
        accuracy=float(accuracy),
        precision=float(precision),
        recall=float(recall),
        specificity=float(specificity),
        f1_score=float(f1),
        iou=float(iou),
        tp=tp,
        fp=fp,
        tn=tn,
        fn=fn,
    )


def metrics_to_dict(metrics: SegmentationMetrics) -> dict:
    return asdict(metrics)
