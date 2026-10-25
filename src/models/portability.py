"""S2 (portability): a telemetry score learned on other sources, scored on one
source's held-out agents, paired against that source's in-domain naive baseline.

The cross-domain model sees no model identity and no task type (their categories
do not overlap across sources), only telemetry, step count and exit status. Its
training rows are the other sources' train agents, so no target-source row and no
held-out agent is ever in its training set."""
import pandas as pd

from src.models.baselines import naive_baseline
from src.models.fit import SEED, TELEMETRY, _clean, _gbm
from src.models.metrics import auc_delta_with_ci, auc_with_ci

CROSS_INPUTS = ["exit_status", "task_length_steps"] + TELEMETRY


def cross_domain_scores(df: pd.DataFrame, test_agents) -> dict:
    test_agents = set(test_agents)
    is_test = df["agent_id"].isin(test_agents)
    out = {}
    for src in sorted(df["source"].unique()):
        target = df[(df["source"] == src) & is_test]
        in_train = df[(df["source"] == src) & ~is_test]
        other = df[(df["source"] != src) & ~is_test]
        if target.empty or in_train.empty or other.empty:
            continue
        cols = [c for c in CROSS_INPUTS if c == "exit_status" or other[c].notna().any()]
        gbm = _gbm(cols).fit(_clean(other, cols), other["outcome"].to_numpy())
        out[src] = {
            "train_sources": sorted(other["source"].unique()),
            "n_train_rows": int(len(other)),
            "y": target["outcome"].to_numpy(),
            "groups": target["agent_id"].to_numpy(),
            "p_cross": gbm.predict_proba(_clean(target, cols))[:, 1],
            "p_baseline": naive_baseline(in_train["model_id"], in_train["task_type"], in_train["task_length_steps"],
                                         in_train["outcome"].to_numpy(),
                                         target["model_id"], target["task_type"], target["task_length_steps"]),
        }
    return out


def portability_report(df: pd.DataFrame, test_agents, n_boot: int = 2000, seed: int = SEED) -> dict:
    """S2 rule (prereg): supported when the paired AUC delta's 95% CI lower bound is at least 0.05."""
    out = {}
    for src, r in cross_domain_scores(df, test_agents).items():
        y, g = r["y"], r["groups"]
        degenerate = len(set(g)) < 2  # one held-out agent: the cluster bootstrap cannot form an interval
        delta = auc_delta_with_ci(y, r["p_cross"], r["p_baseline"], n_boot=n_boot, seed=seed, groups=g)
        out[src] = {"n": int(len(y)), "n_agents": int(len(set(g))), "train_sources": r["train_sources"],
                    "n_train_rows": r["n_train_rows"],
                    "auc_cross": auc_with_ci(y, r["p_cross"], n_boot=n_boot, seed=seed, groups=g),
                    "auc_baseline": auc_with_ci(y, r["p_baseline"], n_boot=n_boot, seed=seed, groups=g),
                    "auc_delta": delta, "ci_degenerate": degenerate,
                    "s2_supported": bool(not degenerate and delta["ci_low"] >= 0.05)}
    return out
