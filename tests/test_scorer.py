import numpy as np
import pandas as pd
import pytest

from src.adversarial.scorer import agent_deciles, decile_edges, frozen_scorer
from src.models.fit import MODEL_INPUTS, fit_predict, model_columns


def _frame(n, seed, agents):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "agent_id": rng.choice(agents, n), "model_id": rng.choice(["m1", "m2"], n),
        "task_type": rng.choice(["t1", "t2"], n), "exit_status": [""] * n,
        "task_length_steps": rng.integers(1, 30, n).astype(float),
        "n_tool_calls": rng.integers(0, 20, n).astype(float), "n_distinct_tools": rng.integers(0, 5, n).astype(float),
        "repeat_call_ratio": rng.random(n), "n_errors": rng.integers(0, 4, n).astype(float),
        "error_rate": rng.random(n), "max_error_run": rng.integers(0, 3, n).astype(float),
        "mean_text_len": rng.random(n) * 500, "duration_s": np.nan, "api_calls": np.nan, "tokens_sent": np.nan,
    })
    df["outcome"] = (df["error_rate"] + rng.normal(0, 0.3, n) > 0.6).astype(int)
    return df


@pytest.fixture
def small_frozen():
    return _frame(120, 1, ["a", "b", "c", "d"]), _frame(60, 2, ["e", "f"])


def test_model_columns_matches_fit_predict_choice(small_frozen):
    train, _ = small_frozen
    cols = model_columns(train)
    assert cols[:3] == ["model_id", "task_type", "exit_status"]
    assert "duration_s" not in cols
    assert set(cols) <= set(MODEL_INPUTS)


def test_frozen_scorer_reproduces_fit_predict_gbm(small_frozen):
    train, test = small_frozen
    p = frozen_scorer(train)(test)
    assert np.allclose(p, fit_predict(train, test)["gbm"])


def test_agent_deciles_marks_decile_one_unmovable():
    edges = decile_edges(np.linspace(0, 1, 100))
    d = agent_deciles(np.array([0.01, 0.01, 0.95]), np.array(["a", "a", "b"]), edges).set_index("agent_id")
    assert d.loc["a", "decile"] == 1 and not d.loc["a", "movable"]
    assert d.loc["b", "decile"] == 10 and d.loc["b", "movable"]
    assert d.loc["a", "p_mean"] == pytest.approx(0.01)
