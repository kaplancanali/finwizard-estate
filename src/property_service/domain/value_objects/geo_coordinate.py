from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class GeoCoordinate:
    latitude: Decimal
    longitude: Decimal
    elevation: Decimal | None = None

    def __post_init__(self) -> None:
        if not (-90 <= self.latitude <= 90):
            raise ValueError(f"Latitude must be between -90 and 90: {self.latitude}")
        if not (-180 <= self.longitude <= 180):
            raise ValueError(f"Longitude must be between -180 and 180: {self.longitude}")

    @property
    def has_coordinates(self) -> bool:
        return True
