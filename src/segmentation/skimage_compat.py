"""Compatibility helpers for scikit-image morphology API changes."""

from __future__ import annotations

import numpy as np
from skimage.morphology import remove_small_holes


def remove_small_holes_compat(mask: np.ndarray, area_threshold: int) -> np.ndarray:
    """
    Fill holes using the scikit-image API without emitting deprecation warnings.

    scikit-image 0.26 renamed ``area_threshold`` to ``max_size`` and changed the
    boundary rule from "< threshold" to "<= max_size". Using ``threshold - 1``
    keeps the older behavior for existing experiment configs.
    """
    threshold = int(area_threshold)
    if threshold <= 0:
        return np.asarray(mask).astype(bool)

    try:
        return remove_small_holes(mask, max_size=max(threshold - 1, 0)).astype(bool)
    except TypeError:
        return remove_small_holes(mask, area_threshold=threshold).astype(bool)

