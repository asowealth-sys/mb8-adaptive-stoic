from __future__ import annotations


def dominance_score(features: dict[str, float | str]) -> float:
    strength_gap = float(features["home_strength"]) - float(features["away_strength"])
    score = (
        50
        + strength_gap * 0.35
        + float(features["xg_gap"]) * 8
        + float(features["elo_gap"]) / 25
        + float(features["momentum"]) * 12
        + float(features["goal_pressure"]) * 6
    )
    return max(0.0, min(100.0, round(score, 2)))

