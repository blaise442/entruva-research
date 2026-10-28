"""Measure chars-per-token on each source's own trace text and write
data/prices/chars_per_token.csv. One row per (source, held-out model_id) with the
model's tiktoken encoding where tiktoken knows the id, else cl100k_base, plus a
cl100k_base fallback row per source. Samples up to N messages per source."""
import json
import re
import sys
import zipfile
from datetime import date
from pathlib import Path

import pandas as pd
import tiktoken

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
N = 2000


def _texts(source: str) -> list[str]:
    out = []
    if source == "tau-bench":
        for p in sorted((RAW / "tau-bench").glob("*.json")):
            for run in json.loads(p.read_text()):
                out += [str(m["content"]) for m in run["traj"] if m["role"] == "tool"]
    elif source == "agentdojo":
        for p in sorted((RAW / "agentdojo" / "runs").rglob("*.json")):
            for m in json.loads(p.read_text()).get("messages", []):
                if m["role"] == "tool":
                    c = m.get("content") or []
                    out.append(c if isinstance(c, str) else " ".join(x.get("content") or "" for x in c))
            if len(out) >= N:
                break
    elif source == "swe-bench":
        for d in sorted((RAW / "swe-bench").iterdir()):
            for t in sorted(d.glob("trajs/*.traj")) if d.is_dir() else []:
                out += [st.get("observation") or "" for st in json.loads(t.read_text())["trajectory"]]
            if len(out) >= N:
                break
    elif source == "webarena":
        for z in sorted((RAW / "webarena").rglob("*.zip")):
            with zipfile.ZipFile(z) as zf:
                for name in zf.namelist():
                    if name.endswith(".html") and "render_" in name:
                        html = zf.read(name).decode(errors="replace")
                        out += [m.group(1).strip() for m in re.finditer(r"class='parsed_action'[^>]*><pre>(.*?)</pre>", html, re.S)]
            if len(out) >= N:
                break
    return [t for t in out if t][:N]


def _encoding(model_id: str):
    try:
        return tiktoken.encoding_for_model(model_id)
    except KeyError:
        return tiktoken.get_encoding("cl100k_base")


def main():
    split = json.loads((ROOT / "splits" / "primary_split.json").read_text())
    feats = pd.read_csv(ROOT / "data/processed/features.csv", low_memory=False, usecols=["source", "agent_id", "model_id"])
    pairs = feats[feats.agent_id.isin(split["test_agents"])][["source", "model_id"]].drop_duplicates()
    rows = []
    for source in sorted(pairs.source.unique()):
        texts = _texts(source)
        chars = sum(len(t) for t in texts)
        encs = {"cl100k_base": tiktoken.get_encoding("cl100k_base")}
        for mid in pairs[pairs.source == source].model_id:
            encs[mid] = _encoding(mid)
        for mid, enc in encs.items():
            toks = sum(len(enc.encode(t, disallowed_special=())) for t in texts)
            rows.append({"source": source, "model_id": mid, "encoding": enc.name,
                         "chars_per_token": round(chars / toks, 4), "n_chars_sampled": chars,
                         "measured_on": date.today().isoformat()})
    out = ROOT / "data" / "prices" / "chars_per_token.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(out)


if __name__ == "__main__":
    sys.exit(main())
