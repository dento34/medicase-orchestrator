# Business Case — MediCase Orchestrator

> What this is, who it's for, and where the real market is — past the FIFA 2026 demo.

## The problem (in numbers)

**Language barrier × mass-gathering medical events:**

- **2.5 billion+** annual cross-border travelers (UNWTO 2024)
- **~4.5 billion** annual mass-gathering attendees (sports + festivals + religious + transport hubs)
- **5–15%** of on-site medical incidents at international events involve a language gap between responder and patient (event medicine literature varies by venue)
- **Every minute lost** to language confusion in cardiac arrest reduces survival by ~10% (AHA data)

Existing approaches:
- **Translation apps** (Google Translate, DeepL) → tool, not coordination. No routing, no resources, no audit.
- **On-call interpreters** → expensive, slow, often unavailable in rare languages
- **Bilingual volunteer rosters** → inconsistent, not scalable beyond a few common languages
- **Manual handoff to hospital** → information loss, repeat questions in ER

MediCase Orchestrator is a **case-management platform**, not a translator. It orchestrates the entire flow from first contact to hospital handoff, with language as one of several agents within the case.

## The platform pitch (in one sentence)

**"Same case flow, same five agents — different deployment."**

A UiPath Maestro Case template that any mass-gathering operator can install on their UiPath tenant within days, configure their specialist roster + language coverage + venue map, and start running.

## Production roadmap — concrete events

| Event | Date | Scale | Why suitable |
|---|---|---|---|
| **FIFA World Cup 2026** | 11 Jun – 19 Jul 2026 | 48 nations, 3M attendees | Demo scenario (hackathon timing) |
| **Hajj 2027** | Jun 2027 | ~2M pilgrims, 100+ languages, extreme heat | Saudi MoH already invests in digital health; ideal first pilot |
| **2027 World Athletics** | Sep 2027, Beijing | 200 nations | High-visibility, athlete medical readiness |
| **2027 Rugby World Cup** | Australia | 20 nations | Tournament-format pilot |
| **EURO 2028** | Jun–Jul 2028 | UK + Ireland, multi-language fans | Strong English-speaking host with multi-language visitors |
| **LA 2028 Summer Olympics** | Jul–Aug 2028 | 200+ nations | Largest single deployment opportunity |
| **2028 Asian Games** | Aichi-Nagoya | 45 nations | Asian language coverage proven |
| **Festival circuit (annual)** | Coachella, Tomorrowland, Glastonbury | 100K–500K per event | Drug-related emergencies + young multi-national crowds |
| **Marathon series (annual)** | Boston / London / Berlin / Tokyo / NYC | 30K–50K runners each | Athlete cardiac events, multi-language elite fields |
| **Cruise lines** | Year-round | ~30M passengers/year | Floating mass-gathering, classic language gap |
| **Major airports** | Year-round | Heathrow, JFK, Dubai, Atlanta | ~50 medical incidents/day per major hub, multilingual transit |

## Buyer personas

| Persona | Where they sit | What they buy with |
|---|---|---|
| **Event medical director** | FIFA, IOC, WHO partners, festival ops | Event safety budget (multimillion at world-level events) |
| **Stadium/venue operations** | Permanent venues hosting multiple events | Annual operations contract |
| **Cruise medical officer** | Royal Caribbean, MSC, Carnival | Fleet-level platform subscription |
| **Airport medical services** | Major airport authorities | Operational technology budget |
| **National sport authority** | Ministry of Sport / National Olympic Committees | Public sector procurement |

## Why UiPath, not a custom build

For target buyers (enterprise event ops, government, large healthcare orgs):

- **UiPath is already a procurement-approved vendor** in many of these orgs
- **Maestro provides the audit trail** regulatory bodies require
- **Agent Builder is low-code** — buyer's existing automation teams can extend, not just developers
- **Compliance posture** (UiPath SOC 2, HIPAA-ready cloud) is enterprise-grade out of the box
- **External agent framework support** (LangChain, CrewAI) means specialized models don't lock the platform

This is the differentiation from a "we built it ourselves on AWS" pitch.

## Open-source posture

The core orchestration is MIT-licensed (this repo). UiPath proprietary components remain under their license. This means:

- Event organizers can adopt without lock-in fear
- Community contributions add language support, region-specific protocols
- Marketplace listing post-hackathon is feasible (per UiPath blog, prior winners pursue this)

## Post-hackathon plan

1. **Aug 2026** — Apply submission to UiPath Marketplace (per finalist requirement)
2. **Sep–Oct 2026** — Outreach to Hajj 2027 organizers (Saudi MoH digital health initiative)
3. **Nov 2026 – Mar 2027** — Pilot setup at one event partner
4. **Jun 2027** — Hajj 2027 live deployment
5. **2028** — Scale to EURO + LA Olympics

This is not a hackathon demo. It's the working prototype of a real platform.
