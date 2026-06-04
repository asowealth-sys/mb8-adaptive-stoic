"""Non-runtime-editable MB 8.0 Adaptive STOIC thresholds."""

from pydantic import BaseModel


class Settings(BaseModel):
    stoic_score_threshold: float = 70.0
    max_cdc_risk: float = 0.74
    dominance_pass_threshold: float = 52.0
    pgce_max_risk: float = 0.70
    duplicate_subset: tuple[str, ...] = ("match", "league", "kickoff")
    required_columns: tuple[str, ...] = (
        "home_team",
        "away_team",
        "league",
        "market",
        "odds",
    )


SETTINGS = Settings()

