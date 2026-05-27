# Claude Code Session Log

This folder is **evidence for the UiPath for Coding Agents bonus points** (up to +2 in judging).

Per the hackathon rules:

> "To qualify for bonus points, participants must clearly document in their Devpost project description or GitHub README: (a) which coding agent tool or tools were used; (b) how the coding agent contributed to the solution; and (c) that the coding agent output is meaningfully integrated into the solution, not merely referenced."

> "Evidence must include at least one of the following: a prompt log or session export, screenshots of the coding agent interaction, a dedicated section in the README describing the coding agent's role in the build, or equivalent documentation that allows the reviewer to independently verify the claim."

## What goes here

| Subfolder | What |
|---|---|
| `sessions/` | Cleaned, redacted Claude Code session exports — one file per major build session |
| `screenshots/` | Screenshots of the Claude Code terminal during key build moments |
| `prompts/` | Notable prompts that produced agent scaffolds, integration glue, or refactors |
| `summaries/` | One-paragraph plain-English notes: what we asked, what Code produced, what we kept |

## Naming convention

`YYYY-MM-DD_<agent-or-area>_<session-summary>.md`

Examples:
- `2026-05-30_triage-agent_first-scaffold.md`
- `2026-06-12_rts-lookup_crewai-integration.md`
- `2026-06-20_compliance-agent_audit-log-design.md`

## What to capture in each session log

1. **Date + duration**
2. **Goal** — what we wanted to produce
3. **Inputs to Claude Code** — the prompt(s), in full
4. **Output summary** — what Claude Code produced (don't paste 500 lines of code; link to commit)
5. **What we kept vs. modified** — honest engineering note
6. **Commit hash(es)** — where the output landed in the codebase

## Don't include

- Real PII / patient data (we don't have any anyway; demo data is synthetic)
- API keys (they should never be in prompts; double-check before exporting)
- UiPath proprietary materials beyond what the hackathon rules permit sharing

## How this maps to bonus point scoring

| Score | Criteria | Our approach |
|---|---|---|
| 2 pts | Clear documentation + verifiable evidence + meaningfully integrated | This folder + README's "Claude Code" section + commits referenced from session logs |
| 1 pt | Partial documentation | Avoid by being thorough |
| 0 pts | Insufficient documentation | Avoid by maintaining this folder weekly |

## Cadence

Write one session summary per significant Claude Code interaction. Aim for at least 5–8 documented sessions by submission deadline.

Update the table below as we go:

| # | Date | Session file | What | Commit |
|---|---|---|---|---|
| 1 | 2026-05-27 | [language-agent first scaffold](sessions/2026-05-27_language-agent_first-scaffold.md) | Built LanguageAgent end-to-end: models, prompts, LLM abstraction, mock+real smoke test | [`52b49ae`](https://github.com/dento34/medicase-orchestrator/commit/52b49ae) |
| 2 | TBD | — | — | — |
| 3 | TBD | — | — | — |
