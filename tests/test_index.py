import pytest

from src.collect.index import build_index, write_index
from src.collect.schema import TRACE_COLUMNS, make_trace_row

def _row(trace_id="t1", source="tau-bench", **over):
    base = dict(trace_id=trace_id, source=source, domain="retail", model_id="m",
                agent_id="m::h", task_id="k", task_type="retail",
                task_length_steps=3, outcome=1, started_at="",
                has_step_latency=False, has_tool_calls=True,
                has_retries=False, has_errors=False)
    return make_trace_row(**{**base, **over})

def test_index_keeps_schema_order_and_rows():
    df = build_index([_row("a"), _row("b", outcome=0)])
    assert list(df.columns) == TRACE_COLUMNS
    assert len(df) == 2

def test_duplicate_source_trace_id_raises_naming_the_id():
    with pytest.raises(ValueError, match="t1"):
        build_index([_row("t1"), _row("t1")])

def test_same_trace_id_across_sources_is_allowed():
    df = build_index([_row("t1", source="tau-bench"), _row("t1", source="webarena", domain="web")])
    assert len(df) == 2

def test_write_index_round_trips(tmp_path):
    import pandas as pd
    df = build_index([_row("a"), _row("b")])
    out = tmp_path / "trace_index.csv"
    write_index(df, out)
    back = pd.read_csv(out, keep_default_na=False)
    assert list(back.columns) == TRACE_COLUMNS
    assert len(back) == 2
