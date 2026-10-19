"""Regenerates every result in results/ from data/raw. Fails loudly while no data exists."""
import sys
from pathlib import Path

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"

def main() -> int:
    files = [p for p in RAW.rglob("*") if p.is_file()] if RAW.exists() else []
    if not files:
        print("reproduce: no raw data present. Phase 1 has not collected anything yet.")
        print("See data/MANIFEST.md for sources and src/collect/ for fetch scripts.")
        return 1
    print("reproduce: pipeline stages are defined in later phases; raw files found:", len(files))
    return 1

if __name__ == "__main__":
    sys.exit(main())
