from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass
class PropertyPricing:
    sale_price: Decimal | None = None
    rental_price: Decimal | None = None
    maintenance_fee: Decimal | None = None
    currency: str | None = None
    price_on_request: bool = False
    price_per_sqm: Decimal | None = None

    def has_any_price(self) -> bool:
        return any([
            self.sale_price is not None,
            self.rental_price is not None,
            self.maintenance_fee is not None,
        ])

    def compute_price_per_sqm(self, net_area_sqm: Decimal | None) -> None:
        if net_area_sqm and net_area_sqm > 0 and self.sale_price is not None:
            self.price_per_sqm = (self.sale_price / net_area_sqm).quantize(Decimal("0.01"))
        else:
            self.price_per_sqm = None


@dataclass
class PriceHistoryEntry:
    id: UUID = field(default_factory=uuid4)
    price_type: str = "sale"
    old_amount: Decimal | None = None
    new_amount: Decimal | None = None
    currency: str | None = None
    changed_by: UUID | None = None
    change_reason: str | None = None
