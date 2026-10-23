from pathlib import Path

from src.collect.incidents import AGENTIC_RULE_DOC, agentic_filter, parse_aiid

FIXTURE_SNAPSHOT = Path(__file__).parent / "fixtures" / "aiid" / "mongodump_full_snapshot"

AGENTIC = {
    "title": "Delivery robot autonomously crossed an active rail crossing",
    "description": "An autonomous sidewalk delivery robot entered a rail crossing while the barriers were down.",
}
NON_AGENTIC = {
    "title": "Loan scoring model found biased against applicants",
    "description": "A credit scoring classifier systematically under-scored applicants from minority neighborhoods.",
}
BORDERLINE_AUTOPILOT = {
    "title": "Tesla on Autopilot struck a stopped emergency vehicle",
    "description": "The driver assistance system failed to detect a stationary fire truck.",
}

def test_clearly_agentic_incident_is_included():
    assert agentic_filter(AGENTIC) is True

def test_clearly_non_agentic_biased_classifier_is_excluded():
    assert agentic_filter(NON_AGENTIC) is False

def test_borderline_autopilot_crash_counts_as_agentic():
    assert agentic_filter(BORDERLINE_AUTOPILOT) is True

def test_rule_is_documented_and_word_bounded():
    assert "autonomous" in AGENTIC_RULE_DOC
    # "robotics" the research field is not an autonomous actor; word bounds matter
    assert agentic_filter({"title": "Chatbots in botany", "description": "a botany quiz chatbot"}) is True
    assert agentic_filter({"title": "Botany dataset mislabeled", "description": "herbarium photos misclassified"}) is False

def test_parse_aiid_keeps_only_agentic_incidents_as_failure_rows():
    rows = parse_aiid(FIXTURE_SNAPSHOT)
    assert {r["task_id"] for r in rows} == {"101", "103"}  # 102 is the biased classifier
    for r in rows:
        assert r["source"] == "incident"
        assert r["outcome"] == 1
        assert r["task_type"] == "incident"
        assert r["task_length_steps"] == 0
        assert r["has_step_latency"] is False and r["has_tool_calls"] is False
        assert r["has_retries"] is False and r["has_errors"] is False

def test_parse_aiid_identity_domain_and_date():
    rows = {r["task_id"]: r for r in parse_aiid(FIXTURE_SNAPSHOT)}
    robot = rows["101"]
    assert robot["trace_id"] == "aiid-101"
    assert robot["model_id"] == "starship-technologies"
    assert robot["agent_id"] == "starship-technologies::incident"
    assert robot["domain"] == "AI system safety failures & limitations"
    assert robot["started_at"] == "2023-04-01"
    assert rows["103"]["domain"] == "unclassified"  # no MIT classification row
