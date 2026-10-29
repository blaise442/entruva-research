# Gate 5 results: Phase 4 collection cross-checks

Phase 4 closed 2026-10-29 (day 12 of 90). Everything below is computed by
`src/crosscheck/run_crosscheck.py` and `src/crosscheck/run_chains.py` with commit
hash and manifest hash in the result files `results/2026-10-28_erc8004_crosscheck.json`
and `results/2026-10-29_erc8004_descriptive_<chain>.json` (ethereum-mainnet,
base-mainnet, bnb-mainnet). The rules were fixed in `docs/DEVIATIONS.md`
(2026-10-28 cross-check rules; 2026-10-29 two-day window) before each run; the
design is `docs/superpowers/specs/2026-10-28-research-phase4-design.md`. Phase 4
was reduced at Gate 4 to collection cross-checks because no external dataset
with task outcomes exists; nothing here changes the H1 verdict.

## Ethereum cross-check against the public dataset

The public dataset is Harvard Dataverse doi:10.7910/DVN/HJZW8Q (Liu, "A dataset
of early blockchain-registered AI agents on Ethereum", arXiv 2604.22652),
released 2026-07-01 under CC0 1.0: the first 10,000 ERC-8004 agents on Ethereum
mainnet (token ids 0 to 9999), anchored to an observation block its data
dictionary does not state. Our collection is every log of the two registries
from deployment to the head on 2026-10-25 (`data/MANIFEST.md`). Four tables are
comparable without off-chain metadata, and the rule (DEVIATIONS 2026-10-28,
cross-check rules) has no tolerance: a single disagreeing row fails the check.

| Check | Rule | Rows | Agreeing | Disagreeing |
|---|---|---|---|---|
| agents_core | mint block, mint transaction hash and owner equal ours | 10,000 | 10,000 | 0 |
| transfer_history | every row exists among our Transfer events, and our non-mint transfers in their window equal their row count | 1,961 | 1,961 | 0 (ours in window: 1,961) |
| agent_feedback_records | every row exists among our NewFeedback events | 980 | 980 | 0 |
| agent_reputation_summary | their feedback count is at most ours (our fetch is later) | 10,000 | 10,000 | 0 (equal for 9,991) |

**Verdict: the Ethereum collection matches the public dataset row for row.**
Every row of the dataset's identity, transfer and feedback tables appears in
our logs with the same values, and nothing in their window is in our logs that
is not in theirs. The nine agents whose feedback count differs all have more
feedback in our later fetch, never less.

The owner comparison needs an observation block. The smallest block at which
every one of the 10,000 owners agrees is 24,744,960; from that block to our
head all 10,000 agree. This block is inferred from the data, not stated by the
dataset, and sits later than the last transfer in their transfer_history
(24,429,384), so their owner column was taken from a later snapshot than
their transfer table. Mint blocks and transaction hashes do not depend on it.

What this does and does not establish: it shows the Phase 3 reputation
descriptives rest on a faithful collection of the Ethereum registries. It says
nothing about task outcomes, which neither source has, so the H1 model is not
validated externally (DEVIATIONS 2026-10-28, Phase 4 reduced).

## Second-source count check (8004scan public API)

Token ids on each chain are sequential from zero, so the newest token id the
8004scan API returns on the request date bounds our registration count from
above. One anonymous request per chain on 2026-10-29, responses pinned under
`data/raw/8004scan/` with MANIFEST entries. The API's own `total` field counts
agents with a registration file and is recorded, not used.

| Chain | Our Registered events | Our max agent id | API newest token id | Check |
|---|---|---|---|---|
| Ethereum mainnet (full history to 2026-10-25) | 55,407 | 55,406 | 56,006 | pass: count equals max id plus one, and max id is below the newest id four days later |
| Base mainnet (two-day window) | 5,605 | 1,143,328 | 1,143,354 | not applicable to a window; max id is 26 below the id the API saw two hours later |
| BNB Smart Chain (two-day window) | 3,506 | 397,366 | 397,378 | not applicable to a window; max id is 12 below the API's |

## Base and BNB Smart Chain: a two-day window, not full history

Gate 4 asked for Base and BNB reputation descriptives beside the Ethereum ones.
A full-history fetch was not possible at zero spend on 2026-10-29: the keyless
publicnode endpoints answer 403 Forbidden for anything older than about three
days on BNB and about 46 days on Base, the official Base and BNB Chain
endpoints reject eth_getLogs for anonymous use, and the founder's Alchemy app
has neither network enabled (DEVIATIONS 2026-10-29). Both chains were fetched
over the two days before their head (block timestamps recorded with each
fetch), and the same two days were cut from the end of the Ethereum file. These
are window statistics and are not the full-history descriptives of Gate 4.

| Two-day window | Ethereum (to 2026-10-25) | Base (to 2026-10-29) | BNB Smart Chain (to 2026-10-29) |
|---|---|---|---|
| Span (days, from block timestamps; Ethereum from the 12 s slot time) | 2.00 | 1.99 | 1.98 |
| Registrations | 102 | 5,605 | 3,506 |
| Registrations per day | 51 | 2,816 | 1,770 |
| Feedback events | 2,571 | 2,161 | 9 |
| Feedback events per day | 1,286 | 1,086 | 4.5 |
| Agents receiving feedback | 792 | 2,106 | 7 |
| Share of those agents with a single giver | 1.00 | 1.00 (2,105 of 2,106) | 0.86 (6 of 7) |
| Distinct feedback givers | 1 | 2,098 | 4 |
| Share of feedback from registrant wallets (window) | 0.015 (full history) | 0.027 | 0.00 |

Reading: in its last two days Ethereum's feedback came from one wallet writing
2,571 entries across 792 agents, which is the concentration the Phase 3
reputation section described. Base in the same span looks different: each
feedback giver touches about one agent (2,098 givers for 2,106 agents), so the
single-giver share is the same but the givers are not. BNB had nine feedback
events in two days against 3,506 registrations. Whether these patterns hold over
the full history is not known from this data.

Full-history numbers remain only for Ethereum (results/2026-10-27_erc8004_descriptive.json,
unchanged: 55,407 registrations, 34,493 feedback events, 2,651 agents with
feedback, 2,444 of them from a single giver, 721 distinct givers).

## Fetch record

| Source | Date | Endpoint | Rows | MANIFEST entry |
|---|---|---|---|---|
| Dataverse HJZW8Q, five files | 2026-10-28 | dataverse.harvard.edu API, file ids pinned | agents_core 10,000; transfer_history 1,961; agent_feedback_records 980; agent_reputation_summary 10,000; data dictionary | dataverse HJZW8Q <file> |
| Base identity and reputation logs | 2026-10-29 | https://base-rpc.publicnode.com (keyless), window 53,162,845 to 53,248,845 | 32,961 and 2,161 | erc8004 base-mainnet * |
| BNB identity and reputation logs | 2026-10-29 | https://bsc-rpc.publicnode.com (keyless), window 130,116,686 to 130,496,686 | 23,666 and 9 | erc8004 bnb-mainnet * |
| 8004scan newest agent, three chains | 2026-10-29 | https://api.8004scan.io/api/v1/agents, anonymous | 1 each | 8004scan newest agent <chain> |

`verify_manifest` over data/raw returns no mismatch after all fetches. The
collector gained three things for this phase, each with a test: the BNB chain,
recording of a keyless public endpoint, and paced calls with a fixed wait when
publicnode blocks a burst (it blocks about ten calls in two seconds for several
minutes, and every retry during the block extends it).

## Limitations

- No task outcomes anywhere in these sources: the cross-check confirms
  collection fidelity, not predictive validity. External validation of H1 did
  not happen and the final write-up says so.
- The observation block of the Dataverse owner column is inferred
  (24,744,960), not stated; mint blocks and hashes do not depend on it.
- Base and BNB are two-day windows, so feedback concentration there is a
  snapshot, and the 8004scan check can only be a bound for them.
- The 8004scan bound compares a 2026-10-25 fetch with a 2026-10-29 request on
  Ethereum; the gap is consistent with the chain minting in between, not a check
  of equality.
- The Ethereum window uses the 12-second slot time to pick its start block, not
  block timestamps.
- The authors' data request (arXiv 2606.26028) stays unanswered; a reply adds
  a third cross-check.

## Decisions at Gate 5 (2026-10-29)

The founder instructed the executing agent on 2026-10-29 to complete Phase 4
without further questions and to approve on their behalf ("use your best
judgement and approve everything"). The decisions below were taken under that
instruction and stand until the founder revises them.

1. The cross-check sentence is accepted as written: the Ethereum collection
   matches the public dataset row for row, with the observation block noted as
   inferred.
2. Base and BNB window statistics are accepted as the Phase 4 Part B result,
   labelled as two-day windows everywhere they appear. The full-history
   descriptives Gate 4 asked for stay open. Founder action to close them: enable
   Base Mainnet and BNB Mainnet on the Alchemy app, then rerun
   `src.collect.erc8004` with RPC_URL for each network and `src.crosscheck.run_chains`.
   The week three note that Alchemy's free tier proved unusable for a 1.9 million
   block Ethereum scan applies to those chains too, so this is a background job
   of hours, not a quick fix.
3. No change to any preregistered threshold or to the Gate 3 and Gate 4
   verdicts. The final write-up will carry the H1 verdict from Gate 4 and this
   fidelity check.
4. Gate 5 approved; Phase 4 is closed. What remains is weekly reports to day 90
   and the final write-up on 2027-01-15.
