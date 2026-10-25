"""Build data/processed/features.csv: one row per benchmark trace in the index,
trace_index columns plus telemetry features. Raises if any index row lacks features."""
import sys
from pathlib import Path

import pandas as pd

from src.features.extract import (FEATURE_COLUMNS, features_agentdojo, features_swe_bench,
                                  features_tau_bench, features_webarena)

ROOT = Path(__file__).resolve().parents[2]


def collect_features(raw: Path) -> pd.DataFrame:
    rows = []
    def add(source, feats):
        rows.extend({"source": source, "trace_id": k, **v} for k, v in feats.items())
    for p in sorted((raw / "tau-bench").glob("*.json")):
        add("tau-bench", features_tau_bench(p))
    for d in sorted((raw / "swe-bench").iterdir()):
        if d.is_dir():
            add("swe-bench", features_swe_bench(d))
    if (raw / "agentdojo" / "runs").exists():
        add("agentdojo", features_agentdojo(raw / "agentdojo" / "runs"))
    for z in sorted((raw / "webarena").rglob("*.zip")):
        add("webarena", features_webarena(z))
    return pd.DataFrame(rows, columns=["source", "trace_id"] + FEATURE_COLUMNS)


def check_no_feature_equals_outcome(merged: pd.DataFrame) -> None:
    """Raises if any numeric feature equals the outcome or is an affine image of it (|corr| == 1)."""
    y = merged["outcome"].astype(float)
    for c in [c for c in FEATURE_COLUMNS if c in merged]:
        x = pd.to_numeric(merged[c], errors="coerce")
        if x.notna().sum() > 1 and x.std() > 0 and y.std() > 0 and abs(x.corr(y)) > 1 - 1e-9:
            raise ValueError(f"feature {c} is a function of the outcome (|corr| = 1); leakage")


def build(index_path: Path, raw: Path, out_path: Path) -> pd.DataFrame:
    idx = pd.read_csv(index_path)
    idx = idx[idx["source"] != "incident"]
    feats = collect_features(raw)
    merged = idx.merge(feats, on=["source", "trace_id"], how="left", validate="one_to_one")
    missing = int(merged["n_tool_calls"].isna().sum())
    if missing:
        raise ValueError(f"{missing} index rows have no features; extractor and parser disagree")
    check_no_feature_equals_outcome(merged)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(out_path, index=False)
    return merged


if __name__ == "__main__":
    df = build(ROOT / "data/processed/trace_index.csv", ROOT / "data/raw", ROOT / "data/processed/features.csv")
    print(len(df), "rows written")
    sys.exit(0)
