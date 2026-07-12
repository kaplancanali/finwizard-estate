from __future__ import annotations

import redis.asyncio as redis

from property_service.config import get_settings

_client: redis.Redis | None = None


async def get_redis_client() -> redis.Redis:
    global _client
    if _client is None:
        settings = get_settings()
        _client = redis.from_url(settings.redis_url, decode_responses=True)
    return _client


async def close_redis_client() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None
