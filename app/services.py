from __future__ import annotations

from uuid import uuid4

import pandas as pd

from app.database import init_db, save_run_history
from rules_engine.stoic_pipeline import run_stoic_pipeline


def run_mb8_application(df: pd.DataFrame, source_filename: str) -> dict[str, object]:
    init_db()
    result = run_stoic_pipeline(df, persist=True).model_dump()
    run_id = f"RUN-{uuid4().hex[:12].upper()}"
    payload: dict[str, object] = {
        "run_id": run_id,
        "source_filename": source_filename,
        "total_rows": int(len(df)),
        "final_count": len(result["final_slip"]),
        "rejected_count": len(result["rejected_picks"]),
        "result": result,
    }
    save_run_history(
        run_id=run_id,
        source_filename=source_filename,
        total_rows=int(len(df)),
        final_count=len(result["final_slip"]),
        rejected_count=len(result["rejected_picks"]),
        result=payload,
    )
    return payload
