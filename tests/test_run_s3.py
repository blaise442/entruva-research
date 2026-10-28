import pandas as pd

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
