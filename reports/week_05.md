# Week 5 report (2026-11-02)

## What ran

- The research page gained a data section on 2026-10-29: dataset counts, the
  model table with intervals, the breakeven table, the ERC-8004 counts, the
  cross-check table and four result plots.
- The founder approved spend on 2026-11-01 (Alchemy paid plan, estimate about
  one dollar) and the full Base and BNB Smart Chain registries were fetched on
  2026-11-02, closing Gate 5 decision 2. The free plan could not do it: its
  eth_getLogs range is 10 blocks on every chain.
- The first paid run was incomplete on BNB. The provider answers a range wider
  than 10,000 blocks with a short log list and no error; 13 agent ids were
  missing. The collector is now capped at 10,000 blocks per call, both chains
  were refetched, and an integrity check passes on all three chains: ids
  contiguous, feedback indices contiguous, no duplicate logs (DEVIATIONS
  2026-11-02). Two new tests, suite at 176.
- Full-history reputation descriptives for three chains sit side by side in the
  Gate 5 report update: Base 1,149,957 agents and 673,980 feedback events, BNB
  401,341 and 30,144, Ethereum 55,407 and 34,493. The 8004scan count check
  passes on all three.

## What it means

The feedback concentration described in week three holds on every chain: the
share of agents whose feedback comes from a single wallet is 0.92 on Ethereum,
0.91 on Base and 0.89 on BNB, and the median agent with feedback has one entry.
Base differs in scale, not shape: one agent holds 390,890 of its 673,980
feedback entries, and 136,371 distinct wallets gave feedback, almost one per
agent. The Sybil-cost finding from Gate 4 therefore reads across chains.

## Next

- Weekly reports through day 90; final write-up on 2027-01-15.
- The data request to the arXiv 2606.26028 authors remains unanswered.
