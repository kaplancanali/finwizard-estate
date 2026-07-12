from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from property_service.application.services.property_application_service import AuthContext
from property_service.application.services.property_history_service import PropertyHistoryService
from property_service.presentation.api.deps import get_auth_context, get_history_service
from property_service.presentation.api.helpers import pagination_meta, response_meta
from property_service.presentation.schemas.common import ApiResponse, PaginatedResponse
from property_service.presentation.schemas.history_schemas import AuditLogResponse, VersionSummaryResponse

router = APIRouter(prefix="/properties", tags=["property-versions"])


@router.get("/{property_id}/versions", response_model=PaginatedResponse[VersionSummaryResponse])
async def list_versions(
    request: Request,
    property_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    auth: AuthContext = Depends(get_auth_context),
    service: PropertyHistoryService = Depends(get_history_service),
):
    items, total = await service.get_versions(property_id, auth, page=page, page_size=page_size)
    return PaginatedResponse(
        data=[
            VersionSummaryResponse(
                id=v.id,
                version_number=v.version_number,
                change_summary=v.change_summary,
                created_by=v.created_by,
            )
            for v in items
        ],
        pagination=pagination_meta(page, page_size, total),
        meta=response_meta(request),
    )


@router.get("/{property_id}/versions/{version_number}")
async def get_version(
    request: Request,
    property_id: UUID,
    version_number: int,
    auth: AuthContext = Depends(get_auth_context),
    service: PropertyHistoryService = Depends(get_history_service),
):
    version = await service.get_version(property_id, version_number, auth)
    return ApiResponse(
        data={
            "version_number": version.version_number,
            "change_summary": version.change_summary,
            "snapshot": version.snapshot,
            "created_by": str(version.created_by) if version.created_by else None,
        },
        meta=response_meta(request),
    )


@router.get("/{property_id}/audit-logs", response_model=PaginatedResponse[AuditLogResponse])
async def audit_logs(
    request: Request,
    property_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    auth: AuthContext = Depends(get_auth_context),
    service: PropertyHistoryService = Depends(get_history_service),
):
    items, total = await service.get_audit_logs(property_id, auth, page=page, page_size=page_size)
    return PaginatedResponse(
        data=[
            AuditLogResponse(
                id=a.id,
                action=a.action,
                actor_id=a.actor_id,
                actor_type=a.actor_type,
                changes=a.changes,
                correlation_id=a.correlation_id,
            )
            for a in items
        ],
        pagination=pagination_meta(page, page_size, total),
        meta=response_meta(request),
    )
