import pandas as pd
import pytest

from src.adversarial import reputation
from src.adversarial.reputation import attack_costs, descriptives, eth_usd_daily


def _ids(agents, owners=None):
    owners = owners or [f"0xowner{a}" for a in agents]
    return pd.DataFrame({"event": "Registered", "blockNumber": range(len(agents)),
                         "args": [{"agentId": a, "owner": o} for a, o in zip(agents, owners)]})


def _fb(pairs):
    return pd.DataFrame({"event": "NewFeedback", "blockNumber": range(len(pairs)),
                         "args": [{"agentId": a, "clientAddress": w} for a, w in pairs]})


def test_descriptives_single_giver_share():
    d = descriptives(_ids(["a", "b"]), _fb([("a", "w1"), ("a", "w1"), ("b", "w2"), ("b", "w3")]))
    assert d["n_registered"] == 2 and d["n_feedback"] == 4
    assert d["agents_with_single_giver"] == 1 and d["agents_with_feedback"] == 2
    assert d["givers_per_agent"]["median"] == 1.5


def test_descriptives_share_from_registrants():
    d = descriptives(_ids(["a", "b"], owners=["w1", "w9"]), _fb([("a", "w1"), ("b", "w2")]))
    assert d["share_feedback_from_registrant_wallets"] == 0.5


def test_attack_costs_scale_with_counts():
    gas = pd.DataFrame({"event": ["Registered", "NewFeedback"], "gasUsed": [100_000, 50_000],
                        "effectiveGasPrice_wei": [10**10, 10**10], "block_day": ["2026-01-01", "2026-01-01"]})
    c = attack_costs(gas, usd=None, median_feedback=3, ring_k=3)
    assert c["registration_eth"] == pytest.approx(1e-3) and c["feedback_eth"] == pytest.approx(5e-4)
    assert c["sybil_eth"] == pytest.approx(3 * (100_000 + 50_000) * 1e-8)
    assert c["collusion_eth"] == pytest.approx(6 * 50_000 * 1e-8)
    assert c["whitewash_eth"] == pytest.approx(1e-3) and "sybil_usd" not in c


def test_attack_costs_in_usd_use_the_block_day_price():
    gas = pd.DataFrame({"event": ["Registered", "NewFeedback"], "gasUsed": [100_000, 50_000],
                        "effectiveGasPrice_wei": [10**10, 10**10], "block_day": ["2026-01-01", "2026-01-02"]})
    usd = pd.DataFrame({"day": ["2026-01-01", "2026-01-02"], "usd": [1000.0, 2000.0]})
    c = attack_costs(gas, usd=usd, median_feedback=1, ring_k=2)
    assert c["registration_usd"] == pytest.approx(1.0) and c["feedback_usd"] == pytest.approx(1.0)


class _Resp:
    def __init__(self, status, payload=None):
        self.status_code, self._payload = status, payload or {}

    def json(self):
        return self._payload


def test_eth_usd_fetch_failure_leaves_usd_empty(monkeypatch):
    monkeypatch.setattr(reputation.requests, "get", lambda *a, **k: _Resp(500))
    with pytest.raises(RuntimeError, match="ETH-USD"):
        eth_usd_daily(["2026-01-01"])


def test_eth_usd_daily_parses_coinbase(monkeypatch):
    monkeypatch.setattr(reputation.requests, "get", lambda url, **k: _Resp(200, {"data": {"amount": "1234.5"}}))
    df = eth_usd_daily(["2026-01-01"])
    assert list(df.columns) == ["day", "usd"] and df.usd.iloc[0] == 1234.5


class _RateLimitedW3:
    """Receipts fail with 429 twice, then succeed; blocks always succeed."""
    def __init__(self):
        self.fails = 2
        self.eth = self

    def get_transaction_receipt(self, h):
        if self.fails:
            self.fails -= 1
            raise reputation.requests.HTTPError("429", response=_Resp(429))
        return {"blockNumber": 7, "gasUsed": 100, "effectiveGasPrice": 5}

    def get_block(self, b):
        return {"timestamp": 1_700_000_000}


def test_gas_sample_retries_a_429_with_backoff(monkeypatch):
    sleeps = []
    monkeypatch.setattr(reputation.time, "sleep", lambda s: sleeps.append(s))
    events = pd.DataFrame({"event": ["Registered", "NewFeedback"], "transactionHash": ["0xa", "0xb"]})
    gas = reputation.gas_sample(events, _RateLimitedW3(), n=1, seed=0)
    assert len(gas) == 2 and (gas.gasUsed == 100).all()
    assert len([s for s in sleeps if s >= 1]) == 2  # two backoff waits, pacing sleeps aside
