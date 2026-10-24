import json

import pandas as pd

from src.models.split import freeze_split


def _df():
    rows = []
    for src, agents in {"tau-bench": 2, "agentdojo": 10, "webarena": 5}.items():
        for a in range(agents):
            for i in range(3):
                rows.append(dict(source=src, trace_id=f"{src}/{a}/{i}", agent_id=f"m{a}::{src}", outcome=i % 2))
    rows.append(dict(source="incident", trace_id="i1", agent_id="x::incident", outcome=1))
    return pd.DataFrame(rows)


def test_no_agent_on_both_sides_and_incidents_excluded(tmp_path):
    split = freeze_split(_df(), tmp_path / "s.json")
    assert not set(split["test_agents"]) & set(split["train_agents"])
    assert "x::incident" not in split["test_agents"] + split["train_agents"]


def test_every_source_has_train_and_test_agents(tmp_path):
    split = freeze_split(_df(), tmp_path / "s.json")
    for src in ("tau-bench", "agentdojo", "webarena"):
        assert any(a.endswith(f"::{src}") for a in split["test_agents"])
        assert any(a.endswith(f"::{src}") for a in split["train_agents"])


def test_deterministic_and_written(tmp_path):
    a = freeze_split(_df(), tmp_path / "a.json")
    b = freeze_split(_df(), tmp_path / "b.json")
    assert a["test_agents"] == b["test_agents"]
    assert json.loads((tmp_path / "a.json").read_text())["seed"] == 20261017
