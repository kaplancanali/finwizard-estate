from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime


@dataclass
class PropertyParcel:
    block: str | None = None
    parcel_number: str | None = None
    parcel_area_sqm: Decimal | None = None
    cadastral_reference: str | None = None
    zoning_type: str | None = None

    def has_parcel_info(self) -> bool:
        return any([self.block, self.parcel_number, self.cadastral_reference])
