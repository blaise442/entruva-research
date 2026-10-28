"""S4 flywheel (design Part D, DEVIATIONS 2026-10-27). Synthetic: every output of
run_s4 carries "synthetic" in its filename and feeds no headline result.

Agents' true failure rates are resampled from the Phase 2 held-out agents; each
round their observed telemetry is a resample of that source agent's real rows with
the chosen attack applied for attackers; the insurer refits the Phase 2 model
class on the previous round's observed rows and true outcomes."""
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from src.adversarial.attacks import ATTACKS
from src.adversarial.scorer import frozen_scorer
from src.models.fit import NUMERIC


@dataclass
class Population:
    agent_ids: np.ndarray
    source_agent: np.ndarray
    true_rate: np.ndarray
    is_attacker: np.ndarray


def make_population(test: pd.DataFrame, n_agents: int, f: float, seed: int) -> Population:
    rng = np.random.default_rng(seed)
    rates = test.groupby("agent_id")["outcome"].mean()
    src = rng.choice(rates.index.to_numpy(), size=n_agents, replace=True)
    attackers = np.zeros(n_agents, dtype=bool)
    attackers[rng.permutation(n_agents)[: int(round(f * n_agents))]] = True
    return Population(np.array([f"sim{i:04d}" for i in range(n_agents)]), src, rates.loc[src].to_numpy(), attackers)


def draw_round(pop: Population, test: pd.DataFrame, rows_per_agent: int, rng: np.random.Generator) -> pd.DataFrame:
    by_src = {a: g.index.to_numpy() for a, g in test.groupby("agent_id")}
    parts = []
    for sid, src, rate in zip(pop.agent_ids, pop.source_agent, pop.true_rate):
        rows = test.loc[rng.choice(by_src[src], size=rows_per_agent, replace=True)].copy()
        rows["sim_agent_id"] = sid
        rows["outcome"] = (rng.random(rows_per_agent) < rate).astype(int)
        parts.append(rows)
    return pd.concat(parts, ignore_index=True)


def refit(observed: pd.DataFrame, previous: Callable) -> tuple[Callable, bool]:
    if observed["outcome"].nunique() < 2:
        return previous, False
    return frozen_scorer(observed), True


def overwrite_rows(observed: pd.DataFrame, attacked: pd.DataFrame, mask: np.ndarray) -> pd.DataFrame:
    """Copy the attacked telemetry columns into the masked rows; every other column
    (outcome, ids) keeps its values and dtype."""
    out = observed.copy()
    cols = [c for c in NUMERIC if c in attacked.columns]
    out.loc[mask, cols] = attacked.loc[mask, cols].to_numpy()
    return out


def _apply(rows: pd.DataFrame, cheapest: dict) -> pd.DataFrame:
    spec = ATTACKS[cheapest["attack"]]
    return spec["fn"](rows) if cheapest["strength"] is None else spec["fn"](rows, cheapest["strength"])


def attack_pays(dp: float, exposure_usd: float, cost_usd: float) -> bool:
    """The attacker's own rule: saving over the year exceeds cost. The 3x in the
    breakeven table is the insurer's floor, not the attacker's."""
    return dp * exposure_usd > cost_usd


def simulate(test, scenario, cheapest, f, rounds, burn_in, rows_per_agent, n_agents, seed, baseline_auc, gbm_ci, scorer0) -> dict:
    rng = np.random.default_rng(seed)
    pop = make_population(test, n_agents, f, seed)
    scorer = scorer0  # round 0 uses the Phase 2 scorer (design Part D)
    paid = np.zeros(n_agents, dtype=bool)
    R, X, E = scenario["runs_per_year"], scenario["exposure_usd"], scenario["one_time_usd"]
    out = []
    for _ in range(rounds):
        honest = draw_round(pop, test, rows_per_agent, rng)
        observed = honest.copy()
        active = 0
        if cheapest is not None and pop.is_attacker.any():
            attacked = _apply(honest, cheapest)
            p_h, p_a = scorer(honest), scorer(attacked)
            for i, sid in enumerate(pop.agent_ids):
                if not pop.is_attacker[i]:
                    continue
                m = (honest["sim_agent_id"] == sid).to_numpy()
                dp = float(p_h[m].mean() - p_a[m].mean())
                if attack_pays(dp, X, (0.0 if paid[i] else E) + cheapest["per_run_usd"] * R):
                    observed = overwrite_rows(observed, attacked, m)
                    paid[i] = True
                    active += 1
        p = scorer(observed)
        agent_p = pd.Series(p).groupby(observed["sim_agent_id"].to_numpy()).mean().reindex(pop.agent_ids).to_numpy()
        premium = agent_p * X
        top = pop.true_rate >= np.quantile(pop.true_rate, 0.75)
        auc = float(roc_auc_score(observed["outcome"], p)) if observed["outcome"].nunique() > 1 else float("nan")
        out.append({"auc": auc, "top_quartile_premium_share": float(premium[top].sum() / premium.sum()) if premium.sum() else float("nan"),
                    "attackers_active": active, "refit_ok": None})
        scorer, ok = refit(observed, scorer)
        out[-1]["refit_ok"] = ok
    tail = [r["auc"] for r in out[burn_in:]]
    finite = [a for a in tail if a == a]
    return {"scenario": scenario, "f": f, "n_attackers": int(pop.is_attacker.sum()), "rounds": out,
            "converged": bool(finite) and all(gbm_ci[0] <= a <= gbm_ci[1] for a in finite),
            "collapsed": bool(finite) and all(a < baseline_auc for a in finite)}
