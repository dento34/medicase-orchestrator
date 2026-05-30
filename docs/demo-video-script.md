# MediCase Orchestrator — Demo Video Script (3 min, very detailed)

> Target: **UiPath AgentHack 2026 — Track 1 (Maestro Case Management)**
> Hard cap: 3 minutes. Hook in first 8 seconds. Strongest proof (cloud Successful) in last third.
> Tone: calm, confident, technical-but-human. Voice-over is short; the screen is the star.

---

## Why this script works

Two "wow" moments anchor it:

1. **2:00 — UiPath Orchestrator → Latest jobs panel showing four `Agent (python) | Successful` rows.** Mechanical proof the orchestration actually ran on UiPath cloud.
2. **2:15 — Patient app flipping right-to-left when locale switches to Arabic.** Human proof the multi-language design is real, not a stub.

Everything else is structure that earns the right to those two seconds.

---

## Pre-recording setup (do this 10 minutes before you hit record)

### A. Software / windows to have open

Open these in **this exact order** so Alt+Tab follows the storyboard:

1. **PowerPoint / Keynote** — three title slides (see "Slides" below).
2. **Chrome tab 1 — UiPath Studio Web, Process.bpmn open:**
   `https://staging.uipath.com/hackathon26_137/studio_/designer/90651d02-44a8-437e-b74c-be4a34f30636?solutionId=f4376787-0654-4ecb-2ffa-08debcc25de2`
3. **Chrome tab 2 — UiPath Studio Web, TriageAgent (Agent Builder) Definition:**
   Solution → Agent → Definition. Scroll so System prompt is visible.
4. **Chrome tab 3 — UiPath Orchestrator Overview / Latest jobs:**
   `https://staging.uipath.com/hackathon26_137/DefaultTenant/orchestrator_/global-monitoring/overview`
   Scroll until **Latest jobs** table is on screen with at least four "✅ Successful" rows for `medicase-coded-summary | Agent (python)`.
5. **Chrome tab 4 — Patient mini web app, Portuguese:**
   `http://localhost:8000/?lang=pt&case_id=demo-fifa-001`
   Open Chrome DevTools (F12) → toggle **mobile device** → iPhone 14 Pro.
6. **Chrome tab 5 — same patient app, Arabic:**
   `http://localhost:8000/?lang=ar&case_id=demo-fifa-001` (RTL flip ready to show)
7. **Chrome tab 6 — same patient app, Turkish:**
   `http://localhost:8000/?lang=tr&case_id=demo-fifa-001`
8. **Chrome tab 7 — GitHub repo (closing CTA):**
   `https://github.com/dento34/medicase-orchestrator`
9. **Terminal window — fullscreen, dark theme, font 16pt+,** sitting in repo root with the venv active. Ready to run:
   ```bash
   .venv/Scripts/python.exe agents/demo_runner.py
   ```

### B. Pre-flight checks (one minute)

```bash
# Terminal sanity check before pressing record:
cd "C:\Users\mehme\OneDrive\Masaüstü\slack-agent\medicase-orchestrator"
python patient-app/serve.py &        # patient app on http://localhost:8000
.venv/Scripts/python.exe agents/demo_runner.py | head -5   # smoke
```

Confirm:
- [ ] Patient app responds at `localhost:8000/?lang=pt&case_id=demo` in mobile view.
- [ ] Orchestrator tab actually shows ✅ Successful rows (refresh if cached).
- [ ] Microphone level is fine. Mute Discord / Slack / Teams notifications.
- [ ] Close email, browser tab strip is clean (no clutter to read).
- [ ] Screen resolution 1920×1080. Cursor highlighter ON if your recorder supports it.

### C. Recording tool

- **Loom (recommended)** — fastest path, auto-uploads, gives you a public URL for Devpost.
- **OBS Studio** — best quality + scene cuts, but needs setup.
- **Win + G (Xbox Game Bar)** — built-in fallback, no install.

Output: **mp4, 1920×1080, 30 fps, < 200 MB** (Devpost likes <200 MB).

### D. Three title slides (PowerPoint)

