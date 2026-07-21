"""
Edge-delayed priority-queue region growing for retinal vessel segmentation.

This module adapts the SRG growing strategy described by Kang et al. to the
binary vessel-segmentation pipeline used by APSRG/CA-APSRG.

Main ideas:
- every connected seed component is treated as an initial region;
- candidate pixels are processed using a priority queue;
- fuzzy distance is computed between a candidate pixel and the mean intensity
  of its neighboring region;
- connected-edge membership delays edge pixels so smoother vessel interiors
  are processed first;
- growth remains constrained by the candidate vessel map and optional FoV.

The original Kang-style priority is d_H = d * CE. A small edge floor can be
used to avoid every perfectly non-edge pixel obtaining an identical zero
priority. Additive and hybrid priority modes are also provided for controlled
retinal-vessel experiments.
"""

from __future__ import annotations

import heapq
from dataclasses import asdict, dataclass
from itertools import count
from typing import Any, Literal, Optional

import cv2
import numpy as np

from src.segmentation.srg_features import compute_connected_edge_map
from src.utils.image_io import ensure_binary_mask, to_uint8


PriorityMode = Literal["kang_product", "additive", "hybrid"]


@dataclass(frozen=True)
class EdgeDelayedRegionGrowingParams:
    """Configuration for edge-delayed region growing."""

    enabled: bool = True

    # Priority calculation.
    priority_mode: PriorityMode = "kang_product"
    fuzzy_distance_scale: float = 0.4
    connected_edge_wd: float = 0.4
    edge_floor: float = 0.05
    edge_weight: float = 0.35

    # Value 1.0 means the fuzzy-distance rejection gate is disabled.
    max_fuzzy_distance: float = 1.0

    # Recalculate the priority when a region mean changes.
    recompute_priority: bool = True
    priority_tolerance: float = 1e-6

    # Store growth-order map for debugging and Streamlit.
    record_growth_order: bool = True

    @classmethod
    def from_dict(
        cls,
        config: dict[str, Any] | None,
    ) -> "EdgeDelayedRegionGrowingParams":
        """Create parameters from a YAML-like dictionary."""
        if not config:
            return cls()

        return cls(
            enabled=bool(config.get("enabled", True)),
            priority_mode=str(
                config.get("priority_mode", "kang_product")
            ),
            fuzzy_distance_scale=float(
                config.get("fuzzy_distance_scale", 0.4)
            ),
            connected_edge_wd=float(
                config.get("connected_edge_wd", 0.4)
            ),
            edge_floor=float(config.get("edge_floor", 0.05)),
            edge_weight=float(config.get("edge_weight", 0.35)),
            max_fuzzy_distance=float(
                config.get("max_fuzzy_distance", 1.0)
            ),
            recompute_priority=bool(
                config.get("recompute_priority", True)
            ),
            priority_tolerance=float(
                config.get("priority_tolerance", 1e-6)
            ),
            record_growth_order=bool(
                config.get("record_growth_order", True)
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return parameters as a dictionary."""
        return asdict(self)


def _prepare_bool_mask(
    mask: np.ndarray,
    *,
    name: str,
    shape: tuple[int, int] | None = None,
) -> np.ndarray:
    """Convert a mask to boolean and validate its shape."""
    result = ensure_binary_mask(
        mask,
        return_uint8=False,
    ).astype(bool)

    if result.ndim != 2:
        raise ValueError(
            f"{name} must be 2D, got shape {result.shape}"
        )

    if shape is not None and result.shape != shape:
        raise ValueError(
            f"{name} shape {result.shape} does not match {shape}"
        )

    return result


def _prepare_intensity(
    image: Optional[np.ndarray],
    shape: tuple[int, int],
) -> np.ndarray:
    """Prepare a 2D float32 intensity image in the range 0..255."""
    if image is None:
        return np.zeros(shape, dtype=np.float32)

    arr = np.asarray(image)

    if arr.ndim == 3:
        arr = cv2.cvtColor(
            to_uint8(arr),
            cv2.COLOR_RGB2GRAY,
        )

    if arr.ndim != 2:
        raise ValueError(
            f"intensity_image must be 2D, got shape {arr.shape}"
        )

    if arr.shape != shape:
        raise ValueError(
            f"intensity_image shape {arr.shape} does not match {shape}"
        )

    return to_uint8(arr).astype(np.float32)


def _prepare_connected_edge(
    connected_edge_map: Optional[np.ndarray],
    *,
    edge_image: np.ndarray,
    shape: tuple[int, int],
    wd: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return CE, edge intensity, and edge-direction maps."""
    if connected_edge_map is None:
        connected_edge, edge_intensity, edge_direction = (
            compute_connected_edge_map(
                edge_image,
                wd=float(wd),
            )
        )

        return (
            np.clip(
                connected_edge,
                0.0,
                1.0,
            ).astype(np.float32),
            np.clip(
                edge_intensity,
                0.0,
                1.0,
            ).astype(np.float32),
            edge_direction.astype(np.uint8),
        )

    connected_edge = np.asarray(
        connected_edge_map,
        dtype=np.float32,
    )

    if connected_edge.shape != shape:
        raise ValueError(
            "connected_edge_map shape "
            f"{connected_edge.shape} does not match {shape}"
        )

    connected_edge = np.clip(
        connected_edge,
        0.0,
        1.0,
    )

    edge_intensity = connected_edge.copy()
    edge_direction = np.zeros(
        shape,
        dtype=np.uint8,
    )

    return connected_edge, edge_intensity, edge_direction


def get_neighbor_offsets(
    connectivity: int,
) -> list[tuple[int, int]]:
    """Return 4- or 8-connected neighbor offsets."""
    if int(connectivity) == 4:
        return [
            (-1, 0),
            (0, -1),
            (0, 1),
            (1, 0),
        ]

    if int(connectivity) == 8:
        return [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]

    raise ValueError(
        "connectivity must be either 4 or 8"
    )


def compute_fuzzy_region_distance(
    pixel_value: float,
    region_mean: float,
    *,
    scale: float = 0.4,
) -> float:
    """
    Compute fuzzy distance between one pixel and a region mean.

    Intensity values are normalized from 0..255 to 0..1:

        d = min(abs(pixel - region_mean) / scale, 1)
    """
    scale = max(
        float(scale),
        1e-8,
    )

    difference = (
        abs(
            float(pixel_value) - float(region_mean)
        )
        / 255.0
    )

    return float(
        min(
            difference / scale,
            1.0,
        )
    )


def compute_edge_delayed_priority(
    fuzzy_distance: float,
    connected_edge_value: float,
    *,
    params: EdgeDelayedRegionGrowingParams,
) -> float:
    """Compute candidate priority; smaller values are processed first."""
    distance = float(
        np.clip(
            fuzzy_distance,
            0.0,
            1.0,
        )
    )

    edge = float(
        np.clip(
            connected_edge_value,
            0.0,
            1.0,
        )
    )

    mode = str(
        params.priority_mode
    ).lower()

    if mode == "kang_product":
        effective_edge = max(
            edge,
            float(params.edge_floor),
        )

        return distance * effective_edge

    if mode == "additive":
        return (
            distance
            + float(params.edge_weight) * edge
        )

    if mode == "hybrid":
        effective_edge = max(
            edge,
            float(params.edge_floor),
        )

        return (
            distance * effective_edge
            + float(params.edge_weight) * edge
        )

    raise ValueError(
        f"Unsupported priority_mode: {params.priority_mode}"
    )


def _neighbor_region_ids(
    labels: np.ndarray,
    y: int,
    x: int,
    neighbors: list[tuple[int, int]],
) -> set[int]:
    """Return positive region labels adjacent to one pixel."""
    h, w = labels.shape
    region_ids: set[int] = set()

    for dy, dx in neighbors:
        yy = y + dy
        xx = x + dx

        if (
            yy < 0
            or yy >= h
            or xx < 0
            or xx >= w
        ):
            continue

        region_id = int(
            labels[yy, xx]
        )

        if region_id > 0:
            region_ids.add(
                region_id
            )

    return region_ids


def _best_neighbor_region(
    labels: np.ndarray,
    intensity: np.ndarray,
    region_sums: np.ndarray,
    region_counts: np.ndarray,
    y: int,
    x: int,
    neighbors: list[tuple[int, int]],
    *,
    distance_scale: float,
) -> tuple[int, float, float] | None:
    """
    Select the adjacent region with minimum fuzzy distance.

    Returns:
        region_id,
        fuzzy_distance,
        raw intensity difference.
    """
    region_ids = _neighbor_region_ids(
        labels,
        y,
        x,
        neighbors,
    )

    if not region_ids:
        return None

    pixel_value = float(
        intensity[y, x]
    )

    best_region_id = 0
    best_fuzzy_distance = float("inf")
    best_raw_difference = float("inf")

    for region_id in region_ids:
        count_value = int(
            region_counts[region_id]
        )

        if count_value <= 0:
            continue

        region_mean = (
            float(region_sums[region_id])
            / float(count_value)
        )

        raw_difference = abs(
            pixel_value - region_mean
        )

        fuzzy_distance = (
            compute_fuzzy_region_distance(
                pixel_value,
                region_mean,
                scale=distance_scale,
            )
        )

        if (
            fuzzy_distance < best_fuzzy_distance
            or (
                abs(
                    fuzzy_distance
                    - best_fuzzy_distance
                )
                <= 1e-12
                and raw_difference
                < best_raw_difference
            )
        ):
            best_region_id = int(
                region_id
            )
            best_fuzzy_distance = float(
                fuzzy_distance
            )
            best_raw_difference = float(
                raw_difference
            )

    if best_region_id <= 0:
        return None

    return (
        best_region_id,
        best_fuzzy_distance,
        best_raw_difference,
    )


def edge_delayed_region_growing(
    candidate_map: np.ndarray,
    seed_mask: np.ndarray,
    intensity_image: Optional[np.ndarray] = None,
    *,
    connected_edge_map: Optional[np.ndarray] = None,
    edge_image: Optional[np.ndarray] = None,
    fov_mask: Optional[np.ndarray] = None,
    params: Optional[
        EdgeDelayedRegionGrowingParams
    ] = None,
    connectivity: int = 8,
    max_intensity_difference: float = 18.0,
    max_iterations: int = 500_000,
) -> tuple[np.ndarray, dict[str, Any]]:
    """
    Grow vessel regions using fuzzy distance and connected-edge delay.

    Each connected seed component becomes an initial region. Candidate pixels
    adjacent to existing regions are placed into a priority queue. The queue is
    ordered by fuzzy pixel-to-region distance corrected by connected-edge
    membership, so pixels on strong connected edges are generally processed
    later.
    """
    params = (
        params
        or EdgeDelayedRegionGrowingParams()
    )

    candidate = _prepare_bool_mask(
        candidate_map,
        name="candidate_map",
    )

    shape = candidate.shape

    seeds = _prepare_bool_mask(
        seed_mask,
        name="seed_mask",
        shape=shape,
    )

    if fov_mask is not None:
        fov = _prepare_bool_mask(
            fov_mask,
            name="fov_mask",
            shape=shape,
        )

        candidate &= fov
    else:
        fov = None

    seeds &= candidate

    intensity = _prepare_intensity(
        intensity_image,
        shape,
    )

    if edge_image is None:
        edge_source = intensity
    else:
        edge_source = _prepare_intensity(
            edge_image,
            shape,
        )

    (
        connected_edge,
        edge_intensity,
        edge_direction,
    ) = _prepare_connected_edge(
        connected_edge_map,
        edge_image=edge_source,
        shape=shape,
        wd=params.connected_edge_wd,
    )

    if not params.enabled:
        result = seeds.copy()

        return result, {
            "enabled": False,
            "mode": "edge_delayed",
            "connected_edge": connected_edge,
            "edge_intensity": edge_intensity,
            "edge_direction": edge_direction,
            "region_labels": result.astype(
                np.int32
            ),
            "growth_order": np.zeros(
                shape,
                dtype=np.int32,
            ),
            "n_output_pixels": int(
                result.sum()
            ),
            "params": params.to_dict(),
        }

    if not seeds.any():
        empty = np.zeros(
            shape,
            dtype=bool,
        )

        return empty, {
            "enabled": True,
            "mode": "edge_delayed",
            "reason": "No valid seed pixels",
            "connected_edge": connected_edge,
            "edge_intensity": edge_intensity,
            "edge_direction": edge_direction,
            "region_labels": np.zeros(
                shape,
                dtype=np.int32,
            ),
            "growth_order": np.zeros(
                shape,
                dtype=np.int32,
            ),
            "n_initial_seed_components": 0,
            "n_output_pixels": 0,
            "params": params.to_dict(),
        }

    conn = (
        8
        if int(connectivity) == 8
        else 4
    )

    n_labels, labels = (
        cv2.connectedComponents(
            seeds.astype(np.uint8),
            connectivity=conn,
        )
    )

    labels = labels.astype(
        np.int32
    )

    region_sums = np.bincount(
        labels.reshape(-1),
        weights=intensity.reshape(-1),
        minlength=n_labels,
    ).astype(np.float64)

    region_counts = np.bincount(
        labels.reshape(-1),
        minlength=n_labels,
    ).astype(np.int64)

    neighbors = get_neighbor_offsets(
        connectivity
    )

    queue: list[
        tuple[float, int, int, int, int]
    ] = []

    sequence = count()

    best_queued_priority = np.full(
        shape,
        np.inf,
        dtype=np.float64,
    )

    growth_order = np.zeros(
        shape,
        dtype=np.int32,
    )

    if params.record_growth_order:
        growth_order[seeds] = 1

    accepted_pixels = 0
    rejected_by_intensity = 0
    rejected_by_fuzzy_distance = 0
    stale_queue_entries = 0
    reprioritized_entries = 0

    def enqueue_pixel(
        y: int,
        x: int,
    ) -> None:
        """Evaluate and enqueue one unlabeled candidate pixel."""
        if (
            labels[y, x] > 0
            or not candidate[y, x]
        ):
            return

        best = _best_neighbor_region(
            labels,
            intensity,
            region_sums,
            region_counts,
            y,
            x,
            neighbors,
            distance_scale=(
                params.fuzzy_distance_scale
            ),
        )

        if best is None:
            return

        (
            region_id,
            fuzzy_distance,
            _,
        ) = best

        priority = (
            compute_edge_delayed_priority(
                fuzzy_distance,
                float(
                    connected_edge[y, x]
                ),
                params=params,
            )
        )

        if (
            priority + 1e-12
            >= best_queued_priority[y, x]
        ):
            return

        best_queued_priority[
            y,
            x,
        ] = priority

        heapq.heappush(
            queue,
            (
                float(priority),
                next(sequence),
                int(y),
                int(x),
                int(region_id),
            ),
        )

    seed_y, seed_x = np.where(
        seeds
    )

    for y, x in zip(
        seed_y,
        seed_x,
    ):
        for dy, dx in neighbors:
            yy = int(y + dy)
            xx = int(x + dx)

            if (
                yy < 0
                or yy >= shape[0]
                or xx < 0
                or xx >= shape[1]
            ):
                continue

            enqueue_pixel(
                yy,
                xx,
            )

    iterations = 0
    max_iterations = int(
        max_iterations
    )

    max_raw_difference = float(
        max_intensity_difference
    )

    max_fuzzy_distance = float(
        params.max_fuzzy_distance
    )

    tolerance = max(
        float(params.priority_tolerance),
        0.0,
    )

    while queue:
        (
            priority,
            _,
            y,
            x,
            _queued_region_id,
        ) = heapq.heappop(
            queue
        )

        iterations += 1

        if (
            max_iterations > 0
            and iterations > max_iterations
        ):
            break

        if (
            labels[y, x] > 0
            or not candidate[y, x]
        ):
            stale_queue_entries += 1
            continue

        if (
            priority
            > best_queued_priority[y, x]
            + tolerance
        ):
            stale_queue_entries += 1
            continue

        best = _best_neighbor_region(
            labels,
            intensity,
            region_sums,
            region_counts,
            y,
            x,
            neighbors,
            distance_scale=(
                params.fuzzy_distance_scale
            ),
        )

        if best is None:
            best_queued_priority[
                y,
                x,
            ] = np.inf

            continue

        (
            region_id,
            fuzzy_distance,
            raw_difference,
        ) = best

        current_priority = (
            compute_edge_delayed_priority(
                fuzzy_distance,
                float(
                    connected_edge[y, x]
                ),
                params=params,
            )
        )

        if (
            params.recompute_priority
            and current_priority
            > priority + tolerance
        ):
            best_queued_priority[
                y,
                x,
            ] = current_priority

            heapq.heappush(
                queue,
                (
                    float(current_priority),
                    next(sequence),
                    int(y),
                    int(x),
                    int(region_id),
                ),
            )

            reprioritized_entries += 1
            continue

        if (
            max_raw_difference > 0.0
            and raw_difference
            > max_raw_difference
        ):
            rejected_by_intensity += 1
            best_queued_priority[
                y,
                x,
            ] = np.inf

            continue

        if (
            0.0
            <= max_fuzzy_distance
            < 1.0
            and fuzzy_distance
            > max_fuzzy_distance
        ):
            rejected_by_fuzzy_distance += 1
            best_queued_priority[
                y,
                x,
            ] = np.inf

            continue

        labels[
            y,
            x,
        ] = int(region_id)

        best_queued_priority[
            y,
            x,
        ] = np.inf

        region_sums[
            region_id
        ] += float(
            intensity[y, x]
        )

        region_counts[
            region_id
        ] += 1

        accepted_pixels += 1

        if params.record_growth_order:
            growth_order[
                y,
                x,
            ] = accepted_pixels + 1

        for dy, dx in neighbors:
            yy = y + dy
            xx = x + dx

            if (
                yy < 0
                or yy >= shape[0]
                or xx < 0
                or xx >= shape[1]
            ):
                continue

            enqueue_pixel(
                yy,
                xx,
            )

    result = labels > 0

    if fov is not None:
        result &= fov
        labels[~fov] = 0
        growth_order[~fov] = 0

    final_region_means: dict[
        str,
        float,
    ] = {}

    final_region_sizes: dict[
        str,
        int,
    ] = {}

    for region_id in range(
        1,
        n_labels,
    ):
        region_count = int(
            region_counts[region_id]
        )

        if region_count <= 0:
            continue

        final_region_means[
            str(region_id)
        ] = float(
            region_sums[region_id]
            / float(region_count)
        )

        final_region_sizes[
            str(region_id)
        ] = region_count

    debug: dict[str, Any] = {
        "enabled": True,
        "mode": "edge_delayed",
        "priority_mode": str(
            params.priority_mode
        ),
        "connected_edge": connected_edge,
        "edge_intensity": edge_intensity,
        "edge_direction": edge_direction,
        "region_labels": labels,
        "growth_order": growth_order,
        "n_initial_seed_pixels": int(
            seeds.sum()
        ),
        "n_initial_seed_components": int(
            n_labels - 1
        ),
        "n_candidate_pixels": int(
            candidate.sum()
        ),
        "n_accepted_growth_pixels": int(
            accepted_pixels
        ),
        "n_rejected_by_intensity": int(
            rejected_by_intensity
        ),
        "n_rejected_by_fuzzy_distance": int(
            rejected_by_fuzzy_distance
        ),
        "n_stale_queue_entries": int(
            stale_queue_entries
        ),
        "n_reprioritized_entries": int(
            reprioritized_entries
        ),
        "n_output_pixels": int(
            result.sum()
        ),
        "iterations": int(
            iterations
        ),
        "max_iterations_reached": bool(
            max_iterations > 0
            and iterations > max_iterations
        ),
        "remaining_queue_size": int(
            len(queue)
        ),
        "final_region_means": (
            final_region_means
        ),
        "final_region_sizes": (
            final_region_sizes
        ),
        "params": params.to_dict(),
    }

    return result.astype(bool), debug