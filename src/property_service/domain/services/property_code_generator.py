from __future__ import annotations

import re

from property_service.domain.value_objects.property_code import PropertyCode
from property_service.domain.value_objects.slug import Slug


class PropertyCodeGenerator:
    """Generates unique property codes: FW-{COUNTRY}-{REGION}-{SEQUENCE:08d}."""

    def __init__(self) -> None:
        self._sequences: dict[str, int] = {}

    def generate(self, country_code: str, region_code: str) -> PropertyCode:
        country = country_code.strip().upper()
        region = self._normalize_region(region_code)
        key = f"{country}:{region}"
        seq = self._sequences.get(key, 0) + 1
        self._sequences[key] = seq
        return PropertyCode(f"FW-{country}-{region}-{seq:08d}")

    @staticmethod
    def _normalize_region(region_code: str) -> str:
        region = region_code.strip().upper()
        region = re.sub(r"[^A-Z0-9]", "", region)
        return region[:6] or "GEN"
