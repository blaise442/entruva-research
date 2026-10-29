# Week 4 report (2026-10-29)

## What ran

- Gate 4 approved 2026-10-28; Phase 4 reduced to collection cross-checks
  because no external data with task outcomes exists (DEVIATIONS 2026-10-28).
- Phase 4 designed and executed 2026-10-28 to 29 under the founder's instruction
  to proceed and approve: eight plan tasks plus the research page update,
  24 new tests (suite at 170), one whole-branch review.
- The Ethereum ERC-8004 collection was checked row for row against the public
  CC0 dataset of the first 10,000 agents (Harvard Dataverse HJZW8Q): all
  10,000 agents agree on mint block, transaction hash and owner; all 1,961
  transfer rows and 980 feedback rows exist in our logs; feedback counts never
  shrink. Verdict: matches row for row.
- Base and BNB Smart Chain registries were fetched over a two-day window each
  through keyless endpoints, after measuring that those endpoints serve no older
  history to anonymous clients (DEVIATIONS 2026-10-29). Window statistics for
  the three chains sit side by side in the Gate 5 report; full-history Base and
  BNB numbers stay open pending the founder enabling those networks on the
  Alchemy app.
- One anonymous 8004scan request per chain bounds our registration counts:
  Ethereum passes (55,407 events, ids 0 to 55,406, newest id 56,006 four days
  later); the windows are consistent with the API's newest ids.
- The public /research page now shows results so far, phase progress, what
  exists in the private repository for verification, and the flywheel question
  closed as answered within the study's limits.

## What it means

The reputation numbers in the Phase 3 report rest on a collection that an
independent dataset reproduces exactly. In the same two days, Ethereum's
feedback came from a single wallet writing to 794 agents while Base's came
from 2,098 wallets each writing to about one agent, so feedback concentration
differs by chain and the Sybil-cost finding should be read as Ethereum's
pattern until a full-history fetch of the other chains exists.

## Next

- Weekly reports through day 90; final write-up on 2027-01-15 with the
  verdict from Gate 4 (supported under the preregistered rule, gameable at the
  margin for one agent in ten at no cost) and the statement that external
  validation was not possible.
- Founder action, optional: enable Base and BNB on the Alchemy app for a
  full-history rerun; reply from the arXiv 2606.26028 authors would add a
  third cross-check.
