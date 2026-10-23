# Week 1 report (2026-10-17 to 2026-10-23)

## What ran

- Phase 0 closed at Gate 1: preregistration frozen as prereg-v1 (hypotheses,
  thresholds, analysis plan, baselines), pinned environment, provenance and
  manifest utilities, 25 tests.
- Phase 1 data collection executed: unified trace schema, manifest writer and
  checksum verifier, and fixture-tested parsers for five sources. All raw
  artifacts carry URL, fetch date, row count, SHA-256, license, and
  limitations in data/MANIFEST.md; verify_manifest passes against every file.
- Collected: tau-bench authors' trajectories (1,980 traces, 4 files),
  SWE-bench lite official SWE-agent submissions (1,167 traces, 4 models),
  AgentDojo full published runs (36,678 traces, including injection attacks),
  WebArena official v2 execution traces (4,818 traces, 6 configurations,
  8.3 GB), and the AI Incident Database weekly snapshot (274 agentic
  incidents of 1,751, kept by the documented keyword rule).
- The unified index holds 44,917 rows across 41 benchmark agents;
  `make reproduce` rebuilds the index and the dated data report from raw and
  verifies manifest checksums first. Test suite: 65 passing.
- Gate 2 power simulation implemented (cluster bootstrap, correlated agents);
  the full n_sims=500 run on the real row counts is executing and lands in
  the Gate 2 package.

## What changed

- gdown was added to the pinned dependencies (the WebArena distribution is a
  Google Drive folder that the standard library cannot list).
- SWE-bench scope: 4 official SWE-agent submissions with a uniform .traj
  format; the other 59 lite submissions publish trajectories in
  heterogeneous per-harness formats (~25 GB) and are excluded as a MANIFEST
  limitation, revisitable.
- The OECD AI Incidents Monitor publishes no export or API (verified
  2026-10-22), recorded as a MANIFEST limitation.
- A status bar showing experiment phase progress was added to /research on
  the website.

## Hypothesis status

- H1 (telemetry predicts failure beyond the naive baseline): untested; no
  model has been fit. Data readiness is the Gate 2 question.
- S1 to S4: untested; Phase 2 and later.
- Known data weakness for H1: no source publishes per-step latency (missing
  in 100% of rows), so the latency-distribution feature family will be
  unavailable unless traces are regenerated (spend gate) or a dataset owner
  shares richer traces (request drafted, see below).

## Deviations

- None against the preregistration this week. The manipulation-cost dollar
  floor remains deferred (logged 2026-10-19); it must be set before Phase 3.

## Blocked on the founder

- RPC_URL for the ERC-8004 collector (research/.env); the collector is ready
  and the gap is logged in MANIFEST.md.
- Manipulation-cost dollar floor, due before Phase 3.
- Sending reports/email-2606.26028-data-request.md (data request for the
  ERC-8004 ecosystem dataset behind arXiv 2606.26028).
- Gate 2 review once the package lands: proceed to Phase 2 or reduce scope.
