import numpy as np
import pytest
from src.models.metrics import (
    auc_with_ci, brier_skill, reliability_bins, decile_lift, quartile_failure_ratio,
)

rng = np.random.default_rng(0)
Y = rng.integers(0, 2, 400)
P_GOOD = np.clip(Y * 0.6 + rng.uniform(0, 0.4, 400), 0, 1)
P_FLAT = np.full(400, Y.mean())

def test_auc_perfect_and_ci_bounds():
    y = np.array([0, 0, 0, 1, 1, 1])
    p = np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9])
    r = auc_with_ci(y, p, n_boot=200, seed=1)
    assert r["auc"] == 1.0
    assert r["ci_low"] <= r["auc"] <= r["ci_high"]

def test_auc_rejects_single_class():
    with pytest.raises(ValueError, match="one class"):
        auc_with_ci(np.zeros(10), np.linspace(0, 1, 10))

def test_auc_is_seed_deterministic():
    a = auc_with_ci(Y, P_GOOD, n_boot=100, seed=7)
    b = auc_with_ci(Y, P_GOOD, n_boot=100, seed=7)
    assert a == b

def test_brier_skill_positive_for_better_model():
    r = brier_skill(Y, P_GOOD, P_FLAT, n_boot=200, seed=2)
    assert r["skill"] > 0
    assert r["ci_low"] <= r["skill"] <= r["ci_high"]

def test_reliability_bins_shape_and_counts():
    bins = reliability_bins(Y, P_GOOD, n_bins=10)
    assert sum(b["n"] for b in bins) == len(Y)
    for b in bins:
        assert 0.0 <= b["p_mean"] <= 1.0 and 0.0 <= b["y_rate"] <= 1.0

def test_decile_lift_has_ten_rows_summing_to_population():
    rows = decile_lift(Y, P_GOOD)
    assert [r["decile"] for r in rows] == list(range(1, 11))
    overall = Y.mean()
    top = rows[-1]
    assert top["lift"] == pytest.approx(top["failure_rate"] / overall)

def test_quartile_ratio_ordering_and_inf():
    y = np.array([0]*50 + [1]*50)
    p = np.concatenate([np.linspace(0, 0.4, 50), np.linspace(0.6, 1.0, 50)])
    assert quartile_failure_ratio(y, p) == float("inf")
    assert quartile_failure_ratio(Y, P_GOOD) > 1.0
