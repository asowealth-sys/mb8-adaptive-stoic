from __future__ import annotations

import pandas as pd

from mb8_adaptive_stoic.app.config import SETTINGS


def missing_required_columns(df: pd.DataFrame) -> list[str]:
    return [column for column in SETTINGS.required_columns if column not in df.columns]


def validate_required_columns(df: pd.DataFrame) -> None:
    missing = missing_required_columns(df)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

