# 2026-05-27 — UiPath entry-points + audit hook

## Goal

Prepare every part that doesn't require the UiPath canvas:
1. LLM-based drug interaction (closes the retired-RxNav gap)
2. Audit hook so agents auto-log to the compliance sink
3. UiPath Coded Agent entry-points wrapping all 4 coded agents

## Tool: Claude Code (Anthropic)

All scaffolded in this session.

## What was produced

| Path | Purpose |
|---|---|
| `agents/rts_lookup_agent/drug_llm.py` | Conservative LLM drug-interaction analysis |
| `agents/shared/audit.py` | `audited()` context manager + AuditSink protocol |
| `agents/shared/tests/test_audit.py` | invoked/completed/exception + no-op sink |
| `agents/uipath/language_entry.py` | Stage 1 entry: detect / translate / parse |
| `agents/uipath/rts_entry.py` | Stage 2 entry: parallel lookup |
| `agents/uipath/summary_entry.py` | Stage 3 entry: build handoff |
| `agents/uipath/compliance_entry.py` | Stage 4 entry: log / close / similar / trail |
| `agents/uipath/agent_manifest.json` | Stage→entry mapping for all 6 agents |
| `agents/uipath/tests/test_entries.py` | JSON-in/out smoke test for all 4 entries |

## Key design decisions

1. **Entry-points are `run(input: dict) -> dict`.** This is the stable
   contract a UiPath Coded Agent / API Workflow calls. The SDK binding
   (decorators, manifest registration) wraps these without changing them,
   so Maestro integration is additive, not a rewrite.
2. **Op-based dispatch** for multi-method agents (language, compliance) —
   one coded agent per stage, `op` selects the operation.
3. **`make_client(prefer_real=True)`** inside entries — uses the real LLM
   when `ANTHROPIC_API_KEY` is present, falls back to mock otherwise, so
   the contract is testable without secrets.
4. **Audit hook is sink-agnostic** (Protocol) and **None-safe**, so agents
   stay runnable standalone.

## Smoke test result

```
language_entry  detect (locale fallback) -> pt
summary_entry   build (template)         -> PATIENT HANDOFF rendered
compliance_entry log->close->similar->trail -> hash, 1 similar, 2 events
rts_entry       lookup (live OSM)        -> 2 AEDs, ambulance yes
All entry-point smoke tests passed.
```

(Drug interaction in the rts entry degrades gracefully to 0 when no LLM key
is set — by design; with a key it returns the LLM analysis.)

## What's now ready for the UiPath canvas

The coded side is complete and contract-stable. Remaining UiPath-canvas work
(needs the human + Studio Web):
- Build TriageAgent + RoutingAgent in Agent Builder (low-code)
- Create the Maestro Case with 4 stages
- Wire each stage to call the matching `agents/uipath/*_entry.py:run`
- Register coded agents via UiPath CLI / Python SDK

## Commit reference

[`8af27c8`](https://github.com/dento34/medicase-orchestrator/commit/8af27c8)
(audit hook shipped in [`1bffe5a`](https://github.com/dento34/medicase-orchestrator/commit/1bffe5a),
LLM drug interaction in [`ec2c28f`](https://github.com/dento34/medicase-orchestrator/commit/ec2c28f),
patient app in [`761cb7d`](https://github.com/dento34/medicase-orchestrator/commit/761cb7d))
