# Data report

- sources obtained: 5 of 6 planned (agentdojo, incident, swe-bench, tau-bench, webarena)
- Benchmark and on-chain rows: 44643
- Incident rows (context weight, all failures): 274
- distinct domains: 16, models: 139, agents: 142
- cross-source trace_id collisions: 0

## Rows and label balance per source

- overall: 44917 rows, failure rate 51.7%
- agentdojo: 36678 rows, failure rate 45.6%
- incident: 274 rows, failure rate 100.0%
- swe-bench: 1167 rows, failure rate 81.7%
- tau-bench: 1980 rows, failure rate 40.3%
- webarena: 4818 rows, failure rate 92.8%

## Availability flags (fraction of rows missing the signal)

- has_step_latency: missing in 100.0% of rows
- has_tool_calls: missing in 0.6% of rows
- has_retries: missing in 100.0% of rows
- has_errors: missing in 15.7% of rows

Manifest checksums verified against data/raw: OK
