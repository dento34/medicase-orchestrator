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

## Tenant constraint discovered → dispatcher pattern

While binding the coded agents in the canvas we found two hard limits of the
hackathon **staging** tenant:

1. The Maestro agent picker only lists **personal-workspace processes** (not
   the tenant package feed), and the workspace is capped at **1 process**.
2. Binding a multi-entrypoint package always uses its **first entrypoint** —
   there is no per-node entrypoint selector, and no "Shared" folder exists to
   deploy multiple processes into.

So a single multi-entrypoint package could not expose 4 distinct bindable
agents. The fix: `main.py` was turned into a **dispatcher** (entrypoint
`MediCaseCodedAgent`) that routes on an `agent` input
(`language|rts|summary|compliance`) to the matching `agents/uipath/*_entry.py`.
All four Maestro coded nodes bind to this one published process and set
`agent` per stage with a `payload` matching that agent's contract. Published
as `medicase-coded-summary` v0.4.0 (workspace process 2151660). The typed
per-agent entrypoints (`main_language.py`, `main_rts.py`, `main_summary.py`,
`main_compliance.py`) stay in the repo as the documented I/O contracts.

## End-to-end execution verification

Verified the coded agent across every layer we could:

| Layer | Test | Result |
|---|---|---|
| Agent logic (pure Python) | local smoke tests | PASS |
| **UiPath runtime contract** | `uipath run MediCaseCodedAgent <input>` | **PASS** — produced the real PATIENT HANDOFF, `agent=summary`, `case_id=demo-verify` |
| Publish | `uipath publish --my-workspace` | PASS (process 2151660) |
| Remote job creation | `uipath invoke MediCaseCodedAgent` | PASS — a real Orchestrator job starts |
| **Serverless cloud execution** | `uipath invoke` job final state | **PASS (v0.7.0)** — `compliance` and `summary` both ran on the UiPath serverless runtime and returned correct output (the real PATIENT HANDOFF rendered remotely) |

### Root cause of the earlier serverless faults (and the fix)

The first cloud runs faulted, debugged in order:
1. v0.4.0 (no `uipath` dep) → `exec: uipath: not found`. The serverless
   runner needs `uipath` on PATH → added `uipath>=2.10` to deps.
2. v0.5.0 / v0.6.0 → `"Failed to prepare environment / install
   dependencies"`. Two real causes, found via `uv lock`:
   - **`requires-python` was `>=3.10`, but `uipath` requires `>=3.11`** →
     the dependency set was unsatisfiable, so the runner's install step
     failed.
   - **No `uv.lock`** — the serverless runtime installs from a lock file
     (`uipath.json` had `includeUvLock: true`), which we hadn't generated.
3. **Fix (v0.7.0):** set `requires-python = ">=3.11"` and ran `uv lock`
   (62 packages, CPython 3.12). Republished → job state **Successful**,
   correct JSON output returned from the cloud.

Note: user licenses (Pro/Plus) were also allocated to the account during this
session, and there are 2 Production (Unattended) Robots + a Maestro license in
the tenant — but the actual blocker was the Python-version / lockfile packaging
issue above, not entitlement.

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
