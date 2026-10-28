"""Feature-level telemetry attacks (design Part A, DEVIATIONS 2026-10-27).

Each attack states the trace change an operator would make and moves every
feature the extractor would move for it. All functions return a copy. Missing
telemetry (NaN) stays missing: an attack never invents a value the extractor
never had."""
import numpy as np
import pandas as pd


def _zeros(before: pd.DataFrame, after: pd.DataFrame) -> pd.Series:
    return pd.Series(0.0, index=before.index)


def _added_chars(before: pd.DataFrame, after: pd.DataFrame) -> pd.Series:
    total = lambda df: df["mean_text_len"] * df["task_length_steps"]
    return (total(after) - total(before)).clip(lower=0).fillna(0.0)


def error_suppression(rows: pd.DataFrame) -> pd.DataFrame:
    """Catch and swallow every error inside the agent and retry it silently with the
    same call: errors vanish, the retries show up as identical extra calls."""
    out = rows.copy()
    e = out["n_errors"].fillna(0.0)
    old = out["n_tool_calls"]
    repeats = out["repeat_call_ratio"] * old
    new = old + e
    out["n_errors"], out["error_rate"], out["max_error_run"] = 0.0, 0.0, 0.0
    out["n_tool_calls"] = new
    out["task_length_steps"] = out["task_length_steps"] + e
    out["repeat_call_ratio"] = np.where(new > 0, (repeats + e) / new.replace(0, np.nan), 0.0)
    out["api_calls"] = out["api_calls"] + e
    out["tokens_sent"] = out["tokens_sent"] * np.where(old > 0, new / old.replace(0, np.nan), 1.0)
    return out


def retry_diversification(rows: pd.DataFrame) -> pd.DataFrame:
    """Vary the arguments on every retry so no two calls are identical."""
    out = rows.copy()
    out["repeat_call_ratio"] = 0.0
    return out


def call_shaping(rows: pd.DataFrame, k: int, pad_chars: int = 50, chars_per_token: float = 4.0) -> pd.DataFrame:
    """Add k cheap successful calls to one extra tool, each with distinct arguments
    and a short message of pad_chars characters."""
    out = rows.copy()
    if k <= 0:
        return out
    old = out["n_tool_calls"]
    steps = out["task_length_steps"]
    new = old + k
    out["n_tool_calls"] = new
    out["task_length_steps"] = steps + k
    out["n_distinct_tools"] = out["n_distinct_tools"] + 1
    out["error_rate"] = out["n_errors"] / new
    out["repeat_call_ratio"] = out["repeat_call_ratio"] * old / new
    out["mean_text_len"] = (out["mean_text_len"] * steps + k * pad_chars) / (steps + k)
    out["api_calls"] = out["api_calls"] + k
    out["tokens_sent"] = out["tokens_sent"] + k * pad_chars / chars_per_token
    return out


def message_shaping(rows: pd.DataFrame, factor: float) -> pd.DataFrame:
    """Pad (factor > 1) or trim (factor < 1) every emitted message by the same factor."""
    out = rows.copy()
    out["mean_text_len"] = out["mean_text_len"] * factor
    out["tokens_sent"] = out["tokens_sent"] * factor
    return out


ATTACKS = {
    "error_suppression": {"fn": error_suppression, "strengths": [None], "per_run_chars": _zeros,
                          "trace_change": error_suppression.__doc__},
    "retry_diversification": {"fn": retry_diversification, "strengths": [None], "per_run_chars": _zeros,
                              "trace_change": retry_diversification.__doc__},
    "call_shaping": {"fn": call_shaping, "strengths": [1, 2, 4, 8, 16, 32], "per_run_chars": _added_chars,
                     "trace_change": call_shaping.__doc__},
    "message_shaping": {"fn": message_shaping, "strengths": [0.25, 0.5, 0.75, 1.5, 2, 4], "per_run_chars": _added_chars,
                        "trace_change": message_shaping.__doc__},
}
