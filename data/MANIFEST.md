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

## policy: Markel Technology Combined specimen wording
- URL / contract address: https://content.markel.com/api/public/content/specimen-wording-and-product-information-technology-combined
- Fetch date: 2026-10-22
- Method (script path): WebSearch + curl via src/common/manifest.append_entry (docs/COVERAGE_LANDSCAPE.md)
- Row count: 0
- File: markel-technology-combined-specimen.pdf
- SHA-256: 8fbe4cc3af8f5ca2fd997c2aba24c94e2b432a3ce54817513458bd43bcef1e35
- License: publicly posted specimen wording, Markel terms apply
- Known limitations: context only, feeds no model; row_count 0 because these are documents, not trace data

## policy: Hiscox CyberClear policy summary
- URL / contract address: https://hiscox.co.uk/sites/uk/files/documents/2019-03/19326-CyberClear-policy-summary.pdf
- Fetch date: 2026-10-22
- Method (script path): WebSearch + curl via src/common/manifest.append_entry (docs/COVERAGE_LANDSCAPE.md)
- Row count: 0
- File: hiscox-cyberclear-policy-summary.pdf
- SHA-256: 47d9260879ec26241b293aa05c5deddd732dbde78de81a1ddabdbff34a2b9f40
- License: publicly posted summary (2019), Hiscox terms apply
- Known limitations: context only, feeds no model; row_count 0 because these are documents, not trace data

## policy: tech E&O coverage overview
- URL / contract address: https://cdn.zephyrcms.com/967865c2-afef-4415-91f9-f68e65d09b4c/-/inline/yes/technology-professional-liability-errors-and-omissions-coverage.pdf
- Fetch date: 2026-10-22
- Method (script path): WebSearch + curl via src/common/manifest.append_entry (docs/COVERAGE_LANDSCAPE.md)
- Row count: 0
- File: tech-eo-coverage-overview.pdf
- SHA-256: 227e26bf11cb8a754903b6c241d35273a3ff36c462b59a2ad59f00dc7147d7a8
- License: broker explainer, 2 pages
- Known limitations: context only, feeds no model; row_count 0 because these are documents, not trace data

## erc8004 ethereum-mainnet identity registry events
- URL / contract address: https://github.com/erc-8004/erc-8004-contracts (address source); events via eth_getLogs
- Fetch date: 2026-10-25
- Method (script path): src/collect/erc8004.py
- Row count: 275118
- File: ethereum-mainnet_identity.jsonl
- SHA-256: 0ca1ee3dd3e8d3a755abce5690b15d83930ba29cc1b148c2c913503f1572e7e4
- License: public blockchain data
- Known limitations: fetched 2026-10-25 from the keyless public endpoint https://rpc.mevblocker.io (Ethereum mainnet only; Base not yet fetched); ValidationRegistry has no published curated address

## erc8004 ethereum-mainnet reputation registry events
- URL / contract address: https://github.com/erc-8004/erc-8004-contracts (address source); events via eth_getLogs
- Fetch date: 2026-10-25
- Method (script path): src/collect/erc8004.py
- Row count: 34535
- File: ethereum-mainnet_reputation.jsonl
- SHA-256: c0063e0932fab68079bb1287e5e1ca1afa55d4413446dfa9c1ac06c5526a4a3b
- License: public blockchain data
- Known limitations: fetched 2026-10-25 from the keyless public endpoint https://rpc.mevblocker.io (Ethereum mainnet only; Base not yet fetched); ValidationRegistry has no published curated address

## erc8004 contract ABI pin
- URL / contract address: https://github.com/erc-8004/erc-8004-contracts/tree/b9e466c250744a7e06b13dff9d3c2844ed64f825/abis
- Fetch date: 2026-10-27
- Method (script path): src/adversarial/run_reputation.py
- Row count: 0
- File: IdentityRegistry.json
- SHA-256: cdb8e30f41a56ed53421126dab87551ff2a178b8463646f69f75bc5dc9620564
- License: public data
- Known limitations: IdentityRegistry.json and ReputationRegistry.json copied from commit b9e466c250744a7e06b13dff9d3c2844ed64f825; used only to decode events

