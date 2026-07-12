from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from property_service.domain.events.base import DomainEvent


@dataclass
class PropertyImagesUpdated(DomainEvent):
    property_id: UUID | None = None
    action: str = ""
    image_ids: list[UUID] | None = None
    primary_image_id: UUID | None = None
    total_images: int = 0
    updated_by: UUID | None = None

    def __post_init__(self) -> None:
        if self.image_ids is None:
            self.image_ids = []

    def to_payload(self) -> dict[str, object]:
        return {
            "property_id": str(self.property_id or self.aggregate_id),
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "action": self.action,
            "image_ids": [str(i) for i in self.image_ids or []],
            "primary_image_id": str(self.primary_image_id) if self.primary_image_id else None,
            "total_images": self.total_images,
            "updated_by": str(self.updated_by) if self.updated_by else None,
            "updated_at": self.occurred_at.isoformat(),
        }
