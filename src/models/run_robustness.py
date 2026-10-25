"""Robustness for H1: grouped 5-fold CV by agent with pooled OOF predictions,
reported pooled and within each source (within-source scoring removes the
between-source base-rate differences that can inflate a pooled AUC). Also the
S2 portability test on the frozen split and the descriptive Poisson GLM
relativities (actuarial framing, decides no clause)."""
import sys
from datetime import date
from pathlib import Path

import pandas as pd

from src.common.provenance import write_result
from src.models.cv import cv_oof
from src.models.fit import SEED
from src.models.glm import poisson_relativities
from src.models.portability import portability_report
from src.models.split import load_split
from src.models.metrics import auc_delta_with_ci, auc_with_ci, brier_skill, quartile_failure_ratio

ROOT = Path(__file__).resolve().parents[2]
N_BOOT = 2000


def score(y, oof, groups, mask):
    y, g, base = y[mask], groups[mask], oof["baseline"][mask]
    out = {"n": int(mask.sum()), "n_agents": int(len(set(g))), "failure_rate": float(y.mean()),
           "auc_baseline": auc_with_ci(y, base, n_boot=N_BOOT, seed=SEED, groups=g)}
    for k in ("gbm", "logit"):
        p = oof[k][mask]
        out[k] = {"auc": auc_with_ci(y, p, n_boot=N_BOOT, seed=SEED, groups=g),
                  "auc_delta": auc_delta_with_ci(y, p, base, n_boot=N_BOOT, seed=SEED, groups=g),
                  "brier_skill": brier_skill(y, p, base, n_boot=N_BOOT, seed=SEED, groups=g),
                  "quartile": quartile_failure_ratio(y, p, seed=SEED)}
    return out


def main():
    df = pd.read_csv(ROOT / "data/processed/features.csv", low_memory=False).reset_index(drop=True)
    oof, folds = cv_oof(df)
    y, groups, src = df["outcome"].to_numpy(), df["agent_id"].to_numpy(), df["source"].to_numpy()
    res = {"pooled": score(y, oof, groups, src == src)}
    res["by_source"] = {s: score(y, oof, groups, src == s) for s in sorted(set(src))}
    split = load_split(ROOT / "splits/primary_split.json", ROOT / "data/processed/trace_index.csv", df["agent_id"])
    res["s2_portability"] = portability_report(df, split["test_agents"], n_boot=N_BOOT, seed=SEED)
    res["s2_supported_any_source"] = any(r["s2_supported"] for r in res["s2_portability"].values())
    res["glm_relativities_per_sd"] = poisson_relativities(df, n_boot=N_BOOT, seed=SEED)
    out = ROOT / "results" / f"{date.today().isoformat()}_H1_robustness_cv.json"
    write_result(out, "H1 robustness (grouped 5-fold CV)", res, {"cv_seed": SEED, "model_seed": SEED, "split_seed": split["seed"], "n_boot": N_BOOT})
    print(out)


if __name__ == "__main__":
    sys.exit(main())
