from __future__ import annotations

from pydantic import BaseModel, Field


class EngineResult(BaseModel):
    final_slip: list[dict[str, object]] = Field(default_factory=list)
    rejected_picks: list[dict[str, object]] = Field(default_factory=list)
    audit_logs: list[dict[str, object]] = Field(default_factory=list)

