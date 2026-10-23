"""Unified trace index: every parser's rows in one preregistered table."""
import pandas as pd

from src.collect.schema import TRACE_COLUMNS


def build_index(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows, columns=TRACE_COLUMNS)
    dupes = df[df.duplicated(subset=["source", "trace_id"], keep=False)]
    if not dupes.empty:
        ids = sorted(set(dupes["trace_id"]))[:5]
        raise ValueError(f"duplicate (source, trace_id) rows: {ids}")
    return df


def write_index(df: pd.DataFrame, path) -> None:
    df.to_csv(path, index=False)
