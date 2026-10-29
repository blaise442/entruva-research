import pandas as pd

from src.crosscheck.window import window_stats

A, B, C = "0x" + "aa" * 20, "0x" + "bb" * 20, "0x" + "cc" * 20


def _identity():
    return pd.DataFrame([{"blockNumber": b, "logIndex": 0, "transactionHash": "0x00", "event": "Registered", "args": {"agentId": i, "agentURI": "", "owner": A}}
                         for i, b in enumerate((5, 50, 60, 90))])


def _feedback():
    rows = [(1, B, 55), (1, B, 56), (2, B, 70), (2, C, 71), (0, A, 10)]
    return pd.DataFrame([{"blockNumber": b, "logIndex": 0, "transactionHash": "0x00", "event": "NewFeedback",
                          "args": {"agentId": a, "clientAddress": g, "feedbackIndex": 1}} for a, g, b in rows])


def test_window_stats_count_only_events_inside_the_window():
    out = window_stats(_identity(), _feedback(), from_block=50, head=100, days=2.0)
    assert out["registrations"] == 3 and out["registrations_per_day"] == 1.5
    assert out["feedback_events"] == 4 and out["feedback_per_day"] == 2.0
    assert out["agents_with_feedback"] == 2 and out["single_giver_share"] == 0.5 and out["distinct_givers"] == 2
    assert out["from_block"] == 50 and out["head"] == 100 and out["days"] == 2.0


def test_window_stats_with_no_feedback_reports_zero_and_no_share():
    out = window_stats(_identity(), _feedback().iloc[0:0], from_block=50, head=100, days=1.0)
    assert out["feedback_events"] == 0 and out["agents_with_feedback"] == 0 and out["single_giver_share"] is None
