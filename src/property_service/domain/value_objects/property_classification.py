from __future__ import annotations

from dataclasses import dataclass

from property_service.domain.enums.property_category import PropertyCategory
from property_service.domain.enums.property_type import PropertyType


@dataclass(frozen=True)
class PropertyClassification:
    property_type: PropertyType
    category: PropertyCategory
    subtype: str | None = None

    def __post_init__(self) -> None:
        if self.subtype is not None and not self.subtype.strip():
            object.__setattr__(self, "subtype", None)
