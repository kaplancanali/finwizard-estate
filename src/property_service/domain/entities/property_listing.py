from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from property_service.domain.enums.listing_provider import ListingProvider
from property_service.domain.enums.sync_status import SyncStatus


@dataclass
class PropertyListing:
    original_url: str | None = None
    provider: ListingProvider | None = None
    listing_id: str | None = None
    listing_date: date | None = None
    last_synced_at: datetime | None = None
    sync_status: SyncStatus = SyncStatus.PENDING
    provider_metadata: dict[str, object] | None = None
