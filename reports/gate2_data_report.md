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

## Power estimate (simulation, synthetic data; feeds only this section)

Procedure: src/models/power.py simulation with agent-correlated outcomes
(logistic random intercept per agent), a no-signal baseline score, and a
binormal telemetry score at each true AUC delta on the fixed grid. Detection
means the preregistered paired cluster-bootstrap test (grouped by agent) has
its 95% CI lower bound above 0. Inputs from the real index, benchmark rows
only: n_rows 44,643, failure rate 0.514, 41 agents. n_sims 500 total, run as
10 workers of 50 sims with seeds 20261017+i and powers averaged; n_boot 200
per test (the real analysis uses the preregistered n_boot 2000).

- power at delta 0.02: 1.00
- power at delta 0.03: 1.00
- power at delta 0.05: 1.00 (the preregistered threshold margin)
- power at delta 0.08: 1.00
- power at delta 0.10: 1.00
- minimum detectable delta on the grid at power >= 0.8: 0.02

Caveat, stated plainly: this simulation is optimistic. Its telemetry score is
cleanly binormal and its agent correlation is a single random intercept; real
telemetry features will be messier and more strongly clustered by agent, and
grouped cross-validation with 41 agents leaves limited headroom for
agent-level heterogeneity. Power 1.0 should be read as "sample size is not
the binding constraint", not as a promise of detection.

## Is this dataset large enough? (honest comparison to prereg-v1)

- Sample size and power: yes. 44,643 labeled benchmark traces across 41
  agents give power ~1.0 to detect the preregistered AUC margin of 0.05;
  the minimum detectable delta on the grid is 0.02.
- Label balance: yes. Overall failure rate 51.4%, and every source is within
  40% to 93%, so no class is rare.
- Grouping: adequate. 41 agents support grouped CV without any agent spanning
  train and test; agent count, not row count, is the limiting resource.
- Sources obtained: 5 of 6 planned. ERC-8004 events are pending an RPC
  endpoint (collector ready, gap logged in MANIFEST.md); registry events are
  context for the on-chain question and do not gate H1.
- Known weakness that does bind: per-step latency is missing in 100% of rows,
  so the latency-distribution feature family named in H1 cannot be built from
  the collected sources. Tool-call sequences, error signals, retries (where
  recorded), and task length are available. H1 will be tested on the
  available families; if telemetry fails, the untestable latency family is a
  stated limitation of the verdict, not a loophole. Options that would close
  the gap, both needing a founder decision: generate traces ourselves (spend
  gate) or obtain richer traces from dataset owners (request drafted).
- Incident rows (274, all failures) are context weight and sit outside the
  benchmark modeling set, counted separately above.

Verdict proposed at Gate 2: the dataset is large enough to run the
preregistered test on the available feature families; no scope reduction is
proposed. The latency gap is recorded here and in MANIFEST.md rather than in
DEVIATIONS.md because the preregistration names feature families as
candidates, not as commitments. STOP: founder reviews this package before
Phase 2 begins.
