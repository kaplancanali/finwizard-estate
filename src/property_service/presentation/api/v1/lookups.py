from __future__ import annotations

from fastapi import APIRouter

from property_service.di.container import get_container
from property_service.infrastructure.cache.cache_config import lookup_amenities_key, lookup_types_key
from property_service.presentation.schemas.common import ApiResponse, ResponseMeta

router = APIRouter(prefix="/lookups", tags=["lookups"])


@router.get("/property-types")
async def property_types():
    cache = get_container().cache_manager
    cached = await cache.get_lookup(lookup_types_key())
    if cached:
        return ApiResponse(data=cached["items"], meta=ResponseMeta())
    await cache.warm_lookup_caches()
    cached = await cache.get_lookup(lookup_types_key())
    return ApiResponse(data=(cached or {}).get("items", []), meta=ResponseMeta())


@router.get("/statuses")
async def statuses():
    from property_service.domain.enums.property_status import PropertyStatus

    return ApiResponse(
        data=[{"code": s.value} for s in PropertyStatus],
        meta=ResponseMeta(),
    )


@router.get("/amenities")
async def amenities():
    cache = get_container().cache_manager
    cached = await cache.get_lookup(lookup_amenities_key())
    if cached:
        return ApiResponse(data=cached["items"], meta=ResponseMeta())
    await cache.warm_lookup_caches()
    cached = await cache.get_lookup(lookup_amenities_key())
    return ApiResponse(data=(cached or {}).get("items", []), meta=ResponseMeta())
