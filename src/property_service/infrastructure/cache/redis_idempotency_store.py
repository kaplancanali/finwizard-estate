from __future__ import annotations

import json

from property_service.application.ports.idempotency_store import IIdempotencyStore
from property_service.infrastructure.cache.redis_client import get_redis_client


class RedisIdempotencyStore(IIdempotencyStore):
    def _response_key(self, key: str) -> str:
        return f"idempotency:response:{key}"

    def _processing_key(self, key: str) -> str:
        return f"idempotency:processing:{key}"

    async def get_response(self, key: str) -> dict | None:
        try:
            client = await get_redis_client()
            data = await client.get(self._response_key(key))
            return json.loads(data) if data else None
        except Exception:
            return None

    async def store_response(self, key: str, response: dict, ttl: int = 86400) -> None:
        try:
            client = await get_redis_client()
            await client.setex(self._response_key(key), ttl, json.dumps(response, default=str))
        except Exception:
            return None

    async def is_processing(self, key: str) -> bool:
        try:
            client = await get_redis_client()
            return bool(await client.exists(self._processing_key(key)))
        except Exception:
            return False

    async def mark_processing(self, key: str, ttl: int = 300) -> bool:
        try:
            client = await get_redis_client()
            return bool(await client.set(self._processing_key(key), "1", nx=True, ex=ttl))
        except Exception:
            return True
