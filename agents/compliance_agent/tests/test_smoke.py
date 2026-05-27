"""ComplianceAgent smoke test.

Exercises the full Stage 4 lifecycle:
  1. Open a case (audit event)
  2. Log agent invocations + a human decision
  3. Close the case (writes an anonymized record)
  4. Query for similar prior cases (the learning loop demo moment)

Uses a throwaway temp SQLite file so this doesn't pollute the real DB.

Run:
    .venv/Scripts/python.exe agents/compliance_agent/tests/test_smoke.py
"""
from __future__ import annotations

import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from agents.compliance_agent import ComplianceAgent  # noqa: E402
from agents.shared.logging import get_logger  # noqa: E402

logger = get_logger("compliance_smoke")


def main() -> int:
    print("=" * 70)
    print("ComplianceAgent smoke test — temp SQLite")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "medicase-test.db"
        agent = ComplianceAgent(db_path=str(db_path))

        # ---- seed two earlier cases so 'similar' has something to find ----
        for i, (cluster, lang, age, outcome) in enumerate(
            [
                ("cardiac", "pt", 47, "transported"),
                ("cardiac", "pt", 52, "resolved_on_site"),
                ("trauma", "en", 24, "transported"),
            ]
        ):
            opened = datetime.now(timezone.utc) - timedelta(days=i + 1)
            agent.close_case(
                case_id=f"prior-{i}",
                opened_at=opened,
                language_code=lang,
                age=age,
                sex="m",
                symptom_cluster=cluster,
                severity="urgent",
                interventions=["aspirin", "nitro"]
                if cluster == "cardiac"
                else ["splint"],
                outcome=outcome,
                event_venue_type="stadium",
            )

        # ---- the real case being demoed ----
        case_id = "case-2026-05-27-001"
        opened_at = datetime.now(timezone.utc) - timedelta(seconds=85)

        agent.log_event(
            case_id=case_id, kind="case_opened",
            actor="volunteer:@sara", summary="Volunteer reported collapsed fan, sector 12.",
        )
        agent.log_event(
            case_id=case_id, kind="agent_invoked",
            actor="language_agent", summary="Detected Portuguese (pt) confidence=0.92",
            payload={"language_code": "pt", "confidence": 0.92},
        )
        agent.log_event(
            case_id=case_id, kind="external_api_called",
            actor="rts_lookup_agent", summary="Overpass returned 2 AEDs within 300m.",
            payload={"aed_count": 2, "ambulance_eta_min": 9},
        )
        agent.log_event(
            case_id=case_id, kind="human_decision",
            actor="medic:@dr_emre", summary="Accepted case; administering nitroglycerin.",
        )
        agent.log_event(
            case_id=case_id, kind="stage_transition",
            actor="maestro", summary="Stabilization -> Handoff",
        )

        # Close + anonymize the demo case
        record = agent.close_case(
            case_id=case_id,
            opened_at=opened_at,
            language_code="pt-BR",
            age=42,
            sex="M",
            symptom_cluster="cardiac",
            severity="urgent",
            interventions=["nitroglycerin"],
            outcome="transported",
            event_venue_type="stadium",
        )

        # Audit trail readback
        trail = agent.case_audit_trail(case_id)
        print(f"\n--- audit trail for {case_id} ({len(trail)} events) ---")
        for ev in trail:
            print(f"  {ev.timestamp.isoformat()[:19]}  [{ev.kind:<22}] {ev.actor:<22} {ev.summary}")

        # Anonymized record
        print(f"\n--- anonymized record ---")
        print(f"  case_id_hash    : {record.case_id_hash}")
        print(f"  language_family : {record.language_family}")
        print(f"  age_band        : {record.age_band}")
        print(f"  symptom_cluster : {record.symptom_cluster}")
        print(f"  outcome         : {record.outcome}")
        print(f"  duration_s      : {record.duration_seconds}")

        # Learning loop: query similar prior cases
        priors = agent.similar_prior_cases(
            symptom_cluster="cardiac", language_code="pt", limit=5
        )
        print(f"\n--- learning loop: similar prior cases ---")
        print(f"  found {len(priors)} prior cardiac/Portuguese cases")
        for p in priors:
            print(
                f"  - {p.case_id_hash}  age={p.age_band}  "
                f"outcome={p.outcome}  duration={p.duration_seconds}s"
            )

        # Assertions
        assert len(trail) == 6, f"expected 6 audit events, got {len(trail)}"
        assert record.case_id_hash != case_id, "case_id_hash must NOT equal raw case_id"
        assert record.language_family == "indo-european"
        assert record.age_band == "30-44"
        assert any(p.case_id_hash != record.case_id_hash for p in priors), (
            "expected to find earlier seeded prior cases"
        )

    print("\n[OK] ComplianceAgent smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
