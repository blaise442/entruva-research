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
