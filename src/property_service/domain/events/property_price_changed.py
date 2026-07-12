from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from property_service.domain.events.base import DomainEvent


@dataclass
class PropertyPriceChanged(DomainEvent):
    property_id: UUID | None = None
    property_code: str = ""
    price_type: str = ""
    old_amount: Decimal | None = None
    new_amount: Decimal | None = None
    currency: str | None = None
    price_per_sqm: Decimal | None = None
    changed_by: UUID | None = None
    change_reason: str | None = None

    def to_payload(self) -> dict[str, object]:
        return {
            "property_id": str(self.property_id or self.aggregate_id),
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "property_code": self.property_code,
            "price_type": self.price_type,
            "old_amount": float(self.old_amount) if self.old_amount is not None else None,
            "new_amount": float(self.new_amount) if self.new_amount is not None else None,
            "currency": self.currency,
            "price_per_sqm": float(self.price_per_sqm) if self.price_per_sqm is not None else None,
            "changed_by": str(self.changed_by) if self.changed_by else None,
            "changed_at": self.occurred_at.isoformat(),
            "change_reason": self.change_reason,
        }
