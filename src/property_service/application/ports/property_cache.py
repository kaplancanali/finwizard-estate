from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID


class IPropertyCache(ABC):
    @abstractmethod
    async def get_property(self, property_id: UUID) -> dict | None: ...

    @abstractmethod
    async def set_property(self, property_id: UUID, data: dict, ttl: int) -> None: ...

    @abstractmethod
    async def invalidate_property(self, property_id: UUID) -> None: ...

    @abstractmethod
    async def get_metadata(self, property_id: UUID) -> dict | None: ...

    @abstractmethod
    async def set_metadata(self, property_id: UUID, data: dict, ttl: int) -> None: ...

    @abstractmethod
    async def get_property_id_by_code(self, tenant_id: UUID, code: str) -> str | None: ...

    @abstractmethod
    async def set_property_id_by_code(
        self, tenant_id: UUID, code: str, property_id: UUID, ttl: int
    ) -> None: ...

    @abstractmethod
    async def get_property_id_by_slug(self, tenant_id: UUID, slug: str) -> str | None: ...

    @abstractmethod
    async def set_property_id_by_slug(
        self, tenant_id: UUID, slug: str, property_id: UUID, ttl: int
    ) -> None: ...

    @abstractmethod
    async def invalidate_code(self, tenant_id: UUID, code: str) -> None: ...

    @abstractmethod
    async def invalidate_slug(self, tenant_id: UUID, slug: str) -> None: ...

    @abstractmethod
    async def get_search_results(self, cache_key: str) -> dict | None: ...

    @abstractmethod
    async def set_search_results(self, cache_key: str, data: dict, ttl: int) -> None: ...

    @abstractmethod
    async def invalidate_tenant_search(self, tenant_id: UUID) -> None: ...

    @abstractmethod
    async def get_nearby(self, key: str) -> dict | None: ...

    @abstractmethod
    async def set_nearby(self, key: str, data: dict, ttl: int) -> None: ...

    @abstractmethod
    async def invalidate_nearby_pattern(self, tenant_id: UUID, geohash: str) -> None: ...

    @abstractmethod
    async def get_statistics(self, tenant_id: UUID) -> dict | None: ...

    @abstractmethod
    async def set_statistics(self, tenant_id: UUID, data: dict, ttl: int) -> None: ...

    @abstractmethod
    async def invalidate_statistics(self, tenant_id: UUID) -> None: ...

    @abstractmethod
    async def get_lookup(self, key: str) -> dict | None: ...

    @abstractmethod
    async def set_lookup(self, key: str, data: dict, ttl: int) -> None: ...

    @abstractmethod
    async def get_jwks(self) -> dict | None: ...

    @abstractmethod
    async def set_jwks(self, data: dict, ttl: int) -> None: ...

    @abstractmethod
    async def try_acquire_lock(self, lock_key: str, ttl: int = 5) -> bool: ...

    @abstractmethod
    async def release_lock(self, lock_key: str) -> None: ...

    def search_cache_key(self, tenant_id: UUID, criteria_hash: str) -> str:
        return f"property:search:{tenant_id}:{criteria_hash}"

    def nearby_cache_key(self, tenant_id: UUID, geohash: str, radius: int) -> str:
        return f"property:nearby:{tenant_id}:{geohash}:{radius}"
