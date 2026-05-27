"""ComplianceAgent — coordinates audit logging + anonymized case memory."""
from __future__ import annotations

import os
from datetime import datetime, timezone

from .anonymize import bucket_age, hash_case_id, language_family
from .models import AnonymizedCaseRecord, AuditEvent, AuditEventKind
from .storage import Storage
from ..shared.logging import get_logger

logger = get_logger("compliance_agent")


class ComplianceAgent:
    """Stage 4 helper: write audit events; anonymize and store closed cases."""

    def __init__(self, *, db_path: str | None = None):
        path = (
            db_path
            or _strip_sqlite_prefix(os.getenv("DATABASE_URL", ""))
            or "medicase.db"
        )
        self.storage = Storage(path)
        logger.info(f"ComplianceAgent initialized (db={self.storage.db_path})")

    # ------------------------------------------------------------- audit
    def log_event(
        self,
        *,
        case_id: str,
        kind: AuditEventKind,
        actor: str,
        summary: str,
        payload: dict | None = None,
    ) -> AuditEvent:
        event = AuditEvent(
            case_id=case_id,
            kind=kind,
            actor=actor,
            summary=summary,
            payload=payload or {},
        )
        row_id = self.storage.write_audit(event)
        logger.info(
            f"[{event.kind}] case={case_id} actor={actor}: {summary} "
            f"(audit_id={row_id})"
        )
        return event

    def case_audit_trail(self, case_id: str) -> list[AuditEvent]:
        return self.storage.list_audit(case_id)

    # ------------------------------------------------------- anonymize
    def close_case(
        self,
        *,
        case_id: str,
        opened_at: datetime,
        language_code: str | None,
        age: int | None,
        sex: str | None,
        symptom_cluster: str | None,
        severity: str | None,
        interventions: list[str],
        outcome: str | None,
        event_venue_type: str | None = None,
    ) -> AnonymizedCaseRecord:
        """Record a stripped-down learning record for a closed case."""
        closed_at = datetime.now(timezone.utc)
        duration = int((closed_at - opened_at).total_seconds()) if opened_at else None

        record = AnonymizedCaseRecord(
            case_id_hash=hash_case_id(case_id),
            closed_at=closed_at,
            language_family=language_family(language_code),
            age_band=bucket_age(age),
            sex=sex.lower() if sex else None,
            symptom_cluster=symptom_cluster,
            severity=severity,
            interventions=interventions,
            outcome=outcome,
            duration_seconds=duration,
            event_venue_type=event_venue_type,
        )
        self.storage.upsert_anonymized(record)
        # Also log the close in the audit trail.
        self.log_event(
            case_id=case_id,
            kind="case_closed",
            actor="compliance_agent",
            summary=f"Case closed; anonymized record stored ({record.case_id_hash}).",
            payload={"outcome": outcome, "duration_s": duration},
        )
        return record

    # ------------------------------------------------------ retrieval
    def similar_prior_cases(
        self,
        *,
        symptom_cluster: str | None = None,
        language_code: str | None = None,
        limit: int = 5,
    ) -> list[AnonymizedCaseRecord]:
        """Return prior closed cases with the same cluster + language family.

        Used by Stage 1 to pre-load triage suggestions (the 'learning loop'
        demo moment).
        """
        return self.storage.similar_cases(
            symptom_cluster=symptom_cluster,
            language_family=language_family(language_code),
            limit=limit,
        )


def _strip_sqlite_prefix(url: str) -> str | None:
    if not url:
        return None
    if url.startswith("sqlite:///"):
        return url[len("sqlite:///") :]
    if url.startswith("sqlite://"):
        return url[len("sqlite://") :]
    return url
