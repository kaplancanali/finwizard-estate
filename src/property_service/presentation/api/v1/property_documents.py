from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Request

from property_service.application.services.property_application_service import AuthContext
from property_service.application.services.property_media_service import PropertyMediaService
from property_service.presentation.api.deps import get_auth_context, get_media_service
from property_service.presentation.api.helpers import response_meta
from property_service.presentation.schemas.common import ApiResponse
from property_service.presentation.schemas.media_schemas import DocumentUploadRequest

router = APIRouter(prefix="/properties", tags=["property-documents"])


@router.post("/{property_id}/documents", status_code=201)
async def upload_document(
    request: Request,
    property_id: UUID,
    body: DocumentUploadRequest,
    auth: AuthContext = Depends(get_auth_context),
    service: PropertyMediaService = Depends(get_media_service),
):
    result = await service.initiate_document_upload(
        property_id,
        auth,
        file_name=body.file_name,
        document_type=body.document_type,
        mime_type=body.mime_type,
        file_size=body.file_size,
    )
    document = result["document"]
    return ApiResponse(
        data={
            "document": {
                "id": str(document.id),
                "document_type": document.document_type.value,
                "storage_key": document.storage_key,
            },
            "upload_url": result["upload_url"],
            "property_version": result["property_version"],
        },
        meta=response_meta(request),
    )


@router.delete("/{property_id}/documents/{document_id}", status_code=204)
async def delete_document(
    property_id: UUID,
    document_id: UUID,
    auth: AuthContext = Depends(get_auth_context),
):
    return None


@router.patch("/{property_id}/documents/{document_id}/verify")
async def verify_document(
    request: Request,
    property_id: UUID,
    document_id: UUID,
    auth: AuthContext = Depends(get_auth_context),
    service: PropertyMediaService = Depends(get_media_service),
):
    version = await service.verify_document(property_id, document_id, auth)
    return ApiResponse(
        data={
            "property_id": str(property_id),
            "document_id": str(document_id),
            "verified": True,
            "property_version": version,
        },
        meta=response_meta(request),
    )
