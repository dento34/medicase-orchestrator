"""Pydantic models for SummaryAgent."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PatientSnapshot(BaseModel):
    """Everything we know about the patient at handoff time.

    Fields are optional because real emergencies are incomplete. The
    handoff renderer shows 'Unknown' for missing data rather than omitting.
    """

    name: str | None = None
    approx_age: str | None = Field(default=None, description="e.g. '35-45'")
    sex: str | None = None
    language_name: str | None = None
    language_code: str | None = None

    symptoms: list[str] = Field(default_factory=list)
    pain_location: str | None = None
    pain_scale: int | None = None
    allergies: list[str] = Field(default_factory=list)
    medications: list[str] = Field(default_factory=list)
    chronic_conditions: list[str] = Field(default_factory=list)

    wearable_snapshot: dict[str, Any] | None = Field(
        default=None, description="e.g. {'hr': 142, 'rhythm': 'irregular'}"
    )


class HandoffReport(BaseModel):
    """The full handoff package for the receiving hospital."""

    case_id: str
    created_at: datetime = Field(default_factory=_utcnow)

    patient: PatientSnapshot

    location: str | None = None
    nearest_aed: str | None = None
    ambulance_eta_min: int | None = None
    drug_warnings: list[str] = Field(default_factory=list)

    handed_off_by: str | None = None
    accepted_by: str | None = None

    clinical_impression: str | None = Field(
        default=None,
        description="AI-generated one-liner; clearly labelled in render",
    )
