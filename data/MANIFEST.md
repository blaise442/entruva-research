# Data manifest

Every source gets one section before its data is used. data/raw is gitignored; this file plus src/collect regenerates it.

Format:
## <source name>
- URL / contract address:
- Fetch date:
- Method (script path):
- Row count:
- SHA-256:
- License:
- Known limitations:



## erc8004 registry events (pending)
- URL / contract address: IdentityRegistry and ReputationRegistry at 0x8004A169FB4a3325136EB29fA0ceB6D2e539a432 / 0x8004BAa17C55a88189AE136b182e5fdA19dE9b63 on Ethereum mainnet and Base (source: https://github.com/erc-8004/erc-8004-contracts, cross-checked 2026-10-20)
- Fetch date: not yet fetched
- Method (script path): src/collect/erc8004.py
- Row count: 0
- SHA-256: none (no file yet)
- License: public blockchain data
- Known limitations: awaiting RPC endpoint from the founder; the EIP publishes no addresses itself (Draft); the ValidationRegistry has no published curated address and is excluded until one is verified

## tau-bench gpt-4o-airline.json
- URL / contract address: https://raw.githubusercontent.com/sierra-research/tau-bench/59a200c6d575d595120f1cb70fea53cef0632f6b/historical_trajectories/gpt-4o-airline.json
- Fetch date: 2026-10-22
- Method (script path): src/collect/benchmarks.py
- Row count: 200
- File: gpt-4o-airline.json
- SHA-256: e9e6c0297660c537f83d4fd9c476ce7a9a86ecd2784874b7bfc13be598e37bfa
- License: MIT (sierra-research/tau-bench)
- Known limitations: authors' historical trajectories only (2 models x 2 domains); no timestamps or per-step latency

## tau-bench gpt-4o-retail.json
- URL / contract address: https://raw.githubusercontent.com/sierra-research/tau-bench/59a200c6d575d595120f1cb70fea53cef0632f6b/historical_trajectories/gpt-4o-retail.json
- Fetch date: 2026-10-22
- Method (script path): src/collect/benchmarks.py
- Row count: 460
- File: gpt-4o-retail.json
- SHA-256: df01707894836168ff0ec9616b0bf08f66c7e5afcf313e5fe4f7a2f5c2ec938b
- License: MIT (sierra-research/tau-bench)
- Known limitations: authors' historical trajectories only (2 models x 2 domains); no timestamps or per-step latency

## tau-bench sonnet-35-new-airline.json
- URL / contract address: https://raw.githubusercontent.com/sierra-research/tau-bench/59a200c6d575d595120f1cb70fea53cef0632f6b/historical_trajectories/sonnet-35-new-airline.json
- Fetch date: 2026-10-22
- Method (script path): src/collect/benchmarks.py
- Row count: 400
- File: sonnet-35-new-airline.json
- SHA-256: fe62fcd514b855b36f156dd4c3c7748597b392b006aff739b53337a9f3ba94d1
- License: MIT (sierra-research/tau-bench)
- Known limitations: authors' historical trajectories only (2 models x 2 domains); no timestamps or per-step latency

## tau-bench sonnet-35-new-retail.json
- URL / contract address: https://raw.githubusercontent.com/sierra-research/tau-bench/59a200c6d575d595120f1cb70fea53cef0632f6b/historical_trajectories/sonnet-35-new-retail.json
- Fetch date: 2026-10-22
- Method (script path): src/collect/benchmarks.py
- Row count: 920
- File: sonnet-35-new-retail.json
- SHA-256: 0df526398e9d2720c32d340815cffb04fe8c4f8a61b1f4f84bf3bb558f760131
- License: MIT (sierra-research/tau-bench)
- Known limitations: authors' historical trajectories only (2 models x 2 domains); no timestamps or per-step latency

## agentdojo runs
- URL / contract address: https://codeload.github.com/ethz-spylab/agentdojo/tar.gz/089ed468cf3ed0322acc66b0211f26d9d90dbf60
- Fetch date: 2026-10-22
- Method (script path): src/collect/benchmarks.py
- Row count: 36678
- File: agentdojo-089ed468cf3e.tar.gz
- SHA-256: d7e0ee021be27a69e7e66647979b5a5e0dd10030d38d04ce4102e18a76a228d8
- License: MIT (ethz-spylab/agentdojo)
- Known limitations: only a per-run total duration is published, no per-step latency; includes injection-attacked runs (task_type=injection)

## webarena v2_919_gpt35_16k_cot.zip
- URL / contract address: https://drive.google.com/drive/folders/1H4wkzDkY2ufiC63DISMXllri0j-ipWcs
- Fetch date: 2026-10-22
- Method (script path): src/collect/benchmarks.py
- Row count: 802
- File: v2_919_gpt35_16k_cot.zip
- SHA-256: 5c663b7661b315682e91bf92e65cbc470596715b3792af7648c0ed9d8d6ddc76
- License: Apache-2.0 (web-arena-x/webarena)
- Known limitations: authors' v2 execution traces; v1 traces are superseded and the human-annotator recordings are not agent traces, neither is fetched; result lines without a shipped render html are skipped; no per-step latency

## webarena v2_919_gpt35_16k_cot_na.zip
- URL / contract address: https://drive.google.com/drive/folders/1H4wkzDkY2ufiC63DISMXllri0j-ipWcs
- Fetch date: 2026-10-22
- Method (script path): src/collect/benchmarks.py
- Row count: 811
- File: v2_919_gpt35_16k_cot_na.zip
- SHA-256: 03f7a9bf1baa85cc2e3ae960f6b40a29704503bf11b4ae8eb27339d9cbb20df8
- License: Apache-2.0 (web-arena-x/webarena)
- Known limitations: authors' v2 execution traces; v1 traces are superseded and the human-annotator recordings are not agent traces, neither is fetched; result lines without a shipped render html are skipped; no per-step latency

## webarena v2_919_gpt35_16k_direct.zip
- URL / contract address: https://drive.google.com/drive/folders/1H4wkzDkY2ufiC63DISMXllri0j-ipWcs
- Fetch date: 2026-10-22
- Method (script path): src/collect/benchmarks.py
- Row count: 803
- File: v2_919_gpt35_16k_direct.zip
- SHA-256: 885fcf486e042eaf923a681e8861bf5f4b1a17959dc7e99086ca62dffd1cffac
- License: Apache-2.0 (web-arena-x/webarena)
- Known limitations: authors' v2 execution traces; v1 traces are superseded and the human-annotator recordings are not agent traces, neither is fetched; result lines without a shipped render html are skipped; no per-step latency

## webarena v2_919_gpt35_16k_direct_na.zip
- URL / contract address: https://drive.google.com/drive/folders/1H4wkzDkY2ufiC63DISMXllri0j-ipWcs
- Fetch date: 2026-10-22
- Method (script path): src/collect/benchmarks.py
- Row count: 811
- File: v2_919_gpt35_16k_direct_na.zip
- SHA-256: a2edfab5df18e2519e769057a6a689cf02d6043ec6f575d39999dd39eda72a03
- License: Apache-2.0 (web-arena-x/webarena)
- Known limitations: authors' v2 execution traces; v1 traces are superseded and the human-annotator recordings are not agent traces, neither is fetched; result lines without a shipped render html are skipped; no per-step latency

## swe-bench lite 20240402_sweagent_claude3opus
- URL / contract address: https://swe-bench-submissions.s3.amazonaws.com/lite/20240402_sweagent_claude3opus/trajs/ + https://raw.githubusercontent.com/swe-bench/experiments/40f164d5b8f1d249bf95a6df8b74b577fd8e519d/evaluation/lite/20240402_sweagent_claude3opus/results/results.json
- Fetch date: 2026-10-22
- Method (script path): src/collect/benchmarks.py
- Row count: 300
- File: 20240402_sweagent_claude3opus.tar.gz
- SHA-256: 04fb88de91b241358682e0594d79a698462381dcfb95f2dc33d29c1ac4b7872a
- License: none stated in swe-bench/experiments; public leaderboard submissions
- Known limitations: official SWE-agent submissions only; 59 other lite submissions publish trajectories in other formats (~25 GB) and are not fetched; no per-step latency

## webarena v2_919_gpt4_8k_cot.zip
- URL / contract address: https://drive.google.com/drive/folders/1H4wkzDkY2ufiC63DISMXllri0j-ipWcs
- Fetch date: 2026-10-22
- Method (script path): src/collect/benchmarks.py
- Row count: 810
- File: v2_919_gpt4_8k_cot.zip
- SHA-256: da39bb960a138da4f04cce6c3c2af405d3b9feca72a9ece75e89b610046a3e3a
- License: Apache-2.0 (web-arena-x/webarena)
- Known limitations: authors' v2 execution traces; v1 traces are superseded and the human-annotator recordings are not agent traces, neither is fetched; result lines without a shipped render html are skipped; no per-step latency

## webarena v2_919_text_bison_001_cot.zip
- URL / contract address: https://drive.google.com/drive/folders/1H4wkzDkY2ufiC63DISMXllri0j-ipWcs
- Fetch date: 2026-10-22
- Method (script path): src/collect/benchmarks.py
- Row count: 781
- File: v2_919_text_bison_001_cot.zip
- SHA-256: 1583df6e4e72dfa4eec061901cba6e685ab752b3f65188376da54083ac159c7a
- License: Apache-2.0 (web-arena-x/webarena)
- Known limitations: authors' v2 execution traces; v1 traces are superseded and the human-annotator recordings are not agent traces, neither is fetched; result lines without a shipped render html are skipped; no per-step latency

## swe-bench lite 20240402_sweagent_gpt4
- URL / contract address: https://swe-bench-submissions.s3.amazonaws.com/lite/20240402_sweagent_gpt4/trajs/ + https://raw.githubusercontent.com/swe-bench/experiments/40f164d5b8f1d249bf95a6df8b74b577fd8e519d/evaluation/lite/20240402_sweagent_gpt4/results/results.json
- Fetch date: 2026-10-22
- Method (script path): src/collect/benchmarks.py
- Row count: 300
- File: 20240402_sweagent_gpt4.tar.gz
- SHA-256: ec4c0c75602a5a3c5a813616fe4f780a6a618a8be62652d3de850a27a01262da
- License: none stated in swe-bench/experiments; public leaderboard submissions
- Known limitations: official SWE-agent submissions only; 59 other lite submissions publish trajectories in other formats (~25 GB) and are not fetched; no per-step latency

## swe-bench lite 20240620_sweagent_claude3.5sonnet
- URL / contract address: https://swe-bench-submissions.s3.amazonaws.com/lite/20240620_sweagent_claude3.5sonnet/trajs/ + https://raw.githubusercontent.com/swe-bench/experiments/40f164d5b8f1d249bf95a6df8b74b577fd8e519d/evaluation/lite/20240620_sweagent_claude3.5sonnet/results/results.json
- Fetch date: 2026-10-22
- Method (script path): src/collect/benchmarks.py
- Row count: 289
- File: 20240620_sweagent_claude3.5sonnet.tar.gz
- SHA-256: ac17c09cff6527dd2d3f9d4dcd7b7b0c55ed6c2f50e8e80cf618ee682b33b55d
- License: none stated in swe-bench/experiments; public leaderboard submissions
- Known limitations: official SWE-agent submissions only; 59 other lite submissions publish trajectories in other formats (~25 GB) and are not fetched; no per-step latency

## swe-bench lite 20240728_sweagent_gpt4o
- URL / contract address: https://swe-bench-submissions.s3.amazonaws.com/lite/20240728_sweagent_gpt4o/trajs/ + https://raw.githubusercontent.com/swe-bench/experiments/40f164d5b8f1d249bf95a6df8b74b577fd8e519d/evaluation/lite/20240728_sweagent_gpt4o/results/results.json
- Fetch date: 2026-10-22
- Method (script path): src/collect/benchmarks.py
- Row count: 278
- File: 20240728_sweagent_gpt4o.tar.gz
- SHA-256: cd05bbd19182c550a544ee517dc58e2c5e79ce6dc417301de0b45ad3d2942808
- License: none stated in swe-bench/experiments; public leaderboard submissions
- Known limitations: official SWE-agent submissions only; 59 other lite submissions publish trajectories in other formats (~25 GB) and are not fetched; no per-step latency

## AI Incident Database weekly snapshot
- URL / contract address: https://pub-72b2b2fc36ec423189843747af98f80e.r2.dev/backup-20261019101022.tar.bz2
- Fetch date: 2026-10-22
- Method (script path): src/collect/incidents.py
- Row count: 274
- File: backup-20261019101022.tar.bz2
- SHA-256: 72f8ba3b6a2d7bee3f1242efbbdce47b5658d184a1c8b8270b4c0fa11fc70c0e
- License: CC BY-SA 4.0 (snapshot license.txt); report contents keep their own rights
- Known limitations: row count is agentic incidents only (AGENTIC_RULE_DOC keyword rule over title and description); context-weight data with outcome=1 and no steps or telemetry; the OECD AI Incidents Monitor publishes no export or API (checked 2026-10-22) and is not collected
