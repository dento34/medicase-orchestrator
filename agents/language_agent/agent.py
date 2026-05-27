"""LanguageAgent — Stage 1 (Intake) language detection + in-language triage."""
from __future__ import annotations

import json
import re
from pathlib import Path

from .models import (
    LanguageDetectionResult,
    PatientResponse,
    TriageQuestionSet,
    TriageRequest,
)
from .prompts import (
    DETECT_LANGUAGE_SYSTEM,
    PARSE_RESPONSE_SYSTEM,
    TRANSLATE_TRIAGE_SYSTEM,
)
from ..shared.llm import LLMClient, make_client
from ..shared.logging import get_logger

logger = get_logger("language_agent")

_FIXTURES_DIR = Path(__file__).parent / "fixtures"
with open(_FIXTURES_DIR / "triage_questions.json", "r", encoding="utf-8") as f:
    _FIXTURES = json.load(f)

DEFAULT_QUESTIONS_EN: list[str] = _FIXTURES["default_questions_en"]


_CODE_FENCE_RE = re.compile(r"^```[a-zA-Z0-9_]*\s*|\s*```$", flags=re.MULTILINE)


def _parse_json_response(text: str) -> dict:
    """Extract JSON object from an LLM response.

    Tolerates models that wrap in ```json fences or add a stray prose prefix.
    """
    text = text.strip()
    if text.startswith("```"):
        text = _CODE_FENCE_RE.sub("", text).strip()
    # Find first '{' and last '}' to strip any stray prose.
    if "{" in text and "}" in text:
        text = text[text.index("{") : text.rindex("}") + 1]
    return json.loads(text)


class LanguageAgent:
    """Stage 1 helper: detect language, translate triage Qs, parse responses."""

    def __init__(self, llm: LLMClient | None = None):
        self.llm = llm or make_client()
        logger.info(f"LanguageAgent ready (llm={type(self.llm).__name__})")

    # -------------------------------------------------------------- detect
    def detect(self, request: TriageRequest) -> LanguageDetectionResult:
        snippet = request.patient_utterance or request.volunteer_utterance or ""
        if not snippet:
            if request.browser_locale:
                code = request.browser_locale.split("-")[0].lower()
                logger.info(
                    f"No utterance; falling back to browser locale '{request.browser_locale}'"
                )
                return LanguageDetectionResult(
                    language_code=code,
                    language_name=code.upper(),
                    confidence=0.5,
                    rationale=(
                        f"No utterance available; relied on browser locale "
                        f"'{request.browser_locale}'."
                    ),
                )
            raise ValueError(
                "Cannot detect language: no utterance and no browser_locale provided."
            )

        user_prompt = (
            f"Speech snippet: {snippet!r}\n"
            f"Browser locale: {request.browser_locale or 'unknown'}"
        )
        resp = self.llm.complete(system=DETECT_LANGUAGE_SYSTEM, user=user_prompt)
        data = _parse_json_response(resp)
        result = LanguageDetectionResult(**data)
        logger.info(
            f"Detected {result.language_name} ({result.language_code}) "
            f"conf={result.confidence:.2f}"
        )
        return result

    # ----------------------------------------------------- translate triage
    def generate_triage_questions(
        self,
        lang: LanguageDetectionResult,
        questions_en: list[str] | None = None,
    ) -> TriageQuestionSet:
        questions_en = questions_en or DEFAULT_QUESTIONS_EN
        system = TRANSLATE_TRIAGE_SYSTEM.format(language_name=lang.language_name)
        user_prompt = "Translate these questions:\n" + "\n".join(
            f"- {q}" for q in questions_en
        )
        resp = self.llm.complete(system=system, user=user_prompt)
        data = _parse_json_response(resp)
        translated = data["questions"]
        if len(translated) != len(questions_en):
            logger.warning(
                f"Translation count mismatch: got {len(translated)} for "
                f"{len(questions_en)} source questions"
            )
        return TriageQuestionSet(
            language_code=lang.language_code,
            questions=translated,
            questions_english=questions_en,
        )

    # --------------------------------------------------- parse patient reply
    def parse_patient_response(
        self,
        raw_reply: str,
        lang: LanguageDetectionResult,
    ) -> PatientResponse:
        system = PARSE_RESPONSE_SYSTEM.format(language_name=lang.language_name)
        user_prompt = f"Patient said: {raw_reply!r}"
        resp = self.llm.complete(system=system, user=user_prompt)
        data = _parse_json_response(resp)
        english = data.pop("english_translation", "")
        return PatientResponse(
            raw_text=raw_reply,
            detected_language=lang.language_code,
            english_translation=english,
            structured=data,
        )
