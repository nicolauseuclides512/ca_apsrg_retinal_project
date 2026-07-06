from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List

import pandas as pd
from PIL import Image
import numpy as np
from tqdm import tqdm


IMAGE_EXTENSIONS = {".ppm", ".jpg", ".jpeg", ".tif", ".tiff", ".gif", ".bmp", ".png"}
CONVERT_EXTENSIONS = {".ppm", ".jpg", ".jpeg", ".tif", ".tiff", ".gif", ".bmp"}
ARCHIVE_EXTENSIONS = {".gz", ".7z", ".zip", ".tar", ".rar"}


@dataclass
class ConversionRecord:
    source_path: str
    output_path: str
    extension: str
    action: str
    reason: str
    width: int | None = None
    height: int | None = None
    mode: str | None = None


def _looks_like_mask(path: Path) -> bool:
    text = str(path).lower()
    mask_keywords = [
        "mask",
        "manual",
        "label",
        "1stho",
        "2ndho",
        "ah",
        "vk",
        "groundtruth",
        "ground_truth",
        "gt",
    ]
    return any(keyword in text for keyword in mask_keywords)


def _save_as_png(
    source_path: Path,
    output_path: Path,
    *,
    binarize_mask: bool = False,
) -> tuple[int, int, str]:
    img = Image.open(source_path)
    mode = img.mode

    if binarize_mask:
        gray = img.convert("L")
        arr = np.array(gray)
        arr = (arr > 127).astype(np.uint8) * 255
        out = Image.fromarray(arr, mode="L")
    else:
        # Fundus images should be RGB. Masks that are not binarized remain grayscale/RGB depending on mode.
        if img.mode in ("1", "L", "I;16", "I"):
            out = img.convert("L")
        else:
            out = img.convert("RGB")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.save(output_path, format="PNG")
    return img.size[0], img.size[1], mode


def convert_tree_to_png(
    input_root: str | Path,
    output_root: str | Path,
    *,
    copy_png: bool = True,
    binarize_masks: bool = True,
    overwrite: bool = False,
) -> pd.DataFrame:
    """
    Convert all image files recursively into PNG working files.

    Rules:
    - Non-PNG image files are converted to PNG.
    - Existing PNG can be copied to the working directory when copy_png=True.
    - If an output PNG with the same relative stem already exists, it is skipped unless overwrite=True.
    - Compressed archives are skipped.
    """
    input_root = Path(input_root)
    output_root = Path(output_root)

    if not input_root.exists():
        raise FileNotFoundError(f"Input root not found: {input_root}")

    records: List[ConversionRecord] = []
    all_files = [p for p in input_root.rglob("*") if p.is_file()]

    for source_path in tqdm(all_files, desc="Converting to PNG"):
        ext = source_path.suffix.lower()
        rel = source_path.relative_to(input_root)

        if ext in ARCHIVE_EXTENSIONS:
            records.append(
                ConversionRecord(str(source_path), "", ext, "skipped", "archive file")
            )
            continue

        if ext not in IMAGE_EXTENSIONS:
            records.append(
                ConversionRecord(str(source_path), "", ext, "skipped", "unsupported extension")
            )
            continue

        output_rel = rel.with_suffix(".png")
        output_path = output_root / output_rel

        if output_path.exists() and not overwrite:
            records.append(
                ConversionRecord(
                    str(source_path),
                    str(output_path),
                    ext,
                    "skipped",
                    "output PNG already exists",
                )
            )
            continue

        if ext == ".png" and not copy_png:
            records.append(
                ConversionRecord(
                    str(source_path), str(output_path), ext, "skipped", "source already PNG"
                )
            )
            continue

        try:
            binarize = binarize_masks and _looks_like_mask(source_path)
            width, height, mode = _save_as_png(source_path, output_path, binarize_mask=binarize)

            action = "copied_png" if ext == ".png" else "converted"
            reason = "binarized as mask" if binarize else "saved as PNG"
            records.append(
                ConversionRecord(
                    str(source_path), str(output_path), ext, action, reason, width, height, mode
                )
            )
        except Exception as exc:
            records.append(
                ConversionRecord(str(source_path), str(output_path), ext, "error", str(exc))
            )

    return pd.DataFrame([asdict(r) for r in records])
