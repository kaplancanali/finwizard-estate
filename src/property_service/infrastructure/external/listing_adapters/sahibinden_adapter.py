from __future__ import annotations

from typing import Any

from property_service.infrastructure.external.listing_adapters.base import ListingAdapter


class SahibindenAdapter(ListingAdapter):
    def supports_url(self, url: str) -> bool:
        return "sahibinden.com" in url.lower()

    async def fetch_listing(self, url: str) -> dict[str, Any]:
        return {"source": "sahibinden", "url": url, "status": "not_implemented"}
