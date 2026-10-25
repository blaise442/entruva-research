"""Actuarial framing: Poisson GLM frequency model on standardized telemetry
features, reporting relativities exp(coef) per one-SD increase with cluster
bootstrap CIs over agents. Descriptive; it decides no clause."""
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.linear_model import PoissonRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.models.fit import SEED, TELEMETRY

GLM_INPUTS = ["task_length_steps"] + TELEMETRY


def _fit_coefs(X, y):
    pipe = Pipeline([("imp", SimpleImputer(strategy="median", keep_empty_features=True)), ("sc", StandardScaler()),
                     ("glm", PoissonRegressor(alpha=1e-6, max_iter=1000))]).fit(X, y)
    return pipe["glm"].coef_


def poisson_relativities(df, n_boot: int = 2000, seed: int = SEED) -> dict:
    cols = [c for c in GLM_INPUTS if df[c].notna().any()]
    X, y, groups = df[cols].to_numpy(dtype=float), df["outcome"].to_numpy(), df["agent_id"].to_numpy()
    point = _fit_coefs(X, y)
    agents = np.unique(groups)
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(n_boot):
        pick = rng.choice(agents, size=len(agents), replace=True)
        idx = np.concatenate([np.flatnonzero(groups == a) for a in pick])
        boots.append(_fit_coefs(X[idx], y[idx]))
    lo, hi = np.percentile(np.exp(boots), [2.5, 97.5], axis=0)
    return {c: {"relativity": float(np.exp(point[i])), "ci_low": float(lo[i]), "ci_high": float(hi[i])}
            for i, c in enumerate(cols)}
