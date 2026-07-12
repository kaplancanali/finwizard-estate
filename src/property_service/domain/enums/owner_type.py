from __future__ import annotations

from property_service.domain.enums._base import StrEnum


class OwnerType(StrEnum):
    INDIVIDUAL = "individual"
    COMPANY = "company"
    TRUST = "trust"
