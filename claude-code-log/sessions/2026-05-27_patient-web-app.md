# 2026-05-27 — Patient mini web app

## Goal

Build the patient-side surface: a QR-launched, in-language, voice-first
triage that runs on any phone with no install and no backend dependency.

## Tool: Claude Code (Anthropic)

Scaffolded the whole static app in this session.

## What was produced

| Path | Purpose |
|---|---|
| `patient-app/public/index.html` | Single-screen app shell |
| `patient-app/public/styles.css` | Mobile-first, large tap targets, pulse animation |
| `patient-app/public/triage-content.js` | Pre-translated triage content (en/pt/es/ar/tr) + body emoji |
| `patient-app/public/app.js` | Triage flow, Web Speech API (TTS+STT), tap-card fallback, intake POST |
| `patient-app/serve.py` | Stdlib static dev server |
| `patient-app/vercel.json` | Static deploy config + mic permission header |

## Key design decisions

1. **No framework.** Browser-native Web Speech API covers TTS + STT;
   a React/Next bundle would only add weight and a failure surface for a
   single-screen emergency intake. Loads instantly, degrades gracefully.
2. **Voice-first, tap-card fallback.** Each question is spoken + shown;
   answer by voice OR tap. Body map + 0–10 color pain scale work for
   non-verbal, low-literacy, or loud-stadium situations.
3. **RTL support** for Arabic (sets `dir="rtl"`).
4. **Privacy by construction** — in-memory only, speech cancelled on
   unload, answers go only to the case API.
5. **Zero-backend demo** — if no case API is reachable, the intake
   payload is logged to console + `window.__lastIntake` so a demo
   screen-recording still shows the captured data.

## How it connects to the pipeline

Opened via `?case=<id>&lang=<code>` (the QR the Maestro Case generates at
intake). On completion it POSTs to
`{CASE_API}/api/case/{case_id}/intake`, which a UiPath API Workflow
forwards into the Maestro Case as the Stage 1 payload — the same structured
data the LanguageAgent parses.

## Verification

```bash
python patient-app/serve.py
# open http://localhost:5173/?case=demo-001&lang=pt
node --check patient-app/public/app.js   # syntax OK
```

Validated: JS parses, 5 languages load, Arabic RTL flag present.

## Commit reference

`<pending>` — to be linked.

## Follow-ups

- Wire `window.CASE_API_URL` to the real UiPath API Workflow endpoint
- Optionally fetch live translations from LanguageAgent for languages
  outside the bundled set
