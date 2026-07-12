from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from property_service.application.auth_context import AuthContext
from property_service.application.services.property_application_service import PropertyApplicationService
from property_service.domain.enums.property_category import PropertyCategory
from property_service.domain.enums.property_status import PropertyStatus
from property_service.domain.enums.property_type import PropertyType
from property_service.domain.enums.source_type import SourceType
from property_service.domain.factories.property_factory import CreatePropertyData
from property_service.presentation.api.deps import get_property_service, require_permission
from property_service.presentation.api.helpers import response_meta
from property_service.presentation.mappers.property_mappers import (
    building_from_schema,
    create_dto_from_request,
    features_from_schema,
    location_from_schema,
    pricing_from_schema,
    property_to_detail,
    property_to_response,
)
from property_service.presentation.schemas.common import ApiResponse
from property_service.presentation.schemas.property_schemas import (
    PropertyCreateRequest,
    PropertyResponse,
    PropertyUpdateRequest,
    StatusChangeRequest,
)
from property_service.presentation.schemas.search_schemas import RegisterPropertyRequest

router = APIRouter(prefix="/properties", tags=["properties"])


@router.post("", status_code=201, response_model=ApiResponse[PropertyResponse])
async def create_property(
    request: Request,
    body: PropertyCreateRequest,
    auth: AuthContext = Depends(require_permission("property:create")),
    service: PropertyApplicationService = Depends(get_property_service),
):
    dto = create_dto_from_request(body, auth.tenant_id, auth.user_id)
    prop = await service.create_property(dto, auth)
    return ApiResponse(data=property_to_response(prop), meta=response_meta(request))


@router.post("/register", status_code=201, response_model=ApiResponse[PropertyResponse])
async def register_property(
    request: Request,
    body: RegisterPropertyRequest,
    auth: AuthContext = Depends(require_permission("property:create")),
    service: PropertyApplicationService = Depends(get_property_service),
):
    data = CreatePropertyData(
        tenant_id=auth.tenant_id,
        created_by=auth.user_id,
        title=body.title or "Imported Property",
        property_type=PropertyType(body.property_type or "apartment"),
        property_category=PropertyCategory(body.property_category or "residential"),
        source_type=SourceType(body.source_type),
        source_reference=body.source_reference,
    )
    prop = await service.register_property(data, auth)
    return ApiResponse(data=property_to_response(prop), meta=response_meta(request))


@router.get("/code/{property_code}")
async def get_by_code(
    request: Request,
    property_code: str,
    include: str | None = Query(None),
    auth: AuthContext = Depends(require_permission("property:read")),
    service: PropertyApplicationService = Depends(get_property_service),
):
    prop = await service.get_by_code(property_code, auth)
    return ApiResponse(data=property_to_detail(prop, include), meta=response_meta(request))


@router.get("/slug/{slug}")
async def get_by_slug(
    request: Request,
    slug: str,
    include: str | None = Query(None),
    auth: AuthContext = Depends(require_permission("property:read")),
    service: PropertyApplicationService = Depends(get_property_service),
):
    prop = await service.get_by_slug(slug, auth)
    return ApiResponse(data=property_to_detail(prop, include), meta=response_meta(request))


@router.get("/{property_id}")
async def get_property(
    request: Request,
    property_id: UUID,
    include: str | None = Query(None, description="images,documents,ownership,history,listing"),
    auth: AuthContext = Depends(require_permission("property:read")),
    service: PropertyApplicationService = Depends(get_property_service),
):
    prop = await service.get_property(property_id, auth)
    return ApiResponse(data=property_to_detail(prop, include), meta=response_meta(request))


@router.put("/{property_id}", response_model=ApiResponse[PropertyResponse])
async def replace_property(
    request: Request,
    property_id: UUID,
    body: PropertyUpdateRequest,
    auth: AuthContext = Depends(require_permission("property:update")),
    service: PropertyApplicationService = Depends(get_property_service),
):
    prop = await service.update_property(
        property_id,
        auth,
        expected_version=body.version,
        title=body.title,
        description=body.description,
        pricing=pricing_from_schema(body.pricing),
        location=location_from_schema(body.location) if body.location else None,
        building=building_from_schema(body.building),
        features=features_from_schema(body.features),
        amenities=body.amenities,
        tags=body.tags,
    )
    return ApiResponse(data=property_to_response(prop), meta=response_meta(request))


@router.patch("/{property_id}", response_model=ApiResponse[PropertyResponse])
async def update_property(
    request: Request,
    property_id: UUID,
    body: PropertyUpdateRequest,
    auth: AuthContext = Depends(require_permission("property:update")),
    service: PropertyApplicationService = Depends(get_property_service),
):
    prop = await service.update_property(
        property_id,
        auth,
        expected_version=body.version,
        title=body.title,
        description=body.description,
        pricing=pricing_from_schema(body.pricing),
        location=location_from_schema(body.location) if body.location else None,
        building=building_from_schema(body.building),
        features=features_from_schema(body.features),
        amenities=body.amenities,
        tags=body.tags,
    )
    return ApiResponse(data=property_to_response(prop), meta=response_meta(request))


@router.delete("/{property_id}", status_code=204)
async def delete_property(
    property_id: UUID,
    auth: AuthContext = Depends(require_permission("property:delete")),
    service: PropertyApplicationService = Depends(get_property_service),
):
    await service.delete_property(property_id, auth)


@router.post("/{property_id}/restore", response_model=ApiResponse[PropertyResponse])
async def restore_property(
    request: Request,
    property_id: UUID,
    auth: AuthContext = Depends(require_permission("property:delete")),
    service: PropertyApplicationService = Depends(get_property_service),
):
    prop = await service.restore_property(property_id, auth)
    return ApiResponse(data=property_to_response(prop), meta=response_meta(request))


@router.post("/{property_id}/status", response_model=ApiResponse[PropertyResponse])
async def change_status(
    request: Request,
    property_id: UUID,
    body: StatusChangeRequest,
    auth: AuthContext = Depends(require_permission("property:update")),
    service: PropertyApplicationService = Depends(get_property_service),
):
    prop = await service.change_status(
        property_id,
        PropertyStatus(body.status),
        auth,
        expected_version=body.version,
        reason=body.reason,
    )
    return ApiResponse(data=property_to_response(prop), meta=response_meta(request))
