import numpy as np
import pandas as pd

from src.models.fit import MODEL_INPUTS, evaluate_split


def _frame(n, seed, signal):
    rng = np.random.default_rng(seed)
    agents = [f"m{i % 6}::s{i % 2}" for i in range(n)]
    err = rng.poisson(1.0, n)
    y = (rng.random(n) < 1 / (1 + np.exp(-(signal * (err - 1))))).astype(int)
    return pd.DataFrame(dict(
        agent_id=agents, model_id=[a.split("::")[0] for a in agents], task_type="t",
        task_length_steps=rng.integers(1, 30, n), outcome=y, n_errors=err,
        n_tool_calls=rng.integers(1, 30, n), n_distinct_tools=2, repeat_call_ratio=0.0,
        error_rate=err / 10, max_error_run=err, mean_text_len=50.0,
        duration_s=np.nan, exit_status="", api_calls=np.nan, tokens_sent=np.nan))


def test_telemetry_beats_baseline_when_signal_exists_and_never_uses_outcome():
    assert "outcome" not in MODEL_INPUTS and "agent_id" not in MODEL_INPUTS
    tr, te = _frame(4000, 1, 1.5), _frame(2000, 2, 1.5)
    te["agent_id"] = [a.replace("m", "x") for a in te.agent_id]  # unseen agents
    r = evaluate_split(tr, te, n_boot=50)
    assert r["auc"]["gbm"]["auc"] > r["auc"]["baseline"]["auc"] + 0.05
    assert r["brier_skill_gbm"]["skill"] > 0


def test_no_signal_gives_no_meaningful_gain():
    tr, te = _frame(4000, 3, 0.0), _frame(2000, 4, 0.0)
    te["agent_id"] = [a.replace("m", "x") for a in te.agent_id]
    r = evaluate_split(tr, te, n_boot=50)
    assert abs(r["auc_delta_gbm"]["delta"]) < 0.05
