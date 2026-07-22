import numpy as np

from src.segmentation.hybrid_seed_selection import HybridSeedParams, select_hybrid_fuzzy_harris_seeds


def test_hybrid_seed_map_and_fallback_debug_are_consistent():
    image = np.indices((48, 48)).sum(axis=0).astype(np.uint8)
    candidate = np.ones_like(image, dtype=bool)
    params = HybridSeedParams(target_seed_count=4, min_seed_count=1, max_seed_count=4, min_seed_distance=1)
    seeds, debug = select_hybrid_fuzzy_harris_seeds(image, candidate_map=candidate, hybrid_params=params)
    assert seeds.dtype == np.bool_
    assert set(np.unique(seeds)).issubset({False, True})
    assert debug["requested_target_seed_count"] == 4
    assert isinstance(debug["fallback_stage"], str)
    assert debug["target_seed_count_reached"] == (len(debug["selected_coordinates"]) >= 4)
