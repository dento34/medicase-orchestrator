"""Pydantic models for LanguageAgent inputs and outputs."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


SeverityTier = Literal["critical", "urgent", "stable"]


class TriageRequest(BaseModel):
    """A volunteer-initiated triage trigger.

    At least one of (volunteer_utterance, patient_utterance, browser_locale)
    must be present for language detection to do useful work.
    """

    case_id: str = Field(..., description="UiPath Maestro Case ID")
    volunteer_utterance: str | None = Field(
        default=None,
        description="What the volunteer reports about the patient, in English.",
    )
    patient_utterance: str | None = Field(
        default=None,
        description="Raw transcript of the patient's first utterance.",
    )
    browser_locale: str | None = Field(
        default=None,
        description="Patient browser locale, e.g. 'pt-BR' — used as fallback hint.",
    )


class LanguageDetectionResult(BaseModel):
    """Detected language for downstream translation."""

    language_code: str = Field(..., description="ISO 639-1 code, e.g. 'pt'")
    language_name: str = Field(..., description="Human-readable name in English")
    confidence: float = Field(..., ge=0.0, le=1.0)
    rationale: str = Field(..., description="One-sentence explanation")


class TriageQuestionSet(BaseModel):
    """Standard emergency triage questions translated for the patient."""

    language_code: str
    questions: list[str] = Field(
        ..., description="Triage questions in the patient's language"
    )
    questions_english: list[str] = Field(
        ..., description="Source English questions (for traceability / audit)"
    )


class PatientResponse(BaseModel):
    """Structured representation of a patient's reply."""

    raw_text: str = Field(..., description="Patient's text, in their own language")
    detected_language: str = Field(..., description="ISO 639-1 code")
    english_translation: str = Field(
        ..., description="Faithful English translation for the case record"
    )
    structured: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Extracted fields: symptoms, allergies, medications, "
            "chronic_conditions, pain_location, pain_scale"
        ),
    )
