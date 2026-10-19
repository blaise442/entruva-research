"""Preregistered metrics. y is 0/1 with 1 = failure; p is predicted failure probability.

Bootstrap scheme (preregistered): with groups given, a cluster bootstrap that
resamples whole groups (agents), because rows within an agent are correlated and
an iid row bootstrap narrows the CI. Without groups, a class-stratified row
bootstrap that preserves class counts, so no resample ever loses a class.
Cluster resamples that lose a class are redrawn; if fewer than n_boot survive
10 * n_boot attempts the function raises instead of returning a quiet, narrow CI.
"""
import numpy as np
from sklearn.metrics import brier_score_loss, roc_auc_score

def _check_two_classes(y: np.ndarray) -> None:
    if len(np.unique(y)) < 2:
        raise ValueError("y contains only one class; AUC and skill are undefined")

def _resample_indices(y: np.ndarray, groups, n_boot: int, seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed)
    out: list[np.ndarray] = []
    if groups is None:
        pos, neg = np.flatnonzero(y == 1), np.flatnonzero(y == 0)
        for _ in range(n_boot):
            out.append(np.concatenate([rng.choice(pos, len(pos)), rng.choice(neg, len(neg))]))
        return out
    groups = np.asarray(groups)
    uniq = np.unique(groups)
    members = {g: np.flatnonzero(groups == g) for g in uniq}
    attempts = 0
    while len(out) < n_boot and attempts < n_boot * 10:
        attempts += 1
        idx = np.concatenate([members[g] for g in rng.choice(uniq, len(uniq))])
        if len(np.unique(y[idx])) == 2:
            out.append(idx)
    if len(out) < n_boot:
        raise ValueError(
            f"cluster bootstrap kept only {len(out)} of {n_boot} resamples; "
            "too many group resamples lose a class, so the CI would be unreliable"
        )
    return out

def _boot_ci(stat_fn, resamples) -> tuple[float, float]:
    stats = [stat_fn(idx) for idx in resamples]
    lo, hi = np.percentile(stats, [2.5, 97.5])
    return float(lo), float(hi)

def auc_with_ci(y, p, n_boot: int = 2000, seed: int = 0, groups=None) -> dict:
    y, p = np.asarray(y), np.asarray(p)
    _check_two_classes(y)
    resamples = _resample_indices(y, groups, n_boot, seed)
    lo, hi = _boot_ci(lambda idx: roc_auc_score(y[idx], p[idx]), resamples)
    return {"auc": float(roc_auc_score(y, p)), "ci_low": lo, "ci_high": hi, "n_boot_used": len(resamples)}

def auc_delta_with_ci(y, p_model, p_baseline, n_boot: int = 2000, seed: int = 0, groups=None) -> dict:
    """Paired bootstrap of AUC(model) - AUC(baseline) on the same resamples (S1, S2 rule)."""
    y, pm, pb = np.asarray(y), np.asarray(p_model), np.asarray(p_baseline)
    _check_two_classes(y)
    resamples = _resample_indices(y, groups, n_boot, seed)
    lo, hi = _boot_ci(lambda idx: roc_auc_score(y[idx], pm[idx]) - roc_auc_score(y[idx], pb[idx]), resamples)
    delta = float(roc_auc_score(y, pm) - roc_auc_score(y, pb))
    return {"delta": delta, "ci_low": lo, "ci_high": hi, "n_boot_used": len(resamples)}

def brier_skill(y, p_model, p_baseline, n_boot: int = 2000, seed: int = 0, groups=None) -> dict:
    y, pm, pb = np.asarray(y), np.asarray(p_model), np.asarray(p_baseline)
    _check_two_classes(y)
    base = brier_score_loss(y, pb)
    if base == 0:
        raise ValueError("baseline Brier score is 0 (perfect baseline); skill is undefined")
    resamples = _resample_indices(y, groups, n_boot, seed)
    def skill(idx):
        b = brier_score_loss(y[idx], pb[idx])
        return 1.0 - brier_score_loss(y[idx], pm[idx]) / b if b > 0 else 1.0
    lo, hi = _boot_ci(skill, resamples)
    return {"skill": float(1.0 - brier_score_loss(y, pm) / base), "ci_low": lo, "ci_high": hi,
            "n_boot_used": len(resamples)}

def reliability_bins(y, p, n_bins: int = 10) -> list[dict]:
    y, p = np.asarray(y), np.asarray(p)
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    which = np.clip(np.digitize(p, edges[1:-1]), 0, n_bins - 1)
    out = []
    for b in range(n_bins):
        mask = which == b
        if mask.any():
            out.append({"p_mean": float(p[mask].mean()), "y_rate": float(y[mask].mean()), "n": int(mask.sum())})
    return out

def _rank_groups(y, p, n_groups: int, rng) -> list[np.ndarray]:
    # ties in p are broken by a seeded random key, never by row order
    order = np.lexsort((rng.permutation(len(p)), np.asarray(p)))
    return [np.asarray(y)[chunk] for chunk in np.array_split(order, n_groups)]

def decile_lift(y, p, seed: int = 0) -> list[dict]:
    y = np.asarray(y)
    if len(y) < 10:
        raise ValueError("decile lift needs at least 10 rows")
    overall = float(y.mean())
    rng = np.random.default_rng(seed)
    rows = []
    for i, chunk in enumerate(_rank_groups(y, p, 10, rng), start=1):
        rate = float(chunk.mean())
        rows.append({"decile": i, "failure_rate": rate, "lift": rate / overall if overall else float("inf")})
    return rows

def quartile_failure_ratio(y, p, seed: int = 0, n_draws: int = 25) -> dict:
    """Top/bottom predicted-risk quartile failure ratio, averaged over seeded
    tie-break draws, with the counts reported so an inf is never a bare number."""
    rng = np.random.default_rng(seed)
    ratios, tops, bottoms, top_n, bottom_n = [], [], [], 0, 0
    for _ in range(n_draws):
        quartiles = _rank_groups(y, p, 4, rng)
        bottom, top = quartiles[0], quartiles[-1]
        top_n, bottom_n = len(top), len(bottom)
        tops.append(float(top.sum()))
        bottoms.append(float(bottom.sum()))
        ratios.append(float("inf") if bottom.sum() == 0 else float(top.mean() / bottom.mean()))
    return {
        "ratio": float(np.mean(ratios)),
        "top_failures": float(np.mean(tops)),
        "bottom_failures": float(np.mean(bottoms)),
        "top_n": top_n,
        "bottom_n": bottom_n,
        "n_draws": n_draws,
    }
