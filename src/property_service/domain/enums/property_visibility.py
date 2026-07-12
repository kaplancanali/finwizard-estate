from __future__ import annotations

from property_service.domain.enums._base import StrEnum


class PropertyVisibility(StrEnum):
    PRIVATE = "private"
    TENANT = "tenant"
    PUBLIC = "public"
    PARTNER = "partner"
