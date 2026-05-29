"""End-to-end demo runner — chains all coded agents for the FIFA scenario.

This is the single-command proof that the whole MediCase pipeline works
before it's wired into UiPath Maestro. It runs the four coded agents in
sequence, mirroring the four case stages:

  Stage 1 (Intake)        -> LanguageAgent
  Stage 2 (Stabilization) -> RTSLookupAgent
  Stage 3 (Handoff)       -> SummaryAgent
  Stage 4 (Post-incident) -> ComplianceAgent

Modes:
  - default: LanguageAgent/SummaryAgent use MockClient unless ANTHROPIC_API_KEY
    is set; RTSLookupAgent runs LIVE unless RTS_OFFLINE=1
  - this keeps the demo runnable with zero secrets, while upgrading to real
    APIs the moment keys/network are available.

Run:
    .venv/Scripts/python.exe agents/demo_runner.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from agents.compliance_agent import ComplianceAgent  # noqa: E402
from agents.language_agent import LanguageAgent, TriageRequest  # noqa: E402
from agents.rts_lookup_agent import RTSLookupAgent, RTSLookupRequest  # noqa: E402
from agents.rts_lookup_agent.models import GeoPoint  # noqa: E402
from agents.summary_agent import SummaryAgent, PatientSnapshot  # noqa: E402
from agents.shared.env import load  # noqa: E402
from agents.shared.llm import MockClient  # noqa: E402
from agents.shared.logging import get_logger  # noqa: E402

logger = get_logger("demo")
load()


# --- Mock fixtures so the demo runs offline without an API key -------------
LANG_FIXTURES = {
    "Speech snippet": json.dumps(
        {
            "language_code": "pt",
            "language_name": "Portuguese",
            "confidence": 0.92,
            "rationale": "Phrases are clearly Brazilian Portuguese.",
        }
    ),
    "Translate these questions": json.dumps(
        {
            "questions": [
                "Onde está doendo?",
                "Numa escala de 0 a 10, qual é a intensidade da dor?",
                "Você tem alguma alergia?",
                "Está tomando algum remédio agora?",
                "Tem alguma condição crônica?",
            ]
        }
    ),
    "Patient said": json.dumps(
        {
            "symptoms": ["chest pain", "dizziness", "sweating"],
            "allergies": ["penicillin"],
            "medications": ["Losartan 50mg"],
            "chronic_conditions": ["hypertension"],
            "pain_location": "chest",
            "pain_scale": 8,
            "english_translation": (
                "My chest hurts a lot, pain is 8. Allergic to penicillin. "
                "I take Losartan."
            ),
        }
    ),
}
SUMMARY_FIXTURE = {
    "Patient data": (
        "Findings consistent with possible acute coronary syndrome; "
        "irregular tachycardia with chest pain in a hypertensive patient."
    )
}


def banner(stage: str, title: str) -> None:
    print("\n" + "=" * 72)
    print(f"  {stage}  |  {title}")
    print("=" * 72)


def main() -> int:
    case_id = "demo-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    opened_at = datetime.now(timezone.utc)
    t0 = time.time()

    use_real_llm = bool(os.getenv("ANTHROPIC_API_KEY"))
    lang_llm = None if use_real_llm else MockClient(LANG_FIXTURES)
    sum_llm = None if use_real_llm else MockClient(SUMMARY_FIXTURE)

    print("\n" + "#" * 72)
    print("#  MediCase Orchestrator — end-to-end demo (Brazilian fan, chest pain)")
    print(f"#  case_id = {case_id}")
    print(f"#  LLM mode = {'REAL (Anthropic)' if use_real_llm else 'MOCK'}")
    print("#" * 72)

    # Stage 4 agent doubles as our audit sink throughout.
    with tempfile.TemporaryDirectory() as tmp:
        compliance = ComplianceAgent(db_path=str(Path(tmp) / "demo.db"))
        compliance.log_event(
            case_id=case_id, kind="case_opened", actor="volunteer:@sara",
            summary="Collapsed fan, Stadium A Sector 12. No shared language.",
        )

        # ---------------- Stage 1: Intake -----------------------------------
        banner("STAGE 1", "Intake — LanguageAgent")
        language = LanguageAgent(llm=lang_llm) if lang_llm else LanguageAgent()
        req = TriageRequest(
            case_id=case_id,
            patient_utterance="Minha cabeça está doendo muito, meu peito também.",
            browser_locale="pt-BR",
        )
        lang = language.detect(req)
        print(f"  detected: {lang.language_name} ({lang.language_code}) @ {lang.confidence}")
        compliance.log_event(
            case_id=case_id, kind="agent_invoked", actor="language_agent",
            summary=f"Detected {lang.language_name} ({lang.confidence})",
            payload={"language_code": lang.language_code},
        )
        triage = language.generate_triage_questions(lang)
        print(f"  triage questions ({len(triage.questions)}):")
        for q in triage.questions:
            print(f"    - {q}")
        reply = (
            "Meu peito dói muito, é um 8. Tenho alergia a penicilina. Tomo Losartan. "
            "Tenho pressão alta."
        )
        parsed = language.parse_patient_response(reply, lang)
        print(f"  parsed english: {parsed.english_translation}")
        s = parsed.structured

        # ---------------- Stage 2: Stabilization ----------------------------
        banner("STAGE 2", "Stabilization — RTSLookupAgent")
        rts = RTSLookupAgent()
        rts_req = RTSLookupRequest(
            case_id=case_id,
            location=GeoPoint(lat=51.5074, lon=-0.1278),  # demo coord
            medications=s.get("medications", []),
            proposed_treatments=["Nitroglycerin", "Aspirin"],
            aed_radius_m=300,
        )
        rts_result = rts.lookup(rts_req)
        nearest_aed = None
        if rts_result.aeds:
            a = rts_result.aeds[0]
            nearest_aed = f"{a.distance_m:.0f}m away ({a.lat:.5f},{a.lon:.5f})"
        print(f"  nearest AED   : {nearest_aed or 'none found'}")
        print(f"  drug warnings : {len(rts_result.drug_interactions)}")
        eta = rts_result.ambulance.eta_minutes if rts_result.ambulance else None
        print(f"  ambulance ETA : {eta} min")
        compliance.log_event(
            case_id=case_id, kind="external_api_called", actor="rts_lookup_agent",
            summary=f"{len(rts_result.aeds)} AEDs, ETA {eta} min",
            payload={"aeds": len(rts_result.aeds), "eta_min": eta},
        )
        compliance.log_event(
            case_id=case_id, kind="human_decision", actor="medic:@dr_emre",
            summary="Accepted case; preparing nitroglycerin.",
        )
        compliance.log_event(
            case_id=case_id, kind="stage_transition", actor="maestro",
            summary="Stabilization -> Handoff",
        )

        # ---------------- Stage 3: Handoff ----------------------------------
        banner("STAGE 3", "Handoff — SummaryAgent")
        summary = SummaryAgent(llm=sum_llm) if sum_llm else SummaryAgent()
        patient = PatientSnapshot(
            approx_age="35-45",
            sex="M",
            language_name=lang.language_name,
            language_code=lang.language_code,
            symptoms=s.get("symptoms", []),
            pain_location=s.get("pain_location"),
            pain_scale=s.get("pain_scale"),
            allergies=s.get("allergies", []),
            medications=s.get("medications", []),
            chronic_conditions=s.get("chronic_conditions", []),
            wearable_snapshot={"hr": 142, "rhythm": "irregular"},
        )
        report = summary.build_handoff(
            case_id=case_id,
            patient=patient,
            location="Stadium A / Sector 12 / Gate C7",
            nearest_aed=nearest_aed,
            ambulance_eta_min=eta,
            drug_warnings=[
                f"{d.severity}: {d.drug_a}<>{d.drug_b}"
                for d in rts_result.drug_interactions
            ],
            handed_off_by="@volunteer_sara",
            accepted_by="Dr. Emre",
        )
        print()
        print(summary.render_text(report))

        # ---------------- Stage 4: Post-incident ----------------------------
        banner("STAGE 4", "Post-incident — ComplianceAgent")
        record = compliance.close_case(
            case_id=case_id,
            opened_at=opened_at,
            language_code=lang.language_code,
            age=42,
            sex="M",
            symptom_cluster="cardiac",
            severity="urgent",
            interventions=["nitroglycerin"],
            outcome="transported",
            event_venue_type="stadium",
        )
        print(f"  anonymized record : {record.case_id_hash}")
        print(f"  language family   : {record.language_family}")
        print(f"  duration          : {record.duration_seconds}s")

        # Learning loop demo
        priors = compliance.similar_prior_cases(
            symptom_cluster="cardiac", language_code=lang.language_code
        )
        print(f"  learning loop     : {len(priors)} similar prior case(s)")

        trail = compliance.case_audit_trail(case_id)
        print(f"  audit events      : {len(trail)}")

    elapsed = time.time() - t0
    print("\n" + "#" * 72)
    print(f"#  Pipeline complete in {elapsed:.1f}s (target: <90s real-world)")
    print("#" * 72 + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
