from __future__ import annotations

from typing import Optional

import cv2
import numpy as np

from src.utils.image_io import apply_fov_mask


def green_channel(image_rgb: np.ndarray) -> np.ndarray:
    """Retinal vessels are usually more visible in the green channel."""
    return image_rgb[:, :, 1]


def normalize_uint8(gray: np.ndarray) -> np.ndarray:
    gray = gray.astype(np.float32)
    min_val = float(gray.min())
    max_val = float(gray.max())
    if max_val - min_val < 1e-8:
        return np.zeros_like(gray, dtype=np.uint8)
    norm = (gray - min_val) / (max_val - min_val)
    return (norm * 255).astype(np.uint8)


def apply_clahe(gray: np.ndarray, clip_limit: float = 2.0, tile_grid_size: tuple[int, int] = (8, 8)) -> np.ndarray:
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    return clahe.apply(gray.astype(np.uint8))


def preprocess_fundus(
    image_rgb: np.ndarray,
    fov_mask: Optional[np.ndarray] = None,
    *,
    use_green: bool = True,
    use_clahe: bool = True,
    clahe_clip_limit: float = 2.0,
    clahe_tile_grid_size: tuple[int, int] = (8, 8),
) -> np.ndarray:
    """Basic preprocessing for retinal vessel segmentation."""
    gray = green_channel(image_rgb) if use_green else cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    gray = normalize_uint8(gray)

    if use_clahe:
        gray = apply_clahe(gray, clip_limit=clahe_clip_limit, tile_grid_size=clahe_tile_grid_size)

    gray = apply_fov_mask(gray, fov_mask)
    return gray
