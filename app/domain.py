from langchain_core.tools import tool

from agentic_core.contracts import AgentRun, Explanation
from agentic_core.tracing import observe_agent
from agentic_core.workflow import run_agent_workflow

TRANSACTIONS = [{"id": "TX-201", "amount": 42, "velocity_1h": 1, "new_device": False, "country_mismatch": False}, {"id": "TX-202", "amount": 1250, "velocity_1h": 7, "new_device": True, "country_mismatch": True}, {"id": "TX-203", "amount": 210, "velocity_1h": 3, "new_device": True, "country_mismatch": False}]


@tool
def get_transaction_signals() -> list[dict]:
    """Return deterministic synthetic transaction features for analyst review."""
    return TRANSACTIONS


def collect() -> list[dict]:
    return [{"source": "transaction_monitoring", "fact": row["id"], "value": row} for row in get_transaction_signals.invoke({})]


def policy(evidence: list[dict]) -> dict:
    alerts = []
    for item in evidence:
        tx = item["value"]
        score = min(100, int(tx["amount"] / 25) + tx["velocity_1h"] * 8 + (20 if tx["new_device"] else 0) + (25 if tx["country_mismatch"] else 0))
        alerts.append({"transaction": tx["id"], "risk_score": score, "disposition": "analyst_review" if score >= 60 else "monitor", "signals": [key for key in ("new_device", "country_mismatch") if tx[key]]})
    return {"alerts": alerts, "review_queue": [alert["transaction"] for alert in alerts if alert["disposition"] == "analyst_review"], "execution": "no_automatic_decline"}


def fallback(result: dict) -> Explanation:
    return Explanation(summary=f"{len(result['review_queue'])} transactions require analyst review.", rationale="The reproducible score combines amount, velocity, device novelty, and country mismatch; it is not a fraud verdict.", next_steps=["Inspect transaction evidence", "Record analyst disposition"])


def analyze(request: str) -> AgentRun:
    with observe_agent("fraud-investigation", {"request": request}):
        return run_agent_workflow(domain="fraud_investigation", request=request, collect_evidence=collect, apply_policy=policy, fallback_explanation=fallback)
