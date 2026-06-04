from __future__ import annotations

from uuid import uuid4

from mb8_adaptive_stoic.schemas.audit_schema import AuditTrail


def new_audit_trail() -> AuditTrail:
    return AuditTrail(audit_trail_id=f"MB8-{uuid4().hex[:12].upper()}")


def reject_candidate(candidate: dict[str, object], layer: str, reason: str) -> dict[str, object]:
    candidate["final_decision"] = "REJECT"
    candidate["failed_layer"] = layer
    candidate["reason"] = reason
    candidate["rejection_reason"] = reason
    candidate.setdefault("risk_flags", [])
    audit = candidate.get("audit")
    if audit:
        audit.add(layer, "REJECT", reason)
    return candidate

