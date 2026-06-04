from __future__ import annotations

import pandas as pd


def behavioral_flags(row: pd.Series) -> list[str]:
    flags: list[str] = []
    if float(row.get("pressure_index", 0.25)) >= 0.72:
        flags.append("pressure_analysis_high")
    if float(row.get("tactical_freeze", 0.0)) >= 0.60:
        flags.append("tactical_freeze_detected")
    if float(row.get("emotional_chaos", 0.0)) >= 0.60:
        flags.append("emotional_chaos")
    if float(row.get("motivation_distortion", 0.0)) >= 0.60:
        flags.append("motivation_distortion")
    if float(row.get("draw_acceptance", 0.0)) >= 0.60:
        flags.append("draw_acceptance")
    return flags

