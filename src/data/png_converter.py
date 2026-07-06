"""
Recursive PNG converter for retinal vessel datasets.

This module prepares a clean working dataset by converting all supported image
formats into PNG while preserving the original folder structure.

Main goals:
- Keep the original dataset untouched.
- Convert fundus images to RGB PNG.
- Convert masks/labels/manual annotations/FoV masks to binary 0/255 PNG.
- Generate a conversion report for reproducibility.

Supported source formats:
.ppm, .jpg, .jpeg, .tif, .tiff, .gif, .bmp, and optionally existing .png files.

Archives such as .zip, .7z, .tar, .gz, and .rar are skipped.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Optional

import numpy as np
import pandas as pd
from PIL import Image, ImageOps, UnidentifiedImageError
from tqdm import tqdm

from src.utils.image_io import ensure_binary_mask, ensure_dir, ensure_parent_dir


@dataclass(frozen=True)
class PngConversionConfig:
    """Configuration for recursive PNG conversion."""

    convertible_extensions: tuple[str, ...] = (
        ".ppm",
        ".jpg",
        ".jpeg",
        ".tif",
        ".tiff",
        ".gif",
        ".bmp",
    )
    copy_existing_png: bool = True
    skip_archive_extensions: tuple[str, ...] = (
        ".zip",
        ".7z",
        ".rar",
        ".tar",
        ".gz",
    )
    binarize_masks: bool = True
    binary_threshold: int = 127
    png_compress_level: int = 3
    preserve_relative_structure: bool = True
    overwrite: bool = False
    mask_name_keywords: tuple[str, ...] = (
        "mask",
        "manual",
        "label",
        "groundtruth",
        "ground_truth",
        "gt",
        "1stho",
        "2ndho",
        "fov",
    )
    observer_suffixes: tuple[str, ...] = ("ah", "vk")

    @property
    def supported_image_extensions(self) -> set[str]:
        extensions = {ext.lower() for ext in self.convertible_extensions}
        if self.copy_existing_png:
            extensions.add(".png")
        return extensions

    @property
    def archive_extensions(self) -> set[str]:
        return {ext.lower() for ext in self.skip_archive_extensions}


@dataclass
class ConversionRecord:
    """One row in the conversion report."""

    source_path: str
    output_path: str
    extension: str
    action: str
    reason: str
    is_mask_like: bool = False
    width: Optional[int] = None
    height: Optional[int] = None
    original_mode: Optional[str] = None
    output_mode: Optional[str] = None
    output_min: Optional[int] = None
    output_max: Optional[int] = None


def normalize_extension(ext: str) -> str:
    """Return a normalized lowercase file extension."""
    return ext.lower().strip()


def is_archive_file(path: str | Path, config: PngConversionConfig | None = None) -> bool:
    """Return True when path has an archive extension that should be skipped."""
    config = config or PngConversionConfig()
    return normalize_extension(Path(path).suffix) in config.archive_extensions


def is_supported_image_file(path: str | Path, config: PngConversionConfig | None = None) -> bool:
    """Return True when path is a supported image input for conversion/copying."""
    config = config or PngConversionConfig()
    return normalize_extension(Path(path).suffix) in config.supported_image_extensions


def _split_stem_tokens(path: Path) -> list[str]:
    """
    Split filename and folder parts into simple lowercase tokens.

    This improves mask detection for names such as:
    - 21_manual1.gif
    - im0001.ah.ppm
    - Image_01L_1stHO.png
    - pnglabel_ah/
    """
    text = "/".join(part.lower() for part in path.parts)
    for ch in ["/", "\\", "-", "_", ".", " ", "(", ")"]:
        text = text.replace(ch, " ")
    return [token for token in text.split() if token]


def detect_mask_file(path: str | Path, config: PngConversionConfig | None = None) -> bool:
    """
    Detect whether a file likely represents a binary mask/label/manual annotation.

    The function is intentionally conservative but covers the folder conventions
    used by DRIVE, STARE, and CHASEDB1.
    """
    config = config or PngConversionConfig()
    path = Path(path)
    lower_path = str(path).lower().replace("\\", "/")
    tokens = _split_stem_tokens(path)

    for keyword in config.mask_name_keywords:
        kw = keyword.lower()
        if kw in tokens or kw in lower_path:
            return True

    suffix_chain = [suffix.lower() for suffix in path.suffixes]
    for observer in config.observer_suffixes:
        if f".{observer}" in suffix_chain:
            return True

    for observer in config.observer_suffixes:
        if f"label_{observer}" in lower_path or f"label{observer}" in lower_path:
            return True

    return False


def get_output_path(
    source_path: str | Path,
    input_root: str | Path,
    output_root: str | Path,
    *,
    preserve_relative_structure: bool = True,
) -> Path:
    """
    Build the PNG output path for a source file.

    When preserve_relative_structure=True, the source folder hierarchy under
    input_root is replicated under output_root.
    """
    source_path = Path(source_path)
    input_root = Path(input_root)
    output_root = Path(output_root)

    if preserve_relative_structure:
        relative_path = source_path.relative_to(input_root)
        return (output_root / relative_path).with_suffix(".png")

    return (output_root / source_path.name).with_suffix(".png")


def _load_first_frame(path: Path) -> Image.Image:
    """
    Load an image with EXIF orientation handling and return a detached PIL image.

    For GIF/TIFF with multiple frames, the first frame is used.
    """
    with Image.open(path) as img:
        img.seek(0)
        img = ImageOps.exif_transpose(img)
        return img.copy()


def _convert_fundus_image_to_png_array(img: Image.Image) -> tuple[np.ndarray, str]:
    """
    Convert a fundus/input image to a PNG-safe uint8 array.

    Fundus images are standardized as RGB because later preprocessing can choose
    the green channel or use RGB visualization.
    """
    output = img.convert("RGB")
    return np.asarray(output, dtype=np.uint8), "RGB"


def _convert_mask_to_png_array(
    img: Image.Image,
    *,
    binary_threshold: int,
) -> tuple[np.ndarray, str]:
    """Convert a mask-like image to a binary uint8 array with values 0 and 255."""
    gray = img.convert("L")
    gray_arr = np.asarray(gray)
    binary = ensure_binary_mask(gray_arr, threshold=binary_threshold, return_uint8=True)
    return binary.astype(np.uint8), "L"


def save_png_array(
    output_path: str | Path,
    array: np.ndarray,
    *,
    compress_level: int = 3,
) -> None:
    """Save an RGB or grayscale uint8 array as PNG."""
    output_path = ensure_parent_dir(output_path)
    arr = np.asarray(array)

    if arr.dtype != np.uint8:
        arr = np.clip(arr, 0, 255).astype(np.uint8)

    if arr.ndim == 2:
        image = Image.fromarray(arr, mode="L")
    elif arr.ndim == 3 and arr.shape[2] == 3:
        image = Image.fromarray(arr, mode="RGB")
    else:
        raise ValueError(f"Unsupported array shape for PNG saving: {arr.shape}")

    image.save(output_path, format="PNG", compress_level=int(compress_level))


def convert_image_to_png(
    source_path: str | Path,
    output_path: str | Path,
    *,
    config: PngConversionConfig | None = None,
    force_mask: bool | None = None,
) -> ConversionRecord:
    """
    Convert one image file into PNG.

    Parameters
    ----------
    source_path:
        Source image path.
    output_path:
        Destination PNG path.
    config:
        PNG conversion configuration.
    force_mask:
        - True: save as binary mask.
        - False: save as RGB fundus image.
        - None: use automatic mask detection.
    """
    config = config or PngConversionConfig()
    source_path = Path(source_path)
    output_path = Path(output_path).with_suffix(".png")
    ext = normalize_extension(source_path.suffix)

    if not source_path.is_file():
        return ConversionRecord(
            source_path=str(source_path),
            output_path=str(output_path),
            extension=ext,
            action="error",
            reason="source file not found",
        )

    if output_path.exists() and not config.overwrite:
        return ConversionRecord(
            source_path=str(source_path),
            output_path=str(output_path),
            extension=ext,
            action="skipped",
            reason="output PNG already exists",
            is_mask_like=detect_mask_file(source_path, config),
        )

    try:
        is_mask_like = detect_mask_file(source_path, config) if force_mask is None else bool(force_mask)
        img = _load_first_frame(source_path)
        original_mode = img.mode
        width, height = img.size

        if is_mask_like and config.binarize_masks:
            output_array, output_mode = _convert_mask_to_png_array(
                img,
                binary_threshold=config.binary_threshold,
            )
            reason = "binarized mask-like image to 0/255 PNG"
        elif is_mask_like and not config.binarize_masks:
            gray = img.convert("L")
            output_array = np.asarray(gray, dtype=np.uint8)
            output_mode = "L"
            reason = "saved mask-like image as grayscale PNG without binarization"
        else:
            output_array, output_mode = _convert_fundus_image_to_png_array(img)
            reason = "saved fundus/image as RGB PNG"

        save_png_array(
            output_path,
            output_array,
            compress_level=config.png_compress_level,
        )

        action = "copied_png" if ext == ".png" else "converted"
        return ConversionRecord(
            source_path=str(source_path),
            output_path=str(output_path),
            extension=ext,
            action=action,
            reason=reason,
            is_mask_like=is_mask_like,
            width=width,
            height=height,
            original_mode=original_mode,
            output_mode=output_mode,
            output_min=int(np.min(output_array)) if output_array.size else None,
            output_max=int(np.max(output_array)) if output_array.size else None,
        )

    except UnidentifiedImageError as exc:
        return ConversionRecord(
            source_path=str(source_path),
            output_path=str(output_path),
            extension=ext,
            action="error",
            reason=f"unidentified image: {exc}",
        )
    except Exception as exc:
        return ConversionRecord(
            source_path=str(source_path),
            output_path=str(output_path),
            extension=ext,
            action="error",
            reason=str(exc),
        )


def iter_files_recursive(root: str | Path) -> Iterable[Path]:
    """Yield files recursively in deterministic order."""
    root = Path(root)
    yield from sorted((path for path in root.rglob("*") if path.is_file()), key=lambda p: str(p).lower())


def convert_folder_recursive(
    input_root: str | Path,
    output_root: str | Path,
    *,
    config: PngConversionConfig | None = None,
    show_progress: bool = True,
) -> pd.DataFrame:
    """
    Convert/copy all supported image files under input_root to PNG under output_root.

    Unsupported files and archive files are recorded in the report as skipped.
    """
    config = config or PngConversionConfig()
    input_root = Path(input_root)
    output_root = Path(output_root)

    if not input_root.exists():
        raise FileNotFoundError(f"Input root not found: {input_root}")
    if not input_root.is_dir():
        raise NotADirectoryError(f"Input root is not a directory: {input_root}")

    ensure_dir(output_root)
    records: list[ConversionRecord] = []

    files = list(iter_files_recursive(input_root))
    iterator = tqdm(files, desc="Converting images to PNG") if show_progress else files

    for source_path in iterator:
        ext = normalize_extension(source_path.suffix)

        if is_archive_file(source_path, config):
            records.append(
                ConversionRecord(
                    source_path=str(source_path),
                    output_path="",
                    extension=ext,
                    action="skipped",
                    reason="archive file",
                )
            )
            continue

        if not is_supported_image_file(source_path, config):
            records.append(
                ConversionRecord(
                    source_path=str(source_path),
                    output_path="",
                    extension=ext,
                    action="skipped",
                    reason="unsupported extension",
                )
            )
            continue

        if ext == ".png" and not config.copy_existing_png:
            records.append(
                ConversionRecord(
                    source_path=str(source_path),
                    output_path="",
                    extension=ext,
                    action="skipped",
                    reason="source already PNG and copy_existing_png=False",
                    is_mask_like=detect_mask_file(source_path, config),
                )
            )
            continue

        output_path = get_output_path(
            source_path,
            input_root,
            output_root,
            preserve_relative_structure=config.preserve_relative_structure,
        )
        records.append(convert_image_to_png(source_path, output_path, config=config))

    df = pd.DataFrame([asdict(record) for record in records])
    if not df.empty:
        df = df.sort_values(by=["action", "source_path"]).reset_index(drop=True)
    return df


def write_conversion_report(report: pd.DataFrame, report_path: str | Path) -> Path:
    """Save the conversion report as CSV and return the report path."""
    report_path = ensure_parent_dir(report_path)
    report.to_csv(report_path, index=False)
    return report_path


def summarize_conversion_report(report: pd.DataFrame) -> dict[str, int]:
    """Return simple action counts for quick console output."""
    if report.empty or "action" not in report.columns:
        return {}
    return {str(k): int(v) for k, v in report["action"].value_counts().to_dict().items()}


def convert_tree_to_png(
    input_root: str | Path,
    output_root: str | Path,
    *,
    copy_png: bool = True,
    binarize_masks: bool = True,
    overwrite: bool = False,
) -> pd.DataFrame:
    """Backward-compatible wrapper around convert_folder_recursive()."""
    config = PngConversionConfig(
        copy_existing_png=copy_png,
        binarize_masks=binarize_masks,
        overwrite=overwrite,
    )
    return convert_folder_recursive(input_root, output_root, config=config)