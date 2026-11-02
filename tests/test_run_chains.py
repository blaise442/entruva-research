import pandas as pd

from src.crosscheck.run_chains import _window


def test_ethereum_window_ends_at_the_later_of_the_two_files(tmp_path):
    identity = pd.DataFrame({"blockNumber": [100, 26_271_457]})
    feedback = pd.DataFrame({"blockNumber": [26_271_911]})
    w, days, windowed = _window(tmp_path, "ethereum-mainnet", identity, feedback)
    assert (w["head"], w["from_block"], days, windowed) == (26_271_911, 26_271_911 - 14_400, 2.0, False)


def test_window_fallback_uses_the_chains_own_block_time(tmp_path):
    """Base blocks are 2 s and BNB 0.45 s (measured 2026-10-29 from the window fetch
    timestamps), so two days is not 14,400 blocks on those chains."""
    identity = pd.DataFrame({"blockNumber": [1_000_000]})
    feedback = pd.DataFrame({"blockNumber": [1]})
    base, _, _ = _window(tmp_path, "base-mainnet", identity, feedback)
    bnb, _, _ = _window(tmp_path, "bnb-mainnet", identity, feedback)
    assert base["from_block"] == 1_000_000 - 86_400
    assert bnb["from_block"] == 1_000_000 - 384_000
