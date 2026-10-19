# Preregistration: telemetry as a rating factor for agent liability insurance

Study start: 2026-10-17 (day 0). Day 90: 2027-01-15. Frozen at tag prereg-v1; commit hash recorded here after tagging: TODO(tag). Design decisions: ../../docs/superpowers/specs/2026-10-19-research-study-design.md. Public criteria: ../../docs/EXPERIMENT_SCOPE.md and the live /research page; this document matches them in substance and pins every analysis choice they leave open. Deviations after the tag go to DEVIATIONS.md with date, reason, and decider; the hypotheses and thresholds below do not change.

## Hypotheses

H1: Runtime behavioral telemetry from AI agents (latency distributions, error rates, tool-call sequences, output consistency) predicts task failure out of sample better than the naive baseline, well enough to serve as a rating factor for agent liability insurance.

H0: Telemetry adds no predictive power beyond the naive baseline, or adds power that is too small, too easy to manipulate, or too weak actuarially to support its use as a rating factor.

The naive baseline sees only agent model identity, task type, and task length (the published definition). If telemetry cannot beat this, it is not adding information.

Secondary:

S1 (reputation ablation): non-telemetry reputation components (interaction history, peer feedback) add predictive value beyond telemetry alone.

S2 (portability): a score learned on one task domain predicts failure in another domain.

S3 (adversarial): the cost to manipulate the score by whitewashing, Sybil feedback, collusion, or strategic oscillation is measurable and is reported in compute or dollars.

S4 (flywheel): in an agent-based simulation where premiums are coupled to score, aggregate trust quality converges under at least some adversarial fractions and collapses under others; the boundary is reported.

## Thresholds (fixed now; identical in substance to the published criteria)

H1 is supported only if all of the following hold on the primary held-out evaluation:

1. The lower bound of the 95% bootstrap confidence interval of the telemetry model's AUC exceeds the baseline's point-estimate AUC by at least 0.05.
2. The Brier skill score against the baseline is above 0 with its 95% bootstrap interval excluding 0.
3. The failure rate in the top predicted-risk quartile divided by the bottom quartile is at least 2.0, and ranking by the score would move a hypothetical premium schedule in the correct direction (the decile lift table is monotone enough that higher predicted risk receives a higher premium).
4. The cost of the cheapest S3 intervention that lowers an agent's predicted risk by one decile while its true failure rate is unchanged is at least the founder's dollar floor. Floor: TODO(founder). If unset at Gate 1, it must be fixed before Phase 3 begins and the delay is logged in DEVIATIONS.md.

A calibration (reliability) curve is reported in every case. If 1 to 3 hold and 4 fails, the published verdict is "predictive but gameable", not supported. H1 is refuted if the telemetry model's AUC interval contains or lies below the baseline AUC point estimate, or the Brier skill score is 0 or below. Anything else is inconclusive; we say so and state what data would resolve it. A refutation is a valid, publishable result.

S1 and S2 are supported when the lower bound of the 95% CI of the paired AUC delta (auc_delta_with_ci, same resamples for both scores) is at least 0.05: S1 compares combined (telemetry plus reputation components) against telemetry alone; S2 compares the cross-domain score against the in-domain naive baseline. S3 and S4 have no pass or fail; they produce reported numbers and plots.

Quartile ties and small cells: ties in predicted risk are broken by a seeded random key and the ratio is averaged over 25 draws; the per-quartile failure counts and sizes are always reported next to the ratio, and a ratio of inf (zero failures in the bottom quartile) is reported as inf with its counts, never as a bare pass.

## Analysis plan (fixed before any data is loaded)

Baseline: one logistic regression on one-hot agent model identity, one-hot task type, and standardized task length (src/models/baselines.py naive_baseline). This is the only baseline for clauses 1 and 2.

Telemetry model: the primary model is gradient boosting (sklearn HistGradientBoostingClassifier, library defaults, random_state 20261017); a logistic regression on the same features is reported alongside but does not decide H1. No deep models unless the Gate 2 data report justifies the sample size.

Primary evaluation: a single held-out split frozen before any model is fit, temporal where timestamps allow and otherwise grouped by agent identity, with the split files committed to the repo. Grouped 5-fold cross-validation by agent identity (src/models/validation.py, shuffle seed 20261017) is reported as a robustness check with pooled out-of-fold predictions. No agent appears in both train and test anywhere; the splitter raises on any violation and the leakage check is run and reported explicitly.

Uncertainty: 95% bootstrap confidence intervals with n_boot 2000 and seed 20261017 throughout. Where rows cluster by agent, the bootstrap resamples whole agents (cluster bootstrap); otherwise it is stratified by class so no resample loses a class. A bootstrap that cannot keep n_boot valid resamples raises rather than reporting a quiet interval (src/models/metrics.py).

Metrics: AUC with CI, paired AUC delta with CI, Brier skill score with CI, reliability diagram, lift chart by decile (seeded tie-breaks), top-to-bottom quartile failure ratio with counts. Actuarial framing: a Poisson or Tweedie GLM frequency model on telemetry features, reporting relativities with CIs. A power estimate against the thresholds above is due at Gate 2 and determines whether the collected data can support the preregistered test; if not, scope reduction is proposed in DEVIATIONS.md and work pauses for founder review.

Every result is a JSON file plus figures in results/, named by date and hypothesis, embedding git commit hash, data manifest hash, random seeds, and timestamp (src/common/provenance.py; the dirty flag is scoped to the research tree). Nothing in notebooks/ is a result.

## Planned data sources

ERC-8004 Identity, Reputation, and Validation registry events on Ethereum mainnet and Base (contract addresses verified from eips.ethereum.org/EIPS/eip-8004 and the erc-8004 GitHub org, never guessed). Benchmark traces with ground-truth failure labels: tau-bench, SWE-bench agent runs, AgentDojo, WebArena, preferring published trace releases; any generated traces require approved spend first. AI Incident Database and OECD AI Incidents Monitor, filtered to agentic or automated-action cases by a documented rule stored in code. Policy wordings and rate filings are context only, never model data. Every source is recorded in data/MANIFEST.md with URL or contract address, fetch date, method, row count, checksum, license, and known limitations. An unobtainable source is recorded as such and never substituted silently; synthetic data is labeled synthetic in the filename and excluded from headline results.
