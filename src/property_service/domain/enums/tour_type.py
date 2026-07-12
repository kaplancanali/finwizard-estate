from __future__ import annotations

from property_service.domain.enums._base import StrEnum


class TourType(StrEnum):
    VIRTUAL = "virtual"
    WALKTHROUGH = "walkthrough"
    TOUR_360 = "360"
