from __future__ import annotations

import re

import pandas as pd

from app.config import SETTINGS
from data_layer.normalize_odds import normalize_odds


SRL_PATTERN = re.compile(r"\b(srl|simulation|simulated reality|virtual)\b", re.IGNORECASE)
FRIENDLY_PATTERN = re.compile(r"\b(friendlies|friendly|club friendly|international friendly)\b", re.IGNORECASE)


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned.columns = [str(column).strip().lower().replace(" ", "_") for column in cleaned.columns]
    if "match" not in cleaned.columns and {"home_team", "away_team"}.issubset(cleaned.columns):
        cleaned["match"] = cleaned["home_team"].astype(str).str.strip() + " vs " + cleaned["away_team"].astype(str).str.strip()
    if "kickoff" not in cleaned.columns:
        cleaned["kickoff"] = ""
    return cleaned


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    subset = [column for column in SETTINGS.duplicate_subset if column in df.columns]
    return df.drop_duplicates(subset=subset or None).reset_index(drop=True)


def exclusion_reason(row: pd.Series) -> str | None:
    text = " ".join(str(row.get(column, "")) for column in ("league", "competition_type", "match", "source"))
    if SRL_PATTERN.search(text):
        return "SRL or simulated match detected"
    if FRIENDLY_PATTERN.search(text):
        return "Friendly match detected"
    return None


def split_excluded_matches(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if df.empty:
        return df.copy(), df.copy()
    marked = df.copy()
    marked["exclusion_reason"] = marked.apply(exclusion_reason, axis=1)
    excluded = marked[marked["exclusion_reason"].notna()].reset_index(drop=True)
    kept = marked[marked["exclusion_reason"].isna()].drop(columns=["exclusion_reason"]).reset_index(drop=True)
    return kept, excluded


def clean_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cleaned = standardize_columns(df)
    cleaned = normalize_odds(cleaned)
    cleaned = remove_duplicates(cleaned)
    return split_excluded_matches(cleaned)

