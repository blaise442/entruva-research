import numpy as np
import pytest
from src.models.validation import grouped_folds, check_no_group_leak, temporal_split

GROUPS = np.array([f"agent_{i % 23}" for i in range(200)])

def test_grouped_folds_are_group_disjoint():
    folds = grouped_folds(GROUPS, n_splits=5, seed=0)
    assert len(folds) == 5
    for train, test in folds:
        assert set(GROUPS[train]) & set(GROUPS[test]) == set()

def test_grouped_folds_seed_changes_folds_and_is_deterministic():
    f0 = grouped_folds(GROUPS, n_splits=5, seed=0)
    f0b = grouped_folds(GROUPS, n_splits=5, seed=0)
    f1 = grouped_folds(GROUPS, n_splits=5, seed=1)
    assert all(np.array_equal(a[1], b[1]) for a, b in zip(f0, f0b))
    assert any(not np.array_equal(a[1], b[1]) for a, b in zip(f0, f1))

def test_leak_check_raises_on_rigged_fold_even_under_O():
    rigged = [(np.arange(0, 150), np.arange(100, 200))]
    with pytest.raises(ValueError, match="agent_"):
        check_no_group_leak(GROUPS, rigged)

def test_temporal_split_orders_strictly():
    ts = np.arange(100)
    train, test = temporal_split(ts, test_fraction=0.2)
    assert len(test) == 20
    assert ts[train].max() < ts[test].min()

def test_temporal_split_rejects_empty_test():
    with pytest.raises(ValueError, match="empty"):
        temporal_split(np.arange(3), test_fraction=0.01)
