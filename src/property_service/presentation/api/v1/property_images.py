from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from property_service.application.services.property_application_service import AuthContext
from property_service.application.services.property_media_service import PropertyMediaService
from property_service.presentation.api.deps import get_auth_context, get_media_service
from property_service.presentation.api.helpers import response_meta
from property_service.presentation.schemas.common import ApiResponse
from property_service.presentation.schemas.media_schemas import ImageReorderRequest, ImageUploadRequest

router = APIRouter(prefix="/properties", tags=["property-images"])


@router.post("/{property_id}/images", status_code=201)
async def upload_image(
    request: Request,
    property_id: UUID,
    body: ImageUploadRequest,
    auth: AuthContext = Depends(get_auth_context),
    service: PropertyMediaService = Depends(get_media_service),
):
    result = await service.initiate_image_upload(
        property_id,
        auth,
        file_name=body.file_name,
        mime_type=body.mime_type,
        file_size=body.file_size,
        caption=body.caption,
        is_primary=body.is_primary,
        sort_order=body.sort_order,
    )
    image = result["image"]
    return ApiResponse(
        data={
            "image": {"id": str(image.id), "storage_key": image.storage_key, "url": image.url},
            "upload_url": result["upload_url"],
            "property_version": result["property_version"],
        },
        meta=response_meta(request),
    )


@router.post("/{property_id}/images/{image_id}/confirm")
async def confirm_image_upload(
    request: Request,
    property_id: UUID,
    image_id: UUID,
    auth: AuthContext = Depends(get_auth_context),
    service: PropertyMediaService = Depends(get_media_service),
):
    data = await service.confirm_image_upload(property_id, image_id, auth)
    return ApiResponse(data=data, meta=response_meta(request))


@router.patch("/{property_id}/images/reorder")
async def reorder_images(
    request: Request,
    property_id: UUID,
    body: ImageReorderRequest,
    auth: AuthContext = Depends(get_auth_context),
    service: PropertyMediaService = Depends(get_media_service),
):
    version = await service.reorder_images(property_id, body.image_ids, auth)
    return ApiResponse(
        data={"property_id": str(property_id), "image_ids": [str(i) for i in body.image_ids], "property_version": version},
        meta=response_meta(request),
    )


@router.delete("/{property_id}/images/{image_id}", status_code=204)
async def delete_image(
    property_id: UUID,
    image_id: UUID,
    auth: AuthContext = Depends(get_auth_context),
    service: PropertyMediaService = Depends(get_media_service),
):
    await service.delete_image(property_id, image_id, auth)
    return None
