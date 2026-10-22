"""Benchmark trace fetchers and parsers.

Each source has parse_<source>(path) -> list[dict] rows via make_trace_row,
and download_<source>(out_dir, manifest_path). Availability flags are
per-source constants that describe what the published format contains.
"""
import json
import re
import tarfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from src.collect.schema import make_trace_row
from src.common.manifest import append_entry

METHOD = "src/collect/benchmarks.py"

# Upstream refs pinned 2026-10-22 (commits/main via the GitHub API).
TAU_BENCH_SHA = "59a200c6d575d595120f1cb70fea53cef0632f6b"  # sierra-research/tau-bench
AGENTDOJO_SHA = "089ed468cf3ed0322acc66b0211f26d9d90dbf60"  # ethz-spylab/agentdojo
EXPERIMENTS_SHA = "40f164d5b8f1d249bf95a6df8b74b577fd8e519d"  # swe-bench/experiments

# Every file in historical_trajectories/ at the pinned ref.
TAU_BENCH_FILES = ["gpt-4o-airline.json", "gpt-4o-retail.json",
                   "sonnet-35-new-airline.json", "sonnet-35-new-retail.json"]

# Official SWE-agent submissions on the lite split with SWE-agent-format .traj
# files in the public s3://swe-bench-submissions bucket. Other submissions
# publish trajectories too (~25 GB across 63 submissions, each harness in its
# own format); they are excluded as a MANIFEST limitation, not fetched.
SWE_BENCH_SUBMISSIONS = [
    "20240402_sweagent_claude3opus",
    "20240402_sweagent_gpt4",
    "20240620_sweagent_claude3.5sonnet",
    "20240728_sweagent_gpt4o",
]
SWE_BENCH_S3 = "https://swe-bench-submissions.s3.amazonaws.com"

# Official v2 execution traces folder from webarena resources/README.md.
WEBARENA_FOLDER_ID = "1H4wkzDkY2ufiC63DISMXllri0j-ipWcs"
WEBARENA_ZIPS = ["v2_919_gpt35_16k_cot.zip", "v2_919_gpt35_16k_cot_na.zip",
                 "v2_919_gpt35_16k_direct.zip", "v2_919_gpt35_16k_direct_na.zip",
                 "v2_919_gpt4_8k_cot.zip", "v2_919_text_bison_001_cot.zip"]


def _get(url) -> bytes:
    import requests
    r = requests.get(url, timeout=300)
    r.raise_for_status()
    return r.content


def download_tau_bench(out_dir, manifest_path):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name in TAU_BENCH_FILES:
        url = (f"https://raw.githubusercontent.com/sierra-research/tau-bench/"
               f"{TAU_BENCH_SHA}/historical_trajectories/{name}")
        dest = out / name
        if not dest.exists():
            dest.write_bytes(_get(url))
        append_entry(manifest_path, name=f"tau-bench {name}", url=url, method=METHOD,
                     row_count=len(json.loads(dest.read_text())), file_path=dest,
                     license="MIT (sierra-research/tau-bench)",
                     limitations="authors' historical trajectories only (2 models x 2 domains); no timestamps or per-step latency")


def download_swe_bench(out_dir, manifest_path):
    out = Path(out_dir)
    for sub in SWE_BENCH_SUBMISSIONS:
        subdir = out / sub
        (subdir / "trajs").mkdir(parents=True, exist_ok=True)
        (subdir / "results").mkdir(exist_ok=True)
        results_url = (f"https://raw.githubusercontent.com/swe-bench/experiments/"
                       f"{EXPERIMENTS_SHA}/evaluation/lite/{sub}/results/results.json")
        results_path = subdir / "results" / "results.json"
        if not results_path.exists():
            results_path.write_bytes(_get(results_url))
        for key in _s3_keys(f"lite/{sub}/trajs/"):
            dest = subdir / "trajs" / key.rsplit("/", 1)[1]
            if not dest.exists():
                dest.write_bytes(_get(f"{SWE_BENCH_S3}/{key}"))
        tar_path = out / f"{sub}.tar.gz"
        if not tar_path.exists():
            with tarfile.open(tar_path, "w:gz") as tar:
                tar.add(subdir, arcname=sub)
        append_entry(manifest_path, name=f"swe-bench lite {sub}", url=f"{SWE_BENCH_S3}/lite/{sub}/trajs/ + {results_url}",
                     method=METHOD, row_count=len(parse_swe_bench(subdir)), file_path=tar_path,
                     license="none stated in swe-bench/experiments; public leaderboard submissions",
                     limitations="official SWE-agent submissions only; 59 other lite submissions publish trajectories in other formats (~25 GB) and are not fetched; no per-step latency")


