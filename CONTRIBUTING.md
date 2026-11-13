# Contributing

This repository is the public record of a preregistered study. Its value is that
the record is stable, so contributions are welcome but gated.

- Every change lands by pull request. Nobody pushes to main, including the
  maintainer. The main branch is protected: a pull request needs an approving
  review from the code owner (Blaise Wangmeni, @blaise442) before it can merge, and
  force pushes and branch deletion are blocked.
- Preregistered material does not change. docs/PREREGISTRATION.md is frozen at
  tag prereg-v1. Any analysis choice goes in docs/DEVIATIONS.md with its date,
  its reason and who decided it, before the run that uses it. Result files under
  results/ are never edited; a rerun writes a new dated file.
- Numbers must trace. Every figure in a report or on the site names the result
  file it comes from. A pull request that adds a number without a result file
  is not merged.
- No secrets, no raw data. data/raw is gitignored; .env is gitignored and the
  RPC URL is never written to a tracked file or printed in a log.
- Style: no em dashes in documents; Python is formatted with ruff; tests run
  with `make test` and must pass.
- To report a problem with the data, the code or a claim, open an issue with
  the file and line, what you expected and what you found.
