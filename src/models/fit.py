"""Preregistered models fit on the frozen train agents and scored on the test agents.

Baseline: src/models/baselines.py. Telemetry model: HistGradientBoosting with
library defaults, random_state 20261017. A logistic regression on the same inputs
is reported alongside but does not decide H1. Nothing here reads the outcome as an
input; MODEL_INPUTS is the whole feature list."""
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

from src.models.baselines import naive_baseline
from src.models.metrics import (auc_delta_with_ci, auc_with_ci, brier_skill,
                                decile_lift, quartile_failure_ratio, reliability_bins)

SEED = 20261017
CATEGORICAL = ["model_id", "task_type", "exit_status"]
TELEMETRY = ["n_tool_calls", "n_distinct_tools", "repeat_call_ratio", "n_errors",
             "error_rate", "max_error_run", "mean_text_len", "duration_s",
             "api_calls", "tokens_sent"]
MODEL_INPUTS = CATEGORICAL + ["task_length_steps"] + TELEMETRY
NUMERIC = [c for c in MODEL_INPUTS if c not in CATEGORICAL]


def _gbm(cols):
    cat = [c for c in cols if c in CATEGORICAL]
    enc = ColumnTransformer(
        [("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=np.nan), cat)],
        remainder="passthrough", verbose_feature_names_out=False)
    mask = [True] * len(cat) + [False] * (len(cols) - len(cat))
    return Pipeline([("enc", enc),
                     ("clf", HistGradientBoostingClassifier(random_state=SEED, categorical_features=mask))])


def _logit(cols):
    cat = [c for c in cols if c in CATEGORICAL]
    num = [c for c in cols if c not in CATEGORICAL]
    pre = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
        ("num", Pipeline([("imp", SimpleImputer(strategy="median", add_indicator=True)),
                          ("sc", StandardScaler())]), num)])
    return Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=2000))])


def _clean(df, cols):
    X = df[cols].copy()
    if "exit_status" in X:
        X["exit_status"] = X["exit_status"].fillna("").astype(str)
    return X


def model_columns(train, with_model_id: bool = True) -> list[str]:
    """The exact input columns a fit uses: categoricals first (the ordinal-encoder
    mask depends on it), all-missing numerics dropped (they carry nothing)."""
    cols = MODEL_INPUTS if with_model_id else [c for c in MODEL_INPUTS if c != "model_id"]
    cols = [c for c in cols if c in CATEGORICAL] + [c for c in cols if c not in CATEGORICAL]
    return [c for c in cols if c in CATEGORICAL or train[c].notna().any()]


def fit_predict(train, test, with_model_id: bool = True) -> dict:
    """Out-of-sample failure probabilities for every model on the test rows."""
    cols = model_columns(train, with_model_id)
    ytr = train["outcome"].to_numpy()
    out = {"baseline": naive_baseline(train["model_id"], train["task_type"], train["task_length_steps"], ytr,
                                      test["model_id"], test["task_type"], test["task_length_steps"])}
    for name, make in (("gbm", _gbm), ("logit", _logit)):
        m = make(cols).fit(_clean(train, cols), ytr)
        out[name] = m.predict_proba(_clean(test, cols))[:, 1]
    return out


def _report(y, p, base, groups, n_boot, seed):
    return {
        "auc": auc_with_ci(y, p, n_boot=n_boot, seed=seed, groups=groups),
        "auc_delta": auc_delta_with_ci(y, p, base, n_boot=n_boot, seed=seed, groups=groups),
        "brier_skill": brier_skill(y, p, base, n_boot=n_boot, seed=seed, groups=groups),
        "quartile": quartile_failure_ratio(y, p, seed=seed),
        "decile_lift": decile_lift(y, p, seed=seed),
        "reliability": reliability_bins(y, p),
    }


def evaluate_split(train, test, n_boot: int = 2000, seed: int = SEED) -> dict:
    if set(train["agent_id"]) & set(test["agent_id"]):
        raise ValueError("train and test share agents; the split is not agent-held-out")
    y, groups = test["outcome"].to_numpy(), test["agent_id"].to_numpy()
    preds = fit_predict(train, test)
    base = preds["baseline"]
    res = {"n_train": len(train), "n_test": len(test), "n_test_agents": int(len(set(groups))),
           "test_failure_rate": float(y.mean()),
           "auc": {"baseline": auc_with_ci(y, base, n_boot=n_boot, seed=seed, groups=groups)}}
    for name in ("gbm", "logit"):
        r = _report(y, preds[name], base, groups, n_boot, seed)
        res["auc"][name] = r["auc"]
        res[f"auc_delta_{name}"] = r["auc_delta"]
        res[f"brier_skill_{name}"] = r["brier_skill"]
        res[f"quartile_{name}"] = r["quartile"]
        res[f"decile_lift_{name}"] = r["decile_lift"]
        res[f"reliability_{name}"] = r["reliability"]
    tonly = fit_predict(train, test, with_model_id=False)["gbm"]
    res["sensitivity_telemetry_only_gbm"] = _report(y, tonly, base, groups, n_boot, seed)
    return res
