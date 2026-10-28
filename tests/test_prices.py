import json
from pathlib import Path

import pandas as pd
import pytest

from src.adversarial.prices import chars_per_token_for, load_prices, price_for, usd_per_run

ROOT = Path(__file__).resolve().parents[1]
PRICES = ROOT / "data/prices/model_prices.csv"
RATIOS = ROOT / "data/prices/chars_per_token.csv"
SPLIT = ROOT / "splits/primary_split.json"


def test_price_for_unknown_model_is_none():
    assert price_for("meta-llama_Llama-3.3-70B-Instruct", load_prices(PRICES)) is None
    assert price_for("never-seen-model", load_prices(PRICES)) is None


def test_price_rows_cover_every_held_out_model_or_are_explicitly_unpriced():
    held = {a.split("::")[0] for a in json.load(open(SPLIT))["test_agents"]}
    table = load_prices(PRICES)
    assert held <= set(table.model_id)
    assert table.source_url.notna().all() and table.fetched_on.notna().all()
    priced = table.dropna(subset=["input_usd_per_mtok"])
    assert (priced.input_usd_per_mtok > 0).all() and (priced.output_usd_per_mtok > 0).all()


def test_ratio_table_has_a_fallback_row_per_source():
    r = pd.read_csv(RATIOS)
    assert {"agentdojo", "swe-bench", "tau-bench", "webarena"} <= set(r[r.model_id == "cl100k_base"].source)
    assert (r.chars_per_token > 1).all()


def test_usd_per_run_uses_measured_ratio_and_both_directions():
    prices = pd.DataFrame([{"model_id": "m", "input_usd_per_mtok": 2.0, "output_usd_per_mtok": 8.0}])
    ratios = pd.DataFrame([{"source": "s", "model_id": "m", "encoding": "x", "chars_per_token": 4.0},
                           {"source": "s", "model_id": "cl100k_base", "encoding": "cl100k_base", "chars_per_token": 2.0}])
    assert usd_per_run(4_000_000, "m", "s", prices, ratios) == pytest.approx(10.0)
    assert usd_per_run(100, "unknown", "s", prices, ratios) is None
    assert chars_per_token_for("s", "other", ratios) == 2.0
    with pytest.raises(KeyError):
        chars_per_token_for("nosource", "m", ratios)
