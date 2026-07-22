from src.pipeline.run_pipeline import load_pipeline_config


def test_main_r04_configuration():
    config = load_pipeline_config("configs/main_methods/ca_apsrg_r04.yaml")
    assert config.apsrg.hybrid_seed.target_seed_count == 77
    assert config.apsrg.hybrid_seed.seed_dilate_radius == 1
    assert config.apsrg.edge_delayed_region_growing.priority_mode == "kang_product"
    assert config.apsrg.edge_delayed_region_growing.acceptance_mode == "local_or_region"
