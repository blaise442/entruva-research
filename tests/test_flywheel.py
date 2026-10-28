import numpy as np

from src.adversarial.breakeven import SCENARIOS
from src.simulation.flywheel import make_population, refit, simulate
from tests.test_scorer import small_frozen  # noqa: F401  (fixture)


def test_make_population_attacker_fraction_and_rates(small_frozen):
    _, test = small_frozen
    pop = make_population(test, n_agents=20, f=0.25, seed=1)
    assert pop.is_attacker.sum() == 5 and len(pop.agent_ids) == 20
    assert set(pop.source_agent) <= set(test.agent_id)
    rates = test.groupby("agent_id")["outcome"].mean()
    assert all(abs(r - rates[s]) < 1e-12 for r, s in zip(pop.true_rate, pop.source_agent))


def test_refit_round_with_one_class_keeps_previous_scorer(small_frozen):
    _, test = small_frozen
    prev = lambda df: np.full(len(df), 0.3)
    scorer, ok = refit(test.assign(outcome=0), prev)
    assert scorer is prev and ok is False
    scorer2, ok2 = refit(test, prev)
    assert ok2 is True and scorer2 is not prev and len(scorer2(test)) == len(test)


def test_simulate_with_no_attackers_converges(small_frozen):
    train, test = small_frozen
    out = simulate(test, SCENARIOS[0], cheapest=None, f=0.0, rounds=3, burn_in=1, rows_per_agent=5, n_agents=8, seed=1,
                   baseline_auc=0.5, gbm_ci=(0.0, 1.0))
    assert out["converged"] and not out["collapsed"] and len(out["rounds"]) == 3
    assert {"auc", "top_quartile_premium_share", "attackers_active", "refit_ok"} <= set(out["rounds"][0])
    assert all(r["attackers_active"] == 0 for r in out["rounds"])


def test_simulate_attackers_act_when_breakeven_says_it_pays(small_frozen):
    train, test = small_frozen
    cheapest = {"attack": "error_suppression", "strength": None, "per_run_usd": 0.0, "delta_p": 0.05}
    scen = {"runs_per_year": 1000, "exposure_usd": 1_000_000, "one_time_usd": 0}
    out = simulate(test, scen, cheapest=cheapest, f=0.5, rounds=2, burn_in=1, rows_per_agent=5, n_agents=8, seed=1,
                   baseline_auc=0.5, gbm_ci=(0.0, 1.0))
    assert out["rounds"][0]["attackers_active"] >= 0 and out["n_attackers"] == 4


def test_overwrite_attacked_rows_keeps_integer_columns():
    import pandas as pd
    from src.simulation.flywheel import overwrite_rows
    observed = pd.DataFrame({"outcome": [1, 0, 1], "n_errors": [2.0, 1.0, 0.0], "sim_agent_id": ["a", "a", "b"]})
    attacked = observed.assign(n_errors=0.0)
    out = overwrite_rows(observed, attacked, observed.sim_agent_id.to_numpy() == "a")
    assert list(out.n_errors) == [0.0, 0.0, 0.0] and out.outcome.dtype == observed.outcome.dtype
    assert list(observed.n_errors) == [2.0, 1.0, 0.0]  # pure
