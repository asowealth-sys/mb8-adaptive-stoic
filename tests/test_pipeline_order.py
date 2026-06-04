from __future__ import annotations

from rules_engine.stoic_pipeline import get_pipeline_order


def test_pipeline_order_cannot_be_changed():
    assert get_pipeline_order() == (
        "RAW_DATASET",
        "FEATURE_ENGINEERING_LAYER",
        "ECOSYSTEM_ENGINE",
        "DOMINANCE_AND_STABILITY_LAYER",
        "BEHAVIORAL_AI_LAYER",
        "PGCE_RISK_ENGINE",
        "MARKET_SELECTION_ENGINE",
        "MVSS_SCORING",
        "CDC",
        "STOIC_SLIP_SCORER",
        "MAGIC_CHECK",
        "FINAL_SLIP",
    )