def _s3_keys(prefix) -> list[str]:
    keys, token = [], ""
    while True:
        url = f"{SWE_BENCH_S3}/?list-type=2&prefix={prefix}{token}"
        root = ET.fromstring(_get(url))
        ns = {"s3": root.tag.split("}")[0].strip("{")}
        keys += [k.text for k in root.findall(".//s3:Contents/s3:Key", ns)]
        nxt = root.find("s3:NextContinuationToken", ns)
        if nxt is None:
            return keys
        import urllib.parse
        token = "&continuation-token=" + urllib.parse.quote(nxt.text)


def download_agentdojo(out_dir, manifest_path):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    url = f"https://codeload.github.com/ethz-spylab/agentdojo/tar.gz/{AGENTDOJO_SHA}"
    tar_path = out / f"agentdojo-{AGENTDOJO_SHA[:12]}.tar.gz"
    if not tar_path.exists():
        tar_path.write_bytes(_get(url))
    runs_root = out / "runs"
    if not runs_root.exists():
        with tarfile.open(tar_path) as tar:
            members = [m for m in tar.getmembers() if "/runs/" in m.name]
            prefix = members[0].name.split("/runs/")[0] + "/"
            for m in members:
                m.name = m.name.removeprefix(prefix)
            tar.extractall(out, members=members, filter="data")
    append_entry(manifest_path, name="agentdojo runs", url=url, method=METHOD,
                 row_count=len(parse_agentdojo(runs_root)), file_path=tar_path,
                 license="MIT (ethz-spylab/agentdojo)",
                 limitations="only a per-run total duration is published, no per-step latency; includes injection-attacked runs (task_type=injection)")


def download_webarena(out_dir, manifest_path):
    out = Path(out_dir) / "102023_release_v2"
    if not all((out / z).exists() for z in WEBARENA_ZIPS):
        import gdown
        gdown.download_folder(id=WEBARENA_FOLDER_ID, output=str(out))
    folder_url = f"https://drive.google.com/drive/folders/{WEBARENA_FOLDER_ID}"
    for name in WEBARENA_ZIPS:
        append_entry(manifest_path, name=f"webarena {name}", url=folder_url, method=METHOD,
                     row_count=len(parse_webarena(out / name)), file_path=out / name,
                     license="Apache-2.0 (web-arena-x/webarena)",
                     limitations="authors' v2 execution traces; v1 traces are superseded and the human-annotator recordings are not agent traces, neither is fetched; no per-step latency")



_WEBARENA_HARNESSES = ("cot_na", "direct_na", "cot", "direct")


def parse_webarena(zip_path) -> list[dict]:
    """One official v2 release zip (e.g. v2_919_gpt4_8k_cot.zip): an inner dir
    named <n>_<model>_<harness> holding merged_log.txt with one
    '[Result] (PASS|FAIL) .../<task_id>.json' line per task and one
    render_<task_id>.html per task with one state_obv div per step. The format
    records actions but no per-step timestamps, retries, or error fields."""
    rows = []
    with zipfile.ZipFile(zip_path) as z:
        inner = z.namelist()[0].split("/")[0]
        run = inner.split("_", 1)[1]
        for h in _WEBARENA_HARNESSES:
            if run.endswith("_" + h):
                model, harness = run.removesuffix("_" + h), h
                break
        else:
            raise ValueError(f"unrecognized webarena run name {inner!r}")
        log = z.read(f"{inner}/merged_log.txt").decode(errors="replace")
        outcomes = {m.group(2): 0 if m.group(1) == "PASS" else 1
                    for m in re.finditer(r"\[Result\] \((PASS|FAIL)\) \S*?(\d+)\.json", log)}
        for task_id, outcome in sorted(outcomes.items(), key=lambda kv: int(kv[0])):
            html = z.read(f"{inner}/render_{task_id}.html").decode(errors="replace")
            site = re.search(r"sites: \['([^']+)'", html)
            rows.append(make_trace_row(
                trace_id=f"{inner}/{task_id}",
                source="webarena", domain="web", model_id=model,
                agent_id=f"{model}::webarena-{harness}", task_id=task_id,
                task_type=site.group(1) if site else "web",
                task_length_steps=html.count("class='state_obv'"),
                outcome=outcome, started_at="",
                has_step_latency=False, has_tool_calls=True,
                has_retries=False, has_errors=False,
            ))
    return rows


