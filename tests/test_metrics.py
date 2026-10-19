import numpy as np
import pytest
from src.models.metrics import (
    auc_with_ci, auc_delta_with_ci, brier_skill, reliability_bins, decile_lift,
    quartile_failure_ratio,
)

rng = np.random.default_rng(0)
Y = rng.integers(0, 2, 400)
P_GOOD = np.clip(Y * 0.3 + rng.uniform(0, 0.7, 400), 0, 1)  # informative but overlapping
P_FLAT = np.full(400, Y.mean())
GROUPS = np.array([f"agent_{i % 40}" for i in range(400)])

def test_auc_perfect_and_ci_bounds():
    y = np.array([0, 0, 0, 1, 1, 1])
    p = np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9])
    r = auc_with_ci(y, p, n_boot=200, seed=1)
    assert r["auc"] == 1.0
    assert r["ci_low"] <= r["auc"] <= r["ci_high"]

def test_auc_rejects_single_class():
    with pytest.raises(ValueError, match="one class"):
        auc_with_ci(np.zeros(10), np.linspace(0, 1, 10))

def test_auc_stratified_never_discards_on_rare_positives():
    # 1 positive in 30 rows: an iid bootstrap discards ~36% of resamples; the
    # class-stratified row bootstrap preserves class counts so none are lost.
    y = np.zeros(30); y[7] = 1
    p = np.linspace(0, 1, 30)
    r = auc_with_ci(y, p, n_boot=300, seed=4)
    assert r["n_boot_used"] == 300

def test_auc_cluster_bootstrap_resamples_groups():
    a = auc_with_ci(Y, P_GOOD, n_boot=150, seed=7, groups=GROUPS)
    b = auc_with_ci(Y, P_GOOD, n_boot=150, seed=7, groups=GROUPS)
    c = auc_with_ci(Y, P_GOOD, n_boot=150, seed=8, groups=GROUPS)
    assert a == b
    assert a["ci_low"] <= a["auc"] <= a["ci_high"]
    assert (a["ci_low"], a["ci_high"]) != (c["ci_low"], c["ci_high"])

def test_auc_cluster_bootstrap_redraws_lost_class():
    groups = np.array(["pos"] * 10 + ["neg"] * 10)   # half of 2-group resamples lose a class
    y = np.array([1] * 10 + [0] * 10)
    p = np.linspace(0, 1, 20)
    r = auc_with_ci(y, p, n_boot=100, seed=0, groups=groups)
    assert r["n_boot_used"] == 100

def test_auc_delta_paired():
    r = auc_delta_with_ci(Y, P_GOOD, P_FLAT, n_boot=200, seed=3)
    assert r["delta"] > 0
    assert r["ci_low"] <= r["delta"] <= r["ci_high"]
    assert r == auc_delta_with_ci(Y, P_GOOD, P_FLAT, n_boot=200, seed=3)

def test_brier_skill_positive_for_better_model():
    r = brier_skill(Y, P_GOOD, P_FLAT, n_boot=200, seed=2)
    assert r["skill"] > 0
    assert r["ci_low"] <= r["skill"] <= r["ci_high"]

def test_brier_skill_names_perfect_baseline():
    y = np.array([0, 1, 0, 1])
    perfect = y.astype(float)
    with pytest.raises(ValueError, match="baseline Brier score is 0"):
        brier_skill(y, np.full(4, 0.5), perfect, n_boot=50, seed=0)

def test_reliability_bins_shape_and_counts():
    bins = reliability_bins(Y, P_GOOD, n_bins=10)
    assert sum(b["n"] for b in bins) == len(Y)
    for b in bins:
        assert 0.0 <= b["p_mean"] <= 1.0 and 0.0 <= b["y_rate"] <= 1.0

def test_decile_lift_rows_and_small_n_raises():
    rows = decile_lift(Y, P_GOOD, seed=0)
    assert [r["decile"] for r in rows] == list(range(1, 11))
    overall = Y.mean()
    assert rows[-1]["lift"] == pytest.approx(rows[-1]["failure_rate"] / overall)
    with pytest.raises(ValueError, match="at least 10"):
        decile_lift(np.array([0, 1, 0]), np.array([0.1, 0.9, 0.2]), seed=0)

def test_quartile_ratio_reports_counts_and_inf():
    y = np.array([0] * 50 + [1] * 50)
    p = np.concatenate([np.linspace(0, 0.4, 50), np.linspace(0.6, 1.0, 50)])
    r = quartile_failure_ratio(y, p, seed=0)
    assert r["ratio"] == float("inf")
    assert r["bottom_failures"] == 0.0 and r["top_failures"] == 25.0
    assert r["top_n"] == 25 and r["bottom_n"] == 25

def test_quartile_ratio_ties_do_not_depend_on_row_order():
    # identical predictions: failure placement in the array must not decide the ratio
    y_first = np.array([1] * 50 + [0] * 50)
    y_last = np.array([0] * 50 + [1] * 50)
    p = np.full(100, 0.5)
    for y in (y_first, y_last):
        r = quartile_failure_ratio(y, p, seed=0)
        assert 0.4 < r["ratio"] < 2.0
