from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Request

from property_service.application.services.property_application_service import (
    AuthContext,
    PropertyApplicationService,
)
from property_service.presentation.api.deps import get_auth_context, get_property_service
from property_service.presentation.api.helpers import response_meta
from property_service.presentation.schemas.common import ApiResponse
from property_service.presentation.schemas.metadata_schemas import MetadataPatchRequest, MetadataResponse

router = APIRouter(prefix="/properties", tags=["property-metadata"])


@router.get("/{property_id}/metadata", response_model=ApiResponse[MetadataResponse])
async def get_metadata(
    request: Request,
    property_id: UUID,
    auth: AuthContext = Depends(get_auth_context),
    service: PropertyApplicationService = Depends(get_property_service),
):
    metadata = await service.get_metadata(property_id, auth)
    return ApiResponse(
        data=MetadataResponse(
            metadata=metadata.metadata,
            tenant_extensions=metadata.tenant_extensions,
            schema_version=metadata.schema_version,
        ),
        meta=response_meta(request),
    )


@router.patch("/{property_id}/metadata", response_model=ApiResponse[MetadataResponse])
async def patch_metadata(
    request: Request,
    property_id: UUID,
    body: MetadataPatchRequest,
    auth: AuthContext = Depends(get_auth_context),
    service: PropertyApplicationService = Depends(get_property_service),
):
    prop = await service.update_metadata(
        property_id,
        auth,
        metadata=body.metadata,
        tenant_extensions=body.tenant_extensions,
    )
    return ApiResponse(
        data=MetadataResponse(
            metadata=prop.metadata.metadata,
            tenant_extensions=prop.metadata.tenant_extensions,
            schema_version=prop.metadata.schema_version,
        ),
        meta=response_meta(request),
    )
