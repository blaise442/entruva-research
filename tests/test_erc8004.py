import json
from pathlib import Path

import pytest
from src.collect.erc8004 import _chain_name, fetch_logs, run, to_jsonable


@pytest.fixture(autouse=True)
def no_pacing(monkeypatch):
    """Stubs answer instantly; the real pacing is for public endpoints."""
    import src.collect.erc8004 as mod
    monkeypatch.setattr(mod, "CALL_GAP", 0.0)

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

class ResultCappedEth:
    """get_logs stub that rejects any window holding more than max_results logs,
    like a provider's 10k-result cap: dense regions force small chunks."""
    def __init__(self, logs_by_block: dict[int, list[dict]], max_results: int):
        self.logs_by_block = logs_by_block
        self.max_results = max_results
        self.calls = 0

    def get_logs(self, params):
        self.calls += 1
        out = [l for b in range(params["fromBlock"], params["toBlock"] + 1) for l in self.logs_by_block.get(b, [])]
        if len(out) > self.max_results:
            raise ValueError("query returned more than 10000 results")
        return out

def test_fetch_logs_grows_chunk_back_after_a_dense_region():
    dense = {b: [_log(b, i) for i in range(10)] for b in range(50)}  # 500 logs in 50 blocks, then nothing
    eth = ResultCappedEth(dense, max_results=100)
    logs = fetch_logs(eth, "0xabc", 0, 100_000, chunk=50_000)
    assert len(logs) == 500
    assert eth.calls < 100  # a chunk stuck at ~6 blocks would need ~16k calls for the empty tail

def test_fetch_logs_gives_up_below_minimum_chunk():
    eth = StubEth({}, max_span=0)
    with pytest.raises(ValueError, match="chunk"):
        fetch_logs(eth, "0xabc", 0, 10, chunk=8)

def test_chain_name_maps_known_ids_and_rejects_unknown_chains():
    assert _chain_name(1) == "ethereum-mainnet"
    assert _chain_name(8453) == "base-mainnet"
    with pytest.raises(ValueError, match="11155111"):
        _chain_name(11155111)  # a Sepolia endpoint must never be written as Base

class _StubEth:
    block_number = 5
    chain_id = 1
    def get_logs(self, params):
        return [_log(3)]
    def get_code(self, address, block_identifier):
        return b"\x60"
    def get_block(self, n):
        raise AssertionError("block headers are read raw: get_block fails on proof-of-authority chains")


class _StubProvider:
    """eth_getBlockByNumber answered raw, as a POA chain's header would need."""
    @staticmethod
    def make_request(method, params):
        assert method == "eth_getBlockByNumber"
        return {"result": {"timestamp": hex(1_000_000 + 12 * int(params[0], 16)), "extraData": "0x" + "00" * 280}}

class _StubWeb3:
    @staticmethod
    def HTTPProvider(url):
        return url
    def __init__(self, provider):
        self.eth = _StubEth()
        self.provider = _StubProvider()

def test_run_never_writes_the_rpc_secret_anywhere(tmp_path, monkeypatch):
    import web3
    secret = "http://secret.example/abc123"
    monkeypatch.setenv("RPC_URL", secret)
    monkeypatch.setattr(web3, "Web3", _StubWeb3)
    manifest = tmp_path / "MANIFEST.md"
    manifest.write_text("# manifest\n")
    out = tmp_path / "erc8004"
    assert run(out, manifest) == 0
    texts = [manifest.read_text()] + [p.read_text() for p in out.rglob("*") if p.is_file()]
    assert texts[1:], "run() wrote no output files"
    for t in texts:
        assert secret not in t and "secret.example" not in t

def test_to_jsonable_round_trips():
    row = to_jsonable(_log(7), chain="base-mainnet", registry="identity")
    json.dumps(row)
    assert row["blockNumber"] == 7 and row["chain"] == "base-mainnet"
    assert row["transactionHash"] == "0x" + "ab" * 32
    assert row["topics"] == ["0x" + "cd" * 32]


class RateLimitedEth(StubEth):
    """First `n_429` calls raise HTTP 429; afterwards behaves like StubEth."""
    def __init__(self, logs_by_block, n_429, status=429):
        super().__init__(logs_by_block)
        self.n_429 = n_429
        self.status = status
        self.spans = []

    def get_logs(self, params):
        self.spans.append(params["toBlock"] - params["fromBlock"] + 1)
        if self.n_429 > 0:
            self.n_429 -= 1
            import requests
            resp = requests.Response(); resp.status_code = self.status
            raise requests.exceptions.HTTPError("429 Client Error: Too Many Requests", response=resp)
        return super().get_logs(params)


def test_fetch_logs_retries_a_429_on_the_same_window_without_halving(monkeypatch):
    import src.collect.erc8004 as mod
    monkeypatch.setattr(mod.time, "sleep", lambda s: None)
    eth = RateLimitedEth({7: [_log(7)]}, n_429=3)
    logs = fetch_logs(eth, "0xabc", 0, 99, chunk=100)
    assert [l["blockNumber"] for l in logs] == [7]
    assert eth.spans == [100, 100, 100, 100]


