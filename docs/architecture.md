# Architecture

## High-level diagram

```
                    ┌───────────────────────────────────────────┐
                    │       UIPATH MAESTRO CASE (4 STAGES)      │
                    │                                           │
                    │   ┌─────────────────────────────────────┐ │
                    │   │ 1. INTAKE                           │ │
                    │   │   • TriageAgent  (Agent Builder)    │ │
                    │   │   • LanguageAgent (Coded Agent)     │ │
                    │   │   • Document Understanding (intake) │ │
                    │   │   • Human-in-loop: volunteer        │ │
                    │   └─────────────────────────────────────┘ │
                    │                    ↓                      │
                    │   ┌─────────────────────────────────────┐ │
                    │   │ 2. STABILIZATION                    │ │
                    │   │   • RTSLookupAgent (Coded + API WF) │ │
                    │   │   • RoutingAgent (Agent Builder)    │ │
                    │   │   • Human-in-loop: on-site medic    │ │
                    │   └─────────────────────────────────────┘ │
                    │                    ↓                      │
                    │   ┌─────────────────────────────────────┐ │
                    │   │ 3. HANDOFF                          │ │
                    │   │   • SummaryAgent (Coded)            │ │
                    │   │   • NotificationAgent (API WF)      │ │
                    │   │   • Human-in-loop: receiving hospital│ │
                    │   └─────────────────────────────────────┘ │
                    │                    ↓                      │
                    │   ┌─────────────────────────────────────┐ │
                    │   │ 4. POST-INCIDENT                    │ │
                    │   │   • ComplianceAgent (Coded)         │ │
                    │   │   • LearningAgent (Coded + memory)  │ │
                    │   └─────────────────────────────────────┘ │
                    └───────────────────────────────────────────┘
                                         ↑↓
                    ┌───────────────────────────────────────────┐
                    │            EXTERNAL SURFACES               │
                    │                                           │
                    │  • Patient mini web app (Next.js, QR)     │
                    │  • Volunteer interface (Slack/Teams DM)   │
                    │  • Specialist channels (Slack/Teams)      │
                    │  • Hospital handoff endpoint              │
                    │  • RTS sources: OSM AED, drug API, ETA    │
                    │  • Wearable bridge (Apple Health, optional)│
                    └───────────────────────────────────────────┘
```

## Case stages — detailed

### Stage 1: INTAKE

**Trigger:** Volunteer initiates case via Slack/Teams DM, web form, or voice command.

**Inputs collected:**
- Volunteer location (event sector / gate)
- Patient observable state (conscious / unconscious, visible injury, etc.)
- Initial patient utterance (text or audio)
- Optional: photo of patient's ID / medical card → Document Understanding

**Agents:**
- `TriageAgent` (Agent Builder, low-code) — classifies severity, narrows symptom cluster
- `LanguageAgent` (Coded Agent, Python SDK) — detects language from utterance + browser locale; generates in-language voice triage prompts (TTS); transcribes patient responses (STT)
- `DocumentUnderstandingAgent` (UiPath IDP) — extracts data from ID / medical card photos

**Human-in-loop:** Volunteer confirms / corrects detected language and severity before progressing.

**Stage exit:** Validated triage record + patient language identified.

---

### Stage 2: STABILIZATION

**Goal:** Resource discovery + specialist routing in parallel.

**Agents:**
- `RTSLookupAgent` (Coded + API Workflows) — three parallel queries:
  - Nearest AED (OpenStreetMap defibrillator nodes / AED Locator API)
  - Drug interactions (given patient-reported meds + suggested treatments)
  - Ambulance ETA (event ops API or mock)
- `RoutingAgent` (Agent Builder) — matches case profile to available specialist:
  - Specialty (cardiac / trauma / pediatric / neuro / allergic)
  - Distance / sector proximity
  - Current load
  - Posts case to specialist's preferred channel with full context

**Human-in-loop:** On-site medic accepts case, may request additional info or escalate.

**Stage exit:** Specialist assigned + critical resources located.

---

### Stage 3: HANDOFF

**Goal:** Produce a clean English handoff package for the receiving hospital.

**Agents:**
- `SummaryAgent` (Coded Agent, LLM-backed) — composes structured handoff from full case log:
  - Patient demographics + language
  - Location + time
  - Symptoms (translated to English)
  - Allergies / medications / chronic conditions
  - Wearable snapshot (if available)
  - Interventions taken on-site
- `NotificationAgent` (API Workflows) — pushes handoff to hospital intake system; pings designated family contact if patient gave consent.

**Human-in-loop:** Receiving hospital confirms acceptance; if not received within X seconds, escalates.

**Stage exit:** Hospital acknowledged + ambulance dispatched.

---

### Stage 4: POST-INCIDENT

**Goal:** Audit trail + organizational learning.

**Agents:**
- `ComplianceAgent` (Coded Agent) — writes full audit log (timestamps, agent actions, human decisions, data sources accessed) to immutable storage. HIPAA-style record.
- `LearningAgent` (Coded Agent) — anonymizes case (strip PII), embeds it into vector store, runs pattern analysis. Future similar cases (same language + symptom cluster) get pre-loaded triage suggestions.

**Stage exit:** Case archived + anonymized record added to learning store.

---

## Multi-agent coordination pattern

We use **Maestro as the orchestration layer**, not a single super-agent. Each stage has clearly scoped agents that:

1. Receive structured inputs from the Maestro Case context
2. Run their reasoning step (LLM call, API call, or UiPath workflow)
3. Write structured outputs back to the case for the next stage to consume
4. Raise exceptions to the human-in-loop when confidence is low

For external multi-agent coordination within a stage (e.g., the three parallel queries in Stage 2), we use **CrewAI** wrapped inside a Coded Agent — UiPath remains the governance layer.

## Exception paths (handled, not ignored)

| Exception | Stage | Response |
|---|---|---|
| Patient unconscious / non-verbal | 1 | Skip voice triage → wearable + observable-only protocol |
| Language model low confidence | 1 | Escalate to human; fallback to tap-card visual triage |
| No AED within reasonable distance | 2 | Skip AED route, prioritize ambulance ETA |
| Drug interaction critical conflict | 2 | Block recommendation, page senior doctor immediately |
| No matching specialist available | 2 | Round-robin to general medic + flag in case |
| Hospital handoff unacknowledged | 3 | Retry, then escalate to event ops |
| Multiple concurrent cases | All | Case-ID isolation; specialist load tracked in routing |

## Why Maestro Case (not BPMN, not standalone agents)

Track 1 (Maestro Case) is chosen because:
- **Process is dynamic** — case may skip stages, loop back, escalate based on patient state
- **Exception-heavy** — each stage has multiple failure modes that require graceful handling
- **Human-in-loop critical** — medical decisions must remain under human accountability
- **Stage-based natural decomposition** — emergency medicine workflows already follow intake/stabilize/handoff/post

BPMN (Track 2) would force premature path-locking. Standalone agents (no orchestration) would lose audit trail and exception coordination.
