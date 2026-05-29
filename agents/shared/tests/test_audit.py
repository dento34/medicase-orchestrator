"""Test the audit hook against a real ComplianceAgent sink."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from agents.compliance_agent import ComplianceAgent  # noqa: E402
from agents.shared.audit import audited  # noqa: E402
from agents.shared.logging import get_logger  # noqa: E402

logger = get_logger("audit_test")


def main() -> int:
    print("=" * 70)
    print("audit hook smoke test")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmp:
        sink = ComplianceAgent(db_path=str(Path(tmp) / "audit.db"))
        cid = "case-audit-001"

        # happy path
        with audited(sink, case_id=cid, actor="language_agent",
                     summary="detect language") as span:
            span.note(payload={"language": "pt", "confidence": 0.92})

        # exception path
        try:
            with audited(sink, case_id=cid, actor="rts_lookup_agent",
                         summary="lookup AEDs"):
                raise RuntimeError("Overpass timed out")
        except RuntimeError:
            pass  # expected; the hook re-raises

        # None sink → no-op, must not crash
        with audited(None, case_id=cid, actor="noop", summary="standalone"):
            pass

        trail = sink.case_audit_trail(cid)
        print(f"\naudit events recorded: {len(trail)}")
        for ev in trail:
            extra = ev.payload.get("elapsed_ms")
            print(f"  [{ev.kind:<18}] {ev.actor:<18} {ev.summary} "
                  f"(elapsed_ms={extra})")

        kinds = [ev.kind for ev in trail]
        assert kinds == [
            "agent_invoked",
            "agent_completed",
            "agent_invoked",
            "exception_raised",
        ], f"unexpected event sequence: {kinds}"
        # completion carries the noted payload
        completed = trail[1]
        assert completed.payload.get("language") == "pt"
        assert "elapsed_ms" in completed.payload

    print("\n[OK] audit hook smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
