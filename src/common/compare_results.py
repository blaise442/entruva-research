"""Compare rerun result files with the files they reproduce (DEVIATIONS 2026-11-13).

For each pair, every value under "metrics" is walked: numbers are compared by
absolute difference, everything else by equality. Writes
results/<date>_rerun_comparison.json. A file reproduces by the rule fixed before
the rerun when every number agrees to six decimal places (difference below 5e-7)
and nothing else differs."""
import json
import sys
from datetime import date
from pathlib import Path

from src.common.provenance import write_result

ROOT = Path(__file__).resolve().parents[2]
TOLERANCE = 5e-7
PAIRS = [("2026-10-25_H1_primary.json", "2026-11-13_H1_primary.json"),
         ("2026-10-25_H1_robustness_cv.json", "2026-11-13_H1_robustness_cv.json"),
         ("2026-10-28_S3_attacks.json", "2026-11-13_S3_attacks.json")]
# The S4 flywheel (synthetic, feeds no headline result) was not rerun: see the outcome note in DEVIATIONS 2026-11-13.


def diffs(a, b, path: str = "") -> list[tuple[str, float | None]]:
    """(path, absolute difference) per number; (path, None) where structure or a non-number differs."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = [(f"{path}/{k}", None) for k in sorted(set(a) ^ set(b))]
        return out + [d for k in sorted(set(a) & set(b)) for d in diffs(a[k], b[k], f"{path}/{k}")]
    if isinstance(a, list) and isinstance(b, list):
        out = [(path, None)] if len(a) != len(b) else []
        return out + [d for i, (x, y) in enumerate(zip(a, b)) for d in diffs(x, y, f"{path}[{i}]")]
    number = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)
    if number(a) and number(b):
        return [(path, abs(float(a) - float(b)))]
    return [] if type(a) is type(b) and a == b else [(path, None)]


def compare(old: dict, new: dict) -> dict:
    d = diffs(old["metrics"], new["metrics"])
    nums = [(p, v) for p, v in d if v is not None]
    over = sorted(((p, v) for p, v in nums if v >= TOLERANCE), key=lambda pv: -pv[1])
    other = [p for p, v in d if v is None]
    return {"numbers_compared": len(nums), "max_abs_difference": max((v for _, v in nums), default=0.0),
            "numbers_beyond_six_decimals": len(over), "largest_differences": [{"path": p, "abs_difference": v} for p, v in over[:10]],
            "paths_beyond_six_decimals": sorted({_generic(p) for p, _ in over}),
            "non_numeric_mismatches": other, "reproduces_by_rule": not over and not other}


def _generic(path: str) -> str:
    """Path with list indices dropped, so the affected keys can be listed compactly."""
    out, skip = [], False
    for ch in path:
        if ch == "[":
            skip = True
        elif ch == "]":
            skip = False
        elif not skip:
            out.append(ch)
    return "".join(out)


def main() -> int:
    res = {}
    for old_name, new_name in PAIRS:
        old, new = (json.loads((ROOT / "results" / n).read_text()) for n in (old_name, new_name))
        res[new_name] = {"reproduces": old_name, "rerun_git_commit": new["provenance"]["git_commit"],
                         "rerun_git_dirty": new["provenance"]["git_dirty"], **compare(old, new)}
    out = ROOT / "results" / f"{date.today().isoformat()}_rerun_comparison.json"
    write_result(out, "rerun comparison (DEVIATIONS 2026-11-13)", res, {})
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
