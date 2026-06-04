from __future__ import annotations

import pandas as pd


ALLOWED_MARKETS = {"O1.5", "U3.5", "WIN", "DNB", "SAFETY"}


def select_market(row: pd.Series, dominance: float, pgce: float) -> tuple[str, str | None]:
    market = str(row.get("market", "")).strip().upper()
    if market in {"OVER 1.5", "OVER_1.5"}:
        market = "O1.5"
    if market in {"UNDER 3.5", "UNDER_3.5"}:
        market = "U3.5"
    if market not in ALLOWED_MARKETS:
        return market or "UNKNOWN", "Unsupported market"
    if market == "WIN" and dominance < 58:
        return market, "Win market requires stronger dominance"
    if market == "DNB" and pgce > 0.62:
        return market, "DNB blocked by high PGCE risk"
    return market, None

