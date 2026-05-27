# 2026-05-27 — RTSLookupAgent first scaffold

## Goal

Build the second Coded Agent for MediCase: **RTSLookupAgent** for Stage 2
(Stabilization). Three parallel real-time lookups:

1. Nearest AED (defibrillator) via OpenStreetMap Overpass API
2. Drug-interaction warnings via NIH RxNav
3. Ambulance ETA (mock during hackathon, event-ops API in production)

Coordinator runs all three concurrently and surfaces soft failures as
warnings without blocking the case.

## Tool: Claude Code (Anthropic)

Same session as LanguageAgent scaffold; this is the second agent in a
batch. Bonus-point criteria notes (a) Claude Code used, (b) it produced
the orchestration + lookup modules + tests, (c) the smoke test ran live
against real public APIs.

## What was produced

| Path | Purpose |
|---|---|
| `agents/rts_lookup_agent/__init__.py` | Package marker, exports |
| `agents/rts_lookup_agent/models.py` | 5 Pydantic models (GeoPoint, AedLocation, DrugInteraction, AmbulanceEta, request/result) |
| `agents/rts_lookup_agent/aed.py` | OSM Overpass query + haversine distance + multi-instance fallback |
| `agents/rts_lookup_agent/drug.py` | RxNav RxCUI resolution + per-drug pairwise interaction |
| `agents/rts_lookup_agent/ambulance.py` | Deterministic mock ETA seeded by case_id |
| `agents/rts_lookup_agent/agent.py` | `ThreadPoolExecutor` coordinator with soft failure capture |
| `agents/rts_lookup_agent/tests/test_smoke.py` | LIVE smoke test (Central London, 3 drugs) |

## Key design decisions

1. **Parallel fan-out with safe wrapper.** `_safe(fn, label, warnings)`
   captures exceptions per branch so one upstream failure doesn't crash
   the case stage.
2. **Multi-instance Overpass fallback.** Primary `overpass-api.de`,
   fallbacks to `overpass.kumi.systems` and `overpass.openstreetmap.fr`.
   Used because the public Overpass instance occasionally returns 504.
3. **No `requests` dependency** — used stdlib `urllib` to keep the deps
   list minimal.
4. **Browser-style User-Agent header** on Overpass requests because
   their abuse rules prefer identified clients.
5. **Drug name normalization** — strip dosage like "50mg" before sending
   to RxNav RxCUI lookup, dramatically improves match rate.

## Smoke test result (LIVE mode, central London)

```
--- AEDs ---
  count: 2
  - 222.9m (51.50819, -0.12484) indoor=True
  - 234.7m (51.50772, -0.12445) indoor=True

--- drug interactions ---
  count: 0
  (RxCUI resolution succeeded: Aspirin→1191, Nitroglycerin→4917,
   Losartan→52175. RxNav /interaction endpoint returns 404 — see below.)

--- ambulance ---
  eta=9 min  unit=AMB-051  confidence=0.91  source=mock
```

## Known issue: RxNav interaction API discontinued

NIH retired the `/interaction/list.json` endpoint in **January 2024** and
appears to have also taken down `/interaction/interaction.json?rxcui=`
(returns 404 on every drug we tried during this session).

The free RxCUI resolution endpoints (`/rxcui.json`, `/REST/...`) are still
served and we use them. RxCUI normalization remains valuable — it lets us
look up drugs in alternative interaction databases.

**Follow-up planned**: add an LLM-based drug-interaction warning module
that asks Claude *"are there clinically significant interactions between
{drugs} for a patient with {conditions}?"* and returns structured findings.
This becomes another use of the same `LLMClient` abstraction already
built for LanguageAgent. Filed for the next session.

## Commit reference

[`<pending>`](https://github.com/dento34/medicase-orchestrator/) — to be linked.

## Verification

```bash
.venv/Scripts/python.exe agents/rts_lookup_agent/tests/test_smoke.py
```

Force offline mode (no network):

```bash
RTS_OFFLINE=1 .venv/Scripts/python.exe agents/rts_lookup_agent/tests/test_smoke.py
```
