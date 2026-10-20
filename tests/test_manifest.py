import hashlib
from pathlib import Path
from src.common.manifest import sha256_file

def test_sha256_matches_hashlib(tmp_path: Path):
    f = tmp_path / "x.bin"
    f.write_bytes(b"abc123")
    assert sha256_file(f) == hashlib.sha256(b"abc123").hexdigest()

import pytest
from src.common.manifest import append_entry, verify_manifest

def _manifest(tmp_path: Path) -> Path:
    m = tmp_path / "MANIFEST.md"
    m.write_text("# Data manifest\n\nheader text\n")
    return m

def _raw(tmp_path: Path, name: str, content: bytes) -> Path:
    f = tmp_path / "raw" / name
    f.parent.mkdir(exist_ok=True)
    f.write_bytes(content)
    return f

def test_append_entry_records_real_checksum_and_fields(tmp_path: Path):
    m = _manifest(tmp_path)
    f = _raw(tmp_path, "a.jsonl", b"row1\nrow2\n")
    section = append_entry(m, name="source-a", url="https://example.org/a", method="src/collect/a.py",
                           row_count=2, file_path=f, license="MIT", limitations="none known")
    text = m.read_text()
    assert section in text and "header text" in text
    assert "source-a" in section and "https://example.org/a" in section
    assert hashlib.sha256(b"row1\nrow2\n").hexdigest() in section
    assert "Row count: 2" in section and "MIT" in section

def test_append_twice_keeps_first_section(tmp_path: Path):
    m = _manifest(tmp_path)
    f = _raw(tmp_path, "a.jsonl", b"x")
    append_entry(m, name="one", url="u1", method="m", row_count=1, file_path=f, license="L", limitations="-")
    append_entry(m, name="two", url="u2", method="m", row_count=1, file_path=f, license="L", limitations="-")
    text = m.read_text()
    assert text.index("## one") < text.index("## two")

def test_verify_manifest_catches_mutated_raw_file(tmp_path: Path):
    m = _manifest(tmp_path)
    f = _raw(tmp_path, "a.jsonl", b"original")
    append_entry(m, name="src", url="u", method="m", row_count=1, file_path=f, license="L", limitations="-")
    assert verify_manifest(m, tmp_path / "raw") == []
    f.write_bytes(b"tampered")
    with pytest.raises(ValueError, match="a.jsonl"):
        verify_manifest(m, tmp_path / "raw")

def test_manifest_never_contains_env_secrets(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("RPC_URL", "https://rpc.secret.example/key/abc123")
    m = _manifest(tmp_path)
    f = _raw(tmp_path, "events.jsonl", b"{}")
    append_entry(m, name="erc8004 mainnet", url="https://eips.ethereum.org/EIPS/eip-8004",
                 method="src/collect/erc8004.py", row_count=1, file_path=f, license="public data",
                 limitations="fetched via private RPC; endpoint not recorded")
    assert "abc123" not in m.read_text() and "rpc.secret.example" not in m.read_text()