## erc8004 gas sample (receipts)
- URL / contract address: https://rpc.mevblocker.io
- Fetch date: 2026-10-27
- Method (script path): src/adversarial/run_reputation.py
- Row count: 400
- File: gas_sample.csv
- SHA-256: b1046d6832c9b0255957683facb970185638f05ed10dc019bf1a32f1cd8cab19
- License: public data
- Known limitations: 200 seeded transactions per event type (Registered, NewFeedback) via eth_getTransactionReceipt on the keyless public endpoint https://rpc.mevblocker.io

## erc8004 ETH-USD daily spot
- URL / contract address: https://api.coinbase.com/v2/prices/ETH-USD/spot
- Fetch date: 2026-10-27
- Method (script path): src/adversarial/run_reputation.py
- Row count: 101
- File: eth_usd_daily.csv
- SHA-256: 51711c0c8a9f36cfe65e7e961fb2c43fe182172ac8c92f5fe031bdc8278a003d
- License: public data
- Known limitations: Coinbase public spot price by date (api.coinbase.com/v2/prices/ETH-USD/spot?date=), one row per block day in the gas sample; no key

## dataverse HJZW8Q agents_core.csv
- URL / contract address: https://doi.org/10.7910/DVN/HJZW8Q (file id 13683212)
- Fetch date: 2026-10-28
- Method (script path): src/collect/dataverse.py
- Row count: 10000
- File: agents_core.csv
- SHA-256: 5c6fe3da38d4f3acbadbce71c723e9ce4aaa08eac96b8dba528e9de3b3583784
- License: CC0 1.0
- Known limitations: first 10,000 Ethereum agents (ids 0 to 9999) at an observation block the data dictionary does not state; released 2026-07-01

## dataverse HJZW8Q transfer_history.csv
- URL / contract address: https://doi.org/10.7910/DVN/HJZW8Q (file id 13683210)
- Fetch date: 2026-10-28
- Method (script path): src/collect/dataverse.py
- Row count: 1961
- File: transfer_history.csv
- SHA-256: 9cbd19a964da6d03aaece72b94816cb759dbd5dbc0f8a3bd44ab9c89a1320bd7
- License: CC0 1.0
- Known limitations: first 10,000 Ethereum agents (ids 0 to 9999) at an observation block the data dictionary does not state; released 2026-07-01

## dataverse HJZW8Q agent_feedback_records.csv
- URL / contract address: https://doi.org/10.7910/DVN/HJZW8Q (file id 13683215)
- Fetch date: 2026-10-28
- Method (script path): src/collect/dataverse.py
- Row count: 980
- File: agent_feedback_records.csv
- SHA-256: 554200d21d4f47e8929c91863e211a6b7f2b8a4a782b80f28a3244bd319fee95
- License: CC0 1.0
- Known limitations: first 10,000 Ethereum agents (ids 0 to 9999) at an observation block the data dictionary does not state; released 2026-07-01

## dataverse HJZW8Q agent_reputation_summary.csv
- URL / contract address: https://doi.org/10.7910/DVN/HJZW8Q (file id 14033649)
- Fetch date: 2026-10-28
- Method (script path): src/collect/dataverse.py
- Row count: 10000
- File: agent_reputation_summary.csv
- SHA-256: 2663fa2db7d326f10c545f904d2b41e8dc80c1ff2c723e9783ee5ae9dd8ecbc8
- License: CC0 1.0
- Known limitations: first 10,000 Ethereum agents (ids 0 to 9999) at an observation block the data dictionary does not state; released 2026-07-01

## dataverse HJZW8Q data_dictionary.md
- URL / contract address: https://doi.org/10.7910/DVN/HJZW8Q (file id 13687590)
- Fetch date: 2026-10-28
- Method (script path): src/collect/dataverse.py
- Row count: 0
- File: data_dictionary.md
- SHA-256: 039aad4c70b85ce81471da72b90b7ce244302815889c07945d90146ebe50a1e4
- License: CC0 1.0
- Known limitations: first 10,000 Ethereum agents (ids 0 to 9999) at an observation block the data dictionary does not state; released 2026-07-01

