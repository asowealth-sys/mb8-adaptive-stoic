from __future__ import annotations

from execution_engine.cdc import apply_cdc_control
from rules_engine.stoic_pipeline import run_stoic_pipeline


def test_high_cdc_risk_blocks_final_slip():
    kept, rejected = apply_cdc_control(
        [
            {
                "stoic_score": 99,
                "ecosystem_type": "COMPRESSION",
                "cdc_risk": 0.90,
                "risk_flags": [],
            }
        ],
        max_risk=0.74,
    )
    assert kept == []
    assert rejected[0]["failed_layer"] == "CDC"


def test_cdc_correlation_rejects_from_pipeline(frame, valid_row):
    result = run_stoic_pipeline(
        frame(
            valid_row(home_team="Atlas A", away_team="River A"),
            valid_row(home_team="Atlas B", away_team="River B", odds=1.45),
        )
    )
    assert len(result.final_slip) == 1
    assert any(pick["Failed Layer"] == "CDC" for pick in result.rejected_picks)

