# Does runtime telemetry predict AI agent failure?

A preregistered study with a practical question behind it: could an insurer
price liability cover for an AI agent from how the agent behaves while it
works, the way motor insurers price from driving data?

## What we tested, in plain language

An AI agent that does a task leaves a trail: how many tools it called, how often
it repeated itself, how many errors it hit, how long its messages were, how long
the task ran. We call that trail telemetry. We asked three things.

1. Does telemetry predict whether an agent fails a task, on agents the model has
   never seen, better than simply knowing which model it is, what kind of task
   it is and how long the task is? That simpler guess is the baseline. If
   telemetry cannot beat it, it adds nothing an underwriter does not already
   know.
2. If telemetry did set a premium, how cheaply could an agent's operator edit
   the trail to look safer than it is?
3. Is on-chain agent reputation (the ERC-8004 registries on Ethereum, Base and
   BNB Smart Chain) a usable alternative input, or is it cheap to fake?

The data are public benchmark runs with a recorded pass or fail for every task
(AgentDojo, SWE-bench, tau-bench, WebArena: 44,643 runs from 41 agents) and the
complete event history of the three on-chain registries. A failure here means
the agent did not complete the benchmark task; it is not an insured loss, and
the paper is explicit about that gap.

The hypotheses, the pass thresholds and the baseline were frozen before any
data was loaded (docs/PREREGISTRATION.md, git tag prereg-v1). Every choice made
after that is dated in docs/DEVIATIONS.md with its reason and who decided it.

## What we found

Telemetry predicts failure within a task domain and not across domains. On
held-out agents a gradient boosting model on telemetry reached an AUC of 0.843
against 0.654 for the baseline, and agents in the top predicted-risk quartile
failed four times as often as those in the bottom. Inside one benchmark
(AgentDojo) the gain is large; inside another (SWE-bench) telemetry is worse
than the baseline; a score trained on other domains beat the in-domain baseline
nowhere. The cheapest edits to the trail do not move a typical agent's risk
decile and do not help the worst-scoring agents at all, though one held-out
agent in ten could be nudged across a decile boundary for free. On-chain
reputation is not a substitute: nine in ten rated agents have a single feedback
giver and a median reputation costs about 0.27 USD in gas to fabricate.

Read the paper for the full result, the intervals and the limitations:

- paper/paper.pdf, version 1 of 2026-11-02 (source: paper/paper.md)
- reports/final_writeup.md, the longer internal write-up with every table
- reports/gate2_data_report.md to gate5_results.md, the per-gate packages
- docs/PREREGISTRATION.md and docs/DEVIATIONS.md

## Replicate it

Prerequisites: Python 3.12, make, about 25 GB of disk if you fetch every
on-chain registry in full (the Base identity log alone is 4.4 GB).

```bash
make env          # creates .venv and installs the pinned requirements
make test         # 176 tests, no network needed
```

### 1. Get the benchmark data

Each source is listed in data/MANIFEST.md with its URL, the exact file or
snapshot, the fetch method, row count, SHA-256 and licence. The download
functions are in src/collect/benchmarks.py, one per source
(download_taubench, download_agentdojo, download_webarena, download_swebench),
and src/collect/incidents.py for the AI Incident Database snapshot. Raw files
go under data/raw/, which is gitignored and never modified after fetch. If a
checksum you fetch differs from the manifest, the upstream file changed; say so
rather than editing the manifest.

### 2. Get an RPC URL for the on-chain data

The ERC-8004 collector reads registry events straight from the chains, so it
needs a JSON-RPC endpoint. Two ways:

- A keyless public endpoint, for Ethereum mainnet only. Set PUBLIC_RPC_URL to
  one that allows eth_getLogs over wide block ranges (publicnode worked for the
  Ethereum history in this study).
- A provider account, for Base and BNB Smart Chain and for Ethereum if the
  public endpoint rate-limits you. Create an app at dashboard.alchemy.com (any
  provider with the same JSON-RPC methods works), enable the Ethereum, Base and
  BNB Smart Chain networks on it, and copy the HTTPS URL for one network at a
  time. Two limits to know: the free plan answers eth_getLogs over at most 10
  blocks per request, which makes a full history impractical, and the paid
  pay-as-you-go plan (the full Base and BNB fetch cost about one dollar) returns
  a silently truncated answer above 10,000 blocks per request, so the collector
  never asks for more than that.

