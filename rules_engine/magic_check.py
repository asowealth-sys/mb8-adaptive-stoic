from __future__ import annotations

from app.config import SETTINGS


REQUIRED_PREVIOUS_LAYERS = (
    "FEATURE_ENGINEERING_LAYER",
    "ECOSYSTEM_ENGINE",
    "DOMINANCE_AND_STABILITY_LAYER",
    "BEHAVIORAL_AI_LAYER",
    "PGCE_RISK_ENGINE",
    "MARKET_SELECTION_ENGINE",
    "MVSS_SCORING",
    "CDC",
    "STOIC_SLIP_SCORER",
)


def magic_check(candidate: dict[str, object]) -> tuple[str, str]:
    audit = candidate.get("audit")
    if audit is None or not getattr(audit, "audit_trail_id", ""):
        return "REJECT", "Magic Check rejected: missing audit trail"
    completed = set(audit.completed_layers)
    missing_layers = [layer for layer in REQUIRED_PREVIOUS_LAYERS if layer not in completed]
    if missing_layers:
        return "REJECT", f"Magic Check rejected: incomplete pipeline ({', '.join(missing_layers)})"
    if candidate.get("excluded_reason"):
        return "REJECT", "Magic Check rejected: SRL/Friendly detected"
    if float(candidate.get("cdc_risk", 1.0)) > SETTINGS.max_cdc_risk:
        return "REJECT", "Magic Check rejected: CDC risk too high"
    if candidate.get("mvss_rating") == "FRAGILE":
        return "REJECT", "Magic Check rejected: MVSS is FRAGILE"
    if float(candidate.get("stoic_score", 0.0)) < SETTINGS.stoic_score_threshold:
        return "REJECT", f"Magic Check rejected: STOIC Score below {SETTINGS.stoic_score_threshold}"
    if candidate.get("cdc_status") != "PASS":
        return "REJECT", "Magic Check rejected: final slip did not pass CDC"
    return "PASS", "Magic Check passed as final non-bypassable gate"

