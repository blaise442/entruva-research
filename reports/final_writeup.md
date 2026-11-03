# Does runtime telemetry predict AI agent failure? A preregistered 90-day study

Status: FINAL, version 1, published 2026-11-02 (day 16 of 90). The analysis is
complete. Publication before day 90 is recorded in docs/DEVIATIONS.md
(2026-11-02); any later result becomes a new dated version. Every number below is copied from a gate report in this directory,
which in turn names the result file under results/ that produced it. The
preregistration is docs/PREREGISTRATION.md, frozen at git tag prereg-v1 on
2026-10-19. Every analysis choice made after that tag is in docs/DEVIATIONS.md
with its date and decider; none changed a threshold.

## Verdict

H1 is supported under the preregistered rule, and gameable at the margin for
one agent in ten at no cost.

On the frozen held-out split, gradient boosting on telemetry reaches an AUC of
0.843 [0.777, 0.888] against 0.654 for the naive baseline, a Brier skill of
0.220 [0.049, 0.315], and a top-to-bottom quartile failure ratio of 4.14 with
monotone deciles. Under the preregistered median-agent reading of the
manipulation clause, no attack moves an agent one decile, so clause 4 passes in
all 16 scenario cells. Under the harsher any-agent reading, error suppression,
which costs nothing per run, moves one of the ten held-out agents from decile 6
to 5, and the verdict would be "predictive but gameable". Both readings are
stated here because the decile unit was fixed before any attack ran, and a
reader should see how much the verdict rests on it.

Three qualifications travel with the verdict. The pooled pass is carried by one
benchmark source, AgentDojo, which is 82 percent of rows; inside SWE-bench
telemetry is worse than the baseline. Cross-domain portability (S2) is not
supported anywhere. External validation on data outside the study was not
possible, because no available dataset joins agent telemetry to task outcomes.

## The question and the test

H1: runtime behavioral telemetry from AI agents (latency distributions, error
rates, tool-call sequences, output consistency) predicts task failure out of
sample better than a naive baseline, well enough to serve as a rating factor
for agent liability insurance.

H0: telemetry adds no predictive power beyond the naive baseline, or adds power
that is too small, too easy to manipulate, or too weak actuarially to support
its use as a rating factor.

The naive baseline sees only agent model identity, task type and task length.
H1 is supported only if all four clauses hold on the primary held-out
evaluation:

1. The lower bound of the telemetry model's 95 percent bootstrap AUC interval
   exceeds the baseline's point-estimate AUC by at least 0.05.
2. The Brier skill score against the baseline is above 0 with its interval
   excluding 0.
3. The failure rate in the top predicted-risk quartile divided by the bottom
   quartile is at least 2.0, and the decile lift table is monotone enough that
   higher predicted risk receives a higher premium.
4. The cheapest intervention that lowers an agent's predicted risk by one
   decile while its true failure rate is unchanged costs at least 3 times the
   annual premium saving that drop would produce, one-time attack cost against
   one year of saving.

If clauses 1 to 3 hold and 4 fails, the verdict is "predictive but gameable".
H1 is refuted if the telemetry AUC interval contains or lies below the baseline
point estimate, or the Brier skill is 0 or below. Anything else is
inconclusive. Clauses 1 to 3 were frozen with the preregistration; the dollar
floor in clause 4 was deferred at Gate 1 and set on 2026-10-25, after the
prediction results were known and before any adversarial run (DEVIATIONS
2026-10-19 and 2026-10-25). That ordering is stated so a reader can weigh it.

Four secondary hypotheses: S1, reputation components add predictive value
beyond telemetry; S2, a score learned in one task domain predicts failure in
another; S3, the cost to manipulate the score is measurable in dollars; S4, in
a simulation with premiums coupled to score, trust quality converges under some
adversarial fractions and collapses under others. S1 and S2 use the paired AUC
delta rule (lower 95 percent bound at least 0.05). S3 and S4 have no pass or
fail.

## Data

Five of six planned sources were obtained; the sixth, ERC-8004 registry
events, arrived in Phase 3 and carries no task outcomes. Benchmark traces with
ground-truth failure labels form the modelling set (Gate 2 data report,
2026-10-23).

