import numpy as np
import pandas as pd
import pytest

from src.adversarial.attacks import ATTACKS, call_shaping, error_suppression, message_shaping, retry_diversification
from src.models.fit import MODEL_INPUTS

_DEFAULTS = {"model_id": "m", "task_type": "t", "exit_status": "", "task_length_steps": 10.0, "n_tool_calls": 10.0,
             "n_distinct_tools": 3.0, "repeat_call_ratio": 0.0, "n_errors": 0.0, "error_rate": 0.0, "max_error_run": 0.0,
             "mean_text_len": 100.0, "duration_s": 5.0, "api_calls": 10.0, "tokens_sent": 1000.0}
assert set(_DEFAULTS) == set(MODEL_INPUTS)


def _row(**over):
    return pd.DataFrame([{**_DEFAULTS, **over, "agent_id": "a", "source": "s"}])


def _apply(spec, row):
    s = spec["strengths"][0]
    return spec["fn"](row) if s is None else spec["fn"](row, s)


def test_error_suppression_zeroes_errors_and_adds_silent_retries():
    row = _row(n_tool_calls=10.0, repeat_call_ratio=0.1, n_errors=2.0, error_rate=0.2, max_error_run=2.0, task_length_steps=12.0,
               api_calls=10.0, tokens_sent=1000.0)
    out = error_suppression(row)
    assert (out[["n_errors", "error_rate", "max_error_run"]] == 0).all().all()
    assert out.n_tool_calls.iloc[0] == 12 and out.task_length_steps.iloc[0] == 14
    assert out.repeat_call_ratio.iloc[0] == pytest.approx(3 / 12)
    assert out.api_calls.iloc[0] == 12 and out.tokens_sent.iloc[0] == pytest.approx(1200.0)
    assert out.duration_s.iloc[0] == 5.0 and out.exit_status.iloc[0] == ""
    assert row.n_errors.iloc[0] == 2.0  # pure: input untouched


def test_retry_diversification_moves_only_repeat_ratio():
    row = _row(repeat_call_ratio=0.4)
    out = retry_diversification(row)
    assert out.repeat_call_ratio.iloc[0] == 0
    assert out.drop(columns="repeat_call_ratio").equals(row.drop(columns="repeat_call_ratio"))


def test_call_shaping_couples_count_length_and_rates():
    row = _row(n_tool_calls=10.0, n_distinct_tools=3.0, repeat_call_ratio=0.2, n_errors=1.0, error_rate=0.1,
               mean_text_len=100.0, task_length_steps=10.0, api_calls=10.0, tokens_sent=1000.0)
    out = call_shaping(row, k=10, pad_chars=50)
    assert out.n_tool_calls.iloc[0] == 20 and out.n_distinct_tools.iloc[0] == 4 and out.task_length_steps.iloc[0] == 20
    assert out.error_rate.iloc[0] == pytest.approx(0.05) and out.repeat_call_ratio.iloc[0] == pytest.approx(0.1)
    assert out.mean_text_len.iloc[0] == pytest.approx(75.0)
    assert out.api_calls.iloc[0] == 20 and out.tokens_sent.iloc[0] == pytest.approx(1000.0 + 10 * 50 / 4.0)
    assert call_shaping(row, k=0).equals(row)


def test_message_shaping_scales_length_and_tokens_only():
    row = _row(mean_text_len=200.0, tokens_sent=1000.0)
    out = message_shaping(row, 0.5)
    assert out.mean_text_len.iloc[0] == 100.0 and out.tokens_sent.iloc[0] == 500.0
    assert out.drop(columns=["mean_text_len", "tokens_sent"]).equals(row.drop(columns=["mean_text_len", "tokens_sent"]))


def test_attacks_keep_missing_columns_missing():
    row = _row(tokens_sent=np.nan, api_calls=np.nan, duration_s=np.nan, n_errors=2.0, error_rate=0.2)
    for spec in ATTACKS.values():
        out = _apply(spec, row)
        assert out[["tokens_sent", "api_calls", "duration_s"]].isna().all().all(), spec


def test_per_run_chars_is_zero_for_free_attacks_and_positive_for_padding():
    row = _row(n_tool_calls=10.0, mean_text_len=100.0, task_length_steps=10.0, n_errors=1.0, error_rate=0.1)
    assert ATTACKS["error_suppression"]["per_run_chars"](row, error_suppression(row)).iloc[0] == 0
    assert ATTACKS["retry_diversification"]["per_run_chars"](row, retry_diversification(row)).iloc[0] == 0
    assert ATTACKS["call_shaping"]["per_run_chars"](row, call_shaping(row, 4, 50)).iloc[0] == 200
    assert ATTACKS["message_shaping"]["per_run_chars"](row, message_shaping(row, 0.5)).iloc[0] == 0
    assert ATTACKS["message_shaping"]["per_run_chars"](row, message_shaping(row, 2.0)).iloc[0] == pytest.approx(100.0 * 10)


def test_attack_registry_shape():
    assert set(ATTACKS) == {"error_suppression", "retry_diversification", "call_shaping", "message_shaping"}
    for spec in ATTACKS.values():
        assert {"fn", "strengths", "trace_change", "per_run_chars"} <= set(spec) and spec["trace_change"]


def test_call_shaping_weights_text_length_by_tool_calls_not_steps():
    # extractor: mean_text_len is the mean over tool-call steps (n = n_tool_calls), not task_length_steps
    row = _row(n_tool_calls=10.0, task_length_steps=30.0, mean_text_len=100.0)
    out = call_shaping(row, k=10, pad_chars=50)
    assert out.mean_text_len.iloc[0] == pytest.approx(75.0)
    assert ATTACKS["call_shaping"]["per_run_chars"](row, out).iloc[0] == pytest.approx(500.0)
    assert ATTACKS["message_shaping"]["per_run_chars"](row, message_shaping(row, 2.0)).iloc[0] == pytest.approx(1000.0)


def test_call_shaping_negative_k_drops_repeated_calls():
    row = _row(n_tool_calls=10.0, repeat_call_ratio=0.3, task_length_steps=30.0, n_errors=1.0, error_rate=0.1,
               api_calls=10.0, tokens_sent=1000.0, mean_text_len=100.0, n_distinct_tools=3.0)
    out = call_shaping(row, k=-2)
    assert out.n_tool_calls.iloc[0] == 8 and out.task_length_steps.iloc[0] == 28
    assert out.repeat_call_ratio.iloc[0] == pytest.approx(1 / 8) and out.error_rate.iloc[0] == pytest.approx(1 / 8)
    assert out.api_calls.iloc[0] == 8 and out.tokens_sent.iloc[0] == pytest.approx(800.0)
    assert out.mean_text_len.iloc[0] == 100.0 and out.n_distinct_tools.iloc[0] == 3 and out.n_errors.iloc[0] == 1
    capped = call_shaping(row, k=-5)  # only the 3 repeats are redundant
    assert capped.n_tool_calls.iloc[0] == 7 and capped.repeat_call_ratio.iloc[0] == 0 and capped.tokens_sent.iloc[0] == pytest.approx(700.0)
    assert ATTACKS["call_shaping"]["per_run_chars"](row, capped).iloc[0] == 0
    assert ATTACKS["call_shaping"]["strengths"] == [-32, -16, -8, -4, -2, -1, 1, 2, 4, 8, 16, 32]
