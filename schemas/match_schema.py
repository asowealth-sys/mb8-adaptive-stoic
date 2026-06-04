from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class MatchRecord(BaseModel):
    model_config = ConfigDict(extra="allow")

    home_team: str
    away_team: str
    league: str
    market: str
    odds: float
    kickoff: str | None = None
    competition_type: str | None = None
    source: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()

