from types import SimpleNamespace

import pytest

from src.collect.scan8004 import count_check, newest_token_id


def test_newest_token_id_parses_the_first_item():
    resp = SimpleNamespace(status_code=200, json=lambda: {"items": [{"token_id": "396408"}], "total": 364325})
    out = newest_token_id(56, get=lambda url, timeout: resp)
    assert out["token_id"] == 396408 and out["total"] == 364325 and "chain_id=56" in out["url"]


def test_count_check_passes_only_for_sequential_ids_within_the_api_bound():
    api = {"token_id": 55991, "total": 36268}
    assert count_check(55407, 55406, api)["status"] == "pass"
    assert count_check(55406, 55406, api)["status"] == "fail"
    assert count_check(55407, 55406, {"token_id": 55000, "total": 0})["status"] == "fail"


def test_count_check_is_not_run_when_the_api_fails():
    assert count_check(10, 9, None)["status"] == "not run"
    with pytest.raises(RuntimeError):
        newest_token_id(1, get=lambda url, timeout: SimpleNamespace(status_code=503, json=lambda: {}))


def test_count_check_is_not_applicable_for_a_windowed_fetch():
    out = count_check(10, 9, {"token_id": 20, "total": 5}, complete=False)
    assert out["status"] == "not applicable" and out["api_token_id"] == 20
