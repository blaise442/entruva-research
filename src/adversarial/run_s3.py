"""S3 attack curves and the clause 4 breakeven table (design Parts A and B).
Writes results/<date>_S3_attacks.json and one figure per attack."""
import sys
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.adversarial.attacks import ATTACKS
from src.adversarial.breakeven import SCENARIOS, clause4_table, clause4_verdict
from src.adversarial.prices import chars_per_token_for, load_prices, usd_per_run
from src.adversarial.scorer import agent_deciles, decile_edges, frozen_scorer, load_frozen
from src.common.provenance import write_result
from src.models.fit import SEED

ROOT = Path(__file__).resolve().parents[2]


def _ratios_per_row(test: pd.DataFrame, ratios: pd.DataFrame, default: float = 4.0) -> pd.Series:
    def one(r):
        try:
            return chars_per_token_for(r["source"], r["model_id"], ratios)
        except KeyError:
            return default
    return test.apply(one, axis=1)


def attack_curve(test, score, edges, spec, strength, prices, ratios) -> dict:
    p0 = score(test)
    before = agent_deciles(p0, test["agent_id"].to_numpy(), edges).set_index("agent_id")
    # premium is defined on the decile, so the saving is the difference of decile mean predictions (design Part B)
    dmean = pd.Series(p0).groupby(np.searchsorted(edges, p0, side="right") + 1).mean()
    if strength is None:
        attacked = spec["fn"](test)
    elif spec["fn"].__name__ == "call_shaping":
        attacked = spec["fn"](test, strength, chars_per_token=_ratios_per_row(test, ratios))
    else:
        attacked = spec["fn"](test, strength)
    after = agent_deciles(score(attacked), test["agent_id"].to_numpy(), edges).set_index("agent_id")
    chars = spec["per_run_chars"](test, attacked)
    if (chars == 0).all():
        row_usd = pd.Series(0.0, index=test.index)
    else:
        row_usd = pd.Series([usd_per_run(c, m, s, prices, ratios) for c, m, s in zip(chars, test["model_id"], test["source"])],
                            index=test.index, dtype=object)
    unpriced = sorted(set(test.loc[row_usd.isna(), "model_id"]))
    per_agent = []
    for a in before.index:
        usd = row_usd[test["agent_id"].to_numpy() == a]
        per_agent.append({"agent_id": a, "decile_before": int(before.loc[a, "decile"]), "decile_after": int(after.loc[a, "decile"]),
                          "p_before": float(before.loc[a, "p_mean"]), "p_after": float(after.loc[a, "p_mean"]),
                          "movable": bool(before.loc[a, "movable"]),
                          "per_run_usd": None if usd.isna().any() else float(usd.astype(float).mean())})
    movable = [r for r in per_agent if r["movable"]]
    moved = [r["decile_before"] - r["decile_after"] for r in movable]
    movers = [r for r, m in zip(movable, moved) if m >= 1]
    return {"attack": spec["fn"].__name__, "strength": strength,
            "deciles_moved_median": float(np.median(moved)) if moved else None,
            "movers_frac": len(movers) / len(movable) if movable else 0.0,
            "any_agent_moved": bool(movers), "n_movable": len(movable),
            "delta_p": float(np.mean([dmean[r["decile_before"]] - dmean[r["decile_after"]] for r in movers])) if movers else 0.0,
            "decile_mean_p": [float(dmean.get(d, float("nan"))) for d in range(1, 11)],
            "per_run_usd": None if unpriced else float(row_usd.astype(float).mean()),
            "unpriced_models": unpriced, "per_agent": per_agent}


def any_agent_view(curves: list[dict]) -> list[dict]:
    """The harsher reading: an attack counts as moving a decile when it moves any agent."""
    return [{**c, "deciles_moved_median": max(1.0, c["deciles_moved_median"]) if c["any_agent_moved"] else c["deciles_moved_median"]}
            for c in curves]


def _figure(curves: list[dict], attack: str, out: Path) -> None:
    cs = [c for c in curves if c["attack"] == attack]
    x = [str(c["strength"]) for c in cs]
    med = [c["deciles_moved_median"] if c["deciles_moved_median"] is not None else 0.0 for c in cs]
    lo = [min(r["decile_before"] - r["decile_after"] for r in c["per_agent"] if r["movable"]) if c["n_movable"] else 0 for c in cs]
    hi = [max(r["decile_before"] - r["decile_after"] for r in c["per_agent"] if r["movable"]) if c["n_movable"] else 0 for c in cs]
    fig, ax = plt.subplots(figsize=(5, 3.5))
    ax.errorbar(x, med, yerr=[np.subtract(med, lo), np.subtract(hi, med)], fmt="o-", capsize=3, label="deciles moved (median, min..max)")
    ax.set(xlabel="strength", ylabel="deciles moved (held-out agents)", title=attack)
    ax2 = ax.twinx()
    ax2.plot(x, [c["per_run_usd"] if c["per_run_usd"] is not None else np.nan for c in cs], "s--", color="gray", label="USD per run")
    ax2.set_ylabel("USD per run (None = unpriced)")
    fig.tight_layout(); fig.savefig(out, dpi=150); plt.close(fig)


def main():
    train, test = load_frozen(ROOT)
    prices, ratios = load_prices(ROOT / "data/prices/model_prices.csv"), pd.read_csv(ROOT / "data/prices/chars_per_token.csv")
    score = frozen_scorer(train)
    edges = decile_edges(score(test))
    curves = [attack_curve(test, score, edges, spec, s, prices, ratios) for spec in ATTACKS.values() for s in spec["strengths"]]
    table = clause4_table(curves, SCENARIOS)
    table_any = clause4_table(any_agent_view(curves), SCENARIOS)
    res = {"n_test": len(test), "n_test_agents": int(test["agent_id"].nunique()), "decile_edges": [float(e) for e in edges],
           "curves": curves, "clause4_table": table, "clause4_verdict": clause4_verdict(table),
           "clause4_table_any_agent": table_any, "clause4_verdict_any_agent": clause4_verdict(table_any),
           "unpriced_models": sorted({m for c in curves for m in c["unpriced_models"]})}
    stamp = date.today().isoformat()
    out = ROOT / "results" / f"{stamp}_S3_attacks.json"
    write_result(out, "H1 clause 4 (S3)", res, {"split_seed": SEED, "model_seed": SEED})
    for attack in ATTACKS:
        _figure(curves, attack, ROOT / "results" / f"{stamp}_S3_{attack}.png")
    print(out)


if __name__ == "__main__":
    sys.exit(main())
