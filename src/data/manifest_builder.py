from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional

import pandas as pd


@dataclass
class ManifestRow:
    dataset: str
    image_id: str
    image_path: str
    mask_path: str
    fov_path: str = ""
    observer: str = ""


def _find_first(root: Path, patterns: list[str]) -> Optional[Path]:
    for pattern in patterns:
        found = list(root.rglob(pattern))
        if found:
            return found[0]
    return None


def build_drive_manifest(root: Path) -> List[ManifestRow]:
    rows: List[ManifestRow] = []

    # Supports paths like DRIVE/DRIVE/training/images/21_training.png
    image_files = list(root.rglob("*/training/images/*_training.png"))
    for image_path in sorted(image_files):
        image_id = image_path.stem.replace("_training", "")
        training_dir = image_path.parent.parent

        mask_path = _find_first(training_dir, [
            f"1st_manual/{image_id}_manual1.png",
            f"1st_manual/*{image_id}*manual*.png",
        ])
        fov_path = _find_first(training_dir, [
            f"mask/{image_id}_training_mask.png",
            f"mask/*{image_id}*mask*.png",
        ])

        if mask_path:
            rows.append(
                ManifestRow(
                    dataset="DRIVE",
                    image_id=image_id,
                    image_path=str(image_path),
                    mask_path=str(mask_path),
                    fov_path=str(fov_path) if fov_path else "",
                    observer="1st_manual",
                )
            )

    return rows


def build_stare_manifest(root: Path, prefer_observer: str = "ah") -> List[ManifestRow]:
    rows: List[ManifestRow] = []

    image_files = list(root.rglob("*/pngdata/*.png")) + list(root.rglob("*/all-images/*.png"))
    image_files = sorted(set(image_files))

    for image_path in image_files:
        image_id = image_path.stem

        # Try converted PNG labels.
        if prefer_observer.lower() == "vk":
            label_patterns = [
                f"pnglabel_vk/{image_id}.png",
                f"pnglabel_vk/*{image_id}*.png",
                f"*label*vk*/*{image_id}*.png",
            ]
            observer = "vk"
        else:
            label_patterns = [
                f"pnglabel_ah/{image_id}.png",
                f"pnglabel_ah/*{image_id}*.png",
                f"*label*ah*/*{image_id}*.png",
            ]
            observer = "ah"

        dataset_root = image_path.parents[1] if len(image_path.parents) > 1 else root
        mask_path = _find_first(dataset_root, label_patterns)

        if mask_path:
            rows.append(
                ManifestRow(
                    dataset="STARE",
                    image_id=image_id,
                    image_path=str(image_path),
                    mask_path=str(mask_path),
                    fov_path="",
                    observer=observer,
                )
            )

    return rows


def build_chasedb1_manifest(root: Path, observer: str = "1stHO") -> List[ManifestRow]:
    rows: List[ManifestRow] = []

    image_files = sorted([
        p for p in root.rglob("Image_*.png")
        if not p.stem.endswith("_1stHO") and not p.stem.endswith("_2ndHO")
    ])

    for image_path in image_files:
        image_id = image_path.stem
        mask_path = image_path.with_name(f"{image_id}_{observer}.png")
        if mask_path.exists():
            rows.append(
                ManifestRow(
                    dataset="CHASEDB1",
                    image_id=image_id,
                    image_path=str(image_path),
                    mask_path=str(mask_path),
                    fov_path="",
                    observer=observer,
                )
            )

    return rows


def build_manifest(
    working_root: str | Path,
    output_csv: str | Path,
    *,
    stare_observer: str = "ah",
    chasedb1_observer: str = "1stHO",
) -> pd.DataFrame:
    working_root = Path(working_root)
    output_csv = Path(output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    rows: List[ManifestRow] = []
    rows.extend(build_drive_manifest(working_root))
    rows.extend(build_stare_manifest(working_root, prefer_observer=stare_observer))
    rows.extend(build_chasedb1_manifest(working_root, observer=chasedb1_observer))

    df = pd.DataFrame([asdict(row) for row in rows])
    if not df.empty:
        df = df.drop_duplicates(subset=["dataset", "image_id", "image_path", "mask_path"])
    df.to_csv(output_csv, index=False)
    return df
