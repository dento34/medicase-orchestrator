"""Smoke test for UiPath Coded Agent entry-points.

Exercises the JSON-in/JSON-out contract for ops that don't require an LLM
key, so this runs green in CI without secrets:
  - compliance: log -> close -> similar -> trail
  - summary: build with_impression=False (template only)
  - rts: lookup (live OSM; drug analysis degrades gracefully without a key)
  - language: detect via browser_locale fallback (no LLM call)

Run:
    .venv/Scripts/python.exe agents/uipath/tests/test_entries.py
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from agents.uipath import (  # noqa: E402
    compliance_entry,
    language_entry,
    rts_entry,
    summary_entry,
)
from agents.shared.logging import get_logger  # noqa: E402

logger = get_logger("uipath_entries_test")


def test_language_locale_fallback() -> None:
    print("\n--- language_entry: detect (locale fallback, no LLM) ---")
    out = language_entry.run(
        {"op": "detect", "case_id": "c1", "browser_locale": "pt-BR"}
    )
    print(f"  -> {out}")
    assert out["language_code"] == "pt"


def test_summary_template_only() -> None:
    print("\n--- summary_entry: build (template only) ---")
    out = summary_entry.run(
        {
            "case_id": "c1",
            "with_impression": False,
            "patient": {
                "approx_age": "35-45",
                "language_name": "Portuguese",
                "symptoms": ["chest pain"],
                "pain_scale": 8,
                "allergies": ["penicillin"],
            },
            "location": "Sector 12",
            "ambulance_eta_min": 4,
            "handed_off_by": "@sara",
        }
    )
    assert "PATIENT HANDOFF" in out["rendered_text"]
    assert out["report"]["patient"]["pain_scale"] == 8
    print("  -> rendered_text OK, report dict OK")


def test_compliance_lifecycle() -> None:
    print("\n--- compliance_entry: log -> close -> similar -> trail ---")
    import tempfile, os

    with tempfile.TemporaryDirectory() as tmp:
        os.environ["DATABASE_URL"] = f"sqlite:///{Path(tmp) / 'e.db'}"
        cid = "case-entry-001"
        log = compliance_entry.run(
            {
                "op": "log", "case_id": cid, "kind": "case_opened",
                "actor": "volunteer:@sara", "summary": "Collapsed fan.",
            }
        )
        assert log["kind"] == "case_opened"
        closed = compliance_entry.run(
            {
                "op": "close", "case_id": cid,
                "opened_at": datetime.now(timezone.utc).isoformat(),
                "language_code": "pt", "age": 42, "sex": "M",
                "symptom_cluster": "cardiac", "severity": "urgent",
                "interventions": ["nitro"], "outcome": "transported",
                "event_venue_type": "stadium",
            }
        )
        assert closed["case_id_hash"] != cid
        similar = compliance_entry.run(
            {"op": "similar", "symptom_cluster": "cardiac", "language_code": "pt"}
        )
        trail = compliance_entry.run({"op": "trail", "case_id": cid})
        print(
            f"  -> closed hash={closed['case_id_hash']}, "
            f"similar={len(similar['cases'])}, trail={len(trail['events'])}"
        )
        assert len(trail["events"]) >= 2
        os.environ.pop("DATABASE_URL", None)


def test_rts_lookup() -> None:
    print("\n--- rts_entry: lookup (live OSM) ---")
    out = rts_entry.run(
        {
            "case_id": "c1",
            "lat": 51.5074,
            "lon": -0.1278,
            "medications": ["Losartan 50mg"],
            "proposed_treatments": ["Nitroglycerin"],
            "patient_conditions": ["hypertension"],
            "aed_radius_m": 300,
        }
    )
    print(
        f"  -> aeds={len(out['aeds'])}, "
        f"ambulance={'yes' if out['ambulance'] else 'no'}, "
        f"warnings={len(out['warnings'])}"
    )
    assert "aeds" in out and "ambulance" in out


if __name__ == "__main__":
    print("=" * 70)
    print("UiPath entry-point smoke test")
    print("=" * 70)
    test_language_locale_fallback()
    test_summary_template_only()
    test_compliance_lifecycle()
    test_rts_lookup()
    print("\n[OK] all entry-point smoke tests passed.\n")
