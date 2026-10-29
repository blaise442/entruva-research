# Gate 4 results: clause 4, adversarial cost (S3), reputation layer, flywheel (S4)

Phase 3 closed 2026-10-28 (day 11 of 90). Everything below is computed by
`src/adversarial/run_s3.py`, `src/adversarial/run_reputation.py` and
`src/simulation/run_s4.py` with seeds, commit hash and manifest hash in the
result files `results/2026-10-28_S3_attacks.json`,
`results/2026-10-27_erc8004_descriptive.json` and
`results/2026-10-28_S4_flywheel_synthetic.json`. The analysis choices were fixed
in `docs/DEVIATIONS.md` (three entries dated 2026-10-27) before any attack was
run; the design is `docs/superpowers/specs/2026-10-25-research-phase3-design.md`.
The S3 and S4 numbers are from a rerun on 2026-10-28 after a whole-branch review
of the first run found seven departures from the design and the feature
extractor (DEVIATIONS 2026-10-28, written before the rerun). The first run's
files are in git history at commit 1488a19; its verdicts under both readings
were the same as below.

## Clause 4 verdict

Clause 4 (prereg, floor filled 2026-10-25): the cheapest intervention that lowers
an agent's predicted risk by one decile with its true failure rate unchanged must
cost at least 3 times the annual premium saving from that drop. No premium is
quoted. The premium is pure expected loss, predicted probability times severity,
and the two unknowns (severity, runs per year) are collapsed into the agent's
annual exposure X. The breakeven exposure for an attack is X* = (E + c R) / (3 dp).
Clause 4 passes in a scenario cell when the cheapest priced decile-moving attack
has X* above that cell's exposure, and passes overall only in every cell.

**Under the preregistered reading (an attack moves one decile when it moves the
median movable held-out agent): no attack moves a decile. Clause 4 passes in all
16 cells. Verdict: pass.**

**Under the harsher any-agent reading (an attack counts when it moves any one
agent): error suppression, which costs nothing per run, moves one of ten agents
(the Llama 3.3 70B AgentDojo agent, decile 6 to 5). dp is the difference of the
decile mean predicted probabilities, 0.560 for decile 6 and 0.409 for decile 5,
so 0.151. With E = 0 the breakeven exposure is 0 and every E = 0 cell fails;
with E = 10,000 USD it is 22,087 USD, so the cells at 100,000 and 1,000,000 USD
exposure fail as well. Verdict: fail.**

Both readings are reported because the decile unit was chosen before the run
(DEVIATIONS 2026-10-27) and a reader should see how much the verdict depends on
it. The honest summary: the frozen scorer is hard to move for a typical agent by
editing telemetry alone, because most of its signal comes from model identity
and task type, which an operator cannot forge; but a single agent whose score
sits near a decile boundary can be nudged across for free.

### Attack curves (held-out agents, n = 10, all movable)

**error suppression**

| strength | deciles moved (median) | agents moved | any agent moved | dp over movers (decile means) | USD per run |
|---|---|---|---|---|---|
| None | +0.0 | 1/10 | yes | 0.1509 | 0.000000 |

**retry diversification**

| strength | deciles moved (median) | agents moved | any agent moved | dp over movers (decile means) | USD per run |
|---|---|---|---|---|---|
| None | +0.0 | 1/10 | yes | 0.1509 | 0.000000 |

**call shaping**

| strength | deciles moved (median) | agents moved | any agent moved | dp over movers (decile means) | USD per run |
|---|---|---|---|---|---|
| -32 | +0.0 | 0/10 | no | 0.0000 | 0.000000 |
| -16 | +0.0 | 0/10 | no | 0.0000 | 0.000000 |
| -8 | +0.0 | 0/10 | no | 0.0000 | 0.000000 |
| -4 | +0.0 | 0/10 | no | 0.0000 | 0.000000 |
| -2 | +0.0 | 0/10 | no | 0.0000 | 0.000000 |
| -1 | +0.0 | 0/10 | no | 0.0000 | 0.000000 |
| 1 | +0.0 | 0/10 | no | 0.0000 | unpriced |
| 2 | +0.0 | 0/10 | no | 0.0000 | unpriced |
| 4 | +0.0 | 0/10 | no | 0.0000 | unpriced |
| 8 | -0.5 | 0/10 | no | 0.0000 | unpriced |
| 16 | -1.0 | 0/10 | no | 0.0000 | unpriced |
| 32 | -2.0 | 0/10 | no | 0.0000 | unpriced |

