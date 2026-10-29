import pandas as pd

from src.crosscheck.dataverse_eth import (check_agents_core, check_feedback, check_summary, check_transfers,
                                          feedback, observation_block, registered, transfers, verdict)

ZERO = "0x" + "00" * 20
A, B, C = "0x" + "aa" * 20, "0x" + "bb" * 20, "0x" + "cc" * 20
TX = "0x" + "ab" * 32


def _identity():
    """Agents 0, 1, 2 minted at block 10; agent 1 transferred A->B at block 50 and B->C at block 90."""
    rows = []
    for i in range(3):
        rows.append({"blockNumber": 10, "logIndex": 2 * i, "transactionHash": TX, "event": "Registered",
                     "args": {"agentId": i, "agentURI": "", "owner": A}})
        rows.append({"blockNumber": 10, "logIndex": 2 * i + 1, "transactionHash": TX, "event": "Transfer",
                     "args": {"from": ZERO, "to": A, "tokenId": i}})
    rows.append({"blockNumber": 50, "logIndex": 0, "transactionHash": "0x" + "11" * 32, "event": "Transfer", "args": {"from": A, "to": B, "tokenId": 1}})
    rows.append({"blockNumber": 90, "logIndex": 0, "transactionHash": "0x" + "22" * 32, "event": "Transfer", "args": {"from": B, "to": C, "tokenId": 1}})
    return pd.DataFrame(rows)


def _reputation():
    return pd.DataFrame([{"blockNumber": 60, "logIndex": 0, "transactionHash": TX, "event": "NewFeedback",
                          "args": {"agentId": i, "clientAddress": B, "feedbackIndex": 1}} for i in (0, 1)]
                        + [{"blockNumber": 61, "logIndex": 0, "transactionHash": TX, "event": "NewFeedback",
                            "args": {"agentId": 1, "clientAddress": B, "feedbackIndex": 2}}])


def _core(owner1=C, extra=None):
    rows = [{"agent_id": i, "mint_block": 10, "mint_tx_hash": "AB" * 32, "owner_wallet": A} for i in range(3)]
    rows[1]["owner_wallet"] = owner1
    if extra is not None:
        rows.append(extra)
    return pd.DataFrame(rows)


def test_agents_core_matches_hash_without_prefix_case_insensitively():
    out = check_agents_core(_core(), registered(_identity()), transfers(_identity()))
    assert out["rows"] == 3 and out["agreeing"] == 3 and out["disagreeing"] == 0 and out["keys"] == []


def test_agents_core_lists_agents_missing_from_our_logs():
    core = _core(extra={"agent_id": 3, "mint_block": 10, "mint_tx_hash": "ab" * 32, "owner_wallet": A})
    out = check_agents_core(core, registered(_identity()), transfers(_identity()))
    assert out["disagreeing"] == 1 and out["keys"] == [3]


def test_observation_block_is_none_when_owners_never_all_agree():
    core = _core(owner1="0x" + "dd" * 20)
    assert observation_block(core, transfers(_identity())) is None
    out = check_agents_core(core, registered(_identity()), transfers(_identity()))
    assert out["observation_block"] is None and out["keys"] == [1]


def test_observation_block_is_the_smallest_block_with_full_agreement():
    assert observation_block(_core(owner1=B), transfers(_identity())) == 50
    assert observation_block(_core(owner1=C), transfers(_identity())) == 90


def test_transfers_exclude_mints_from_our_window_count():
    dv = pd.DataFrame([{"agent_id": 1, "tx_hash": "11" * 32, "log_index": 0, "block_number": 50},
                       {"agent_id": 1, "tx_hash": "22" * 32, "log_index": 0, "block_number": 90}])
    out = check_transfers(dv, transfers(_identity()), {0, 1, 2})
    assert out["rows"] == 2 and out["agreeing"] == 2 and out["ours_in_window"] == 2 and out["theirs"] == 2


def test_feedback_rows_must_all_exist_in_ours():
    dv = pd.DataFrame([{"agent_id": 0, "client_address": B.upper(), "feedback_index": 1},
                       {"agent_id": 1, "client_address": B, "feedback_index": 9}])
    out = check_feedback(dv, feedback(_reputation()))
    assert out["rows"] == 2 and out["agreeing"] == 1 and out["disagreeing"] == 1 and out["keys"] == [[1, B, 9]]


def test_summary_counts_may_grow_but_never_shrink():
    ok = pd.DataFrame([{"agent_id": 0, "feedback_count_total": 1}, {"agent_id": 1, "feedback_count_total": 1}, {"agent_id": 2, "feedback_count_total": 0}])
    out = check_summary(ok, feedback(_reputation()))
    assert out["rows"] == 3 and out["at_most_ours"] == 3 and out["equal"] == 2 and out["disagreeing"] == 0
    bad = pd.DataFrame([{"agent_id": 1, "feedback_count_total": 3}])
    assert check_summary(bad, feedback(_reputation()))["disagreeing"] == 1


def test_verdict_names_the_failing_checks():
    clean = {"agents_core": {"disagreeing": 0}, "transfer_history": {"disagreeing": 0, "ours_in_window": 2, "theirs": 2},
             "agent_feedback_records": {"disagreeing": 0}, "agent_reputation_summary": {"disagreeing": 0}}
    assert verdict(clean) == "matches row for row"
    failing = {**clean, "agent_feedback_records": {"disagreeing": 1}}
    assert verdict(failing).startswith("differs: agent_feedback_records")
    extra = {**clean, "transfer_history": {"disagreeing": 0, "ours_in_window": 3, "theirs": 2}}
    assert verdict(extra) == "differs: transfer_history"


def test_transfers_notice_an_agent_whose_rows_the_dataset_lacks():
    """The window count runs over every core agent, not only agents the dataset lists."""
    ident = _identity()
    ident = pd.concat([ident, pd.DataFrame([{"blockNumber": 50, "logIndex": 1, "transactionHash": "0x" + "33" * 32, "event": "Transfer",
                                             "args": {"from": A, "to": B, "tokenId": 2}}])], ignore_index=True)
    dv = pd.DataFrame([{"agent_id": 1, "tx_hash": "11" * 32, "log_index": 0, "block_number": 50},
                       {"agent_id": 1, "tx_hash": "22" * 32, "log_index": 0, "block_number": 90}])
    out = check_transfers(dv, transfers(ident), {0, 1, 2})
    assert out["ours_in_window"] == 3 and out["theirs"] == 2 and out["their_max_block"] == 90
    assert verdict({"transfer_history": out}) == "differs: transfer_history"