## erc8004 base-mainnet identity registry events
- URL / contract address: https://github.com/erc-8004/erc-8004-contracts (address source); events via eth_getLogs
- Fetch date: 2026-10-29
- Method (script path): src/collect/erc8004.py
- Row count: 32961
- File: base-mainnet_identity.jsonl
- SHA-256: 41d0e1f15b7e4559fc65221d41b8766db07041648beb648344602d0ce7ce5446
- License: public blockchain data
- Known limitations: fetched from the keyless public endpoint https://base-rpc.publicnode.com; window of 86000 blocks (53162845..53248845) because the endpoint serves no older history; ValidationRegistry has no published curated address

## erc8004 base-mainnet reputation registry events
- URL / contract address: https://github.com/erc-8004/erc-8004-contracts (address source); events via eth_getLogs
- Fetch date: 2026-10-29
- Method (script path): src/collect/erc8004.py
- Row count: 2161
- File: base-mainnet_reputation.jsonl
- SHA-256: 7ce00444ce92e8a92b7c5ff7d973f88469bc2545ca4afbf4ddd1544026ccf787
- License: public blockchain data
- Known limitations: fetched from the keyless public endpoint https://base-rpc.publicnode.com; window of 86000 blocks (53162845..53248845) because the endpoint serves no older history; ValidationRegistry has no published curated address

## erc8004 bnb-mainnet identity registry events
- URL / contract address: https://github.com/erc-8004/erc-8004-contracts (address source); events via eth_getLogs
- Fetch date: 2026-10-29
- Method (script path): src/collect/erc8004.py
- Row count: 23666
- File: bnb-mainnet_identity.jsonl
- SHA-256: 3089057fa87282781b0dedc348b02f644045a56c8c1d4ca599b4ffc2e87a20a3
- License: public blockchain data
- Known limitations: fetched from the keyless public endpoint https://bsc-rpc.publicnode.com; window of 380000 blocks (130116686..130496686) because the endpoint serves no older history; ValidationRegistry has no published curated address

## erc8004 bnb-mainnet reputation registry events
- URL / contract address: https://github.com/erc-8004/erc-8004-contracts (address source); events via eth_getLogs
- Fetch date: 2026-10-29
- Method (script path): src/collect/erc8004.py
- Row count: 9
- File: bnb-mainnet_reputation.jsonl
- SHA-256: d9fd4f97c5f461d9e72ab53848380c17a435e126e8dcb26b84361bbb095d00fe
- License: public blockchain data
- Known limitations: fetched from the keyless public endpoint https://bsc-rpc.publicnode.com; window of 380000 blocks (130116686..130496686) because the endpoint serves no older history; ValidationRegistry has no published curated address

## 8004scan newest agent ethereum-mainnet
- URL / contract address: https://api.8004scan.io/api/v1/agents?chain_id=1&limit=1&is_active=any&is_registered=true
- Fetch date: 2026-10-29
- Method (script path): src/crosscheck/run_chains.py
- Row count: 1
- File: ethereum-mainnet_newest.json
- SHA-256: 556bd78e08b56c67143ee396c31f30628f26f8e53afa386bc9c22080ed0c8adb
- License: public API, anonymous tier
- Known limitations: one request; newest token_id on the request date bounds our registration count; the total field is recorded, not used

## 8004scan newest agent base-mainnet
- URL / contract address: https://api.8004scan.io/api/v1/agents?chain_id=8453&limit=1&is_active=any&is_registered=true
- Fetch date: 2026-10-29
- Method (script path): src/crosscheck/run_chains.py
- Row count: 1
- File: base-mainnet_newest.json
- SHA-256: c94c3e1666099a9cfe292782121789726cd92a2b364d4879680ae7755865061a
- License: public API, anonymous tier
- Known limitations: one request; newest token_id on the request date bounds our registration count; the total field is recorded, not used

## 8004scan newest agent bnb-mainnet
- URL / contract address: https://api.8004scan.io/api/v1/agents?chain_id=56&limit=1&is_active=any&is_registered=true
- Fetch date: 2026-10-29
- Method (script path): src/crosscheck/run_chains.py
- Row count: 1
- File: bnb-mainnet_newest.json
- SHA-256: 893e772c6745c00e690e38a3d51d2cd49527463bc6f27002ced72ef060afd634
- License: public API, anonymous tier
- Known limitations: one request; newest token_id on the request date bounds our registration count; the total field is recorded, not used
