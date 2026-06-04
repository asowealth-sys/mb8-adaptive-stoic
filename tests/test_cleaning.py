from __future__ import annotations

from data_layer.clean import clean_dataset
from rules_engine.stoic_pipeline import run_stoic_pipeline


def test_duplicate_matches_are_removed(frame, valid_row):
    df = frame(valid_row(), valid_row())
    cleaned, excluded = clean_dataset(df)
    assert len(cleaned) == 1
    assert excluded.empty


def test_missing_required_fields_cause_reject_not_silent_pass(frame, valid_row):
    df = frame(valid_row()).drop(columns=["odds"])
    result = run_stoic_pipeline(df)
    assert result.final_slip == []
    assert result.rejected_picks[0]["Failed Layer"] == "RAW_DATASET"
    assert "Missing required columns" in result.rejected_picks[0]["Rejection Reason"]

