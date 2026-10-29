import pandas as pd

from src.crosscheck.run_chains import _window


def test_ethereum_window_ends_at_the_later_of_the_two_files(tmp_path):
    identity = pd.DataFrame({"blockNumber": [100, 26_271_457]})
    feedback = pd.DataFrame({"blockNumber": [26_271_911]})
    w, days, windowed = _window(tmp_path, "ethereum-mainnet", identity, feedback)
    assert (w["head"], w["from_block"], days, windowed) == (26_271_911, 26_271_911 - 14_400, 2.0, False)
