from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PropertyFeatures:
    heating_type: str | None = None
    cooling_type: str | None = None
    energy_certificate_class: str | None = None
    has_elevator: bool = False
    has_parking: bool = False
    has_balcony: bool = False
    has_garden: bool = False
    has_pool: bool = False
    has_security: bool = False
    has_storage: bool = False
    has_smart_home: bool = False
    has_solar: bool = False
    has_ev_charger: bool = False
    accessibility_level: str | None = None
