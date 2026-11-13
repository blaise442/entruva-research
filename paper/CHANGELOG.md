# Paper change log

## Version 1.1, 2026-11-13

Text corrections after a pre-submission review of version 1. No analysis
choice changed and no version 1 result file was edited. Every number added
below is read from a result file that existed at version 1, except item 25,
which reports a reproduction rerun. The register entries are
docs/DEVIATIONS.md, 2026-11-13. Version 1 is at tag v1.0.

Corrections to claims about the preregistration:

1. Abstract, Sections 1, 3.1, 3.2. Version 1 said the pass thresholds were
   frozen before any model was fit. Only the thresholds of clauses 1 to 3 were.
   The clause 4 floor was left open at the freeze and set on 2026-10-25, after
   the prediction results.
2. Sections 3.7, 4.3, 5.5. Version 1 called the median-agent reading of clause 4
   "the preregistered reading". It was fixed on 2026-10-27, after the held-out
   scores existed. The preregistered wording is closer to the any-agent
   reading, under which clause 4 fails and the preregistered verdict is
   "predictive but gameable". Version 1 reported the verdict as "supported,
   and gameable at the margin"; version 1.1 reports both readings and no longer
   says the preregistered rule passed without qualification.
3. Sections 3.2, 3.7, 5.4. The preregistration named whitewashing, Sybil
   feedback, collusion and strategic oscillation as the manipulations to cost.
   Version 1 did not say that four feature-level attacks took their place for
   the telemetry score.
4. Section 3.1, 5.4. Added: the preregistration was self-held in a repository
   that was private until 2026-11-02, with no third-party timestamp.
5. Section 4.7. Version 1 said two register entries follow a result. The
   attack set, decile unit and median-agent reading of 2026-10-27 also follow
   the prediction results. Table 7 gains the 2026-11-13 entry.

Corrections to results as described:

6. Table 3 and Section 4.2. Version 1 captioned Table 3 as an evaluation on
   each source's held-out agents. Its numbers are the grouped five-fold
   cross-validation over all agents (results/2026-10-25_H1_robustness_cv.json,
   by_source). The caption is corrected and the held-out point AUCs
   (results/2026-10-25_H1_primary.json, per_source_auc_descriptive) are added.
   Version 1 also said the tau-bench interval touches zero; it does not, it is
   degenerate.
7. Section 4.1, Figure 1 caption, Section 5.3 item 5. Version 1 said the
   reliability curve under-predicts between 0.3 and 0.5 and is close to the
   diagonal elsewhere. It under-predicts in each of the eight bins below 0.8,
   by 0.05 to 0.18 (results/2026-10-25_H1_primary.json, reliability_gbm). The
   bins are equal-width, not deciles.
8. Section 5.1. Version 1 explained the telemetry-only result by saying that
   telemetry is nearly a fingerprint of the agent and that most of the score's
   signal sits in model identity and task type. No analysis in the study
   supports either statement and Table 2 contradicts the second. Both are
   withdrawn; the paragraph now says the mechanism is not established.
9. Section 5.2. Version 1 said fewer than one agent in twenty has any feedback
   on three chains. That holds on Ethereum and BNB Smart Chain; on Base it is
   about one in eight, as Section 4.5 already said.
10. Sections 3.7, 5.4. Version 1 said five of the ten held-out agents run on
    models with no public list price. Six agents do, on five models
    (results/2026-10-28_S3_attacks.json). Four of the five models are ones the
    vendor no longer lists, three of them retired; one is open-weights.
11. Section 3.5. Version 1 read the Gate 2 power simulation as a minimum
    detectable gain of 0.02. The simulation reported power of 1.0 at every gain
    it tried and the realised interval is far wider, so the sentence now says it
    understated the variance between agents.
12. Abstract, Sections 1 and 6. "Resists free manipulation" and "cannot cheaply
    improve their score" are restated as what was tested: none of the four
    edits tested lowers the score.

Corrections to descriptions:

13. Title. From "Telemetry predicts agent failure within domains but not across
    them" to "Telemetry predicts agent task failure within one benchmark and
    does not transfer across benchmarks". The within-source gain is established
    in one source of four. Section 3.3 now states that a domain is
    operationalised as a benchmark source.
14. Section 3.4. "Mean message length" is the mean text length per tool call:
    the tool output in AgentDojo, tau-bench and SWE-bench, the agent's parsed
    action in WebArena. Task length in the baseline is the number of steps the
    run took, read from the same trace. Both are now stated, with which sources
    publish which features.
15. Section 3.3. "Five of six planned sources" follows the collection plan. The
    preregistration also named the OECD AI Incidents Monitor and the ERC-8004
    validation registry; neither could be collected and the paper now says so.
16. Section 5.4. Added: every feature is read from the run whose outcome is
    scored, so the test is of discrimination within a run, not of prediction
    from an earlier period.
17. Section 4.6. The simulation is cut to one paragraph and its figure is no
    longer reproduced; the section already said it is uninformative.
18. Declarations. Data availability now says that commit hashes in result files
    refer to the private monorepo and that every result file records git_dirty
    as true. The AI-use statement now says where the AI agent, not the author,
    fixed an analysis choice.
19. Wording. "The authors' proposals" becomes "the author's proposals"; the
    abstract's quartile sentence has runs, not the model, as its subject.

Editorial changes and the journal-format copy:

20. Author. The byline is the author's full name, Blaise Wangmeni, with
    correspondence addresses. Version 1 gave "Blaise W".
21. Abstract. Rewritten to 250 words. The claims are those of the corrected
    text above; no number is new.
22. Voice and vocabulary. The first person plural is removed, because the paper
    has one author. Internal process terms (gate, phase) are replaced by plain
    descriptions; the stage reports keep their file names.
23. Section 3.1. The pointer for the reduced external validation now reads
    Section 3.9, where it is described; version 1 pointed to Section 3.8.
24. paper/manuscript.tex and paper/manuscript.pdf are a single-column
    journal-format copy of the same text, generated from paper.md by
    paper/build_tex.py. paper/paper.pdf remains the two-column layout.

Reproduction check:

25. Declarations, Sections 3.1 and 4.7. The prediction, robustness and
    manipulation drivers were rerun unchanged from the public repository on
    clean committed trees and compared with the version 1 files
    (results/2026-11-13_rerun_comparison.json). 2,954 of 2,983 numbers agree to
    six decimal places; the rest differ by at most 0.000075 and no verdict
    differs. The paper states this and keeps citing the version 1 files. The
    register now has fifteen entries.

## Version 1, 2026-11-02

First public version. Tag v1.0.
