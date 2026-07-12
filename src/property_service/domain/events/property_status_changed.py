from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from property_service.domain.events.base import DomainEvent


@dataclass
class PropertyStatusChanged(DomainEvent):
    property_id: UUID | None = None
    property_code: str = ""
    old_status: str = ""
    new_status: str = ""
    reason: str | None = None
    changed_by: UUID | None = None

    def to_payload(self) -> dict[str, object]:
        return {
            "property_id": str(self.property_id or self.aggregate_id),
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "property_code": self.property_code,
            "old_status": self.old_status,
            "new_status": self.new_status,
            "reason": self.reason,
            "changed_by": str(self.changed_by) if self.changed_by else None,
            "changed_at": self.occurred_at.isoformat(),
        }
