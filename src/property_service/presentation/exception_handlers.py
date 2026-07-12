from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from property_service.domain.exceptions import PropertyServiceError, RateLimitExceededError
from property_service.presentation.errors.error_logging import log_service_error, log_unhandled_error
from property_service.presentation.errors.error_registry import http_status_for_code
from property_service.presentation.errors.response_builder import build_error_payload


def _correlation_id(request: Request) -> str | None:
    return getattr(request.state, "correlation_id", None)


def _detail_dicts(exc: PropertyServiceError) -> list[dict]:
    return [
        {"field": detail.field, "message": detail.message, "code": detail.code}
        for detail in exc.details
    ]


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(request: Request, exc: RequestValidationError):
        details = []
        for error in exc.errors():
            location = [str(part) for part in error.get("loc", ()) if part != "body"]
            details.append(
                {
                    "field": ".".join(location) if location else None,
                    "message": error.get("msg", "Invalid input"),
                    "code": "VALIDATION_ERROR",
                }
            )
        return JSONResponse(
            status_code=400,
            content=build_error_payload(
                request,
                code="VALIDATION_ERROR",
                message="Request validation failed",
                details=details,
            ),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        code = "UNAUTHORIZED" if exc.status_code == 401 else "VALIDATION_ERROR"
        if exc.status_code == 403:
            code = "FORBIDDEN"
        if exc.status_code == 429:
            code = "RATE_LIMIT_EXCEEDED"
        if exc.status_code >= 500:
            code = "INTERNAL_ERROR"
        message = exc.detail if isinstance(exc.detail, str) else "Request failed"
        log_service_error(
            PropertyServiceError(message=message, code=code),
            correlation_id=_correlation_id(request),
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=build_error_payload(request, code=code, message=message),
        )

    @app.exception_handler(PropertyServiceError)
    async def property_error_handler(request: Request, exc: PropertyServiceError):
        status_code = http_status_for_code(exc.code)
        log_service_error(exc, correlation_id=_correlation_id(request))
        headers: dict[str, str] | None = None
        if isinstance(exc, RateLimitExceededError):
            headers = {"Retry-After": str(exc.retry_after)}
        return JSONResponse(
            status_code=status_code,
            content=build_error_payload(
                request,
                code=exc.code,
                message=exc.message,
                details=_detail_dicts(exc),
            ),
            headers=headers,
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception):
        log_unhandled_error(exc, correlation_id=_correlation_id(request))
        return JSONResponse(
            status_code=500,
            content=build_error_payload(
                request,
                code="INTERNAL_ERROR",
                message="An unexpected error occurred",
            ),
        )
