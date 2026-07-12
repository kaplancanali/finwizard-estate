from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class ListingSnapshot:
    title: str
    description: str | None
    sale_price: Decimal | None
    currency: str | None
    province: str | None
    district: str | None
    provider: str
    listing_id: str
    raw_payload: dict[str, object]


class ListingAdapter(ABC):
    @abstractmethod
    async def fetch_listing(self, url: str) -> ListingSnapshot: ...


class StubListingAdapter(ListingAdapter):
    """Placeholder adapter until external listing integrations are wired."""

    async def fetch_listing(self, url: str) -> ListingSnapshot:
        return ListingSnapshot(
            title="Imported Listing",
            description=None,
            sale_price=None,
            currency="TRY",
            province=None,
            district=None,
            provider="stub",
            listing_id=url,
            raw_payload={"url": url},
        )
