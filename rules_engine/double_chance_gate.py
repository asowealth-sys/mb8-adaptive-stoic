from __future__ import annotations


def double_chance_integrity_gate(market_pick: str, draw_risk: float) -> tuple[bool, str]:
    if market_pick in {"WIN", "DNB"} and draw_risk >= 0.66:
        return False, "Double Chance Integrity Gate blocked win-side market under high draw risk"
    return True, "Double Chance Integrity Gate passed"

