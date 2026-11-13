"""ERC-8004 registry event collector.

Reads RPC_URL from .env at the repository root or the environment, or PUBLIC_RPC_URL for a
keyless public endpoint. Raw logs go to data/raw/erc8004/<chain>_<registry>.jsonl;
a private endpoint value is never written anywhere (the MANIFEST url field is the
public source of the addresses); a public one is recorded in the MANIFEST limitations.
"""
import json
import os
import sys
import time
from pathlib import Path

from src.collect.addresses import REGISTRIES
from src.common.manifest import append_entry

MIN_CHUNK = 1
MAX_429_RETRIES = 8
# publicnode blocks a client that sends a burst of calls (about ten in two seconds)
# with 403 for minutes, and every retry during the block extends it: pace every
# call, and on a block wait a fixed long time rather than backing off from 2 s.
CALL_GAP = 0.5
BAN_WAIT = 120


def _is_rate_limit(exc: Exception) -> bool:
    # 429 is the usual throttle code; publicnode answers a burst with 403 Forbidden
    resp = getattr(exc, "response", None)
    return getattr(resp, "status_code", None) in (429, 403)


def _throttled(call):
    """Run one paced RPC call, waiting and retrying while the provider throttles it."""
    for _ in range(MAX_429_RETRIES):
        time.sleep(CALL_GAP)
        try:
            return call()
        except Exception as exc:
            if not _is_rate_limit(exc):
                raise
            time.sleep(BAN_WAIT)
    time.sleep(CALL_GAP)
    return call()

# Chain ids verified against chainlist.org entries for the chains with
# published registry addresses; anything else must fail, never be mislabeled.
CHAIN_IDS = {1: "ethereum-mainnet", 8453: "base-mainnet", 56: "bnb-mainnet"}

def _chain_name(chain_id: int) -> str:
    if chain_id not in CHAIN_IDS:
        raise ValueError(f"RPC endpoint reports chain_id {chain_id}, which has no "
                         f"published ERC-8004 registry addresses; refusing to label its logs")
    return CHAIN_IDS[chain_id]

def fetch_logs(eth, address: str, from_block: int, to_block: int, chunk: int = 10_000) -> list[dict]:
    """Chunked eth_getLogs, at most 10,000 blocks per call: a keyed provider answered
    a wider BNB range with an incomplete list and no error (measured 2026-11-02).
    On a provider range error the chunk is halved and the
    same range retried, so every log is returned exactly once; after each success
    it doubles back toward the starting chunk so a dense region does not slow the
    sparse remainder."""
    logs: list[dict] = []
    lo = from_block
    max_chunk = chunk
    while lo <= to_block:
        hi = min(lo + chunk - 1, to_block)
        try:  # throttling is retried on the same window inside _throttled; any other error halves the window
            logs.extend(_throttled(lambda: eth.get_logs({"address": address, "fromBlock": lo, "toBlock": hi})))
        except Exception as exc:
            if _is_rate_limit(exc):
                raise
            if chunk <= MIN_CHUNK:
                raise ValueError(f"provider rejects even chunk={chunk}; cannot fetch {lo}..{hi}")
            chunk = max(MIN_CHUNK, chunk // 2)
            continue
        lo = hi + 1
        chunk = min(chunk * 2, max_chunk)
    return logs


def first_block_with_code(eth, address: str, head: int) -> int:
    """Lowest block at which the address has code (binary search on eth_getCode),
    so the log scan skips the empty blocks before deployment."""
    lo, hi = 0, head
    while lo < hi:
        mid = (lo + hi) // 2
        if _throttled(lambda: eth.get_code(address, block_identifier=mid)):
            hi = mid
        else:
            lo = mid + 1
    return lo

def _hex(v) -> str:
    return v if isinstance(v, str) else "0x" + bytes(v).hex()

def to_jsonable(log: dict, *, chain: str, registry: str) -> dict:
    return {
        "chain": chain,
        "registry": registry,
        "blockNumber": int(log["blockNumber"]),
        "logIndex": int(log["logIndex"]),
        "transactionHash": _hex(log["transactionHash"]),
        "address": log["address"],
        "topics": [_hex(t) for t in log["topics"]],
        "data": _hex(log["data"]),
    }

def _rpc_url() -> str | None:
    if os.environ.get("RPC_URL"):
        return os.environ["RPC_URL"]
    env = Path(__file__).resolve().parents[2] / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if line.startswith("RPC_URL=") and line.split("=", 1)[1].strip():
                return line.split("=", 1)[1].strip()
    return None

def run(out_dir: Path, manifest_path: Path) -> int:
    public = os.environ.get("PUBLIC_RPC_URL")
    url = public or _rpc_url()
    if not url:
        print("erc8004: RPC_URL not set; skipping. The gap is recorded in data/MANIFEST.md.")
        return 1
    from web3 import Web3
    w3 = Web3(Web3.HTTPProvider(url))
    out_dir.mkdir(parents=True, exist_ok=True)
    head = w3.eth.block_number
    endpoint_chain = _chain_name(w3.eth.chain_id)  # raises on any unmapped chain
    # WINDOW_BLOCKS: fetch only the last N blocks (a keyless endpoint that serves no
    # older history); the exact span is recorded from block timestamps.
    window = int(os.environ["WINDOW_BLOCKS"]) if os.environ.get("WINDOW_BLOCKS") else None
    for chain, regs in REGISTRIES.items():
        # shortcut: one RPC endpoint serves one chain; fetch only the chain it reports,
        # upgrade to per-chain endpoints when a second RPC is provided.
        if chain != endpoint_chain:
            continue
        wf = out_dir / f"{chain}_window.json"
        if window is None:
            wf.unlink(missing_ok=True)  # a stale file would mark a full-history fetch as windowed
        else:
            start_w = head - window
            # raw header read: w3.eth.get_block rejects proof-of-authority headers (BNB Smart Chain)
            ts = [_throttled(lambda b=b: int(w3.provider.make_request("eth_getBlockByNumber", [hex(b), False])["result"]["timestamp"], 16)) for b in (start_w, head)]
            wf.write_text(json.dumps(
                {"from_block": start_w, "head": head, "from_timestamp": ts[0], "head_timestamp": ts[1]}) + "\n")
        for registry, address in regs.items():
            start = start_w if window is not None else first_block_with_code(w3.eth, address, head)
            print(f"erc8004: {chain} {registry} deployed by block {start}; scanning {start}..{head}")
            logs = fetch_logs(w3.eth, address, start, head)
            rows = [to_jsonable(dict(l), chain=chain, registry=registry) for l in logs]
            path = out_dir / f"{chain}_{registry}.jsonl"
            path.write_text("".join(json.dumps(r) + "\n" for r in rows))
            append_entry(manifest_path, name=f"erc8004 {chain} {registry} registry events",
                         url="https://github.com/erc-8004/erc-8004-contracts (address source); events via eth_getLogs",
                         method="src/collect/erc8004.py", row_count=len(rows), file_path=path,
                         license="public blockchain data",
                         limitations=(f"fetched from the keyless public endpoint {public}" if public else "fetched via a private RPC endpoint (not recorded)")
                         + (f"; window of {window} blocks ({start}..{head}) because the endpoint serves no older history" if window is not None else "")
                         + "; ValidationRegistry has no published curated address")
    return 0

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    sys.exit(run(root / "data" / "raw" / "erc8004", root / "data" / "MANIFEST.md"))
