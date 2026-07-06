"""
Preprocessing utilities for retinal fundus images in the CA-APSRG project.

This module prepares fundus images before APSRG baseline segmentation.
The default preprocessing flow is:

1. Read RGB fundus image.
2. Extract green channel, because retinal vessels are commonly clearer there.
3. Normalize intensity to uint8 [0, 255].
4. Apply CLAHE to improve local vessel contrast.
5. Apply optional denoising: none, median, or bilateral.
6. Apply optional FoV mask to remove pixels outside the retinal region.

Conventions:
- Input RGB image uses channel order RGB, not BGR.
- Output preprocessed image is grayscale uint8 with shape (H, W).
- FoV mask, when provided, can be bool or 0/255 uint8.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal, Optional

import cv2
import numpy as np

from src.utils.image_io import (
    apply_fov_mask as apply_fov_mask_to_array,
    normalize_to_uint8,
    read_binary_mask,
    read_rgb_image,
    save_png_uint8,
    to_uint8,
)

DenoiseMethod = Literal["none", "median", "bilateral"]


@dataclass(frozen=True)
class PreprocessConfig:
    """Configuration for retinal fundus preprocessing."""

    use_green_channel: bool = True
    normalize_intensity: bool = True
    apply_clahe: bool = True
    clahe_clip_limit: float = 2.0
    clahe_tile_grid_size: tuple[int, int] = (8, 8)

    denoise_method: DenoiseMethod = "median"
    median_kernel_size: int = 3

    bilateral_d: int = 5
    bilateral_sigma_color: float = 50.0
    bilateral_sigma_space: float = 50.0

    apply_fov_mask: bool = True

    @classmethod
    def from_dict(cls, config: dict[str, Any] | None) -> "PreprocessConfig":
        """Create PreprocessConfig from a dictionary, usually config['preprocessing']."""
        if not config:
            return cls()

        tile_grid = config.get("clahe_tile_grid_size", (8, 8))
        if isinstance(tile_grid, list):
            tile_grid = tuple(tile_grid)

        normalize_intensity = bool(config.get("normalize_intensity", config.get("normalize", True)))

        return cls(
            use_green_channel=bool(config.get("use_green_channel", True)),
            normalize_intensity=normalize_intensity,
            apply_clahe=bool(config.get("apply_clahe", True)),
            clahe_clip_limit=float(config.get("clahe_clip_limit", 2.0)),
            clahe_tile_grid_size=(int(tile_grid[0]), int(tile_grid[1])),
            denoise_method=str(config.get("denoise_method", "median")).lower(),
            median_kernel_size=int(config.get("median_kernel_size", 3)),
            bilateral_d=int(config.get("bilateral_d", 5)),
            bilateral_sigma_color=float(config.get("bilateral_sigma_color", 50.0)),
            bilateral_sigma_space=float(config.get("bilateral_sigma_space", 50.0)),
            apply_fov_mask=bool(config.get("apply_fov_mask", True)),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return the configuration as a serializable dictionary."""
        return asdict(self)


def validate_rgb_image(image_rgb: np.ndarray) -> np.ndarray:
    """Validate and return an RGB uint8 fundus image."""
    image = np.asarray(image_rgb)
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError(f"Expected RGB image with shape (H, W, 3), got {image.shape}")
    return to_uint8(image)


def extract_green_channel(image_rgb: np.ndarray) -> np.ndarray:
    """Extract green channel from RGB image as uint8."""
    image = validate_rgb_image(image_rgb)
    return image[:, :, 1].copy()


green_channel = extract_green_channel


def rgb_to_gray(image_rgb: np.ndarray) -> np.ndarray:
    """Convert RGB image to grayscale uint8."""
    image = validate_rgb_image(image_rgb)
    return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)


def normalize_uint8(gray: np.ndarray) -> np.ndarray:
    """Min-max normalize grayscale image to uint8 [0, 255]."""
    return normalize_to_uint8(gray)


