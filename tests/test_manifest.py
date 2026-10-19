import hashlib
from pathlib import Path
from src.common.manifest import sha256_file

def test_sha256_matches_hashlib(tmp_path: Path):
    f = tmp_path / "x.bin"
    f.write_bytes(b"abc123")
    assert sha256_file(f) == hashlib.sha256(b"abc123").hexdigest()
