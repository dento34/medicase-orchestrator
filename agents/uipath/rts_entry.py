"""UiPath Coded Agent entry-point for RTSLookupAgent (Stage 2)."""
from __future__ import annotations

from typing import Any

from ..rts_lookup_agent import RTSLookupAgent, RTSLookupRequest
from ..rts_lookup_agent.models import GeoPoint
from ..shared.llm import make_client
from ..shared.logging import get_logger

logger = get_logger("uipath.rts")


def run(input: dict[str, Any]) -> dict[str, Any]:
    """Run the three parallel lookups.

    input:
      { "case_id", "lat", "lon",
        "medications": [...], "proposed_treatments": [...],
        "patient_conditions": [...], "aed_radius_m"? }
    """
    req = RTSLookupRequest(
        case_id=input["case_id"],
        location=GeoPoint(lat=input["lat"], lon=input["lon"]),
        medications=input.get("medications", []),
        proposed_treatments=input.get("proposed_treatments", []),
        patient_conditions=input.get("patient_conditions", []),
        aed_radius_m=input.get("aed_radius_m", 200),
    )
    # Use a real LLM for drug interactions if a key is configured.
    llm = make_client(prefer_real=True)
    agent = RTSLookupAgent(llm=llm)
    return agent.lookup(req).model_dump()
