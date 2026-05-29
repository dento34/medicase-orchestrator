# 2026-05-29 — Maestro canvas build + coded-agent publish to UiPath

## Goal

Move from local scaffolding to a live UiPath integration:
1. Build the Maestro Agentic Process (4-stage emergency case flow) on the
   Studio Web canvas.
2. Create the two low-code agents (TriageAgent, RoutingAgent) in Agent Builder.
3. Package the four coded agents and publish them to the UiPath tenant so they
   are bindable from Maestro.

## Tool: Claude Code (Anthropic)

Claude Code drove the whole session: it guided the canvas build step-by-step
(screenshot-by-screenshot) and then autonomously built + published the coded
agents from the terminal.

## What was produced

### Maestro canvas (UiPath Studio Web)
- Agentic Process `Process.bpmn` with the full flow:
  `Start → LanguageAgent → TriageAgent → RTSLookupAgent → RoutingAgent →
   SummaryAgent → ComplianceAgent → End`
- **TriageAgent** (Autonomous, low-code): system prompt = conservative triage
  classifier; inputs `symptoms`(req), `pain_scale`, `age_band`, `conditions`;
  outputs `severity`, `symptom_cluster`, `red_flags`; bound to its node.
- **RoutingAgent** (Autonomous, low-code): maps symptom_cluster → `#medic-*`
  channel and severity → P1–P4 priority; inputs `severity`, `symptom_cluster`,
  `red_flags`, `location`; outputs `target_channel`, `priority`,
  `assigned_specialist`, `rationale`; bound to its node.

### Coded-agent package (`uipath-coded/`)
A single UiPath coded-agent package exposing four typed entrypoints:

| Entrypoint | File | Stage |
|---|---|---|
| LanguageAgent | `main_language.py:main` | 1 Intake |
| RTSLookupAgent | `main_rts.py:main` | 2 Stabilization |
| SummaryAgent | `main.py:main` | 3 Handoff |
| ComplianceAgent | `main_compliance.py:main` | 4 Post-incident |

Each entrypoint wraps the existing `agents/uipath/*_entry.py:run` with typed
Pydantic Input/Output models so `uipath init` generates a clean I/O schema for
Maestro field mapping. `build.py` keeps the bundled `agents/` copy DRY.

## Verified facts about the hackathon tenant

- **PAT auth works for the UiPath CLI** by mapping `UIPATH_URL`=`UIPATH_TENANT_URL`
  and `UIPATH_ACCESS_TOKEN`=`UIPATH_PAT` (no interactive browser login needed).
- `uipath list-models` shows the tenant has **anthropic.claude-opus-4-7,
  claude-sonnet-4-5, claude-haiku-4-5** and the **gpt-5 / gpt-4.1 / gpt-4o**
  families available via the LLM Gateway.
- **Autopilot agent generation is license-gated** ("No license detected") — the
  low-code agents were therefore configured manually (better control anyway).
- **Personal workspace is limited to 1 published process** (license). The
  4-entrypoint package was published to the **tenant package feed** instead.

## Publish result

```
uipath pack    -> .uipath/medicase-coded-agents.0.2.0.nupkg
uipath publish --tenant
   -> RC 0  "Package published successfully!"
```

(An earlier single-entrypoint proof, `medicase-coded-summary.0.1.0`, was
published to the personal workspace — Orchestrator process id 2151660 — which
validated the end-to-end pack/publish path before consolidating into the
4-entrypoint package.)

## What remains (canvas, human)

- Bind each of the four coded-agent Maestro nodes to the matching entrypoint of
  the published `medicase-coded-agents` package (Select an agent → published
  package → entrypoint).
- Map node inputs/outputs between stages (e.g. TriageAgent.outputs →
  RoutingAgent.inputs).
- Live end-to-end execution is subject to the tenant's AI-unit/license limits.

## Commit reference

This session's canvas + coded-agent work; see the commit that adds
`uipath-coded/` and this log.
