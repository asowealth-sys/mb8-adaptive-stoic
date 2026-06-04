from __future__ import annotations

import pandas as pd


def normalize_odds(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    normalized["odds"] = pd.to_numeric(normalized.get("odds"), errors="coerce")
    return normalized

