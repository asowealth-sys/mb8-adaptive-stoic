from __future__ import annotations

from pydantic import BaseModel, Field


class AuditEvent(BaseModel):
    layer: str
    status: str
    reason: str
    details: dict[str, object] = Field(default_factory=dict)


class AuditTrail(BaseModel):
    audit_trail_id: str
    events: list[AuditEvent] = Field(default_factory=list)

    def add(self, layer: str, status: str, reason: str, **details: object) -> None:
        self.events.append(AuditEvent(layer=layer, status=status, reason=reason, details=details))

    @property
    def completed_layers(self) -> list[str]:
        return [event.layer for event in self.events]

