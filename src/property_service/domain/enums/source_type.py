from __future__ import annotations

from property_service.domain.enums._base import StrEnum


class SourceType(StrEnum):
    MANUAL = "manual"
    LISTING_URL = "listing_url"
    ADDRESS = "address"
    COORDINATES = "coordinates"
    MAP_SELECTION = "map_selection"
    PARCEL = "parcel"
    OCR = "ocr"
    VOICE = "voice"
