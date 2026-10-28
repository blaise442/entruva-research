"""The ERC-8004 reputation layer: descriptives and on-chain attack costs (design
Part C). Gas is read from real receipts; dollars use the ETH-USD daily spot on the
block day from Coinbase's public endpoint; nothing is filled from memory."""
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import requests

MAX_429_RETRIES = 8
PACE_S = 0.2  # keyless public endpoint: keep well under its burst limit
BLOCKS_PER_WEEK = 50_400


def _with_backoff(fn):
    """Call fn(); on HTTP 429 wait 2, 4, ... 60 s and retry, as the collector does."""
    for attempt in range(MAX_429_RETRIES + 1):
        try:
            return fn()
        except requests.HTTPError as exc:
            if getattr(getattr(exc, "response", None), "status_code", None) != 429 or attempt == MAX_429_RETRIES:
                raise
            time.sleep(min(2 ** (attempt + 1), 60))  # 12 s blocks, approximate week bins
COINBASE = "https://api.coinbase.com/v2/prices/ETH-USD/spot?date={day}"


def _q(s: pd.Series) -> dict:
    return {"min": float(s.min()), "p25": float(s.quantile(0.25)), "median": float(s.median()),
            "p75": float(s.quantile(0.75)), "max": float(s.max()), "mean": float(s.mean())}


def descriptives(identity: pd.DataFrame, feedback: pd.DataFrame) -> dict:
    reg = identity[identity.event == "Registered"]
    fb = feedback[feedback.event == "NewFeedback"]
    fb_agent = fb.args.map(lambda a: a["agentId"])
    fb_giver = fb.args.map(lambda a: a["clientAddress"].lower())
    owners = set(reg.args.map(lambda a: a["owner"].lower()))
    per_agent = fb.assign(agent=fb_agent, giver=fb_giver).groupby("agent")
    givers = per_agent["giver"].nunique()
    counts = per_agent.size()
    bins = (reg.blockNumber - reg.blockNumber.min()) // BLOCKS_PER_WEEK if len(reg) else pd.Series(dtype=int)
    return {"n_registered": int(len(reg)), "n_feedback": int(len(fb)),
            "registrations_per_week_bin": {int(k): int(v) for k, v in bins.value_counts().sort_index().items()},
            "agents_with_feedback": int(len(counts)),
            "feedback_per_agent": _q(counts) if len(counts) else None,
            "givers_per_agent": _q(givers) if len(givers) else None,
            "agents_with_single_giver": int((givers == 1).sum()),
            "share_feedback_from_registrant_wallets": float(fb_giver.isin(owners).mean()) if len(fb) else None,
            "n_distinct_givers": int(fb_giver.nunique())}


def gas_sample(events: pd.DataFrame, w3, n: int, seed: int, names=("Registered", "NewFeedback")) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows, days = [], {}
    for name in names:
        hashes = events.loc[events.event == name, "transactionHash"].drop_duplicates().to_numpy()
        for h in rng.choice(hashes, size=min(n, len(hashes)), replace=False):
            time.sleep(PACE_S)
            r = _with_backoff(lambda: w3.eth.get_transaction_receipt(h))
            b = r["blockNumber"]
            if b not in days:
                ts = _with_backoff(lambda: w3.eth.get_block(b)["timestamp"])
                days[b] = datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat()
            rows.append({"event": name, "transactionHash": h, "gasUsed": int(r["gasUsed"]),
                         "effectiveGasPrice_wei": int(r["effectiveGasPrice"]), "block_day": days[b]})
    return pd.DataFrame(rows)


def eth_usd_daily(days: list[str]) -> pd.DataFrame:
    rows = []
    for day in sorted(set(days)):
        resp = requests.get(COINBASE.format(day=day), timeout=30)
        if resp.status_code != 200:
            raise RuntimeError(f"ETH-USD price fetch failed for {day}: HTTP {resp.status_code}")
        rows.append({"day": day, "usd": float(resp.json()["data"]["amount"])})
    return pd.DataFrame(rows, columns=["day", "usd"])


def attack_costs(gas: pd.DataFrame, usd: pd.DataFrame | None, median_feedback: int, ring_k: int = 5) -> dict:
    g = gas.assign(eth=gas.gasUsed * gas.effectiveGasPrice_wei / 1e18)
    med = {name: float(g.loc[g.event == name, "eth"].median()) for name in ("Registered", "NewFeedback")}
    reg, fb = med["Registered"], med["NewFeedback"]
    out = {"registration_eth": reg, "feedback_eth": fb, "sybil_eth": median_feedback * (reg + fb),
           "collusion_eth": ring_k * (ring_k - 1) * fb, "whitewash_eth": reg,
           "median_feedback": median_feedback, "ring_k": ring_k, "n_gas_sampled": int(len(gas))}
    if usd is not None:
        g = g.merge(usd, left_on="block_day", right_on="day", how="left")
        g["usd_cost"] = g.eth * g.usd
        reg_u = float(g.loc[g.event == "Registered", "usd_cost"].median())
        fb_u = float(g.loc[g.event == "NewFeedback", "usd_cost"].median())
        out.update({"registration_usd": reg_u, "feedback_usd": fb_u, "sybil_usd": median_feedback * (reg_u + fb_u),
                    "collusion_usd": ring_k * (ring_k - 1) * fb_u, "whitewash_usd": reg_u})
    return out
