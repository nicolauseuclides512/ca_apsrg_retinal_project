import numpy as np
import pytest

from src.segmentation.edge_delayed_region_growing import EdgeDelayedRegionGrowingParams, edge_delayed_region_growing


@pytest.mark.parametrize("mode", ["region_mean", "local_path", "local_or_region", "local_and_region"])
def test_edge_delayed_acceptance_modes(mode):
    candidate = np.ones((7, 7), dtype=bool)
    seeds = np.zeros_like(candidate)
    seeds[3, 3] = True
    intensity = np.full((7, 7), 100, dtype=np.uint8)
    params = EdgeDelayedRegionGrowingParams(acceptance_mode=mode, record_growth_order=False)
    mask, debug = edge_delayed_region_growing(candidate, seeds, intensity, params=params)
    assert mask.dtype == np.bool_
    assert mask.shape == candidate.shape
    assert mask[3, 3]
    assert debug["params"]["acceptance_mode"] == mode
