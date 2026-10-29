"""Phase 4 Part A driver: one result file with the four checks and the verdict."""
import sys
from datetime import date
from pathlib import Path

import pandas as pd

from src.collect.erc8004_decode import decode_events
from src.common.provenance import write_result
from src.crosscheck.dataverse_eth import (check_agents_core, check_feedback, check_summary, check_transfers,
                                          feedback, registered, transfers, verdict)

ROOT = Path(__file__).resolve().parents[2]


def main():
    raw, dv = ROOT / "data/raw/erc8004", ROOT / "data/raw/dataverse_HJZW8Q"
    identity = decode_events(raw / "ethereum-mainnet_identity.jsonl", ROOT / "data/abi/IdentityRegistry.json")
    reputation = decode_events(raw / "ethereum-mainnet_reputation.jsonl", ROOT / "data/abi/ReputationRegistry.json")
    reg, tr, fb = registered(identity), transfers(identity), feedback(reputation)
    core = pd.read_csv(dv / "agents_core.csv")
    checks = {"agents_core": check_agents_core(core, reg, tr),
              "transfer_history": check_transfers(pd.read_csv(dv / "transfer_history.csv"), tr, set(core.agent_id.astype(int))),
              "agent_feedback_records": check_feedback(pd.read_csv(dv / "agent_feedback_records.csv"), fb),
              "agent_reputation_summary": check_summary(pd.read_csv(dv / "agent_reputation_summary.csv"), fb)}
    v = verdict(checks)
    out = ROOT / "results" / f"{date.today().isoformat()}_erc8004_crosscheck.json"
    write_result(out, "Phase 4 Ethereum cross-check (Dataverse HJZW8Q)",
                 {"verdict": v, "checks": checks, "dataverse_release": "2026-07-01", "our_fetch_date": "2026-10-25"}, {})
    print(v); print(out)


if __name__ == "__main__":
    sys.exit(main())
