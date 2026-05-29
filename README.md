# MediCase Orchestrator

> Agentic case management for emergency medical handoffs at mass-gathering events, where on-site responders and patients often don't share a language.

Built for [UiPath AgentHack 2026](https://uipath-agenthack.devpost.com/) — **Track 1: UiPath Maestro Case**.

---

## The Problem

At mass-attendance events (FIFA World Cup, Hajj, Olympics, festivals, marathons), volunteer medical responders and collapsed patients often don't share a language. Critical minutes are lost to communication failure. Existing tools (translation apps) only solve part of the problem — they don't coordinate handoffs, route to the right specialist, fetch real-time resources (nearest AED, drug interactions), or produce a clean handoff to the receiving hospital.

## The Solution

A UiPath Maestro Case coordinates **five agents** across four case stages, with humans-in-the-loop at every critical decision:

1. **TriageAgent** — symptom classification, severity, urgency
2. **LanguageAgent** — detection + in-language voice intake (TTS/STT + translation)
3. **RTSLookupAgent** — real-time AED location, drug interactions, ambulance ETA
4. **RoutingAgent** — selects and assigns the right on-site specialist
5. **ComplianceAgent** — HIPAA-style audit trail + anonymized case memory

**Target:** under 90 seconds from volunteer trigger to ambulance handoff.

See [docs/architecture.md](docs/architecture.md) for the case stage flow.

---

## UiPath components used

- **UiPath Maestro** — Case Management orchestration (4 stages, exception handling, human handoffs)
- **UiPath Agent Builder** — low-code agents (TriageAgent, RoutingAgent)
- **UiPath Coded Agents** (Python SDK) — LanguageAgent, RTSLookupAgent, ComplianceAgent
- **UiPath API Workflows** — external integrations (AED API, hospital handoff)
- **UiPath Document Understanding (IDP)** — passport / medical card intake when available
- **UiPath Studio Web** — development environment
- **External frameworks** — CrewAI for multi-agent coordination, LangChain for tool use

## Agent types

This solution combines:

- **Low-code Agents** (built with UiPath Agent Builder)
- **Coded Agents** (built with UiPath Python SDK)
- **External Agents** (LangChain / CrewAI, orchestrated through Maestro)

## UiPath for Coding Agents (Claude Code) — bonus point category

Significant portions of this solution were scaffolded using **Claude Code** through UiPath for Coding Agents. See [claude-code-log/](claude-code-log/) for prompt sessions and integration evidence.

---

## Setup

> Detailed setup is being completed during the development period (May–June 2026).

```bash
# 1. Clone
git clone https://github.com/dento34/medicase-orchestrator.git
cd medicase-orchestrator

# 2. Python env for coded agents
python -m venv .venv
.venv/Scripts/python.exe -m pip install anthropic python-dotenv pydantic

# 3. Copy env template and fill in values
cp .env.example .env       # then edit: UIPATH_PAT, (optional) ANTHROPIC_API_KEY

# 4. Run the end-to-end demo (chains all 4 coded agents)
.venv/Scripts/python.exe agents/demo_runner.py
```

The demo runs with zero secrets: LLM calls fall back to deterministic mocks
unless `ANTHROPIC_API_KEY` is set, and RTS lookups run live against free
public APIs (OpenStreetMap, NIH RxNav) unless `RTS_OFFLINE=1`.

### Status of the coded agents

| Agent | Stage | Status | Verify |
|---|---|---|---|
| LanguageAgent | 1 Intake | ✅ built + tested | `agents/language_agent/tests/test_smoke.py` |
| RTSLookupAgent | 2 Stabilization | ✅ built + tested (live OSM) | `agents/rts_lookup_agent/tests/test_smoke.py` |
| SummaryAgent | 3 Handoff | ✅ built + tested | `agents/summary_agent/tests/test_smoke.py` |
| ComplianceAgent | 4 Post-incident | ✅ built + tested | `agents/compliance_agent/tests/test_smoke.py` |
| TriageAgent | 1 Intake | ⏳ low-code (UiPath Agent Builder) | — |
| RoutingAgent | 2 Stabilization | ⏳ low-code (UiPath Agent Builder) | — |

End-to-end: `agents/demo_runner.py` chains all 4 coded agents in ~5s.

---

## Repository layout

```
medicase-orchestrator/
├── README.md                          # this file
├── LICENSE                            # MIT
├── .gitignore
├── docs/
│   ├── architecture.md                # case stages + agent topology
│   ├── agents.md                      # detailed agent specifications
│   ├── demo-script.md                 # 5-minute demo storyboard
│   ├── learning-path.md               # UiPath Academy + webinar schedule
│   └── business-case.md               # production roadmap, TAM
├── agents/                            # coded agent implementations (Python SDK)
├── patient-app/                       # patient-side mini web app (QR-launched)
├── claude-code-log/                   # Claude Code session exports (bonus evidence)
└── submission/
    └── devpost-project-page.md        # Devpost project page draft
```

---

## Demo

> 5-minute demonstration video will be linked here before submission.

Demo scenario: a Brazilian fan with chest pain at FIFA World Cup 2026. Volunteer triggers a case in Slack/Teams → patient scans QR → in-language voice triage → real-time AED + drug interaction lookup → specialist routed in `#medic-cardiac` → live Huddle translation → hospital handoff.

See [docs/demo-script.md](docs/demo-script.md).

---

## Production roadmap

| Event | Date | Why |
|---|---|---|
| FIFA World Cup 2026 | Jun–Jul 2026 (demo scenario) | Multi-language stadium triage |
| Hajj 2027 | Jun 2027 | ~2M pilgrims, 100+ languages, heat-related emergencies |
| EURO 2028 | Jun–Jul 2028 | UK + Ireland |
| LA 2028 Olympics | Jul–Aug 2028 | 200+ nation athletes + visitors |
| Yearly festival circuit | Coachella, Tomorrowland, Glastonbury | Drug-related emergencies |
| Marathon series | Boston, London, Berlin, Tokyo | Athlete emergencies |
| Cruise lines & major airports | Year-round | Classic language-barrier medical scenarios |

Same case flow, same agents — different deployment.

See [docs/business-case.md](docs/business-case.md) for the full pitch.

---

## License

MIT — see [LICENSE](LICENSE).

---

## Team

[Representative name + contact will be added after team assembly]

Built during the UiPath AgentHack 2026 Submission Period (15 May – 29 Jun 2026).
