from __future__ import annotations

import pandas as pd


def coerce_numeric(row: pd.Series, key: str, default: float) -> float:
    try:
        value = float(row.get(key, default))
    except (TypeError, ValueError):
        return default
    return default if pd.isna(value) else value


def profile_match(row: pd.Series) -> dict[str, float | str]:
    home_strength = coerce_numeric(row, "home_strength", 55)
    away_strength = coerce_numeric(row, "away_strength", 45)
    xg_gap = coerce_numeric(row, "xg_gap", (home_strength - away_strength) / 20)
    elo_gap = coerce_numeric(row, "elo_gap", (home_strength - away_strength) * 8)
    momentum = coerce_numeric(row, "momentum", 0.55)
    goal_pressure = coerce_numeric(row, "goal_pressure", 0.55)
    return {
        "home_strength": home_strength,
        "away_strength": away_strength,
        "xg_gap": xg_gap,
        "elo_gap": elo_gap,
        "momentum": momentum,
        "goal_pressure": goal_pressure,
        "match": str(row.get("match", "")),
        "league": str(row.get("league", "")),
    }

