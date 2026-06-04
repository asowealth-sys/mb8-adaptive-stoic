from __future__ import annotations

from rules_engine.magic_check import magic_check
from rules_engine.rejection_logic import new_audit_trail
from rules_engine.stoic_pipeline import run_stoic_pipeline


def test_magic_check_cannot_be_bypassed_without_full_pipeline():
    audit = new_audit_trail()
    status, reason = magic_check(
        {
            "audit": audit,
            "cdc_risk": 0.1,
            "mvss_rating": "STRONG",
            "stoic_score": 99,
            "cdc_status": "PASS",
        }
    )
    assert status == "REJECT"
    assert "incomplete pipeline" in reason


def test_fragile_mvss_cannot_enter_final_slip(frame, valid_row):
    row = valid_row(
        chaos_index=0.65,
        volatility=0.65,
        draw_risk=0.65,
        market_drift=0.65,
        lineup_risk=0.65,
    )
    result = run_stoic_pipeline(frame(row))
    assert result.final_slip == []
    assert result.rejected_picks[0]["Failed Layer"] == "MAGIC_CHECK"
    assert "MVSS is FRAGILE" in result.rejected_picks[0]["Rejection Reason"]

def test_every_final_pick_has_an_audit_trail(frame, valid_row):
    result = run_stoic_pipeline(frame(valid_row()))
    assert len(result.final_slip) == 1
    assert result.final_slip[0]["Audit Trail ID"]
    assert result.audit_logs[0]["events"]

