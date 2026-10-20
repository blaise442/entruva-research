"""ERC-8004 registry addresses, verified from primary sources on 2026-10-20.

Sources:
- https://eips.ethereum.org/EIPS/eip-8004 (Draft): defines the three registries,
  publishes no addresses, expects singleton deployments per chain.
- https://github.com/erc-8004/erc-8004-contracts (curated by the 8004 team, CC0):
  lists IdentityRegistry and ReputationRegistry, same address on every chain via
  deterministic deployment.
- Cross-checked against https://adapter8004.xyz/docs/addresses (IdentityRegistry matches).

The ValidationRegistry has no address in the curated repo or the cross-check
source; it is recorded in data/MANIFEST.md as a limitation, never guessed.
"""
REGISTRIES = {
    "ethereum-mainnet": {
        "identity": "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432",
        "reputation": "0x8004BAa17C55a88189AE136b182e5fdA19dE9b63",
    },
    "base-mainnet": {
        "identity": "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432",
        "reputation": "0x8004BAa17C55a88189AE136b182e5fdA19dE9b63",
    },
}
