"""S4 driver: sweep attacker fraction f per scenario cell with the scorer-refit
flywheel. Outputs are synthetic (filename says so) and feed no headline result."""
import json
import sys
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.adversarial.breakeven import SCENARIOS
from src.adversarial.scorer import load_frozen
from src.common.provenance import write_result
from src.simulation.flywheel import simulate

ROOT = Path(__file__).resolve().parents[2]
N_AGENTS, ROWS_PER_AGENT, ROUNDS, BURN_IN, SEED = 500, 50, 12, 4, 20261017
F_GRID = [round(x, 2) for x in np.arange(0, 1.0001, 0.05)]


def _latest(pattern: str) -> Path:
    return sorted((ROOT / "results").glob(pattern))[-1]


def main():
    _, test = load_frozen(ROOT)
    s3 = json.loads(_latest("*_S3_attacks.json").read_text())["metrics"]
    primary = json.loads((ROOT / "results" / "2026-10-25_H1_primary.json").read_text())["metrics"]
    baseline_auc, gbm_ci = primary["auc"]["baseline"]["auc"], (primary["auc"]["gbm"]["ci_low"], primary["auc"]["gbm"]["ci_high"])
    # attackers decide per agent, which is the any-agent reading of the S3 table (ledger ruling, Task 8)
    cheapest_by_cell = {(r["runs_per_year"], r["exposure_usd"], r["one_time_usd"]): r["cheapest_attack"] for r in s3["clause4_table_any_agent"]}
    cells = []
    for scen in SCENARIOS:
        key = (scen["runs_per_year"], scen["exposure_usd"], scen["one_time_usd"])
        cheapest = cheapest_by_cell[key]
        runs = [simulate(test, scen, cheapest, f, ROUNDS, BURN_IN, ROWS_PER_AGENT, N_AGENTS, SEED, baseline_auc, gbm_ci) for f in F_GRID]
        collapsed = [r["f"] for r in runs if r["collapsed"]]
        cells.append({"scenario": scen, "cheapest_attack": cheapest, "boundary_f": min(collapsed) if collapsed else None,
                      "auc_after_burn_in": [float(np.nanmean([x["auc"] for x in r["rounds"][BURN_IN:]])) for r in runs],
                      "attackers_active_last_round": [r["rounds"][-1]["attackers_active"] for r in runs],
                      "converged": [r["converged"] for r in runs], "runs": runs})
        print(f"cell {key}: boundary_f={cells[-1]['boundary_f']}", flush=True)
    stamp = date.today().isoformat()
    out = ROOT / "results" / f"{stamp}_S4_flywheel_synthetic.json"
    write_result(out, "S4 flywheel (synthetic)", {"f_grid": F_GRID, "n_agents": N_AGENTS, "rows_per_agent": ROWS_PER_AGENT, "rounds": ROUNDS,
                 "burn_in": BURN_IN, "baseline_auc": baseline_auc, "gbm_ci": list(gbm_ci), "cells": cells},
                 {"sim_seed": SEED, "split_seed": SEED, "model_seed": SEED})
    fig, ax = plt.subplots(figsize=(6, 4))
    for c in cells:
        s = c["scenario"]
        ax.plot(F_GRID, c["auc_after_burn_in"], marker=".", label=f'R={s["runs_per_year"]} X={s["exposure_usd"]} E={s["one_time_usd"]}')
    ax.axhline(baseline_auc, color="gray", ls="--", label="naive baseline AUC")
    ax.set(xlabel="attacker fraction f", ylabel="AUC after burn-in (synthetic)", title="S4 flywheel with scorer refit")
    ax.legend(fontsize=5, ncol=2); fig.tight_layout()
    fig.savefig(ROOT / "results" / f"{stamp}_S4_flywheel_synthetic.png", dpi=150); plt.close(fig)
    print(out)


if __name__ == "__main__":
    sys.exit(main())
