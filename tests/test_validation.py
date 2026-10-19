import numpy as np
import pytest
from src.models.validation import grouped_folds, assert_no_group_leak, temporal_split

GROUPS = np.array([f"agent_{i % 23}" for i in range(200)])

def test_grouped_folds_are_group_disjoint():
    folds = grouped_folds(GROUPS, n_splits=5, seed=0)
    assert len(folds) == 5
    for train, test in folds:
        assert set(GROUPS[train]) & set(GROUPS[test]) == set()

def test_leak_assertion_fires_on_rigged_fold():
    rigged = [(np.arange(0, 150), np.arange(100, 200))]
    with pytest.raises(AssertionError, match="agent_"):
        assert_no_group_leak(GROUPS, rigged)

def test_temporal_split_orders_strictly():
    ts = np.arange(100)
    train, test = temporal_split(ts, test_fraction=0.2)
    assert len(test) == 20
    assert ts[train].max() < ts[test].min()
