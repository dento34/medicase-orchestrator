"""UiPath Coded Agent entrypoint — RTSLookupAgent (Maestro Stage 2: Stabilization).

Runs three parallel real-time lookups: nearest AED (OpenStreetMap Overpass),
ambulance ETA, and LLM-based drug-interaction analysis.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from agents.uipath.rts_entry import run as _run


class RtsInput(BaseModel):
    case_id: str
    lat: float = Field(description="Patient latitude")
    lon: float = Field(description="Patient longitude")
    medications: list[str] = Field(default_factory=list)
    proposed_treatments: list[str] = Field(default_factory=list)
    patient_conditions: list[str] = Field(default_factory=list)
    aed_radius_m: int = Field(default=200, description="AED search radius (m)")


class RtsOutput(BaseModel):
    result: dict[str, Any] = Field(
        description="RTSLookupResult: AEDs, ambulance ETA, drug warnings"
    )


def main(input: RtsInput) -> RtsOutput:
    return RtsOutput(result=_run(input.model_dump()))
