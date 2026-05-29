# 2026-05-27 — SummaryAgent + end-to-end demo runner

## Goal

1. Build the fourth coded agent, **SummaryAgent** (Stage 3 Handoff).
2. Build a **demo_runner** that chains all four coded agents end-to-end,
   proving the whole pipeline before UiPath Maestro wiring.

## Tool: Claude Code (Anthropic)

Fourth + fifth deliverable of this scaffold session. Same bonus-point
posture: documented, integrated, verifiable via a runnable script.

## What was produced

| Path | Purpose |
|---|---|
| `agents/summary_agent/models.py` | `PatientSnapshot`, `HandoffReport` |
| `agents/summary_agent/prompts.py` | One narrow LLM prompt (clinical impression) |
| `agents/summary_agent/agent.py` | Template-driven handoff + render + optional LLM impression |
| `agents/summary_agent/tests/test_smoke.py` | template-only + mock-impression tests |
| `agents/demo_runner.py` | Chains Language -> RTS -> Summary -> Compliance |

## Key design decisions

1. **Handoff is template-driven, NOT LLM-generated.** In a medical
   context, hallucinating allergies or dosages is unacceptable. Every
   critical field is rendered deterministically from structured data.
   The LLM writes ONLY a clearly-labelled "AI IMPRESSION (not a
   diagnosis)" one-liner.
2. **demo_runner doubles ComplianceAgent as the audit sink** — every
   stage transition logs through it, exactly as it will in Maestro.
3. **Graceful mode switching** — the runner uses MockClient for LLM calls
   unless `ANTHROPIC_API_KEY` is set, and runs RTS live unless
   `RTS_OFFLINE=1`. Zero-secret runnable for anyone who clones the repo.

## End-to-end result (MOCK LLM + LIVE RTS)

```
Pipeline complete in 4.8s (target: <90s real-world)

Stage 1: Portuguese (pt) @0.92, 5 triage Qs, parsed reply
Stage 2: 2 AEDs found via real OSM Overpass, ambulance ETA 6 min,
         3 RxCUIs resolved
Stage 3: full PATIENT HANDOFF block + AI impression
Stage 4: anonymized record d20937ff1a6af903, learning loop found
         1 similar prior case, 6 audit events recorded
```

The handoff output matches the format envisioned in the original
`medipass-agent.md`, extended with AED location, ambulance ETA, wearable
snapshot, and the labelled AI impression.

## What this de-risks

The whole agent pipeline works as a unit. The remaining integration is
"lift these four agents into UiPath Coded Agents + wire the Maestro Case
stages to call them" — the logic is proven, only the orchestration host
changes.

## Open follow-ups

- TriageAgent + RoutingAgent (low-code) in UiPath Agent Builder — user task
- Patient mini web app (Next.js) calling LanguageAgent over HTTP
- Wire all four coded agents as UiPath Coded Agents inside Maestro stages
- Add LLM-based drug interaction (the RxNav gap from session 2)

## Commit reference

[`61a50bb`](https://github.com/dento34/medicase-orchestrator/commit/61a50bb)

## Verification

```bash
.venv/Scripts/python.exe agents/demo_runner.py
```
