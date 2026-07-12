from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from property_service.domain.events.base import DomainEvent


@dataclass
class PropertyRestored(DomainEvent):
    property_id: UUID | None = None
    property_code: str = ""
    restored_by: UUID | None = None

    def to_payload(self) -> dict[str, object]:
        return {
            "property_id": str(self.property_id or self.aggregate_id),
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "property_code": self.property_code,
            "restored_by": str(self.restored_by) if self.restored_by else None,
            "restored_at": self.occurred_at.isoformat(),
        }
