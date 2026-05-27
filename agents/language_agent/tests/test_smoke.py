"""LanguageAgent smoke test.

Run modes:
  - MOCK (default, offline, deterministic) — always runs
  - REAL (calls Anthropic API) — only if ANTHROPIC_API_KEY is set in .env

Usage from project root:
    .venv/Scripts/python.exe agents/language_agent/tests/test_smoke.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Allow running this file directly without `pip install -e .`
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from agents.language_agent import LanguageAgent, TriageRequest  # noqa: E402
from agents.shared.env import load  # noqa: E402
from agents.shared.llm import AnthropicClient, MockClient  # noqa: E402
from agents.shared.logging import get_logger  # noqa: E402

logger = get_logger("smoke")
load()  # load .env from project root

# ---------------------------------------------------------------------------
# MOCK fixtures — keyed on substring matches against the user prompt the
# LanguageAgent will build. Order matters: first match wins.
# ---------------------------------------------------------------------------
MOCK_FIXTURES: dict[str, str] = {
    "Speech snippet": json.dumps(
        {
            "language_code": "pt",
            "language_name": "Portuguese",
            "confidence": 0.92,
            "rationale": "Phrases like 'minha cabeça' are clearly Portuguese.",
        }
    ),
    "Translate these questions": json.dumps(
        {
            "questions": [
                "Onde está doendo?",
                "Numa escala de 0 a 10, qual é a intensidade da dor?",
                "Você tem alguma alergia?",
                "Está tomando algum remédio agora?",
                "Tem alguma condição crônica, como diabetes ou problemas cardíacos?",
            ]
        }
    ),
    "Patient said": json.dumps(
        {
            "symptoms": ["chest pain", "dizziness"],
            "allergies": ["penicillin"],
            "medications": ["Losartan 50mg"],
            "chronic_conditions": ["hypertension"],
            "pain_location": "chest",
            "pain_scale": 8,
            "english_translation": (
                "My chest hurts a lot, the pain is 8 out of 10. "
                "I am allergic to penicillin. I take Losartan."
            ),
        }
    ),
}


SCENARIO = {
    "case_id": "case-2026-05-27-001",
    "patient_utterance": "Minha cabeça está doendo muito.",
    "browser_locale": "pt-BR",
    "patient_reply": (
        "Meu peito dói muito, é um 8. Tenho alergia a penicilina. "
        "Tomo Losartan."
    ),
}


def _run_pipeline(agent: LanguageAgent) -> dict:
    request = TriageRequest(
        case_id=SCENARIO["case_id"],
        patient_utterance=SCENARIO["patient_utterance"],
        browser_locale=SCENARIO["browser_locale"],
    )

    print("\n--- detect ---")
    lang = agent.detect(request)
    print(
        f"  language    : {lang.language_name} ({lang.language_code})\n"
        f"  confidence  : {lang.confidence}\n"
        f"  rationale   : {lang.rationale}"
    )

    print("\n--- translate triage ---")
    triage = agent.generate_triage_questions(lang)
    print(f"  language    : {triage.language_code}")
    print(f"  questions   : ({len(triage.questions)} translated)")
    for q in triage.questions:
        print(f"    - {q}")

    print("\n--- parse patient reply ---")
    parsed = agent.parse_patient_response(SCENARIO["patient_reply"], lang)
    print(f"  english     : {parsed.english_translation}")
    print(f"  structured  : {json.dumps(parsed.structured, ensure_ascii=False)}")

    return {
        "lang": lang.model_dump(),
        "triage": triage.model_dump(),
        "parsed": parsed.model_dump(),
    }


def test_mock_mode() -> dict:
    print("\n" + "=" * 70)
    print("MOCK mode (offline)")
    print("=" * 70)
    agent = LanguageAgent(llm=MockClient(MOCK_FIXTURES))
    result = _run_pipeline(agent)

    # Lightweight assertions
    assert result["lang"]["language_code"] == "pt", "expected Portuguese"
    assert any("doendo" in q.lower() for q in result["triage"]["questions"]), (
        "expected at least one translated question containing 'doendo'"
    )
    assert result["parsed"]["structured"]["pain_scale"] == 8, "expected pain_scale=8"
    assert "penicillin" in [
        a.lower() for a in result["parsed"]["structured"]["allergies"]
    ], "expected penicillin in allergies"

    print("\n[OK] mock-mode smoke test passed.")
    return result


def test_real_mode_if_key() -> dict | None:
    print("\n" + "=" * 70)
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("REAL mode — SKIPPED (no ANTHROPIC_API_KEY in .env)")
        print("=" * 70)
        return None

    print("REAL mode (Anthropic API)")
    print("=" * 70)
    agent = LanguageAgent(llm=AnthropicClient())
    result = _run_pipeline(agent)
    print("\n[OK] real-mode smoke test completed.")
    return result


if __name__ == "__main__":
    test_mock_mode()
    test_real_mode_if_key()
    print("\nAll requested tests finished.\n")
