from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml


@dataclass
class ProjectConfig:
    raw_root: Path
    working_png_root: Path
    manifest_path: Path
    output_dir: Path
    always_refine: bool
    false_positive_precision_threshold: float
    params: Dict[str, Any]

    @classmethod
    def from_yaml(cls, config_path: str | Path = "configs/default.yaml") -> "ProjectConfig":
        config_path = Path(config_path)
        with config_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return cls(
            raw_root=Path(data["data"]["raw_root"]),
            working_png_root=Path(data["data"]["working_png_root"]),
            manifest_path=Path(data["data"]["manifest_path"]),
            output_dir=Path(data["experiment"]["output_dir"]),
            always_refine=bool(data["experiment"].get("always_refine", True)),
            false_positive_precision_threshold=float(
                data["experiment"].get("false_positive_precision_threshold", 0.95)
            ),
            params=data,
        )
