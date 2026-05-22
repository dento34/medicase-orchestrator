# Learning Path — UiPath AgentHack 2026

Resources from the official AgentHack resources page, sequenced for our needs (Track 1: Maestro Case, with coded agents + Claude Code).

## Week-by-week plan

### Week 1 (22–29 May 2026): Foundations

**Goal:** Understand UiPath Platform structure, register for everything, attend overview webinars.

**Live sessions (mark calendar):**
- **26 May** — AgentHack General Overview & Logistic Guidelines ([link](https://community.uipath.com/events/details/uipath-new-york-presents-uipath-agenthack-general-overview-and-logistic-guideline-review-2026/))
- **27 May** — Connector Corner: Agent Builder ([link](https://community.uipath.com/events/details/uipath-pennsylvania-presents-connector-corner-agent-builder-create-test-and-deploy-enterprise-ai-agents/))
- **28 May** — Dev Dives: Empower Coding Agents to enhance RPA SDLC ([link](https://community.uipath.com/events/details/uipath-americas-virtual-events-presents-dev-dives-empower-coding-agents-to-enhance-the-rpa-sdlc/)) — **critical for our Claude Code strategy**

**Self-paced:**
- [UiPath Platform overview for developers](https://www.uipath.com/developers)
- [Agentic Automation introduction](https://www.uipath.com/automation/agentic-automation)
- [Studio Web basics](https://docs.uipath.com/studio-web/docs/getting-started)
- [UiPath Academy — find Maestro and Agent Builder learning plans](https://academy.uipath.com/learning-plans?sort=-date)

### Week 2 (30 May – 5 Jun): Maestro Case deep-dive

**Goal:** Build a minimal Maestro Case end-to-end. Get familiar with stages, exception handling, human-in-loop.

**Read / watch:**
- [Maestro overview](https://docs.uipath.com/maestro)
- [Maestro orchestration concepts](https://docs.uipath.com/maestro/docs/orchestration-overview)
- [Maestro Use Case Explorer](https://maestro-use-case.azurewebsites.net/) — look specifically for healthcare / patient-care examples

**Build:**
- A 2-stage toy case (intake → review) in UiPath Cloud
- Trigger via webhook
- Add 1 human-in-loop checkpoint

### Week 3 (6–12 Jun): Agent Builder + first real agent

**Goal:** Build TriageAgent + RoutingAgent in Agent Builder. Hook into Maestro Case.

**Read:**
- [Agent Builder getting started](https://docs.uipath.com/agent-builder/docs/getting-started)
- [Building an agent in Studio Web](https://docs.uipath.com/agents/automation-cloud/latest/user-guide/building-an-agent-in-studio-web)

**Live session:**
- **9 Jun** — AgentHack Winner Overview & Best Practices ([link](https://community.uipath.com/events/details/uipath-new-york-presents-uipath-agenthack-winner-overview-and-best-practices-2026/)) — **must attend**, this is where 2025 winners share what worked

**Build:**
- TriageAgent in Agent Builder (low-code)
- RoutingAgent in Agent Builder
- Connect both to the Maestro Case stages

### Week 4 (13–19 Jun): Coded Agents + Claude Code integration

**Goal:** Build the three coded agents (Language, RTSLookup, Compliance). Set up Claude Code + UiPath CLI integration.

**Read:**
- [Coded Automation docs](https://docs.uipath.com/studio/docs/coded-automation)
- [About Coded Agents](https://docs.uipath.com/agents/automation-cloud/latest/user-guide/about-coded-agents)
- [Python SDK repo](https://github.com/UiPath/uipath-python)
- [UiPath for Coding Agents](https://www.uipath.com/developers/coding-agents)
- [UiPath CLI with coding agents](https://docs.uipath.com/uipath-cli/standalone/latest/user-guide/coding-agents)
- [UiPath skills repo (Claude Code skills)](https://github.com/UiPath/skills)
- [CLI npm package](https://www.npmjs.com/package/@uipath/cli)

**Live session:**
- **15 Jun** — AgentHack Office Hour ([link](https://community.uipath.com/events/details/uipath-new-york-presents-uipath-agenthack-office-hour-for-questions-and-support-2026/)) — bring questions

**Build:**
- LanguageAgent (Coded Agent, Python SDK)
- RTSLookupAgent (Coded + API Workflows + CrewAI wrap)
- ComplianceAgent (Coded Agent)
- Capture every Claude Code session in `claude-code-log/`

### Week 5 (20–25 Jun): End-to-end + integration polish

**Goal:** Happy path runs in under 90 seconds. Three edge cases verified.

**Live sessions:**
- **23 Jun** — Connector Corner: UiPath Maestro Case Management ([link](https://community.uipath.com/events/details/uipath-phoenix-presents-connector-corners-uipath-maestro-enterprise-orchestration-with-case-management/))
- **25 Jun** — Dev Dives: Troubleshoot any automation failure with UiPath for Coding Agents ([link](https://community.uipath.com/events/details/uipath-americas-virtual-events-presents-dev-dives-troubleshoot-any-automation-failure-with-uipath-for-coding-agents/))

**Build:**
- Patient mini web app deployed (Vercel)
- Three edge cases scripted: unconscious patient, rare language fallback, concurrent cases
- Demo video script frozen

### Week 6 (26–29 Jun): Demo + submission

**Goal:** Ship.

- Record demo video (live screen capture, no slides)
- README.md final polish (UiPath components list, Claude Code section, setup steps)
- Presentation deck (UiPath template)
- Devpost project page final
- Best Product Feedback survey filled
- Submit at least 24h before deadline

---

## Key external frameworks

We integrate one external multi-agent framework. UiPath explicitly encourages this and bonus-rewards the blend.

- **CrewAI** ([docs](https://docs.crewai.com/)) — chosen for RTSLookupAgent's parallel multi-source query coordination
- **LangChain** ([site](https://www.langchain.com/)) — used inside LanguageAgent for tool-use orchestration (TTS, STT, translation)
- **AutoGen** — evaluated, not used for v1

## Key UiPath surfaces we will touch

| Surface | Track 1 relevance | Our usage |
|---|---|---|
| UiPath Studio Web | Build environment | All development |
| UiPath Automation Cloud | Runtime | Everything runs here |
| Maestro Case | **Track 1 primary** | 4-stage case orchestration |
| Agent Builder | Track 1 supported | TriageAgent, RoutingAgent |
| Coded Agents (Python SDK) | Track 1 supported | LanguageAgent, RTSLookupAgent, ComplianceAgent |
| API Workflows | Track 1 supported | External integrations (AED, drug, hospital handoff) |
| Document Understanding | **Track 1 highly relevant** | Patient ID / medical card OCR |
| UiPath for Coding Agents | **Bonus points** | Claude Code scaffolding |
| Test Cloud | Track 3 only | Not used by us |

---

## Daily learning rhythm (suggested)

- **1–2 hours/day** of focused learning + building
- Mornings: read docs / watch session recording (lower energy)
- Evenings: build (higher focus)
- **Saturday mornings**: weekly review — what works, what doesn't, what to cut

## Where to get help

| Channel | Use for |
|---|---|
| [UiPath Forum](https://forum.uipath.com/) | Specific technical questions, search archives first |
| AgentHack Office Hours (15 Jun live) | Open Q&A with UiPath staff |
| [UiPath Community](https://community.uipath.com/agenthack-resources/) | Inspiration hub, prior winner projects |
| [UiPath GitHub](https://github.com/UiPath) | Source code, examples |
| Claude Code (this repo's `claude-code-log/`) | Implementation drafts, refactors |
