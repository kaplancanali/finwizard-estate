from __future__ import annotations

from typing import Any


class WithinRadiusSpec:
    """PostGIS ST_DWithin — filter criteria for search repository."""

    def __init__(self, latitude: float, longitude: float, radius_meters: int) -> None:
        self.latitude = latitude
        self.longitude = longitude
        self.radius_meters = radius_meters

    def to_filter(self) -> dict[str, Any]:
        return {
            "geo": {
                "type": "radius",
                "latitude": self.latitude,
                "longitude": self.longitude,
                "radius_meters": self.radius_meters,
            }
        }


class WithinBoundingBoxSpec:
    def __init__(self, north: float, south: float, east: float, west: float) -> None:
        self.north = north
        self.south = south
        self.east = east
        self.west = west

    def to_filter(self) -> dict[str, Any]:
        return {
            "geo": {
                "type": "bounding_box",
                "north": self.north,
                "south": self.south,
                "east": self.east,
                "west": self.west,
            }
        }


class WithinPolygonSpec:
    def __init__(self, coordinates: list[list[float]]) -> None:
        self.coordinates = coordinates

    def to_filter(self) -> dict[str, Any]:
        return {
            "geo": {
                "type": "polygon",
                "coordinates": self.coordinates,
            }
        }
