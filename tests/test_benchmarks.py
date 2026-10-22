import zipfile
from pathlib import Path

from src.collect.benchmarks import (BENCHMARK_SOURCES, parse_agentdojo,
                                    parse_swe_bench, parse_tau_bench,
                                    parse_webarena)

def test_registry_names_match_schema_sources():
    assert set(BENCHMARK_SOURCES) == {"tau-bench", "swe-bench", "agentdojo", "webarena"}
    for download, parse in BENCHMARK_SOURCES.values():
        assert callable(download) and callable(parse)

FIXTURES = Path(__file__).parent / "fixtures"

def test_tau_bench_outcome_mapping_and_identity():
    rows = parse_tau_bench(FIXTURES / "tau_bench" / "gpt-4o-airline.json")
    assert len(rows) == 2
    fail, ok = rows
    assert fail["outcome"] == 1 and ok["outcome"] == 0
    assert fail["source"] == "tau-bench"
    assert fail["model_id"] == "gpt-4o"
    assert fail["agent_id"] == "gpt-4o::tau-bench"
    assert fail["domain"] == "airline" and fail["task_type"] == "airline"
    assert fail["task_length_steps"] == 5
    assert ok["task_length_steps"] == 6
    assert fail["trace_id"] != ok["trace_id"]

def test_tau_bench_availability_flags_match_format():
    rows = parse_tau_bench(FIXTURES / "tau_bench" / "gpt-4o-airline.json")
    for r in rows:
        assert r["has_step_latency"] is False
        assert r["has_tool_calls"] is True
        assert r["has_retries"] is False
        assert r["has_errors"] is False
        assert r["started_at"] == ""

def test_swe_bench_outcome_from_resolved_list():
    rows = parse_swe_bench(FIXTURES / "swe_bench" / "20240402_sweagent_gpt4")
    assert len(rows) == 2
    by_task = {r["task_id"]: r for r in rows}
    assert by_task["django__django-11001"]["outcome"] == 0
    assert by_task["astropy__astropy-14365"]["outcome"] == 1

def test_swe_bench_identity_steps_and_flags():
    rows = parse_swe_bench(FIXTURES / "swe_bench" / "20240402_sweagent_gpt4")
    r = {x["task_id"]: x for x in rows}["astropy__astropy-14365"]
    assert r["source"] == "swe-bench" and r["domain"] == "code"
    assert r["model_id"] == "gpt4"
    assert r["agent_id"] == "gpt4::sweagent"
    assert r["task_length_steps"] == 3
    assert r["has_step_latency"] is False
    assert r["has_tool_calls"] is True
    assert r["has_retries"] is False
    assert r["has_errors"] is True
    assert r["trace_id"] == "20240402_sweagent_gpt4/astropy__astropy-14365"

def test_agentdojo_skips_errored_runs_without_an_outcome():
    rows = parse_agentdojo(FIXTURES / "agentdojo" / "runs")
    assert not any(r["task_id"] == "user_task_3" for r in rows)

def test_agentdojo_utility_maps_to_outcome_and_attack_to_task_type():
    rows = parse_agentdojo(FIXTURES / "agentdojo" / "runs")
    assert len(rows) == 2
    by_task = {r["task_id"]: r for r in rows}
    ok = by_task["user_task_1"]
    fail = by_task["user_task_2"]
    assert ok["outcome"] == 0 and ok["task_type"] == "benign"
    assert fail["outcome"] == 1 and fail["task_type"] == "injection"

def test_agentdojo_identity_steps_and_flags():
    rows = parse_agentdojo(FIXTURES / "agentdojo" / "runs")
    r = {x["task_id"]: x for x in rows}["user_task_1"]
    assert r["source"] == "agentdojo" and r["domain"] == "banking"
    assert r["model_id"] == "gpt-4o-2024-05-13"
    assert r["agent_id"] == "gpt-4o-2024-05-13::agentdojo"
    assert r["task_length_steps"] == 5
    assert r["trace_id"] == "gpt-4o-2024-05-13/banking/user_task_1/none/none"
    assert r["has_step_latency"] is False
    assert r["has_tool_calls"] is True
    assert r["has_retries"] is False
    assert r["has_errors"] is True

def _webarena_zip(tmp_path):
    src = FIXTURES / "webarena" / "919_gpt4_8k_cot"
    zpath = tmp_path / "v2_919_gpt4_8k_cot.zip"
    with zipfile.ZipFile(zpath, "w") as z:
        for f in src.iterdir():
            z.write(f, f"919_gpt4_8k_cot/{f.name}")
    return zpath

def test_webarena_skips_result_lines_whose_render_html_is_missing(tmp_path):
    rows = parse_webarena(_webarena_zip(tmp_path))
    assert not any(r["task_id"] == "716" for r in rows)

def test_webarena_outcome_from_merged_log(tmp_path):
    rows = parse_webarena(_webarena_zip(tmp_path))
    assert len(rows) == 2
    by_task = {r["task_id"]: r for r in rows}
    assert by_task["0"]["outcome"] == 1
    assert by_task["1"]["outcome"] == 0

def test_webarena_identity_steps_and_flags(tmp_path):
    rows = parse_webarena(_webarena_zip(tmp_path))
    r = {x["task_id"]: x for x in rows}["0"]
    assert r["source"] == "webarena" and r["domain"] == "web"
    assert r["model_id"] == "gpt4_8k"
    assert r["agent_id"] == "gpt4_8k::webarena-cot"
    assert r["task_type"] == "shopping_admin"
    assert r["task_length_steps"] == 2
    assert {x["task_id"]: x for x in rows}["1"]["task_length_steps"] == 1
    assert r["trace_id"] == "919_gpt4_8k_cot/0"
    assert r["has_step_latency"] is False
    assert r["has_tool_calls"] is True
    assert r["has_retries"] is False
    assert r["has_errors"] is False
