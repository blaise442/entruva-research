# Entruva 90 day study

A preregistered empirical study: can runtime behavioral telemetry from AI agents predict task failure out of sample better than a naive baseline, well enough to serve as a rating factor for agent liability insurance? Hypotheses, thresholds, and the analysis plan are frozen in docs/PREREGISTRATION.md (tag prereg-v1). Design decisions and repo adaptations: ../docs/superpowers/specs/2026-10-19-research-study-design.md. Deviations are logged in docs/DEVIATIONS.md.

Day convention: day 0 is 2026-10-17, day 90 is 2027-01-15. All reports use this convention.

## Status

Phase 4 closed 2026-10-29 (day 12) and Gate 5 closed 2026-11-02 (day 16); analysis is complete and the weekly reports run to day 90, with the write-up due 2027-01-15. H1 clauses 1 to 3 hold on the frozen held-out split (Gate 3). Clause 4 passes under the preregistered median-agent reading and fails under the any-agent reading (reports/gate4_results.md); the verdict is supported under the preregistered rule, gameable at the margin. S1 is not evaluable, S2 is not supported, S3 and S4 are reported. The Ethereum collection matches the public Dataverse dataset row for row, and the Base and BNB registries are fetched in full (reports/gate5_results.md). Weekly reports are reports/week_NN.md. The final write-up is drafted in reports/final_writeup.md and becomes final on 2027-01-15.

## Layout

- docs/: PREREGISTRATION.md (frozen), DEVIATIONS.md (dated log), COVERAGE_LANDSCAPE.md
- data/: MANIFEST.md (every source with checksum and license), raw/ (gitignored), processed/ (trace_index.csv, features.csv)
- src/collect/: fetchers and parsers per source, the unified trace index, the data report
- src/features/: telemetry extractors reading raw traces, features table build with a leakage check
- src/models/: split.py (frozen split and its integrity check), baselines.py, fit.py, metrics.py (cluster bootstrap by agent), cv.py, portability.py (S2), glm.py, power.py, run_primary.py, run_robustness.py
- splits/primary_split.json: held-out agents per source, frozen before any model fit, with the index hash
- results/: dated JSON and figures, each embedding git commit, manifest hash, seeds and timestamp
- reports/: gate packages, weekly reports, the data request draft
- site-updates/: research-log entries staged for apps/web/content/research-log/

## Commands (from this directory)

- make env: create .venv (Python 3.12) and install pinned requirements.txt
- make test: run the test suite
- make reproduce: verify manifest checksums, then rebuild the index, data report, features table and both result files from data/raw. It fails with a clear message while no data exists.

data/raw is gitignored and never modified after fetch. notebooks/ is exploration only; nothing in a notebook is a result. Results live in results/ with git commit hash, manifest hash, seeds, and timestamp embedded. The result drivers refuse to run if the index hash or agent set no longer matches the frozen split.
