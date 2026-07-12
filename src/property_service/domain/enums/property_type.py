from __future__ import annotations

from property_service.domain.enums._base import StrEnum


class PropertyType(StrEnum):
    APARTMENT = "apartment"
    VILLA = "villa"
    RESIDENCE = "residence"
    DETACHED_HOUSE = "detached_house"
    LAND = "land"
    COMMERCIAL = "commercial"
    OFFICE = "office"
    STORE = "store"
    WAREHOUSE = "warehouse"
    FACTORY = "factory"
    HOTEL = "hotel"
    FARM = "farm"
    MIXED_PROJECT = "mixed_project"
    INDUSTRIAL = "industrial"
    OTHER = "other"


# Maps property types to their default category for validation.
PROPERTY_TYPE_CATEGORY_MAP: dict[PropertyType, str] = {
    PropertyType.APARTMENT: "residential",
    PropertyType.VILLA: "residential",
    PropertyType.RESIDENCE: "residential",
    PropertyType.DETACHED_HOUSE: "residential",
    PropertyType.LAND: "land",
    PropertyType.COMMERCIAL: "commercial",
    PropertyType.OFFICE: "commercial",
    PropertyType.STORE: "commercial",
    PropertyType.WAREHOUSE: "industrial",
    PropertyType.FACTORY: "industrial",
    PropertyType.HOTEL: "hospitality",
    PropertyType.FARM: "agricultural",
    PropertyType.MIXED_PROJECT: "mixed_use",
    PropertyType.INDUSTRIAL: "industrial",
    PropertyType.OTHER: "residential",
}
