from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from property_service.domain.events.base import DomainEvent


@dataclass
class PropertyOwnershipChanged(DomainEvent):
    property_id: UUID | None = None
    action: str = ""
    current_owners: list[dict[str, object]] | None = None
    changed_by: UUID | None = None

    def __post_init__(self) -> None:
        if self.current_owners is None:
            self.current_owners = []

    def to_payload(self) -> dict[str, object]:
        return {
            "property_id": str(self.property_id or self.aggregate_id),
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "action": self.action,
            "current_owners": self.current_owners or [],
            "changed_by": str(self.changed_by) if self.changed_by else None,
            "changed_at": self.occurred_at.isoformat(),
        }
