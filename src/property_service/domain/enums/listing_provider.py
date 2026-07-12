from __future__ import annotations

from property_service.domain.enums._base import StrEnum


class ListingProvider(StrEnum):
    SAHIBINDEN = "sahibinden"
    EMLAKJET = "emlakjet"
    HEPSEMLAK = "hepsiemlak"
    CUSTOM = "custom"
