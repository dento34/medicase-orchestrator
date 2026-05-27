"""SQLite-backed storage for ComplianceAgent.

Two tables:
  - audit_events           : append-only, never deleted, fully identified
  - anonymized_case_record : one row per closed case, PII stripped

For the hackathon a single SQLite file is sufficient. In production this
would be Postgres + a write-once-read-many policy on the audit table.
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .models import AnonymizedCaseRecord, AuditEvent


SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_events (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id       TEXT NOT NULL,
    kind          TEXT NOT NULL,
    actor         TEXT NOT NULL,
    summary       TEXT NOT NULL,
    payload_json  TEXT NOT NULL DEFAULT '{}',
    ts_utc        TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_audit_case ON audit_events(case_id);
CREATE INDEX IF NOT EXISTS ix_audit_ts ON audit_events(ts_utc);

CREATE TABLE IF NOT EXISTS anonymized_case_record (
    case_id_hash      TEXT PRIMARY KEY,
    closed_at         TEXT NOT NULL,
    language_family   TEXT,
    age_band          TEXT,
    sex               TEXT,
    symptom_cluster   TEXT,
    severity          TEXT,
    interventions     TEXT NOT NULL DEFAULT '[]',
    outcome           TEXT,
    duration_seconds  INTEGER,
    event_venue_type  TEXT
);
CREATE INDEX IF NOT EXISTS ix_anon_cluster
    ON anonymized_case_record(symptom_cluster);
CREATE INDEX IF NOT EXISTS ix_anon_lang
    ON anonymized_case_record(language_family);
"""


class Storage:
    def __init__(self, db_path: str | Path = "medicase.db"):
        self.db_path = Path(db_path)
        self._init_schema()

    def _init_schema(self) -> None:
        with self._conn() as cx:
            for stmt in SCHEMA.split(";"):
                s = stmt.strip()
                if s:
                    cx.execute(s)

    @contextmanager
    def _conn(self) -> Iterator[sqlite3.Connection]:
        cx = sqlite3.connect(self.db_path)
        cx.row_factory = sqlite3.Row
        try:
            yield cx
            cx.commit()
        finally:
            cx.close()

    # -------------------------------------------------- audit
    def write_audit(self, event: AuditEvent) -> int:
        with self._conn() as cx:
            cur = cx.execute(
                """
                INSERT INTO audit_events
                    (case_id, kind, actor, summary, payload_json, ts_utc)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event.case_id,
                    event.kind,
                    event.actor,
                    event.summary,
                    json.dumps(event.payload, default=str, ensure_ascii=False),
                    event.timestamp.isoformat(),
                ),
            )
            return int(cur.lastrowid)

    def list_audit(self, case_id: str) -> list[AuditEvent]:
        with self._conn() as cx:
            rows = cx.execute(
                "SELECT * FROM audit_events WHERE case_id = ? ORDER BY id ASC",
                (case_id,),
            ).fetchall()
        return [
            AuditEvent(
                case_id=r["case_id"],
                kind=r["kind"],
                actor=r["actor"],
                summary=r["summary"],
                payload=json.loads(r["payload_json"] or "{}"),
                timestamp=r["ts_utc"],
            )
            for r in rows
        ]

    # ----------------------------------------------- anonymized
    def upsert_anonymized(self, rec: AnonymizedCaseRecord) -> None:
        with self._conn() as cx:
            cx.execute(
                """
                INSERT INTO anonymized_case_record (
                    case_id_hash, closed_at, language_family, age_band, sex,
                    symptom_cluster, severity, interventions, outcome,
                    duration_seconds, event_venue_type
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(case_id_hash) DO UPDATE SET
                    closed_at        = excluded.closed_at,
                    language_family  = excluded.language_family,
                    age_band         = excluded.age_band,
                    sex              = excluded.sex,
                    symptom_cluster  = excluded.symptom_cluster,
                    severity         = excluded.severity,
                    interventions    = excluded.interventions,
                    outcome          = excluded.outcome,
                    duration_seconds = excluded.duration_seconds,
                    event_venue_type = excluded.event_venue_type
                """,
                (
                    rec.case_id_hash,
                    rec.closed_at.isoformat(),
                    rec.language_family,
                    rec.age_band,
                    rec.sex,
                    rec.symptom_cluster,
                    rec.severity,
                    json.dumps(rec.interventions, ensure_ascii=False),
                    rec.outcome,
                    rec.duration_seconds,
                    rec.event_venue_type,
                ),
            )

    def similar_cases(
        self,
        *,
        symptom_cluster: str | None = None,
        language_family: str | None = None,
        limit: int = 5,
    ) -> list[AnonymizedCaseRecord]:
        sql = "SELECT * FROM anonymized_case_record WHERE 1=1"
        params: list = []
        if symptom_cluster:
            sql += " AND symptom_cluster = ?"
            params.append(symptom_cluster)
        if language_family:
            sql += " AND language_family = ?"
            params.append(language_family)
        sql += " ORDER BY closed_at DESC LIMIT ?"
        params.append(limit)

        with self._conn() as cx:
            rows = cx.execute(sql, params).fetchall()

        return [
            AnonymizedCaseRecord(
                case_id_hash=r["case_id_hash"],
                closed_at=r["closed_at"],
                language_family=r["language_family"],
                age_band=r["age_band"],
                sex=r["sex"],
                symptom_cluster=r["symptom_cluster"],
                severity=r["severity"],
                interventions=json.loads(r["interventions"] or "[]"),
                outcome=r["outcome"],
                duration_seconds=r["duration_seconds"],
                event_venue_type=r["event_venue_type"],
            )
            for r in rows
        ]
