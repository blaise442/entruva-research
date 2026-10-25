import math

import numpy as np

from src.models.glm import poisson_relativities
from tests.test_fit import _frame


def test_relativities_recover_direction_with_cluster_ci():
    df = _frame(3000, 7, 1.5)  # failure rises with n_errors by construction
    rel = poisson_relativities(df, n_boot=40)
    err = rel["n_errors"]
    assert err["relativity"] > 1.0 and err["ci_low"] > 1.0
    assert all(math.isfinite(v["relativity"]) for v in rel.values())
    assert "outcome" not in rel and "model_id" not in rel


def test_bootstrap_survives_feature_present_in_only_some_agents():
    df = _frame(600, 7, 1.5)
    df["duration_s"] = np.where(df.agent_id == "m0::s0", 1.0, np.nan)  # resamples without m0 see all-NaN
    rel = poisson_relativities(df, n_boot=30)
    assert "duration_s" in rel and all(math.isfinite(v["ci_low"]) for v in rel.values())
