"""Part C driver: decode the ERC-8004 events, describe the reputation layer, price
its attacks from sampled receipts, and record every fetch in data/MANIFEST.md."""
import sys
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.adversarial.reputation import attack_costs, descriptives, eth_usd_daily, gas_sample
from src.collect.erc8004 import _rpc_url
from src.collect.erc8004_decode import decode_events
from src.common.manifest import append_entry
from src.common.provenance import write_result

ROOT = Path(__file__).resolve().parents[2]
ABI_COMMIT = "b9e466c250744a7e06b13dff9d3c2844ed64f825"
ABI_URL = f"https://github.com/erc-8004/erc-8004-contracts/tree/{ABI_COMMIT}/abis"
GAS_N, SEED = 200, 20261017


def main():
    raw, manifest = ROOT / "data/raw/erc8004", ROOT / "data/MANIFEST.md"
    identity = decode_events(raw / "ethereum-mainnet_identity.jsonl", ROOT / "data/abi/IdentityRegistry.json")
    feedback = decode_events(raw / "ethereum-mainnet_reputation.jsonl", ROOT / "data/abi/ReputationRegistry.json")
    desc = descriptives(identity, feedback)
    desc["event_counts"] = {"identity": identity.event.value_counts().to_dict(), "reputation": feedback.event.value_counts().to_dict()}
    url = _rpc_url()
    if not url:
        raise SystemExit("RPC_URL not set; the gas sample needs an endpoint")
    from web3 import Web3
    w3 = Web3(Web3.HTTPProvider(url, request_kwargs={"timeout": 60}))
    gas = gas_sample(pd.concat([identity, feedback]), w3, GAS_N, SEED)
    gas.to_csv(raw / "gas_sample.csv", index=False)
    usd = eth_usd_daily(gas.block_day.tolist())
    usd.to_csv(raw / "eth_usd_daily.csv", index=False)
    median_fb = int(round(desc["feedback_per_agent"]["median"])) if desc["feedback_per_agent"] else 1
    costs = attack_costs(gas, usd, median_feedback=max(1, median_fb))
    stamp = date.today().isoformat()
    out = ROOT / "results" / f"{stamp}_erc8004_descriptive.json"
    write_result(out, "S3 reputation layer (descriptive)", {"descriptives": desc, "attack_costs": costs,
                 "eth_usd": {"source": "Coinbase public spot by date", "days": int(len(usd)), "min": float(usd.usd.min()), "max": float(usd.usd.max())}},
                 {"gas_sample_seed": SEED})
    for name, path, rows, lim in (
        ("erc8004 contract ABI pin", ROOT / "data/abi/IdentityRegistry.json", 0,
         f"IdentityRegistry.json and ReputationRegistry.json copied from commit {ABI_COMMIT}; used only to decode events"),
        ("erc8004 gas sample (receipts)", raw / "gas_sample.csv", len(gas),
         f"{GAS_N} seeded transactions per event type (Registered, NewFeedback) via eth_getTransactionReceipt on the keyless public endpoint https://rpc.mevblocker.io"),
        ("erc8004 ETH-USD daily spot", raw / "eth_usd_daily.csv", len(usd),
         "Coinbase public spot price by date (api.coinbase.com/v2/prices/ETH-USD/spot?date=), one row per block day in the gas sample; no key")):
        append_entry(manifest, name=name, url=ABI_URL if "ABI" in name else ("https://rpc.mevblocker.io" if "gas" in name else "https://api.coinbase.com/v2/prices/ETH-USD/spot"),
                     method="src/adversarial/run_reputation.py", row_count=rows, file_path=path, license="public data", limitations=lim)
    reg = identity[identity.event == "Registered"]
    fig, ax = plt.subplots(figsize=(5, 3.5))
    ax.hist(reg.blockNumber, bins=40); ax.set(xlabel="block", ylabel="registrations", title="ERC-8004 registrations (Ethereum mainnet)")
    fig.tight_layout(); fig.savefig(ROOT / "results" / f"{stamp}_erc8004_registrations.png", dpi=150); plt.close(fig)
    fb = feedback[feedback.event == "NewFeedback"]
    givers = fb.assign(agent=fb.args.map(lambda a: a["agentId"]), giver=fb.args.map(lambda a: a["clientAddress"])).groupby("agent")["giver"].nunique()
    fig, ax = plt.subplots(figsize=(5, 3.5))
    ax.hist(givers, bins=range(1, int(givers.max()) + 2), log=True); ax.set(xlabel="distinct feedback givers per agent", ylabel="agents (log)", title="Feedback concentration")
    fig.tight_layout(); fig.savefig(ROOT / "results" / f"{stamp}_erc8004_givers.png", dpi=150); plt.close(fig)
    print(out)


if __name__ == "__main__":
    sys.exit(main())
