import numpy as np

from src.segmentation.apsrg_harris import HarrisSeedParams, select_harris_seeds


def test_harris_seeds_respect_fov_and_limit():
    image = np.zeros((32, 32), dtype=np.uint8)
    image[8:24, 8:24] = 255
    fov = np.zeros_like(image, dtype=bool)
    fov[4:28, 4:28] = True
    params = HarrisSeedParams(target_seed_count=5, min_seed_count=1, max_seed_count=5)
    seeds, debug = select_harris_seeds(image, fov_mask=fov, params=params)
    assert seeds.dtype == np.bool_
    assert not np.any(seeds & ~fov)
    assert debug["selected_seed_count"] <= 5
