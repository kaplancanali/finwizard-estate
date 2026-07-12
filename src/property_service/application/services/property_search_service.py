from __future__ import annotations

from dataclasses import asdict
from typing import Any
from uuid import UUID

from property_service.application.auth_context import AuthContext
from property_service.application.dto.property_search_dto import (
    MapSearchCriteria,
    NearbySearchCriteria,
    PropertySearchCriteria,
    PropertySearchResult,
    PropertySummary,
)
from property_service.application.ports.property_cache import IPropertyCache
from property_service.infrastructure.cache.cache_config import TTL_PROPERTY_NEARBY, TTL_PROPERTY_SEARCH, hash_search_criteria
from property_service.infrastructure.cache.geohash_utils import encode_geohash


class PropertySearchService:
    """Read-side search orchestration (CQRS query handler)."""

    def __init__(
        self,
        search_uow_factory,
        property_cache: IPropertyCache | None = None,
    ) -> None:
        self._search_uow_factory = search_uow_factory
        self._cache = property_cache

    async def search(self, criteria: PropertySearchCriteria, auth: AuthContext) -> PropertySearchResult:
        tenant_id = auth.tenant_id
        cache_key = None
        if self._cache:
            criteria_hash = hash_search_criteria(criteria)
            cache_key = self._cache.search_cache_key(tenant_id, criteria_hash)
            try:
                cached = await self._cache.get_search_results(cache_key)
                if cached:
                    return self._result_from_cache(cached)
            except Exception:
                pass

        async with self._search_uow_factory() as repo:
            result = await repo.search(criteria, tenant_id)

        if self._cache and cache_key:
            try:
                await self._cache.set_search_results(
                    cache_key,
                    {
                        "items": [asdict(i) for i in result.items],
                        "total": result.total,
                        "page": result.page,
                        "page_size": result.page_size,
                        "facets": result.facets,
                    },
                    ttl=TTL_PROPERTY_SEARCH,
                )
            except Exception:
                pass
        return result

    async def find_nearby(
        self,
        auth: AuthContext,
        lat: float,
        lng: float,
        radius_meters: int = 5000,
        limit: int = 20,
        property_type: str | None = None,
        status: list[str] | None = None,
    ) -> PropertySearchResult:
        tenant_id = auth.tenant_id
        geohash = encode_geohash(lat, lng)
        cache_key = None
        if self._cache:
            cache_key = self._cache.nearby_cache_key(tenant_id, geohash, radius_meters)
            try:
                cached = await self._cache.get_nearby(cache_key)
                if cached:
                    return self._result_from_cache(cached)
            except Exception:
                pass

        criteria = NearbySearchCriteria(
            latitude=lat,
            longitude=lng,
            radius_meters=radius_meters,
            limit=limit,
            property_type=property_type,
            status=status,
        )
        async with self._search_uow_factory() as repo:
            result = await repo.find_nearby(criteria, tenant_id)

        if self._cache and cache_key:
            try:
                await self._cache.set_nearby(
                    cache_key,
                    {
                        "items": [asdict(i) for i in result.items],
                        "total": result.total,
                        "page": result.page,
                        "page_size": result.page_size,
                        "facets": result.facets,
                    },
                    ttl=TTL_PROPERTY_NEARBY,
                )
            except Exception:
                pass
        return result

    async def nearby(self, auth: AuthContext, lat: float, lng: float, radius_meters: int = 5000, **kwargs):
        return await self.find_nearby(auth, lat, lng, radius_meters, **kwargs)

    async def map_search(
        self,
        auth: AuthContext,
        *,
        north: float,
        south: float,
        east: float,
        west: float,
        zoom: int = 12,
        cluster: bool = True,
    ) -> dict[str, Any]:
        criteria = MapSearchCriteria(
            north=north,
            south=south,
            east=east,
            west=west,
            zoom=zoom,
            cluster=cluster,
        )
        async with self._search_uow_factory() as repo:
            results = await repo.map_search(criteria, auth.tenant_id)

        from property_service.application.dto.property_search_dto import MapCluster

        if results and isinstance(results[0], MapCluster):
            return {
                "zoom": zoom,
                "cluster": True,
                "clusters": [asdict(item) for item in results],
                "total": sum(item.count for item in results),
            }

        markers = [
            {
                "id": str(item.id),
                "latitude": float(item.latitude) if item.latitude is not None else None,
                "longitude": float(item.longitude) if item.longitude is not None else None,
                "title": item.title,
            }
            for item in results
            if isinstance(item, PropertySummary)
            and item.latitude is not None
            and item.longitude is not None
        ]
        return {"zoom": zoom, "cluster": cluster, "markers": markers, "total": len(markers)}

    @staticmethod
    def _result_from_cache(payload: dict[str, Any]) -> PropertySearchResult:
        items = [PropertySummary(**item) for item in payload["items"]]
        return PropertySearchResult(
            items=items,
            total=payload["total"],
            page=payload["page"],
            page_size=payload["page_size"],
            facets=payload.get("facets"),
        )