Put the URL in research/.env as RPC_URL=... (copy .env.example). The file is
gitignored; never commit it, paste it in an issue, or print it in a log. The
collector reads the chain id from the endpoint and names the output after it,
so run it once per chain, changing the URL between runs:

```bash
.venv/bin/python -m src.collect.erc8004
# writes data/raw/erc8004/<chain>_identity.jsonl and <chain>_reputation.jsonl
```

Every file passes an integrity check: registration ids contiguous from zero
and equal to the mint set, feedback index sequences contiguous from one, no
duplicate log. The gas price sample (data/raw/erc8004/gas_sample.csv) is drawn
from Ethereum receipts by src/adversarial/run_reputation.py and needs RPC_URL
too. The public Dataverse dataset used as an independent cross-check is
fetched by src/collect/dataverse.py with no credentials.

### 3. Rebuild the results

```bash
make reproduce
```

This verifies every manifest checksum, rebuilds the trace index and the
features table, refits the models on the frozen split, reruns the manipulation
analysis, the reputation descriptives and the simulation, and writes dated
files under results/. Each file embeds the git commit, the manifest hash, the
seeds and the timestamp it was produced from. Compare your files with the ones
committed under results/ by name. Drivers refuse to run if the trace index or
the held-out agent set differs from the frozen split in splits/.

## Layout

- docs/: PREREGISTRATION.md (frozen), DEVIATIONS.md (dated log), COVERAGE_LANDSCAPE.md (insurer AI exclusions and products, context only)
- data/: MANIFEST.md (every source with checksum and licence), abi/ (pinned ERC-8004 ABI), prices/, raw/ (gitignored), processed/ (trace_index.csv, features.csv)
- src/collect/: fetchers and parsers per source, the unified trace index, the ERC-8004 collector and decoder, the Dataverse and 8004scan cross-checks
- src/features/: telemetry extractors reading raw traces, features table build with a leakage check
- src/models/: split.py (frozen split and its integrity check), baselines.py, fit.py, metrics.py (cluster bootstrap by agent), glm.py, run_primary.py, run_robustness.py
- src/adversarial/: the four telemetry attacks, breakeven pricing, run_s3.py, run_reputation.py
- src/simulation/: the synthetic flywheel (every output carries "synthetic" in its name and feeds no headline result)
- splits/primary_split.json: held-out agents per source, frozen before any model fit, with the index hash
- results/: dated JSON and figures with provenance
- reports/: gate packages, weekly reports, the final write-up, the data request draft
- paper/: paper.md, paper.pdf, figures/, build_pdf.py (Chrome headless, no LaTeX needed)
- tests/: the suite behind make test

## Provenance

This repository is the research directory of a private monorepo, split out
with its full history. Commit hashes embedded in result files and in the
preregistration refer to the monorepo; the tag prereg-v1 here marks the same
tree as monorepo commit 8f74d7e0e7aa0e5d9e06b93dcbfc0c7e0e0d2c65 and nothing in
it has changed since. The feature build refuses any feature that is a function
of the outcome, and the models never see agent identity or the label.

## Contributing

Contributions are welcome as pull requests and every one of them is reviewed
and approved by the maintainer (Blaise W, @blaise442) before it merges. The main
branch is protected: no direct pushes, a code owner review is required, force
pushes and deletion are blocked. Preregistered material and result files do not
change; see CONTRIBUTING.md.

## Citation

See CITATION.cff. Cite the paper (version 1, 2026-11-02) and the repository
release v1.0.

## Licence

MIT for the code, CC BY 4.0 for the reports and the paper. Third-party datasets
keep their own licences, listed per source in data/MANIFEST.md. See LICENSE.

## Contact

Research questions and data offers: contact@entruva.ai. Live summary and log:
https://app.entruva.ai/research
