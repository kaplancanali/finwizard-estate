from __future__ import annotations

from property_service.domain.enums._base import StrEnum


class DocumentType(StrEnum):
    PROPERTY_DEED = "property_deed"
    BUILDING_PERMIT = "building_permit"
    OCCUPANCY_PERMIT = "occupancy_permit"
    ENERGY_CERTIFICATE = "energy_certificate"
    FLOOR_PLAN = "floor_plan"
    OTHER = "other"
