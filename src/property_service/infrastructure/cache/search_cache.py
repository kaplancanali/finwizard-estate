from __future__ import annotations

import hashlib
import json
from typing import Any
from uuid import UUID

from property_service.infrastructure.cache.redis_client import get_redis_client


class SearchResultCache:
    def _key(self, tenant_id: UUID, criteria_hash: str) -> str:
        return f"property:search:{tenant_id}:{criteria_hash}"

    def hash_criteria(self, criteria: dict[str, Any]) -> str:
        payload = json.dumps(criteria, sort_keys=True, default=str)
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    async def get(self, tenant_id: UUID, criteria_hash: str) -> dict[str, Any] | None:
        client = await get_redis_client()
        data = await client.get(self._key(tenant_id, criteria_hash))
        return json.loads(data) if data else None

    async def set(
        self,
        tenant_id: UUID,
        criteria_hash: str,
        payload: dict[str, Any],
        ttl: int = 300,
    ) -> None:
        client = await get_redis_client()
        await client.setex(self._key(tenant_id, criteria_hash), ttl, json.dumps(payload, default=str))

    async def invalidate_tenant(self, tenant_id: UUID) -> None:
        client = await get_redis_client()
        pattern = f"property:search:{tenant_id}:*"
        cursor = 0
        while True:
            cursor, keys = await client.scan(cursor, match=pattern, count=100)
            if keys:
                await client.delete(*keys)
            if cursor == 0:
                break
