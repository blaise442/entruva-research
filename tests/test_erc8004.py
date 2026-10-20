import json
import pytest
from src.collect.erc8004 import fetch_logs, to_jsonable

class StubEth:
    """get_logs stub: holds (block, log) pairs; raises on ranges wider than max_span."""
    def __init__(self, logs_by_block: dict[int, list[dict]], max_span: int | None = None):
        self.logs_by_block = logs_by_block
        self.max_span = max_span
        self.calls = 0

    def get_logs(self, params):
        self.calls += 1
        lo, hi = params["fromBlock"], params["toBlock"]
        if self.max_span is not None and hi - lo + 1 > self.max_span:
            raise ValueError("query returned more than 10000 results")
        return [l for b in range(lo, hi + 1) for l in self.logs_by_block.get(b, [])]

def _log(block, i=0):
    return {"blockNumber": block, "logIndex": i, "transactionHash": bytes.fromhex("ab" * 32),
            "address": "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432",
            "topics": [bytes.fromhex("cd" * 32)], "data": bytes.fromhex("00")}

def test_fetch_logs_spans_chunk_boundaries():
    eth = StubEth({5: [_log(5)], 100_000: [_log(100_000)], 149_999: [_log(149_999)]})
    logs = fetch_logs(eth, "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432", 0, 149_999, chunk=50_000)
    assert [l["blockNumber"] for l in logs] == [5, 100_000, 149_999]

def test_fetch_logs_halves_chunk_on_provider_range_error_without_duplicates():
    eth = StubEth({b: [_log(b)] for b in range(0, 200, 10)}, max_span=25)
    logs = fetch_logs(eth, "0xabc", 0, 199, chunk=200)
    assert len(logs) == 20
    assert len({(l["blockNumber"], l["logIndex"]) for l in logs}) == 20

def test_fetch_logs_gives_up_below_minimum_chunk():
    eth = StubEth({}, max_span=0)
    with pytest.raises(ValueError, match="chunk"):
        fetch_logs(eth, "0xabc", 0, 10, chunk=8)

def test_to_jsonable_round_trips():
    row = to_jsonable(_log(7), chain="base-mainnet", registry="identity")
    json.dumps(row)
    assert row["blockNumber"] == 7 and row["chain"] == "base-mainnet"
    assert row["transactionHash"] == "0x" + "ab" * 32
    assert row["topics"] == ["0x" + "cd" * 32]
