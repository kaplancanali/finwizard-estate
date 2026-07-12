from __future__ import annotations

from property_service.domain.enums._base import StrEnum


class PropertyCategory(StrEnum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    LAND = "land"
    MIXED_USE = "mixed_use"
    HOSPITALITY = "hospitality"
    AGRICULTURAL = "agricultural"