**message shaping**

| strength | deciles moved (median) | agents moved | any agent moved | dp over movers (decile means) | USD per run |
|---|---|---|---|---|---|
| 0.25 | +0.0 | 0/10 | no | 0.0000 | 0.000000 |
| 0.5 | +0.0 | 0/10 | no | 0.0000 | 0.000000 |
| 0.75 | +0.0 | 0/10 | no | 0.0000 | 0.000000 |
| 1.5 | +0.0 | 0/10 | no | 0.0000 | unpriced |
| 2 | +0.0 | 0/10 | no | 0.0000 | unpriced |
| 4 | +0.0 | 1/10 | yes | 0.1509 | unpriced |

### Per-agent deciles under error suppression

| held-out agent | decile before | decile after | p before | p after |
|---|---|---|---|---|
| claude-3-5-sonnet-20241022::agentdojo | 4 | 4 | 0.305 | 0.294 |
| claude-3-haiku-20240307::agentdojo | 6 | 6 | 0.548 | 0.510 |
| claude3.5sonnet::sweagent | 6 | 7 | 0.603 | 0.677 |
| gpt-3.5-turbo-0125::agentdojo | 5 | 5 | 0.400 | 0.382 |
| gpt-4-turbo-2024-04-09::agentdojo | 5 | 5 | 0.379 | 0.363 |
| gpt-4o-2024-05-13-transformers_pi_detector::agentdojo | 6 | 6 | 0.524 | 0.510 |
| gpt-4o::tau-bench | 5 | 5 | 0.424 | 0.446 |
| gpt35_16k::webarena-cot | 8 | 9 | 0.931 | 0.946 |
| gpt35_16k::webarena-direct | 8 | 8 | 0.939 | 0.939 |
| meta-llama_Llama-3.3-70B-Instruct::agentdojo | 6 | 5 | 0.479 | 0.454 |

### Clause 4 breakeven table, median-agent rule (the preregistered reading)

| runs per year | exposure USD | one-time USD | cheapest attack | breakeven exposure USD | passes |
|---|---|---|---|---|---|
| 1,000 | 1,000 | 0 | none moves a decile | n/a | True |
| 1,000 | 1,000 | 10,000 | none moves a decile | n/a | True |
| 1,000 | 10,000 | 0 | none moves a decile | n/a | True |
| 1,000 | 10,000 | 10,000 | none moves a decile | n/a | True |
| 1,000 | 100,000 | 0 | none moves a decile | n/a | True |
| 1,000 | 100,000 | 10,000 | none moves a decile | n/a | True |
| 1,000 | 1,000,000 | 0 | none moves a decile | n/a | True |
| 1,000 | 1,000,000 | 10,000 | none moves a decile | n/a | True |
| 100,000 | 1,000 | 0 | none moves a decile | n/a | True |
| 100,000 | 1,000 | 10,000 | none moves a decile | n/a | True |
| 100,000 | 10,000 | 0 | none moves a decile | n/a | True |
| 100,000 | 10,000 | 10,000 | none moves a decile | n/a | True |
| 100,000 | 100,000 | 0 | none moves a decile | n/a | True |
| 100,000 | 100,000 | 10,000 | none moves a decile | n/a | True |
| 100,000 | 1,000,000 | 0 | none moves a decile | n/a | True |
| 100,000 | 1,000,000 | 10,000 | none moves a decile | n/a | True |

Verdict under this rule: **pass**

### Clause 4 breakeven table, any-agent rule (the harsher reading)

