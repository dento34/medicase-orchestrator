"""UiPath Coded Agent entry-point for SummaryAgent (Stage 3)."""
from __future__ import annotations

from typing import Any

from ..summary_agent import SummaryAgent, PatientSnapshot
from ..shared.llm import make_client
from ..shared.logging import get_logger

logger = get_logger("uipath.summary")


def run(input: dict[str, Any]) -> dict[str, Any]:
    """Build the handoff package.

    input:
      { "case_id", "patient": {<PatientSnapshot>},
        "location"?, "nearest_aed"?, "ambulance_eta_min"?,
        "drug_warnings"?: [...], "handed_off_by"?, "accepted_by"?,
        "with_impression"?: bool }

    output: { "report": {<HandoffReport>}, "rendered_text": "..." }
    """
    patient = PatientSnapshot(**input["patient"])
    # Impression is optional and only runs if a real LLM key is present.
    llm = make_client(prefer_real=True) if input.get("with_impression", True) else None
    agent = SummaryAgent(llm=llm)
    report = agent.build_handoff(
        case_id=input["case_id"],
        patient=patient,
        location=input.get("location"),
        nearest_aed=input.get("nearest_aed"),
        ambulance_eta_min=input.get("ambulance_eta_min"),
        drug_warnings=input.get("drug_warnings", []),
        handed_off_by=input.get("handed_off_by"),
        accepted_by=input.get("accepted_by"),
        with_impression=input.get("with_impression", True),
    )
    return {
        "report": report.model_dump(),
        "rendered_text": agent.render_text(report),
    }
