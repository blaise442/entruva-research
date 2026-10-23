"""Gate 2 data report rendered from the trace index. Markdown, numbers only
from the DataFrame; nothing here fetches or fabricates."""
import pandas as pd

from src.collect.schema import SOURCES

FLAGS = ["has_step_latency", "has_tool_calls", "has_retries", "has_errors"]


def data_report(df: pd.DataFrame) -> str:
    lines = ["# Data report", ""]
    if df.empty:
        lines.append("The trace index has no rows. No source has been collected yet.")
        return "\n".join(lines) + "\n"

    incidents = df[df["source"] == "incident"]
    bench = df[df["source"] != "incident"]
    obtained = sorted(df["source"].unique())
    lines.append(f"- sources obtained: {len(obtained)} of {len(SOURCES)} planned ({', '.join(obtained)})")
    lines.append(f"- Benchmark and on-chain rows: {len(bench)}")
    lines.append(f"- Incident rows (context weight, all failures): {len(incidents)}")
    lines.append(f"- distinct domains: {df['domain'].nunique()}, models: {df['model_id'].nunique()}, agents: {df['agent_id'].nunique()}")
    # trace_ids are prefixed per source, so the republication check keys on the
    # semantic identity (task_id, model_id) instead of the id string
    collisions = df.groupby(["task_id", "model_id"])["source"].nunique()
    lines.append(f"- cross-source (task_id, model_id) collisions: {int((collisions > 1).sum())}")

    lines += ["", "## Rows and label balance per source", ""]
    overall = df["outcome"].mean() * 100
    lines.append(f"- overall: {len(df)} rows, failure rate {overall:.1f}%")
    for src, g in df.groupby("source"):
        lines.append(f"- {src}: {len(g)} rows, failure rate {g['outcome'].mean() * 100:.1f}%")

    lines += ["", "## Availability flags (fraction of rows missing the signal)", ""]
    for flag in FLAGS:
        missing = (~df[flag].astype(bool)).mean() * 100
        lines.append(f"- {flag}: missing in {missing:.1f}% of rows")
    return "\n".join(lines) + "\n"
