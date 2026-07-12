from __future__ import annotations

from uuid import uuid4

from fastapi import Request

from property_service.presentation.schemas.common import PaginationMeta, ResponseMeta


def response_meta(request: Request) -> ResponseMeta:
    return ResponseMeta(
        correlation_id=getattr(request.state, "correlation_id", None),
        request_id=getattr(request.state, "request_id", None) or str(uuid4()),
    )


def pagination_meta(page: int, page_size: int, total_items: int) -> PaginationMeta:
    total_pages = (total_items + page_size - 1) // page_size if total_items else 0
    return PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
    )
