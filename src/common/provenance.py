"""Every result embeds where it came from: commit, manifest state, seeds, time."""
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from src.common.manifest import sha256_file

REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST = Path(__file__).resolve().parents[2] / "data" / "MANIFEST.md"

def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()

def provenance(seeds: dict) -> dict:
    return {
        "git_commit": _git("rev-parse", "HEAD"),
        # scoped to research/ so unrelated web work does not mark every result dirty
        "git_dirty": bool(_git("status", "--porcelain", "--", "research")),
        "manifest_sha256": sha256_file(MANIFEST),
        "seeds": seeds,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

def _json_safe(value):
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, float) and (value != value or value in (float("inf"), float("-inf"))):
        return str(value)
    return value

def write_result(path: Path, hypothesis: str, metrics: dict, seeds: dict) -> None:
    payload = {"hypothesis": hypothesis, "metrics": _json_safe(metrics), "provenance": provenance(seeds)}
    path.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
