# 2026-05-27 — ComplianceAgent first scaffold

## Goal

Build the third Coded Agent: **ComplianceAgent** for Stage 4 (Post-incident).
Two distinct streams maintained side by side:

1. **Audit log** — append-only, fully identified, regulator-friendly
2. **Anonymized learning store** — PII stripped, fuels next-case suggestions

The same agent also exposes the *learning loop* query the demo video
opens on: "given the cluster + language family, what prior cases are
similar?"

## Tool: Claude Code (Anthropic)

Third agent in this scaffold session. Bonus-point criteria satisfied
the same way: tool documented, contribution evident, output meaningfully
integrated (the agent runs end-to-end in a real smoke test that proves
the learning-loop demo moment is wired up).

## What was produced

| Path | Purpose |
|---|---|
| `agents/compliance_agent/__init__.py` | Package marker + exports |
| `agents/compliance_agent/models.py` | `AuditEvent`, `AnonymizedCaseRecord`, kind enum |
| `agents/compliance_agent/anonymize.py` | `hash_case_id`, `bucket_age`, `language_family` |
| `agents/compliance_agent/storage.py` | SQLite-backed Storage layer (2 tables, indexed) |
| `agents/compliance_agent/agent.py` | `ComplianceAgent` with `log_event`, `close_case`, `similar_prior_cases` |
| `agents/compliance_agent/tests/test_smoke.py` | Full lifecycle smoke test, throwaway tempdir DB |

## Key design decisions

1. **Two tables, never joined.** `audit_events` is regulator-facing,
   identified, retention-locked. `anonymized_case_record` is
   ops-facing, PII stripped. They share a hash, not a key — by design.
2. **Bucketed transforms only for anonymization.** No randomized noise;
   every reduction (age band, language family) is auditable.
3. **SHA-256(case_id)[:16] for the case hash** — irreversible, stable.
4. **Compliance hook into every agent** — the lifecycle is *opened →
   invoked → completed → human-decided → stage-transitioned → closed*,
   with `log_event` callable from any agent.
5. **`similar_prior_cases()` is the demo's learning-loop primitive** —
   filters on `symptom_cluster + language_family`, ordered by recency.
   In production this gets replaced by an embedding-based vector search
   (Context Grounding API), but the contract stays the same.

## Smoke test result

```
audit trail for case-2026-05-27-001 (6 events):
  case_opened       volunteer:@sara
  agent_invoked     language_agent       (Portuguese 0.92)
  external_api_called rts_lookup_agent   (2 AEDs, 9 min ETA)
  human_decision    medic:@dr_emre       (nitro administered)
  stage_transition  maestro              (Stabilization -> Handoff)
  case_closed       compliance_agent

anonymized record:
  case_id_hash = 8ecbb09cbcf055ea
  language_family = indo-european
  age_band = 30-44
  symptom_cluster = cardiac
  outcome = transported

learning loop:
  3 prior cardiac/Portuguese cases returned, age bands varied.

All assertions pass.
```

## Commit reference

`<pending>` — to be linked.

## Open follow-ups

- Wire the audit hook into LanguageAgent and RTSLookupAgent so every
  invocation auto-logs (currently the demo test logs manually).
- Replace `similar_prior_cases` SQL with UiPath Context Grounding API
  embeddings once Labs has it provisioned.
- Add retention policy for `audit_events` per the deployment region's
  data-protection rules.

## Verification

```bash
.venv/Scripts/python.exe agents/compliance_agent/tests/test_smoke.py
```