def test_first_block_with_code_binary_searches_the_deployment_block():
    from src.collect.erc8004 import first_block_with_code

    class CodeEth:
        def __init__(self, deployed_at):
            self.deployed_at, self.calls = deployed_at, 0
        def get_code(self, address, block_identifier):
            self.calls += 1
            return b"\x60\x80" if block_identifier >= self.deployed_at else b""

    eth = CodeEth(23_456_789)
    assert first_block_with_code(eth, "0xabc", head=24_000_000) == 23_456_789
    assert eth.calls < 40
    assert first_block_with_code(CodeEth(0), "0xabc", head=10) == 0


def test_chain_name_maps_bnb_smart_chain():
    from src.collect.addresses import REGISTRIES
    assert _chain_name(56) == "bnb-mainnet"
    assert REGISTRIES["bnb-mainnet"] == REGISTRIES["ethereum-mainnet"]


def test_chain_name_refuses_unmapped_chain_even_when_public(monkeypatch):
    monkeypatch.setenv("PUBLIC_RPC_URL", "https://example-rpc.publicnode.com")
    with pytest.raises(ValueError):
        _chain_name(10)


def test_run_records_a_public_endpoint_in_the_manifest(tmp_path, monkeypatch):
    import web3
    monkeypatch.delenv("RPC_URL", raising=False)
    monkeypatch.setenv("PUBLIC_RPC_URL", "https://base-rpc.publicnode.com")
    monkeypatch.setattr(web3, "Web3", _StubWeb3)
    manifest = tmp_path / "MANIFEST.md"
    manifest.write_text("# manifest\n")
    assert run(tmp_path / "erc8004", manifest) == 0
    text = manifest.read_text()
    assert "keyless public endpoint https://base-rpc.publicnode.com" in text and "private RPC endpoint" not in text


def test_fetch_logs_treats_a_403_as_throttling(monkeypatch):
    """publicnode answers a burst with 403 Forbidden rather than 429."""
    import src.collect.erc8004 as mod
    monkeypatch.setattr(mod.time, "sleep", lambda s: None)
    eth = RateLimitedEth({7: [_log(7)]}, n_429=2, status=403)
    logs = fetch_logs(eth, "0xabc", 0, 99, chunk=100)
    assert [l["blockNumber"] for l in logs] == [7]
    assert eth.spans == [100, 100, 100]


class ThrottledCodeEth:
    """get_code raises HTTP 403 for the first n calls, then reports code from block 40 on."""
    def __init__(self, n):
        self.n = n

    def get_code(self, address, block_identifier):
        if self.n > 0:
            self.n -= 1
            import requests
            resp = requests.Response(); resp.status_code = 403
            raise requests.HTTPError("403", response=resp)
        return b"\x60" if block_identifier >= 40 else b""


def test_first_block_with_code_retries_on_throttling(monkeypatch):
    import src.collect.erc8004 as mod
    from src.collect.erc8004 import first_block_with_code
    monkeypatch.setattr(mod.time, "sleep", lambda s: None)
    assert first_block_with_code(ThrottledCodeEth(3), "0xabc", 100) == 40


def test_rpc_calls_are_paced(monkeypatch):
    import src.collect.erc8004 as mod
    slept = []
    monkeypatch.setattr(mod.time, "sleep", slept.append)
    eth = StubEth({5: [_log(5)], 60: [_log(60)], 140: [_log(140)]})
    fetch_logs(eth, "0xabc", 0, 149, chunk=50)
    assert slept.count(mod.CALL_GAP) >= 3


def test_throttling_waits_a_fixed_long_time_instead_of_hammering(monkeypatch):
    import src.collect.erc8004 as mod
    from src.collect.erc8004 import first_block_with_code
    slept = []
    monkeypatch.setattr(mod.time, "sleep", slept.append)
    assert first_block_with_code(ThrottledCodeEth(3), "0xabc", 100) == 40
    assert slept.count(mod.BAN_WAIT) == 3


def test_run_honours_a_block_window_and_records_it(tmp_path, monkeypatch):
    import web3
    monkeypatch.delenv("RPC_URL", raising=False)
    monkeypatch.setenv("PUBLIC_RPC_URL", "https://base-rpc.publicnode.com")
    monkeypatch.setenv("WINDOW_BLOCKS", "3")
    monkeypatch.setattr(web3, "Web3", _StubWeb3)
    manifest = tmp_path / "MANIFEST.md"
    manifest.write_text("# manifest\n")
    assert run(tmp_path / "erc8004", manifest) == 0
    w = json.loads((tmp_path / "erc8004" / "ethereum-mainnet_window.json").read_text())
    assert w == {"from_block": 2, "head": 5, "from_timestamp": 1_000_024, "head_timestamp": 1_000_060}
    assert "window of 3 blocks" in manifest.read_text()