| runs per year | exposure USD | one-time USD | cheapest attack | breakeven exposure USD | passes |
|---|---|---|---|---|---|
| 1,000 | 1,000 | 0 | error_suppression (s=None) | 0 | False |
| 1,000 | 1,000 | 10,000 | error_suppression (s=None) | 22,087 | True |
| 1,000 | 10,000 | 0 | error_suppression (s=None) | 0 | False |
| 1,000 | 10,000 | 10,000 | error_suppression (s=None) | 22,087 | True |
| 1,000 | 100,000 | 0 | error_suppression (s=None) | 0 | False |
| 1,000 | 100,000 | 10,000 | error_suppression (s=None) | 22,087 | False |
| 1,000 | 1,000,000 | 0 | error_suppression (s=None) | 0 | False |
| 1,000 | 1,000,000 | 10,000 | error_suppression (s=None) | 22,087 | False |
| 100,000 | 1,000 | 0 | error_suppression (s=None) | 0 | False |
| 100,000 | 1,000 | 10,000 | error_suppression (s=None) | 22,087 | True |
| 100,000 | 10,000 | 0 | error_suppression (s=None) | 0 | False |
| 100,000 | 10,000 | 10,000 | error_suppression (s=None) | 22,087 | True |
| 100,000 | 100,000 | 0 | error_suppression (s=None) | 0 | False |
| 100,000 | 100,000 | 10,000 | error_suppression (s=None) | 22,087 | False |
| 100,000 | 1,000,000 | 0 | error_suppression (s=None) | 0 | False |
| 100,000 | 1,000,000 | 10,000 | error_suppression (s=None) | 22,087 | False |

Verdict under this rule: **fail**

Unpriced models: claude-3-5-sonnet-20241022, claude-3-haiku-20240307, claude3.5sonnet, gpt35_16k, meta-llama_Llama-3.3-70B-Instruct
Decile edges: 0.160, 0.222, 0.278, 0.353, 0.478, 0.637, 0.822, 0.939, 0.964
Decile mean predicted probability (1 to 10): 0.124, 0.188, 0.245, 0.311, 0.409, 0.560, 0.717, 0.899, 0.951, 0.975

## Overall H1 verdict

Clauses 1 to 3 held at Gate 3 (held-out AUC 0.843 [0.777, 0.888] against a
naive baseline of 0.654, paired delta 0.189 [0.067, 0.288]; Brier skill 0.220
[0.049, 0.315]; top/bottom quartile ratio 4.14 with monotone deciles). Under the
preregistered pooled rule and the preregistered median-agent reading of clause 4,
**H1 is supported**. Under the any-agent reading of clause 4 the verdict would be
**predictive but gameable**. The final write-up states both and the limitations
below.

## S3 attack curves

The four attacks are feature-level transformations of the held-out rows with the
coupling rule from the design (every feature the extractor would move, moves).
Per-run cost is added characters converted to tokens with the measured
chars-per-token ratio for each source (`data/prices/chars_per_token.csv`) at the
vendor's public list price (`data/prices/model_prices.csv`), input plus an
equal-size output. Two attacks add no text and cost nothing per run. Figures:
`results/2026-10-28_S3_<attack>.png`.

Call shaping was run in both directions the design names. Dropping redundant
calls (k < 0 removes up to |k| repeated calls, which costs nothing) moves no
agent: only 13.5 percent of held-out rows contain a repeated call at all, so
there is little to drop. Adding calls raises predicted risk for the median agent
from k = 8 upward. Message shaping at factor 4 moves one agent (the gpt-4o
prompt-injection-detector AgentDojo agent) but is unpriced for the five agents
without a list price, so by the preregistered rule it is never the cheapest.

Five of ten held-out agents are unpriced (three retired Claude models, the
retired gpt-3.5-turbo-16k, and Llama 3.3 70B which has no vendor list price), so
the two priced attacks carry no dollar figure wherever those agents are in the
rows. By the preregistered rule an unpriced attack is never the cheapest. The
free attacks are priced at zero per run regardless.

## Reputation layer (ERC-8004, Ethereum mainnet)

No model in this study uses reputation (S1 is not evaluable, below), so these
numbers bound what a future reputation-weighted score would cost to game and do
not bear on the clause 4 verdict above.

From 275,118 IdentityRegistry and 34,535 ReputationRegistry events decoded with
the pinned ABI (commit b9e466c):

