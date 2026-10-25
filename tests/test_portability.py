import numpy as np
import pandas as pd

from src.models.portability import cross_domain_scores
from tests.test_fit import _frame


def _multi(seed, signal):
    parts = []
    for i, src in enumerate(("a", "b", "c")):
        f = _frame(900, seed + i, signal)
        f["source"] = src
        f["agent_id"] = f.agent_id + f"::{src}"
        f["model_id"] = f.model_id + src
        parts.append(f)
    return pd.concat(parts, ignore_index=True)


def test_cross_domain_model_never_sees_target_source_and_is_paired_with_in_domain_baseline():
    df = _multi(10, 1.5)
    test_agents = sorted(set(df.agent_id))[::4]
    out = cross_domain_scores(df, test_agents)
    assert set(out) == {"a", "b", "c"}
    for src, r in out.items():
        assert r["train_sources"] == sorted({"a", "b", "c"} - {src})
        assert len(r["y"]) == len(r["p_cross"]) == len(r["p_baseline"]) > 0
        assert not np.isnan(r["p_cross"]).any()


def test_portability_report_applies_prereg_rule_per_source():
    from src.models.portability import portability_report
    df = _multi(20, 1.5)
    test_agents = sorted(set(df.agent_id))[::4]
    rep = portability_report(df, test_agents, n_boot=40)
    assert set(rep) == {"a", "b", "c"}
    for r in rep.values():
        assert r["n"] > 0 and r["train_sources"]
        assert r["s2_supported"] == (not r["ci_degenerate"] and r["auc_delta"]["ci_low"] >= 0.05)
        assert r["auc_cross"]["auc"] > r["auc_baseline"]["auc"]


def test_one_held_out_agent_cannot_support_s2():
    from src.models.portability import portability_report
    df = _multi(30, 1.5)
    agents = sorted(set(df.agent_id))
    test_agents = [a for a in agents if a.endswith("::a")][:2] + [a for a in agents if a.endswith("::b")][:1] \
        + [a for a in agents if a.endswith("::c")][:2]
    rep = portability_report(df, test_agents, n_boot=20)
    assert rep["b"]["n_agents"] == 1 and rep["b"]["ci_degenerate"] is True and rep["b"]["s2_supported"] is False
    assert rep["a"]["ci_degenerate"] is False
