from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from property_service.domain.events.base import DomainEvent


@dataclass
class PropertyDocumentsUpdated(DomainEvent):
    property_id: UUID | None = None
    action: str = ""
    document_ids: list[UUID] | None = None
    document_types: list[str] | None = None
    updated_by: UUID | None = None

    def __post_init__(self) -> None:
        if self.document_ids is None:
            self.document_ids = []
        if self.document_types is None:
            self.document_types = []

    def to_payload(self) -> dict[str, object]:
        return {
            "property_id": str(self.property_id or self.aggregate_id),
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "action": self.action,
            "document_ids": [str(i) for i in self.document_ids or []],
            "document_types": self.document_types or [],
            "updated_by": str(self.updated_by) if self.updated_by else None,
            "updated_at": self.occurred_at.isoformat(),
        }
