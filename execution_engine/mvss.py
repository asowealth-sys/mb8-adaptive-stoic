from __future__ import annotations


def mvss_rating(dominance: float, pgce: float, behavior_flag_count: int) -> str:
    if dominance >= 70 and pgce <= 0.38 and behavior_flag_count == 0:
        return "STRONG"
    if dominance >= 54 and pgce <= 0.62 and behavior_flag_count <= 2:
        return "MODERATE"
    return "FRAGILE"

