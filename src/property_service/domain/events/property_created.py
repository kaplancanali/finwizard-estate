from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from property_service.domain.events.base import DomainEvent


@dataclass
class PropertyCreated(DomainEvent):
    property_id: UUID | None = None
    property_code: str = ""
    slug: str = ""
    property_type: str = ""
    property_category: str = ""
    status: str = ""
    source_type: str = ""
    country_code: str = ""
    province: str | None = None
    district: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    sale_price: Decimal | None = None
    currency: str | None = None
    created_by: UUID | None = None

    def to_payload(self) -> dict[str, object]:
        return {
            "property_id": str(self.property_id or self.aggregate_id),
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "property_code": self.property_code,
            "slug": self.slug,
            "property_type": self.property_type,
            "property_category": self.property_category,
            "status": self.status,
            "source_type": self.source_type,
            "location": {
                "country_code": self.country_code,
                "province": self.province,
                "district": self.district,
                "latitude": float(self.latitude) if self.latitude is not None else None,
                "longitude": float(self.longitude) if self.longitude is not None else None,
            },
            "pricing": {
                "sale_price": float(self.sale_price) if self.sale_price is not None else None,
                "currency": self.currency,
            },
            "created_by": str(self.created_by) if self.created_by else None,
            "created_at": self.occurred_at.isoformat(),
        }
