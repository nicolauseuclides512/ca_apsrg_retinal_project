"""
APSRG implementation for retinal blood vessel segmentation.

Processing flow:

1. Read the preprocessed fundus image, typically green channel + CLAHE.
2. Enhance vessel-like structures using multi-scale black-hat morphology.
3. Construct the candidate vessel map.
4. Select seeds using percentile/polling, fuzzy SRG, Harris Corner,
   or selective fuzzy-Harris polling.
5. Grow vessel regions using BFS or edge-delayed priority region growing.
6. Apply light binary post-processing.
7. Forward the APSRG mask to the CA-APSRG context-aware refinement stage.

Conventions:
- Input image: grayscale uint8, shape (H, W).
- FoV mask: boolean or binary uint8, shape (H, W).
- Output vessel mask: boolean, shape (H, W).
"""

from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal, Optional

import cv2
import numpy as np

from src.segmentation.skimage_compat import remove_small_holes_compat
from src.segmentation.apsrg_harris import HarrisSeedParams, select_harris_seeds
from src.segmentation.srg_features import SRGFeatureParams, select_fuzzy_srg_seeds
from src.segmentation.edge_delayed_region_growing import EdgeDelayedRegionGrowingParams, edge_delayed_region_growing
from src.segmentation.hybrid_seed_selection import (
    HybridSeedParams,
    select_hybrid_fuzzy_harris_seeds,
)
from src.utils.image_io import (
    ensure_binary_mask,
    normalize_to_uint8,
    read_binary_mask,
    read_gray_image,
    save_binary_mask,
    to_uint8,
)

VesselEnhancementMethod = Literal["blackhat_multiscale", "blackhat", "none"]
SeedSelectionMethod = Literal[
    "percentile",
    "polling",
    "percentile_polling",
    "polling_percentile",

    "harris_polling",
    "percentile_harris_polling",
    "harris_percentile",

    "polling_harris",
    "hybrid_harris",

    "fuzzy_srg",
    "percentile_fuzzy_srg",
    "polling_fuzzy_srg",

    "fuzzy_harris",
    "hybrid_fuzzy_harris",
    "selective_fuzzy_harris",
]

RegionGrowingMode = Literal[
    "bfs",
    "edge_delayed",
]

