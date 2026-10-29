"""Phase 4 Part B driver: reputation descriptives per chain plus the 8004scan count check."""
import json
import sys
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.adversarial.reputation import descriptives
from src.collect.erc8004_decode import decode_events
from src.collect.scan8004 import count_check, newest_token_id
from src.common.manifest import append_entry
from src.common.provenance import write_result
from src.crosscheck.window import window_stats

ROOT = Path(__file__).resolve().parents[2]
CHAIN_IDS = {"ethereum-mainnet": 1, "base-mainnet": 8453, "bnb-mainnet": 56}
ETH_SLOT_SECONDS, WINDOW_DAYS = 12, 2.0  # the Ethereum window is cut from the full file (DEVIATIONS 2026-10-29)


def _window(raw: Path, chain: str, identity, feedback) -> tuple[dict, float, bool]:
    """(window bounds, days, windowed fetch?) from the collector's window file, or the last
    two days of a full-history file using the slot time, ending at the later of its two files."""
    wf = raw / f"{chain}_window.json"
    if wf.exists():
        w = json.loads(wf.read_text())
        days = (w["head_timestamp"] - w["from_timestamp"]) / 86400
        return w, days, True
    head = int(max(identity.blockNumber.max(), feedback.blockNumber.max()))
    return {"from_block": head - int(WINDOW_DAYS * 86400 / ETH_SLOT_SECONDS), "head": head}, WINDOW_DAYS, False


def main():
    raw, manifest, stamp = ROOT / "data/raw/erc8004", ROOT / "data/MANIFEST.md", date.today().isoformat()
    for chain, chain_id in CHAIN_IDS.items():
        ident_path, rep_path = raw / f"{chain}_identity.jsonl", raw / f"{chain}_reputation.jsonl"
        if not (ident_path.exists() and rep_path.exists()):
            print(f"{chain}: no raw files, skipped"); continue
        identity = decode_events(ident_path, ROOT / "data/abi/IdentityRegistry.json")
        feedback = decode_events(rep_path, ROOT / "data/abi/ReputationRegistry.json")
        desc = descriptives(identity, feedback)
        reg = identity[identity.event == "Registered"]
        max_id = int(reg.args.map(lambda a: int(a["agentId"])).max()) if len(reg) else -1
        w, days, windowed = _window(raw, chain, identity, feedback)
        window = window_stats(identity, feedback, w["from_block"], w["head"], days)
        try:
            scan = ROOT / "data/raw/8004scan"; scan.mkdir(parents=True, exist_ok=True)
            p = scan / f"{chain}_newest.json"
            if p.exists():  # one request per chain: a rerun reuses the pinned response and adds no MANIFEST entry
                api = json.loads(p.read_text())
            else:
                api = newest_token_id(chain_id)
                p.write_text(json.dumps(api, indent=2) + "\n")
                append_entry(manifest, name=f"8004scan newest agent {chain}", url=api["url"], method="src/crosscheck/run_chains.py",
                             row_count=1, file_path=p, license="public API, anonymous tier",
                             limitations="one request; newest token_id on the request date bounds our registration count; the total field is recorded, not used")
            check = count_check(len(reg), max_id, api, complete=not windowed)
        except RuntimeError as exc:
            check = {**count_check(len(reg), max_id, None), "error": str(exc)}
        out = ROOT / "results" / f"{stamp}_erc8004_descriptive_{chain}.json"
        write_result(out, "Phase 4 reputation descriptives", {"chain": chain, "windowed_fetch": windowed, "window": window,
                     "descriptives": desc, "count_check": check,
                     "n_identity_logs": int(len(identity)), "n_reputation_logs": int(len(feedback))}, {})
        fig, ax = plt.subplots(figsize=(5, 3.5))
        ax.hist(reg.blockNumber, bins=40); ax.set(xlabel="block", ylabel="registrations", title=f"ERC-8004 registrations ({chain}{', 2-day window' if windowed else ''})")
        fig.tight_layout(); fig.savefig(ROOT / "results" / f"{stamp}_erc8004_registrations_{chain}.png", dpi=150); plt.close(fig)
        print(chain, "count check:", check["status"], "| window:", {k: window[k] for k in ("days", "registrations", "feedback_events", "agents_with_feedback", "single_giver_share")}, out)


if __name__ == "__main__":
    sys.exit(main())
