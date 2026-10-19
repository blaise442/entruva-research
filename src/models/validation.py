"""Validation schemes: grouped CV by agent identity, temporal split. Leakage checks are explicit."""
import numpy as np
from sklearn.model_selection import GroupKFold

def assert_no_group_leak(groups, folds) -> None:
    groups = np.asarray(groups)
    for i, (train, test) in enumerate(folds):
        leaked = sorted(set(groups[train]) & set(groups[test]))
        assert not leaked, f"fold {i}: groups in both train and test: {leaked[:5]}"

def grouped_folds(groups, n_splits: int = 5, seed: int = 0):
    groups = np.asarray(groups)
    # GroupKFold does not shuffle; permute group labels with the seed so fold membership
    # is deterministic per seed, not an artifact of label order.
    uniq = np.unique(groups)
    perm = {g: i for g, i in zip(uniq, np.random.default_rng(seed).permutation(len(uniq)))}
    shuffled = np.array([perm[g] for g in groups])
    folds = [
        (train, test)
        for train, test in GroupKFold(n_splits=n_splits).split(np.zeros(len(groups)), groups=shuffled)
    ]
    assert_no_group_leak(groups, folds)
    return folds

def temporal_split(timestamps, test_fraction: float = 0.2):
    timestamps = np.asarray(timestamps)
    order = np.argsort(timestamps, kind="stable")
    n_test = int(round(len(timestamps) * test_fraction))
    train, test = order[:-n_test], order[-n_test:]
    assert timestamps[train].max() < timestamps[test].min(), "temporal split is not strictly ordered"
    return train, test
