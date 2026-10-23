from src.models.power import DELTA_GRID, min_detectable_auc_delta

def test_output_keys_and_echoed_inputs():
    r = min_detectable_auc_delta(400, 0.4, 8, n_sims=8, seed=1, n_boot=30)
    assert r["n_rows"] == 400 and r["failure_rate"] == 0.4 and r["n_agents"] == 8
    assert r["n_sims"] == 8 and r["seed"] == 1
    assert "power_at_0.05" in r and 0.0 <= r["power_at_0.05"] <= 1.0
    assert set(r["power_by_delta"]) == set(DELTA_GRID)
    assert r["min_detectable_delta"] is None or r["min_detectable_delta"] in DELTA_GRID

def test_deterministic_under_seed():
    a = min_detectable_auc_delta(200, 0.5, 6, n_sims=5, seed=7, n_boot=30)
    b = min_detectable_auc_delta(200, 0.5, 6, n_sims=5, seed=7, n_boot=30)
    assert a == b

def test_more_rows_means_detectable_delta_no_larger():
    worse_than_any = 1.0
    small = min_detectable_auc_delta(150, 0.5, 6, n_sims=10, seed=3, n_boot=30)
    big = min_detectable_auc_delta(1200, 0.5, 6, n_sims=10, seed=3, n_boot=30)
    s = small["min_detectable_delta"] or worse_than_any
    b = big["min_detectable_delta"] or worse_than_any
    assert b <= s
