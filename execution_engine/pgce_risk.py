from __future__ import annotations

import pandas as pd


def pgce_score(row: pd.Series) -> float:
    values = [
        float(row.get("chaos_index", 0.25)),
        float(row.get("volatility", 0.35)),
        float(row.get("draw_risk", 0.35)),
        float(row.get("market_drift", 0.20)),
        float(row.get("lineup_risk", 0.20)),
    ]
    return round(sum(values) / len(values), 3)

