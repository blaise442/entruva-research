from src.common.compare_results import compare, diffs


def test_identical_metrics_reproduce():
    m = {"metrics": {"auc": 0.5, "rows": [{"p": 0.25, "name": "a"}], "verdict": "pass", "flag": True}}
    r = compare(m, m)
    assert r["reproduces_by_rule"] and r["numbers_compared"] == 2 and r["max_abs_difference"] == 0.0


def test_small_difference_is_within_six_decimals_and_large_is_not():
    old = {"metrics": {"a": 0.5, "b": [0.25, 0.75]}}
    assert compare(old, {"metrics": {"a": 0.5 + 1e-9, "b": [0.25, 0.75]}})["reproduces_by_rule"]
    r = compare(old, {"metrics": {"a": 0.5, "b": [0.25, 0.75001]}})
    assert not r["reproduces_by_rule"] and r["numbers_beyond_six_decimals"] == 1
    assert r["paths_beyond_six_decimals"] == ["/b"] and r["largest_differences"][0]["path"] == "/b[1]"


def test_non_numeric_and_structural_mismatches_are_reported():
    old = {"metrics": {"verdict": "pass", "xs": [1, 2], "only_old": 1, "flag": True}}
    new = {"metrics": {"verdict": "fail", "xs": [1], "flag": False}}
    r = compare(old, new)
    assert not r["reproduces_by_rule"]
    assert set(r["non_numeric_mismatches"]) == {"/verdict", "/xs", "/only_old", "/flag"}


def test_bool_is_not_compared_as_a_number():
    assert diffs(True, 1) == [("", None)]
