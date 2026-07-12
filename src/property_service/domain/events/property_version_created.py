from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from property_service.domain.events.base import DomainEvent


@dataclass
class PropertyVersionCreated(DomainEvent):
    property_id: UUID | None = None
    version_number: int = 0
    change_summary: str | None = None
    created_by: UUID | None = None
