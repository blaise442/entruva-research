import math
import zipfile
from pathlib import Path

from src.collect.benchmarks import (parse_agentdojo, parse_swe_bench,
                                    parse_tau_bench, parse_webarena)
from src.features.extract import (FEATURE_COLUMNS, features_from_steps,
                                  features_agentdojo, features_swe_bench,
                                  features_tau_bench, features_webarena)
from tests.test_benchmarks import FIXTURES, _webarena_zip


def S(tool, args="", error=False, n=0):
    return dict(tool=tool, args=args, error=error, text_len=n)


def test_core_counts_ratios_and_error_run():
    f = features_from_steps([S("a", "1"), S("a", "1", True, 10), S("b", "", True, 20), S("b", "", True, 30), S("c")])
    assert f["n_tool_calls"] == 5 and f["n_distinct_tools"] == 3
    assert f["repeat_call_ratio"] == 2 / 5  # a/1 repeats once, b repeats once
    assert f["n_errors"] == 3 and f["error_rate"] == 3 / 5 and f["max_error_run"] == 3
    assert f["mean_text_len"] == 12.0


def test_core_no_tool_calls_is_zero_not_nan_for_counts():
    f = features_from_steps([])
    assert f["n_tool_calls"] == 0 and f["max_error_run"] == 0
    assert math.isnan(f["error_rate"]) and math.isnan(f["mean_text_len"])


def _keys(feats):
    return {k for k in feats}


def test_tau_keys_match_parser_and_columns():
    feats = features_tau_bench(FIXTURES / "tau_bench" / "gpt-4o-airline.json")
    rows = parse_tau_bench(FIXTURES / "tau_bench" / "gpt-4o-airline.json")
    assert _keys(feats) == {r["trace_id"] for r in rows}
    assert set(next(iter(feats.values()))) == set(FEATURE_COLUMNS)


def test_agentdojo_keys_match_parser_and_duration_is_read():
    feats = features_agentdojo(FIXTURES / "agentdojo" / "runs")
    rows = parse_agentdojo(FIXTURES / "agentdojo" / "runs")
    assert _keys(feats) == {r["trace_id"] for r in rows}
    assert any(not math.isnan(v["duration_s"]) for v in feats.values())


def test_swe_keys_match_parser_and_exit_status_present():
    d = FIXTURES / "swe_bench" / "20240402_sweagent_gpt4"
    feats = features_swe_bench(d)
    assert _keys(feats) == {r["trace_id"] for r in parse_swe_bench(d)}
    assert all(isinstance(v["exit_status"], str) for v in feats.values())


def test_webarena_keys_match_parser(tmp_path):
    z = _webarena_zip(tmp_path)
    assert _keys(features_webarena(z)) == {r["trace_id"] for r in parse_webarena(z)}


def test_no_feature_column_is_the_outcome_or_a_label_field():
    banned = {"outcome", "reward", "utility", "security", "resolved", "submission", "info"}
    assert not banned & set(FEATURE_COLUMNS)


def test_build_rejects_a_feature_that_equals_or_mirrors_the_outcome():
    import pandas as pd
    import pytest
    from src.features.build import check_no_feature_equals_outcome
    base = pd.DataFrame(dict(outcome=[0, 1, 1, 0, 1], n_errors=[1, 3, 0, 2, 2], n_tool_calls=[4, 4, 4, 4, 4]))
    check_no_feature_equals_outcome(base)
    with pytest.raises(ValueError, match="n_errors"):
        check_no_feature_equals_outcome(base.assign(n_errors=base.outcome))
    with pytest.raises(ValueError, match="n_errors"):
        check_no_feature_equals_outcome(base.assign(n_errors=5 - 2 * base.outcome))
