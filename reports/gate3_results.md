# Gate 3 results: H1 on the frozen held-out split

Phase 2 closed 2026-10-25 (day 8 of 90; the checkpoint was day 60). Everything
below is computed by `src/models/run_primary.py` and `src/models/run_robustness.py`
from `data/processed/features.csv`, with seeds, commit hash and manifest hash in
the result files `results/2026-10-23_H1_primary.json` and
`results/2026-10-25_H1_robustness_cv.json`. The analysis plan is
`docs/PREREGISTRATION.md` (tag prereg-v1); the two Phase 2 clarifications are in
`docs/DEVIATIONS.md` (2026-10-23, 2026-10-24) and change no threshold.

## Verdict on the preregistered clauses

Primary held-out evaluation: 10 agents, 9,298 rows, failure rate 0.609, trained
on the other 31 agents (35,345 rows). Baseline is the preregistered logistic
regression on model identity, task type and task length. Telemetry model is
gradient boosting on those inputs plus telemetry. All intervals are 95 percent
cluster bootstraps over agents, n_boot 2000.

| Clause | Rule | Observed | Holds |
|---|---|---|---|
| 1 | telemetry AUC CI lower bound exceeds baseline AUC by 0.05 | 0.777 vs 0.654, margin 0.124 | yes |
| 2 | Brier skill above 0, CI excludes 0 | 0.220 [0.049, 0.315] | yes |
| 3 | top/bottom quartile failure ratio at least 2.0, decile lift monotone | 4.14 (2249.4 of 2324 vs 544 of 2325), Spearman 1.00 | yes |
| 4 | cheapest S3 manipulation costs at least the founder's dollar floor | not run (Phase 3); floor still unset | pending |

Refutation rule: not triggered. The telemetry AUC interval [0.777, 0.888] lies
above the baseline point estimate and the Brier skill is positive.

Status under the preregistration: clauses 1 to 3 hold, clause 4 is untested.
H1 is therefore neither supported nor refuted yet. The published verdict is
pending Phase 3; if clause 4 fails there the verdict is "predictive but
gameable".

Supporting numbers on the same split:

| Score | AUC [CI] | paired delta vs baseline [CI] | Brier skill [CI] | quartile ratio |
|---|---|---|---|---|
| baseline | 0.654 [0.528, 0.803] | | | |
| gradient boosting (primary) | 0.843 [0.777, 0.888] | 0.189 [0.067, 0.288] | 0.220 [0.049, 0.315] | 4.14 |
| gradient boosting, telemetry only (sensitivity, no model identity) | 0.839 [0.768, 0.885] | 0.186 [0.058, 0.290] | 0.233 [0.047, 0.326] | 4.04 |
| logistic regression (reported, does not decide) | 0.767 [0.638, 0.849] | 0.113 [-0.004, 0.230] | 0.104 [-0.089, 0.213] | 2.84 |

The telemetry-only sensitivity matches the primary model, so the gain is not
model identity leaking through telemetry. The linear model would not pass
clauses 1 or 2: the signal is non-linear or interaction-heavy.

Calibration: the reliability curve (`results/2026-10-23_H1_reliability.png`)
under-predicts in the 0.3 to 0.5 band (predicted 0.35 to 0.45, observed 0.49
to 0.63) and is close to the diagonal elsewhere. A premium schedule would need
recalibration on the target book; ranking is what clause 3 tests.

## Robustness: grouped 5-fold cross-validation, all 41 agents

Pooled out-of-fold, 44,643 rows: baseline AUC 0.590, gradient boosting 0.792
[0.755, 0.826], paired delta 0.202 [0.140, 0.259], Brier skill 0.218
[0.133, 0.281], quartile ratio 4.21. The primary result is not an artefact of
the one split.

Within each source, which removes between-source base-rate differences:

| Source | rows | agents | failure rate | baseline AUC | GBM AUC [CI] | paired delta [CI] | Brier skill [CI] | quartile |
|---|---|---|---|---|---|---|---|---|
| agentdojo | 36,678 | 29 | 0.456 | 0.478 | 0.759 [0.723, 0.793] | +0.281 [+0.226, +0.333] | +0.237 [+0.152, +0.305] | 3.96 |
| swe-bench | 1,167 | 4 | 0.817 | 0.592 | 0.564 [0.518, 0.688] | -0.028 [-0.121, +0.010] | -0.458 [-0.946, -0.040] | 1.12 |
| tau-bench | 1,980 | 2 | 0.403 | 0.648 | 0.667 [0.667, 0.707] | +0.020 [+0.020, +0.064] | +0.187 [+0.186, +0.190] | 2.59 |
| webarena | 4,818 | 6 | 0.928 | 0.618 | 0.642 [0.579, 0.699] | +0.024 [-0.005, +0.053] | +0.077 [-0.001, +0.192] | 1.10 |

