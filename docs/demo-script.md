# Demo Video Storyboard (5 minutes max)

The submission video must show the working solution running on UiPath, walk through the architecture, explain agent orchestration, and show where humans fit. Hard cap: 5 minutes.

## Storyboard

### 0:00 – 0:25 — Open the wound

**Visual:** Stadium crowd, a fan collapses, volunteer Sara runs over.

**Voiceover (English subtitled):**
> "FIFA 2026. A Brazilian fan collapses. The volunteer who reaches him first speaks no Portuguese. The patient is conscious but disoriented. Every second now matters — for triage, for the right specialist, for the hospital that will receive him."

**On screen text:** "Language should never be the reason care arrives late."

---

### 0:25 – 1:15 — Case opens, Stage 1 (Intake)

**Visual:** Switch to UiPath Studio Web. A Maestro Case is triggered via Slack message `@medicase new patient` (or web trigger). Maestro Case view opens.

**Show on screen:**
- Case ID generated, location auto-captured from volunteer's Slack profile
- TriageAgent invoked → returns "cardiac cluster, urgent" (0.83 confidence)
- LanguageAgent invoked → detects Portuguese → sends QR code back to volunteer's phone

**Cut to:** Patient phone screen. Scans QR. Patient mini web app opens **in Portuguese**. Voice prompts in Portuguese: *"Onde está doendo? Você tem alergia? Está tomando algum remédio?"*

**Voiceover:** "Five agents are running. The patient never opens an app store. The volunteer never tries to translate."

---

### 1:15 – 2:10 — Stage 2 (Stabilization)

**Visual:** Maestro Case advances to Stabilization stage.

**Show on screen:**
- RTSLookupAgent fans out three parallel calls
  - Nearest AED → "8m away, Sector 12 wall, accessible"
  - Drug interaction check → "Losartan + epinephrine: monitor BP, no contraindication"
  - Ambulance ETA → "4 min"
- RoutingAgent scores three available specialists; assigns Dr. Emre (cardiac, in Sector 11, low load)
- Case auto-posts in `#medic-cardiac` channel with full context

**Cut to:** Slack channel. Dr. Emre clicks "Join Huddle" inside the case.

**Voiceover:** "The right specialist isn't the closest, or the most senior. It's the one with the right specialty, the right load, the right proximity. The routing agent picks. The case provides the full context — no re-explaining."

---

### 2:10 – 3:00 — Live Huddle + edge case (exception path)

**Visual:** Slack Huddle with three participants. Live translation overlay.

**Show on screen:**
- Sara speaks English → Dr. Emre's audio in Turkish, patient's web app receives Portuguese
- Suddenly: patient stops speaking, low STT confidence
- Maestro Case raises **exception** → falls back to **tap-card visual triage** (body map, pain scale icons)
- Patient taps chest + 8/10 pain → case continues without dropping

**Voiceover:** "Real emergencies don't follow happy paths. The case handles the patient going non-verbal, a low-confidence translation, a missing wearable — without dropping."

---

### 3:00 – 3:40 — Stage 3 (Handoff)

**Visual:** Maestro Case advances to Handoff stage.

**Show on screen:**
- SummaryAgent generates English handoff:
  ```
  🚨 PATIENT HANDOFF — MediCase Orchestrator
  Approx. Age: 35-45 | Language: Portuguese (Brazil)
  Location: Stadium A · Sector 12 · Gate C7 | Time: 14:32 UTC
  SYMPTOMS: Chest pain (8/10), dizziness, sweating
  ALLERGIES: Penicillin | MEDICATIONS: Losartan 50mg
  CHRONIC: Hypertension | WEARABLE: HR 142, irregular
  AED LOCATED: Sector 12 wall, 8m | AMBULANCE ETA: 4 min
  HANDED OFF BY: @volunteer_sara | ACCEPTED BY: Dr. Emre
  ```
- NotificationAgent pushes to receiving hospital's intake system
- Hospital ack received in 3 sec
- Family contact pinged (consent confirmed in Stage 1)

**Voiceover:** "The receiving hospital gets a clean English package — not a 'figure it out' phone call."

---

### 3:40 – 4:10 — Stage 4 (Post-incident) + learning loop

**Visual:** Maestro Case closes. ComplianceAgent writes audit log. LearningAgent anonymizes and stores.

**Show on screen:**
- Audit log entry (immutable, timestamped, with data source attribution)
- Anonymized record added to vector store
- **Demo magic moment:** Trigger a *second* case (same language + symptom cluster) → Stage 1 now shows "Similar prior case suggests asking about cardiac history" — learning loop visible in real time

**Voiceover:** "Every case the system handles makes the next one faster. The MCP-style case memory is the platform's compounding advantage."

---

### 4:10 – 4:40 — Claude Code reveal (bonus points)

**Visual:** Cut to terminal. Claude Code session export.

**Show on screen:**
- Session log: agent scaffolds generated, integration glue written, refactors made
- README's "Claude Code" section
- `claude-code-log/` folder with prompt evidence

**Voiceover:** "Every coded agent in this case was scaffolded with Claude Code via the UiPath CLI. Prompt logs are in the repo. UiPath for Coding Agents took us from idea to production-ready in 38 days."

---

### 4:40 – 5:00 — Close: TAM + roadmap

**Visual:** Map dissolves through events.

**Show on screen:**
- FIFA 2026 → Hajj 2027 → EURO 2028 → LA 2028 Olympics → festivals → marathons → cruise ships → airports

**Voiceover:** "FIFA 2026 is a vivid demo. Hajj 2027 is two million pilgrims, a hundred languages, real heat-stroke risk. LA 2028 is 200 nation states under one roof. Same case flow, same agents — different deployment. MediCase Orchestrator. Built on UiPath Maestro. Ready to ship."

**End card:** github.com/dento34/medicase-orchestrator · UiPath AgentHack 2026

---

## Production notes

- **Live screen capture only.** Per UiPath's rules and culture, "not slides, not marketing videos." Real Maestro Case running.
- **Subtitles in English** throughout.
- **Music:** royalty-free, low energy, slight tension; ramp at 4:40.
- **Total budget:** 4:55 to leave 5-second buffer for end card.
- **Test:** play back at 1.25x to ensure clarity — many judges scrub.

## Checklist before recording

- [ ] UiPath Cloud sandbox running stable
- [ ] Test case data set ready (Brazilian + chest pain seed)
- [ ] Edge case scenario rehearsed (non-verbal fallback)
- [ ] Second-case learning loop demo prepared
- [ ] Claude Code session log freshly exported, clean
- [ ] All names / IDs anonymized (no real PII in demo)
- [ ] Audio levels balanced
- [ ] End card has correct GitHub URL
