from __future__ import annotations

from typing import Any

import httpx

from property_service.config import get_settings
from property_service.infrastructure.geocoding.geocoding_client import GeocodingClient


class NominatimAdapter(GeocodingClient):
    def __init__(self) -> None:
        self._base_url = get_settings().nominatim_url

    async def reverse_geocode(self, latitude: float, longitude: float) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self._base_url}/reverse",
                params={"lat": latitude, "lon": longitude, "format": "json"},
                headers={"User-Agent": "finwizard-property-service/0.1"},
            )
            response.raise_for_status()
            return response.json()

    async def forward_geocode(self, address: str) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self._base_url}/search",
                params={"q": address, "format": "json", "limit": 1},
                headers={"User-Agent": "finwizard-property-service/0.1"},
            )
            response.raise_for_status()
            data = response.json()
            return data[0] if data else {}
