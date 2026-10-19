import numpy as np
from src.models.baselines import class_prior_baseline, task_count_baseline, combined_baseline

def test_class_prior_maps_known_and_unseen_groups():
    tg = np.array(["a", "a", "a", "a", "b", "b"])
    y  = np.array([1, 1, 0, 0, 0, 0])
    p = class_prior_baseline(tg, y, np.array(["a", "b", "zz"]))
    assert p[0] == 0.5 and p[1] == 0.0 and p[2] == y.mean()

def test_task_count_baseline_is_probability():
    rng = np.random.default_rng(3)
    counts = rng.integers(1, 50, 120).astype(float)
    y = (counts < 10).astype(int)
    p = task_count_baseline(counts, y, counts)
    assert p.shape == (120,) and ((0 <= p) & (p <= 1)).all()
    assert p[counts.argmin()] > p[counts.argmax()]

def test_combined_baseline_runs_and_bounds():
    tg = np.array(["a"] * 30 + ["b"] * 30)
    counts = np.arange(60, dtype=float)
    y = np.array([1] * 20 + [0] * 40)
    p = combined_baseline(tg, counts, y, tg, counts)
    assert p.shape == (60,) and ((0 <= p) & (p <= 1)).all()
