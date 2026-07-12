from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from property_service.domain.exceptions import IdempotencyConflictError
from property_service.presentation.errors.error_registry import http_status_for_code
from property_service.presentation.errors.response_builder import build_error_payload
from property_service.shared.idempotency import InMemoryIdempotencyStore

_store = InMemoryIdempotencyStore()


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """Honour Idempotency-Key on mutating requests."""

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return await call_next(request)

        key = request.headers.get("Idempotency-Key")
        if not key:
            return await call_next(request)

        tenant_id = request.headers.get("X-Tenant-ID") or "default"
        from uuid import UUID as UUIDType

        try:
            tenant_uuid = UUIDType(tenant_id)
        except ValueError:
            tenant_uuid = UUIDType("00000000-0000-0000-0000-000000000010")

        if _store.seen(tenant_uuid, key):
            exc = IdempotencyConflictError("Idempotency-Key already used")
            return JSONResponse(
                status_code=http_status_for_code(exc.code),
                content=build_error_payload(
                    request,
                    code=exc.code,
                    message=exc.message,
                ),
            )

        request.state.idempotency_key = key
        return await call_next(request)
