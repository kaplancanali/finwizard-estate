from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request

from property_service.application.services.property_statistics_service import PropertyStatisticsService
from property_service.presentation.api.deps import get_auth_context, get_statistics_service
from property_service.presentation.api.helpers import response_meta
from property_service.presentation.schemas.common import ApiResponse

router = APIRouter(prefix="/properties", tags=["property-statistics"])


@router.get("/statistics")
async def property_statistics(
    request: Request,
    group_by: str | None = Query(None),
    auth=Depends(get_auth_context),
    service: PropertyStatisticsService = Depends(get_statistics_service),
):
    stats = await service.get_tenant_statistics(auth)
    if group_by and group_by in stats:
        stats = {"group_by": group_by, "values": stats.get(f"by_{group_by}", stats.get(group_by, {}))}
    return ApiResponse(data=stats, meta=response_meta(request))


@router.get("/statistics/price-distribution")
async def price_distribution(
    request: Request,
    auth=Depends(get_auth_context),
    service: PropertyStatisticsService = Depends(get_statistics_service),
):
    data = await service.get_price_distribution(auth)
    return ApiResponse(data=data, meta=response_meta(request))
