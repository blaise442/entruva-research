"""Regenerates every result in results/ from data/raw. Fails loudly while no data exists."""
import json
import sys
from datetime import date
from pathlib import Path

RESEARCH = Path(__file__).resolve().parents[1]
RAW = RESEARCH / "data" / "raw"


def collect_all(raw_root: Path) -> list[dict]:
    """Parse every source present under raw_root; a missing source is skipped,
    never faked. ERC-8004 registry events are raw events, not traces, and join
    the index only when a mapping is preregistered (none yet; see MANIFEST)."""
    from src.collect.benchmarks import parse_agentdojo, parse_swe_bench, parse_tau_bench, parse_webarena
    from src.collect.incidents import parse_aiid
    raw_root = Path(raw_root)
    rows: list[dict] = []
    for f in sorted(raw_root.glob("tau-bench/*.json")):
        rows += parse_tau_bench(f)
    for sub in sorted(raw_root.glob("swe-bench/*/")):
        if (sub / "results" / "results.json").exists():
            rows += parse_swe_bench(sub)
    if (raw_root / "agentdojo" / "runs").exists():
        rows += parse_agentdojo(raw_root / "agentdojo" / "runs")
    for z in sorted(raw_root.glob("webarena/*/*.zip")):
        rows += parse_webarena(z)
    if (raw_root / "incidents" / "mongodump_full_snapshot" / "incidents.csv").exists():
        rows += parse_aiid(raw_root / "incidents" / "mongodump_full_snapshot")
    return rows


def main() -> int:
    files = [p for p in RAW.rglob("*") if p.is_file()] if RAW.exists() else []
    if not files:
        print("reproduce: no raw data present. Phase 1 has not collected anything yet.")
        print("See data/MANIFEST.md for sources and src/collect/ for fetch scripts.")
        return 1

    from src.collect.index import build_index, write_index
    from src.collect.report import data_report
    from src.common.manifest import verify_manifest
    from src.common.provenance import provenance

    verify_manifest(RESEARCH / "data" / "MANIFEST.md", RAW)  # raises on checksum drift
    rows = collect_all(RAW)
    df = build_index(rows)
    processed = RESEARCH / "data" / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    write_index(df, processed / "trace_index.csv")

    report = data_report(df) + "\nManifest checksums verified against data/raw: OK\n"
    results = RESEARCH / "results"
    results.mkdir(exist_ok=True)
    report_path = results / f"{date.today().isoformat()}_data_report.md"
    report_path.write_text(report)
    sidecar = {"artifact": report_path.name, "rows": len(df), "provenance": provenance(seeds={})}
    report_path.with_suffix(".provenance.json").write_text(json.dumps(sidecar, indent=2) + "\n")
    print(f"reproduce: wrote {processed / 'trace_index.csv'} ({len(df)} rows) and {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
