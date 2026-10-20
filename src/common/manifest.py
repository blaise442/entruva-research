"""Checksums for data/MANIFEST.md entries."""
import hashlib
from pathlib import Path

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

from datetime import date

def append_entry(manifest_path: Path, *, name: str, url: str, method: str, row_count: int,
                 file_path: Path, license: str, limitations: str) -> str:
    """Append one source section. The caller passes a public url; this function
    never reads environment variables, so secrets cannot end up in the manifest."""
    rel = Path(file_path).name
    section = (
        f"\n## {name}\n"
        f"- URL / contract address: {url}\n"
        f"- Fetch date: {date.today().isoformat()}\n"
        f"- Method (script path): {method}\n"
        f"- Row count: {row_count}\n"
        f"- File: {rel}\n"
        f"- SHA-256: {sha256_file(Path(file_path))}\n"
        f"- License: {license}\n"
        f"- Known limitations: {limitations}\n"
    )
    with open(manifest_path, "a") as f:
        f.write(section)
    return section

def verify_manifest(manifest_path: Path, raw_root: Path) -> list[str]:
    """Recompute checksums for every entry whose file exists under raw_root.
    Raises if any file on disk no longer matches its recorded SHA-256."""
    entries: list[tuple[str, str]] = []
    fname = sha = None
    for line in Path(manifest_path).read_text().splitlines():
        if line.startswith("- File: "):
            fname = line.removeprefix("- File: ").strip()
        elif line.startswith("- SHA-256: "):
            sha = line.removeprefix("- SHA-256: ").strip()
            if fname and sha:
                entries.append((fname, sha))
            fname = sha = None
    mismatches = []
    for fname, sha in entries:
        hits = list(Path(raw_root).rglob(fname))
        for hit in hits:
            actual = sha256_file(hit)
            if actual != sha:
                mismatches.append(f"{fname}: manifest {sha[:12]}... but file is {actual[:12]}...")
    if mismatches:
        raise ValueError("raw data changed after fetch: " + "; ".join(mismatches))
    return mismatches
