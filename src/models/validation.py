"""Validation schemes: grouped CV by agent identity, temporal split.

Leakage checks raise ValueError (never bare assert, which python -O strips)."""
import numpy as np
from sklearn.model_selection import GroupKFold

def check_no_group_leak(groups, folds) -> None:
    groups = np.asarray(groups)
    for i, (train, test) in enumerate(folds):
        leaked = sorted(set(groups[train]) & set(groups[test]))
        if leaked:
            raise ValueError(f"fold {i}: groups in both train and test: {leaked[:5]}")

def grouped_folds(groups, n_splits: int = 5, seed: int = 0):
    groups = np.asarray(groups)
    kf = GroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    folds = [(train, test) for train, test in kf.split(np.zeros(len(groups)), groups=groups)]
    check_no_group_leak(groups, folds)
    return folds

def temporal_split(timestamps, test_fraction: float = 0.2):
    timestamps = np.asarray(timestamps)
    n_test = int(round(len(timestamps) * test_fraction))
    if n_test == 0 or n_test == len(timestamps):
        raise ValueError(f"test_fraction={test_fraction} leaves an empty train or test set")
    order = np.argsort(timestamps, kind="stable")
    train, test = order[:-n_test], order[-n_test:]
    if timestamps[train].max() >= timestamps[test].min():
        raise ValueError("temporal split is not strictly ordered (tied timestamps at the boundary)")
    return train, test