This is the main caveat on the verdict. The pooled pass is carried by
AgentDojo, which is 82 percent of rows and 72 percent of the held-out test set.
Inside SWE-bench telemetry is worse than the baseline; inside tau-bench and
WebArena it is a small gain with intervals touching zero. Intervals for
tau-bench are near-degenerate because the cluster bootstrap resamples two
agents. The preregistered rule is pooled and it passes; the claim that
telemetry predicts failure across task domains is not yet established.

## S2 portability: not supported

For each source, a gradient boosting model trained on the other sources' train
agents (telemetry, step count, exit status only) is scored on that source's
held-out agents and paired against the source's own in-domain naive baseline.
Rule: paired AUC delta CI lower bound at least 0.05.

| Target source | held-out rows | held-out agents | cross-domain AUC | in-domain baseline AUC | paired delta [CI] | supported |
|---|---|---|---|---|---|---|
| agentdojo | 6,744 | 6 | 0.669 | 0.529 | +0.139 [+0.035, +0.192] | no |
| swe-bench | 289 | 1 | 0.595 | 0.700 | -0.105 [-0.105, -0.105] | no |
| tau-bench | 660 | 1 | 0.646 | 0.648 | -0.003 [-0.003, -0.003] | no |
| webarena | 1,605 | 2 | 0.507 | 0.673 | -0.166 [-0.199, -0.109] | no |

S2 fails everywhere. The only positive transfer is into AgentDojo and its lower
bound is 0.035. SWE-bench and tau-bench have one held-out agent each, so the
cluster bootstrap cannot form an interval there (zero width is reported, not a
precise estimate). The split is 20 percent of agents per source, so sources
with 2 or 4 agents hold out 1.

S1 (reputation components) was not run: no reputation data exists yet. See
DEVIATIONS.md 2026-10-24.

## Actuarial framing: Poisson GLM relativities

Descriptive only, all benchmark rows, relativity per one standard deviation
increase, cluster bootstrap CIs over agents. Features whose interval excludes 1:

| Feature | relativity [CI] |
|---|---|
| n_tool_calls | 1.48 [1.32, 1.70] |
| repeat_call_ratio | 1.13 [1.05, 1.23] |
| error_rate | 1.08 [1.04, 1.12] |
| api_calls | 0.90 [0.85, 0.99] |
| mean_text_len | 0.86 [0.82, 0.91] |
| task_length_steps | 0.75 [0.65, 0.85] |

n_distinct_tools, n_errors, max_error_run, duration_s and tokens_sent have
intervals containing 1. More tool calls, more repeated identical calls and a
higher error rate load toward failure; longer tasks and longer messages load
away from it, which is consistent with benchmarks where agents that give up
early fail. Relativities are marginal to the other features and are not a
rating plan.

## Limitations

- Domain concentration: one source dominates every pooled number (see the
  within-source table). The next data that would change this is traces from
  more agents in SWE-bench, tau-bench and WebArena, or a new source.
- Few agents per source: 41 agents in total, 2 to 6 in three of four sources.
  Cluster bootstrap intervals are honest about this and are wide or degenerate.
- No latency telemetry: no source publishes per-step latency, so one of the
  three preregistered telemetry families is absent (DEVIATIONS 2026-10-23).
- Incident rows (274) are excluded from all models: no telemetry, all failures.
- Benchmarks, not production: failure here is a benchmark task outcome, not
  an insured loss.
- Clause 4 and the dollar floor: Phase 3 cannot start until the founder sets
  the floor (deferred since Gate 1).

## Decision requested at Gate 3

1. Accept the H1 clause 1 to 3 result as written, including the domain
   concentration caveat, or ask for a within-source rule to be added as a
   secondary report (that would be a deviation and is proposed, not done).
2. Set the manipulation-cost dollar floor so Phase 3 can begin.
3. Confirm S2 is reported as not supported, with a note that two sources had
   one held-out agent.
