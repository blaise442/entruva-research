import json
from pathlib import Path

from web3 import Web3

from src.collect.erc8004_decode import decode_events

ABI_IDENTITY = Path(__file__).resolve().parents[1] / "data/abi/IdentityRegistry.json"


def _topic(sig):
    h = Web3.keccak(text=sig).hex()
    return h if h.startswith("0x") else "0x" + h  # raw logs carry 0x-prefixed topics


def _addr_topic(a):
    return "0x" + a[2:].rjust(64, "0")


def test_decode_events_names_known_events_and_keeps_unknown(tmp_path):
    transfer = {"chain": "ethereum-mainnet", "registry": "identity", "blockNumber": 5, "logIndex": 0, "transactionHash": "0xaa",
                "address": "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432",
                "topics": [_topic("Transfer(address,address,uint256)"), _addr_topic("0x" + "11" * 20), _addr_topic("0x" + "22" * 20),
                           "0x" + "7".rjust(64, "0")], "data": "0x"}
    unknown = {**transfer, "logIndex": 1, "topics": ["0x" + "ab" * 32], "data": "0x"}
    p = tmp_path / "x.jsonl"
    p.write_text(json.dumps(transfer) + "\n" + json.dumps(unknown) + "\n")
    df = decode_events(p, ABI_IDENTITY)
    assert list(df.event) == ["Transfer", "unknown:0x" + "ab" * 32]
    assert df.args.iloc[0]["tokenId"] == 7 and df.args.iloc[0]["to"].lower() == "0x" + "22" * 20
    assert list(df.columns) == ["blockNumber", "logIndex", "transactionHash", "event", "args"]