| Source | Rows | Agents | Failure rate |
|---|---|---|---|
| AgentDojo | 36,678 | 29 | 0.456 |
| WebArena | 4,818 | 6 | 0.928 |
| tau-bench | 1,980 | 2 | 0.403 |
| SWE-bench agent runs | 1,167 | 4 | 0.817 |
| Modelling set | 44,643 | 41 | 0.514 |
| AI Incident Database (context only) | 274 | | 1.000 |

The 274 incident rows carry no telemetry and are all failures; they are
excluded from every model (DEVIATIONS 2026-10-23). Per-step latency, one of the
preregistered telemetry families, is missing in 100 percent of rows, as are
retry records. The models use tool-call sequences, error signals, message
lengths and task length. If telemetry had
failed, the absent latency family would have been a stated limitation, not a
loophole; it passed without it.

The held-out split is 20 percent of agents per source, frozen in
splits/primary_split.json before any model was fit, grouped by agent because
no benchmark row has a timestamp: 10 held-out agents with 9,298 rows (failure
rate 0.609), 31 training agents with 35,345 rows. A power simulation at Gate 2
put the minimum detectable AUC delta at 0.02, so sample size was not the
binding constraint; agent count was.

## Prediction (clauses 1 to 3)

Gate 3, 2026-10-25, results/2026-10-25_H1_primary.json. All intervals are 95
percent cluster bootstraps over agents, n_boot 2000, seed 20261017.

| Clause | Rule | Observed | Holds |
|---|---|---|---|
| 1 | telemetry AUC lower bound exceeds baseline AUC by 0.05 | 0.777 vs 0.654, margin 0.124 | yes |
| 2 | Brier skill above 0, interval excludes 0 | 0.220 [0.049, 0.315] | yes |
| 3 | quartile ratio at least 2.0, deciles monotone (Spearman above 0.8) | 4.14 (2,249.4 of 2,324 vs 544 of 2,325, averaged over 25 seeded tie-break draws), Spearman 1.00 | yes |

| Score | AUC [CI] | Paired delta vs baseline [CI] | Brier skill [CI] | Quartile ratio |
|---|---|---|---|---|
| Naive baseline (logistic: model identity, task type, task length) | 0.654 [0.528, 0.803] | | | |
| Gradient boosting, telemetry plus baseline inputs (primary) | 0.843 [0.777, 0.888] | 0.189 [0.067, 0.288] | 0.220 [0.049, 0.315] | 4.14 |
| Gradient boosting, telemetry only (sensitivity) | 0.839 [0.768, 0.885] | 0.186 [0.058, 0.290] | 0.233 [0.047, 0.326] | 4.04 |
| Logistic regression on the same features (reported, does not decide) | 0.767 [0.638, 0.849] | 0.113 [-0.004, 0.230] | 0.104 [-0.089, 0.213] | 2.84 |

The telemetry-only sensitivity matches the primary model, so the gain is not
model identity leaking through telemetry. The linear model would not pass
clauses 1 or 2: the signal is non-linear or interaction-heavy. The reliability
curve under-predicts in the 0.3 to 0.5 band (predicted 0.35 to 0.45, observed
0.49 to 0.63) and is close to the diagonal elsewhere; a premium schedule would
need recalibration on the target book, and ranking is what clause 3 tests.

Robustness: grouped 5-fold cross-validation over all 41 agents, pooled
out-of-fold on 44,643 rows, gives baseline AUC 0.590, gradient boosting 0.792
[0.755, 0.826], paired delta 0.202 [0.140, 0.259], Brier skill 0.218 [0.133,
0.281], quartile ratio 4.21. The primary result is not an artefact of one
split.

Within each source, which removes between-source base-rate differences:

| Source | Rows | Agents | Baseline AUC | GBM AUC [CI] | Paired delta [CI] | Brier skill [CI] |
|---|---|---|---|---|---|---|
| AgentDojo | 36,678 | 29 | 0.478 | 0.759 [0.723, 0.793] | +0.281 [+0.226, +0.333] | +0.237 [+0.152, +0.305] |
| SWE-bench | 1,167 | 4 | 0.592 | 0.564 [0.518, 0.688] | -0.028 [-0.121, +0.010] | -0.458 [-0.946, -0.040] |
| tau-bench | 1,980 | 2 | 0.648 | 0.667 [0.667, 0.707] | +0.020 [+0.020, +0.064] | +0.187 [+0.186, +0.190] |
| WebArena | 4,818 | 6 | 0.618 | 0.642 [0.579, 0.699] | +0.024 [-0.005, +0.053] | +0.077 [-0.001, +0.192] |

