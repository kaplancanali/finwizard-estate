from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from property_service.domain.events.base import DomainEvent


@dataclass
class PropertyDeleted(DomainEvent):
    property_id: UUID | None = None
    property_code: str = ""
    deleted_by: UUID | None = None
    hard_delete: bool = False

    def to_payload(self) -> dict[str, object]:
        return {
            "property_id": str(self.property_id or self.aggregate_id),
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "property_code": self.property_code,
            "deleted_by": str(self.deleted_by) if self.deleted_by else None,
            "deleted_at": self.occurred_at.isoformat(),
            "hard_delete": self.hard_delete,
        }
