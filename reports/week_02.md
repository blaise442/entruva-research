# Week 2 report (2026-10-24 to 2026-10-25)

## What ran

- Gate 2 approved 2026-10-23; Phase 2 executed and closed in two days, well
  ahead of the day-60 checkpoint for first AUC and Brier results.
- Held-out split frozen before any model fit: 20 percent of agents per source
  (ceil), 10 test agents, committed in `splits/primary_split.json`.
- Telemetry features extracted from raw traces per source (tool-call counts,
  distinct-tool ratio, repeated-call ratio, error counts and rate, error run
  length, message length, plus AgentDojo-only duration, API calls and tokens).
  Leakage guard test: no feature equals or encodes the outcome.
- Primary H1 evaluation on the frozen split, grouped 5-fold CV robustness,
  per-source breakdown, S2 portability, Poisson GLM relativities. All in
  `results/` with provenance. Test suite: 85 passing. `make reproduce` now
  rebuilds features and both result files after the index.

## Results in one paragraph

On the held-out agents the telemetry model's AUC is 0.843 [0.777, 0.888]
against a baseline of 0.654; the paired delta is 0.189 [0.067, 0.288], Brier
skill 0.220 [0.049, 0.315], top-to-bottom quartile failure ratio 4.14 with a
perfectly monotone decile lift. Clauses 1 to 3 of H1 hold; clause 4 is Phase 3.
Grouped CV over all 41 agents agrees (delta 0.202 [0.140, 0.259]). Within
sources the gain lives almost entirely in AgentDojo; SWE-bench shows none,
tau-bench and WebArena show small gains with intervals at zero. S2 portability
is not supported in any source. Full tables: `reports/gate3_results.md`.

## What changed

- DEVIATIONS 2026-10-23: model input set, incident exclusion, no latency
  feature, split rule. DEVIATIONS 2026-10-24: S1 deferred, S2 and GLM
  operationalised. No threshold changed.
- A bootstrap bug in the GLM (a feature present in only one source dropped
  out of resamples that excluded that source) crashed the first robustness
  run before any S2 or GLM number was written. Fixed with a regression test
  and the run repeated; the CV numbers are unchanged between runs.

## Hypothesis status

- H1: clauses 1 to 3 hold on the primary held-out evaluation; clause 4
  pending Phase 3. Not refuted. Caveat: domain concentration in AgentDojo.
- S1: not run, no reputation data.
- S2: not supported in any source.
- S3, S4: Phase 3.

## Blocked on the founder

- Gate 3 review (`reports/gate3_results.md`): three decisions listed there.
- Manipulation-cost dollar floor, required before Phase 3 starts.
- RPC_URL for the ERC-8004 collector.
- The data request email for arXiv 2606.26028 was sent; reply pending.
