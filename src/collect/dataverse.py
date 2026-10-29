"""Pin the public Dataverse dataset used by the Phase 4 cross-check (spec Part A).

doi:10.7910/DVN/HJZW8Q, CC0 1.0, released 2026-07-01: the first 10,000 ERC-8004
agents on Ethereum mainnet. Files are fetched by id in their original format and
recorded in data/MANIFEST.md with a checksum."""
from collections.abc import Callable
from pathlib import Path

import requests

from src.common.manifest import append_entry

DOI = "doi:10.7910/DVN/HJZW8Q"
FILES = {"agents_core.csv": 13683212, "transfer_history.csv": 13683210,
         "agent_feedback_records.csv": 13683215, "agent_reputation_summary.csv": 14033649,
         "data_dictionary.md": 13687590}
LIMITATIONS = ("first 10,000 Ethereum agents (ids 0 to 9999) at an observation block the data "
               "dictionary does not state; released 2026-07-01")


def url_for(file_id: int) -> str:
    return f"https://dataverse.harvard.edu/api/access/datafile/{file_id}?format=original"


def _download(url: str) -> bytes:
    r = requests.get(url, timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"{url} returned {r.status_code}")
    return r.content


def fetch(out_dir: Path, manifest_path: Path, download: Callable[[str], bytes] = _download) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, file_id in FILES.items():
        path = out_dir / name
        path.write_bytes(download(url_for(file_id)))
        rows = max(0, len(path.read_bytes().splitlines()) - 1) if name.endswith(".csv") else 0
        append_entry(manifest_path, name=f"dataverse HJZW8Q {name}", url=f"https://doi.org/10.7910/DVN/HJZW8Q (file id {file_id})",
                     method="src/collect/dataverse.py", row_count=rows, file_path=path, license="CC0 1.0", limitations=LIMITATIONS)
        paths.append(path)
    return paths


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    fetch(root / "data" / "raw" / "dataverse_HJZW8Q", root / "data" / "MANIFEST.md")
