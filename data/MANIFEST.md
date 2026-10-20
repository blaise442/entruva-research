# Data manifest

Every source gets one section before its data is used. data/raw is gitignored; this file plus src/collect regenerates it.

Format:
## <source name>
- URL / contract address:
- Fetch date:
- Method (script path):
- Row count:
- SHA-256:
- License:
- Known limitations:



## erc8004 registry events (pending)
- URL / contract address: IdentityRegistry and ReputationRegistry at 0x8004A169FB4a3325136EB29fA0ceB6D2e539a432 / 0x8004BAa17C55a88189AE136b182e5fdA19dE9b63 on Ethereum mainnet and Base (source: https://github.com/erc-8004/erc-8004-contracts, cross-checked 2026-10-20)
- Fetch date: not yet fetched
- Method (script path): src/collect/erc8004.py
- Row count: 0
- SHA-256: none (no file yet)
- License: public blockchain data
- Known limitations: awaiting RPC endpoint from the founder; the EIP publishes no addresses itself (Draft); the ValidationRegistry has no published curated address and is excluded until one is verified
