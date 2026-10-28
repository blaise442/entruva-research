"""The frozen Phase 2 scorer and agent-level deciles for Phase 3.

There is no saved model artifact: the frozen GBM is the deterministic refit on
the frozen train agents with the Phase 2 seed, exactly as run_primary does it."""
from collections.abc import Callable
from pathlib import Path

import numpy as np
import pandas as pd

from src.models.fit import _clean, _gbm, model_columns
from src.models.split import load_split


def frozen_scorer(train: pd.DataFrame) -> Callable[[pd.DataFrame], np.ndarray]:
    cols = model_columns(train)
    m = _gbm(cols).fit(_clean(train, cols), train["outcome"].to_numpy())
    return lambda df: m.predict_proba(_clean(df, cols))[:, 1]


def decile_edges(p: np.ndarray) -> np.ndarray:
    """Nine interior cut points of the untransformed held-out predictions."""
    return np.quantile(np.asarray(p), np.linspace(0.1, 0.9, 9))


def agent_deciles(p: np.ndarray, agent_ids: np.ndarray, edges: np.ndarray) -> pd.DataFrame:
    """Decile (1 = lowest risk) of each agent's mean predicted probability."""
    d = pd.DataFrame({"agent_id": agent_ids, "p": np.asarray(p)}).groupby("agent_id", as_index=False)["p"].mean()
    d = d.rename(columns={"p": "p_mean"})
    d["decile"] = np.searchsorted(edges, d["p_mean"].to_numpy(), side="right") + 1
    d["movable"] = d["decile"] > 1
    return d


def load_frozen(root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(train, test) exactly as run_primary builds them from the frozen split."""
    df = pd.read_csv(root / "data/processed/features.csv", low_memory=False)
    split = load_split(root / "splits/primary_split.json", root / "data/processed/trace_index.csv", df["agent_id"])
    return df[df.agent_id.isin(split["train_agents"])], df[df.agent_id.isin(split["test_agents"])]
