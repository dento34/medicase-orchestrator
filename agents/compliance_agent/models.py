"""Pydantic models for ComplianceAgent."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

AuditEventKind = Literal[
    "case_opened",
    "agent_invoked",
    "agent_completed",
    "human_decision",
    "data_accessed",
    "external_api_called",
    "exception_raised",
    "stage_transition",
    "case_closed",
    # Orchestration-completion variants (final stage emits one of these to
    # signal the whole MediCase flow has wrapped up):
    "case_completed",
    "case_resolved",
]


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AuditEvent(BaseModel):
    """One immutable audit-log entry."""

    case_id: str
    kind: AuditEventKind
    actor: str = Field(..., description="agent name, user id, or 'system'")
    summary: str = Field(..., description="short, human-readable")
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=_utcnow)


class AnonymizedCaseRecord(BaseModel):
    """Stripped-down representation of a closed case for organizational learning.

    Fields chosen to retain clinical signal without re-identifying the patient.
    """

    case_id_hash: str = Field(..., description="SHA-256 truncated case_id")
    closed_at: datetime
    language_family: str | None = None
    age_band: str | None = Field(
        default=None,
        description="Bucketed age range, e.g. '30-44', not exact age",
    )
    sex: str | None = None
    symptom_cluster: str | None = Field(
        default=None, description="cardiac / trauma / neuro / allergic / general"
    )
    severity: str | None = None
    interventions: list[str] = Field(default_factory=list)
    outcome: str | None = Field(
        default=None,
        description="resolved_on_site / transported / no_show / unknown",
    )
    duration_seconds: int | None = None
    event_venue_type: str | None = Field(
        default=None,
        description="stadium / airport / festival / pilgrimage / cruise / other",
    )
