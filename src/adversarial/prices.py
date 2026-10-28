"""Public list prices and measured chars-per-token ratios (design Part A pricing rule).

model_prices.csv rows come from vendor pricing pages, each with its URL and fetch
date; a model with no public list price has empty price columns and a note, and
comes out unpriced (None). Nothing here is typed from memory."""
from pathlib import Path

import pandas as pd

FALLBACK = "cl100k_base"


def load_prices(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def price_for(model_id: str, prices: pd.DataFrame) -> dict | None:
    row = prices[prices.model_id == model_id].dropna(subset=["input_usd_per_mtok", "output_usd_per_mtok"])
    if row.empty:
        return None
    r = row.iloc[0]
    return {"input_usd_per_mtok": float(r.input_usd_per_mtok), "output_usd_per_mtok": float(r.output_usd_per_mtok)}


def chars_per_token_for(source: str, model_id: str, table: pd.DataFrame) -> float:
    src = table[table.source == source]
    exact = src[src.model_id == model_id]
    fallback = src[src.model_id == FALLBACK]
    if not exact.empty:
        return float(exact.chars_per_token.iloc[0])
    if not fallback.empty:
        return float(fallback.chars_per_token.iloc[0])
    raise KeyError(f"no chars-per-token ratio for source {source!r}")


def usd_per_run(added_chars: float, model_id: str, source: str, prices: pd.DataFrame, ratios: pd.DataFrame) -> float | None:
    """Added characters as tokens, charged once as input and once as an equal-size output."""
    p = price_for(model_id, prices)
    if p is None:
        return None
    tokens = added_chars / chars_per_token_for(source, model_id, ratios)
    return tokens / 1e6 * (p["input_usd_per_mtok"] + p["output_usd_per_mtok"])
