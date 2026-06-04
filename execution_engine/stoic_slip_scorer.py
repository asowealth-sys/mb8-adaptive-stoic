from __future__ import annotations


def stoic_score(dominance: float, mvss: str, ecosystem_quality: float, pgce: float, cdc_risk: float) -> float:
    mvss_bonus = {"STRONG": 14, "MODERATE": 7, "FRAGILE": -18}[mvss]
    raw = dominance * 0.55 + ecosystem_quality * 20 + (1 - pgce) * 18 + (1 - cdc_risk) * 12 + mvss_bonus
    return round(max(0.0, min(100.0, raw)), 2)


def survivability_rating(score: float) -> str:
    if score >= 82:
        return "HIGH"
    if score >= 70:
        return "MEDIUM"
    return "LOW"


def slip_label(score: float) -> str:
    if score >= 86:
        return "A-STOIC"
    if score >= 76:
        return "B-STOIC"
    return "WATCHLIST"

