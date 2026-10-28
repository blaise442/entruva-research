# Gate 4 results: clause 4, adversarial cost (S3), reputation layer, flywheel (S4)

Phase 3 closed 2026-10-27 (day 10 of 90). Everything below is computed by
`src/adversarial/run_s3.py`, `src/adversarial/run_reputation.py` and
`src/simulation/run_s4.py` with seeds, commit hash and manifest hash in the
result files `results/2026-10-27_S3_attacks.json`,
`results/2026-10-27_erc8004_descriptive.json` and
`results/2026-10-27_S4_flywheel_synthetic.json`. The analysis choices were fixed
in `docs/DEVIATIONS.md` (three entries dated 2026-10-27) before any attack was
run; the design is `docs/superpowers/specs/2026-10-25-research-phase3-design.md`.

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
(the Llama 3.3 70B AgentDojo agent, decile 6 to 5). With E = 0 the breakeven
exposure is 0 and every E = 0 cell fails. Verdict: fail.**

Both readings are reported because the decile unit was chosen before the run
(DEVIATIONS 2026-10-27) and a reader should see how much the verdict depends on
it. The honest summary: the frozen scorer is hard to move for a typical agent by
editing telemetry alone, because most of its signal comes from model identity
and task type, which an operator cannot forge; but a single agent whose score
sits near a decile boundary can be nudged across for free.

### Attack curves (held-out agents, n = 10, all movable)

**error suppression**

| strength | deciles moved (median) | agents moved | any agent moved | mean dp over movers | USD per run |
|---|---|---|---|---|---|
| None | +0.0 | 1/10 | yes | 0.0253 | 0.000000 |

**retry diversification**

| strength | deciles moved (median) | agents moved | any agent moved | mean dp over movers | USD per run |
|---|---|---|---|---|---|
| None | +0.0 | 1/10 | yes | 0.0053 | 0.000000 |

**call shaping**

| strength | deciles moved (median) | agents moved | any agent moved | mean dp over movers | USD per run |
|---|---|---|---|---|---|
| 1 | +0.0 | 0/10 | no | 0.0000 | unpriced |
| 2 | +0.0 | 0/10 | no | 0.0000 | unpriced |
| 4 | +0.0 | 0/10 | no | 0.0000 | unpriced |
| 8 | -0.5 | 0/10 | no | 0.0000 | unpriced |
| 16 | -1.0 | 0/10 | no | 0.0000 | unpriced |
| 32 | -2.0 | 0/10 | no | 0.0000 | unpriced |

**message shaping**

| strength | deciles moved (median) | agents moved | any agent moved | mean dp over movers | USD per run |
|---|---|---|---|---|---|
| 0.25 | +0.0 | 0/10 | no | 0.0000 | 0.000000 |
| 0.5 | +0.0 | 0/10 | no | 0.0000 | 0.000000 |
| 0.75 | +0.0 | 0/10 | no | 0.0000 | 0.000000 |
| 1.5 | +0.0 | 0/10 | no | 0.0000 | unpriced |
| 2 | +0.0 | 0/10 | no | 0.0000 | unpriced |
| 4 | +0.0 | 1/10 | yes | 0.0990 | unpriced |

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
| 1,000 | 1,000 | 10,000 | error_suppression (s=None) | 131,548 | True |
| 1,000 | 10,000 | 0 | error_suppression (s=None) | 0 | False |
| 1,000 | 10,000 | 10,000 | error_suppression (s=None) | 131,548 | True |
| 1,000 | 100,000 | 0 | error_suppression (s=None) | 0 | False |
| 1,000 | 100,000 | 10,000 | error_suppression (s=None) | 131,548 | True |
| 1,000 | 1,000,000 | 0 | error_suppression (s=None) | 0 | False |
| 1,000 | 1,000,000 | 10,000 | error_suppression (s=None) | 131,548 | False |
| 100,000 | 1,000 | 0 | error_suppression (s=None) | 0 | False |
| 100,000 | 1,000 | 10,000 | error_suppression (s=None) | 131,548 | True |
| 100,000 | 10,000 | 0 | error_suppression (s=None) | 0 | False |
| 100,000 | 10,000 | 10,000 | error_suppression (s=None) | 131,548 | True |
| 100,000 | 100,000 | 0 | error_suppression (s=None) | 0 | False |
| 100,000 | 100,000 | 10,000 | error_suppression (s=None) | 131,548 | True |
| 100,000 | 1,000,000 | 0 | error_suppression (s=None) | 0 | False |
| 100,000 | 1,000,000 | 10,000 | error_suppression (s=None) | 131,548 | False |

Verdict under this rule: **fail**

Unpriced models: claude-3-5-sonnet-20241022, claude-3-haiku-20240307, claude3.5sonnet, gpt35_16k, meta-llama_Llama-3.3-70B-Instruct
Decile edges: 0.160, 0.222, 0.278, 0.353, 0.478, 0.637, 0.822, 0.939, 0.964

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
`results/2026-10-27_S3_<attack>.png`.

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
scenario cell (16 cells), seed 20261017. Each round the insurer refits the Phase 2
model class on the previous round's observed telemetry (attacked rows included)
and true outcomes. Attackers are rational: they apply the cheapest attack from
the any-agent S3 table (error suppression, free per run) whenever the breakeven
under the current scorer says it pays at the cell's exposure, paying E once.
Outputs carry `synthetic` in the filename and feed no headline result
(`results/2026-10-27_S4_flywheel_synthetic.json`, `.png`).

Result: **no collapse in any cell**. AUC after burn-in is 0.757 at f = 0 and
0.756 at f = 1 in every cell, against a naive baseline of 0.654. Attackers are
active (294 of 500 agents at f = 1 when E = 0; 0 to 200 when E = 10,000 USD,
depending on exposure) but error suppression barely moves the refit scorer, so
trust quality is flat in f. The boundary f is therefore not reached on this grid
and is reported as none.

Neither of the two preregistered outcomes fired by its fixed rule. "Converged"
required AUC within the Phase 2 held-out GBM CI [0.777, 0.888]; the simulation's
ceiling is lower (0.757) because its outcomes are Bernoulli draws from each
agent's rate, so within-agent variation is pure noise. The rule is kept as fixed
in DEVIATIONS and the mismatch is listed under limitations rather than patched
after the run. The substantive finding stands on the plot: a scorer that keeps
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

## Decisions at Gate 4 (founder)

To be filled by the founder.
