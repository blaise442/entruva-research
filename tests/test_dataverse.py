from src.collect.dataverse import FILES, fetch, url_for


def test_url_for_requests_the_original_format():
    assert url_for(13683212) == "https://dataverse.harvard.edu/api/access/datafile/13683212?format=original"


def test_fetch_writes_every_file_and_one_manifest_entry_each(tmp_path):
    seen = []

    def fake(url):
        seen.append(url)
        return b"a,b\n1,2\n"

    manifest = tmp_path / "MANIFEST.md"
    manifest.write_text("# m\n")
    paths = fetch(tmp_path / "dv", manifest, download=fake)
    assert sorted(p.name for p in paths) == sorted(FILES)
    assert len(seen) == 5 and all("format=original" in u for u in seen)
    text = manifest.read_text()
    assert text.count("## dataverse HJZW8Q") == 5 and "CC0 1.0" in text and "Row count: 1\n" in text
