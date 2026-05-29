"""SummaryAgent smoke test.

Runs in two configs:
  - template-only (no LLM) — always
  - with mock LLM impression — always (deterministic)

Run:
    .venv/Scripts/python.exe agents/summary_agent/tests/test_smoke.py
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from agents.summary_agent import SummaryAgent, PatientSnapshot  # noqa: E402
from agents.shared.llm import MockClient  # noqa: E402
from agents.shared.logging import get_logger  # noqa: E402

logger = get_logger("summary_smoke")


PATIENT = PatientSnapshot(
    name=None,
    approx_age="35-45",
    sex="M",
    language_name="Portuguese (Brazil)",
    language_code="pt",
    symptoms=["chest pain", "dizziness", "sweating"],
    pain_location="chest",
    pain_scale=8,
    allergies=["penicillin"],
    medications=["Losartan 50mg"],
    chronic_conditions=["hypertension"],
    wearable_snapshot={"hr": 142, "rhythm": "irregular"},
)


def test_template_only() -> None:
    print("\n" + "=" * 70)
    print("template-only (no LLM)")
    print("=" * 70)
    agent = SummaryAgent(llm=None)
    report = agent.build_handoff(
        case_id="case-2026-05-27-001",
        patient=PATIENT,
        location="Stadium A / Sector 12 / Gate C7",
        nearest_aed="Sector 12 wall, 8m, indoor",
        ambulance_eta_min=4,
        drug_warnings=[],
        handed_off_by="@volunteer_sara",
        accepted_by="Dr. Emre",
        with_impression=True,  # ignored — no LLM
    )
    text = agent.render_text(report)
    print(text)
    assert "PATIENT HANDOFF" in text
    assert "Portuguese" in text
    assert "8/10" in text
    assert report.clinical_impression is None
    print("\n[OK] template-only passed.")


def test_with_mock_impression() -> None:
    print("\n" + "=" * 70)
    print("with mock LLM clinical impression")
    print("=" * 70)
    mock = MockClient(
        {
            "Patient data": (
                "Findings consistent with possible acute coronary syndrome; "
                "irregular tachycardia with chest pain in a hypertensive patient."
            )
        }
    )
    agent = SummaryAgent(llm=mock)
    report = agent.build_handoff(
        case_id="case-2026-05-27-001",
        patient=PATIENT,
        location="Stadium A / Sector 12 / Gate C7",
        nearest_aed="Sector 12 wall, 8m, indoor",
        ambulance_eta_min=4,
        handed_off_by="@volunteer_sara",
        accepted_by="Dr. Emre",
    )
    text = agent.render_text(report)
    print(text)
    assert report.clinical_impression is not None
    assert "AI IMPRESSION" in text
    print("\n[OK] mock-impression passed.")


if __name__ == "__main__":
    test_template_only()
    test_with_mock_impression()
    print("\nAll requested tests finished.\n")