| quantity | value |
|---|---|
| agents registered | 55,407 |
| feedback events | 34,493 |
| agents with any feedback | 2,651 |
| agents whose feedback comes from a single wallet | 2,444 (92 percent of rated agents) |
| distinct feedback-giving wallets | 721 |
| share of feedback from wallets that also registered an agent | 1.5 percent |
| feedback per rated agent, median (p75, max) | 1 (9, 636) |

Registrations are bursty: 23,107 in the first week after deployment and 10,167 in
one later week, with most weeks under 1,000 (`results/2026-10-27_erc8004_registrations.png`).

Attack costs from 400 sampled receipts (200 per event type, seed 20261017) with
ETH-USD at the block-day spot price from Coinbase's public endpoint (101 days,
1,569 to 3,009 USD per ETH):

| attack | ETH | USD |
|---|---|---|
| one registration (also one on-chain whitewash) | 0.000068 | 0.17 |
| one feedback event | 0.000040 | 0.10 |
| Sybil campaign to reach the median feedback count (1) | 0.000108 | 0.27 |
| collusion ring of 5 agents rating each other (20 feedbacks) | 0.000796 | 1.93 |

A fresh identity with as much feedback as the median rated agent costs about a
quarter of a dollar in gas. Any reputation component built on this registry must
weight feedback by something other than its count.

## S4 flywheel (synthetic)

Agent-based simulation, 500 agents whose true failure rates are resampled from
the ten held-out agents, 50 resampled real rows per agent per round, 12 rounds
with burn-in 4, attacker fraction f from 0 to 1 in steps of 0.05, one run per
scenario cell (16 cells), seed 20261017. Round 0 scores with the Phase 2 scorer;
each later round the insurer refits the Phase 2 model class on the previous
round's observed telemetry (attacked rows included) and true outcomes.
Attackers are rational: they apply the cheapest attack from the any-agent S3
table (error suppression, free per run) whenever their own saving under the
current scorer, dp times the cell's exposure, exceeds their cost, paying E once.
The 3x floor is the insurer's rule, not the attacker's. Outputs carry
`synthetic` in the filename and feed no headline result
(`results/2026-10-28_S4_flywheel_synthetic.json`, `.png`).

Result: **no collapse in any cell**. AUC after burn-in is 0.757 at f = 0 and
0.756 to 0.757 at f = 1 in every cell, against a naive baseline of 0.654; round
0 under the Phase 2 scorer is 0.661. Attackers are active when E = 0 (up to 314
of 500 agents in a round, 179 in the last round at f = 1); when E = 10,000 USD
nobody attacks below 1,000,000 USD exposure, and at that exposure 233 of 500
attack at f = 1. Error suppression barely moves the refit scorer, so trust
quality is flat in f. The share of premium paid by the riskiest true-risk
quartile of agents is 0.40 at every f. The boundary f is therefore not reached
on this grid and is reported as none.

Neither of the two preregistered outcomes fired by its fixed rule. "Converged"
required AUC within the Phase 2 held-out GBM CI [0.777, 0.888]; the simulation's
ceiling is lower (0.757) because its outcomes are Bernoulli draws from each
agent's rate, so within-agent variation is pure noise. The rule is kept as fixed
in DEVIATIONS and the mismatch is listed under limitations rather than patched
after the run. "No collapse" is also close to guaranteed by construction (see
limitations): the refit scorer can learn agent identity from model_id, which no
attack touches. The plot shows what the simulation can show: a scorer that keeps
refitting on gamed telemetry neither improves nor degrades under the one attack
that pays.

## S1

S1 (combined telemetry plus reputation against telemetry alone) is not
evaluable with available data: the benchmark agents with telemetry and outcomes
have no on-chain identity, and the on-chain agents have no task outcomes
(DEVIATIONS 2026-10-27).

## Limitations

- Attacks are feature-level: they state the trace change in words and move the
  features the extractor would move. A real operator rewriting traces could find
  interactions this misses, in either direction.
- The one-time engineering cost E is a parameter (0 and 10,000 USD), not a
  measurement.
- Ten held-out agents; the decile unit is coarse at that count and the median
  and any-agent readings disagree.
