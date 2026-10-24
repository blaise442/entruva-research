"""Runtime telemetry features read from raw traces, keyed by the parser's trace_id.

Every extractor reads only what an observer sees while the agent runs (calls,
tool results, errors, termination status, total duration). None reads the
outcome: no reward, utility, security, resolved list, submission text, or the
final answer. Per-step latency is published by no source and is not built.
"""
import json
import math
import re
import zipfile
from pathlib import Path

import numpy as np

CORE = ["n_tool_calls", "n_distinct_tools", "repeat_call_ratio", "n_errors",
        "error_rate", "max_error_run", "mean_text_len"]
# source-specific signals; NaN where the source does not publish them
EXTRA = ["duration_s", "exit_status", "api_calls", "tokens_sent"]
FEATURE_COLUMNS = CORE + EXTRA
_NAN = float("nan")


def features_from_steps(steps: list[dict]) -> dict:
    """steps: dicts with tool, args, error, text_len, one per tool call."""
    n = len(steps)
    run = best = 0
    for s in steps:
        run = run + 1 if s["error"] else 0
        best = max(best, run)
    repeats = sum(1 for a, b in zip(steps, steps[1:]) if (a["tool"], a["args"]) == (b["tool"], b["args"]))
    errs = sum(1 for s in steps if s["error"])
    return {
        "n_tool_calls": n,
        "n_distinct_tools": len({s["tool"] for s in steps}),
        "repeat_call_ratio": repeats / n if n else _NAN,
        "n_errors": errs,
        "error_rate": errs / n if n else _NAN,
        "max_error_run": best,
        "mean_text_len": float(np.mean([s["text_len"] for s in steps])) if n else _NAN,
    }


def _full(core: dict, **extra) -> dict:
    out = {**core, "duration_s": _NAN, "exit_status": "", "api_calls": _NAN, "tokens_sent": _NAN}
    out.update(extra)
    return out


def features_tau_bench(path) -> dict:
    path = Path(path)
    out = {}
    for run in json.loads(path.read_text()):
        pending, steps = {}, []
        for m in run["traj"]:
            for tc in m.get("tool_calls") or []:
                pending[tc["id"]] = (tc["function"]["name"], tc["function"]["arguments"])
            if m["role"] == "tool":
                name, args = pending.get(m["tool_call_id"], (m.get("name"), ""))
                text = str(m["content"])
                steps.append(dict(tool=name, args=args, error=text.lower().startswith("error"),
                                  text_len=len(text)))
        out[f"{path.stem}/task{run['task_id']}/trial{run['trial']}"] = _full(features_from_steps(steps))
    return out


def features_agentdojo(runs_root) -> dict:
    runs_root = Path(runs_root)
    out = {}
    for p in sorted(runs_root.rglob("*.json")):
        run = json.loads(p.read_text())
        if "utility" not in run:
            continue  # same skip as the parser: no outcome, no row
        steps = []
        for m in run["messages"]:
            if m["role"] != "tool":
                continue
            tc = m.get("tool_call") or {}
            content = m.get("content") or []
            text = content if isinstance(content, str) else " ".join(c.get("content") or "" for c in content)
            steps.append(dict(tool=tc.get("function"), args=json.dumps(tc.get("args"), sort_keys=True),
                              error=bool(m.get("error")), text_len=len(text)))
        dur = run.get("duration")
        out[str(p.relative_to(runs_root).with_suffix(""))] = _full(
            features_from_steps(steps), duration_s=float(dur) if dur is not None else _NAN)
    return out


# heuristic: SWE-agent observations carry raw shell/python output
_SWE_ERR = re.compile(r"Traceback \(most recent call last\)|\bError\b|command not found|SyntaxError")


def features_swe_bench(submission_dir) -> dict:
    submission_dir = Path(submission_dir)
    out = {}
    for traj_path in sorted(submission_dir.glob("trajs/*.traj")):
        traj = json.loads(traj_path.read_text())
        steps = []
        for st in traj["trajectory"]:
            action = (st.get("action") or "").strip()
            obs = st.get("observation") or ""
            steps.append(dict(tool=action.split(" ", 1)[0] if action else "", args=action,
                              error=bool(_SWE_ERR.search(obs)), text_len=len(obs)))
        info = traj.get("info", {})
        stats = info.get("model_stats") or {}
        out[f"{submission_dir.name}/{traj_path.stem}"] = _full(
            features_from_steps(steps), exit_status=str(info.get("exit_status") or ""),
            api_calls=float(stats.get("api_calls", _NAN)), tokens_sent=float(stats.get("tokens_sent", _NAN)))
    return out


def features_webarena(zip_path) -> dict:
    """Steps are the agent's parsed actions; only the action verb and bracketed
    arguments enter, never the text of a final 'stop' answer. A parse failure
    ('none' action) counts as an error."""
    out = {}
    with zipfile.ZipFile(zip_path) as z:
        inner = z.namelist()[0].split("/")[0]
        names = set(z.namelist())
        log = z.read(f"{inner}/merged_log.txt").decode(errors="replace")
        for tid in sorted({m.group(1) for m in re.finditer(r"\[Result\] \((?:PASS|FAIL)\) \S*?(\d+)\.json", log)}, key=int):
            if f"{inner}/render_{tid}.html" not in names:
                continue
            html = z.read(f"{inner}/render_{tid}.html").decode(errors="replace")
            steps = []
            for m in re.finditer(r"class='parsed_action'[^>]*><pre>(.*?)</pre>", html, re.S):
                act = m.group(1).strip()
                verb = act.split(" ", 1)[0].lower()
                args = "" if verb == "stop" else act
                steps.append(dict(tool=verb, args=args, error=verb == "none", text_len=len(act)))
            out[f"{inner}/{tid}"] = _full(features_from_steps(steps))
    return out
