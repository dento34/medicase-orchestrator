"""UiPath Coded Agent entrypoint — SummaryAgent (Maestro Stage 3: Handoff).

Typed Pydantic in/out so UiPath `uipath init` can generate a clean I/O
schema that Maestro can map field-by-field. The actual logic lives in the
shared `agents` package (template-driven handoff; never LLM for critical
clinical fields).
"""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

from agents.uipath.summary_entry import run as _summary_run


class PatientSnapshotIn(BaseModel):
    name: Optional[str] = None
    approx_age: Optional[str] = Field(default=None, description="e.g. '35-45'")
    sex: Optional[str] = None
    language_name: Optional[str] = None
    language_code: Optional[str] = None
    symptoms: list[str] = Field(default_factory=list)
    pain_location: Optional[str] = None
    pain_scale: Optional[int] = None
    allergies: list[str] = Field(default_factory=list)
    medications: list[str] = Field(default_factory=list)
    chronic_conditions: list[str] = Field(default_factory=list)
    wearable_snapshot: Optional[dict[str, Any]] = None


class SummaryInput(BaseModel):
    case_id: str
    patient: PatientSnapshotIn
    location: Optional[str] = None
    nearest_aed: Optional[str] = None
    ambulance_eta_min: Optional[int] = None
    drug_warnings: list[str] = Field(default_factory=list)
    handed_off_by: Optional[str] = None
    accepted_by: Optional[str] = None
    with_impression: bool = Field(
        default=False,
        description="If true, adds an LLM clinical impression (needs API key).",
    )


class SummaryOutput(BaseModel):
    rendered_text: str = Field(description="Human-readable handoff card")
    report: dict[str, Any] = Field(description="Structured HandoffReport")


def main(input: SummaryInput) -> SummaryOutput:
    out = _summary_run(input.model_dump())
    return SummaryOutput(rendered_text=out["rendered_text"], report=out["report"])
