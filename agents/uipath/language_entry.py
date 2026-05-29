"""UiPath Coded Agent entry-point for LanguageAgent (Stage 1)."""
from __future__ import annotations

from typing import Any

from ..language_agent import LanguageAgent, TriageRequest
from ..language_agent.models import LanguageDetectionResult
from ..shared.logging import get_logger

logger = get_logger("uipath.language")


def run(input: dict[str, Any]) -> dict[str, Any]:
    """Dispatch by `op`: detect | translate | parse.

    input:
      { "op": "detect", "case_id", "patient_utterance"?, "volunteer_utterance"?,
        "browser_locale"? }
      { "op": "translate", "language": {<LanguageDetectionResult>},
        "questions_en"?: [...] }
      { "op": "parse", "reply": "...", "language": {<LanguageDetectionResult>} }
    """
    op = input.get("op", "detect")
    agent = LanguageAgent()

    if op == "detect":
        req = TriageRequest(
            case_id=input["case_id"],
            patient_utterance=input.get("patient_utterance"),
            volunteer_utterance=input.get("volunteer_utterance"),
            browser_locale=input.get("browser_locale"),
        )
        return agent.detect(req).model_dump()

    if op == "translate":
        lang = LanguageDetectionResult(**input["language"])
        qs = agent.generate_triage_questions(lang, input.get("questions_en"))
        return qs.model_dump()

    if op == "parse":
        lang = LanguageDetectionResult(**input["language"])
        parsed = agent.parse_patient_response(input["reply"], lang)
        return parsed.model_dump()

    raise ValueError(f"Unknown op: {op!r}")
