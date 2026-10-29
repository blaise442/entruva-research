"""One anonymous request per chain to the 8004scan public API, used only as a
bound on our registration count (DEVIATIONS 2026-10-28, cross-check rules)."""
from datetime import date

import requests

BASE = "https://api.8004scan.io/api/v1"


def newest_token_id(chain_id: int, get=requests.get) -> dict:
    url = f"{BASE}/agents?chain_id={chain_id}&limit=1&is_active=any&is_registered=true"
    r = get(url, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"8004scan returned {r.status_code} for chain {chain_id}")
    body = r.json()
    try:
        return {"chain_id": chain_id, "token_id": int(body["items"][0]["token_id"]), "total": int(body["total"]),
                "url": url, "date": date.today().isoformat()}
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise RuntimeError(f"8004scan response for chain {chain_id} lacks items[0].token_id or total: {exc}")


def count_check(n_registered: int, max_agent_id: int, api: dict | None, complete: bool = True) -> dict:
    """complete=False marks a windowed fetch, where our count cannot equal max id plus one."""
    out = {"n_registered": n_registered, "max_agent_id": max_agent_id,
           "api_token_id": api["token_id"] if api else None, "api_total": api["total"] if api else None}
    if api is None:
        return {"status": "not run", **out}
    if not complete:
        return {"status": "not applicable", **out}
    ok = n_registered == max_agent_id + 1 and max_agent_id <= api["token_id"]
    return {"status": "pass" if ok else "fail", **out}
