from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request

from property_service.application.dto.property_search_dto import GeoCriteria, PropertySearchCriteria, SearchFilterSet
from property_service.application.auth_context import AuthContext
from property_service.application.services.property_search_service import PropertySearchService
from property_service.presentation.api.deps import get_auth_context, get_search_service, require_permission
from property_service.presentation.api.helpers import pagination_meta, response_meta
from property_service.presentation.mappers.property_mappers import search_criteria_from_request, summary_to_response
from property_service.presentation.schemas.common import ApiResponse, PaginatedResponse
from property_service.presentation.schemas.property_schemas import PropertySummaryResponse
from property_service.presentation.schemas.search_schemas import PropertySearchRequest

router = APIRouter(prefix="/properties", tags=["search"])


@router.post("/search", response_model=PaginatedResponse[PropertySummaryResponse])
async def search_properties(
    request: Request,
    body: PropertySearchRequest,
    auth: AuthContext = Depends(require_permission("property:search")),
    service: PropertySearchService = Depends(get_search_service),
):
    criteria = search_criteria_from_request(body, auth.tenant_id)
    result = await service.search(criteria, auth)
    return PaginatedResponse(
        data=[summary_to_response(i) for i in result.items],
        pagination=pagination_meta(body.page, body.page_size, result.total),
        meta=response_meta(request),
    )


@router.get("/search", response_model=PaginatedResponse[PropertySummaryResponse])
async def search_properties_get(
    request: Request,
    q: str | None = Query(None),
    type: str | None = Query(None, alias="type"),
    status: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_area: float | None = None,
    max_area: float | None = None,
    rooms: float | None = None,
    province: str | None = None,
    district: str | None = None,
    lat: float | None = None,
    lng: float | None = None,
    radius: int = Query(5000),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    auth: AuthContext = Depends(require_permission("property:search")),
    service: PropertySearchService = Depends(get_search_service),
):
    filters: dict = {}
    if type:
        filters["property_types"] = [type]
    if status:
        filters["status"] = [status]
    if min_price is not None or max_price is not None:
        filters["sale_price"] = {"min": min_price, "max": max_price}
    if min_area is not None or max_area is not None:
        filters["net_area_sqm"] = {"min": min_area, "max": max_area}
    if rooms is not None:
        filters["room_count"] = {"min": rooms, "max": rooms}
    if province:
        filters["provinces"] = [province]
    if district:
        filters["districts"] = [district]

    geo = None
    if lat is not None and lng is not None:
        geo = GeoCriteria(
            type="radius",
            payload={"type": "radius", "latitude": lat, "longitude": lng, "radius_meters": radius},
        )

    criteria = PropertySearchCriteria(
        tenant_id=auth.tenant_id,
        query=q,
        filters=SearchFilterSet(raw=filters),
        geo=geo,
        page=page,
        page_size=page_size,
    )
    result = await service.search(criteria, auth)
    return PaginatedResponse(
        data=[summary_to_response(i) for i in result.items],
        pagination=pagination_meta(page, page_size, result.total),
        meta=response_meta(request),
    )


@router.get("/nearby", response_model=PaginatedResponse[PropertySummaryResponse])
async def nearby_properties(
    request: Request,
    lat: float = Query(...),
    lng: float = Query(...),
    radius: int = Query(5000),
    limit: int = Query(20, le=100),
    property_type: str | None = None,
    status: str | None = None,
    auth: AuthContext = Depends(require_permission("property:search")),
    service: PropertySearchService = Depends(get_search_service),
):
    status_list = [status] if status else None
    result = await service.nearby(
        auth, lat, lng, radius, limit=limit, property_type=property_type, status=status_list
    )
    return PaginatedResponse(
        data=[summary_to_response(i) for i in result.items],
        pagination=pagination_meta(1, limit, result.total),
        meta=response_meta(request),
    )


@router.get("/map")
async def map_clusters(
    request: Request,
    north: float = Query(...),
    south: float = Query(...),
    east: float = Query(...),
    west: float = Query(...),
    zoom: int = Query(12),
    cluster: bool = Query(True),
    auth: AuthContext = Depends(require_permission("property:search")),
    service: PropertySearchService = Depends(get_search_service),
):
    data = await service.map_search(
        auth,
        north=north,
        south=south,
        east=east,
        west=west,
        zoom=zoom,
        cluster=cluster,
    )
    return ApiResponse(data=data, meta=response_meta(request))
