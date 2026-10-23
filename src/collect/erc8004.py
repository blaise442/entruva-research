"""ERC-8004 registry event collector.

Reads RPC_URL from research/.env or the environment. Raw logs go to
data/raw/erc8004/<chain>_<registry>.jsonl; the endpoint value is never written
anywhere (the MANIFEST url field is the public source of the addresses).
"""
import json
import os
import sys
from pathlib import Path

from src.collect.addresses import REGISTRIES
from src.common.manifest import append_entry

MIN_CHUNK = 1

# Chain ids verified against chainlist.org entries for the two chains with
# published registry addresses; anything else must fail, never be mislabeled.
CHAIN_IDS = {1: "ethereum-mainnet", 8453: "base-mainnet"}

def _chain_name(chain_id: int) -> str:
    if chain_id not in CHAIN_IDS:
        raise ValueError(f"RPC endpoint reports chain_id {chain_id}, which has no "
                         f"published ERC-8004 registry addresses; refusing to label its logs")
    return CHAIN_IDS[chain_id]

def fetch_logs(eth, address: str, from_block: int, to_block: int, chunk: int = 50_000) -> list[dict]:
    """Chunked eth_getLogs. On a provider range error the chunk is halved and the
    same range retried, so every log is returned exactly once."""
    logs: list[dict] = []
    lo = from_block
    while lo <= to_block:
        hi = min(lo + chunk - 1, to_block)
        try:
            logs.extend(eth.get_logs({"address": address, "fromBlock": lo, "toBlock": hi}))
        except Exception:
            if chunk <= MIN_CHUNK:
                raise ValueError(f"provider rejects even chunk={chunk}; cannot fetch {lo}..{hi}")
            chunk = max(MIN_CHUNK, chunk // 2)
            continue
        lo = hi + 1
    return logs

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
    url = _rpc_url()
    if not url:
        print("erc8004: RPC_URL not set; skipping. The gap is recorded in data/MANIFEST.md.")
        return 1
    from web3 import Web3
    w3 = Web3(Web3.HTTPProvider(url))
    out_dir.mkdir(parents=True, exist_ok=True)
    head = w3.eth.block_number
    endpoint_chain = _chain_name(w3.eth.chain_id)  # raises on any unmapped chain
    for chain, regs in REGISTRIES.items():
        # shortcut: one RPC endpoint serves one chain; fetch only the chain it reports,
        # upgrade to per-chain endpoints when a second RPC is provided.
        if chain != endpoint_chain:
            continue
        for registry, address in regs.items():
            logs = fetch_logs(w3.eth, address, 0, head)
            rows = [to_jsonable(dict(l), chain=chain, registry=registry) for l in logs]
            path = out_dir / f"{chain}_{registry}.jsonl"
            path.write_text("".join(json.dumps(r) + "\n" for r in rows))
            append_entry(manifest_path, name=f"erc8004 {chain} {registry} registry events",
                         url="https://github.com/erc-8004/erc-8004-contracts (address source); events via eth_getLogs",
                         method="src/collect/erc8004.py", row_count=len(rows), file_path=path,
                         license="public blockchain data",
                         limitations="fetched via a private RPC endpoint (not recorded); ValidationRegistry has no published curated address")
    return 0

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    sys.exit(run(root / "data" / "raw" / "erc8004", root / "data" / "MANIFEST.md"))
