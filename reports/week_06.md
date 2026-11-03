# Week 6 report (2026-11-02 to 2026-11-09)

Drafted 2026-11-02 after the week 5 report; updated if anything else runs
before 2026-11-09.

## What ran

- The final write-up was drafted on 2026-11-02 (day 16) in
  reports/final_writeup.md from the five gate reports. Every number in it
  traces to a result file.
- The journal paper was drafted the same day in paper/paper.md: IMRaD, about
  7,300 words, aimed at insurers. Its title is a finding, not a caveat:
  "Telemetry predicts agent failure within domains but not across them:
  evidence and requirements for agent liability rating". The abstract carries
  the SWE-bench reversal next to the pooled pass, and Section 5.3 states seven
  requirements an insurer would need as numbers, most of which this study
  itself does not meet. The conflict of interest is declared and the
  Discussion is written to argue against the founder's premise wherever the
  data does.
- 22 references, every one checked against a primary page before inclusion
  (publisher page, Crossref DOI, arXiv listing or the Dataverse record). Where
  no primary page confirmed a venue the work is cited as a preprint.
- A tail check was added to the manipulation section from the per-agent
  output already in the Gate 4 result file (results/2026-10-28_S3_attacks.json):
  across all twenty attack settings there are three downward decile moves in
  the held-out set, all mid-distribution (decile 6 to 5). The two worst-scoring
  held-out agents, both WebArena agents at a predicted probability of 0.93,
  never move down under any attack; error suppression moves one of them up a
  decile. No new analysis was run and no threshold is involved, so there is no
  deviations entry.
- The paper was built as a PDF (paper/paper.pdf, 17 pages, Times New Roman)
  with five figures, two of them composites of existing result plots, by
  paper/build_pdf.py using Chrome headless; no LaTeX or pandoc on the machine.
  One Python dependency was added (markdown 3.11.2).
- The research page links the PDF from its how-to-verify list. One new page
  test; the research page tests are at 11.
- The write-up and paper are version 1 of 2026-11-02. The research directory
  is now its own public repository with its full history, and the research
  page links the preregistration,
  manifest, splits and deviations register directly. The publication date is
  the thirteenth deviations entry; it touches no threshold.

## What it means

The study's findings did not change this week; they were written up. The one
new reading, the tail check, sharpens the Gate 4 verdict: the free attacks act
in the middle of the predicted-risk distribution, where an agent near a decile
boundary can nudge across, and not at the top, where the agents an insurer most
needs to identify stay identified. The caveat stands that the held-out tail is
two or three agents and both of the worst are WebArena agents, where the
within-domain signal is weak.

## Deviations

One: the publication date (2026-11-02, decided by the founder after all
results were known). The register holds thirteen entries; none changes a
threshold.

## Next

- Weekly reports through day 90; any later result is a new dated version of
  the write-up and paper.
- Founder read-through of the paper: the 30 held-out agents per domain and
  the 0.05 calibration tolerance in Section 5.3 were set by judgement.
- The data request to the arXiv 2606.26028 authors remains unanswered.
