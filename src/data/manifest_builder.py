"""
Manifest builder for the CA-APSRG retinal vessel segmentation project.

This module builds a clean CSV manifest after the recursive PNG conversion step.
The manifest pairs each fundus image with its corresponding vessel ground-truth
mask and, when available, the field-of-view (FoV) mask.

Supported datasets:
- DRIVE
- STARE
- CHASEDB1

Expected main columns:
- dataset
- split
- image_id
- image_path
- mask_path
- fov_path
- observer

The output CSV is used by the experimental pipeline.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".ppm", ".bmp"}


@dataclass(frozen=True)
class ManifestConfig:
    """Configuration for manifest building."""

    require_ground_truth: bool = True
    include_fov_mask_if_available: bool = True
    stare_observer: str = "ah"  # options commonly available: ah, vk
    chasedb1_observer: str = "1stHO"  # options: 1stHO, 2ndHO
    use_absolute_paths: bool = False


@dataclass
class ManifestRow:
    """One image-mask pair in the experiment manifest."""

    dataset: str
    split: str
    image_id: str
    image_path: str
    mask_path: str
    fov_path: str = ""
    observer: str = ""
    notes: str = ""


def _is_image_file(path: Path) -> bool:
    """Return True if a path has a supported image extension."""
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def _path_text(path: Path, *, use_absolute_paths: bool = False) -> str:
    """Convert a Path to a string for the manifest."""
    if not path:
        return ""
    return str(path.resolve()) if use_absolute_paths else str(path)


def _sorted_files(root: Path, pattern: str) -> list[Path]:
    """Return sorted files matching a glob pattern."""
    if not root.exists():
        return []
    return sorted((p for p in root.rglob(pattern) if p.is_file()), key=lambda p: str(p).lower())


def _find_first(root: Path, patterns: Iterable[str]) -> Optional[Path]:
    """Find the first existing file under root matching one of several patterns."""
    for pattern in patterns:
        matches = _sorted_files(root, pattern)
        if matches:
            return matches[0]
    return None


def _contains_any(path: Path, keywords: Iterable[str]) -> bool:
    """Return True if path contains any keyword, case-insensitive."""
    text = str(path).lower().replace("\\", "/")
    return any(keyword.lower() in text for keyword in keywords)


def _is_probably_mask_or_label(path: Path) -> bool:
    """Avoid treating labels/manual annotations/FoV masks as fundus images."""
    keywords = [
        "manual",
        "mask",
        "label",
        "1stho",
        "2ndho",
        "groundtruth",
        "ground_truth",
    ]
    lower_name = path.name.lower()
    if lower_name.endswith(".ah.png") or lower_name.endswith(".vk.png"):
        return True
    return _contains_any(path, keywords)


def _canonical_stare_image_id(path: Path) -> str:
    """
    Normalize STARE identifiers.

    Examples:
    - im0001.png -> im0001
    - im0001.ah.png -> im0001
    - im0001.vk.png -> im0001
    - im0001_2ndHO.png -> im0001
    """
    stem = path.stem
    lower = stem.lower()

    if lower.endswith(".ah") or lower.endswith(".vk"):
        stem = stem.rsplit(".", 1)[0]

    for suffix in ["_1stho", "_2ndho"]:
        if stem.lower().endswith(suffix):
            stem = stem[: -len(suffix)]

    return stem


def _score_stare_image_candidate(path: Path) -> int:
    """
    Prefer STARE images from pngdata, then ppmdata, then stare-images.

    Lower score means higher priority.
    """
    text = str(path).lower().replace("\\", "/")
    if "/pngdata/" in text:
        return 0
    if "/ppmdata/" in text:
        return 1
    if "/stare-images/" in text:
        return 2
    return 9


def _score_stare_label_candidate(path: Path, observer: str) -> int:
    """
    Prefer clean PNG labels from pnglabel_{observer}, then converted labelppm.

    Lower score means higher priority.
    """
    text = str(path).lower().replace("\\", "/")
    name = path.name.lower()
    observer = observer.lower()

    score = 50
    if f"/pnglabel_{observer}/" in text:
        score = 0
    elif f"/labelppm_{observer}/" in text:
        score = 10
    elif f"/labels-{observer}/" in text:
        score = 20
    elif f"label{observer}" in text or f"label_{observer}" in text:
        score = 30

    # Prefer exact im0001.png over duplicate variants such as im0001_2ndHO.png.
    if "_1stho" in name or "_2ndho" in name:
        score += 5
    if name.endswith(f".{observer}.png"):
        score += 1

    return score


def _select_best_by_id(candidates: list[Path], id_func, score_func) -> dict[str, Path]:
    """Select the best file for each canonical image id."""
    selected: dict[str, Path] = {}
    scores: dict[str, int] = {}

    for path in candidates:
        image_id = id_func(path)
        score = score_func(path)
        if image_id not in selected or score < scores[image_id]:
            selected[image_id] = path
            scores[image_id] = score

    return selected


def build_drive_manifest(
    working_root: str | Path,
    *,
    require_ground_truth: bool = True,
    include_fov_mask_if_available: bool = True,
    use_absolute_paths: bool = False,
) -> list[ManifestRow]:
    """
    Build manifest rows for DRIVE.

    The standard DRIVE evaluation-safe subset in this project is the training
    set because it contains images, 1st manual annotations, and FoV masks.
    Test images are skipped when no manual ground truth is available.
    """
    root = Path(working_root)
    rows: list[ManifestRow] = []

    image_files = [
        p
        for p in _sorted_files(root, "*_training.png")
        if _is_image_file(p) and "/images/" in str(p).lower().replace("\\", "/")
    ]

    for image_path in image_files:
        image_id = image_path.stem.replace("_training", "")
        split_root = image_path.parent.parent

        mask_path = _find_first(
            split_root,
            [
                f"1st_manual/{image_id}_manual1.png",
                f"1st_manual/*{image_id}*manual*.png",
                f"manual/*{image_id}*.png",
            ],
        )

        fov_path = None
        if include_fov_mask_if_available:
            fov_path = _find_first(
                split_root,
                [
                    f"mask/{image_id}_training_mask.png",
                    f"mask/*{image_id}*mask*.png",
                ],
            )

        if require_ground_truth and mask_path is None:
            continue

        rows.append(
            ManifestRow(
                dataset="DRIVE",
                split="training",
                image_id=image_id,
                image_path=_path_text(image_path, use_absolute_paths=use_absolute_paths),
                mask_path=_path_text(mask_path, use_absolute_paths=use_absolute_paths) if mask_path else "",
                fov_path=_path_text(fov_path, use_absolute_paths=use_absolute_paths) if fov_path else "",
                observer="1st_manual",
                notes="DRIVE training image with manual vessel annotation",
            )
        )

    return sorted(rows, key=lambda row: row.image_id)


def build_stare_manifest(
    working_root: str | Path,
    *,
    prefer_observer: str = "ah",
    require_ground_truth: bool = True,
    use_absolute_paths: bool = False,
) -> list[ManifestRow]:
    """
    Build manifest rows for STARE.

    STARE commonly contains two observers/annotations: ah and vk. This function
    selects one observer for the experiment manifest, defaulting to ah.
    """
    root = Path(working_root)
    observer = prefer_observer.lower()
    if observer not in {"ah", "vk"}:
        raise ValueError("prefer_observer must be either 'ah' or 'vk'.")

    image_candidates = [
        p
        for p in _sorted_files(root, "*.png")
        if _is_image_file(p)
        and "stare" in str(p).lower()
        and not _is_probably_mask_or_label(p)
        and any(folder in str(p).lower().replace("\\", "/") for folder in ["/pngdata/", "/ppmdata/", "/stare-images/"])
    ]

    label_candidates = [
        p
        for p in _sorted_files(root, "*.png")
        if _is_image_file(p)
        and "stare" in str(p).lower()
        and (
            f"pnglabel_{observer}" in str(p).lower()
            or f"labelppm_{observer}" in str(p).lower()
            or f"labels-{observer}" in str(p).lower()
            or p.name.lower().endswith(f".{observer}.png")
        )
    ]

    images_by_id = _select_best_by_id(
        image_candidates,
        id_func=_canonical_stare_image_id,
        score_func=_score_stare_image_candidate,
    )
    labels_by_id = _select_best_by_id(
        label_candidates,
        id_func=_canonical_stare_image_id,
        score_func=lambda path: _score_stare_label_candidate(path, observer),
    )

    rows: list[ManifestRow] = []
    for image_id in sorted(images_by_id):
        image_path = images_by_id[image_id]
        mask_path = labels_by_id.get(image_id)

        if require_ground_truth and mask_path is None:
            continue

        rows.append(
            ManifestRow(
                dataset="STARE",
                split="all",
                image_id=image_id,
                image_path=_path_text(image_path, use_absolute_paths=use_absolute_paths),
                mask_path=_path_text(mask_path, use_absolute_paths=use_absolute_paths) if mask_path else "",
                fov_path="",
                observer=observer,
                notes=f"STARE image paired with {observer} observer annotation",
            )
        )

    return rows


def build_chasedb1_manifest(
    working_root: str | Path,
    *,
    observer: str = "1stHO",
    require_ground_truth: bool = True,
    use_absolute_paths: bool = False,
) -> list[ManifestRow]:
    """
    Build manifest rows for CHASEDB1.

    CHASEDB1 contains left/right eye images and two human observer annotations:
    1stHO and 2ndHO.
    """
    root = Path(working_root)
    observer = observer.strip()
    if observer not in {"1stHO", "2ndHO"}:
        raise ValueError("observer must be either '1stHO' or '2ndHO'.")

    image_files = [
        p
        for p in _sorted_files(root, "Image_*.png")
        if _is_image_file(p)
        and "chasedb1" in str(p).lower()
        and not p.stem.lower().endswith("_1stho")
        and not p.stem.lower().endswith("_2ndho")
    ]

    rows: list[ManifestRow] = []
    for image_path in image_files:
        image_id = image_path.stem
        mask_path = image_path.with_name(f"{image_id}_{observer}.png")

        if require_ground_truth and not mask_path.exists():
            continue

        rows.append(
            ManifestRow(
                dataset="CHASEDB1",
                split="all",
                image_id=image_id,
                image_path=_path_text(image_path, use_absolute_paths=use_absolute_paths),
                mask_path=_path_text(mask_path, use_absolute_paths=use_absolute_paths) if mask_path.exists() else "",
                fov_path="",
                observer=observer,
                notes=f"CHASEDB1 image paired with {observer} annotation",
            )
        )

    return sorted(rows, key=lambda row: row.image_id)


def build_all_manifest(
    working_root: str | Path,
    *,
    config: ManifestConfig | None = None,
) -> pd.DataFrame:
    """Build a combined DRIVE + STARE + CHASEDB1 manifest as a DataFrame."""
    config = config or ManifestConfig()
    working_root = Path(working_root)

    rows: list[ManifestRow] = []
    rows.extend(
        build_drive_manifest(
            working_root,
            require_ground_truth=config.require_ground_truth,
            include_fov_mask_if_available=config.include_fov_mask_if_available,
            use_absolute_paths=config.use_absolute_paths,
        )
    )
    rows.extend(
        build_stare_manifest(
            working_root,
            prefer_observer=config.stare_observer,
            require_ground_truth=config.require_ground_truth,
            use_absolute_paths=config.use_absolute_paths,
        )
    )
    rows.extend(
        build_chasedb1_manifest(
            working_root,
            observer=config.chasedb1_observer,
            require_ground_truth=config.require_ground_truth,
            use_absolute_paths=config.use_absolute_paths,
        )
    )

    df = pd.DataFrame([asdict(row) for row in rows])

    if df.empty:
        return pd.DataFrame(
            columns=["dataset", "split", "image_id", "image_path", "mask_path", "fov_path", "observer", "notes"]
        )

    df = df.drop_duplicates(subset=["dataset", "image_id", "image_path", "mask_path"]).reset_index(drop=True)
    df = df.sort_values(by=["dataset", "image_id", "observer"]).reset_index(drop=True)
    return df


def validate_manifest(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add simple validation columns to a manifest DataFrame.

    This is useful before running expensive experiments.
    """
    if df.empty:
        return df.copy()

    checked = df.copy()
    checked["image_exists"] = checked["image_path"].apply(lambda p: Path(str(p)).is_file())
    checked["mask_exists"] = checked["mask_path"].apply(lambda p: Path(str(p)).is_file() if str(p) else False)
    checked["fov_exists"] = checked["fov_path"].apply(lambda p: Path(str(p)).is_file() if str(p) else False)
    checked["is_ready"] = checked["image_exists"] & checked["mask_exists"]
    return checked