This is the main caveat on the verdict. The preregistered rule is pooled and it
passes; the claim that telemetry predicts failure across task domains is not
established. The founder declined at Gate 3 to add a within-source pass rule
after these numbers were seen, because adding a rule after the data is what
the preregistration exists to prevent.

Actuarial framing (descriptive, decides nothing): a Poisson GLM over all
benchmark rows with no source control gives relativities per one standard
deviation whose intervals exclude 1 for n_tool_calls 1.48 [1.32, 1.70],
repeat_call_ratio 1.13 [1.05, 1.23], error_rate 1.08 [1.04, 1.12], api_calls
0.90 [0.85, 0.99], mean_text_len 0.86 [0.82, 0.91] and task_length_steps 0.75
[0.65, 0.85]. More tool calls, more repeated identical calls and a higher error
rate load toward failure. This table is not a rating plan: it has no source
control and task length is measured in different units per source.

## Manipulation cost (clause 4)

Gate 4, 2026-10-28, results/2026-10-28_S3_attacks.json. Four feature-level
attacks, each stating the trace change an operator would make and moving every
feature the extractor would move: error suppression (errors become silent
identical retries), retry diversification, call shaping (padding calls added or
redundant calls dropped), message shaping (message length scaled). Per-run
cost is added text at the vendor's public list price; two attacks add no text
and cost nothing. The breakeven exposure for an attack is X* = (E + cR) / (3
dp), with E the one-time cost (0 or 10,000 USD), c the per-run cost, R runs per
year (1,000 or 100,000) and dp the drop in decile mean predicted probability.
Clause 4 passes in a scenario cell when the cheapest priced decile-moving
attack has X* above the cell's exposure (1,000 to 1,000,000 USD), and overall
only in every one of the 16 cells (DEVIATIONS 2026-10-27).

Under the preregistered reading, an attack moves one decile when it does so for
at least half of the held-out agents that can move. No attack does. Clause 4
passes in all 16 cells.

Under the any-agent reading, error suppression moves the Llama 3.3 70B
AgentDojo agent from decile 6 (mean predicted probability 0.560) to decile 5
(0.409), a dp of 0.151, at zero per-run cost. With E = 0 the breakeven is 0 USD
and every such cell fails; with E = 10,000 USD it is 22,087 USD, so the cells at
100,000 and 1,000,000 USD exposure fail too. Twelve of 16 cells fail.

The honest summary: the frozen scorer is hard to move for a typical agent by
editing telemetry alone, because most of its signal comes from model identity
and task type, which an operator cannot forge; but a single agent whose score
sits near a decile boundary can be nudged across for free. Five of the ten
held-out agents run on models with no public list price, so call shaping and
message shaping carry no dollar cost for them and by the preregistered rule an
unpriced attack is never the cheapest.

## Secondary hypotheses

S1, reputation ablation: not evaluable. The benchmark agents with telemetry and
outcomes have no on-chain identity, and the on-chain agents have no task
outcomes anywhere available to the study, so no join exists (DEVIATIONS
2026-10-27). Reported as not evaluable, not as failed.

S2, portability: not supported. For each source, gradient boosting trained on
the other sources' training agents (telemetry, step count, exit status) is
scored on that source's held-out agents against its in-domain naive baseline.

| Target source | Held-out agents | Cross-domain AUC | In-domain baseline AUC | Paired delta [CI] | Supported |
|---|---|---|---|---|---|
| AgentDojo | 6 | 0.669 | 0.529 | +0.139 [+0.035, +0.192] | no |
| WebArena | 2 | 0.507 | 0.673 | -0.166 [-0.199, -0.109] | no |
| SWE-bench | 1 | 0.595 | 0.700 | not evaluable (one agent) | no |
| tau-bench | 1 | 0.646 | 0.648 | not evaluable (one agent) | no |

