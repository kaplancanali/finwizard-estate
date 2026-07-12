from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from property_service.application.ports.property_cache import IPropertyCache
from property_service.infrastructure.cache.cache_config import (
    TTL_LOOKUP,
    TTL_PROPERTY_CODE,
    TTL_PROPERTY_DETAIL,
    TTL_PROPERTY_METADATA,
    TTL_PROPERTY_NEARBY,
    TTL_PROPERTY_SEARCH,
    TTL_PROPERTY_SLUG,
    TTL_PROPERTY_STATS,
    TTL_STAMPEDE_LOCK,
    jwks_cache_key,
    lookup_amenities_key,
    lookup_types_key,
    property_code_key,
    property_detail_key,
    property_metadata_key,
    property_nearby_key,
    property_nearby_pattern,
    property_search_pattern,
    property_slug_key,
    property_stats_key,
    search_cache_key,
    stampede_lock_key,
)


class InMemoryPropertyCache(IPropertyCache):
    """Test/dev fallback when Redis is unavailable."""

    def __init__(self) -> None:
        self._store: dict[str, str] = {}
        self._locks: set[str] = set()

    async def get_property(self, property_id: UUID) -> dict | None:
        return self._loads(property_detail_key(property_id))

    async def set_property(self, property_id: UUID, data: dict, ttl: int = TTL_PROPERTY_DETAIL) -> None:
        self._store[property_detail_key(property_id)] = json.dumps(data, default=str)

    async def invalidate_property(self, property_id: UUID) -> None:
        self._store.pop(property_detail_key(property_id), None)
        self._store.pop(property_metadata_key(property_id), None)

    async def get_metadata(self, property_id: UUID) -> dict | None:
        return self._loads(property_metadata_key(property_id))

    async def set_metadata(self, property_id: UUID, data: dict, ttl: int = TTL_PROPERTY_METADATA) -> None:
        self._store[property_metadata_key(property_id)] = json.dumps(data, default=str)

    async def get_property_id_by_code(self, tenant_id: UUID, code: str) -> str | None:
        return self._store.get(property_code_key(tenant_id, code))

    async def set_property_id_by_code(
        self, tenant_id: UUID, code: str, property_id: UUID, ttl: int = TTL_PROPERTY_CODE
    ) -> None:
        self._store[property_code_key(tenant_id, code)] = str(property_id)

    async def get_property_id_by_slug(self, tenant_id: UUID, slug: str) -> str | None:
        return self._store.get(property_slug_key(tenant_id, slug))

    async def set_property_id_by_slug(
        self, tenant_id: UUID, slug: str, property_id: UUID, ttl: int = TTL_PROPERTY_SLUG
    ) -> None:
        self._store[property_slug_key(tenant_id, slug)] = str(property_id)

    async def invalidate_code(self, tenant_id: UUID, code: str) -> None:
        self._store.pop(property_code_key(tenant_id, code), None)

    async def invalidate_slug(self, tenant_id: UUID, slug: str) -> None:
        self._store.pop(property_slug_key(tenant_id, slug), None)

    async def get_search_results(self, key: str) -> dict | None:
        return self._loads(key)

    async def set_search_results(self, key: str, data: dict, ttl: int = TTL_PROPERTY_SEARCH) -> None:
        self._store[key] = json.dumps(data, default=str)

    async def invalidate_tenant_search(self, tenant_id: UUID) -> None:
        prefix = f"property:search:{tenant_id}:"
        for key in list(self._store):
            if key.startswith(prefix):
                del self._store[key]

    async def get_nearby(self, key: str) -> dict | None:
        return self._loads(key)

    async def set_nearby(self, key: str, data: dict, ttl: int = TTL_PROPERTY_NEARBY) -> None:
        self._store[key] = json.dumps(data, default=str)

    async def invalidate_nearby_pattern(self, tenant_id: UUID, geohash: str) -> None:
        prefix = property_nearby_pattern(tenant_id, geohash).replace("*", "")
        for key in list(self._store):
            if key.startswith(prefix):
                del self._store[key]

    async def get_statistics(self, tenant_id: UUID) -> dict | None:
        return self._loads(property_stats_key(tenant_id))

    async def set_statistics(self, tenant_id: UUID, data: dict, ttl: int = TTL_PROPERTY_STATS) -> None:
        self._store[property_stats_key(tenant_id)] = json.dumps(data, default=str)

    async def invalidate_statistics(self, tenant_id: UUID) -> None:
        self._store.pop(property_stats_key(tenant_id), None)

    async def get_lookup(self, key: str) -> dict | None:
        return self._loads(key)

    async def set_lookup(self, key: str, data: dict, ttl: int = TTL_LOOKUP) -> None:
        self._store[key] = json.dumps(data, default=str)

    async def get_jwks(self) -> dict | None:
        return self._loads(jwks_cache_key())

    async def set_jwks(self, data: dict, ttl: int = 3600) -> None:
        self._store[jwks_cache_key()] = json.dumps(data, default=str)

    async def try_acquire_lock(self, lock_key: str, ttl: int = TTL_STAMPEDE_LOCK) -> bool:
        if lock_key in self._locks:
            return False
        self._locks.add(lock_key)
        return True

    async def release_lock(self, lock_key: str) -> None:
        self._locks.discard(lock_key)

    def search_cache_key(self, tenant_id: UUID, criteria_hash: str) -> str:
        return search_cache_key(tenant_id, criteria_hash)

    def nearby_cache_key(self, tenant_id: UUID, geohash: str, radius: int) -> str:
        return property_nearby_key(tenant_id, geohash, radius)

    def _loads(self, key: str) -> dict | None:
        raw = self._store.get(key)
        return json.loads(raw) if raw else None
