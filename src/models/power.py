"""Gate 2 power estimate by simulation. Synthetic data here is a power
calculation tool, clearly not study data; it feeds only the Gate 2 report's
power section and never touches results/ headline files.

Model: outcomes are correlated within agent (a logistic random intercept per
agent), the baseline score carries no signal (AUC 0.5), and the telemetry
score is binormal so its marginal AUC is 0.5 + delta. A simulated study
"detects" delta when the preregistered paired cluster-bootstrap test
(auc_delta_with_ci, grouped by agent) has its CI lower bound above 0.
"""
import numpy as np
from scipy.special import expit, logit, ndtri

from src.models.metrics import auc_delta_with_ci

DELTA_GRID = (0.02, 0.03, 0.05, 0.08, 0.10)
POWER_TARGET = 0.8


def _simulate(rng, n_rows, failure_rate, n_agents, delta):
    agents = rng.integers(0, n_agents, n_rows)
    u = rng.normal(0.0, 0.5, n_agents)
    y = (rng.random(n_rows) < expit(logit(failure_rate) + u[agents])).astype(int)
    dprime = np.sqrt(2.0) * ndtri(0.5 + delta)
    score = rng.normal(0.0, 1.0, n_rows) + dprime * y + 0.3 * u[agents]
    baseline = rng.normal(0.0, 1.0, n_rows)
    return y, score, baseline, agents


def min_detectable_auc_delta(n_rows, failure_rate, n_agents, n_sims=500,
                             seed=20261017, n_boot=200) -> dict:
    rng = np.random.default_rng(seed)
    power_by_delta = {}
    for delta in DELTA_GRID:
        hits = 0
        for _ in range(n_sims):
            y, score, baseline, agents = _simulate(rng, n_rows, failure_rate, n_agents, delta)
            if len(set(y)) < 2:
                continue  # degenerate draw, counts as a miss
            res = auc_delta_with_ci(y, score, baseline, n_boot=n_boot,
                                    seed=int(rng.integers(2**31)), groups=agents)
            hits += res["ci_low"] > 0
        power_by_delta[delta] = hits / n_sims
    detectable = [d for d in DELTA_GRID if power_by_delta[d] >= POWER_TARGET]
    return {
        "n_rows": n_rows, "failure_rate": failure_rate, "n_agents": n_agents,
        "n_sims": n_sims, "seed": seed, "n_boot": n_boot,
        "power_by_delta": power_by_delta,
        "power_at_0.05": power_by_delta[0.05],
        "min_detectable_delta": min(detectable) if detectable else None,
    }
