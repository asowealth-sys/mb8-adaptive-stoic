from __future__ import annotations

from mb8_adaptive_stoic.app.config import SETTINGS


def dominance_gate(score: float) -> tuple[bool, str]:
    if score < SETTINGS.dominance_pass_threshold:
        return False, f"Dominance score {score} below threshold {SETTINGS.dominance_pass_threshold}"
    return True, "Dominance and stability threshold met"

