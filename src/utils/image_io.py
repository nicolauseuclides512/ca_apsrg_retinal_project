from __future__ import annotations

from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from PIL import Image


def ensure_dir(path: str | Path) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_rgb(path: str | Path) -> np.ndarray:
    """Read image as RGB uint8."""
    path = Path(path)
    img = Image.open(path).convert("RGB")
    return np.array(img, dtype=np.uint8)


def read_gray(path: str | Path) -> np.ndarray:
    """Read image as grayscale uint8."""
    path = Path(path)
    img = Image.open(path).convert("L")
    return np.array(img, dtype=np.uint8)


def read_binary_mask(path: str | Path, threshold: int = 127) -> np.ndarray:
    """Read a binary mask and return bool array."""
    gray = read_gray(path)
    return gray > threshold


def save_png_uint8(path: str | Path, image: np.ndarray) -> None:
    """Save uint8 image to PNG."""
    path = Path(path)
    ensure_dir(path.parent)

    arr = np.asarray(image)
    if arr.dtype == bool:
        arr = arr.astype(np.uint8) * 255
    elif arr.dtype != np.uint8:
        arr = np.clip(arr, 0, 255).astype(np.uint8)

    Image.fromarray(arr).save(path, format="PNG")


def save_binary_mask(path: str | Path, mask: np.ndarray) -> None:
    """Save bool/binary mask as 0/255 PNG."""
    arr = (mask > 0).astype(np.uint8) * 255
    save_png_uint8(path, arr)


def apply_fov_mask(image_or_mask: np.ndarray, fov_mask: Optional[np.ndarray]) -> np.ndarray:
    """Set pixels outside FoV to zero."""
    if fov_mask is None:
        return image_or_mask

    result = image_or_mask.copy()
    if result.ndim == 2:
        result[~fov_mask] = 0
    else:
        result[~fov_mask, :] = 0
    return result


def overlay_mask_on_image(image_rgb: np.ndarray, mask: np.ndarray, alpha: float = 0.45) -> np.ndarray:
    """Create simple overlay for visual inspection. Vessel mask is shown in bright channel."""
    image = image_rgb.copy().astype(np.float32)
    overlay = image.copy()
    overlay[mask > 0] = [255, 0, 0]
    blended = (1 - alpha) * image + alpha * overlay
    return np.clip(blended, 0, 255).astype(np.uint8)
