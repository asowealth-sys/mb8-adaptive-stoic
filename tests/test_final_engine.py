from __future__ import annotations

from rules_engine.stoic_pipeline import run_stoic_pipeline


def test_every_rejected_pick_has_rejection_reason(frame, valid_row):
    result = run_stoic_pipeline(frame(valid_row(market="UNSUPPORTED")))
    assert result.final_slip == []
    assert result.rejected_picks[0]["Rejection Reason"]
    assert result.rejected_picks[0]["Audit Trail ID"]


def test_final_slip_contains_default_columns(frame, valid_row):
    result = run_stoic_pipeline(frame(valid_row()))
    assert set(result.final_slip[0]) == {
        "Match",
        "League",
        "Market Pick",
        "Odds",
        "Ecosystem Type",
        "MVSS Rating",
        "STOIC Score",
        "Survivability Rating",
        "Slip Label",
        "Magic Check Status",
        "Final Decision",
        "Reason",
        "Audit Trail ID",
    }

