"""Incident database collectors.

AIID rows are context-weight data: source="incident", outcome=1, counted
separately in the Gate 2 report. The OECD AI Incidents Monitor publishes no
export or API (verified 2026-10-22 at oecd.ai/en/incidents-methodology), so
it is a MANIFEST limitation, not a fetcher.
"""
import csv
import json
import re
import tarfile
from pathlib import Path

from src.collect.schema import make_trace_row
from src.common.manifest import append_entry

AIID_SNAPSHOT_URL = ("https://pub-72b2b2fc36ec423189843747af98f80e.r2.dev/"
                     "backup-20261019101022.tar.bz2")  # weekly snapshot listed at incidentdatabase.ai/research/snapshots, checked 2026-10-22

AGENTIC_RULE_DOC = (
    "An incident is agentic when its title or description mentions software "
    "taking autonomous action: any word-bounded match of autonomous(ly), "
    "agentic, ai agent(s), chatbot(s), robot(s), bot(s), self-driving, "
    "driverless, or autopilot. Pure prediction or classification failures "
    "(biased scoring, misclassification) do not match and are excluded."
)
_AGENTIC_RE = re.compile(
    r"\b(autonomous(ly)?|agentic|ai agents?|chatbots?|robots?|bots?|"
    r"self-driving|driverless|autopilot)\b", re.IGNORECASE)


def agentic_filter(incident: dict) -> bool:
    """The documented rule in AGENTIC_RULE_DOC, over title and description."""
    text = f"{incident.get('title', '')} {incident.get('description', '')}"
    return bool(_AGENTIC_RE.search(text))


def parse_aiid(snapshot_dir) -> list[dict]:
    """The mongodump_full_snapshot CSVs: incidents.csv filtered by
    agentic_filter, domain from the MIT taxonomy's Risk Domain where the
    incident is classified (the snapshot has no sector field), else
    "unclassified". Incidents carry no steps or telemetry."""
    snapshot_dir = Path(snapshot_dir)
    csv.field_size_limit(10**8)
    with open(snapshot_dir / "classifications_MIT.csv") as f:
        domains = {r["Incident ID"]: r["Risk Domain"] for r in csv.DictReader(f)}
    rows = []
    with open(snapshot_dir / "incidents.csv") as f:
        for inc in csv.DictReader(f):
            if not agentic_filter(inc):
                continue
            developers = json.loads(inc["Alleged developer of AI system"] or "[]")
            model = developers[0] if developers else "unknown"
            rows.append(make_trace_row(
                trace_id=f"aiid-{inc['incident_id']}",
                source="incident",
                domain=domains.get(inc["incident_id"], "unclassified"),
                model_id=model, agent_id=f"{model}::incident",
                task_id=inc["incident_id"], task_type="incident",
                task_length_steps=0, outcome=1, started_at=inc["date"],
                has_step_latency=False, has_tool_calls=False,
                has_retries=False, has_errors=False,
            ))
    return rows


def download_aiid(out_dir, manifest_path):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tar_path = out / AIID_SNAPSHOT_URL.rsplit("/", 1)[1]
    if not tar_path.exists():
        import requests
        r = requests.get(AIID_SNAPSHOT_URL, timeout=600)
        r.raise_for_status()
        tar_path.write_bytes(r.content)
    snapshot_dir = out / "mongodump_full_snapshot"
    members = ["mongodump_full_snapshot/incidents.csv",
               "mongodump_full_snapshot/classifications_MIT.csv",
               "mongodump_full_snapshot/license.txt"]
    if not all((out / m).exists() for m in members):
        with tarfile.open(tar_path) as tar:
            tar.extractall(out, members=[tar.getmember(m) for m in members], filter="data")
    append_entry(manifest_path, name="AI Incident Database weekly snapshot", url=AIID_SNAPSHOT_URL,
                 method="src/collect/incidents.py", row_count=len(parse_aiid(snapshot_dir)),
                 file_path=tar_path, license="CC BY-SA 4.0 (snapshot license.txt); report contents keep their own rights",
                 limitations="row count is agentic incidents only (AGENTIC_RULE_DOC keyword rule over title and description); context-weight data with outcome=1 and no steps or telemetry; the OECD AI Incidents Monitor publishes no export or API (checked 2026-10-22) and is not collected")
