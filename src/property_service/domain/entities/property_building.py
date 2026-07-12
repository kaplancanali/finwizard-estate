from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime


@dataclass
class PropertyBuilding:
    construction_year: int | None = None
    building_age: int | None = None
    floor_count: int | None = None
    floor_number: int | None = None
    unit_number: str | None = None
    net_area_sqm: Decimal | None = None
    gross_area_sqm: Decimal | None = None
    room_count: Decimal | None = None
    living_room_count: int | None = None
    bedroom_count: int | None = None
    bathroom_count: int | None = None
    balcony_count: int | None = None
    parking_count: int | None = None

    def compute_building_age(self, *, current_year: int | None = None) -> None:
        if self.construction_year is None:
            self.building_age = None
            return
        year = current_year if current_year is not None else datetime.now().year
        self.building_age = max(0, year - self.construction_year)

    def has_residential_fields(self) -> bool:
        return any([
            self.room_count is not None,
            self.floor_number is not None,
            self.bedroom_count is not None,
        ])
