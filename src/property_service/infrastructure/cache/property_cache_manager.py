from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any
from uuid import UUID

from property_service.application.ports.property_cache import IPropertyCache
from property_service.domain.aggregates.property import Property
from property_service.domain.events.base import DomainEvent
from property_service.domain.events.property_created import PropertyCreated
from property_service.domain.events.property_deleted import PropertyDeleted
from property_service.domain.events.property_documents_updated import PropertyDocumentsUpdated
from property_service.domain.events.property_images_updated import PropertyImagesUpdated
from property_service.domain.events.property_location_changed import PropertyLocationChanged
from property_service.domain.events.property_price_changed import PropertyPriceChanged
from property_service.domain.events.property_status_changed import PropertyStatusChanged
from property_service.domain.events.property_updated import PropertyUpdated
from property_service.infrastructure.cache.cache_config import (
    TTL_PROPERTY_DETAIL,
    lookup_amenities_key,
    lookup_types_key,
    stampede_lock_key,
)
from property_service.infrastructure.cache.geohash_utils import encode_geohash, geohash_neighbors
from property_service.infrastructure.cache.in_memory_property_cache import InMemoryPropertyCache
from property_service.infrastructure.cache.property_cache import RedisPropertyCache

logger = logging.getLogger(__name__)


class PropertyCacheManager:
    """Cache-aside coordinator with event-driven invalidation."""

    def __init__(self, property_cache: IPropertyCache | None = None) -> None:
        self._property = property_cache or RedisPropertyCache()
        self._hits = 0
        self._misses = 0

    @property
    def metrics(self) -> dict[str, int]:
        total = self._hits + self._misses
        ratio = round(self._hits / total, 4) if total else 0.0
        return {"hits": self._hits, "misses": self._misses, "hit_ratio": ratio}

    async def get_property_detail(self, property_id: UUID) -> dict[str, Any] | None:
        try:
            data = await self._property.get_property(property_id)
            if data:
                self._hits += 1
            else:
                self._misses += 1
            return data
        except Exception:
            logger.debug("property_cache_get_skipped", extra={"property_id": str(property_id)})
            return None

    async def set_property_detail(self, property_id: UUID, data: dict[str, Any], ttl: int = TTL_PROPERTY_DETAIL) -> None:
        try:
            await self._property.set_property(property_id, data, ttl=ttl)
        except Exception:
            logger.debug("property_cache_set_skipped", extra={"property_id": str(property_id)})

    async def get_property_detail_cached(
        self,
        property_id: UUID,
        loader: Callable[[], Awaitable[dict[str, Any]]],
    ) -> dict[str, Any]:
        cached = await self.get_property_detail(property_id)
        if cached:
            return cached

        lock = stampede_lock_key(property_id)
        acquired = await self._safe_acquire_lock(lock)
        if not acquired:
            await asyncio.sleep(0.1)
            cached = await self.get_property_detail(property_id)
            if cached:
                return cached

        try:
            data = await loader()
            await self.set_property_detail(property_id, data)
            return data
        finally:
            if acquired:
                await self._safe_release_lock(lock)

    async def invalidate_property(self, property_id: UUID) -> None:
        try:
            await self._property.invalidate_property(property_id)
        except Exception:
            logger.debug("property_cache_invalidate_skipped", extra={"property_id": str(property_id)})

    async def invalidate_tenant(self, tenant_id: UUID) -> None:
        try:
            await self._property.invalidate_tenant_search(tenant_id)
            await self._property.invalidate_statistics(tenant_id)
        except Exception:
            logger.debug("tenant_cache_invalidate_skipped", extra={"tenant_id": str(tenant_id)})

    async def on_property_changed(self, property_id: UUID, tenant_id: UUID) -> None:
        await self.invalidate_property(property_id)
        await self.invalidate_tenant(tenant_id)

    async def handle_domain_events(self, events: list[DomainEvent], prop: Property) -> None:
        for event in events:
            await self._invalidate_for_event(event, prop)

    async def _invalidate_for_event(self, event: DomainEvent, prop: Property) -> None:
        tenant_id = event.tenant_id or prop.tenant_id
        property_id = event.aggregate_id or prop.id

        if isinstance(event, PropertyCreated):
            await self._property.invalidate_statistics(tenant_id)
            return

        if isinstance(event, PropertyDeleted):
            await self.invalidate_property(property_id)
            await self._property.invalidate_code(tenant_id, str(prop.property_code))
            await self._property.invalidate_slug(tenant_id, str(prop.slug))
            await self.invalidate_tenant(tenant_id)
            return

        if isinstance(event, PropertyPriceChanged):
            await self.invalidate_property(property_id)
            await self._property.invalidate_tenant_search(tenant_id)
            return

        if isinstance(event, PropertyLocationChanged):
            await self.invalidate_property(property_id)
            location = event.new_location or {}
            lat = location.get("latitude")
            lng = location.get("longitude")
            if lat is not None and lng is not None:
                cell = encode_geohash(float(lat), float(lng))
                for neighbor in geohash_neighbors(cell):
                    await self._property.invalidate_nearby_pattern(tenant_id, neighbor)
            return

        if isinstance(event, PropertyStatusChanged):
            await self.invalidate_property(property_id)
            await self.invalidate_tenant(tenant_id)
            return

        if isinstance(event, PropertyImagesUpdated):
            await self.invalidate_property(property_id)
            return

        if isinstance(event, PropertyDocumentsUpdated):
            await self.invalidate_property(property_id)
            return

        if isinstance(event, PropertyUpdated):
            await self.invalidate_property(property_id)
            await self.invalidate_tenant(tenant_id)
            if event.changed_fields and "slug" in event.changed_fields:
                old_slug = (event.changes or {}).get("slug", {}).get("old")
                if old_slug:
                    await self._property.invalidate_slug(tenant_id, str(old_slug))
            if event.changed_fields and any(f.startswith("metadata") for f in event.changed_fields):
                await self._property.invalidate_property(property_id)
            return

        await self.on_property_changed(property_id, tenant_id)

    async def get_statistics(self, tenant_id: UUID) -> dict[str, Any] | None:
        try:
            return await self._property.get_statistics(tenant_id)
        except Exception:
            return None

    async def set_statistics(self, tenant_id: UUID, payload: dict[str, Any], ttl: int = 1800) -> None:
        try:
            await self._property.set_statistics(tenant_id, payload, ttl=ttl)
        except Exception:
            logger.debug("statistics_cache_set_skipped", extra={"tenant_id": str(tenant_id)})

    async def warm_lookup_caches(self) -> None:
        from property_service.config.lookup_codes import KNOWN_AMENITY_CODES
        from property_service.domain.enums.property_type import PropertyType

        types_payload = {"items": [{"code": t.value} for t in PropertyType]}
        amenities_payload = {"items": [{"code": code} for code in sorted(KNOWN_AMENITY_CODES)]}
        try:
            await self._property.set_lookup(lookup_types_key(), types_payload)
            await self._property.set_lookup(lookup_amenities_key(), amenities_payload)
        except Exception:
            logger.debug("lookup_cache_warm_skipped")

    async def get_lookup(self, key: str) -> dict[str, Any] | None:
        try:
            return await self._property.get_lookup(key)
        except Exception:
            return None

    async def get_property_id_by_code(self, tenant_id: UUID, code: str) -> str | None:
        try:
            return await self._property.get_property_id_by_code(tenant_id, code)
        except Exception:
            return None

    async def set_property_id_by_code(self, tenant_id: UUID, code: str, property_id: UUID) -> None:
        try:
            await self._property.set_property_id_by_code(tenant_id, code, property_id, ttl=1800)
        except Exception:
            pass

    async def get_property_id_by_slug(self, tenant_id: UUID, slug: str) -> str | None:
        try:
            return await self._property.get_property_id_by_slug(tenant_id, slug)
        except Exception:
            return None

    async def set_property_id_by_slug(self, tenant_id: UUID, slug: str, property_id: UUID) -> None:
        try:
            await self._property.set_property_id_by_slug(tenant_id, slug, property_id, ttl=1800)
        except Exception:
            pass

    async def _safe_acquire_lock(self, lock_key: str) -> bool:
        try:
            return await self._property.try_acquire_lock(lock_key)
        except Exception:
            return True

    async def _safe_release_lock(self, lock_key: str) -> None:
        try:
            await self._property.release_lock(lock_key)
        except Exception:
            pass
