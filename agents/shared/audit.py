"""Audit hook — auto-log agent invocations to any compliance sink.

Any object with a `log_event(case_id, kind, actor, summary, payload)` method
qualifies as an AuditSink (ComplianceAgent does). Wrap an agent call in the
`audited(...)` context manager and you get automatic
`agent_invoked` / `agent_completed` / `exception_raised` events with timing.

Example:
    with audited(compliance, case_id=cid, actor="language_agent",
                 summary="detect language") as span:
        result = language.detect(req)
        span.note(payload={"language": result.language_code})
"""
from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Any, Iterator, Protocol, runtime_checkable

from .logging import get_logger

logger = get_logger("audit")


@runtime_checkable
class AuditSink(Protocol):
    def log_event(
        self,
        *,
        case_id: str,
        kind: str,
        actor: str,
        summary: str,
        payload: dict | None = None,
    ) -> Any: ...


class _Span:
    """Handle returned by `audited` so the body can attach payload data."""

    def __init__(self) -> None:
        self.payload: dict[str, Any] = {}

    def note(self, **kwargs: Any) -> None:
        """Merge keys into the completion event payload."""
        payload = kwargs.pop("payload", None)
        if payload:
            self.payload.update(payload)
        self.payload.update(kwargs)


@contextmanager
def audited(
    sink: AuditSink | None,
    *,
    case_id: str,
    actor: str,
    summary: str,
) -> Iterator[_Span]:
    """Context manager that emits invoked/completed/exception audit events.

    `sink` may be None (no-op) so agents work standalone in tests/demos.
    """
    span = _Span()
    if sink is None:
        yield span
        return

    t0 = time.time()
    sink.log_event(
        case_id=case_id, kind="agent_invoked", actor=actor, summary=summary
    )
    try:
        yield span
    except Exception as e:
        sink.log_event(
            case_id=case_id,
            kind="exception_raised",
            actor=actor,
            summary=f"{type(e).__name__}: {e}",
            payload={"elapsed_ms": round((time.time() - t0) * 1000)},
        )
        raise
    else:
        span.payload["elapsed_ms"] = round((time.time() - t0) * 1000)
        sink.log_event(
            case_id=case_id,
            kind="agent_completed",
            actor=actor,
            summary=f"{actor} completed: {summary}",
            payload=span.payload,
        )
