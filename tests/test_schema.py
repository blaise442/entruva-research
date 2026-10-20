import pytest
from src.collect.schema import TRACE_COLUMNS, make_trace_row

BASE = dict(trace_id="t1", source="tau-bench", domain="retail", model_id="m",
            agent_id="m::harness", task_id="k", task_type="retail",
            task_length_steps=4, outcome=1, started_at="",
            has_step_latency=True, has_tool_calls=True, has_retries=False, has_errors=True)

def test_row_has_every_column_in_order():
    row = make_trace_row(**BASE)
    assert list(row) == TRACE_COLUMNS

def test_outcome_must_be_binary_and_source_known():
    with pytest.raises(ValueError, match="outcome"):
        make_trace_row(**{**BASE, "outcome": 2})
    with pytest.raises(ValueError, match="source"):
        make_trace_row(**{**BASE, "source": "made-up"})

def test_missing_field_is_an_error_not_a_default():
    bad = {k: v for k, v in BASE.items() if k != "model_id"}
    with pytest.raises(TypeError):
        make_trace_row(**bad)
