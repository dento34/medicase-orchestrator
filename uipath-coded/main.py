"""UiPath Coded Agent entrypoint — MediCase dispatcher.

The hackathon staging tenant allows a single published process in the
personal workspace, and the Maestro agent picker binds a package to its
first entrypoint (no per-node entrypoint selection). To wire ALL FOUR coded
agents into the Maestro flow under that one-process limit, this single
entrypoint dispatches to the right agent based on the `agent` input:

    agent = "language"  -> LanguageAgent   (Stage 1 Intake)
    agent = "rts"       -> RTSLookupAgent   (Stage 2 Stabilization)
    agent = "summary"   -> SummaryAgent     (Stage 3 Handoff)
    agent = "compliance"-> ComplianceAgent  (Stage 4 Post-incident)

Each Maestro node binds to this same process and sets `agent` to its stage
plus a `payload` matching that agent's entry contract (see agents/uipath/*).
The typed per-agent entrypoints (main_language.py, main_rts.py, etc.) remain
in the repo as documentation of each agent's I/O contract.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from agents.uipath import (
    compliance_entry,
    language_entry,
    rts_entry,
    summary_entry,
)

_ROUTES = {
    "language": language_entry.run,
    "rts": rts_entry.run,
    "summary": summary_entry.run,
    "compliance": compliance_entry.run,
}

# Fields the underlying agents type as list[str]. When Maestro passes them
# from String process arguments they arrive as comma-separated strings; we
# split them transparently so the typed agent contracts hold without the
# canvas needing to know about List<String> (which Maestro's arg picker
# doesn't expose).
_LIST_FIELDS = {
    "medications",
    "proposed_treatments",
    "patient_conditions",
    "symptoms",
    "allergies",
    "chronic_conditions",
    "drug_warnings",
    "interventions",
}


def _split_csv(value: str) -> list[str]:
    return [s.strip() for s in value.split(",") if s.strip()]


def _normalize(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize string list-fields to actual lists, top-level and under `patient`."""
    out = dict(payload)
    for k in _LIST_FIELDS:
        v = out.get(k)
        if isinstance(v, str):
            out[k] = _split_csv(v)
    patient = out.get("patient")
    if isinstance(patient, dict):
        p = dict(patient)
        for k in _LIST_FIELDS:
            v = p.get(k)
            if isinstance(v, str):
                p[k] = _split_csv(v)
        out["patient"] = p
    return out


class DispatchInput(BaseModel):
    agent: str = Field(description="language | rts | summary | compliance")
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Input for the selected agent (see agents/uipath/*_entry.py)",
    )


class DispatchOutput(BaseModel):
    agent: str = Field(description="Which agent was invoked")
    result: dict[str, Any] = Field(description="The selected agent's output")


def main(input: DispatchInput) -> DispatchOutput:
    key = (input.agent or "").strip().lower()
    fn = _ROUTES.get(key)
    if fn is None:
        raise ValueError(
            f"Unknown agent {input.agent!r}. "
            f"Expected one of: {', '.join(_ROUTES)}"
        )
    return DispatchOutput(agent=key, result=fn(_normalize(input.payload)))