```
Slide 1 (cover, 0:00–0:08):
  Background: dim stadium crowd photo, low contrast.
  Big text (centered, 80pt):  Language can't wait one second.
  Small text (bottom):  MediCase Orchestrator · UiPath AgentHack 2026

Slide 2 (architecture, 0:35–0:45):
  Title: 6 agents orchestrated by UiPath Maestro
  Diagram (use docs/architecture.md mermaid, exported as PNG):
    Patient app → [LanguageAgent → TriageAgent → RTSLookupAgent → RoutingAgent → SummaryAgent → ComplianceAgent]
    Label: 4 coded (Python) + 2 low-code (Agent Builder)
  Footer:  Built with Claude Code · Published to UiPath workspace

Slide 3 (closing CTA, 2:48–3:00):
  Big:  github.com/dento34/medicase-orchestrator
  Sub:  Built with Claude Code + UiPath Maestro · +2 bonus for "UiPath for Coding Agents"
```

---

## Storyboard — second by second

Each scene has: **what's on screen**, **exact actions** (mouse / clicks / typing), **voice-over (TR + EN)**, **why this scene exists**.

> Voice-over is shown in **Turkish** (primary, what you'll say) and **English** (use as subtitles or alternate take). Keep it slightly faster than natural conversation pace — judges watch many submissions.

---

### 🎬 SCENE 1 · 0:00 – 0:08 · The hook

**Screen:** Slide 1 (stadium crowd image, "Language can't wait one second.")

**Actions:** None. Hold on the slide.

**Voice-over (TR):**
> "FIFA 2026. Stadyumda Brezilyalı bir taraftar göğsünü tutarak yere yığılıyor. Yardıma koşan gönüllü Portekizce bilmiyor. Saniyeler can demek."

**Voice-over (EN):**
> "FIFA 2026. A Brazilian fan collapses in the stadium, clutching his chest. The volunteer who reaches him first speaks no Portuguese. Every second matters now."

**Why:** Emotional hook, problem framed in 8 seconds. No screen reading required — judges hear the stakes.

---

### 🎬 SCENE 2 · 0:08 – 0:35 · The product, in one sentence

**Screen:** Cut to Chrome tab 4 — **patient app in Portuguese, mobile view.** Cursor hovers over the first triage question.

**Actions:**
- Show the patient app idle on first triage screen (`Onde está doendo?`).
- Slowly scroll once to reveal the body-map tap-cards and the mic button.
- **Do not** click anything; this is "what the patient sees."

**Voice-over (TR):**
> "MediCase Orchestrator devreye giriyor. Gönüllü stadyumda QR kodu hastanın telefonuna gösteriyor; hastanın telefonunda kendi dilinde, sesli bir triyaj açılıyor. Konuşamıyorsa vücut haritasında ağrıyan yere dokunabiliyor."

**Voice-over (EN):**
> "MediCase Orchestrator steps in. The volunteer shows a QR code; the patient's phone opens a voice triage **in his own language**. If he can't speak, he taps the body map."

**Why:** Show the human surface area first. Most judges will already be sold on the demo just from this 25 seconds.

---

### 🎬 SCENE 3 · 0:35 – 0:50 · Architecture, in 15 seconds

**Screen:** Slide 2 (the 6-agent architecture diagram).

**Actions:** None — let the diagram do the work.

**Voice-over (TR):**
> "Altı agent var. Dört tanesi Python ile yazılmış kodlu agent, ikisi UiPath Agent Builder'da low-code. Hepsini UiPath Maestro orkestre ediyor. Tüm kod Claude Code ile yazıldı — yarışmanın iki bonus puan getiren kategorisi."

**Voice-over (EN):**
> "Six agents. Four are Python coded agents, two are low-code Agent Builder agents, all orchestrated by UiPath Maestro. Every line written with Claude Code — the +2 bonus track."

**Why:** Establishes the technical surface so the next scenes (Maestro canvas + Orchestrator) land instantly.

---

### 🎬 SCENE 4 · 0:50 – 1:35 · UiPath Maestro canvas — the orchestration heart **(longest scene)**

**Screen:** Chrome tab 2 — **UiPath Studio Web, Process.bpmn open.**

**Actions** (slow, deliberate — this is the centerpiece):

1. **(0:50–0:58)** Hold on the whole BPMN flow. Cursor traces left-to-right along the chain:
   `Start → LanguageAgent → TriageAgent → RTSLookupAgent → RoutingAgent → SummaryAgent → ComplianceAgent → End`
2. **(0:58–1:05)** Click on the **TriageAgent (Intake)** node. Right-side Properties panel opens.
   - Point cursor at the **Inputs** section, hover over `symptoms ← [Tt symptoms]` chip, then `pain_scale ← [123 pain_scale]` chip.
3. **(1:05–1:15)** Click on the **RoutingAgent (Stabilization)** node. Inputs visible.
   - Hover over `severity ← [Tt severity]` chip → **say out loud: "this binds directly to TriageAgent's output."**
   - Hover over `symptom_cluster ← [Tt symptom_cluster]` chip.
4. **(1:15–1:22)** Click in canvas blank space → Properties shows the Process. Cursor moves to **left panel → Data Manager → Arguments**.
   - Quickly scroll the list of 9 arguments: `case_id, symptoms, pain_scale, age_band, conditions, medications, lat, lon, location`.
5. **(1:22–1:35)** Cursor goes to the bottom of the canvas — point at **"Validation issues (0)"** badge. Pause one second on it.

**Voice-over (TR):**
> "İşte tasarım. Soldaki Data Manager'da dokuz tane process input argümanı — hasta intake'inin gerçek veri modeli. TriageAgent bu argümanları doğrudan tüketiyor; sonra RoutingAgent, TriageAgent'ın severity ve symptom_cluster çıktılarını alıp uzman seçimi yapıyor. Stage'ler arasında **gerçek veri akıyor**, kısayol yok. Validation: sıfır hata."

**Voice-over (EN):**
> "Here is the design. The Data Manager on the left exposes nine process input arguments — the real data model of patient intake. TriageAgent consumes those directly; RoutingAgent then chains off TriageAgent's severity and symptom\_cluster outputs to pick a specialist. Real data flows between stages — no shortcuts. Validation: zero issues."

**Why:** This is **the** scene that distinguishes us from teams that wired placeholders together. Judges who orchestrate for a living will recognize the chip-by-chip binding as the real thing.

---

### 🎬 SCENE 5 · 1:35 – 1:50 · Agent Builder — the low-code side

**Screen:** Chrome tab 2 — switch to **Solution → Agent → Definition** (TriageAgent definition).

**Actions:**

1. **(1:35–1:42)** Show the **System prompt** field — visible triage classifier prompt (severity / symptom\_cluster / red\_flags).
2. **(1:42–1:48)** Scroll down to **Edit I/O Schema** → quick glance at Inputs (`symptoms*, pain_scale, age_band, conditions`) and Outputs (`severity, symptom_cluster, red_flags`).
3. **(1:48–1:50)** Point at **Temperature: Precise** and **Model: gpt-5.4**.

**Voice-over (TR):**
> "Low-code agent yanı: Agent Builder'da TriageAgent. Sistem promptu hastayı **cardiac, trauma, respiratory** gibi kümelere ayırıyor; çıkışlar tipli — UiPath'in LLM gateway'i, gpt-5.4, sıcaklık precise. Aynı solution içinde hem kod hem low-code, hibrit ekipler için."

**Voice-over (EN):**
> "The low-code side: TriageAgent in Agent Builder. Its system prompt classifies cases into cardiac, trauma, respiratory clusters; outputs are typed; UiPath's LLM gateway, gpt-5.4, precise temperature. Code and low-code in the same solution — built for hybrid teams."

**Why:** Shows we use both UiPath modalities (a track-1 expectation), not just code.

---

### 🎬 SCENE 6 · 1:50 – 2:15 · ⭐ Orchestrator → Latest jobs — the cloud-Successful proof

**Screen:** Chrome tab 3 — **UiPath Orchestrator Overview / Latest jobs table.**

**Actions** (this is the second wow moment — slow down):

1. **(1:50–1:57)** Hold on the **Latest jobs** table. Cursor traces over four rows:
   ```
   medicase-coded-summary | kadikoyilcesat@gmail.com's workspace | Agent (python) | ✅ Successful | …
   medicase-coded-summary | …                                    | Agent (python) | ✅ Successful | …
   medicase-coded-summary | …                                    | Agent (python) | ✅ Successful | …
   medicase-coded-summary | …                                    | Agent (python) | ✅ Successful | …
   ```
2. **(1:57–2:05)** Click the most recent ✅ Successful row → Job Details side-panel opens.
3. **(2:05–2:15)** Switch tab in the side-panel to **Output**. The output JSON shows:
   ```json
   {
     "agent": "summary",
     "result": {
       "rendered_text": "PATIENT HANDOFF - MediCase Orchestrator …",
       "report": { "case_id": "fifa-brazil-…", … }
     }
   }
   ```
   Cursor hovers over `"rendered_text"` so the multi-line handoff string is partially visible.

**Voice-over (TR):**
> "Tasarladık, ama gerçekten çalışıyor mu? UiPath Orchestrator — staging tenant. Latest jobs ekranında dört tane `Agent (python) — Successful` satırı. Birine girince **bulutta üretilmiş gerçek PATIENT HANDOFF kartı**: stadyum sektör 12, göğüs ağrısı, alerji penisilin, Losartan. Tasarım değil — koşmuş çıktı."

**Voice-over (EN):**
> "Designed — but does it actually run? UiPath Orchestrator, staging tenant. Latest jobs shows four `Agent (python) — Successful` rows. Open one: a real PATIENT HANDOFF card, produced in the cloud — stadium sector 12, chest pain, penicillin allergy, Losartan. Not a mockup. Actually ran."

**Why:** This **is the submission**. Everything else is supporting evidence; this row of green checkmarks is the proof. Linger.

---

### 🎬 SCENE 7 · 2:15 – 2:35 · ⭐ Patient app — multi-language (with the RTL flip)

**Screen:** Chrome tab 4 — Patient app in **Portuguese**, mobile view.

**Actions:**

1. **(2:15–2:20)** Quick pan over the Portuguese screen (`Onde está doendo?` etc.). Hover the body-map tap-card.
2. **(2:20–2:27)** **Alt+Tab to Chrome tab 5** — Arabic. **The whole layout flips right-to-left.** Hold for two beats. Hover the tap-card on the right side now.
3. **(2:27–2:32)** Alt+Tab to **tab 6 — Turkish**. Same screen, Turkish text.
4. **(2:32–2:35)** Briefly Alt+Tab to **tab 7 (Spanish), or back to Portuguese** to seal the multi-language point.

**Voice-over (TR):**
> "Beş dil hazır: Portekizce, Arapça, Türkçe, İspanyolca, İngilizce. Arapçaya geçince **sayfa otomatik sağdan sola** akıyor — Hajj 2027 için bunu kodlamak şart, sonradan ekleyemezsin. Kullanıcı hiç ayar yapmıyor; tarayıcı locale'i tespit edip kendi dili açıyor."

**Voice-over (EN):**
> "Five languages live today: Portuguese, Arabic, Turkish, Spanish, English. The moment you switch to Arabic the layout flips right-to-left — for Hajj 2027 you have to code that in, you can't retrofit it. The user sets nothing; we detect browser locale and open in their language."

**Why:** Proves the system is not Portuguese-only and that the team understood RTL is a first-class concern. Judges from the Middle East / South Asia will care a lot.

---

### 🎬 SCENE 8 · 2:35 – 2:48 · Generalization — same platform, different events

**Screen:** Either Slide 2 again or a 3-photo grid (stadium / airport / Hajj crowd).

**Actions:** Static screen.

**Voice-over (TR):**
> "Demo senaryosu FIFA 2026 ama platform aynı. Havalimanı, festival, Hajj 2027, Olimpiyat 2028 — coğrafi argümanlar değişir, akış değişmez. Bu mimari ürün, demo değil."

**Voice-over (EN):**
> "The demo is FIFA 2026 but the platform is the same. Airport, festival, Hajj 2027, Olympics 2028 — geographic arguments change, the flow doesn't. This is a product, not a demo."

**Why:** Reframes the work as a platform (higher valuation in judges' minds) before the CTA.

---

### 🎬 SCENE 9 · 2:48 – 3:00 · CTA + close

**Screen:** Slide 3 — `github.com/dento34/medicase-orchestrator` + "Built with Claude Code + UiPath Maestro".

**Actions:** Hold. Cursor optionally points at the GitHub URL.

**Voice-over (TR):**
> "Kod, dokümantasyon, oturum logları — hepsi GitHub'da. UiPath Maestro ile orkestre edildi, Claude Code ile yazıldı. Teşekkürler."

**Voice-over (EN):**
> "Code, docs, session logs — all on GitHub. Orchestrated with UiPath Maestro, built with Claude Code. Thank you."

**Why:** Clean exit; judge has a URL to click immediately after the video ends.

---

## Total length budget

| Scene | Length | Cumulative |
|---|---|---|
| 1. Hook | 0:08 | 0:08 |
| 2. Patient app idle (PT) | 0:27 | 0:35 |
| 3. Architecture slide | 0:15 | 0:50 |
| 4. **Maestro canvas** | 0:45 | 1:35 |
| 5. Agent Builder | 0:15 | 1:50 |
| 6. **Orchestrator Successful** | 0:25 | 2:15 |
| 7. **Multi-language + RTL** | 0:20 | 2:35 |
| 8. Generalization | 0:13 | 2:48 |
| 9. CTA | 0:12 | 3:00 |

If you run long: trim Scene 5 to 10 sec and Scene 8 to 8 sec.
If you run short: hold Scene 6 (the Orchestrator handoff JSON) longer.

---

## Recording tips

- **One take per scene** with a 2-sec safety pause between scenes. Stitch in CapCut later if needed.
- **Speak slightly faster than natural** — judges are watching at 1x but feel impatient.
- **Mouse moves slowly and intentionally** — judges follow the cursor; jerky movement reads as "unsure."
- **Highlight your cursor.** Windows Settings → Mouse → larger pointer + click animations, or use the recorder's built-in cursor halo.
- **Hide notifications:** Win + A → Focus assist → Alarms only.
- **Read voice-over off a second screen** (phone propped up) so your eyes don't drift off-camera. Practice 2–3 times before recording.
- **Audio matters more than video.** A headset mic beats laptop mic. Re-record the voice-over if the first take has uhms or background noise.

## Backup tactics

- **If the Orchestrator page is slow:** pre-screenshot the Latest jobs panel **and** the OUTPUT JSON, and cut to a frozen frame for Scene 6. Judges accept this; they care about the proof, not the live API.
- **If a patient-app tab loses its mobile view:** Devtools → Toggle device toolbar (Ctrl+Shift+M) → re-pick iPhone 14 Pro.
- **If you fluff a line:** keep going. Re-record only the voice for that segment and overlay it in CapCut. Don't reshoot the whole video.

---

## Checklist (print this and tick as you go)

Before recording:
- [ ] All 9 windows / tabs open in the order above
- [ ] Patient app `serve.py` running on localhost:8000
- [ ] Latest jobs table shows ≥3 Successful rows (refresh)
- [ ] Mic check (record 3 sec, play back)
- [ ] Notifications muted (Focus assist)
- [ ] Slides 1, 2, 3 ready in PowerPoint, presenter mode off

During recording:
- [ ] Scene 1: hold on slide 1, don't rush
- [ ] Scene 4: linger on TriageAgent chips and RoutingAgent chips
- [ ] Scene 6: open the actual Output JSON, don't just stop at the list
- [ ] Scene 7: include the Arabic RTL moment (most underestimated wow)

After recording:
- [ ] Export 1080p mp4
- [ ] Upload to YouTube **as unlisted**
- [ ] Paste the YouTube link into Devpost submission
- [ ] Save the .mp4 locally as `submission/medicase-demo-v1.mp4` (already in .gitignore)

---

## What to do if you only have 60 seconds

Cut to: Scene 1 (5s) → Scene 4 Maestro canvas, no scrolling (25s) → Scene 6 Orchestrator Successful jobs (20s) → Scene 9 CTA (10s).
The 60-second cut is still a complete pitch.
