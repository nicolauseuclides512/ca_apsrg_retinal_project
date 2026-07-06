import numpy as np

from src.evaluation.metrics import compute_metrics


def test_compute_metrics_perfect_prediction():
    gt = np.array([[1, 0], [1, 0]], dtype=bool)
    pred = gt.copy()
    m = compute_metrics(pred, gt)
    assert m.tp == 2
    assert m.tn == 2
    assert m.fp == 0
    assert m.fn == 0
    assert m.accuracy == 1.0
