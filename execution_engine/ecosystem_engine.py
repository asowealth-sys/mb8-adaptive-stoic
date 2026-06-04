from __future__ import annotations

import pandas as pd


def classify_ecosystem(row: pd.Series) -> tuple[str, float]:
    total_goal_signal = float(row.get("goal_pressure", 0.55))
    volatility = float(row.get("volatility", 0.35))
    draw_risk = float(row.get("draw_risk", 0.35))
    if volatility >= 0.65 or total_goal_signal >= 0.70:
        return "EXPANSION", 0.76
    if draw_risk >= 0.58 or total_goal_signal <= 0.42:
        return "COMPRESSION", 0.60
    return "SITUATIONAL COMPRESSION", 0.68

