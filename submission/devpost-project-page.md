# Devpost Project Page Draft

> Final content to paste into the Devpost submission form, with placeholders for assets that will be ready by 29 Jun 2026.

---

## Project Title

**MediCase Orchestrator — Multilingual Emergency Patient Handoffs at Mass-Gathering Events**

## Track

**Track 1: UiPath Maestro Case**

## Elevator Pitch (250 chars)

```
Multi-agent case management for emergency medical handoffs when responder
and patient don't share a language. Built on UiPath Maestro Case + 5
orchestrated agents + Claude Code scaffolding. Under 90 sec, trigger to
hospital handoff. FIFA 2026 demo, Hajj 2027 production target.
```

## Inspiration

At mass-attendance events — FIFA, Olympics, Hajj, festivals, marathons — volunteer responders and the patients they reach often don't share a language. Translation apps solve part of the problem, but they don't coordinate handoffs, route to the right on-site specialist, fetch real-time resources, or produce a clean handoff package to the receiving hospital. The minutes spent fumbling cost lives. We wanted a case-management platform, not a translator — and Maestro Case is the right substrate for exactly this kind of dynamic, exception-heavy, multi-actor workflow.

## What it does

MediCase Orchestrator runs as a UiPath Maestro Case across four stages:

1. **Intake** — Triage classification + language detection + in-language voice triage (via patient mini web app launched by QR)
2. **Stabilization** — Real-time AED + drug interaction + ambulance ETA lookup, in parallel with specialist routing
3. **Handoff** — English handoff package generated, pushed to receiving hospital, family contact notified
4. **Post-incident** — Audit trail + anonymized case memory for organizational learning

Five agents operate within these stages:

- **TriageAgent** (Agent Builder) — severity + condition cluster
- **LanguageAgent** (Coded Agent) — detection + voice triage
- **RTSLookupAgent** (Coded Agent + API Workflows + CrewAI) — parallel real-time lookups
- **RoutingAgent** (Agent Builder) — specialist selection
- **ComplianceAgent** (Coded Agent) — audit + anonymized learning

Humans stay in the loop at every critical decision point. The system handles unconscious patients, low-resource languages, missing wearables, and concurrent cases without dropping.

## How we built it

- **UiPath Maestro** as the orchestration backbone (case stages, exception handling, human-in-loop checkpoints)
- **UiPath Agent Builder** for low-code agents (TriageAgent, RoutingAgent)
- **UiPath Coded Agents** (Python SDK) for the three logic-heavy agents
- **UiPath API Workflows** for external integrations (AED API, drug interaction, hospital handoff)
- **UiPath Document Understanding** for patient ID / medical card OCR when available
- **CrewAI** integrated inside RTSLookupAgent for multi-source query coordination
- **LangChain** inside LanguageAgent for tool-use orchestration
- **Patient mini web app** built with Next.js, deployed on Vercel, launched via QR

### UiPath for Coding Agents (bonus)

All three coded agents were scaffolded with **Claude Code** via the UiPath CLI integration. See [`claude-code-log/`](https://github.com/<your-user>/medicase-orchestrator/tree/main/claude-code-log) for prompt session exports, summaries, and commit-level evidence.

## Challenges we ran into

[To be filled in by 25 Jun — keep an ongoing notes file. Likely candidates: low-resource language STT accuracy, concurrent case ID isolation, Maestro Case exception path testing.]

## Accomplishments we're proud of

[To be filled in by 25 Jun. Likely: 90-second target hit on happy path; three edge cases handled cleanly; learning loop visible in real-time demo.]

## What we learned

[To be filled in by 25 Jun.]

## What's next

This is not a demo. The production roadmap:

- **Aug 2026** — Submit to UiPath Marketplace
- **Sep–Oct 2026** — Outreach to Hajj 2027 organizers (Saudi MoH digital health initiative)
- **2027** — Hajj 2027 live deployment
- **2028** — EURO 2028 + LA Olympics

Same case flow, same agents — different deployment.

## Built With

- uipath-maestro
- uipath-agent-builder
- uipath-coded-agents
- uipath-api-workflows
- uipath-document-understanding
- claude-code
- python
- crewai
- langchain
- nextjs
- vercel
- openstreetmap

## Try it out

- **GitHub:** https://github.com/<your-user>/medicase-orchestrator
- **Demo video:** [YouTube link by 29 Jun]
- **Presentation deck:** [Drive link by 29 Jun]

---

## Submission checklist (internal — not pasted to Devpost)

- [ ] Devpost project page filled out completely
- [ ] Track selected: Track 1
- [ ] Demo video uploaded to YouTube (public, < 5 min)
- [ ] GitHub repo public + MIT license + complete README
- [ ] Presentation deck shared via Drive/OneDrive (access-to-all)
- [ ] Best Product Feedback survey filled separately (chance at $1.5K)
- [ ] All claims verifiable from repo + video
