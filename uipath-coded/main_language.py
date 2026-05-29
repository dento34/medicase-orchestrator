"""UiPath Coded Agent entrypoint — LanguageAgent (Maestro Stage 1: Intake).

op-based: detect (language) | translate (in-language triage questions) | parse.
Detection falls back to browser locale when no LLM key is set, so it runs
deterministically in CI / license-limited tenants.
"""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

from agents.uipath.language_entry import run as _run


class LanguageInput(BaseModel):
    op: str = Field(default="detect", description="detect | translate | parse")
    case_id: str
    patient_utterance: Optional[str] = None
    volunteer_utterance: Optional[str] = None
    browser_locale: Optional[str] = Field(default=None, description="e.g. 'pt-BR'")
    language: Optional[dict[str, Any]] = Field(
        default=None, description="LanguageDetectionResult (for translate/parse)"
    )
    questions_en: Optional[list[str]] = None
    reply: Optional[str] = None


class LanguageOutput(BaseModel):
    result: dict[str, Any] = Field(
        description="Detection result, translated questions, or parsed reply"
    )


def main(input: LanguageInput) -> LanguageOutput:
    payload = input.model_dump(exclude_none=True)
    return LanguageOutput(result=_run(payload))