@dataclass(frozen=True)
class APSRGParams:
    """Configuration parameters for the APSRG-style baseline."""

    vessel_enhancement_method: VesselEnhancementMethod = "blackhat_multiscale"
    vesselness_kernel_sizes: tuple[int, ...] = (7, 11, 15)

    seed_selection_method: SeedSelectionMethod = "percentile_polling"
    seed_percentile: float = 92.0
    candidate_percentile: float = 78.0

    polling_window_size: int = 16
    polling_top_percentile: float = 97.0
    min_seed_distance: int = 2

    region_growing_connectivity: int = 8
    region_growing_mode: RegionGrowingMode = "bfs"
    max_intensity_difference: float = 18.0
    max_iterations: int = 500_000

    edge_delayed_region_growing: EdgeDelayedRegionGrowingParams = field(
        default_factory=EdgeDelayedRegionGrowingParams
    )

    min_component_area: int = 8
    fill_small_holes_area: int = 8
    harris_seed: HarrisSeedParams = field(default_factory=HarrisSeedParams)
    srg_features: SRGFeatureParams = field(default_factory=SRGFeatureParams)
    hybrid_seed: HybridSeedParams = field(default_factory=HybridSeedParams)

    @classmethod
    def from_dict(cls, config: dict[str, Any] | None) -> "APSRGParams":
        """Create APSRGParams from config['apsrg_baseline']."""
        if not config:
            return cls()

        kernel_sizes = config.get("vesselness_kernel_sizes", (7, 11, 15))
        if isinstance(kernel_sizes, list):
            kernel_sizes = tuple(int(k) for k in kernel_sizes)
        else:
            kernel_sizes = tuple(int(k) for k in kernel_sizes)

        harris_config = (
                config.get("harris_seed", None)
                or config.get("harris", None)
                or {}
        )

        srg_config = (
                config.get("srg_features", None)
                or config.get("srg_core", None)
                or {}
        )

        hybrid_config = (
                config.get("hybrid_seed")
                or config.get("hybrid_fuzzy_harris")
                or {}
        )

        edge_delayed_config = (
                config.get("edge_delayed_region_growing")
                or config.get("edge_delayed")
                or {}
        )

        return cls(
            vessel_enhancement_method=str(
                config.get(
                    "vessel_enhancement_method",
                    "blackhat_multiscale",
                )
            ),
            vesselness_kernel_sizes=kernel_sizes,

            seed_selection_method=str(
                config.get(
                    "seed_selection_method",
                    "percentile_polling",
                )
            ),

            seed_percentile=float(
                config.get("seed_percentile", 92.0)
            ),
            candidate_percentile=float(
                config.get("candidate_percentile", 78.0)
            ),

            polling_window_size=int(
                config.get("polling_window_size", 16)
            ),
            polling_top_percentile=float(
                config.get("polling_top_percentile", 97.0)
            ),
            min_seed_distance=int(
                config.get("min_seed_distance", 2)
            ),

            region_growing_connectivity=int(
                config.get(
                    "region_growing_connectivity",
                    8,
                )
            ),

            region_growing_mode=str(
                config.get(
                    "region_growing_mode",
                    "bfs",
                )
            ),

            max_intensity_difference=float(
                config.get(
                    "max_intensity_difference",
                    18.0,
                )
            ),

            max_iterations=int(
                config.get(
                    "max_iterations",
                    500_000,
                )
            ),

            min_component_area=int(
                config.get("min_component_area", 8)
            ),

            fill_small_holes_area=int(
                config.get("fill_small_holes_area", 8)
            ),

            harris_seed=HarrisSeedParams.from_dict(
                harris_config
            ),

            srg_features=SRGFeatureParams.from_dict(
                srg_config
            ),

            hybrid_seed=HybridSeedParams.from_dict(
                hybrid_config
            ),

            edge_delayed_region_growing=(
                EdgeDelayedRegionGrowingParams.from_dict(
                    edge_delayed_config
                )
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return parameters as a dictionary."""
        return asdict(self)


APSRGConfig = APSRGParams


def _ensure_odd_positive(value: int, minimum: int = 3) -> int:
    """Return an odd positive integer suitable for a morphology kernel."""
    value = max(int(value), minimum)
    if value % 2 == 0:
        value += 1
    return value


def _prepare_gray(gray: np.ndarray) -> np.ndarray:
    """Validate and convert input image to grayscale uint8."""
    arr = np.asarray(gray)

    if arr.ndim == 3:
        arr = cv2.cvtColor(to_uint8(arr), cv2.COLOR_RGB2GRAY)

    if arr.ndim != 2:
        raise ValueError(f"Expected 2D grayscale image, got shape {arr.shape}")

    return to_uint8(arr)


def _prepare_fov_mask(fov_mask: Optional[np.ndarray], shape: tuple[int, int]) -> Optional[np.ndarray]:
    """Validate optional FoV mask and return boolean mask."""
    if fov_mask is None:
        return None

    fov = ensure_binary_mask(fov_mask, return_uint8=False)

    if fov.shape != shape:
        raise ValueError(f"FoV mask shape {fov.shape} does not match image shape {shape}")

    return fov


def get_neighbors(connectivity: int = 8) -> list[tuple[int, int]]:
    """Return 4- or 8-connected neighbor offsets."""
    if int(connectivity) == 4:
        return [(-1, 0), (0, -1), (0, 1), (1, 0)]

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

    raise ValueError("connectivity must be either 4 or 8")


def enhance_dark_vessels(
    gray: np.ndarray,
    kernel_sizes: tuple[int, ...] = (7, 11, 15),
    *,
    method: VesselEnhancementMethod = "blackhat_multiscale",
) -> np.ndarray:
    """
    Enhance dark vessel-like structures in a grayscale fundus image.

    Black-hat morphology is used because retinal vessels usually appear darker
    than their local background in the green channel.
    """
    gray_u8 = _prepare_gray(gray)
    method = str(method).lower()

    if method in {"none", "", "false"}:
        return normalize_to_uint8(gray_u8)

    if method == "blackhat":
        kernel_size = _ensure_odd_positive(kernel_sizes[0] if kernel_sizes else 11)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        blackhat = cv2.morphologyEx(gray_u8, cv2.MORPH_BLACKHAT, kernel)
        return normalize_to_uint8(blackhat)

    if method == "blackhat_multiscale":
        enhanced_list: list[np.ndarray] = []

        for k in kernel_sizes:
            kernel_size = _ensure_odd_positive(k)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
            blackhat = cv2.morphologyEx(gray_u8, cv2.MORPH_BLACKHAT, kernel)
            enhanced_list.append(blackhat.astype(np.float32))

        if not enhanced_list:
            return np.zeros_like(gray_u8, dtype=np.uint8)

        enhanced = np.max(np.stack(enhanced_list, axis=0), axis=0)
        return normalize_to_uint8(enhanced)

    raise ValueError(f"Unsupported vessel_enhancement_method: {method}")


def _valid_pixels(image: np.ndarray, fov_mask: Optional[np.ndarray] = None, *, ignore_zero: bool = True) -> np.ndarray:
    """Return pixels used for percentile threshold estimation."""
    if fov_mask is not None:
        pixels = image[fov_mask]
    else:
        pixels = image.reshape(-1)

    if ignore_zero:
        pixels = pixels[pixels > 0]

    return pixels


def compute_percentile_thresholds(
    vesselness: np.ndarray,
    fov_mask: Optional[np.ndarray] = None,
    *,
    seed_percentile: float = 92.0,
    candidate_percentile: float = 78.0,
) -> tuple[float, float]:
    """Compute seed and candidate thresholds from valid vesselness pixels."""
    pixels = _valid_pixels(vesselness, fov_mask=fov_mask, ignore_zero=True)

    if pixels.size == 0:
        return 255.0, 255.0

    seed_thr = float(np.percentile(pixels, float(seed_percentile)))
    candidate_thr = float(np.percentile(pixels, float(candidate_percentile)))

    candidate_thr = min(candidate_thr, seed_thr)

    return seed_thr, candidate_thr


def create_candidate_map(
    vesselness: np.ndarray,
    candidate_threshold: float,
    fov_mask: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Create a binary candidate vessel map from vesselness thresholding."""
    candidate = np.asarray(vesselness) >= float(candidate_threshold)

    if fov_mask is not None:
        candidate &= fov_mask

    return candidate


def select_percentile_seeds(
    vesselness: np.ndarray,
    seed_threshold: float,
    fov_mask: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Select seed pixels using a global percentile threshold."""
    seeds = np.asarray(vesselness) >= float(seed_threshold)

    if fov_mask is not None:
        seeds &= fov_mask

    return seeds


def _local_maxima_mask(vesselness: np.ndarray, min_distance: int = 2) -> np.ndarray:
    """Return a simple local maxima mask using dilation."""
    radius = max(int(min_distance), 1)
    kernel_size = 2 * radius + 1
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    dilated = cv2.dilate(to_uint8(vesselness), kernel)

    return np.asarray(vesselness) >= dilated


def select_polling_seeds(
    vesselness: np.ndarray,
    fov_mask: Optional[np.ndarray] = None,
    *,
    window_size: int = 16,
    top_percentile: float = 97.0,
    global_seed_threshold: Optional[float] = None,
    min_seed_distance: int = 2,
) -> np.ndarray:
    """
    Select seed pixels automatically using local polling.

    The image is scanned in non-overlapping windows. In each valid window, pixels
    near the local maximum vesselness response are selected as seeds. This keeps
    seeds distributed over the retinal image instead of relying only on global
    high-intensity responses.
    """
    vesselness_u8 = to_uint8(vesselness)
    h, w = vesselness_u8.shape
    window_size = max(int(window_size), 4)

    seeds = np.zeros((h, w), dtype=bool)
    local_maxima = _local_maxima_mask(vesselness_u8, min_distance=min_seed_distance)

    for y0 in range(0, h, window_size):
        y1 = min(y0 + window_size, h)

        for x0 in range(0, w, window_size):
            x1 = min(x0 + window_size, w)

            patch = vesselness_u8[y0:y1, x0:x1]

            if fov_mask is not None:
                valid = fov_mask[y0:y1, x0:x1]
                patch_values = patch[valid]
            else:
                valid = np.ones(patch.shape, dtype=bool)
                patch_values = patch.reshape(-1)

            patch_values = patch_values[patch_values > 0]

            if patch_values.size == 0:
                continue

            local_thr = float(np.percentile(patch_values, float(top_percentile)))

            if global_seed_threshold is not None:
                local_thr = max(local_thr, float(global_seed_threshold) * 0.75)

            patch_seed = (patch >= local_thr) & valid & local_maxima[y0:y1, x0:x1]
            seeds[y0:y1, x0:x1] |= patch_seed

    if global_seed_threshold is not None:
        seeds |= vesselness_u8 >= float(global_seed_threshold)

    if fov_mask is not None:
        seeds &= fov_mask

    return seeds


def select_automatic_seeds_with_debug(
    vesselness: np.ndarray,
    fov_mask: Optional[np.ndarray] = None,
    *,
    params: APSRGParams,
    seed_threshold: float,
    candidate_map: Optional[np.ndarray] = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Select APSRG seeds and return method-specific debug information."""
    method = str(params.seed_selection_method).lower()

    if method == "percentile":
        seeds = select_percentile_seeds(
            vesselness,
            seed_threshold,
            fov_mask=fov_mask,
        )
        return seeds, {
            "method": method,
            "n_seed_pixels": int(seeds.sum()),
        }

    if method == "polling":
        seeds = select_polling_seeds(
            vesselness,
            fov_mask=fov_mask,
            window_size=params.polling_window_size,
            top_percentile=params.polling_top_percentile,
            global_seed_threshold=None,
            min_seed_distance=params.min_seed_distance,
        )
        return seeds, {
            "method": method,
            "n_seed_pixels": int(seeds.sum()),
        }

    if method in {"percentile_polling", "polling_percentile"}:
        percentile_seeds = select_percentile_seeds(
            vesselness,
            seed_threshold,
            fov_mask=fov_mask,
        )

        polling_seeds = select_polling_seeds(
            vesselness,
            fov_mask=fov_mask,
            window_size=params.polling_window_size,
            top_percentile=params.polling_top_percentile,
            global_seed_threshold=seed_threshold,
            min_seed_distance=params.min_seed_distance,
        )

        seeds = percentile_seeds | polling_seeds

        return seeds, {
            "method": method,
            "percentile_seeds": percentile_seeds,
            "polling_seeds": polling_seeds,
            "n_seed_pixels": int(seeds.sum()),
        }

    if method == "harris_polling":
        seeds, debug = select_harris_seeds(
            vesselness,
            vesselness=vesselness,
            candidate_map=candidate_map,
            fov_mask=fov_mask,
            params=params.harris_seed,
        )
        debug["method"] = method
        return seeds, debug

    if method in {
        "percentile_harris_polling",
        "harris_percentile",
    }:
        percentile_seeds = select_percentile_seeds(
            vesselness,
            seed_threshold,
            fov_mask=fov_mask,
        )

        harris_seeds, harris_debug = select_harris_seeds(
            vesselness,
            vesselness=vesselness,
            candidate_map=candidate_map,
            fov_mask=fov_mask,
            params=params.harris_seed,
        )

        seeds = percentile_seeds | harris_seeds

        return seeds, {
            "method": method,
            "percentile_seeds": percentile_seeds,
            "harris_debug": harris_debug,
            "n_seed_pixels": int(seeds.sum()),
        }

    if method in {"polling_harris", "hybrid_harris"}:
        polling_seeds = select_polling_seeds(
            vesselness,
            fov_mask=fov_mask,
            window_size=params.polling_window_size,
            top_percentile=params.polling_top_percentile,
            global_seed_threshold=seed_threshold,
            min_seed_distance=params.min_seed_distance,
        )

        harris_seeds, harris_debug = select_harris_seeds(
            vesselness,
            vesselness=vesselness,
            candidate_map=candidate_map,
            fov_mask=fov_mask,
            params=params.harris_seed,
        )

        seeds = polling_seeds | harris_seeds

        return seeds, {
            "method": method,
            "polling_seeds": polling_seeds,
            "harris_debug": harris_debug,
            "n_seed_pixels": int(seeds.sum()),
        }

    if method == "fuzzy_srg":
        seeds, debug = select_fuzzy_srg_seeds(
            vesselness,
            candidate_map=candidate_map,
            fov_mask=fov_mask,
            params=params.srg_features,
        )
        debug["method"] = method
        return seeds, debug

    if method == "percentile_fuzzy_srg":
        percentile_seeds = select_percentile_seeds(
            vesselness,
            seed_threshold,
            fov_mask=fov_mask,
        )

        fuzzy_seeds, fuzzy_debug = select_fuzzy_srg_seeds(
            vesselness,
            candidate_map=candidate_map,
            fov_mask=fov_mask,
            params=params.srg_features,
        )

        seeds = percentile_seeds | fuzzy_seeds

        return seeds, {
            "method": method,
            "percentile_seeds": percentile_seeds,
            "fuzzy_debug": fuzzy_debug,
            "n_seed_pixels": int(seeds.sum()),
        }

    if method == "polling_fuzzy_srg":
        polling_seeds = select_polling_seeds(
            vesselness,
            fov_mask=fov_mask,
            window_size=params.polling_window_size,
            top_percentile=params.polling_top_percentile,
            global_seed_threshold=seed_threshold,
            min_seed_distance=params.min_seed_distance,
        )

        fuzzy_seeds, fuzzy_debug = select_fuzzy_srg_seeds(
            vesselness,
            candidate_map=candidate_map,
            fov_mask=fov_mask,
            params=params.srg_features,
        )

        seeds = polling_seeds | fuzzy_seeds

        return seeds, {
            "method": method,
            "polling_seeds": polling_seeds,
            "fuzzy_debug": fuzzy_debug,
            "n_seed_pixels": int(seeds.sum()),
        }

    if method in {
        "fuzzy_harris",
        "hybrid_fuzzy_harris",
        "selective_fuzzy_harris",
    }:
        seeds, debug = select_hybrid_fuzzy_harris_seeds(
            vesselness,
            vesselness=vesselness,
            candidate_map=candidate_map,
            fov_mask=fov_mask,
            srg_params=params.srg_features,
            harris_params=params.harris_seed,
            hybrid_params=params.hybrid_seed,
        )
        debug["method"] = method
        return seeds, debug

    raise ValueError(
        f"Unsupported seed_selection_method: "
        f"{params.seed_selection_method}"
    )


def select_automatic_seeds(
    vesselness: np.ndarray,
    fov_mask: Optional[np.ndarray] = None,
    *,
    params: APSRGParams,
    seed_threshold: float,
    candidate_map: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Compatibility wrapper returning only the selected seed mask."""
    seeds, _ = select_automatic_seeds_with_debug(
        vesselness,
        fov_mask=fov_mask,
        params=params,
        seed_threshold=seed_threshold,
        candidate_map=candidate_map,
    )
    return seeds


def _region_growing_from_seeds(
    candidate: np.ndarray,
    seeds: np.ndarray,
    intensity_image: Optional[np.ndarray] = None,
    *,
    connectivity: int = 8,
    max_intensity_difference: float = 18.0,
    max_iterations: int = 500_000,
) -> np.ndarray:
    """
    Grow vessel regions from seed pixels inside the candidate vessel map.

    A candidate neighbor is accepted when it is connected to an existing region
    and, when intensity_image is provided, its intensity is locally consistent
    with the current pixel. If max_intensity_difference <= 0, the intensity
    consistency test is disabled.
    """
    candidate_bool = np.asarray(candidate).astype(bool)
    seeds_bool = np.asarray(seeds).astype(bool) & candidate_bool

    h, w = candidate_bool.shape
    visited = np.zeros((h, w), dtype=bool)
    result = np.zeros((h, w), dtype=bool)

    if intensity_image is not None:
        intensity = np.asarray(intensity_image, dtype=np.float32)
        if intensity.shape != candidate_bool.shape:
            raise ValueError("intensity_image shape must match candidate shape")
    else:
        intensity = None

    queue: deque[tuple[int, int]] = deque()
    ys, xs = np.where(seeds_bool)

    for y, x in zip(ys, xs):
        visited[y, x] = True
        result[y, x] = True
        queue.append((int(y), int(x)))

    neighbors = get_neighbors(connectivity)
    iterations = 0
    max_iterations = int(max_iterations)
    max_diff = float(max_intensity_difference)

    while queue:
        y, x = queue.popleft()
        iterations += 1

        if max_iterations > 0 and iterations > max_iterations:
            break

        current_intensity = intensity[y, x] if intensity is not None else 0.0

        for dy, dx in neighbors:
            yy, xx = y + dy, x + dx

            if yy < 0 or yy >= h or xx < 0 or xx >= w:
                continue

            if visited[yy, xx] or not candidate_bool[yy, xx]:
                continue

            accept = True

            if intensity is not None and max_diff > 0:
                accept = abs(float(intensity[yy, xx]) - float(current_intensity)) <= max_diff

            if accept:
                visited[yy, xx] = True
                result[yy, xx] = True
                queue.append((yy, xx))
            else:
                visited[yy, xx] = True

    return result


def remove_small_components(mask: np.ndarray, min_area: int = 8, *, connectivity: int = 8) -> np.ndarray:
    """Remove connected components smaller than min_area."""
    mask_u8 = ensure_binary_mask(mask, return_uint8=False).astype(np.uint8)
    conn = 8 if int(connectivity) == 8 else 4

    n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask_u8, connectivity=conn)
    clean = np.zeros_like(mask_u8, dtype=np.uint8)

    for label in range(1, n_labels):
        area = int(stats[label, cv2.CC_STAT_AREA])

        if area >= int(min_area):
            clean[labels == label] = 1

    return clean.astype(bool)


def fill_small_holes(mask: np.ndarray, area_threshold: int = 8) -> np.ndarray:
    """Fill small holes inside binary vessel regions."""
    mask_bool = ensure_binary_mask(mask, return_uint8=False)
    area_threshold = int(area_threshold)

    if area_threshold <= 0:
        return mask_bool

    return remove_small_holes_compat(mask_bool, area_threshold=area_threshold)


def apsrg_postprocess(mask: np.ndarray, *, params: APSRGParams) -> np.ndarray:
    """Apply light post-processing for the APSRG baseline."""
    cleaned = remove_small_components(
        mask,
        min_area=params.min_component_area,
        connectivity=params.region_growing_connectivity,
    )

    cleaned = fill_small_holes(cleaned, area_threshold=params.fill_small_holes_area)

    return cleaned.astype(bool)


def apsrg_segment(
    preprocessed_gray: np.ndarray,
    fov_mask: np.ndarray | None = None,
    params: APSRGParams | None = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    """
    Segment retinal blood vessels using the APSRG-style baseline.

    Returns
    -------
    baseline_mask:
        Boolean vessel segmentation mask.
    debug_info:
        Dictionary containing vesselness image, seeds, candidate map,
        thresholds, and parameter values for reproducibility.
    """
    params = params or APSRGParams()
    gray = _prepare_gray(preprocessed_gray)
    fov = _prepare_fov_mask(fov_mask, gray.shape)

    vesselness = enhance_dark_vessels(
        gray,
        kernel_sizes=params.vesselness_kernel_sizes,
        method=params.vessel_enhancement_method,
    )

    valid_vesselness_pixels = _valid_pixels(vesselness, fov_mask=fov, ignore_zero=True)

    seed_thr, candidate_thr = compute_percentile_thresholds(
        vesselness,
        fov_mask=fov,
        seed_percentile=params.seed_percentile,
        candidate_percentile=params.candidate_percentile,
    )

    if valid_vesselness_pixels.size == 0:
        empty = np.zeros_like(gray, dtype=bool)

        return empty, {
            "vesselness": vesselness,
            "seeds": empty,
            "candidate": empty,
            "seed_thr": seed_thr,
            "candidate_thr": candidate_thr,
            "params": params.to_dict(),
            "notes": "no valid pixels available for APSRG segmentation",
        }

    candidate = create_candidate_map(vesselness, candidate_thr, fov_mask=fov)

    seeds, seed_selection_debug = (
        select_automatic_seeds_with_debug(
            vesselness,
            fov_mask=fov,
            params=params,
            seed_threshold=seed_thr,
            candidate_map=candidate,
        )
    )

    seeds &= candidate

    region_growing_mode = str(
        params.region_growing_mode
    ).lower()

    region_growing_debug: dict[str, Any] = {}

    if region_growing_mode == "bfs":
        grown = _region_growing_from_seeds(
            candidate,
            seeds,
            intensity_image=vesselness,
            connectivity=params.region_growing_connectivity,
            max_intensity_difference=params.max_intensity_difference,
            max_iterations=params.max_iterations,
        )

        region_growing_debug = {
            "mode": "bfs",
            "n_initial_seed_pixels": int(
                seeds.sum()
            ),
            "n_candidate_pixels": int(
                candidate.sum()
            ),
            "n_output_pixels": int(
                grown.sum()
            ),
        }

    elif region_growing_mode == "edge_delayed":
        grown, region_growing_debug = (
            edge_delayed_region_growing(
                candidate_map=candidate,
                seed_mask=seeds,
                intensity_image=vesselness,
                edge_image=vesselness,
                fov_mask=fov,
                params=(
                    params.edge_delayed_region_growing
                ),
                connectivity=(
                    params.region_growing_connectivity
                ),
                max_intensity_difference=(
                    params.max_intensity_difference
                ),
                max_iterations=(
                    params.max_iterations
                ),
            )
        )

    else:
        raise ValueError(
            "Unsupported region_growing_mode: "
            f"{params.region_growing_mode}"
        )

    if fov is not None:
        grown &= fov

    baseline_mask = apsrg_postprocess(grown, params=params)

    if fov is not None:
        baseline_mask &= fov

    debug_info: dict[str, Any] = {
        "vesselness": vesselness,
        "seeds": seeds,
        "candidate": candidate,
        "grown_before_postprocess": grown,
        "seed_thr": float(seed_thr),
        "candidate_thr": float(candidate_thr),
        "n_seed_pixels": int(seeds.sum()),
        "n_candidate_pixels": int(candidate.sum()),
        "n_output_pixels": int(baseline_mask.sum()),
        "seed_selection_debug": seed_selection_debug,
        "region_growing_debug": region_growing_debug,
        "params": params.to_dict(),
    }

    return baseline_mask.astype(bool), debug_info


class APSRGBaseline:
    """Small class wrapper for APSRG baseline segmentation."""

    def __init__(self, params: APSRGParams | None = None):
        self.params = params or APSRGParams()

    @classmethod
    def from_dict(cls, config: dict[str, Any] | None) -> "APSRGBaseline":
        """Create APSRGBaseline from a configuration dictionary."""
        return cls(params=APSRGParams.from_dict(config))

    def segment(
        self,
        preprocessed_gray: np.ndarray,
        fov_mask: Optional[np.ndarray] = None,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        """Segment one preprocessed grayscale image."""
        return apsrg_segment(preprocessed_gray, fov_mask=fov_mask, params=self.params)


def segment_apsrg(
    preprocessed_gray: np.ndarray,
    fov_mask: np.ndarray | None = None,
    params: APSRGParams | None = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Alias for apsrg_segment()."""
    return apsrg_segment(preprocessed_gray, fov_mask=fov_mask, params=params)


def run_apsrg_on_files(
    preprocessed_path: str | Path,
    output_mask_path: str | Path,
    fov_path: str | Path | None = None,
    *,
    params: APSRGParams | None = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Read a preprocessed image from disk, segment it, save the mask, and return results."""
    gray = read_gray_image(preprocessed_path)
    fov = read_binary_mask(fov_path) if fov_path else None

    mask, debug_info = apsrg_segment(gray, fov_mask=fov, params=params)
    save_binary_mask(output_mask_path, mask)

    return mask, debug_info