S3, adversarial cost: reported above. On the reputation layer, from 400 sampled
Ethereum receipts at the block-day ETH price, one registration costs 0.17 USD,
one feedback event 0.10 USD, a Sybil campaign to the median feedback count
0.27 USD, and a five-agent collusion ring 1.93 USD. A fresh identity with as
much feedback as the median rated agent costs about a quarter of a dollar in
gas. No model in this study uses reputation, so these numbers bound what a
future reputation-weighted score would cost to game.

S4, flywheel: reported, synthetic, excluded from headline results
(results/2026-10-28_S4_flywheel_synthetic.json). 500 agents with true failure
rates resampled from the held-out agents, 12 rounds, the insurer refitting the
Phase 2 model class each round on gamed telemetry, rational attackers using the
free attack when it pays. No collapse in any cell: AUC after burn-in is 0.756
to 0.757 at every attacker fraction from 0 to 1, against a baseline of 0.654. Neither
preregistered outcome fired by its fixed rule: "converged" required AUC inside
the Phase 2 interval [0.777, 0.888], which sits above the ceiling of a
population whose outcomes are Bernoulli draws. "No collapse" is close to
guaranteed by construction, because model identity, which no attack touches,
nearly identifies the source agents. The band was kept as fixed and the
mismatch is reported as a limitation, not patched (Gate 4 decision 2).

## The reputation layer across three chains

ERC-8004 identity and reputation registry events were collected in full on
Ethereum mainnet (to 2026-10-25, keyless public endpoint), and on Base and BNB
Smart Chain (to 2026-11-02, paid endpoint, spend approved 2026-11-01). Every
file passes an integrity check: registration ids contiguous from zero and equal
to the mint set, every feedback index sequence contiguous from one, no
duplicate log (Gate 5 report, update of 2026-11-02).

| Full history | Ethereum | Base | BNB Smart Chain |
|---|---|---|---|
| Agents registered | 55,407 | 1,149,957 | 401,341 |
| Feedback events | 34,493 | 673,980 | 30,144 |
| Agents receiving feedback | 2,651 | 152,281 | 4,482 |
| Of those, with a single giver | 2,444 (0.92) | 138,387 (0.91) | 3,988 (0.89) |
| Distinct feedback givers | 721 | 136,371 | 143 |
| Feedback per rated agent (median, p75, max) | 1, 9, 636 | 1, 1, 390,890 | 1, 1, 234 |
| Share of feedback from registrant wallets | 0.015 | 0.224 | 0.015 |

On every chain the median rated agent has one feedback entry from one wallet.
Base differs in scale, not shape: one agent holds 390,890 of its 673,980
entries. Any reputation component built on these registries must weight
feedback by something other than its count.

## External validation

Phase 4 was planned as validation of the H1 model on external data. It could
not happen: the data request to the authors of arXiv 2606.26028 (sent week 1)
is unanswered, their dataset has no public release, and no public ERC-8004
source carries task outcomes (DEVIATIONS 2026-10-28). Phase 4 was reduced to a
fidelity check of the collection, with rules fixed before the run.

The Ethereum collection was compared row for row with the public Harvard
Dataverse dataset doi:10.7910/DVN/HJZW8Q (CC0 1.0, the first 10,000 ERC-8004
agents) with zero tolerance. All 10,000 mint blocks, transaction hashes and
owners agree; all 1,961 transfer rows and all 980 feedback rows exist in our
logs with the same values; their feedback counts are at most ours for all
10,000 agents and equal for 9,991. The one inferred quantity is the dataset's
observation block (24,744,960), which its data dictionary does not state. A
second-source count check against the 8004scan public API passes on all three
chains. This establishes that the reputation descriptives rest on a faithful
collection; it says nothing about predictive validity.

## Deviations from the preregistration

Thirteen entries, none changing a threshold. Each names its decider and whether
it was made before or after the result it affects was known.

