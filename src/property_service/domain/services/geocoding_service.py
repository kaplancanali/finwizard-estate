from __future__ import annotations

from abc import ABC, abstractmethod

from property_service.domain.value_objects.geo_coordinate import GeoCoordinate
from property_service.domain.entities.property_location import PropertyLocation


class GeocodingService(ABC):
    """Domain interface for address ↔ coordinate conversion."""

    @abstractmethod
    async def geocode(self, location: PropertyLocation) -> GeoCoordinate:
        ...

    @abstractmethod
    async def reverse_geocode(self, coordinate: GeoCoordinate) -> PropertyLocation:
        ...
