"""
Utility functions for image input/output in the CA-APSRG project.

This module standardizes how retinal images, ground-truth masks, FoV masks,
and segmentation outputs are read, converted, resized, binarized, and saved.

Conventions used in this project:
- RGB fundus image: uint8 array with shape (H, W, 3), channel order RGB.
- Grayscale image: uint8 array with shape (H, W).
- Binary mask for processing/evaluation: boolean array with shape (H, W).
- Binary mask for saving: uint8 PNG with values 0 and 255.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional, Tuple

import cv2
import numpy as np
from PIL import Image, ImageOps

ArrayLike = np.ndarray
InterpolationName = Literal["nearest", "linear", "area", "cubic", "lanczos"]


def ensure_dir(path: str | Path) -> Path:
    """Create a directory if it does not exist and return it as a Path object."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_parent_dir(file_path: str | Path) -> Path:
    """Create the parent directory of a file path and return the file path."""
    file_path = Path(file_path)
    ensure_dir(file_path.parent)
    return file_path


def assert_file_exists(path: str | Path) -> Path:
    """Validate that a file exists."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    return path


def read_rgb_image(path: str | Path, apply_exif_orientation: bool = True) -> np.ndarray:
    """
    Read an image as RGB uint8.

    PIL is used instead of cv2.imread so that formats such as PPM, GIF, TIFF,
    and indexed PNG are handled more consistently.
    """
    path = assert_file_exists(path)

    with Image.open(path) as img:
        if apply_exif_orientation:
            img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        return np.asarray(img, dtype=np.uint8)


def read_gray_image(path: str | Path, apply_exif_orientation: bool = True) -> np.ndarray:
    """Read an image as grayscale uint8."""
    path = assert_file_exists(path)

    with Image.open(path) as img:
        if apply_exif_orientation:
            img = ImageOps.exif_transpose(img)
        img = img.convert("L")
        return np.asarray(img, dtype=np.uint8)


def read_binary_mask(path: str | Path, threshold: int = 127) -> np.ndarray:
    """
    Read a vessel/ground-truth/FoV mask and return a boolean array.

    Any pixel value greater than threshold is interpreted as foreground/True.
    """
    gray = read_gray_image(path)
    return ensure_binary_mask(gray, threshold=threshold, return_uint8=False)


read_rgb = read_rgb_image
read_gray = read_gray_image


def to_uint8(image: ArrayLike) -> np.ndarray:
    """
    Convert an image to uint8 safely.

    - bool becomes 0/255.
    - float in [0, 1] becomes [0, 255].
    - other numeric values are clipped to [0, 255].
    """
    arr = np.asarray(image)

    if arr.dtype == np.bool_:
        return arr.astype(np.uint8) * 255

    if np.issubdtype(arr.dtype, np.floating):
        arr = np.nan_to_num(arr, nan=0.0, posinf=255.0, neginf=0.0)
        if arr.size > 0 and arr.max() <= 1.0 and arr.min() >= 0.0:
            arr = arr * 255.0
        return np.clip(arr, 0, 255).astype(np.uint8)

    return np.clip(arr, 0, 255).astype(np.uint8)


def ensure_binary_mask(
    mask: ArrayLike,
    threshold: int = 127,
    return_uint8: bool = False,
) -> np.ndarray:
    """
    Convert any mask-like array into a binary mask.

    Parameters
    ----------
    mask:
        Input mask. Can be bool, grayscale, RGB, or float.
    threshold:
        Threshold for foreground if the mask is not already boolean.
    return_uint8:
        If True, return 0/255 uint8. If False, return bool.
    """
    arr = np.asarray(mask)

    if arr.ndim == 3:
        arr = cv2.cvtColor(to_uint8(arr), cv2.COLOR_RGB2GRAY)

    if arr.dtype == np.bool_:
        binary = arr
    else:
        arr_u8 = to_uint8(arr)
        binary = arr_u8 > threshold

    if return_uint8:
        return binary.astype(np.uint8) * 255
    return binary


def normalize_to_uint8(image: ArrayLike) -> np.ndarray:
    """
    Min-max normalize an image to uint8 [0, 255].

    Useful for enhanced/vesselness images before visualization or thresholding.
    """
    arr = np.asarray(image, dtype=np.float32)
    arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)

    min_val = float(arr.min()) if arr.size else 0.0
    max_val = float(arr.max()) if arr.size else 0.0

    if max_val <= min_val:
        return np.zeros(arr.shape, dtype=np.uint8)

    norm = (arr - min_val) / (max_val - min_val)
    return (norm * 255.0).round().astype(np.uint8)


def get_image_shape(image: ArrayLike) -> Tuple[int, int]:
    """Return image spatial shape as (height, width)."""
    arr = np.asarray(image)
    if arr.ndim < 2:
        raise ValueError(f"Expected image with at least 2 dimensions, got shape {arr.shape}")
    return int(arr.shape[0]), int(arr.shape[1])


def resize_image(
    image: ArrayLike,
    size: Tuple[int, int],
    interpolation: InterpolationName = "area",
) -> np.ndarray:
    """
    Resize an image to a target size.

    Parameters
    ----------
    image:
        Input image.
    size:
        Target size as (height, width).
    interpolation:
        Interpolation mode. Use "nearest" for masks.
    """
    mapping = {
        "nearest": cv2.INTER_NEAREST,
        "linear": cv2.INTER_LINEAR,
        "area": cv2.INTER_AREA,
        "cubic": cv2.INTER_CUBIC,
        "lanczos": cv2.INTER_LANCZOS4,
    }

    target_h, target_w = size
    arr = np.asarray(image)
    return cv2.resize(arr, (target_w, target_h), interpolation=mapping[interpolation])


def resize_if_needed(
    image: ArrayLike,
    reference: ArrayLike | Tuple[int, int],
    interpolation: InterpolationName = "area",
) -> np.ndarray:
    """
    Resize image only when its shape differs from a reference image/shape.

    For binary masks, call this with interpolation="nearest".
    """
    target_shape = reference if isinstance(reference, tuple) else get_image_shape(reference)
    current_shape = get_image_shape(image)

    if current_shape == target_shape:
        return np.asarray(image)

    return resize_image(image, size=target_shape, interpolation=interpolation)


def save_image(path: str | Path, image: ArrayLike, compress_level: int = 3) -> None:
    """
    Save image as PNG-compatible uint8.

    The output format follows the file extension. For this project, use .png.
    """
    path = ensure_parent_dir(path)
    arr = to_uint8(image)

    if arr.ndim not in (2, 3):
        raise ValueError(f"Only 2D grayscale or 3D RGB images can be saved, got shape {arr.shape}")

    if arr.ndim == 3 and arr.shape[2] not in (3, 4):
        raise ValueError(f"Expected RGB/RGBA image with 3 or 4 channels, got shape {arr.shape}")

    pil_img = Image.fromarray(arr)

    if path.suffix.lower() == ".png":
        pil_img.save(path, format="PNG", compress_level=int(compress_level))
    else:
        pil_img.save(path)


def save_png_uint8(path: str | Path, image: ArrayLike, compress_level: int = 3) -> None:
    """Save an image as uint8 PNG."""
    path = Path(path)
    if path.suffix.lower() != ".png":
        path = path.with_suffix(".png")
    save_image(path, image, compress_level=compress_level)


def save_binary_mask(path: str | Path, mask: ArrayLike, compress_level: int = 3) -> None:
    """Save a binary mask as a 0/255 uint8 PNG."""
    binary_u8 = ensure_binary_mask(mask, return_uint8=True)
    save_png_uint8(path, binary_u8, compress_level=compress_level)


def apply_fov_mask(image_or_mask: ArrayLike, fov_mask: Optional[ArrayLike]) -> np.ndarray:
    """
    Set pixels outside the field-of-view mask to zero.

    fov_mask can be bool, grayscale, or RGB. The output follows the input shape.
    """
    result = np.asarray(image_or_mask).copy()

    if fov_mask is None:
        return result

    fov_bool = ensure_binary_mask(fov_mask, return_uint8=False)
    fov_bool = resize_if_needed(fov_bool.astype(np.uint8), result, interpolation="nearest") > 0

    if result.ndim == 2:
        result[~fov_bool] = 0
    elif result.ndim == 3:
        result[~fov_bool, :] = 0
    else:
        raise ValueError(f"Unsupported image shape for FoV masking: {result.shape}")

    return result


def overlay_mask_on_image(
    image_rgb: ArrayLike,
    mask: ArrayLike,
    alpha: float = 0.45,
    mask_color: Tuple[int, int, int] = (255, 0, 0),
) -> np.ndarray:
    """
    Overlay a binary mask on an RGB image for visual inspection.

    Default color is red. This is only for visualization, not for evaluation.
    """
    image = to_uint8(image_rgb)
    if image.ndim == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

    mask_bool = ensure_binary_mask(mask, return_uint8=False)
    mask_bool = resize_if_needed(mask_bool.astype(np.uint8), image, interpolation="nearest") > 0

    overlay = image.copy().astype(np.float32)
    base = image.astype(np.float32)
    overlay[mask_bool] = np.array(mask_color, dtype=np.float32)

    blended = (1.0 - alpha) * base + alpha * overlay
    return np.clip(blended, 0, 255).astype(np.uint8)


def create_side_by_side(images: list[ArrayLike], gap: int = 8, background_value: int = 255) -> np.ndarray:
    """
    Concatenate several images horizontally with a small gap.

    Grayscale images are converted to RGB for consistent visualization.
    """
    if not images:
        raise ValueError("No images provided for side-by-side visualization.")

    rgb_images: list[np.ndarray] = []
    heights: list[int] = []
    widths: list[int] = []

    for img in images:
        arr = to_uint8(img)
        if arr.ndim == 2:
            arr = cv2.cvtColor(arr, cv2.COLOR_GRAY2RGB)
        elif arr.ndim == 3 and arr.shape[2] == 4:
            arr = arr[:, :, :3]
        elif arr.ndim != 3 or arr.shape[2] != 3:
            raise ValueError(f"Unsupported image shape: {arr.shape}")

        rgb_images.append(arr)
        heights.append(arr.shape[0])
        widths.append(arr.shape[1])

    max_h = max(heights)
    total_w = sum(widths) + gap * (len(rgb_images) - 1)
    canvas = np.full((max_h, total_w, 3), background_value, dtype=np.uint8)

    x = 0
    for arr in rgb_images:
        h, w = arr.shape[:2]
        canvas[:h, x:x + w] = arr
        x += w + gap

    return canvas