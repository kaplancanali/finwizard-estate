from __future__ import annotations

from dataclasses import asdict

from property_service.application.auth_context import AuthContext
from property_service.infrastructure.cache.property_cache_manager import PropertyCacheManager
from property_service.infrastructure.persistence.read_unit_of_work import search_unit_of_work


class PropertyStatisticsService:
    """Aggregated analytics scoped to tenant property data."""

    def __init__(
        self,
        search_uow_factory=search_unit_of_work,
        cache_manager: PropertyCacheManager | None = None,
    ) -> None:
        self._search_uow_factory = search_uow_factory
        self._cache = cache_manager

    async def get_tenant_statistics(self, auth: AuthContext, *, group_by: list[str] | None = None) -> dict:
        if self._cache and not group_by:
            cached = await self._cache.get_statistics(auth.tenant_id)
            if cached:
                return cached

        async with self._search_uow_factory() as repo:
            stats = await repo.get_statistics(auth.tenant_id, group_by=group_by)

        payload = asdict(stats)
        if self._cache and not group_by:
            await self._cache.set_statistics(auth.tenant_id, payload)
        return payload

    async def get_price_distribution(self, auth: AuthContext) -> dict:
        async with self._search_uow_factory() as repo:
            return await repo.price_distribution(auth.tenant_id)
