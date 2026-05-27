"""RTSLookupAgent smoke test.

By default this runs LIVE against OpenStreetMap Overpass + NIH RxNav — both
free, no API key needed. To force offline (no network) mode:

    RTS_OFFLINE=1 python agents/rts_lookup_agent/tests/test_smoke.py

Usage from project root:
    .venv/Scripts/python.exe agents/rts_lookup_agent/tests/test_smoke.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from agents.rts_lookup_agent import (  # noqa: E402
    RTSLookupAgent,
    RTSLookupRequest,
)
from agents.rts_lookup_agent.models import GeoPoint  # noqa: E402
from agents.shared.env import load  # noqa: E402
from agents.shared.logging import get_logger  # noqa: E402

logger = get_logger("rts_smoke")
load()

# Central London (Trafalgar Square area) — dense AED coverage on OSM.
# Easy to verify by browsing https://openstreetmap.org/?lat=51.508&lon=-0.128
DEMO_LOCATION = GeoPoint(lat=51.5074, lon=-0.1278)


SCENARIO = RTSLookupRequest(
    case_id="case-2026-05-27-001",
    location=DEMO_LOCATION,
    medications=["Losartan 50mg", "Aspirin"],
    proposed_treatments=["Nitroglycerin"],
    aed_radius_m=300,
)


def main() -> int:
    offline = os.getenv("RTS_OFFLINE") == "1"
    print("=" * 70)
    print(f"RTSLookupAgent smoke test — {'OFFLINE' if offline else 'LIVE'} mode")
    print("=" * 70)
    print(
        f"case      : {SCENARIO.case_id}\n"
        f"location  : ({SCENARIO.location.lat}, {SCENARIO.location.lon}) "
        f"(central London)\n"
        f"meds      : {SCENARIO.medications}\n"
        f"treatments: {SCENARIO.proposed_treatments}\n"
        f"radius    : {SCENARIO.aed_radius_m}m"
    )

    if offline:
        # Light contract check without hitting the network.
        from agents.rts_lookup_agent import ambulance as ambulance_mod

        eta = ambulance_mod.get_eta(SCENARIO.location, case_id=SCENARIO.case_id)
        print(f"\n[ambulance-only] eta={eta.eta_minutes} min (unit={eta.unit_id})")
        assert 1 <= eta.eta_minutes <= 60
        print("\n[OK] offline smoke (ambulance mock only).")
        return 0

    agent = RTSLookupAgent()
    result = agent.lookup(SCENARIO)

    print("\n--- AEDs ---")
    print(f"  count: {len(result.aeds)}")
    for aed in result.aeds[:5]:
        print(
            f"  - {aed.distance_m:6.1f}m  "
            f"({aed.lat:.5f}, {aed.lon:.5f})  "
            f"name={aed.name or '-'!r}  indoor={aed.indoor}"
        )
    if len(result.aeds) > 5:
        print(f"  … and {len(result.aeds) - 5} more")

    print("\n--- drug interactions ---")
    print(f"  count: {len(result.drug_interactions)}")
    for di in result.drug_interactions[:5]:
        print(
            f"  - {di.severity:>8}  {di.drug_a} <> {di.drug_b}\n"
            f"            {di.description[:140]}"
        )
    if len(result.drug_interactions) > 5:
        print(f"  … and {len(result.drug_interactions) - 5} more")

    print("\n--- ambulance ---")
    if result.ambulance:
        print(
            f"  eta={result.ambulance.eta_minutes} min  "
            f"unit={result.ambulance.unit_id}  "
            f"confidence={result.ambulance.confidence}  "
            f"source={result.ambulance.source}"
        )

    print(f"\n--- warnings ({len(result.warnings)}) ---")
    for w in result.warnings:
        print(f"  - {w}")

    print("\n[OK] live smoke test completed.")

    # Save a small artifact for the journal.
    out = PROJECT_ROOT / "agents" / "rts_lookup_agent" / "tests" / "_last_result.json"
    out.write_text(
        json.dumps(result.model_dump(), default=str, indent=2),
        encoding="utf-8",
    )
    print(f"     result written to {out.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
