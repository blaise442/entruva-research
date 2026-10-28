# Week 3 report (2026-10-26 to 2026-10-28)

## What ran

- Gate 3 approved 2026-10-25 with the dollar floor set and S2 reported as not
  supported. The ERC-8004 registries were collected from Ethereum mainnet on
  2026-10-25 (275,118 identity events, 34,535 reputation events) through a
  keyless public endpoint after Alchemy's free tier proved unusable for a
  1.9 million block scan.
- Phase 3 designed with the founder 2026-10-26 to 27 (attacker model, S1 not
  evaluable, breakeven table instead of an invented premium, scorer-refit
  flywheel) and executed 2026-10-27 to 28: nine plan tasks, 36 new tests, suite
  at 137.
- Four telemetry attacks priced against the frozen Phase 2 scorer; the clause 4
  breakeven table under two readings; the reputation layer described and its
  attacks priced from 400 real receipts; the flywheel simulation run over 16
  scenario cells and 21 attacker fractions.

## Results in one paragraph

Editing telemetry alone does not move the typical held-out agent a decile: under
the preregistered median-agent reading no attack qualifies and clause 4 passes,
so H1 is supported. Under the harsher any-agent reading a free attack (swallow
errors, retry silently) moves one of ten agents across a decile boundary and
clause 4 fails, which would make the verdict "predictive but gameable". The
scorer resists manipulation mostly because its signal sits in model identity and
task type, which an operator cannot forge. On-chain, reputation is cheap to
fake: a fresh identity with as much feedback as the median rated agent costs
about 27 cents in gas, and 92 percent of rated agents have a single feedback
giver. The flywheel does not collapse: a scorer refit each round on gamed
telemetry stays flat at AUC 0.757 from no attackers to all attackers.

## What changed

- DEVIATIONS 2026-10-27: S1 not evaluable; attack, decile and breakeven
  definitions; S4 constants. All fixed before any run.
- Collector: 429 backoff, deployment-block start, chunk regrowth (PR 13).
- New packages src/adversarial and src/simulation; price table and measured
  chars-per-token ratios under data/prices; pinned ERC-8004 ABI under data/abi.

## Hypothesis status

- H1: clauses 1 to 3 hold (Gate 3). Clause 4 passes under the median-agent
  reading and fails under the any-agent reading; the Gate 4 decision is which
  reading the final write-up leads with.
- S1: not evaluable with available data.
- S2: not supported (Gate 3).
- S3: reported; cheapest effective attack is free per run.
- S4: reported; no collapse boundary on the grid.

## Blocked on the founder

- Gate 4 decisions (reports/gate4_results.md, last section).
- Reply to the arXiv data request, which decides whether Phase 4 (external
  validation) can run.
