# Patient Mini Web App

QR-launched, in-language, voice-first triage that opens on the patient's
phone. Zero build, zero framework — pure HTML + vanilla JS using the
browser-native **Web Speech API** (TTS + STT). Deploys as a static site.

## Why no framework

For a single-screen emergency intake that must work on any phone, the
browser already provides everything: speech synthesis, speech recognition,
fetch. A React/Next bundle would only add weight and failure surface. This
app loads instantly and degrades gracefully when speech APIs are missing.

## How it works

Opened via QR code:

```
https://<host>/?case=<case_id>&lang=<iso639-1>
```

1. **Reassurance** screen in the patient's language (spoken + shown)
2. **Triage questions** one at a time:
   - Spoken aloud (TTS) + shown large
   - Answer by voice (STT) **or** tap-cards
   - "Hear again" button
3. **Tap-card fallbacks** for non-verbal / low-literacy / noisy stadium:
   - Body map (head / chest / belly / arm / leg / back)
   - Pain scale 0–10 (color-graded)
4. **Done** screen; answers POSTed to the case API (best-effort)

## Privacy

- Nothing persisted on device (in-memory session only)
- Speech cancelled on page unload
- Answers go only to the on-site medical team's case API

## Supported languages (offline content)

English, Portuguese, Spanish, Arabic (RTL), Turkish. Falls back to English.
In production, the **LanguageAgent** supplies translations on the fly for
any detected language; the static bundle here covers the demo + common
World-Cup languages so it works with no backend.

## Run locally

```bash
python patient-app/serve.py
# open http://localhost:5173/?case=demo-001&lang=pt
```

Voice features need a Chromium-based browser (Chrome/Edge) and mic
permission. Tap-cards work everywhere.

## Deploy (Vercel)

```bash
cd patient-app
vercel deploy --prod
```

`vercel.json` sets `outputDirectory: public` and the
`Permissions-Policy: microphone=(self)` header.

## Wiring to the backend

Set `window.CASE_API_URL` (or it defaults to localhost during dev). The
app POSTs:

```
POST {CASE_API}/api/case/{case_id}/intake
{ "case_id", "language", "answers": [...], "submitted_at" }
```

The case API (a UiPath API Workflow or a thin gateway) forwards this into
the Maestro Case as the Stage 1 intake payload.
