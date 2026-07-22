import numpy as np

from src.segmentation.srg_features import extract_srg_feature_maps


def test_srg_feature_maps_are_finite_and_bounded():
    image = np.tile(np.arange(32, dtype=np.uint8), (32, 1))
    maps = extract_srg_feature_maps(image)
    for value in maps.values():
        if isinstance(value, np.ndarray):
            assert value.shape == image.shape
            assert np.isfinite(value).all()
            assert float(value.min()) >= 0.0
            assert float(value.max()) <= 1.0
