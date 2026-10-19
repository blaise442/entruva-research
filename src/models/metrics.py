"""Preregistered metrics. y is 0/1 with 1 = failure; p is predicted failure probability."""
import numpy as np
from sklearn.metrics import brier_score_loss, roc_auc_score

def _check_two_classes(y: np.ndarray) -> None:
    if len(np.unique(y)) < 2:
        raise ValueError("y contains only one class; AUC and skill are undefined")

def _bootstrap_ci(stat_fn, n: int, n_boot: int, seed: int) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    stats = []
    attempts = 0
    while len(stats) < n_boot and attempts < n_boot * 10:
        attempts += 1
        idx = rng.integers(0, n, n)
        s = stat_fn(idx)
        if s is not None:
            stats.append(s)
    if not stats:
        raise ValueError("bootstrap failed: every resample lost one class")
    lo, hi = np.percentile(stats, [2.5, 97.5])
    return float(lo), float(hi)

def auc_with_ci(y, p, n_boot: int = 2000, seed: int = 0) -> dict:
    y, p = np.asarray(y), np.asarray(p)
    _check_two_classes(y)
    def stat(idx):
        if len(np.unique(y[idx])) < 2:
            return None
        return roc_auc_score(y[idx], p[idx])
    lo, hi = _bootstrap_ci(stat, len(y), n_boot, seed)
    return {"auc": float(roc_auc_score(y, p)), "ci_low": lo, "ci_high": hi}

def brier_skill(y, p_model, p_baseline, n_boot: int = 2000, seed: int = 0) -> dict:
    y, pm, pb = np.asarray(y), np.asarray(p_model), np.asarray(p_baseline)
    _check_two_classes(y)
    def skill(idx):
        b = brier_score_loss(y[idx], pb[idx])
        if b == 0:
            return None
        return 1.0 - brier_score_loss(y[idx], pm[idx]) / b
    lo, hi = _bootstrap_ci(skill, len(y), n_boot, seed)
    base = brier_score_loss(y, pb)
    return {"skill": float(1.0 - brier_score_loss(y, pm) / base), "ci_low": lo, "ci_high": hi}

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

def _rank_groups(y, p, n_groups: int) -> list[np.ndarray]:
    order = np.argsort(p, kind="stable")
    return [np.asarray(y)[chunk] for chunk in np.array_split(order, n_groups)]

def decile_lift(y, p) -> list[dict]:
    overall = float(np.asarray(y).mean())
    rows = []
    for i, chunk in enumerate(_rank_groups(y, p, 10), start=1):
        rate = float(chunk.mean())
        rows.append({"decile": i, "failure_rate": rate, "lift": rate / overall if overall else float("inf")})
    return rows

def quartile_failure_ratio(y, p) -> float:
    quartiles = _rank_groups(y, p, 4)
    bottom, top = float(quartiles[0].mean()), float(quartiles[-1].mean())
    if bottom == 0.0:
        return float("inf")
    return top / bottom
