from __future__ import annotations

import logging

from property_service.domain.exceptions.base import InfrastructureError, PropertyServiceError
from property_service.presentation.errors.error_registry import http_status_for_code, is_client_error

logger = logging.getLogger(__name__)


def log_service_error(
    exc: PropertyServiceError,
    *,
    correlation_id: str | None = None,
    **context: object,
) -> None:
    status_code = http_status_for_code(exc.code)
    extra = {
        "correlation_id": correlation_id,
        "error_code": exc.code,
        **{key: value for key, value in context.items() if value is not None},
    }
    if is_client_error(status_code):
        logger.warning(exc.message, extra=extra)
        return
    logger.error(exc.message, extra=extra, exc_info=isinstance(exc, InfrastructureError))


def log_unhandled_error(exc: Exception, *, correlation_id: str | None = None) -> None:
    logger.exception(
        "Unhandled error",
        extra={"correlation_id": correlation_id, "error_code": "INTERNAL_ERROR"},
        exc_info=exc,
    )
