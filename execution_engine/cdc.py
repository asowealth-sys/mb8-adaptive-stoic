from __future__ import annotations

from collections import Counter


def item_cdc_score(ecosystem_type: str, risk_flags: list[str]) -> float:
    base = {
        "EXPANSION": 0.42,
        "SITUATIONAL COMPRESSION": 0.35,
        "COMPRESSION": 0.46,
    }.get(ecosystem_type, 0.50)
    return round(min(1.0, base + len(risk_flags) * 0.08), 3)


def apply_cdc_control(candidates: list[dict[str, object]], max_risk: float) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    kept: list[dict[str, object]] = []
    rejected: list[dict[str, object]] = []
    ecosystem_counts: Counter[str] = Counter()

    for candidate in sorted(candidates, key=lambda item: float(item["stoic_score"]), reverse=True):
        ecosystem = str(candidate["ecosystem_type"])
        cdc_risk = float(candidate["cdc_risk"])
        correlated = ecosystem_counts[ecosystem] >= 2
        expansion_dense = ecosystem == "EXPANSION" and ecosystem_counts[ecosystem] >= 1
        freeze_dense = "tactical_freeze_detected" in candidate["risk_flags"] and any(
            "tactical_freeze_detected" in item["risk_flags"] for item in kept
        )
        if cdc_risk > max_risk or correlated or expansion_dense or freeze_dense:
            reason = "CDC correlation risk too high"
            candidate["final_decision"] = "REJECT"
            candidate["failed_layer"] = "CDC"
            candidate["reason"] = reason
            candidate["rejection_reason"] = reason
            rejected.append(candidate)
            continue
        candidate["cdc_status"] = "PASS"
        kept.append(candidate)
        ecosystem_counts[ecosystem] += 1
    return kept, rejected

