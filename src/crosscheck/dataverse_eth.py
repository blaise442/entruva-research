"""Phase 4 Part A: row-level cross-check of the Ethereum ERC-8004 collection
against Dataverse HJZW8Q (DEVIATIONS 2026-10-28, cross-check rules). No tolerance."""
import pandas as pd

ZERO = "0x" + "00" * 20


def _hex(s: pd.Series) -> pd.Series:
    return s.astype(str).str.lower().str.replace("0x", "", n=1, regex=False)


def registered(identity: pd.DataFrame) -> pd.DataFrame:
    r = identity[identity.event == "Registered"]
    return pd.DataFrame({"agent_id": r.args.map(lambda a: int(a["agentId"])).to_numpy(), "block": r.blockNumber.to_numpy(),
                         "tx": _hex(r.transactionHash).to_numpy(), "owner": r.args.map(lambda a: a["owner"].lower()).to_numpy()})


def transfers(identity: pd.DataFrame) -> pd.DataFrame:
    t = identity[identity.event == "Transfer"]
    return pd.DataFrame({"agent_id": t.args.map(lambda a: int(a["tokenId"])).to_numpy(), "block": t.blockNumber.to_numpy(),
                         "log_index": t.logIndex.to_numpy(), "tx": _hex(t.transactionHash).to_numpy(),
                         "frm": t.args.map(lambda a: a["from"].lower()).to_numpy(), "to": t.args.map(lambda a: a["to"].lower()).to_numpy()}
                        ).sort_values(["block", "log_index"], kind="stable").reset_index(drop=True)


def feedback(reputation: pd.DataFrame) -> pd.DataFrame:
    f = reputation[reputation.event == "NewFeedback"]
    return pd.DataFrame({"agent_id": f.args.map(lambda a: int(a["agentId"])).to_numpy(),
                         "client": f.args.map(lambda a: a["clientAddress"].lower()).to_numpy(),
                         "index": f.args.map(lambda a: int(a["feedbackIndex"])).to_numpy()})


def _owners_at(tr: pd.DataFrame, block: int) -> pd.Series:
    return tr[tr.block <= block].groupby("agent_id")["to"].last()


def observation_block(core: pd.DataFrame, tr: pd.DataFrame) -> int | None:
    """Smallest block at which every agent we hold transfers for has the owner the
    dataset states; agents absent from our logs are judged in check_agents_core."""
    mine = tr[tr.agent_id.isin(set(core.agent_id.astype(int)))]
    want = core.set_index(core.agent_id.astype(int)).owner_wallet.str.lower()
    want = want[want.index.isin(set(mine.agent_id))]
    for b in sorted(set(mine.block.tolist()) | ({int(tr.block.max())} if len(tr) else set())):
        got = want.index.map(_owners_at(mine, b))
        if (got == want.to_numpy()).all():
            return int(b)
    return None


def check_agents_core(core: pd.DataFrame, reg: pd.DataFrame, tr: pd.DataFrame) -> dict:
    obs = observation_block(core, tr)
    m = core.assign(agent_id=core.agent_id.astype(int)).merge(reg, on="agent_id", how="left")
    # no block gives full agreement: compare at our latest block so only the real disagreements are listed
    owner_obs = m.agent_id.map(_owners_at(tr, obs if obs is not None else int(tr.block.max())))
    ok = (m.mint_block == m.block) & (_hex(m.mint_tx_hash) == m.tx) & (m.owner_wallet.str.lower() == owner_obs)
    ok = ok.fillna(False)
    return {"rows": int(len(m)), "agreeing": int(ok.sum()), "disagreeing": int((~ok).sum()),
            "keys": sorted(m.loc[~ok, "agent_id"].astype(int).tolist()), "observation_block": obs}


def check_transfers(dv_tr: pd.DataFrame, tr: pd.DataFrame, agent_ids: set) -> dict:
    """agent_ids: the dataset's core agents (0 to 9999); the window count covers all of them,
    so an agent whose transfers the dataset dropped entirely still shows up."""
    ours = set(zip(tr.agent_id.astype(int), tr.tx, tr.log_index.astype(int)))
    theirs = list(zip(dv_tr.agent_id.astype(int), _hex(dv_tr.tx_hash), dv_tr.log_index.astype(int)))
    missing = [list(k) for k in theirs if k not in ours]
    their_max = int(dv_tr.block_number.max()) if len(dv_tr) else None
    window = tr[(tr.frm != ZERO) & tr.agent_id.isin(agent_ids) & (tr.block <= their_max)] if len(dv_tr) else tr.iloc[0:0]
    return {"rows": len(theirs), "agreeing": len(theirs) - len(missing), "disagreeing": len(missing), "keys": missing,
            "ours_in_window": int(len(window)), "theirs": len(theirs), "their_max_block": their_max}


def check_feedback(dv_fb: pd.DataFrame, fb: pd.DataFrame) -> dict:
    ours = set(zip(fb.agent_id.astype(int), fb.client, fb["index"].astype(int)))
    theirs = list(zip(dv_fb.agent_id.astype(int), dv_fb.client_address.str.lower(), dv_fb.feedback_index.astype(int)))
    missing = [list(k) for k in theirs if k not in ours]
    return {"rows": len(theirs), "agreeing": len(theirs) - len(missing), "disagreeing": len(missing), "keys": missing}


def check_summary(dv_rs: pd.DataFrame, fb: pd.DataFrame) -> dict:
    ours = dv_rs.agent_id.astype(int).map(fb.groupby("agent_id").size()).fillna(0).astype(int)
    theirs = dv_rs.feedback_count_total.astype(int)
    bad = theirs > ours
    return {"rows": int(len(dv_rs)), "at_most_ours": int((~bad).sum()), "equal": int((theirs == ours).sum()),
            "disagreeing": int(bad.sum()), "keys": sorted(dv_rs.loc[bad, "agent_id"].astype(int).tolist())}


def verdict(checks: dict) -> str:
    failing = [name for name, c in checks.items() if c["disagreeing"] != 0
               or (name == "transfer_history" and c["ours_in_window"] != c["theirs"])]
    return "matches row for row" if not failing else "differs: " + ", ".join(failing)
