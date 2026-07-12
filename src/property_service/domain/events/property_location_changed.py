from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from property_service.domain.events.base import DomainEvent


@dataclass
class PropertyLocationChanged(DomainEvent):
    property_id: UUID | None = None
    property_code: str = ""
    old_location: dict[str, object] | None = None
    new_location: dict[str, object] | None = None
    geocoded: bool = False
    changed_by: UUID | None = None

    def to_payload(self) -> dict[str, object]:
        return {
            "property_id": str(self.property_id or self.aggregate_id),
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "property_code": self.property_code,
            "old_location": self.old_location,
            "new_location": self.new_location,
            "geocoded": self.geocoded,
            "changed_by": str(self.changed_by) if self.changed_by else None,
            "changed_at": self.occurred_at.isoformat(),
        }
