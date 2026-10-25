import math

import pytest

from src.models.run_primary import clauses


def _res(base=0.65, lo=0.78, hi=0.89, skill=0.2, skill_lo=0.05, ratio=4.0, deciles=None):
    deciles = deciles or [0.1 * (i + 1) for i in range(10)]
    return {"auc": {"baseline": {"auc": base}, "gbm": {"auc": (lo + hi) / 2, "ci_low": lo, "ci_high": hi}},
            "brier_skill_gbm": {"skill": skill, "ci_low": skill_lo},
            "quartile_gbm": {"ratio": ratio}, "decile_lift_gbm": [{"failure_rate": d} for d in deciles]}


@pytest.mark.parametrize("res, key, want", [
    (_res(), "clause1_auc", True),
    (_res(base=0.70, lo=0.75), "clause1_auc", True),       # margin exactly 0.05 counts ("at least")
    (_res(base=0.70, lo=0.749), "clause1_auc", False),
    (_res(skill_lo=0.0), "clause2_brier", False),
    (_res(ratio=1.99), "clause3_quartile_and_monotone", False),
    (_res(base=0.80, lo=0.78, hi=0.89), "h1_refuted_by_preregistered_rule", True),   # interval contains baseline
    (_res(base=0.95, lo=0.78, hi=0.89), "h1_refuted_by_preregistered_rule", True),   # interval below baseline
    (_res(skill=0.0), "h1_refuted_by_preregistered_rule", True),
    (_res(), "h1_refuted_by_preregistered_rule", False),
])
def test_clause_rules_match_the_preregistration(res, key, want):
    assert clauses(res)[key] is want


def test_flat_deciles_fail_clause3_with_a_finite_spearman():
    c = clauses(_res(deciles=[0.5] * 10))
    assert c["clause3_quartile_and_monotone"] is False and math.isfinite(c["decile_spearman"])
