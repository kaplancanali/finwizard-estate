from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from property_service.domain.events.base import DomainEvent


@dataclass
class PropertyListed(DomainEvent):
    property_id: UUID | None = None
    provider: str = ""
    listing_id: str = ""
    original_url: str | None = None
