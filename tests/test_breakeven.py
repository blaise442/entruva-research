import math

import pytest

from src.adversarial.breakeven import SCENARIOS, breakeven_exposure, cheapest_attack, clause4_table, clause4_verdict


def _curve(**k):
    base = dict(attack="a", strength=None, deciles_moved_median=1, movers_frac=0.6, per_run_usd=0.0, delta_p=0.05)
    return {**base, **k}


def test_scenario_grid_is_the_fixed_16_cells():
    assert len(SCENARIOS) == 16
    assert {s["runs_per_year"] for s in SCENARIOS} == {1000, 100000}
    assert {s["exposure_usd"] for s in SCENARIOS} == {1000, 10000, 100000, 1000000}
    assert {s["one_time_usd"] for s in SCENARIOS} == {0, 10000}


def test_breakeven_exposure_formula():
    assert breakeven_exposure(0, 0.001, 1000, 0.02) == pytest.approx(1 / 0.06)
    assert breakeven_exposure(10_000, 0, 1000, 0.05) == pytest.approx(10_000 / 0.15)
    assert breakeven_exposure(10, 1, 10, 0) == math.inf


def test_cheapest_attack_ignores_unpriced():
    curves = [_curve(attack="a", per_run_usd=None),
              _curve(attack="b", strength=4, per_run_usd=0.01, delta_p=0.03)]
    assert cheapest_attack(curves)["attack"] == "b"
    assert cheapest_attack([_curve(attack="a", per_run_usd=None)]) is None
    assert cheapest_attack([_curve(deciles_moved_median=0)]) is None


def test_clause4_table_rows_carry_scenario_and_cheapest_curve():
    table = clause4_table([_curve(per_run_usd=0.001, delta_p=0.05)], SCENARIOS)
    assert len(table) == 16
    row = table[0]
    assert {"runs_per_year", "exposure_usd", "one_time_usd", "cheapest_attack", "breakeven_exposure_usd", "passes"} <= set(row)
    assert row["cheapest_attack"]["attack"] == "a"
    assert row["breakeven_exposure_usd"] == pytest.approx(breakeven_exposure(row["one_time_usd"], 0.001, row["runs_per_year"], 0.05))


def test_clause4_verdict_requires_every_cell():
    free = [_curve(per_run_usd=0.0, delta_p=0.05)]
    table = clause4_table(free, SCENARIOS)
    assert all(r["passes"] is False for r in table if r["one_time_usd"] == 0)  # zero cost never clears the floor
    assert clause4_verdict(table) == "fail"
    assert clause4_verdict(clause4_table([], SCENARIOS)) == "pass"  # nothing moves a decile
    unpriced_only = clause4_table([_curve(per_run_usd=None)], SCENARIOS)
    assert all(r["passes"] == "not evaluable" for r in unpriced_only)
    assert clause4_verdict(unpriced_only) == "not evaluable"


def test_clause4_table_with_no_movable_agent_is_not_evaluable():
    table = clause4_table([_curve(deciles_moved_median=None, n_movable=0, delta_p=0.0)], SCENARIOS)
    assert all(r["passes"] == "not evaluable" for r in table)
    assert clause4_verdict(table) == "not evaluable"
