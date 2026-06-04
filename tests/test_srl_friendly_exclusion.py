from __future__ import annotations

from data_layer.clean import clean_dataset
from rules_engine.stoic_pipeline import run_stoic_pipeline


def test_srl_matches_are_removed(frame, valid_row):
    df = frame(valid_row(league="SRL League", competition_type="SRL"))
    cleaned, excluded = clean_dataset(df)
    assert cleaned.empty
    assert excluded.iloc[0]["exclusion_reason"] == "SRL or simulated match detected"


def test_friendly_matches_are_removed(frame, valid_row):
    df = frame(valid_row(league="Club Friendly", competition_type="Friendly"))
    cleaned, excluded = clean_dataset(df)
    assert cleaned.empty
    assert excluded.iloc[0]["exclusion_reason"] == "Friendly match detected"


def test_excluded_matches_have_rejection_reasons(frame, valid_row):
    result = run_stoic_pipeline(frame(valid_row(league="International Friendly", competition_type="Friendly")))
    assert result.final_slip == []
    assert result.rejected_picks[0]["Rejection Reason"] == "Friendly match detected"
    assert result.rejected_picks[0]["Audit Trail ID"]

