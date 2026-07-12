from __future__ import annotations

import json
from typing import Any
from uuid import UUID

import redis.asyncio as redis

from property_service.application.ports.property_cache import IPropertyCache
from property_service.config import get_settings
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
    property_code_key,
    property_detail_key,
    property_metadata_key,
    property_nearby_key,
    property_nearby_pattern,
    property_slug_key,
    property_stats_key,
    search_cache_key,
)


class RedisPropertyCache(IPropertyCache):
    def __init__(self, client: redis.Redis | None = None) -> None:
        self._client = client

    async def _get_client(self) -> redis.Redis:
        if self._client is None:
            settings = get_settings()
            self._client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
                max_connections=settings.redis_max_connections,
            )
        return self._client

    async def _scan_delete(self, pattern: str) -> None:
        client = await self._get_client()
        cursor = 0
        while True:
            cursor, keys = await client.scan(cursor, match=pattern, count=100)
            if keys:
                await client.delete(*keys)
            if cursor == 0:
                break

    async def get_property(self, property_id: UUID) -> dict | None:
        client = await self._get_client()
        data = await client.get(property_detail_key(property_id))
        return json.loads(data) if data else None

    async def set_property(self, property_id: UUID, data: dict, ttl: int = TTL_PROPERTY_DETAIL) -> None:
        client = await self._get_client()
        await client.setex(property_detail_key(property_id), ttl, json.dumps(data, default=str))

    async def invalidate_property(self, property_id: UUID) -> None:
        client = await self._get_client()
        await client.delete(property_detail_key(property_id), property_metadata_key(property_id))

    async def get_metadata(self, property_id: UUID) -> dict | None:
        client = await self._get_client()
        data = await client.get(property_metadata_key(property_id))
        return json.loads(data) if data else None

    async def set_metadata(self, property_id: UUID, data: dict, ttl: int = TTL_PROPERTY_METADATA) -> None:
        client = await self._get_client()
        await client.setex(property_metadata_key(property_id), ttl, json.dumps(data, default=str))

    async def get_property_id_by_code(self, tenant_id: UUID, code: str) -> str | None:
        client = await self._get_client()
        return await client.get(property_code_key(tenant_id, code))

    async def set_property_id_by_code(
        self, tenant_id: UUID, code: str, property_id: UUID, ttl: int = TTL_PROPERTY_CODE
    ) -> None:
        client = await self._get_client()
        await client.setex(property_code_key(tenant_id, code), ttl, str(property_id))

    async def get_property_id_by_slug(self, tenant_id: UUID, slug: str) -> str | None:
        client = await self._get_client()
        return await client.get(property_slug_key(tenant_id, slug))

    async def set_property_id_by_slug(
        self, tenant_id: UUID, slug: str, property_id: UUID, ttl: int = TTL_PROPERTY_SLUG
    ) -> None:
        client = await self._get_client()
        await client.setex(property_slug_key(tenant_id, slug), ttl, str(property_id))

    async def invalidate_code(self, tenant_id: UUID, code: str) -> None:
        client = await self._get_client()
        await client.delete(property_code_key(tenant_id, code))

    async def invalidate_slug(self, tenant_id: UUID, slug: str) -> None:
        client = await self._get_client()
        await client.delete(property_slug_key(tenant_id, slug))

    async def get_search_results(self, cache_key: str) -> dict | None:
        client = await self._get_client()
        data = await client.get(cache_key)
        return json.loads(data) if data else None

    async def set_search_results(self, cache_key: str, data: dict, ttl: int = TTL_PROPERTY_SEARCH) -> None:
        client = await self._get_client()
        await client.setex(cache_key, ttl, json.dumps(data, default=str))

    async def invalidate_tenant_search(self, tenant_id: UUID) -> None:
        await self._scan_delete(f"property:search:{tenant_id}:*")

    async def get_nearby(self, key: str) -> dict | None:
        client = await self._get_client()
        data = await client.get(key)
        return json.loads(data) if data else None

    async def set_nearby(self, key: str, data: dict, ttl: int = TTL_PROPERTY_NEARBY) -> None:
        client = await self._get_client()
        await client.setex(key, ttl, json.dumps(data, default=str))

    async def invalidate_nearby_pattern(self, tenant_id: UUID, geohash: str) -> None:
        await self._scan_delete(property_nearby_pattern(tenant_id, geohash))

    async def get_statistics(self, tenant_id: UUID) -> dict | None:
        client = await self._get_client()
        data = await client.get(property_stats_key(tenant_id))
        return json.loads(data) if data else None

    async def set_statistics(self, tenant_id: UUID, data: dict, ttl: int = TTL_PROPERTY_STATS) -> None:
        client = await self._get_client()
        await client.setex(property_stats_key(tenant_id), ttl, json.dumps(data, default=str))

    async def invalidate_statistics(self, tenant_id: UUID) -> None:
        client = await self._get_client()
        await client.delete(property_stats_key(tenant_id))

    async def get_lookup(self, key: str) -> dict | None:
        client = await self._get_client()
        data = await client.get(key)
        return json.loads(data) if data else None

    async def set_lookup(self, key: str, data: dict, ttl: int = TTL_LOOKUP) -> None:
        client = await self._get_client()
        await client.setex(key, ttl, json.dumps(data, default=str))

    async def get_jwks(self) -> dict | None:
        client = await self._get_client()
        data = await client.get(jwks_cache_key())
        return json.loads(data) if data else None

    async def set_jwks(self, data: dict, ttl: int = 3600) -> None:
        client = await self._get_client()
        await client.setex(jwks_cache_key(), ttl, json.dumps(data, default=str))

    async def try_acquire_lock(self, lock_key: str, ttl: int = TTL_STAMPEDE_LOCK) -> bool:
        client = await self._get_client()
        return bool(await client.set(lock_key, "1", nx=True, ex=ttl))

    async def release_lock(self, lock_key: str) -> None:
        client = await self._get_client()
        await client.delete(lock_key)

    def search_cache_key(self, tenant_id: UUID, criteria_hash: str) -> str:
        return search_cache_key(tenant_id, criteria_hash)

    def nearby_cache_key(self, tenant_id: UUID, geohash: str, radius: int) -> str:
        return property_nearby_key(tenant_id, geohash, radius)
