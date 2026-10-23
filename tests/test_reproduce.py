import shutil
from pathlib import Path

from src.reproduce import collect_all

FIXTURES = Path(__file__).parent / "fixtures"

def test_collect_all_reads_each_present_source_and_skips_missing(tmp_path):
    (tmp_path / "tau-bench").mkdir()
    shutil.copy(FIXTURES / "tau_bench" / "gpt-4o-airline.json", tmp_path / "tau-bench")
    shutil.copytree(FIXTURES / "aiid" / "mongodump_full_snapshot",
                    tmp_path / "incidents" / "mongodump_full_snapshot")
    rows = collect_all(tmp_path)
    sources = {r["source"] for r in rows}
    assert sources == {"tau-bench", "incident"}  # swe-bench, agentdojo, webarena absent: skipped

def test_collect_all_on_empty_raw_returns_nothing(tmp_path):
    assert collect_all(tmp_path) == []
