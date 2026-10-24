"""Grouped 5-fold CV by agent identity with pooled out-of-fold predictions
(robustness check; the frozen split in fit.py is the primary evaluation)."""
import numpy as np

from src.models.fit import SEED, fit_predict
from src.models.validation import check_no_group_leak, grouped_folds


def cv_oof(df, n_splits: int = 5, seed: int = SEED):
    df = df.reset_index(drop=True)
    folds = grouped_folds(df["agent_id"].to_numpy(), n_splits=n_splits, seed=seed)
    check_no_group_leak(df["agent_id"].to_numpy(), folds)
    oof = {k: np.full(len(df), np.nan) for k in ("baseline", "gbm", "logit")}
    for train_idx, test_idx in folds:
        preds = fit_predict(df.iloc[train_idx], df.iloc[test_idx])
        for k, v in preds.items():
            oof[k][test_idx] = v
    return oof, folds
