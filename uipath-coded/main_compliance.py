"""UiPath Coded Agent entrypoint — ComplianceAgent (Maestro Stage 4: Post-incident).

op-based: log (audit event) | close (anonymize + archive case) |
similar (retrieve prior anonymized cases) | trail (full audit trail).
"""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

from agents.uipath.compliance_entry import run as _run


class ComplianceInput(BaseModel):
    op: str = Field(default="log", description="log | close | similar | trail")
    case_id: Optional[str] = None
    kind: Optional[str] = Field(default=None, description="audit event kind (log)")
    actor: Optional[str] = None
    summary: Optional[str] = None
    payload: Optional[dict[str, Any]] = None
    opened_at: Optional[str] = Field(default=None, description="ISO time (close)")
    language_code: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    symptom_cluster: Optional[str] = None
    severity: Optional[str] = None
    interventions: list[str] = Field(default_factory=list)
    outcome: Optional[str] = None
    event_venue_type: Optional[str] = None
    limit: int = Field(default=5, description="similar: max prior cases")


class ComplianceOutput(BaseModel):
    result: dict[str, Any] = Field(
        description="audit event, anonymized record, similar cases, or trail"
    )


def main(input: ComplianceInput) -> ComplianceOutput:
    return ComplianceOutput(result=_run(input.model_dump(exclude_none=True)))
