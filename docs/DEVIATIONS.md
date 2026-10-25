# Deviations from PREREGISTRATION.md

Format for each entry:

## YYYY-MM-DD: short title
- What changed:
- Why:
- Decided by:
- Effect on preregistered thresholds: none | <explanation>

## 2026-10-19: manipulation-cost dollar floor deferred
- What changed: threshold clause 4's dollar floor was not set at Gate 1.
- Why: the founder deferred it; per the preregistration it must be fixed before Phase 3 (adversarial work) begins.
- Decided by: founder, Gate 1.
- Effect on preregistered thresholds: none yet; clause 4 cannot be evaluated until the floor is set, and setting it after adversarial data exists would be a further deviation.

## 2026-10-23: Phase 2 analysis clarifications (no threshold change)
- What changed: (1) The primary telemetry model is gradient boosting on telemetry features plus every input the naive baseline sees (model identity, task type, task length), so the paired delta measures the incremental value of telemetry as a rating factor. A telemetry-only variant (no model identity) is reported as a sensitivity. (2) Incident rows are excluded from all models: they carry no telemetry and are all failures. (3) Per-step latency cannot be built (no source publishes it); the only duration is AgentDojo's per-run total, used as a feature where present. (4) Held-out split is by whole agents per benchmark source (20 percent, ceil), frozen in research/splits/primary_split.json before any model was fit, because no benchmark row has a timestamp.
- Why: the preregistration fixes the model class, seeds and metrics but not the input set; these choices were made before any model was fit or any test label inspected.
- Decided by: executing agent during Phase 2, for founder review at Gate 3.
- Effect on preregistered thresholds: none.

## 2026-10-24: S1 not run in Phase 2; S2 and GLM operationalised (no threshold change)
- What changed: (1) S1 (reputation components added to telemetry) is not run: no reputation data exists yet because the ERC-8004 collection waits on an RPC endpoint and the external dataset request is unanswered. S1 is deferred, not failed. (2) S2 is operationalised as: for each benchmark source, a gradient boosting model is trained on the other sources' train agents using telemetry, step count and exit status only (model identity and task type do not overlap across sources), scored on that source's held-out agents from the frozen split, and paired against that source's in-domain naive baseline with the preregistered paired cluster-bootstrap AUC delta. (3) The actuarial framing is a Poisson GLM on standardized telemetry features over all benchmark rows, reporting relativities per one-SD increase with cluster-bootstrap CIs over agents. It is descriptive and decides no clause.
- Why: the preregistration names S1, S2 and the GLM but fixes neither the cross-domain training set nor the GLM inputs; these choices were made before the S2 or GLM results were inspected.
- Decided by: executing agent during Phase 2, for founder review at Gate 3.
- Effect on preregistered thresholds: none. The S2 rule (paired AUC delta lower CI bound at least 0.05) is applied unchanged.
