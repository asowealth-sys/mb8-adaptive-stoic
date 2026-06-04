from __future__ import annotations

import pandas as pd
import pytest


@pytest.fixture
def valid_row(**overrides: object) -> dict[str, object]:
    def _valid_row(**inner_overrides: object) -> dict[str, object]:
        row: dict[str, object] = {
            "home_team": "Atlas FC",
            "away_team": "River Town",
            "league": "Premier League",
            "competition_type": "League",
            "kickoff": "2026-06-08T18:00:00Z",
            "market": "O1.5",
            "odds": 1.42,
            "home_strength": 72,
            "away_strength": 48,
            "xg_gap": 1.2,
            "elo_gap": 180,
            "momentum": 0.72,
            "goal_pressure": 0.75,
            "chaos_index": 0.18,
            "volatility": 0.24,
            "draw_risk": 0.28,
            "market_drift": 0.10,
            "lineup_risk": 0.12,
            "pressure_index": 0.20,
            "tactical_freeze": 0.00,
            "emotional_chaos": 0.00,
            "motivation_distortion": 0.00,
            "draw_acceptance": 0.10,
        }
        row.update(inner_overrides)
        return row

    return _valid_row


@pytest.fixture
def frame(*rows: dict[str, object]) -> pd.DataFrame:
    def _frame(*inner_rows: dict[str, object]) -> pd.DataFrame:
        return pd.DataFrame(list(inner_rows))

    return _frame
