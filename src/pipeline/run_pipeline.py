from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Optional

import pandas as pd

from src.evaluation.metrics import compute_metrics, metrics_to_dict
from src.preprocessing.preprocess import preprocess_fundus
from src.segmentation.adaptive_morphology import AdaptiveMorphologyParams
from src.segmentation.apsrg_baseline import APSRGParams, apsrg_segment
from src.segmentation.ca_apsrg import ca_apsrg_refine
from src.utils.image_io import (
    ensure_dir,
    overlay_mask_on_image,
    read_binary_mask,
    read_rgb,
    save_binary_mask,
    save_png_uint8,
)


def should_apply_ca_apsrg(
    baseline_precision: Optional[float],
    *,
    always_refine: bool = True,
    precision_threshold: float = 0.95,
) -> bool:
    if always_refine:
        return True
    if baseline_precision is None:
        return True
    return baseline_precision < precision_threshold


def run_single_image(
    image_path: str | Path,
    output_dir: str | Path,
    *,
    mask_path: str | Path | None = None,
    fov_path: str | Path | None = None,
    image_id: str | None = None,
    dataset: str = "",
    always_refine: bool = True,
    precision_threshold: float = 0.95,
) -> dict:
    image_path = Path(image_path)
    output_dir = ensure_dir(output_dir)

    image_id = image_id or image_path.stem

    image_rgb = read_rgb(image_path)
    gt_mask = read_binary_mask(mask_path) if mask_path else None
    fov_mask = read_binary_mask(fov_path) if fov_path else None

    pre = preprocess_fundus(image_rgb, fov_mask=fov_mask)

    baseline_mask, baseline_debug = apsrg_segment(pre, fov_mask=fov_mask, params=APSRGParams())

    baseline_metrics = None
    baseline_precision = None
    if gt_mask is not None:
        baseline_metrics = compute_metrics(baseline_mask, gt_mask, fov_mask)
        baseline_precision = baseline_metrics.precision

    use_refine = should_apply_ca_apsrg(
        baseline_precision,
        always_refine=always_refine,
        precision_threshold=precision_threshold,
    )

    if use_refine:
        ca_mask, ca_debug = ca_apsrg_refine(
            baseline_mask,
            fov_mask=fov_mask,
            params=AdaptiveMorphologyParams(),
        )
    else:
        ca_mask, ca_debug = baseline_mask, {"skipped": True, "reason": "false positive not detected"}

    ca_metrics = None
    if gt_mask is not None:
        ca_metrics = compute_metrics(ca_mask, gt_mask, fov_mask)

    # Save outputs
    save_png_uint8(output_dir / "preprocessed" / f"{image_id}_preprocessed.png", pre)
    save_binary_mask(output_dir / "baseline_masks" / f"{image_id}_apsrg_baseline.png", baseline_mask)
    save_binary_mask(output_dir / "ca_apsrg_masks" / f"{image_id}_ca_apsrg.png", ca_mask)
    save_png_uint8(output_dir / "overlays" / f"{image_id}_baseline_overlay.png", overlay_mask_on_image(image_rgb, baseline_mask))
    save_png_uint8(output_dir / "overlays" / f"{image_id}_ca_apsrg_overlay.png", overlay_mask_on_image(image_rgb, ca_mask))

    row = {
        "dataset": dataset,
        "image_id": image_id,
        "image_path": str(image_path),
        "mask_path": str(mask_path) if mask_path else "",
        "fov_path": str(fov_path) if fov_path else "",
        "ca_apsrg_applied": use_refine,
    }

    if baseline_metrics is not None:
        row.update({f"baseline_{k}": v for k, v in metrics_to_dict(baseline_metrics).items()})
    if ca_metrics is not None:
        row.update({f"ca_apsrg_{k}": v for k, v in metrics_to_dict(ca_metrics).items()})

    # Add context debug values.
    if "context_features" in ca_debug:
        for k, v in ca_debug["context_features"].items():
            row[f"context_{k}"] = v
    if "selected_parameters" in ca_debug:
        for k, v in ca_debug["selected_parameters"].items():
            row[f"selected_{k}"] = v

    return row


def run_batch(
    manifest_path: str | Path,
    output_dir: str | Path,
    *,
    always_refine: bool = True,
    precision_threshold: float = 0.95,
) -> pd.DataFrame:
    manifest_path = Path(manifest_path)
    output_dir = ensure_dir(output_dir)

    df = pd.read_csv(manifest_path)
    rows = []

    for _, item in df.iterrows():
        row = run_single_image(
            image_path=item["image_path"],
            mask_path=item.get("mask_path", ""),
            fov_path=item.get("fov_path", ""),
            output_dir=output_dir,
            image_id=str(item.get("image_id", "")),
            dataset=str(item.get("dataset", "")),
            always_refine=always_refine,
            precision_threshold=precision_threshold,
        )
        rows.append(row)

    results = pd.DataFrame(rows)
    results.to_csv(output_dir / "metrics_summary.csv", index=False)
    return results