- Five of ten held-out agents are unpriced, so call shaping and message shaping
  carry no dollar cost for them.
- Blockchain data came from a keyless public endpoint (rpc.mevblocker.io),
  Ethereum mainnet only.
- The simulation is synthetic and anchored only in the held-out agents' failure
  rates and rows; it is excluded from headline results. Its convergence band
  (the Phase 2 GBM CI) was set above the AUC ceiling of a Bernoulli-outcome
  population, so "converged" is false everywhere even though the curve is flat;
  a future run should fix the band from a no-attacker calibration round.
- "No collapse" in S4 is close to guaranteed by construction, not only by the
  band: outcomes are Bernoulli draws from the agent's rate, independent of the
  resampled row, and model_id, which no attack touches, nearly identifies the
  ten source agents, so a refit scorer can learn agent identity and no
  telemetry attack that leaves model_id intact can collapse it. The S4 result
  is not evidence about a flywheel whose scorer cannot see model identity.
- The S3 and S4 numbers are from the 2026-10-28 rerun after review; the
  corrections (DEVIATIONS 2026-10-28) were made after the first run's numbers
  were known. Neither verdict changed; the any-agent breakeven at E = 10,000
  USD fell from 131,548 to 22,087 USD because dp is now the decile-mean
  difference the design asked for.

## Decisions at Gate 4 (founder)

Draft by the executing agent, 2026-10-28, awaiting founder approval. The
founder's edits replace this text; nothing below is decided until then.

1. The preregistered median-agent reading leads the final write-up: clause 4
   passes, H1 is supported. Reason: the reading was fixed in DEVIATIONS before
   any attack was run, and replacing it after seeing that the harsher reading
   fails is what the preregistration exists to prevent. The any-agent result is
   stated in the same headline sentence, not in a footnote: one held-out agent
   in ten can be moved a decile at zero per-run cost, and under that reading
   clause 4 fails. The write-up's verdict sentence reads: supported under the
   preregistered rule, gameable at the margin for one agent in ten at no cost.
2. The S4 convergence band stays as fixed. "Converged" is false everywhere
   because the band sits above the simulation's ceiling; this is reported as a
   limitation and not patched. A rerun with a band from a no-attacker
   calibration round is not part of this study.
3. Phase 4 is reduced. No reply has come from the authors of arXiv 2606.26028,
   and a search on 2026-10-28 found no public release of their dataset. Two
   public sources exist, and neither carries task outcomes, so external
   validation of the H1 model is not possible with any data available to the
   study; this is recorded in DEVIATIONS. What Phase 4 can do is cross-check
   the ERC-8004 collection and extend the reputation descriptives beyond
   Ethereum:
   - Harvard Dataverse doi:10.7910/DVN/HJZW8Q (Liu, "A dataset of early
     blockchain-registered AI agents on Ethereum", arXiv 2604.22652), published
     2026-07-01, CC0 1.0, twelve public files: the first 10,000 ERC-8004 agents
     on Ethereum mainnet with feedback records, reputation summaries, transfers
     and resolved metadata. Use: a row-level cross-check of the Ethereum
     collection over its block range.
   - The 8004scan public API (https://api.8004scan.io/api/v1, OpenAPI at
     https://api.8004scan.io/openapi.json), agents and feedbacks across 29
     networks; anonymous tier 30 requests per minute and 1,000 per day, a free
     key raises the daily cap to 100,000. Use: Base and BNB Smart Chain
     feedback descriptives beside the Ethereum ones, at zero spend, with the
     fetch recorded in MANIFEST. A direct Base mainnet eth_getLogs collection
     through a keyless endpoint remains the preferred source if one with no
     range cap is found.
   The data request stays open; if the authors reply, their multi-chain crawl
   through 2026-05-13 is added as a third cross-check.
4. None of the thirteen deferred review minors is required before the final
   write-up. The per-model "not evaluable" rule is the one to fix first if any
   are taken up, and it would need a DEVIATIONS entry before a rerun.
5. Gate 4 approved; Phase 3 is closed. The final write-up is drafted from this
   report and the Gate 3 report once the Phase 4 cross-checks have run.
