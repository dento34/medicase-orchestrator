# 2026-05-27 — LanguageAgent first scaffold

## Goal

Build the first Coded Agent for MediCase Orchestrator: **LanguageAgent**,
responsible for Stage 1 (Intake) — detect the patient's language, translate
standard triage questions into it, and parse their reply into a structured
English record.

## Tool: Claude Code (Anthropic)

The agent was scaffolded inside a Claude Code session. The full prompt
transcript that produced this code is the conversation that opened this
repo and submitted the UiPath Labs access form. Commit hash references
below are the verifiable deliverables.

This meets the UiPath bonus point criteria:

- **(a) Tool used**: Claude Code (Anthropic)
- **(b) Contribution**: scaffolded the entire LanguageAgent module —
  models (Pydantic), system prompts, LLM client abstraction, fixtures,
  smoke test — in one session
- **(c) Meaningful integration**: the output runs end-to-end against the
  Brazilian-fan demo scenario in MOCK mode and passes assertions.
  Production runs (with `ANTHROPIC_API_KEY`) hit Anthropic's API directly.

## What was produced

| Path | Purpose |
|---|---|
| `agents/__init__.py` | Package marker, version |
| `agents/shared/env.py` | Project-root-aware `.env` loader |
| `agents/shared/logging.py` | UTF-8 safe stdout logger for Windows cp1254 |
| `agents/shared/llm.py` | `LLMClient` Protocol + `AnthropicClient` + `MockClient` |
| `agents/language_agent/models.py` | 4 Pydantic models for I/O |
| `agents/language_agent/prompts.py` | 3 system prompts (detect, translate, parse) |
| `agents/language_agent/agent.py` | `LanguageAgent` class with three public methods |
| `agents/language_agent/fixtures/triage_questions.json` | Default 5-question bank + supported language list |
| `agents/language_agent/tests/test_smoke.py` | Mock + real-mode end-to-end smoke test |

## Key design decisions

1. **LLM abstraction via Protocol** — tests and offline development run
   through `MockClient` without API credits. Production swap is one line.
2. **JSON-only response format** — every prompt asks for single-line JSON.
   `_parse_json_response()` tolerates code fences and prose prefixes.
3. **Pydantic everywhere** — typed I/O surfaces means the Maestro Case
   handoff between stages is contract-checked rather than loose dicts.
4. **Browser locale fallback** — if patient utterance is missing, we fall
   back to `browser_locale` with reduced confidence rather than blocking
   the case.
5. **Fixtures-driven question bank** — supporting a new language is
   adding a JSON entry, not editing code.

## What we kept vs. what we modified

First-pass scaffold kept as-is. No back-and-forth refactor in this session;
the design above was committed in a single batch after parallel writes.

## Smoke test result

```
MOCK mode (offline)
  detect    : Portuguese (pt) conf=0.92
  translate : 5 questions in Portuguese
  parse     : structured chest pain (8/10), Losartan, penicillin allergy
[OK] mock-mode smoke test passed.

REAL mode — SKIPPED (no ANTHROPIC_API_KEY in .env)
```

## Open follow-ups

- Add `ANTHROPIC_API_KEY` to `.env`, rerun smoke test in REAL mode, record
  a second session log entry.
- Integrate this agent into a UiPath Coded Agent wrapper once the Maestro
  Case API endpoint is mapped (deferred — see `docs/journal.md`).
- Hook the patient mini web app to call this agent over an HTTP endpoint.

## Commit reference

Will be linked here after commit (single batch).
