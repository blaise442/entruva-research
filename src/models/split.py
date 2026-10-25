"""Frozen primary held-out split: whole agents, chosen once, committed to the repo.

Held out per benchmark source: ceil(20%) of its agent_ids, chosen by a seeded
shuffle. Incident rows carry no telemetry and are excluded from every model."""
import hashlib
import json
import math
from pathlib import Path

import numpy as np

SEED = 20261017
TEST_FRACTION = 0.2


def freeze_split(index_df, out_path, seed: int = SEED) -> dict:
    rng = np.random.default_rng(seed)
    bench = index_df[index_df["source"] != "incident"]
    train, test = [], []
    for src in sorted(bench["source"].unique()):
        agents = sorted(bench.loc[bench["source"] == src, "agent_id"].unique())
        if len(agents) < 2:
            raise ValueError(f"source {src} has {len(agents)} agent; cannot hold one out")
        order = rng.permutation(len(agents))
        n_test = math.ceil(TEST_FRACTION * len(agents))
        test += [agents[i] for i in order[:n_test]]
        train += [agents[i] for i in order[n_test:]]
    split = {"seed": seed, "test_fraction": TEST_FRACTION,
             "test_agents": sorted(test), "train_agents": sorted(train)}
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(split, indent=2) + "\n")
    return split


def load_split(path, index_path, agent_ids) -> dict:
    """Reads the frozen split and refuses to apply it to a different index or population."""
    split = json.loads(Path(path).read_text())
    sha = hashlib.sha256(Path(index_path).read_bytes()).hexdigest()
    if sha != split["index_sha256"]:
        raise ValueError(f"index sha256 {sha[:12]} does not match the frozen split's {split['index_sha256'][:12]}")
    extra = set(agent_ids) ^ (set(split["train_agents"]) | set(split["test_agents"]))
    if extra:
        raise ValueError(f"{len(extra)} agent(s) differ between the data and the frozen split: {sorted(extra)[:5]}")
    return split
