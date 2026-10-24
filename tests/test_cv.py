import numpy as np

from src.models.cv import cv_oof
from tests.test_fit import _frame


def test_oof_covers_every_row_once_with_no_agent_leak():
    df = _frame(1500, 5, 1.0)
    oof, folds = cv_oof(df, n_splits=3)
    assert set(oof) == {"baseline", "gbm", "logit"}
    assert all(len(v) == len(df) and not np.isnan(v).any() for v in oof.values())
    seen = np.concatenate([te for _, te in folds])
    assert sorted(seen) == list(range(len(df)))
