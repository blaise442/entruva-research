"""Every result embeds where it came from: commit, manifest state, seeds, time."""
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from src.common.manifest import sha256_file

# The study tree: the repository root here, a subdirectory in the monorepo this was split from.
STUDY_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = STUDY_ROOT / "data" / "MANIFEST.md"

def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=STUDY_ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()

def provenance(seeds: dict) -> dict:
    # scoped to the study tree: every uncommitted or untracked path in it at write time
    dirty = [line.split(maxsplit=1)[1] for line in _git("status", "--porcelain", "--", ".").splitlines()]
    return {
        "git_commit": _git("rev-parse", "HEAD"),
        "git_dirty": bool(dirty),
        "git_dirty_files": dirty,  # names what differed from git_commit, so a true flag can be weighed
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


def headline_results(results_dir: Path) -> list[Path]:
    """Every result JSON that may feed a headline: synthetic outputs are excluded by name."""
    return sorted(p for p in Path(results_dir).glob("*.json") if "synthetic" not in p.name)


def synthetic_leaks(results_dir: Path) -> list[Path]:
    """Simulation outputs (S4, flywheel) that would feed a headline because their name lacks the tag."""
    return [p for p in headline_results(results_dir) if "S4" in p.name or "flywheel" in p.name]
