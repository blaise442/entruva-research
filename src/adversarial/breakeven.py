"""Clause 4 breakeven table (design Part B, DEVIATIONS 2026-10-27).

Premium is pure expected loss: predicted failure probability times severity. The
annual saving from a one-decile drop is dp x exposure, with exposure X = severity x
runs per year. The floor says attack cost over one year must be at least 3 x the
saving, so the breakeven exposure is X* = (E + c R) / (3 dp). No severity, volume
or premium is asserted: the grid rows are labelled scenarios."""
import math

FLOOR_MULTIPLE = 3.0
RUNS_PER_YEAR = [1000, 100000]
EXPOSURE_USD = [1000, 10000, 100000, 1000000]
ONE_TIME_USD = [0, 10000]
SCENARIOS = [{"runs_per_year": r, "exposure_usd": x, "one_time_usd": e}
             for r in RUNS_PER_YEAR for x in EXPOSURE_USD for e in ONE_TIME_USD]


def breakeven_exposure(one_time_usd: float, per_run_usd: float, runs_per_year: float, delta_p: float) -> float:
    if delta_p <= 0:
        return math.inf
    return (one_time_usd + per_run_usd * runs_per_year) / (FLOOR_MULTIPLE * delta_p)


def _moves(c: dict) -> bool:
    return c["deciles_moved_median"] >= 1


def cheapest_attack(curves: list[dict]) -> dict | None:
    """The priced decile-moving curve with the smallest breakeven at E = 0."""
    priced = [c for c in curves if _moves(c) and c["per_run_usd"] is not None]
    if not priced:
        return None
    return min(priced, key=lambda c: breakeven_exposure(0, c["per_run_usd"], 1, c["delta_p"]))


def clause4_table(curves: list[dict], scenarios: list[dict]) -> list[dict]:
    moving = [c for c in curves if _moves(c)]
    unpriced_only = bool(moving) and all(c["per_run_usd"] is None for c in moving)
    rows = []
    for s in scenarios:
        priced = [c for c in moving if c["per_run_usd"] is not None]
        best, x_star = None, None
        if priced:
            scored = [(breakeven_exposure(s["one_time_usd"], c["per_run_usd"], s["runs_per_year"], c["delta_p"]), c) for c in priced]
            x_star, best = min(scored, key=lambda t: t[0])
        passes: bool | str
        if unpriced_only:
            passes = "not evaluable"
        elif best is None:
            passes = True  # nothing moves a decile
        else:
            passes = x_star > s["exposure_usd"]
        rows.append({**s, "cheapest_attack": best, "breakeven_exposure_usd": x_star, "passes": passes})
    return rows


def clause4_verdict(table: list[dict]) -> str:
    if any(r["passes"] is False for r in table):
        return "fail"
    if any(r["passes"] == "not evaluable" for r in table):
        return "not evaluable"
    return "pass"
