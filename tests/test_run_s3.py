import pandas as pd
import pytest

from src.adversarial.attacks import ATTACKS
from src.adversarial.run_s3 import attack_curve
from src.adversarial.scorer import decile_edges, frozen_scorer
from tests.test_scorer import small_frozen  # noqa: F401  (fixture)

EMPTY_PRICES = pd.DataFrame(columns=["model_id", "input_usd_per_mtok", "output_usd_per_mtok"])
EMPTY_RATIOS = pd.DataFrame(columns=["source", "model_id", "encoding", "chars_per_token"])


def test_attack_curve_reports_movers_and_delta_p(small_frozen):
    train, test = small_frozen
    test = test.assign(source="s")
    score = frozen_scorer(train)
    edges = decile_edges(score(test))
    c = attack_curve(test, score, edges, ATTACKS["error_suppression"], None, prices=EMPTY_PRICES, ratios=EMPTY_RATIOS)
    assert set(c) >= {"attack", "strength", "deciles_moved_median", "movers_frac", "any_agent_moved", "per_run_usd", "delta_p", "per_agent"}
    assert c["attack"] == "error_suppression" and c["strength"] is None
    assert c["per_run_usd"] == 0.0  # free attack is priced at zero, not None
    assert len(c["per_agent"]) == test.agent_id.nunique()
    assert {"agent_id", "decile_before", "decile_after", "p_before", "p_after", "per_run_usd"} <= set(c["per_agent"][0])


def test_priced_attack_is_none_when_a_model_is_unpriced(small_frozen):
    train, test = small_frozen
    test = test.assign(source="s")
    score = frozen_scorer(train)
    c = attack_curve(test, score, decile_edges(score(test)), ATTACKS["call_shaping"], 4, prices=EMPTY_PRICES,
                     ratios=pd.DataFrame([{"source": "s", "model_id": "cl100k_base", "encoding": "cl100k_base", "chars_per_token": 4.0}]))
    assert c["per_run_usd"] is None and set(c["unpriced_models"]) == {"m1", "m2"}


def test_any_agent_view_counts_single_movers_as_moving():
    from src.adversarial.run_s3 import any_agent_view
    curves = [{"attack": "a", "deciles_moved_median": 0.0, "any_agent_moved": True, "per_run_usd": 0.0, "delta_p": 0.02},
              {"attack": "b", "deciles_moved_median": 0.0, "any_agent_moved": False, "per_run_usd": 0.0, "delta_p": 0.0}]
    v = any_agent_view(curves)
    assert v[0]["deciles_moved_median"] == 1.0 and v[1]["deciles_moved_median"] == 0.0
    assert curves[0]["deciles_moved_median"] == 0.0  # input untouched


def _toy():
    # one row per decile for z, two rows each for x (decile 9) and y (decile 2); p = mean_text_len / 1000
    rows = [{"agent_id": "z", "mean_text_len": 50.0 + 100 * i} for i in range(10)]
    rows += [{"agent_id": "x", "mean_text_len": 850.0}] * 2 + [{"agent_id": "y", "mean_text_len": 150.0}] * 2
    return pd.DataFrame(rows).assign(model_id="m", source="s", tokens_sent=100.0, n_tool_calls=5.0)


def test_attack_curve_with_no_movable_agent_reports_none():
    import numpy as np
    test = _toy()
    score = lambda df: np.full(len(df), 0.05)
    c = attack_curve(test, score, np.linspace(0.1, 0.9, 9), ATTACKS["message_shaping"], 0.5, prices=EMPTY_PRICES, ratios=EMPTY_RATIOS)
    assert c["n_movable"] == 0 and c["deciles_moved_median"] is None and c["any_agent_moved"] is False


def test_delta_p_is_the_difference_of_decile_mean_predictions():
    import numpy as np
    test = _toy()
    score = lambda df: df["mean_text_len"].to_numpy() / 1000
    c = attack_curve(test, score, np.linspace(0.1, 0.9, 9), ATTACKS["message_shaping"], 0.5, prices=EMPTY_PRICES, ratios=EMPTY_RATIOS)
    # x: 9 -> 5 (0.85 - 0.45), y: 2 -> 1 (0.15 - 0.05), z: 6 -> 3 (0.55 - 0.25); agent-level drops would average 0.25
    assert c["delta_p"] == pytest.approx((0.40 + 0.10 + 0.30) / 3)
    assert c["decile_mean_p"][8] == pytest.approx(0.85) and len(c["decile_mean_p"]) == 10