| Date | What | Timing |
|---|---|---|
| 2026-10-19 | Clause 4 dollar floor deferred at Gate 1 | before any data |
| 2026-10-23 | Model input set, incident exclusion, latency absent, agent-grouped split, monotonicity as Spearman above 0.8 | before any model fit |
| 2026-10-24 | S1 deferred (no reputation data), S2 and GLM operationalised | before S2 or GLM results |
| 2026-10-25 | Dollar floor set at 3 times annual saving | after prediction results, before any attack |
| 2026-10-27 | S1 not evaluable (no join exists) | before Phase 3 |
| 2026-10-27 | Attack set, decile unit, breakeven formula, scenario grid, pricing | before any attack run |
| 2026-10-27 | S4 constants and outcome rules | before the simulation was written |
| 2026-10-28 | Seven Phase 3 corrections from a whole-branch review, then a rerun | after the first run's numbers, before the rerun; neither verdict changed |
| 2026-10-28 | Phase 4 reduced to collection cross-checks | after the data request went unanswered |
| 2026-10-28 | Cross-check rules, zero tolerance | before the run |
| 2026-10-29 | Base and BNB reduced to a two-day window at zero spend | before the run; superseded 2026-11-02 |
| 2026-11-02 | Base and BNB full history through a paid endpoint; collector capped at 10,000 blocks after a silent truncation was found | after the windowed run; statistics unchanged |
| 2026-11-02 | Write-up and paper published at day 16 rather than day 90; research repository opened with full history | after all results were known; timing only |

## Limitations

- Domain concentration. One source is 82 percent of rows and 72 percent of the
  held-out set. Telemetry is worse than the baseline inside SWE-bench and a
  small gain with intervals touching zero inside tau-bench and WebArena.
- Few agents. 41 in total, 2 to 6 in three of four sources; the cluster
  bootstrap is honest about this and intervals are wide or degenerate.
- Benchmarks, not production. Failure here is a benchmark task outcome, not an
  insured loss, and benchmark agents are not production agents.
- Missing telemetry families. No source publishes per-step latency or retries.
- Attacks are feature-level. A real operator rewriting traces could find
  interactions in either direction that the four attacks miss. The one-time
  engineering cost is a parameter, not a measurement. Five of ten held-out
  agents are unpriced.
- Ten held-out agents make the decile unit coarse; the median and any-agent
  readings of clause 4 disagree.
- The simulation is synthetic, its convergence band sits above its ceiling,
  and its no-collapse result is close to guaranteed by construction.
- No external validation of the model. Reputation data and telemetry data do
  not join anywhere available.
- The dollar floor was set after the prediction results were known, and the
  Phase 3 corrections were made after the first adversarial run's numbers were
  known. Both are dated in DEVIATIONS; neither changed a verdict.

## What would change the verdict

Traces from more agents in SWE-bench, tau-bench and WebArena, or a new source,
would test whether the pooled pass survives outside AgentDojo. Per-step
latency from any source would add the missing feature family. A dataset
joining on-chain agent identity to task outcomes would make S1 evaluable and
allow external validation. A reply from the arXiv 2606.26028 authors would add
a third cross-check of the collection but not outcomes.

## How to verify

- Preregistration: docs/PREREGISTRATION.md at tag prereg-v1, commit 8f74d7e.
- Code: src/ in this repository, every fetcher, feature, model and attack.
- Data: data/MANIFEST.md, one entry per source with URL or contract address,
  fetch date, checksum and license; raw files reproduce from it.
- Split and seeds: splits/primary_split.json; seed 20261017 throughout.
- Results: results/*.json, each embedding the git commit, manifest hash, seeds
  and timestamp; figures beside them. Synthetic outputs carry "synthetic" in
  the filename.
- Deviations: docs/DEVIATIONS.md.
- Reports: reports/gate2_data_report.md through gate5_results.md and
  reports/week_NN.md.

The repository is private until this write-up is final and opens with its full
history on publication.

## Timeline

| Checkpoint | Planned | Actual |
|---|---|---|
| Preregistration frozen | day 30 | day 2 (2026-10-19) |
| Data acquired, split frozen, baseline fit | day 30 | day 6 (2026-10-23) |
| Telemetry models fit, first out-of-sample results | day 60 | day 8 (2026-10-25) |
| Manipulation cost and actuarial lift | day 90 | day 11 (2026-10-28) |
| Collection cross-checks, three-chain reputation descriptives | not planned | day 12 and day 16 |
| Final write-up | day 90 (2027-01-15) | day 16 (2026-11-02), published early, DEVIATIONS 2026-11-02 |

## Open at publication

- Weekly reports continue to day 90.
- The data request to the arXiv 2606.26028 authors is unanswered.
- No further spend, collection or analysis is planned.
