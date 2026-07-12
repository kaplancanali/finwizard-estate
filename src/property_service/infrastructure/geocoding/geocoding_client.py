from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class GeocodingClient(ABC):
    @abstractmethod
    async def reverse_geocode(self, latitude: float, longitude: float) -> dict[str, Any]: ...

    @abstractmethod
    async def forward_geocode(self, address: str) -> dict[str, Any]: ...
