from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from property_service.domain.events.base import DomainEvent


@dataclass
class PropertyUpdated(DomainEvent):
    property_id: UUID | None = None
    property_code: str = ""
    version: int = 0
    changed_fields: list[str] | None = None
    changes: dict[str, object] | None = None
    updated_by: UUID | None = None

    def __post_init__(self) -> None:
        if self.changed_fields is None:
            self.changed_fields = []

    def to_payload(self) -> dict[str, object]:
        return {
            "property_id": str(self.property_id or self.aggregate_id),
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "property_code": self.property_code,
            "version": self.version,
            "changed_fields": self.changed_fields,
            "changes": self.changes or {},
            "updated_by": str(self.updated_by) if self.updated_by else None,
            "updated_at": self.occurred_at.isoformat(),
        }