def normalize_percentile_uint8(
    gray: np.ndarray,
    lower_percentile: float = 1.0,
    upper_percentile: float = 99.0,
) -> np.ndarray:
    """Percentile-based normalization to reduce the effect of extreme outliers."""
    arr = np.asarray(gray, dtype=np.float32)
    low = float(np.percentile(arr, lower_percentile))
    high = float(np.percentile(arr, upper_percentile))

    if high <= low:
        return np.zeros(arr.shape, dtype=np.uint8)

    arr = (arr - low) / (high - low)
    arr = np.clip(arr, 0.0, 1.0)
    return (arr * 255.0).round().astype(np.uint8)


def apply_clahe(
    gray: np.ndarray,
    clip_limit: float = 2.0,
    tile_grid_size: tuple[int, int] = (8, 8),
) -> np.ndarray:
    """Apply Contrast Limited Adaptive Histogram Equalization to grayscale image."""
    gray_u8 = to_uint8(gray)
    tile_grid_size = (int(tile_grid_size[0]), int(tile_grid_size[1]))
    clahe = cv2.createCLAHE(clipLimit=float(clip_limit), tileGridSize=tile_grid_size)
    return clahe.apply(gray_u8)


def _ensure_odd_kernel_size(kernel_size: int, minimum: int = 3) -> int:
    """Ensure a valid odd kernel size for OpenCV filters."""
    kernel_size = max(int(kernel_size), int(minimum))
    if kernel_size % 2 == 0:
        kernel_size += 1
    return kernel_size


