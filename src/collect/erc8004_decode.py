"""Decode raw ERC-8004 logs with the pinned contract ABI (data/abi/, commit in
data/MANIFEST.md). Topic hashes are computed from the ABI's event signatures,
never typed in; a log whose topic0 matches no event is kept as unknown:<topic0>."""
import json
from pathlib import Path

import pandas as pd
from eth_abi import decode
from web3 import Web3


def _norm(topic: str) -> str:
    return topic.lower().removeprefix("0x")


def _events(abi: list[dict]) -> dict[str, dict]:
    out = {}
    for e in abi:
        if e.get("type") == "event":
            sig = f'{e["name"]}({",".join(i["type"] for i in e["inputs"])})'
            out[_norm(Web3.keccak(text=sig).hex())] = e
    return out


def _jsonable(v):
    return "0x" + v.hex() if isinstance(v, (bytes, bytearray)) else v


def _decode(log: dict, ev: dict) -> dict:
    indexed = [i for i in ev["inputs"] if i["indexed"]]
    plain = [i for i in ev["inputs"] if not i["indexed"]]
    args = {}
    for inp, topic in zip(indexed, log["topics"][1:]):
        raw = bytes.fromhex(topic[2:])
        args[inp["name"]] = topic if inp["type"] in ("string", "bytes") else _jsonable(decode([inp["type"]], raw)[0])
    if plain:
        vals = decode([i["type"] for i in plain], bytes.fromhex(log["data"][2:]))
        args.update({i["name"]: _jsonable(v) for i, v in zip(plain, vals)})
    return args


def decode_events(jsonl_path: Path, abi_path: Path, keep: set[str] | None = None) -> pd.DataFrame:
    """keep: event names to return; other logs are skipped before decoding so a
    multi-gigabyte file can be reduced to the rows a caller needs."""
    events = _events(json.loads(Path(abi_path).read_text()))
    rows = []
    with open(jsonl_path) as f:
        for line in f:
            log = json.loads(line)
            t0 = log["topics"][0] if log["topics"] else ""
            ev = events.get(_norm(t0))
            if keep is not None and (ev is None or ev["name"] not in keep):
                continue
            rows.append({"blockNumber": log["blockNumber"], "logIndex": log["logIndex"], "transactionHash": log["transactionHash"],
                         "event": ev["name"] if ev else f"unknown:{t0}", "args": _decode(log, ev) if ev else {}})
    return pd.DataFrame(rows, columns=["blockNumber", "logIndex", "transactionHash", "event", "args"])
