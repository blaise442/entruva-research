"""Primary H1 evaluation on the frozen split. Writes results/<date>_H1_primary.json
and two figures. Verdict logic is the preregistered rule; clause 4 (manipulation
cost) is Phase 3 and is reported as pending, never assumed."""
import json
import sys
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

from src.common.provenance import write_result
from src.models.fit import SEED, evaluate_split, fit_predict

ROOT = Path(__file__).resolve().parents[2]


def clauses(res: dict) -> dict:
    base_auc = res["auc"]["baseline"]["auc"]
    g = res["auc"]["gbm"]
    deciles = [d["failure_rate"] for d in res["decile_lift_gbm"]]
    rho = float(spearmanr(range(10), deciles)[0])
    q = res["quartile_gbm"]
    c1 = g["ci_low"] - base_auc >= 0.05
    c2 = res["brier_skill_gbm"]["ci_low"] > 0
    c3 = q["ratio"] >= 2.0 and rho > 0.8  # 0.8: "monotone enough"; fixed here, before results
    refuted = g["ci_low"] <= base_auc <= g["ci_high"] or g["ci_high"] < base_auc or res["brier_skill_gbm"]["skill"] <= 0
    return {"clause1_auc": bool(c1), "clause2_brier": bool(c2), "clause3_quartile_and_monotone": bool(c3),
            "decile_spearman": rho, "clause4_manipulation_cost": "pending Phase 3",
            "h1_refuted_by_preregistered_rule": bool(refuted)}


def per_source(test, preds):
    out = {}
    for src, g in test.groupby("source"):
        idx = g.index.to_numpy()
        if g["outcome"].nunique() < 2:
            continue
        out[src] = {"n": len(g), "failure_rate": float(g["outcome"].mean()),
                    **{k: float(roc_auc_score(g["outcome"], preds[k].loc[idx])) for k in preds}}
    return out


def main():
    df = pd.read_csv(ROOT / "data/processed/features.csv", low_memory=False)
    split = json.loads((ROOT / "splits/primary_split.json").read_text())
    train, test = df[df.agent_id.isin(split["train_agents"])], df[df.agent_id.isin(split["test_agents"])]
    res = evaluate_split(train, test)
    res["clauses"] = clauses(res)
    preds = {k: pd.Series(v, index=test.index) for k, v in fit_predict(train, test).items()}
    res["per_source_auc_descriptive"] = per_source(test, preds)
    stamp = date.today().isoformat()
    out = ROOT / "results" / f"{stamp}_H1_primary.json"
    write_result(out, "H1", res, {"split_seed": split["seed"], "model_seed": SEED, "bootstrap_seed": SEED, "n_boot": 2000})
    rel = res["reliability_gbm"]
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.plot([0, 1], [0, 1], "--", color="gray"); ax.plot([b["p_mean"] for b in rel], [b["y_rate"] for b in rel], "o-")
    ax.set(xlabel="predicted failure probability", ylabel="observed failure rate", title="GBM reliability (held-out agents)")
    fig.tight_layout(); fig.savefig(ROOT / "results" / f"{stamp}_H1_reliability.png", dpi=150); plt.close(fig)
    dl = res["decile_lift_gbm"]
    fig, ax = plt.subplots(figsize=(5, 3.5))
    ax.bar([d["decile"] for d in dl], [d["failure_rate"] for d in dl])
    ax.set(xlabel="predicted-risk decile (1 = lowest)", ylabel="observed failure rate", title="GBM decile lift (held-out agents)")
    fig.tight_layout(); fig.savefig(ROOT / "results" / f"{stamp}_H1_decile_lift.png", dpi=150); plt.close(fig)
    print(out)


if __name__ == "__main__":
    sys.exit(main())