def apply_median_filter(gray: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """Apply median filtering to reduce salt-and-pepper noise."""
    k = _ensure_odd_kernel_size(kernel_size, minimum=3)
    return cv2.medianBlur(to_uint8(gray), k)


def apply_bilateral_filter(
    gray: np.ndarray,
    d: int = 5,
    sigma_color: float = 50.0,
    sigma_space: float = 50.0,
) -> np.ndarray:
    """Apply bilateral filtering to smooth noise while preserving edges."""
    d = max(int(d), 1)
    return cv2.bilateralFilter(
        to_uint8(gray),
        d=d,
        sigmaColor=float(sigma_color),
        sigmaSpace=float(sigma_space),
    )


def denoise_image(
    gray: np.ndarray,
    method: DenoiseMethod = "median",
    *,
    median_kernel_size: int = 3,
    bilateral_d: int = 5,
    bilateral_sigma_color: float = 50.0,
    bilateral_sigma_space: float = 50.0,
) -> np.ndarray:
    """Apply the selected denoising method to a grayscale image."""
    method = str(method).lower()

    if method in {"none", "", "no", "false"}:
        return to_uint8(gray)

    if method == "median":
        return apply_median_filter(gray, kernel_size=median_kernel_size)

    if method == "bilateral":
        return apply_bilateral_filter(
            gray,
            d=bilateral_d,
            sigma_color=bilateral_sigma_color,
            sigma_space=bilateral_sigma_space,
        )

    raise ValueError(f"Unsupported denoise_method: {method}. Use 'none', 'median', or 'bilateral'.")


def select_initial_channel(image_rgb: np.ndarray, *, use_green_channel: bool = True) -> np.ndarray:
    """Select the grayscale base image for preprocessing."""
    return extract_green_channel(image_rgb) if use_green_channel else rgb_to_gray(image_rgb)


def preprocess_fundus(
    image_rgb: np.ndarray,
    fov_mask: Optional[np.ndarray] = None,
    *,
    config: PreprocessConfig | None = None,
    use_green: Optional[bool] = None,
    use_clahe: Optional[bool] = None,
    clahe_clip_limit: Optional[float] = None,
    clahe_tile_grid_size: Optional[tuple[int, int]] = None,
) -> np.ndarray:
    """
    Preprocess one RGB fundus image and return a grayscale uint8 image.

    Optional keyword arguments are kept for backward compatibility with the
    earlier skeleton version. If supplied, they override the config values.
    """
    cfg = config or PreprocessConfig()

    use_green_channel_value = cfg.use_green_channel if use_green is None else bool(use_green)
    apply_clahe_value = cfg.apply_clahe if use_clahe is None else bool(use_clahe)
    clip_limit_value = cfg.clahe_clip_limit if clahe_clip_limit is None else float(clahe_clip_limit)
    tile_grid_value = cfg.clahe_tile_grid_size if clahe_tile_grid_size is None else clahe_tile_grid_size

    gray = select_initial_channel(image_rgb, use_green_channel=use_green_channel_value)

    if cfg.normalize_intensity:
        gray = normalize_uint8(gray)
    else:
        gray = to_uint8(gray)

    if apply_clahe_value:
        gray = apply_clahe(gray, clip_limit=clip_limit_value, tile_grid_size=tile_grid_value)

    gray = denoise_image(
        gray,
        method=cfg.denoise_method,
        median_kernel_size=cfg.median_kernel_size,
        bilateral_d=cfg.bilateral_d,
        bilateral_sigma_color=cfg.bilateral_sigma_color,
        bilateral_sigma_space=cfg.bilateral_sigma_space,
    )

    if cfg.apply_fov_mask and fov_mask is not None:
        gray = apply_fov_mask_to_array(gray, fov_mask)

    return to_uint8(gray)


def preprocess_fundus_with_steps(
    image_rgb: np.ndarray,
    fov_mask: Optional[np.ndarray] = None,
    *,
    config: PreprocessConfig | None = None,
) -> dict[str, np.ndarray]:
    """
    Preprocess one image and return intermediate outputs for debugging.

    Returned keys:
    - selected_channel
    - normalized
    - clahe
    - denoised
    - fov_applied
    - final
    """
    cfg = config or PreprocessConfig()
    steps: dict[str, np.ndarray] = {}

    gray = select_initial_channel(image_rgb, use_green_channel=cfg.use_green_channel)
    steps["selected_channel"] = to_uint8(gray)

    gray = normalize_uint8(gray) if cfg.normalize_intensity else to_uint8(gray)
    steps["normalized"] = gray.copy()

    if cfg.apply_clahe:
        gray = apply_clahe(
            gray,
            clip_limit=cfg.clahe_clip_limit,
            tile_grid_size=cfg.clahe_tile_grid_size,
        )
    steps["clahe"] = gray.copy()

    gray = denoise_image(
        gray,
        method=cfg.denoise_method,
        median_kernel_size=cfg.median_kernel_size,
        bilateral_d=cfg.bilateral_d,
        bilateral_sigma_color=cfg.bilateral_sigma_color,
        bilateral_sigma_space=cfg.bilateral_sigma_space,
    )
    steps["denoised"] = gray.copy()

    if cfg.apply_fov_mask and fov_mask is not None:
        gray = apply_fov_mask_to_array(gray, fov_mask)
    steps["fov_applied"] = gray.copy()
    steps["final"] = gray.copy()

    return steps


def preprocess_from_files(
    image_path: str | Path,
    fov_path: str | Path | None = None,
    *,
    config: PreprocessConfig | None = None,
) -> np.ndarray:
    """Read a fundus image and optional FoV mask from files, then preprocess it."""
    image_rgb = read_rgb_image(image_path)
    fov_mask = read_binary_mask(fov_path) if fov_path else None
    return preprocess_fundus(image_rgb, fov_mask=fov_mask, config=config)


def preprocess_and_save(
    image_path: str | Path,
    output_path: str | Path,
    fov_path: str | Path | None = None,
    *,
    config: PreprocessConfig | None = None,
    compress_level: int = 3,
) -> np.ndarray:
    """Preprocess an image from disk, save the result as PNG, and return it."""
    preprocessed = preprocess_from_files(image_path, fov_path=fov_path, config=config)
    save_png_uint8(output_path, preprocessed, compress_level=compress_level)
    return preprocessed