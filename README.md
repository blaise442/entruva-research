# Entruva 90 day study

A preregistered empirical study: can runtime behavioral telemetry from AI agents predict task failure out of sample better than a naive baseline, well enough to serve as a rating factor for agent liability insurance? Hypotheses, thresholds, and the analysis plan are frozen in docs/PREREGISTRATION.md (tag prereg-v1). Design decisions and repo adaptations: ../docs/superpowers/specs/2026-10-19-research-study-design.md. Deviations are logged in docs/DEVIATIONS.md.

Day convention: day 0 is 2026-10-17, day 90 is 2027-01-15. All reports use this convention.

Commands (from this directory):

- make env: create .venv (Python 3.12) and install pinned requirements.txt
- make test: run the test suite
- make reproduce: regenerate every result in results/ from data/raw. It fails with a clear message while no data exists; see data/MANIFEST.md for sources.

data/raw is gitignored and never modified after fetch; data/MANIFEST.md records every source with checksums. notebooks/ is exploration only; nothing in a notebook is a result. Results live in results/ with git commit hash, manifest hash, seeds, and timestamp embedded.
