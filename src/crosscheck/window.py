"""Window statistics for a chain fetched over its last few days only
(DEVIATIONS 2026-10-29): the same numbers are cut from the full Ethereum file."""
import pandas as pd


def window_stats(identity: pd.DataFrame, feedback: pd.DataFrame, from_block: int, head: int, days: float) -> dict:
    reg = identity[(identity.event == "Registered") & identity.blockNumber.between(from_block, head)]
    fb = feedback[(feedback.event == "NewFeedback") & feedback.blockNumber.between(from_block, head)]
    givers = fb.assign(agent=fb.args.map(lambda a: a["agentId"]), giver=fb.args.map(lambda a: a["clientAddress"].lower())) \
        .groupby("agent")["giver"].nunique() if len(fb) else pd.Series(dtype=int)
    return {"from_block": int(from_block), "head": int(head), "days": float(days),
            "registrations": int(len(reg)), "registrations_per_day": float(len(reg) / days),
            "feedback_events": int(len(fb)), "feedback_per_day": float(len(fb) / days),
            "agents_with_feedback": int(len(givers)),
            "single_giver_share": float((givers == 1).mean()) if len(givers) else None,
            "distinct_givers": int(fb.args.map(lambda a: a["clientAddress"].lower()).nunique()) if len(fb) else 0}
