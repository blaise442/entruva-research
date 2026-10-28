import json
import subprocess
from pathlib import Path
from src.common.provenance import provenance, write_result

def test_provenance_fields():
    p = provenance(seeds={"bootstrap": 7})
    assert len(p["git_commit"]) == 40
    assert p["git_commit"] == subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    assert isinstance(p["git_dirty"], bool)
    assert len(p["manifest_sha256"]) == 64
    assert p["seeds"] == {"bootstrap": 7}
    assert p["timestamp_utc"].endswith("+00:00")

def test_write_result_embeds_provenance(tmp_path: Path):
    out = tmp_path / "2026-10-19_H1_metrics.json"
    write_result(out, hypothesis="H1", metrics={"auc": 0.5, "ratio": float("inf")}, seeds={"cv": 1})
    d = json.loads(out.read_text())
    assert d["hypothesis"] == "H1"
    assert d["metrics"]["ratio"] == "inf"
    assert d["provenance"]["seeds"] == {"cv": 1}


def test_headline_results_excludes_synthetic(tmp_path):
    from src.common.provenance import headline_results
    (tmp_path / "a_S3.json").write_text("{}")
    (tmp_path / "b_S4_flywheel_synthetic.json").write_text("{}")
    assert [p.name for p in headline_results(tmp_path)] == ["a_S3.json"]


def test_synthetic_leaks_lists_simulation_files_without_the_tag(tmp_path):
    from src.common.provenance import synthetic_leaks
    for n in ["a_S3.json", "b_S4_flywheel.json", "c_S4_flywheel_synthetic.json"]:
        (tmp_path / n).write_text("{}")
    assert [p.name for p in synthetic_leaks(tmp_path)] == ["b_S4_flywheel.json"]


def test_committed_results_have_no_synthetic_leaks():
    from src.common.provenance import synthetic_leaks
    results = Path(__file__).resolve().parents[1] / "results"
    assert any("S4" in p.name for p in results.glob("*.json"))  # the check is not vacuous
    assert synthetic_leaks(results) == []
