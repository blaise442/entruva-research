from src.collect.index import build_index
from src.collect.report import data_report
from tests.test_index import _row

def _df():
    return build_index([
        _row("a", outcome=1),
        _row("b", outcome=0),
        _row("w1", source="webarena", domain="web", agent_id="g::cot", model_id="g",
             has_tool_calls=True, has_step_latency=False),
        _row("i1", source="incident", domain="unclassified", agent_id="x::incident",
             model_id="x", task_type="incident", task_length_steps=0,
             has_tool_calls=False),
    ])

def test_report_counts_rows_and_label_balance_per_source():
    r = data_report(_df())
    assert "tau-bench: 2 rows" in r
    assert "failure rate 50.0%" in r
    assert "webarena: 1 rows" in r

def test_report_counts_incidents_separately_from_benchmark_rows():
    r = data_report(_df())
    assert "Benchmark and on-chain rows: 3" in r
    assert "Incident rows (context weight, all failures): 1" in r

def test_report_states_sources_obtained_of_planned():
    r = data_report(_df())
    assert "sources obtained: 3 of 6 planned" in r

def test_report_missing_flag_fractions():
    r = data_report(_df())
    # all 4 rows lack step latency; 1 of 4 lacks tool calls
    assert "has_step_latency: missing in 100.0%" in r
    assert "has_tool_calls: missing in 25.0%" in r

def test_report_cross_source_trace_id_collisions():
    df = build_index([_row("t1", source="tau-bench"),
                      _row("t1", source="webarena", domain="web")])
    assert "cross-source trace_id collisions: 1" in data_report(df)

def test_empty_input_reports_no_rows_instead_of_crashing():
    r = data_report(build_index([]))
    assert "no rows" in r.lower()
