"""ComplianceAgent — Stage 4 (Post-incident): audit log + anonymized memory.

Maintains two distinct data streams:

1. **Audit log** — immutable, fully-identified, retention per regulation.
   Every agent invocation, every human decision, every data access goes here.

2. **Anonymized learning store** — PII stripped, structured signal kept.
   Embeddings of these power next-case triage suggestions.
"""
from .agent import ComplianceAgent
from .models import (
    AuditEvent,
    AnonymizedCaseRecord,
    AuditEventKind,
)

__all__ = [
    "ComplianceAgent",
    "AuditEvent",
    "AnonymizedCaseRecord",
    "AuditEventKind",
]