def parse_swe_bench(submission_dir) -> list[dict]:
    """One swe-bench/experiments submission dir named <date>_<harness>_<model>,
    holding results/results.json (resolved instance ids) and trajs/*.traj
    (SWE-agent format). Success is membership in the resolved list. The format
    has exit_status (errors) and actions (tool calls) but no timestamps."""
    submission_dir = Path(submission_dir)
    _, harness, model = submission_dir.name.split("_", 2)
    resolved = set(json.loads((submission_dir / "results" / "results.json").read_text())["resolved"])
    rows = []
    for traj_path in sorted(submission_dir.glob("trajs/*.traj")):
        instance_id = traj_path.stem
        traj = json.loads(traj_path.read_text())
        rows.append(make_trace_row(
            trace_id=f"{submission_dir.name}/{instance_id}",
            source="swe-bench", domain="code", model_id=model,
            agent_id=f"{model}::{harness}", task_id=instance_id,
            task_type="swe", task_length_steps=len(traj["trajectory"]),
            outcome=0 if instance_id in resolved else 1, started_at="",
            has_step_latency=False, has_tool_calls=True,
            has_retries=False, has_errors=True,
        ))
    return rows


def parse_agentdojo(runs_root) -> list[dict]:
    """The agentdojo repo's runs/ tree: one JSON per
    <pipeline>/<suite>/<task>/<attack>/<injection>.json. utility=false is a
    failure; attacked runs get task_type "injection". Only a total duration is
    published (no per-step latency); the error field exists in the format."""
    runs_root = Path(runs_root)
    rows = []
    for p in sorted(runs_root.rglob("*.json")):
        run = json.loads(p.read_text())
        pipeline = p.relative_to(runs_root).parts[0]
        rel = p.relative_to(runs_root).with_suffix("")
        rows.append(make_trace_row(
            trace_id=str(rel),
            source="agentdojo", domain=run["suite_name"], model_id=pipeline,
            agent_id=f"{pipeline}::agentdojo", task_id=run["user_task_id"],
            task_type="injection" if run["attack_type"] else "benign",
            task_length_steps=len(run["messages"]),
            outcome=0 if run["utility"] else 1, started_at="",
            has_step_latency=False, has_tool_calls=True,
            has_retries=False, has_errors=True,
        ))
    return rows


def parse_tau_bench(path) -> list[dict]:
    """One historical_trajectories file, named <model>-<domain>.json.
    reward 1.0 is success; anything else is a failure. No timestamps,
    no retry or error fields in the format; tool calls are present."""
    path = Path(path)
    model, domain = path.stem.rsplit("-", 1)
    rows = []
    for run in json.loads(path.read_text()):
        rows.append(make_trace_row(
            trace_id=f"{path.stem}/task{run['task_id']}/trial{run['trial']}",
            source="tau-bench", domain=domain, model_id=model,
            agent_id=f"{model}::tau-bench", task_id=str(run["task_id"]),
            task_type=domain, task_length_steps=len(run["traj"]),
            outcome=0 if run["reward"] == 1.0 else 1, started_at="",
            has_step_latency=False, has_tool_calls=True,
            has_retries=False, has_errors=False,
        ))
    return rows


BENCHMARK_SOURCES = {
    "tau-bench": (download_tau_bench, parse_tau_bench),
    "swe-bench": (download_swe_bench, parse_swe_bench),
    "agentdojo": (download_agentdojo, parse_agentdojo),
    "webarena": (download_webarena, parse_webarena),
}
