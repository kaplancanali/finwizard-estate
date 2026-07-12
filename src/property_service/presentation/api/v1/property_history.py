from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from property_service.application.services.property_application_service import AuthContext
from property_service.application.services.property_history_service import PropertyHistoryService
from property_service.presentation.api.deps import get_auth_context, get_history_service
from property_service.presentation.api.helpers import pagination_meta, response_meta
from property_service.presentation.schemas.common import ApiResponse, PaginatedResponse
from property_service.presentation.schemas.history_schemas import (
    OwnershipHistoryResponse,
    PriceHistoryResponse,
    StatusHistoryResponse,
)

router = APIRouter(prefix="/properties", tags=["property-history"])


@router.get("/{property_id}/history/price", response_model=PaginatedResponse[PriceHistoryResponse])
async def price_history(
    request: Request,
    property_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    auth: AuthContext = Depends(get_auth_context),
    service: PropertyHistoryService = Depends(get_history_service),
):
    items, total = await service.get_price_history(property_id, auth, page=page, page_size=page_size)
    return PaginatedResponse(
        data=[
            PriceHistoryResponse(
                id=i.id,
                price_type=i.price_type,
                old_amount=i.old_amount,
                new_amount=i.new_amount,
                currency=i.currency,
                changed_by=i.changed_by,
                change_reason=i.change_reason,
            )
            for i in items
        ],
        pagination=pagination_meta(page, page_size, total),
        meta=response_meta(request),
    )


@router.get("/{property_id}/history/status", response_model=PaginatedResponse[StatusHistoryResponse])
async def status_history(
    request: Request,
    property_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    auth: AuthContext = Depends(get_auth_context),
    service: PropertyHistoryService = Depends(get_history_service),
):
    items, total = await service.get_status_history(property_id, auth, page=page, page_size=page_size)
    return PaginatedResponse(
        data=[
            StatusHistoryResponse(
                id=i.id,
                old_status=i.old_status,
                new_status=i.new_status,
                changed_by=i.changed_by,
                reason=i.reason,
            )
            for i in items
        ],
        pagination=pagination_meta(page, page_size, total),
        meta=response_meta(request),
    )


@router.get("/{property_id}/history/ownership", response_model=PaginatedResponse[OwnershipHistoryResponse])
async def ownership_history(
    request: Request,
    property_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    auth: AuthContext = Depends(get_auth_context),
    service: PropertyHistoryService = Depends(get_history_service),
):
    items, total = await service.get_ownership_history(property_id, auth, page=page, page_size=page_size)
    return PaginatedResponse(
        data=[
            OwnershipHistoryResponse(
                id=i.id,
                owner_type=i.owner_type.value,
                owner_name=i.owner_name,
                ownership_percentage=i.ownership_percentage,
                acquired_at=i.acquired_at,
                released_at=i.released_at,
                effective_from=i.effective_from,
                effective_to=i.effective_to,
            )
            for i in items
        ],
        pagination=pagination_meta(page, page_size, total),
        meta=response_meta(request),
    )
