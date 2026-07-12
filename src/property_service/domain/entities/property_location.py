from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from property_service.domain.value_objects.geo_coordinate import GeoCoordinate


@dataclass
class PropertyLocation:
    country_code: str
    province: str | None = None
    district: str | None = None
    neighborhood: str | None = None
    street: str | None = None
    postal_code: str | None = None
    address_line: str | None = None
    address_line_2: str | None = None
    coordinate: GeoCoordinate | None = None
    geohash: str | None = None
    timezone: str | None = None
    is_verified: bool = False

    def __post_init__(self) -> None:
        self.country_code = self.country_code.strip().upper()
        if len(self.country_code) != 2:
            raise ValueError(f"country_code must be ISO 3166-1 alpha-2: {self.country_code!r}")

    @property
    def latitude(self) -> Decimal | None:
        return self.coordinate.latitude if self.coordinate else None

    @property
    def longitude(self) -> Decimal | None:
        return self.coordinate.longitude if self.coordinate else None

    @property
    def elevation(self) -> Decimal | None:
        return self.coordinate.elevation if self.coordinate else None

    def has_address_components(self) -> bool:
        return any([
            self.province,
            self.district,
            self.neighborhood,
            self.street,
            self.address_line,
        ])

    def has_location(self) -> bool:
        return self.coordinate is not None or self.has_address_components()

    def update_coordinate(self, coordinate: GeoCoordinate) -> None:
        self.coordinate = coordinate
