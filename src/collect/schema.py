"""The preregistered unified trace schema. Every parser writes these rows.

agent_id is the grouped-CV key: model_id + "::" + harness. Rows from one
agent_id never span train and test (see docs/PREREGISTRATION.md).
"""
SOURCES = ("tau-bench", "swe-bench", "agentdojo", "webarena", "erc8004", "incident")

TRACE_COLUMNS = [
    "trace_id", "source", "domain", "model_id", "agent_id", "task_id", "task_type",
    "task_length_steps", "outcome", "started_at",
    "has_step_latency", "has_tool_calls", "has_retries", "has_errors",
]

def make_trace_row(*, trace_id, source, domain, model_id, agent_id, task_id, task_type,
                   task_length_steps, outcome, started_at,
                   has_step_latency, has_tool_calls, has_retries, has_errors) -> dict:
    if source not in SOURCES:
        raise ValueError(f"unknown source {source!r}; expected one of {SOURCES}")
    if outcome not in (0, 1):
        raise ValueError(f"outcome must be 0 or 1, got {outcome!r}")
    if int(task_length_steps) < 0:
        raise ValueError(f"task_length_steps must be >= 0, got {task_length_steps!r}")
    local = locals()
    return {c: local[c] for c in TRACE_COLUMNS}
