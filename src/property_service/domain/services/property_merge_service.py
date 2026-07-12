from __future__ import annotations

"""Deduplication when same parcel or listing is detected."""

from uuid import UUID


class PropertyMergeService:
    """Identifies potential duplicate properties for merge (Phase 6)."""

    @staticmethod
    def is_duplicate_listing(
        existing_provider: str,
        existing_listing_id: str,
        provider: str,
        listing_id: str,
    ) -> bool:
        return existing_provider == provider and existing_listing_id == listing_id

    @staticmethod
    def is_duplicate_parcel(
        existing_block: str | None,
        existing_parcel: str | None,
        block: str | None,
        parcel_number: str | None,
    ) -> bool:
        if not block or not parcel_number:
            return False
        return existing_block == block and existing_parcel == parcel_number
