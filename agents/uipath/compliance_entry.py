"""UiPath Coded Agent entry-point for ComplianceAgent (Stage 4 + audit)."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from ..compliance_agent import ComplianceAgent
from ..shared.logging import get_logger

logger = get_logger("uipath.compliance")


def run(input: dict[str, Any]) -> dict[str, Any]:
    """Dispatch by `op`: log | close | similar | trail.

    input:
      { "op": "log", "case_id", "kind", "actor", "summary", "payload"? }
      { "op": "close", "case_id", "opened_at"(iso), "language_code", "age",
        "sex", "symptom_cluster", "severity", "interventions": [...],
        "outcome", "event_venue_type"? }
      { "op": "similar", "symptom_cluster"?, "language_code"?, "limit"? }
      { "op": "trail", "case_id" }
    """
    op = input.get("op", "log")
    agent = ComplianceAgent()

    if op == "log":
        ev = agent.log_event(
            case_id=input["case_id"],
            kind=input["kind"],
            actor=input["actor"],
            summary=input["summary"],
            payload=input.get("payload"),
        )
        return ev.model_dump()

    if op == "close":
        rec = agent.close_case(
            case_id=input["case_id"],
            opened_at=datetime.fromisoformat(input["opened_at"]),
            language_code=input.get("language_code"),
            age=input.get("age"),
            sex=input.get("sex"),
            symptom_cluster=input.get("symptom_cluster"),
            severity=input.get("severity"),
            interventions=input.get("interventions", []),
            outcome=input.get("outcome"),
            event_venue_type=input.get("event_venue_type"),
        )
        return rec.model_dump()

    if op == "similar":
        recs = agent.similar_prior_cases(
            symptom_cluster=input.get("symptom_cluster"),
            language_code=input.get("language_code"),
            limit=input.get("limit", 5),
        )
        return {"cases": [r.model_dump() for r in recs]}

    if op == "trail":
        evs = agent.case_audit_trail(input["case_id"])
        return {"events": [e.model_dump() for e in evs]}

    raise ValueError(f"Unknown op: {op!r}")