def summarize_manifest(df: pd.DataFrame) -> pd.DataFrame:
    """Create a compact summary table by dataset and observer."""
    if df.empty:
        return pd.DataFrame(columns=["dataset", "observer", "n_images"])

    return (
        df.groupby(["dataset", "observer"], dropna=False)
        .size()
        .reset_index(name="n_images")
        .sort_values(["dataset", "observer"])
        .reset_index(drop=True)
    )


def save_manifest(df: pd.DataFrame, output_csv: str | Path) -> Path:
    """Save the manifest DataFrame to CSV."""
    output_csv = Path(output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)
    return output_csv


def build_manifest(
    working_root: str | Path,
    output_csv: str | Path,
    *,
    stare_observer: str = "ah",
    chasedb1_observer: str = "1stHO",
    require_ground_truth: bool = True,
    include_fov_mask_if_available: bool = True,
    use_absolute_paths: bool = False,
) -> pd.DataFrame:
    """
    Build and save the experiment manifest.

    This function is kept as the main entry point for scripts/01_build_manifest.py.
    """
    config = ManifestConfig(
        require_ground_truth=require_ground_truth,
        include_fov_mask_if_available=include_fov_mask_if_available,
        stare_observer=stare_observer,
        chasedb1_observer=chasedb1_observer,
        use_absolute_paths=use_absolute_paths,
    )
    df = build_all_manifest(working_root, config=config)
    save_manifest(df, output_csv)
    return df