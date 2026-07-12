from __future__ import annotations

from uuid import UUID

from property_service.application.ports.idempotency_store import IIdempotencyStore


class InMemoryIdempotencyStore(IIdempotencyStore):
    """Development fallback when Redis is unavailable."""

    def __init__(self) -> None:
        self._responses: dict[str, dict] = {}
        self._processing: set[str] = set()

    def _composite(self, key: str, tenant_id: UUID | None = None) -> str:
        return f"{tenant_id}:{key}" if tenant_id else key

    async def get_response(self, key: str) -> dict | None:
        return self._responses.get(key)

    async def store_response(self, key: str, response: dict, ttl: int = 86400) -> None:
        self._responses[key] = response

    async def is_processing(self, key: str) -> bool:
        return key in self._processing

    async def mark_processing(self, key: str, ttl: int = 300) -> bool:
        if key in self._processing:
            return False
        self._processing.add(key)
        return True

    def seen(self, tenant_id: UUID, key: str) -> bool:
        composite = self._composite(key, tenant_id)
        if composite in self._responses or composite in self._processing:
            return True
        self._processing.add(composite)
        return False
