# Agent Specifications

This document specifies the five agents that operate within the Maestro Case. Each spec includes: purpose, inputs, outputs, implementation type, and failure mode.

---

## 1. TriageAgent

**Purpose:** Classify symptom severity and narrow down likely condition categories.

**Implementation:** UiPath Agent Builder (low-code).

**Inputs:**
- Patient initial utterance (text, translated to English)
- Volunteer observation notes
- Optional: vital signs from wearable

**Outputs:**
- Severity tier: `critical` / `urgent` / `stable`
- Condition cluster: `cardiac` / `trauma` / `respiratory` / `neuro` / `allergic` / `general`
- Confidence score (0.0–1.0)
- Suggested triage questions (passed to LanguageAgent)

**Failure mode:** If confidence < 0.6, raise human-in-loop interrupt. Default to `urgent` severity until corrected.

---

## 2. LanguageAgent

**Purpose:** Detect patient language and conduct voice-based triage in that language.

**Implementation:** UiPath Coded Agent (Python SDK) + Claude API + Web Speech API on patient web app.

**Inputs:**
- Patient utterance (audio blob or text)
- Browser locale hint (from patient web app)
- Triage questions (from TriageAgent, in English)

**Outputs:**
- Detected language code (ISO 639-1)
- Translated triage questions (in patient's language, TTS-ready)
- Transcribed + back-translated patient responses (English structured record)

**Supported languages (v1):** Spanish, Portuguese, Arabic, French, German, Japanese, Korean, Dutch, Mandarin, Russian, Hindi, Turkish, Wolof, Darija.

**Failure mode:** Low-resource language (Wolof, Darija) → STT confidence drop → fallback to **tap-card visual triage** (body map, pain scale icons).

---

## 3. RTSLookupAgent

**Purpose:** Real-time lookup of nearest AED, drug interactions, and ambulance ETA.

**Implementation:** UiPath Coded Agent (Python SDK) + UiPath API Workflows.

**Inputs:**
- Event location (sector / gate / GPS)
- Patient-reported medications (from LanguageAgent output)
- Proposed interventions

**Outputs:**
- AED list within 200m, sorted by distance + accessibility
- Drug interaction warnings (severity ranked)
- Ambulance ETA (best available estimate)

**Data sources:**
- OpenStreetMap `emergency=defibrillator` nodes (free, open)
- AED Locator API (fallback, registered events)
- RxNav drug interaction API (NIH, free)
- Event operations API for ambulance position (mock during demo)

**Failure mode:** If primary API fails, fall back to secondary source. If both fail, flag stage as "manual lookup required" and surface to medic.

---

## 4. RoutingAgent

**Purpose:** Select and assign the right on-site specialist.

**Implementation:** UiPath Agent Builder (low-code) + workspace metadata.

**Inputs:**
- Condition cluster (from TriageAgent)
- Severity (from TriageAgent)
- Case location
- Specialist roster with: specialty, sector position, current load, language skills

**Outputs:**
- Selected specialist ID
- Specialist's preferred contact channel (Slack/Teams/SMS)
- Pre-filled handoff message with case summary

**Selection logic:** Weighted score = specialty_match × 0.5 + proximity × 0.3 + (1 − current_load) × 0.2.

**Failure mode:** No matching specialist available → escalate to general medic + flag case "specialist gap".

---

## 5. ComplianceAgent

**Purpose:** Maintain HIPAA-style audit trail + organizational learning record.

**Implementation:** UiPath Coded Agent (Python SDK).

**Inputs:**
- Every agent invocation in the case (auto-captured via Maestro audit hook)
- Every human decision (timestamped via case events)
- All data accessed (with source attribution)

**Outputs (two distinct streams):**

1. **Audit log** — immutable, fully-identified, retention per regulation. Includes:
   - Timestamps
   - Agent inputs/outputs
   - Human decisions + rationale (when entered)
   - Data sources accessed (with auth scope)

2. **Anonymized learning record** — strip PII (name, exact location, contact), retain:
   - Demographics buckets (age range, gender, language family)
   - Symptom cluster + interventions
   - Outcome (resolved on-site / transported / no-show)

Anonymized records embed into a vector store → future similar cases get pre-loaded triage suggestions in Stage 1.

**Failure mode:** If audit write fails, BLOCK case progression. Compliance cannot degrade silently.

---

## Multi-agent orchestration patterns used

| Pattern | Where | Why |
|---|---|---|
| **Sequential with handoff** | Stage 1 → 2 → 3 → 4 | Each stage produces structured context for the next |
| **Parallel fan-out** | Stage 2 (RTSLookupAgent) | AED + drug + ETA queries run in parallel for latency |
| **Human-in-loop interrupt** | Every stage exit | Maestro pauses for human confirmation on critical decisions |
| **Exception escalation** | Any agent below confidence threshold | Escalate to senior human |
| **External framework wrap** | CrewAI used inside RTSLookupAgent | Multi-source query coordination within a single coded agent |

## Agent type mix (for Devpost README disclosure)

| Agent | Type |
|---|---|
| TriageAgent | Low-code (Agent Builder) |
| LanguageAgent | Coded (Python SDK) |
| RTSLookupAgent | Coded + API Workflows + CrewAI |
| RoutingAgent | Low-code (Agent Builder) |
| ComplianceAgent | Coded (Python SDK) |

**This solution uses Coded Agents + Low-code Agents + External Frameworks** — exactly the "blended" approach UiPath highlights as preferred.

## Claude Code usage (UiPath for Coding Agents bonus)

The scaffolding, refactors, and integration glue for all three coded agents was done with **Claude Code** via the UiPath CLI integration. See [`../claude-code-log/`](../claude-code-log/) for prompt session exports.
