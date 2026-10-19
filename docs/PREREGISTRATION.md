# Preregistration: telemetry as a rating factor for agent liability insurance

Study start: 2026-10-17 (day 0). Day 90: 2027-01-15. Frozen at tag prereg-v1; commit hash recorded here after tagging: TODO(tag). Design decisions: ../../docs/superpowers/specs/2026-10-19-research-study-design.md. Public criteria: ../../docs/EXPERIMENT_SCOPE.md and the live /research page. Deviations after the tag go to DEVIATIONS.md with date, reason, and decider; the hypotheses and thresholds below do not change.

## Hypotheses

H1: Runtime behavioral telemetry from AI agents (latency distributions, error rates, tool-call sequences, output consistency) predicts task failure out of sample better than a naive baseline.

H0: Telemetry features add no predictive value over the baseline (prior failure rate by agent class, and task count).

Secondary:

S1 (reputation ablation): non-telemetry reputation components (interaction history, peer feedback) add predictive value beyond telemetry alone.

S2 (portability): a score learned on one task domain predicts failure in another domain.

S3 (adversarial): the cost to manipulate the score by whitewashing, Sybil feedback, collusion, or strategic oscillation is measurable and is reported in compute or dollars.

S4 (flywheel): in an agent-based simulation where premiums are coupled to score, aggregate trust quality converges under at least some adversarial fractions and collapses under others; the boundary is reported.

## Thresholds (fixed now; identical in substance to the published criteria)

H1 is supported only if all of the following hold on held-out data:

1. The lower bound of the 95% bootstrap confidence interval of the telemetry model's AUC exceeds the baseline AUC by at least 0.05.
2. The Brier skill score against the baseline is above 0 with its 95% bootstrap interval excluding 0.
3. The failure rate in the top predicted-risk quartile divided by the bottom quartile is at least 2.0.
4. The cost to manipulate an agent's predicted risk down by one decile, from the S3 adversarial tests, is at least the founder's dollar floor. Floor: TODO(founder). If unset at Gate 1, it must be fixed before Phase 3 begins and the delay is logged in DEVIATIONS.md.

A calibration (reliability) curve is reported in every case. If 1 to 3 hold and 4 fails, the published verdict is "predictive but gameable", not supported. H1 is refuted if the AUC interval overlaps the baseline AUC or the Brier skill score is 0 or below; anything else is inconclusive and is published as such. A refutation is a valid, publishable result.

S1 and S2 use the rule in clause 1 applied to the relevant AUC delta (combined vs telemetry-only for S1; cross-domain vs in-domain baseline for S2). S3 and S4 have no pass or fail; they produce reported numbers and plots.

## Analysis plan (fixed before any data is loaded)

Baselines: (a) agent-class prior failure rate, (b) task count only, (c) logistic regression on both combined. Models: logistic regression and gradient boosting on telemetry features; no deep models unless the Gate 2 data report justifies the sample size. Validation: grouped cross-validation by agent identity so no agent appears in both train and test, with explicit leakage checks (src/models/validation.py asserts group disjointness); temporal split where timestamps allow. Metrics: AUC with bootstrap CI, Brier skill score with CI, reliability diagram, lift chart by decile, top-to-bottom quartile failure ratio (src/models/metrics.py, written and tested before data collection). Actuarial framing: a Poisson or Tweedie GLM frequency model on telemetry features, reporting relativities with CIs. A power estimate against the thresholds above is due at Gate 2 and determines whether the collected data can support the preregistered test; if not, scope reduction is proposed in DEVIATIONS.md and work pauses for founder review.

Every result is a JSON file plus figures in results/, named by date and hypothesis, embedding git commit hash, data manifest hash, random seeds, and timestamp (src/common/provenance.py). Nothing in notebooks/ is a result.

## Planned data sources

ERC-8004 Identity, Reputation, and Validation registry events on Ethereum mainnet and Base (contract addresses verified from eips.ethereum.org/EIPS/eip-8004 and the erc-8004 GitHub org, never guessed). Benchmark traces with ground-truth failure labels: tau-bench, SWE-bench agent runs, AgentDojo, WebArena, preferring published trace releases; any generated traces require approved spend first. AI Incident Database and OECD AI Incidents Monitor, filtered to agentic or automated-action cases by a documented rule stored in code. Policy wordings and rate filings are context only, never model data. Every source is recorded in data/MANIFEST.md with URL or contract address, fetch date, method, row count, checksum, license, and known limitations. An unobtainable source is recorded as such and never substituted silently; synthetic data is labeled synthetic in the filename and excluded from headline results.
